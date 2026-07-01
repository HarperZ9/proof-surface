"""Trace-to-receipt adapters: real observability exports -> normalized trace.

Keep your existing observability stack; attach receipts. These adapters flatten
vendor trace exports (OpenTelemetry OTLP/JSON, LangSmith/Langfuse-style run trees)
into the normalized trace shape proof_surface.agent_action.import_trace ingests,
so an agent-action proof packet can be built from data teams already collect.
"""

from __future__ import annotations

from .otel import normalize_otel
from .run_tree import normalize_run_tree

__all__ = ["normalize_otel", "normalize_run_tree"]
