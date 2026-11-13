from datetime import datetime
from ..extensions import db

class Task(db.Model):
    __tablename__ = "tasks"
    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50), nullable=False, default="general")
    status = db.Column(db.String(30), nullable=False, default="pending")
    plan_approved = db.Column(db.Boolean, nullable=False, default=False)
    result = db.Column(db.Text)
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self, include_subtasks=False):
        data = {
            "id": self.id, "title": self.title, "description": self.description,
            "category": self.category, "status": self.status,
            "plan_approved": bool(self.plan_approved), "plan_summary": self.result,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_subtasks:
            data["subtasks"] = [item.to_dict() for item in Subtask.query.filter_by(task_id=self.id).order_by(Subtask.id.asc()).all()]
        return data

class Subtask(db.Model):
    __tablename__ = "subtasks"
    id = db.Column(db.BigInteger, primary_key=True)
    task_id = db.Column(db.BigInteger, db.ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    agent_type = db.Column(db.String(80), nullable=False)
    status = db.Column(db.String(40), nullable=False, default="queued")
    expected_output = db.Column(db.Text)
    dependencies = db.Column(db.JSON, nullable=False, default=list)
    output = db.Column(db.Text)
    retry_count = db.Column(db.Integer, nullable=False, default=0)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id, "title": self.title, "description": self.description,
            "agent_type": self.agent_type, "status": self.status,
            "expected_output": self.expected_output,
            "dependencies": self.dependencies or [],
            "output": self.output,
        }
