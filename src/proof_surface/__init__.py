"""proof-surface — the shared accountability/provenance contract family.

Single source of truth for the proof-surface packet, the work-record receipt
(the structural inverse of an authorization-suppression prefire), and a
consumer-side validator that mirrors EMET's witness-receipt shape. Stdlib-only.
"""

from ._validate import Issue
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
