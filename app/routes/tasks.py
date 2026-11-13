from flask import Blueprint, request, jsonify, g
from ..extensions import db
from ..models.task import Task, Subtask
from ..utils.auth import require_auth
from ..agents.planner_agent import PlannerAgent
import traceback

tasks_bp = Blueprint("tasks", __name__)

@tasks_bp.get("")
@require_auth
def list_tasks():
    tasks = Task.query.filter_by(user_id=g.current_user.id).order_by(Task.created_at.desc()).all()
    return jsonify({"tasks": [t.to_dict() for t in tasks]})

@tasks_bp.post("")
@require_auth
def create_task():
    data = request.get_json(silent=True) or {}
    title = data.get("title", "").strip(); description = data.get("description", "").strip()
    category = data.get("category", "general").strip().lower()
    if not title or len(title) > 255:
        return jsonify({"error": "Task title is required (maximum 255 characters)."}), 400
    if category not in {"general", "research", "document", "planning", "data_analysis", "exam_solver"}:
        return jsonify({"error": "Unsupported task category."}), 400
    task = Task(user_id=g.current_user.id, title=title, description=description, category=category)
    db.session.add(task); db.session.commit()
    return jsonify({"task": task.to_dict(include_subtasks=True)}), 201

@tasks_bp.get("/<int:task_id>")
@require_auth
def get_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=g.current_user.id).first_or_404()
    return jsonify({"task": task.to_dict(include_subtasks=True)})

@tasks_bp.post("/<int:task_id>/plan")
@require_auth
def generate_task_plan(task_id):
    task = Task.query.filter_by(id=task_id, user_id=g.current_user.id).first_or_404()
    if task.plan_approved:
        return jsonify({"error": "This plan has already been approved and cannot be replaced."}), 409
    goal = "\n".join(part for part in [task.title, task.description or ""] if part)
    try:
        plan = PlannerAgent().create_plan(goal, task.category)
        Subtask.query.filter_by(task_id=task.id).delete()
        for item in plan["subtasks"]:
            db.session.add(Subtask(
                task_id=task.id, title=item["title"], description=item["description"],
                agent_type=item["agent_type"], expected_output=item["expected_output"],
                dependencies=item["dependencies"], status="waiting_for_approval"
            ))
        task.status = "planning"
        task.result = plan["summary"]
        task.error_message = None
        db.session.commit()
        return jsonify({"task": task.to_dict(include_subtasks=True), "plan_summary": plan["summary"]})
    except ValueError as exc:
        db.session.rollback()
        message = str(exc)
        return jsonify({"error": message}), (503 if "GEMINI_API_KEY" in message else 422)
    
    except Exception as exc:
        db.session.rollback()
        print("\n========== TASKFORGE PLANNER ERROR ==========")
        traceback.print_exc()
        print("Error type:", type(exc).__name__)
        print("Error message:", str(exc))
        print("=============================================\n")
        return jsonify({
            "error": "Planner failed. Check the backend terminal for the actual error.",
            "error_type": type(exc).__name__
        }), 502
@tasks_bp.post("/<int:task_id>/approve-plan")
@require_auth
def approve_task_plan(task_id):
    task = Task.query.filter_by(id=task_id, user_id=g.current_user.id).first_or_404()
    subtasks = Subtask.query.filter_by(task_id=task.id).all()
    if not subtasks:
        return jsonify({"error": "Generate a plan before approving it."}), 400
    if task.plan_approved:
        return jsonify({"error": "This plan is already approved."}), 409
    task.plan_approved = True
    task.status = "pending"
    for subtask in subtasks:
        subtask.status = "queued"
    db.session.commit()
    return jsonify({"message": "Plan approved. Specialist agents can now execute the queued subtasks one step at a time.", "task": task.to_dict(include_subtasks=True)})

@tasks_bp.delete("/<int:task_id>")
@require_auth
def delete_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=g.current_user.id).first_or_404()
    db.session.delete(task); db.session.commit()
    return jsonify({"message": "Task deleted."})

@tasks_bp.post('/<int:task_id>/execute-next')
@require_auth
def execute_next_subtask(task_id):
    from ..agents.execution_service import ExecutionService
    task = Task.query.filter_by(id=task_id, user_id=g.current_user.id).first_or_404()
    try:
        result = ExecutionService().run_next(task, g.current_user.id)
        return jsonify(result)
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400
    except RuntimeError as exc:
        task = Task.query.filter_by(id=task_id, user_id=g.current_user.id).first()
        return jsonify({'error': str(exc), 'task': task.to_dict(include_subtasks=True) if task else None}), 502

@tasks_bp.post('/<int:task_id>/subtasks/<int:subtask_id>/retry')
@require_auth
def retry_subtask(task_id, subtask_id):
    from ..agents.execution_service import ExecutionService
    task = Task.query.filter_by(id=task_id, user_id=g.current_user.id).first_or_404()
    try:
        updated = ExecutionService().retry(task, subtask_id, g.current_user.id)
        return jsonify({'message': 'Failed subtask queued for retry.', 'task': updated})
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400

@tasks_bp.post('/<int:task_id>/verify')
@require_auth
def verify_task(task_id):
    from ..agents.execution_service import ExecutionService
    task = Task.query.filter_by(id=task_id, user_id=g.current_user.id).first_or_404()
    try:
        return jsonify(ExecutionService().verify(task, g.current_user.id))
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400
    except Exception:
        db.session.rollback()
        return jsonify({'error': 'Independent verification failed. Check the Gemini API configuration and try again.'}), 502

@tasks_bp.get('/<int:task_id>/executions')
@require_auth
def task_executions(task_id):
    from ..models.execution import AgentExecution, ActivityLog
    task = Task.query.filter_by(id=task_id, user_id=g.current_user.id).first_or_404()
    executions = AgentExecution.query.filter_by(task_id=task.id).order_by(AgentExecution.id.desc()).all()
    activity = ActivityLog.query.filter_by(task_id=task.id).order_by(ActivityLog.id.desc()).limit(30).all()
    return jsonify({'executions': [e.to_dict() for e in executions], 'activity': [{'event_type': a.event_type, 'message': a.message, 'created_at': a.created_at.isoformat() if a.created_at else None} for a in activity]})
