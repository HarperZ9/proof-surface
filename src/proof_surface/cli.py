"""Unified `telos proof <domain>` dispatcher.

One buyer-facing seam over the proof-packet family: pick a domain, get the same
mental model. Each domain owns its own arguments; this only routes.

    telos-proof agent-action       --trace ... --authorization ... --claim ...
    telos-proof visual-measurement --input ... --claim ...
    telos-proof research-claim     --input ... --claim ...
"""

from __future__ import annotations

import importlib
import sys

_DOMAINS = {
    "agent-action": "proof_surface.agent_action.cli",
    "visual-measurement": "proof_surface.visual_measurement.cli",
    "research-claim": "proof_surface.research_claim.cli",
    "model-eval": "proof_surface.model_eval.cli",
    "optimization-workflow": "proof_surface.optimization_workflow.cli",
    "rollout-receipt": "proof_surface.rollout_receipt.cli",
}


def _usage() -> str:
    domains = "\n".join(f"    telos-proof {name} ..." for name in sorted(_DOMAINS))
    return "usage: telos-proof <domain> [options]\n\ndomains:\n" + domains


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)

    if not argv:
        print(_usage(), file=sys.stderr)
        return 2
    if argv[0] in ("-h", "--help"):
        print(_usage())
        return 0

    domain = argv[0]
    if domain not in _DOMAINS:
        print(f"error: unknown domain {domain!r}\n\n{_usage()}", file=sys.stderr)
        return 2

    module = importlib.import_module(_DOMAINS[domain])
    return module.main(argv[1:])


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
