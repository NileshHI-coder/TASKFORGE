import json, uuid
from pathlib import Path
import numpy as np
import pandas as pd
from flask import Blueprint, request, jsonify, g, current_app
from werkzeug.utils import secure_filename
from ..extensions import db
from ..models.data_analysis import DataAnalysisRun
from ..utils.auth import require_auth
from ..services.gemini_service import GeminiService

data_bp = Blueprint("data_analysis", __name__)
ALLOWED = {"csv", "xlsx", "xls"}

def build_analysis(frame):
    numeric = frame.select_dtypes(include=["number"])
    stats = {}
    for col in numeric.columns:
        series = pd.to_numeric(frame[col], errors="coerce").dropna()
        if len(series):
            stats[str(col)] = {
                "count": int(series.count()), "mean": round(float(series.mean()), 4),
                "median": round(float(series.median()), 4),
                "std": round(float(series.std()), 4) if len(series) > 1 else 0,
                "min": round(float(series.min()), 4), "max": round(float(series.max()), 4)
            }
    histograms = {}
    numeric_series = {}
    for col in numeric.columns:
        series = pd.to_numeric(frame[col], errors="coerce").dropna()
        if len(series):
            counts, edges = np.histogram(series.to_numpy(dtype=float), bins=min(10, max(3, int(np.sqrt(len(series))))))
            histograms[str(col)] = [{"range": f"{edges[i]:.3g}–{edges[i+1]:.3g}", "count": int(counts[i])} for i in range(len(counts))]
            numeric_series[str(col)] = [float(v) for v in series.head(50).tolist()]
    correlations = []
    if len(numeric.columns) >= 2:
        corr = numeric.corr(numeric_only=True).fillna(0)
        for i, col in enumerate(corr.columns):
            for other in list(corr.columns)[i+1:]:
                correlations.append({"x": str(col), "y": str(other), "value": round(float(corr.loc[col, other]), 4)})
    missing = {str(c): int(v) for c, v in frame.isna().sum().items()}
    preview_frame = frame.head(10).astype(object).where(pd.notna(frame.head(10)), None)
    preview = {"columns": [str(c) for c in frame.columns],
               "rows": [[(v.isoformat() if hasattr(v, "isoformat") else v) for v in row] for row in preview_frame.values.tolist()]}
    distributions = {}
    for col in frame.columns:
        if col not in numeric.columns:
            counts = frame[col].dropna().astype(str).value_counts().head(8)
            if len(counts):
                distributions[str(col)] = [{"label": str(k), "value": int(v)} for k, v in counts.items()]
    return {
        "shape": {"rows": int(frame.shape[0]), "columns": int(frame.shape[1])},
        "columns": [{"name": str(c), "dtype": str(frame[c].dtype), "missing": int(frame[c].isna().sum()),
                     "unique": int(frame[c].nunique(dropna=True))} for c in frame.columns],
        "missing_values": missing, "total_missing": int(frame.isna().sum().sum()),
        "duplicate_rows": int(frame.duplicated().sum()), "numeric_summary": stats,
        "correlations": correlations, "categorical_distributions": distributions, "histograms": histograms, "numeric_series": numeric_series, "preview": preview
    }

@data_bp.post("/upload")
@require_auth
def upload_dataset():
    file = request.files.get("file")
    if not file or not file.filename:
        return jsonify({"error": "Select a CSV or Excel file to upload."}), 400
    original = secure_filename(file.filename)
    ext = original.rsplit(".", 1)[-1].lower() if "." in original else ""
    if ext not in ALLOWED:
        return jsonify({"error": "Only CSV, XLSX and XLS files are supported."}), 400
    raw = file.read()
    if not raw or len(raw) > 10 * 1024 * 1024:
        return jsonify({"error": "File must be non-empty and no larger than 10 MB."}), 400
    folder = Path(current_app.root_path) / "storage" / "datasets"
    folder.mkdir(parents=True, exist_ok=True)
    stored = f"{uuid.uuid4().hex}.{ext}"
    path = folder / stored
    path.write_bytes(raw)
    try:
        frame = pd.read_csv(path) if ext == "csv" else pd.read_excel(path)
        if frame.empty or len(frame.columns) == 0:
            raise ValueError("The uploaded dataset has no data rows or columns.")
        if frame.shape[0] > 100000 or frame.shape[1] > 150:
            raise ValueError("Dataset limit is 100,000 rows and 150 columns.")
        result = build_analysis(frame)
        record = DataAnalysisRun(user_id=g.current_user.id, filename=original, storage_path=str(path),
                                 row_count=int(frame.shape[0]), column_count=int(frame.shape[1]), result_json=result)
        db.session.add(record); db.session.commit()
        return jsonify({"analysis": record.to_dict()}), 201
    except (ValueError, pd.errors.ParserError, ImportError) as exc:
        path.unlink(missing_ok=True)
        db.session.rollback()
        return jsonify({"error": str(exc) or "Could not read this dataset."}), 400
    except Exception:
        path.unlink(missing_ok=True)
        db.session.rollback()
        return jsonify({"error": "Dataset analysis failed. Check that the file is a valid CSV or Excel workbook."}), 400

@data_bp.get("/runs")
@require_auth
def list_runs():
    runs = DataAnalysisRun.query.filter_by(user_id=g.current_user.id).order_by(DataAnalysisRun.created_at.desc()).limit(30).all()
    return jsonify({"runs": [r.to_dict() for r in runs]})

@data_bp.get("/runs/<int:run_id>")
@require_auth
def get_run(run_id):
    run = DataAnalysisRun.query.filter_by(id=run_id, user_id=g.current_user.id).first_or_404()
    return jsonify({"analysis": run.to_dict()})

@data_bp.post("/runs/<int:run_id>/insights")
@require_auth
def generate_insights(run_id):
    run = DataAnalysisRun.query.filter_by(id=run_id, user_id=g.current_user.id).first_or_404()
    result = run.result_json or {}
    prompt = ("Act as a careful data analyst. Explain only patterns supported by this summary. "
              "Do not infer causation, do not invent context, mention limitations and missing values. "
              "Give 4-6 concise findings and 2 practical next checks.\nDATA SUMMARY:\n" +
              json.dumps({k: result.get(k) for k in ["shape","columns","missing_values","duplicate_rows","numeric_summary","correlations","categorical_distributions"]}, ensure_ascii=False))
    try:
        insights = GeminiService().generate(prompt)
        if not insights.strip():
            raise RuntimeError("Empty AI response")
        run.ai_insights = insights
        db.session.commit()
        return jsonify({"ai_insights": insights})
    except ValueError as exc:
        db.session.rollback()
        return jsonify({"error": str(exc)}), 503
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Gemini insight generation failed. Check API configuration and retry."}), 502
