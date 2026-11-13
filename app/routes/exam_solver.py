import json, re, uuid
from pathlib import Path
from xml.sax.saxutils import escape
from flask import Blueprint, request, jsonify, g, current_app, send_file
from werkzeug.utils import secure_filename
from ..extensions import db
from ..models.exam_solver import ExamRun
from ..utils.auth import require_auth
from ..services.gemini_service import GeminiService

exam_bp = Blueprint("exam_solver", __name__)
ALLOWED = {"pdf", "png", "jpg", "jpeg", "tif", "tiff", "webp"}
MAX_BYTES = 15 * 1024 * 1024


def extract_document(path, ext):
    if ext == "pdf":
        import fitz
        doc = fitz.open(path)
        if doc.page_count > 40:
            raise ValueError("PDF limit is 40 pages. Split the paper and upload the parts separately.")
        pages = []
        for page_no, page in enumerate(doc, 1):
            text = page.get_text("text").strip()
            if len(text) < 35:
                try:
                    import pytesseract
                    from PIL import Image
                    import io
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
                    text = pytesseract.image_to_string(Image.open(io.BytesIO(pix.tobytes("png"))))
                except Exception:
                    pass
            if text.strip():
                pages.append(f"[Page {page_no}]\n{text.strip()}")
        doc.close()
        return "\n\n".join(pages)
    try:
        from PIL import Image
        import pytesseract
        return pytesseract.image_to_string(Image.open(path))
    except ImportError as exc:
        raise ValueError("Image OCR requires Pillow and pytesseract. Install backend requirements and the Tesseract OCR engine.") from exc
    except Exception as exc:
        raise ValueError("Could not read this image. Try a clear PNG or JPEG scan.") from exc


def split_questions(text):
    text = re.sub(r"\r", "\n", text)
    # Split at common numbered question starts, retaining question labels.
    pattern = re.compile(r"(?im)(?=^\s*(?:Q(?:uestion)?\s*)?\d{1,3}\s*[.)、:-]\s*)")
    chunks = [x.strip() for x in pattern.split(text) if x.strip()]
    if len(chunks) <= 1:
        chunks = [x.strip() for x in re.split(r"\n\s*\n", text) if len(x.strip()) >= 18]
    questions = []
    for idx, chunk in enumerate(chunks[:30], 1):
        if len(chunk) < 12:
            continue
        label = re.match(r"(?i)^\s*(Q(?:uestion)?\s*)?(\d{1,3})\s*[.)、:-]", chunk)
        number = int(label.group(2)) if label else idx
        questions.append({"number": number, "text": chunk[:5000], "type": classify(chunk)})
    if not questions and len(text.strip()) >= 20:
        questions = [{"number": 1, "text": text.strip()[:5000], "type": classify(text)}]
    return questions


def classify(text):
    t = text.lower()
    if re.search(r"\b(a\)|b\)|c\)|d\)|choose|which of the following|select the correct)\b", t): return "MCQ"
    if re.search(r"\b(program|write a code|algorithm|output of|compile|java|python|c\+\+)\b", t): return "Programming / CS"
    if re.search(r"\b(integral|differentiate|equation|calculate|solve|matrix|probability|numerical)\b", t): return "Mathematical / Numerical"
    if re.search(r"\b(explain|define|describe|compare|why|what is|discuss)\b", t): return "Conceptual"
    return "General"


@exam_bp.post("/upload")
@require_auth
def upload_exam():
    file = request.files.get("file")
    if not file or not file.filename:
        return jsonify({"error": "Choose a PDF or image file."}), 400
    filename = secure_filename(file.filename)
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED:
        return jsonify({"error": "Supported formats: PDF, PNG, JPG, JPEG, TIFF and WEBP."}), 400
    raw = file.read()
    if not raw or len(raw) > MAX_BYTES:
        return jsonify({"error": "File must be non-empty and no larger than 15 MB."}), 400
    folder = Path(current_app.root_path) / "storage" / "exam_uploads"
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{uuid.uuid4().hex}.{ext}"
    path.write_bytes(raw)
    try:
        extracted = extract_document(path, ext)
        if len(extracted.strip()) < 20:
            raise ValueError("No readable text was found. For scanned PDFs, install Tesseract OCR and try a clearer scan.")
        questions = split_questions(extracted)
        result = {"questions": questions, "question_count": len(questions), "extraction_characters": len(extracted),
                  "extraction_note": "OCR output can contain recognition errors. Review extracted text before relying on a solution."}
        run = ExamRun(user_id=g.current_user.id, filename=filename, storage_path=str(path), extracted_text=extracted[:150000], result_json=result)
        db.session.add(run); db.session.commit()
        return jsonify({"exam": run.to_dict()}), 201
    except ValueError as exc:
        path.unlink(missing_ok=True); db.session.rollback()
        return jsonify({"error": str(exc)}), 400
    except Exception:
        path.unlink(missing_ok=True); db.session.rollback()
        return jsonify({"error": "Document extraction failed. Check the PDF/image and OCR installation."}), 400


@exam_bp.get("/runs")
@require_auth
def list_exam_runs():
    runs = ExamRun.query.filter_by(user_id=g.current_user.id).order_by(ExamRun.created_at.desc()).limit(30).all()
    return jsonify({"exams": [r.to_dict() for r in runs]})


