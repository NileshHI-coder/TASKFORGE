from datetime import datetime
from ..extensions import db

class DataAnalysisRun(db.Model):
    __tablename__ = "data_analysis_runs"
    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    filename = db.Column(db.String(255), nullable=False)
    storage_path = db.Column(db.String(500), nullable=False)
    row_count = db.Column(db.Integer, nullable=False, default=0)
    column_count = db.Column(db.Integer, nullable=False, default=0)
    result_json = db.Column(db.JSON, nullable=False)
    ai_insights = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {"id": self.id, "filename": self.filename, "row_count": self.row_count,
                "column_count": self.column_count, "result": self.result_json,
                "ai_insights": self.ai_insights,
                "created_at": self.created_at.isoformat() if self.created_at else None}
