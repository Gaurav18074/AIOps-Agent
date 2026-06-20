"""LangGraph orchestrator wiring the agents into a state machine."""
import logging
from typing import TypedDict
from langgraph.graph import StateGraph, END

logger = logging.getLogger("aiops.graph")


class AgentState(TypedDict, total=False):
    site_id: int
    check_id: int
    context: dict
    analysis: dict
    incident_id: int


def _log_analysis_node(state: AgentState) -> AgentState:
    from app.agents.log_analysis import analyze
    state["context"] = analyze(state["site_id"], state["check_id"])
    return state


def _root_cause_node(state: AgentState) -> AgentState:
    from app.agents.root_cause import analyze
    state["analysis"] = analyze(state["context"])
    return state


def _reporter_node(state: AgentState) -> AgentState:
    from app.agents.reporter import create_incident
    state["incident_id"] = create_incident(
        state["site_id"], state["context"], state["analysis"]
    )
    return state


def _notifier_node(state: AgentState) -> AgentState:
    from app.agents.notifier import notify
    notify(state["incident_id"])
    return state


def build_graph():
    g = StateGraph(AgentState)
    g.add_node("log_analysis", _log_analysis_node)
    g.add_node("root_cause", _root_cause_node)
    g.add_node("reporter", _reporter_node)
    g.add_node("notifier", _notifier_node)

    g.set_entry_point("log_analysis")
    g.add_edge("log_analysis", "root_cause")
    g.add_edge("root_cause", "reporter")
    g.add_edge("reporter", "notifier")
    g.add_edge("notifier", END)

    return g.compile()


_compiled_graph = None


def get_graph():
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_graph()
    return _compiled_graph


def run_pipeline(site_id: int, check_id: int):
    """Run the full agent pipeline for a failed check."""
    try:
        graph = get_graph()
        result = graph.invoke({"site_id": site_id, "check_id": check_id})
        logger.info(f"Pipeline complete: incident_id={result.get('incident_id')}")
        return result
    except Exception as e:
        logger.exception(f"Pipeline failed: {e}")


def run_pipeline_for_incident(incident_id: int):
    """Re-run pipeline for an existing incident (uses its raw_context)."""
    from app.database import SessionLocal
    from app.models import Incident
    db = SessionLocal()
    try:
        inc = db.get(Incident, incident_id)
        if not inc or not inc.raw_context:
            return
        from app.agents.root_cause import analyze
        analysis = analyze(inc.raw_context)
        inc.root_cause = analysis["root_cause"]
        inc.suggested_fix = analysis["suggested_fix"]
        inc.confidence = analysis["confidence"]
        inc.severity = analysis["severity"]
        db.commit()
        logger.info(f"Re-ran pipeline for incident #{incident_id}")
    finally:
        db.close()
