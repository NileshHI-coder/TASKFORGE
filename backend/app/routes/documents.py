import os
import re
from pathlib import Path
from datetime import datetime
from flask import Blueprint, request, jsonify, g, current_app, send_file
from werkzeug.utils import secure_filename
from ..extensions import db
from ..models.task import Task
from ..models.generated_file import GeneratedFile
from ..utils.auth import require_auth
from ..services.gemini_service import GeminiService

documents_bp = Blueprint("documents", __name__)


def create_export(task, user_id, title, content, fmt):
    base_dir = Path(current_app.root_path) / "storage" / "generated"
    base_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
    safe = secure_filename(title)[:70] or "TaskForge-Document"
    filename = f"{safe}-{stamp}.{fmt}"
    path = base_dir / filename
    if fmt == "pdf":
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import mm
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from xml.sax.saxutils import escape
        doc = SimpleDocTemplate(str(path), pagesize=A4, rightMargin=20*mm, leftMargin=20*mm, topMargin=18*mm, bottomMargin=18*mm)
        styles = getSampleStyleSheet(); story = [Paragraph(escape(title), styles["Title"]), Spacer(1, 12)]
        for block in content.split("\n"):
            clean = escape(block.strip())
            if clean:
                story.append(Paragraph(clean, styles["BodyText"]))
                story.append(Spacer(1, 6))
        doc.build(story)
        mime = "application/pdf"
    else:
        from docx import Document
        doc = Document(); doc.add_heading(title, 0)
        for block in content.split("\n"):
            if block.strip(): doc.add_paragraph(block.strip())
        doc.save(str(path)); mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    record = GeneratedFile(task_id=task.id, filename=filename, storage_path=str(path), mime_type=mime)
    db.session.add(record); db.session.commit()
    return record

@documents_bp.post("/generate")
@require_auth
def generate_document():
    data = request.get_json(silent=True) or {}
    task_id = data.get("task_id")
    task = Task.query.filter_by(id=task_id, user_id=g.current_user.id).first() if task_id else None
    if not task:
        return jsonify({"error": "Choose a valid task from your workspace before generating a document."}), 400
    title = (data.get("title") or task.title).strip()[:180]
    instructions = (data.get("instructions") or "").strip()
    source_text = (data.get("content") or task.result or task.description or "").strip()
    if not instructions and not source_text:
        return jsonify({"error": "Provide source content or document instructions."}), 400
    if len(source_text) > 30000 or len(instructions) > 4000:
        return jsonify({"error": "Document input is too long. Keep content under 30,000 characters and instructions under 4,000."}), 400
    fmt = (data.get("format") or "docx").lower()
    if fmt not in {"pdf", "docx"}:
        return jsonify({"error": "Supported formats are PDF and DOCX."}), 400
    try:
        prompt = ("Create a clear, professional document body. Follow the user's instructions, use only facts in the supplied content, "
                  "do not invent references or data, and mark missing information instead of guessing. Return plain text with useful headings.\n\n"
                  f"DOCUMENT TITLE: {title}\nINSTRUCTIONS: {instructions}\nSOURCE CONTENT:\n{source_text}")
        content = GeminiService().generate(prompt)
        if not content.strip():
            raise RuntimeError("Gemini returned empty content")
        record = create_export(task, g.current_user.id, title, content, fmt)
        return jsonify({"file": record.to_dict(), "download_url": f"/documents/files/{record.id}/download"}), 201
    except ValueError as exc:
        db.session.rollback()
        return jsonify({"error": str(exc)}), 503
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Document generation failed. Check Gemini configuration and try again."}), 502

@documents_bp.get("/files")
@require_auth
def list_files():
    owned_task_ids = [t.id for t in Task.query.filter_by(user_id=g.current_user.id).with_entities(Task.id).all()]
    files = GeneratedFile.query.filter(GeneratedFile.task_id.in_(owned_task_ids)).order_by(GeneratedFile.created_at.desc()).limit(100).all() if owned_task_ids else []
    return jsonify({"files": [f.to_dict() for f in files]})

@documents_bp.get("/files/<int:file_id>/download")
@require_auth
def download_file(file_id):
    record = (GeneratedFile.query.join(Task, GeneratedFile.task_id == Task.id)
              .filter(GeneratedFile.id == file_id, Task.user_id == g.current_user.id).first_or_404())
    path = Path(record.storage_path).resolve()
    storage_root = (Path(current_app.root_path) / "storage" / "generated").resolve()
    if storage_root not in path.parents or not path.is_file():
        return jsonify({"error": "Generated file is unavailable."}), 404
    return send_file(path, as_attachment=True, download_name=record.filename, mimetype=record.mime_type)
