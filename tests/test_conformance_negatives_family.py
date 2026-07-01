"""Negative-fixture conformance gate for wedges 5-9: verification is not theater.

The research's own principle -- a verifier that cannot fail on a known-bad input
is not a verifier -- applied to our five newest verifiers. Same shape as
test_conformance_negatives.py: a valid packet per wedge plus a catalog of
mutations that MUST each be rejected; negative_pass_observed_count == 0.
"""

from __future__ import annotations

import copy

from proof_surface.ai4science import build_ai4science_packet, validate_ai4science_packet
from proof_surface.conservation import (
    build_conservation_packet,
    validate_conservation_packet,
)
from proof_surface.eval_attempt import (
    build_eval_attempt_packet,
    validate_eval_attempt_packet,
)
from proof_surface.optimization_workflow import (
    build_optimization_workflow_packet,
    validate_optimization_workflow_packet,
)
from proof_surface.rollout_receipt import (
    build_rollout_receipt_packet,
    validate_rollout_receipt_packet,
)

_HEX = "a" * 64


def _mut(fn):
    def wrapped(packet):
        clone = copy.deepcopy(packet)
        fn(clone)
        return clone

    return wrapped


# Mutations that must break any packet in the family.
_CROSS = {
    "drop-version": _mut(lambda p: p.pop("version", None)),
    "unknown-root-field": _mut(lambda p: p.update({"surprise": 1})),
    "forbidden-field": _mut(lambda p: p.update({"prefire": {}})),
    "authority-language": _mut(
        lambda p: p.update({"claim": "This result is CERTIFIED."})
    ),
    "drop-decision-summary": _mut(lambda p: p.pop("decision_summary", None)),
    "corrupt-decision-outcome": _mut(
        lambda p: p["decision_summary"].update({"decision": "yolo"})
    ),
}


def _optimization_valid():
    return build_optimization_workflow_packet(
        sources=[{"ref": "run:opt", "sha256": _HEX}],
        problem={"sense": "maximize", "objective": "v", "constraints": ["w <= 29"]},
        baseline={
            "method": "exact",
            "objective_value": 162,
            "feasible": True,
            "candidate_digest": _HEX,
        },
        candidate_space={
            "variables": 12,
            "evaluated": 4096,
            "feasible": 2000,
            "infeasible": 2096,
        },
        solver={
            "branch_id": "exact-0",
            "method": "exact",
            "status": "COMPLETED",
            "objective_value": 162,
            "constraint_status": "satisfied",
            "tolerance": 0.5,
        },
        claim="c",
        scope="s",
        packet_id="opt",
    )


_OPTIMIZATION_MUTATIONS = {
    "hardware-claim-without-hardware": _mut(
        lambda p: p["boundary"].update({"hardware_execution_claim": True})
    ),
    "candidate-count-mismatch": _mut(
        lambda p: p["candidate_space"].update({"feasible": 2001})
    ),
    "surrogate-self-certified": _mut(
        lambda p: p["solver"].update({"constraint_encoding": "equality_penalty"})
    ),
    "value-on-missing-dependency-branch": _mut(
        lambda p: p.update(
            {
                "solver_branches": [
                    {
                        "branch_id": "ortools",
                        "method": "ortools",
                        "status": "NOT_EXECUTED_DEPENDENCY_MISSING",
                        "objective_value": 162,
                    }
                ]
            }
        )
    ),
}


def _rollout_valid():
    return build_rollout_receipt_packet(
        sources=[{"ref": "run:r-42", "sha256": _HEX}],
        rollout={
            "rollout_id": "r-42",
            "policy_ref": "policy:v3",
            "checkpoint_ref": "ckpt:12000",
            "verifier_ref": "verifier:suite",
            "reward_digest": _HEX,
            "sandbox_receipt": "sandbox:9",
            "dataset_mutation_ref": "ds:77",
        },
        reward={"score": 0.87, "model_ref": "model:v3"},
        verifier={"verdict": "MATCH", "evidence": ["exit 0"]},
        admission={"decision": "allow", "reasons": []},
        claim="c",
        scope="s",
        packet_id="ro",
    )


_ROLLOUT_MUTATIONS = {
    "promote-on-drift-verifier": _mut(
        lambda p: p["verifier"].update({"verdict": "DRIFT"})
    ),
    "bad-admission-decision": _mut(
        lambda p: p["admission"].update({"decision": "vibe-check"})
    ),
    "bad-reward-digest": _mut(lambda p: p["rollout"].update({"reward_digest": "nope"})),
}


def _eval_attempt_valid():
    return build_eval_attempt_packet(
        sources=[{"ref": "run:att", "sha256": _HEX}],
        benchmark={
            "benchmark_ref": "arc-agi-2",
            "task_id": "t-7",
            "authority_receipt": "arcprize:v2",
        },
        attempt={
            "attempt_id": "att-1",
            "prompt_ref": "prompt:a",
            "model_ref": "model:m",
            "replay_ref": "replay:x",
        },
        result={"outcome": "correct", "score": 1.0},
        boundaries={
            "had_ground_truth": False,
            "had_internet": False,
            "had_tools": True,
        },
        claim="c",
        scope="s",
        packet_id="ea",
    )


