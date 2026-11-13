import json
import pytest
pytest.importorskip("flask")
from backend.app.agents.planner_agent import PlannerAgent
from backend.app.agents import planner_agent


def test_planner_accepts_valid_ordered_dependencies(monkeypatch):
    payload = {
        "summary": "Research, analyze, and report.",
        "subtasks": [
            {"title": "Research sources", "description": "Collect reliable sources", "agent_type": "research", "expected_output": "Source list", "dependencies": []},
            {"title": "Write report", "description": "Draft findings", "agent_type": "document", "expected_output": "DOCX report", "dependencies": ["Research sources"]},
        ],
    }
    monkeypatch.setattr(planner_agent.GeminiService, "generate", lambda self, prompt: json.dumps(payload))
    plan = PlannerAgent().create_plan("Create a report")
    assert len(plan["subtasks"]) == 2
    assert plan["subtasks"][1]["dependencies"] == ["Research sources"]


def test_planner_rejects_forward_dependency(monkeypatch):
    payload = {
        "summary": "Invalid plan",
        "subtasks": [
            {"title": "First", "description": "", "agent_type": "research", "expected_output": "", "dependencies": ["Second"]},
            {"title": "Second", "description": "", "agent_type": "document", "expected_output": "", "dependencies": []},
        ],
    }
    monkeypatch.setattr(planner_agent.GeminiService, "generate", lambda self, prompt: json.dumps(payload))
    with pytest.raises(ValueError, match="Dependencies must reference earlier"):
        PlannerAgent().create_plan("Create a report")
