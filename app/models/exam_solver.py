from datetime import datetime
from ..extensions import db

class ExamRun(db.Model):
    __tablename__ = "exam_runs"
    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    filename = db.Column(db.String(255), nullable=False)
    storage_path = db.Column(db.String(500), nullable=False)
    extracted_text = db.Column(db.Text, nullable=False)
    result_json = db.Column(db.JSON, nullable=False)
    status = db.Column(db.String(24), nullable=False, default="extracted")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {"id": self.id, "filename": self.filename, "status": self.status,
                "result": self.result_json, "created_at": self.created_at.isoformat() if self.created_at else None}
