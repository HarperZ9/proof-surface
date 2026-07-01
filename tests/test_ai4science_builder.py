"""AI4Science claim-to-experiment wedge: no unmeasured / unreproduced discovery.

Harvest of dogfood pass 0104 (AI4ScienceClaimToExperimentReceipt/v1, an
implemented artifact). A scientific claim bound to a protocol, measurement,
reproduction status, and reviewer objections. Honesty gates: reject an unmeasured
discovery claim; require independent reproduction for a REPRODUCED rung; an open
reviewer objection blocks peer-reviewed promotion. Negative results stay valid.
"""

from __future__ import annotations

from proof_surface.ai4science import (
    build_ai4science_packet,
    validate_ai4science_packet,
)

_HEX = "a" * 64


def _packet(
    *,
    measured=True,
    reproduction="INDEPENDENTLY_REPRODUCED",
    objections=None,
    negative_result=False,
):
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
            "measured": measured,
            "measurement_ref": "meas:1" if measured else None,
            "value": 0.4 if measured else None,
            "unit": "uM" if measured else None,
        },
        reproduction={"status": reproduction},
        reviewer_objections=objections or [],
        negative_result=negative_result,
        claim="binding measured and reproduced",
        scope="one assay",
        packet_id="a4s-1",
    )


def test_measured_and_reproduced_reaches_reproduced_and_matches():
    packet = _packet()
    assert validate_ai4science_packet(packet) == []
    assert packet["promotion"] == "REPRODUCED"
    assert packet["verdicts"]["overall"] == "MATCH"


def test_unmeasured_claim_never_reaches_measured():
    packet = _packet(measured=False, reproduction="NOT_RUN")
    assert packet["promotion"] in {"HYPOTHESIS", "SOURCE_LEAD"}
    assert validate_ai4science_packet(packet) == []


def test_forged_measured_without_measurement_is_rejected():
    packet = _packet(measured=False, reproduction="NOT_RUN")
    packet["measurement"]["measured"] = False
    packet["promotion"] = "MEASURED"
    assert any("promotion" in i.path for i in validate_ai4science_packet(packet))


def test_forged_reproduced_without_independent_reproduction_is_rejected():
    packet = _packet(reproduction="SINGLE_RUN")
    packet["promotion"] = "REPRODUCED"
    assert any("promotion" in i.path for i in validate_ai4science_packet(packet))


def test_open_reviewer_objection_blocks_peer_reviewed():
    packet = _packet(objections=[{"objection": "controls missing", "status": "open"}])
    packet["promotion"] = "PEER_REVIEWED"
    assert any("promotion" in i.path for i in validate_ai4science_packet(packet))


def test_negative_result_is_valid_and_drifts():
    packet = _packet(negative_result=True, reproduction="FAILED_REPRODUCTION")
    assert validate_ai4science_packet(packet) == []
    assert packet["verdicts"]["overall"] == "DRIFT"


def test_unknown_reproduction_status_is_rejected():
    packet = _packet()
    packet["reproduction"]["status"] = "maybe"
    assert any("reproduction" in i.path for i in validate_ai4science_packet(packet))
