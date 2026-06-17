"""proof-surface — the shared accountability/provenance contract family.

Single source of truth for the proof-surface packet, the work-record receipt
(the structural inverse of an authorization-suppression prefire), the
authorization receipt (the inward complement: a real, explicit, least-privilege,
expiring, revocable grant from a human principal to an agent), and a
consumer-side validator that mirrors EMET's witness-receipt shape. Stdlib-only.
"""

from ._validate import Issue
from .authorization_receipt import (
    AUTHORIZATION_VERSION,
    RECEIPT_KIND,
    check_action,
    validate_authorization_receipt,
    validate_authorization_receipt_file,
)
from .packet import (
    PACKET_VERSION,
    validate_packet,
    validate_packet_file,
)
from .witness_receipt import (
    WITNESS_VERDICTS,
    validate_witness_receipt,
    validate_witness_receipt_file,
)
from .work_record import (
    WORK_RECORD_VERSION,
    validate_work_record,
    validate_work_record_file,
)

__all__ = [
    "Issue",
    "AUTHORIZATION_VERSION",
    "RECEIPT_KIND",
    "check_action",
    "validate_authorization_receipt",
    "validate_authorization_receipt_file",
    "PACKET_VERSION",
    "validate_packet",
    "validate_packet_file",
    "WITNESS_VERDICTS",
    "validate_witness_receipt",
    "validate_witness_receipt_file",
    "WORK_RECORD_VERSION",
    "validate_work_record",
    "validate_work_record_file",
]
__version__ = "0.1.0"
