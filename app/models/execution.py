from datetime import datetime
from ..extensions import db

class AgentExecution(db.Model):
    __tablename__ = 'agent_executions'
    id = db.Column(db.BigInteger, primary_key=True)
    task_id = db.Column(db.BigInteger, db.ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False, index=True)
    subtask_id = db.Column(db.BigInteger, db.ForeignKey('subtasks.id', ondelete='SET NULL'))
    agent_name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(40), nullable=False)
    input_summary = db.Column(db.Text)
    output_summary = db.Column(db.Text)
    error_summary = db.Column(db.Text)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)

    def to_dict(self):
        return {'id': self.id, 'subtask_id': self.subtask_id, 'agent_name': self.agent_name, 'status': self.status, 'input_summary': self.input_summary, 'output_summary': self.output_summary, 'error_summary': self.error_summary, 'started_at': self.started_at.isoformat() if self.started_at else None, 'completed_at': self.completed_at.isoformat() if self.completed_at else None}

class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'
    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id', ondelete='SET NULL'))
    task_id = db.Column(db.BigInteger, db.ForeignKey('tasks.id', ondelete='CASCADE'), index=True)
    event_type = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
