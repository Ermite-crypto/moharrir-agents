from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_actual_agents_sdk_contract():
    code = (ROOT / "app" / "agents_system.py").read_text(encoding="utf-8")
    assert "from agents import Agent, handoff" in code
    assert code.count("Agent[WorkflowContext]") >= 9
    assert "quality_agent.handoffs" in code
    assert "correction_agent.handoffs" in code
    assert "nest_handoff_history=True" in code


def test_runtime_contract():
    code = (ROOT / "app" / "workflow.py").read_text(encoding="utf-8")
    for token in ["Runner.run", "OpenAIProvider", "SQLiteSession", "with trace("]:
        assert token in code
    assert "trace_include_sensitive_data=False" in code


def test_key_not_hardcoded():
    for path in ROOT.rglob("*"):
        if path.is_file() and path.suffix in {".py", ".html", ".js", ".toml", ".txt", ".yaml"}:
            text = path.read_text(encoding="utf-8", errors="ignore")
            assert ("sk" + "-proj-") not in text