@exam_bp.get("/runs/<int:run_id>")
@require_auth
def get_exam_run(run_id):
    run = ExamRun.query.filter_by(id=run_id, user_id=g.current_user.id).first_or_404()
    return jsonify({"exam": run.to_dict()})


@exam_bp.post("/runs/<int:run_id>/solve")
@require_auth
def solve_exam(run_id):
    run = ExamRun.query.filter_by(id=run_id, user_id=g.current_user.id).first_or_404()
    questions = (run.result_json or {}).get("questions", [])
    if not questions:
        return jsonify({"error": "No questions were extracted from this document."}), 400
    if len(questions) > 30:
        return jsonify({"error": "This run exceeds the 30-question solving limit."}), 400
    try:
        prompt = ("You are an exam tutor. Solve each supplied question carefully. Show concise step-by-step reasoning, formulas or code as appropriate, "
                  "state assumptions, and never fabricate missing diagrams/data. For MCQs identify the selected option and explain briefly. "
                  "If ambiguous or unreadable, say so and give confidence LOW. Return valid JSON only: {\"answers\":[{\"number\":1,\"answer\":\"...\",\"confidence\":\"HIGH|MEDIUM|LOW\"}]}\nQUESTIONS:\n" + json.dumps(questions, ensure_ascii=False))
        raw = GeminiService().generate(prompt)
        match = re.search(r"\{[\s\S]*\}", raw)
        if not match: raise RuntimeError("Model did not return structured answers")
        solved = json.loads(match.group(0)).get("answers", [])
        if not solved: raise RuntimeError("No answers returned")
        verify_prompt = ("Independently audit these proposed exam answers against their original questions. Check calculations, logic, selected options and code. "
                         "Do not assume the proposed answer is correct. Return JSON only: {\"checks\":[{\"number\":1,\"status\":\"VERIFIED|NEEDS_REVIEW|INCORRECT\",\"feedback\":\"...\"}]}\nQUESTIONS:\n" +
                         json.dumps(questions, ensure_ascii=False) + "\nPROPOSED ANSWERS:\n" + json.dumps(solved, ensure_ascii=False))
        verify_raw = GeminiService().generate(verify_prompt)
        verify_match = re.search(r"\{[\s\S]*\}", verify_raw)
        checks = json.loads(verify_match.group(0)).get("checks", []) if verify_match else []
        check_map = {str(x.get("number")): x for x in checks}
        for answer in solved:
            answer["verification"] = check_map.get(str(answer.get("number")), {"status": "NEEDS_REVIEW", "feedback": "Independent verification was not returned."})
        result = dict(run.result_json or {})
        result["answers"] = solved
        result["verification_note"] = "AI verification is a second model review, not a proof of correctness. Independently check important answers."
        run.result_json = result; run.status = "solved"; db.session.commit()
        return jsonify({"exam": run.to_dict()}), 200
    except ValueError as exc:
        db.session.rollback(); return jsonify({"error": str(exc)}), 503
    except Exception:
        db.session.rollback(); return jsonify({"error": "Solving or verification failed. Check Gemini configuration and retry."}), 502


@exam_bp.get("/runs/<int:run_id>/download")
@require_auth
def download_exam_solution(run_id):
    run = ExamRun.query.filter_by(id=run_id, user_id=g.current_user.id).first_or_404()
    answers = (run.result_json or {}).get("answers", [])
    if not answers:
        return jsonify({"error": "Solve this paper before exporting its solution."}), 400
    fmt = (request.args.get("format") or "pdf").lower()
    if fmt not in {"pdf", "docx"}:
        return jsonify({"error": "Format must be pdf or docx."}), 400
    out_dir = Path(current_app.root_path) / "storage" / "exam_exports"
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / f"solution-{run.id}-{uuid.uuid4().hex[:8]}.{fmt}"
    title = f"TaskForge Exam Solution - {run.filename}"
    if fmt == "pdf":
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import mm
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        styles = getSampleStyleSheet(); story = [Paragraph(escape(title), styles["Title"]), Spacer(1, 10)]
        for a in answers:
            story.append(Paragraph(escape(f"Question {a.get('number', '')}"), styles["Heading2"]))
            story.append(Paragraph(escape(str(a.get("answer", ""))).replace("\n", "<br/>"), styles["BodyText"]))
            v = a.get("verification", {})
            story.append(Paragraph(escape(f"Verification: {v.get('status', 'NEEDS_REVIEW')} — {v.get('feedback', '')}"), styles["Italic"]))
            story.append(Spacer(1, 8))
        story.append(Paragraph(escape((run.result_json or {}).get("verification_note", "")), styles["Italic"]))
        SimpleDocTemplate(str(target), pagesize=A4, rightMargin=18*mm, leftMargin=18*mm).build(story)
        mime = "application/pdf"
    else:
        from docx import Document
        doc = Document(); doc.add_heading(title, 0)
        for a in answers:
            doc.add_heading(f"Question {a.get('number', '')}", level=1); doc.add_paragraph(str(a.get("answer", "")))
            v = a.get("verification", {}); doc.add_paragraph(f"Verification: {v.get('status', 'NEEDS_REVIEW')} — {v.get('feedback', '')}")
        doc.add_paragraph((run.result_json or {}).get("verification_note", "")); doc.save(str(target))
        mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    return send_file(target, as_attachment=True, download_name=f"TaskForge-Solution-{run.id}.{fmt}", mimetype=mime)
