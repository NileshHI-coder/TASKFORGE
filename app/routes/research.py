from flask import Blueprint, request, jsonify, g
from ..extensions import db
from ..models.task import Task
from ..models.generated_file import GeneratedFile
from ..models.execution import ActivityLog
from ..utils.auth import require_auth
from ..agents.research_agent import ResearchAgent
from .documents import create_export

research_bp = Blueprint("research", __name__)

@research_bp.post("/<int:task_id>/run")
@require_auth
def run_research(task_id):
    task = Task.query.filter_by(id=task_id, user_id=g.current_user.id).first_or_404()
    if task.category not in {"research", "general", "planning"}:
        return jsonify({"error": "Research can only be run on research, general, or planning tasks."}), 400
    data = request.get_json(silent=True) or {}
    query = (data.get("query") or task.description or task.title).strip()
    if not query or len(query) > 2000:
        return jsonify({"error": "Research query is required and must be under 2,000 characters."}), 400
    include_domains = data.get("include_domains") or []
    exclude_domains = data.get("exclude_domains") or []
    if not isinstance(include_domains, list) or not isinstance(exclude_domains, list):
        return jsonify({"error": "Domain filters must be lists of domain names."}), 400
    try:
        result = ResearchAgent().run(query, max_results=data.get("max_results", 6),
                                     search_depth=data.get("search_depth", "advanced"),
                                     topic=data.get("topic", "general"),
                                     include_domains=include_domains, exclude_domains=exclude_domains)
        task.result = result["report"]
        task.status = "completed" if result["sources"] else "pending"
        task.error_message = None
        db.session.add(ActivityLog(user_id=g.current_user.id, task_id=task.id,
                                   event_type="research_completed", message=f"Research completed with {len(result['sources'])} source(s)."))
        db.session.commit()
        return jsonify({"task_id": task.id, **result})
    except ValueError as exc:
        db.session.rollback()
        return jsonify({"error": str(exc)}), 503
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Research failed. Verify the Tavily and Gemini API keys and try again."}), 502

@research_bp.post("/<int:task_id>/export")
@require_auth
def export_research(task_id):
    task = Task.query.filter_by(id=task_id, user_id=g.current_user.id).first_or_404()
    if not task.result:
        return jsonify({"error": "Run research before exporting a report."}), 400
    data = request.get_json(silent=True) or {}
    fmt = data.get("format", "pdf").lower()
    if fmt not in {"pdf", "docx"}:
        return jsonify({"error": "Supported formats are PDF and DOCX."}), 400
    try:
        record = create_export(task, g.current_user.id, f"Research Report - {task.title}", task.result, fmt)
        return jsonify({"file": record.to_dict(), "download_url": f"/documents/files/{record.id}/download"}), 201
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Could not generate the report file."}), 500
