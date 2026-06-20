"""Root Cause Agent — LLM-powered analysis."""
import json
import logging
from langchain_core.messages import SystemMessage, HumanMessage
from app.services.llm import get_llm

logger = logging.getLogger("aiops.root_cause")

SYSTEM_PROMPT = """You are an SRE expert performing root cause analysis on production incidents.

You will receive a JSON context bundle describing a failing service. Analyze it and respond with STRICT JSON only — no prose, no markdown fences. The JSON must have exactly these fields:

{
  "root_cause": "string — the most likely root cause in 1-2 sentences",
  "suggested_fix": "string — actionable remediation steps. NEVER suggest destructive commands like 'rm -rf', 'DROP TABLE', 'kill -9'. Recommend investigation steps and safe fixes only.",
  "severity": "one of: info, warning, critical",
  "confidence": "float between 0.0 and 1.0",
  "title": "string — short incident title under 80 chars"
}

Reason about: connection errors (DNS, TLS, network), HTTP status codes (4xx auth/routing, 5xx server/dependency), response time trends (degradation vs sudden spike), failure rate (intermittent vs sustained).
"""


def analyze(context: dict) -> dict:
    """Run LLM analysis. Returns a dict with root_cause, suggested_fix, severity, confidence, title."""
    llm = get_llm()
    user_msg = "Analyze this incident context and respond with strict JSON:\n\n" + json.dumps(
        context, indent=2
    )

    try:
        response = llm.invoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_msg),
        ])
        raw = response.content.strip()
        # Strip markdown fences if model added them
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()

        result = json.loads(raw)
        # Validate required fields with defaults
        return {
            "root_cause": result.get("root_cause", "Unknown"),
            "suggested_fix": result.get("suggested_fix", "Investigate manually"),
            "severity": result.get("severity", "warning"),
            "confidence": float(result.get("confidence", 0.5)),
            "title": result.get("title", "Service failure detected")[:200],
        }
    except Exception as e:
        logger.error(f"LLM analysis failed: {e}")
        return {
            "root_cause": f"LLM analysis failed: {str(e)[:200]}",
            "suggested_fix": "Manual investigation required.",
            "severity": "warning",
            "confidence": 0.0,
            "title": "Service failure (LLM unavailable)",
        }
