from flask import Blueprint, jsonify
from ..utils.auth import require_auth
from ..services.tavily_service import TavilyService

integrations_bp = Blueprint("integrations", __name__)

@integrations_bp.post("/tavily/test")
@require_auth
def tavily_test():
    try:
        results = TavilyService().search("TaskForge AI agent orchestration", max_results=3)
        return jsonify({"connected": True, "results": results})
    except ValueError as exc:
        return jsonify({"connected": False, "error": str(exc)}), 400
    except Exception:
        return jsonify({"connected": False, "error": "Tavily request failed. Check the API key and network, then try again."}), 502
