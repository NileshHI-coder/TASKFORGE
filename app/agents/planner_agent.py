import json
from ..services.gemini_service import GeminiService

ALLOWED_AGENTS = {"research", "document", "data_analysis", "project_planning", "exam_solver", "verification"}

class PlannerAgent:
    """Creates a bounded, structured plan for user review before execution."""
    def create_plan(self, goal, category="general"):
        prompt = f"""You are the TaskForge Planner Agent. Convert the user's goal into a practical execution plan.
Return ONLY valid JSON with this exact structure:
{{"summary":"one concise paragraph","category":"{category}","subtasks":[{{"title":"short action title","description":"specific instructions","agent_type":"research|document|data_analysis|project_planning|exam_solver|verification","expected_output":"concrete deliverable","dependencies":["title of an earlier subtask"]}}]}}
Rules:
- Create 3 to 8 ordered subtasks, not one giant task.
- Use only the listed agent_type values.
- Dependencies must refer to earlier subtask titles; use [] when there are none.
- Make outputs measurable and relevant to the goal.
- Do not claim any work has already been executed.
Goal: {goal}
Requested category: {category}"""
        raw = GeminiService().generate(prompt)
        try:
            cleaned = raw.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1].rsplit("```", 1)[0].strip()
            data = json.loads(cleaned)
            subtasks = data.get("subtasks")
            if not isinstance(subtasks, list) or not 1 <= len(subtasks) <= 12:
                raise ValueError("The plan must contain between 1 and 12 subtasks.")
            titles = set()
            normalized = []
            for item in subtasks:
                if not isinstance(item, dict):
                    raise ValueError("A subtask is not a valid object.")
                title = str(item.get("title", "")).strip()
                agent = str(item.get("agent_type", "")).strip().lower()
                if not title or len(title) > 255 or agent not in ALLOWED_AGENTS:
                    raise ValueError("A subtask has a missing title or unsupported agent type.")
                dependencies = item.get("dependencies", [])
                if not isinstance(dependencies, list) or any(dep not in titles for dep in dependencies):
                    raise ValueError("Dependencies must reference earlier subtask titles.")
                titles.add(title)
                normalized.append({
                    "title": title,
                    "description": str(item.get("description", "")).strip(),
                    "agent_type": agent,
                    "expected_output": str(item.get("expected_output", "")).strip(),
                    "dependencies": dependencies,
                })
            return {"summary": str(data.get("summary", "")).strip(), "category": category, "subtasks": normalized}
        except Exception as exc:
            raise ValueError(f"Planner returned an invalid plan: {exc}") from exc
