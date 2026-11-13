from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from .extensions import db
from .routes.auth import auth_bp
from .routes.tasks import tasks_bp
from .routes.integrations import integrations_bp
from .routes.research import research_bp
from .routes.documents import documents_bp
from .routes.data_analysis import data_bp
from .routes.exam_solver import exam_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app, resources={r"/api/*": {"origins": [app.config["FRONTEND_URL"]]}}, supports_credentials=False)
    db.init_app(app)
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(tasks_bp, url_prefix="/api/tasks")
    app.register_blueprint(integrations_bp, url_prefix="/api/integrations")
    app.register_blueprint(research_bp, url_prefix="/api/research")
    app.register_blueprint(documents_bp, url_prefix="/api/documents")
    app.register_blueprint(data_bp, url_prefix="/api/data")
    app.register_blueprint(exam_bp, url_prefix="/api/exams")

    @app.get("/api/health")
    def health():
        try:
            db.session.execute(db.text("SELECT 1"))
            database = "connected"
        except Exception:
            db.session.rollback()
            database = "disconnected"
        return jsonify({"status": "ok", "database": database})

    @app.errorhandler(413)
    def too_large(_):
        return jsonify({"error": "Upload exceeds the configured size limit."}), 413

    return app