_EVAL_ATTEMPT_MUTATIONS = {
    "contaminated-correct": _mut(
        lambda p: p["boundaries"].update({"had_ground_truth": True})
    ),
    "unknown-outcome": _mut(lambda p: p["result"].update({"outcome": "vibes"})),
    "missing-benchmark-authority": _mut(
        lambda p: p["benchmark"].pop("authority_receipt", None)
    ),
}


def _ai4science_valid():
    return build_ai4science_packet(
        sources=[{"ref": "arxiv:2408.06292", "sha256": _HEX}],
        domain="biology",
        scientific_claim="compound X binds target Y",
        agent_actions=[{"action": "design assay", "tool": "benchling"}],
        protocol={
            "protocol_ref": "proto:1",
            "workflow_runtime": "nextflow",
            "reproducible": True,
        },
        measurement={
            "measured": True,
            "measurement_ref": "meas:1",
            "value": 0.4,
            "unit": "uM",
        },
        reproduction={"status": "INDEPENDENTLY_REPRODUCED"},
        reviewer_objections=[],
        negative_result=False,
        claim="c",
        scope="s",
        packet_id="a4s",
    )


_AI4SCIENCE_MUTATIONS = {
    "unmeasured-promotion": _mut(
        lambda p: p["measurement"].update({"measured": False})
    ),
    "reproduced-without-reproduction": _mut(
        lambda p: p["reproduction"].update({"status": "SINGLE_RUN"})
    ),
    "open-objection-peer-reviewed": _mut(
        lambda p: (
            p.update({"promotion": "PEER_REVIEWED"}),
            p.update(
                {"reviewer_objections": [{"objection": "controls", "status": "open"}]}
            ),
        )
    ),
    "bad-reproduction-status": _mut(
        lambda p: p["reproduction"].update({"status": "maybe"})
    ),
}


def _conservation_valid():
    return build_conservation_packet(
        sources=[{"ref": "dogfood:pass-0106", "sha256": _HEX}],
        transformation={"description": "closed network", "domain": "chemistry"},
        invariant={"name": "total mass", "declared": "sum of species"},
        witnesses=[
            {
                "kind": "algebraic",
                "drift": 0.0,
                "tolerance": 1e-12,
                "method": "residual",
            },
        ],
        negative_fixture={
            "description": "leaky network",
            "drift": 0.456,
            "tolerance": 0.01,
            "breaks_invariant": True,
        },
        claim="c",
        scope="s",
        packet_id="cons",
    )


_CONSERVATION_MUTATIONS = {
    "non-breaking-negative-fixture": _mut(
        lambda p: p["negative_fixture"].update({"breaks_invariant": False})
    ),
    "break-within-tolerance": _mut(
        lambda p: p["negative_fixture"].update({"drift": 0.001})
    ),
    "no-witnesses": _mut(lambda p: p.update({"witnesses": []})),
    "invalid-boundary-fixture": _mut(
        lambda p: p.update(
            {
                "boundary_fixture": {
                    "description": "x",
                    "goal_holds": True,
                    "condition_holds": True,
                }
            }
        )
    ),
}


_DOMAINS = [
    (
        "optimization",
        validate_optimization_workflow_packet,
        _optimization_valid(),
        {**_CROSS, **_OPTIMIZATION_MUTATIONS},
    ),
    (
        "rollout",
        validate_rollout_receipt_packet,
        _rollout_valid(),
        {**_CROSS, **_ROLLOUT_MUTATIONS},
    ),
    (
        "eval-attempt",
        validate_eval_attempt_packet,
        _eval_attempt_valid(),
        {**_CROSS, **_EVAL_ATTEMPT_MUTATIONS},
    ),
    (
        "ai4science",
        validate_ai4science_packet,
        _ai4science_valid(),
        {**_CROSS, **_AI4SCIENCE_MUTATIONS},
    ),
    (
        "conservation",
        validate_conservation_packet,
        _conservation_valid(),
        {**_CROSS, **_CONSERVATION_MUTATIONS},
    ),
]


def test_every_valid_packet_validates_clean():
    for name, validate, valid, _muts in _DOMAINS:
        assert validate(valid) == [], name


def test_no_negative_fixture_validates_clean():
    negative_pass_observed: list[str] = []
    total = 0
    for name, validate, valid, muts in _DOMAINS:
        for mname, mutate in muts.items():
            total += 1
            if validate(mutate(valid)) == []:
                negative_pass_observed.append(f"{name}:{mname}")
    assert total >= 45  # the corpus is not empty
    assert negative_pass_observed == [], (
        f"negative_pass_observed_count={len(negative_pass_observed)}: "
        f"{negative_pass_observed}"
    )
