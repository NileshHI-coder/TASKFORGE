from datetime import datetime
from ..extensions import db
from ..models.task import Task, Subtask
from ..models.execution import AgentExecution, ActivityLog
from .execution_agents import SpecialistAgent
from ..services.gemini_service import GeminiService

class ExecutionService:
    """Executes one approved queued subtask per request for observable, resumable progress."""
    def run_next(self, task, user_id):
        if not task.plan_approved:
            raise ValueError('Approve the execution plan before starting agents.')
        subtasks = Subtask.query.filter_by(task_id=task.id).order_by(Subtask.id.asc()).all()
        if not subtasks:
            raise ValueError('This task has no subtasks to execute.')
        if any(s.status == 'running' for s in subtasks):
            raise ValueError('A subtask is already running. Refresh the task before continuing.')
        failed = next((s for s in subtasks if s.status == 'failed'), None)
        if failed:
            raise ValueError('A subtask has failed. Retry or resolve it before continuing.')
        pending = next((s for s in subtasks if s.status == 'queued'), None)
        if not pending:
            if all(s.status == 'completed' for s in subtasks):
                task.status = 'verification'
                db.session.commit()
                return {'message': 'All specialist subtasks are complete. Independent verification is next.', 'task': task.to_dict(include_subtasks=True), 'finished': True}
            raise ValueError('No executable queued subtask is available.')
        completed_titles = {s.title for s in subtasks if s.status == 'completed'}
        if any(dep not in completed_titles for dep in (pending.dependencies or [])):
            raise ValueError('This subtask is waiting for one or more dependencies.')
        execution = AgentExecution(task_id=task.id, subtask_id=pending.id, agent_name=pending.agent_type, status='running', input_summary=pending.title, started_at=datetime.utcnow())
        pending.status = 'running'; pending.started_at = datetime.utcnow(); task.status = 'running'
        db.session.add(execution); db.session.commit()
        try:
            output = SpecialistAgent(pending.agent_type).run(pending, {'title': task.title, 'description': task.description})
            if not output or not str(output).strip():
                raise ValueError('The specialist agent returned an empty result.')
            pending.output = str(output).strip(); pending.status = 'completed'; pending.completed_at = datetime.utcnow()
            execution.status = 'completed'; execution.output_summary = pending.output[:4000]; execution.completed_at = datetime.utcnow()
            db.session.add(ActivityLog(user_id=user_id, task_id=task.id, event_type='subtask_completed', message=f'{pending.agent_type} agent completed: {pending.title}'))
            all_done = all(s.status == 'completed' for s in subtasks)
            task.status = 'verification' if all_done else 'running'
            db.session.commit()
            return {'message': f'{pending.agent_type.replace("_", " ").title()} Agent completed: {pending.title}', 'task': task.to_dict(include_subtasks=True), 'finished': all_done}
        except Exception as exc:
            db.session.rollback()
            pending = db.session.get(Subtask, pending.id); execution = db.session.get(AgentExecution, execution.id); task = db.session.get(Task, task.id)
            pending.status = 'failed'; pending.retry_count = (pending.retry_count or 0) + 1
            execution.status = 'failed'; execution.error_summary = str(exc)[:2000]; execution.completed_at = datetime.utcnow()
            task.status = 'failed'; task.error_message = str(exc)[:2000]
            db.session.add(ActivityLog(user_id=user_id, task_id=task.id, event_type='subtask_failed', message=f'{pending.agent_type} agent failed: {pending.title}'))
            db.session.commit()
            raise RuntimeError('Agent execution failed. Review the error and retry this step.') from exc

    def retry(self, task, subtask_id, user_id):
        subtask = Subtask.query.filter_by(id=subtask_id, task_id=task.id).first()
        if not subtask or subtask.status != 'failed':
            raise ValueError('Only a failed subtask belonging to this task can be retried.')
        subtask.status = 'queued'; subtask.output = None; subtask.started_at = None; subtask.completed_at = None
        task.status = 'pending'; task.error_message = None
        db.session.add(ActivityLog(user_id=user_id, task_id=task.id, event_type='subtask_retry_queued', message=f'Retry queued: {subtask.title}'))
        db.session.commit()
        return task.to_dict(include_subtasks=True)

    def verify(self, task, user_id):
        subtasks = Subtask.query.filter_by(task_id=task.id).order_by(Subtask.id.asc()).all()
        if not task.plan_approved or not subtasks or any(s.status != 'completed' for s in subtasks):
            raise ValueError('Complete all specialist subtasks before verification.')
        work = '\n\n'.join(f"SUBTASK: {s.title}\nEXPECTED: {s.expected_output}\nOUTPUT:\n{s.output or ''}" for s in subtasks)
        prompt = ("Independently audit this TaskForge execution. Return concise JSON with keys verdict (pass, needs_review, fail), summary, issues (array), and recommendations (array). Do not claim external verification. A pass requires all outputs to address their expected deliverables and no material unsupported claims.\n\n" + f"TASK: {task.title}\nGOAL: {task.description or ''}\n\n" + work)
        raw = GeminiService().generate(prompt)
        task.result = raw; task.status = 'completed' if '"verdict": "pass"' in raw.lower() or '"verdict":"pass"' in raw.lower() else 'verification'
        task.error_message = None
        db.session.add(AgentExecution(task_id=task.id, agent_name='verification', status='completed', input_summary='Independent review of all subtask outputs', output_summary=raw[:4000], started_at=datetime.utcnow(), completed_at=datetime.utcnow()))
        db.session.add(ActivityLog(user_id=user_id, task_id=task.id, event_type='verification_completed', message='Independent verification review completed.'))
        db.session.commit()
        return {'verification': raw, 'task': task.to_dict(include_subtasks=True)}
