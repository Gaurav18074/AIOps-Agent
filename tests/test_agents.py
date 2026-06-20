"""Smoke tests for agent components — no LLM calls."""
from app.agents.graph import build_graph


def test_graph_compiles():
    g = build_graph()
    assert g is not None
