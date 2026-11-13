"""Specialist agent dispatch. Each agent returns evidence-backed or clearly scoped output."""
from ..services.gemini_service import GeminiService
from .research_agent import ResearchAgent

class SpecialistAgent:
    def __init__(self, agent_type):
        self.agent_type = agent_type

    def run(self, subtask, task_context):
        goal = f"TASK: {task_context['title']}\nTASK CONTEXT: {task_context.get('description') or 'Not provided'}\nSUBTASK: {subtask.title}\nINSTRUCTIONS: {subtask.description or ''}\nEXPECTED OUTPUT: {subtask.expected_output or 'A useful, structured result'}"
        if self.agent_type == 'research':
            result = ResearchAgent().run(goal)
            return result['report'] + self._sources(result.get('sources', []))
        if self.agent_type == 'document':
            return GeminiService().generate("You are TaskForge Document Agent. Create a polished, well-structured draft based only on the supplied task context. Clearly label assumptions and missing information.\n" + goal)
        if self.agent_type == 'data_analysis':
            return GeminiService().generate("You are TaskForge Data Analysis Agent. The user has not necessarily supplied a dataset. Do not invent numerical results. If no dataset is available, provide an analysis plan, required columns, validation checks, and recommended visualizations.\n" + goal)
        if self.agent_type == 'project_planning':
            return GeminiService().generate("You are TaskForge Project Planning Agent. Produce actionable phases, milestones, dependencies, owners by role, risks, and acceptance criteria.\n" + goal)
        if self.agent_type == 'exam_solver':
            return GeminiService().generate("You are TaskForge Exam Solver Agent. Solve only the question text actually supplied. Show steps, state assumptions, and flag ambiguity. If no actual question is included, explain exactly what question/file input is needed; do not invent a question or claim a verified answer.\n" + goal)
        if self.agent_type == 'verification':
            return GeminiService().generate("You are an independent TaskForge Verification Agent. Review the provided work for factual support, completeness against expected output, logical consistency, and unsupported claims. Return: verdict (pass/needs_review/fail), issues, corrections, and confidence. Never claim external facts were verified unless evidence is present.\n" + goal)
        raise ValueError(f'Unsupported agent type: {self.agent_type}')

    @staticmethod
    def _sources(sources):
        if not sources:
            return "\n\nSources: No web sources returned."
        lines = ["\n\n## Sources"]
        for i, source in enumerate(sources, 1):
            lines.append(f"[{i}] {source.get('title') or 'Untitled'} — {source.get('url') or 'URL unavailable'}" + (f" (Published: {source['published_date']})" if source.get('published_date') else ''))
        return '\n'.join(lines)
