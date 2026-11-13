def test_project_has_required_env_example():
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    text = (root / ".env.example").read_text()
    assert "TAVILY_API_KEY" in text
    assert "GEMINI_API_KEY" in text
