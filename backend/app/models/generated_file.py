from datetime import datetime
from ..extensions import db

class GeneratedFile(db.Model):
    __tablename__ = "generated_files"
    id = db.Column(db.BigInteger, primary_key=True)
    task_id = db.Column(db.BigInteger, db.ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    filename = db.Column(db.String(255), nullable=False)
    storage_path = db.Column(db.String(500), nullable=False)
    mime_type = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {"id": self.id, "task_id": self.task_id, "filename": self.filename,
                "mime_type": self.mime_type, "created_at": self.created_at.isoformat() if self.created_at else None}
