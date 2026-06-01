"""Finding — the typed result the Reasoning layer emits (Q8).

The judgment about a concrete case lives here. The Decision Engine reads these
flags; it never interprets prose. A general rule lookup yields not_applicable /
unknown, never non_compliant.
"""

from enum import StrEnum

from pydantic import BaseModel


class ComplianceStatus(StrEnum):
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    NOT_APPLICABLE = "not_applicable"
    UNKNOWN = "unknown"


class Risk(BaseModel):
    description: str
    severity: str


class Opportunity(BaseModel):
    description: str


class Finding(BaseModel):
    compliance_status: ComplianceStatus = ComplianceStatus.NOT_APPLICABLE
    risks: list[Risk] = []
    opportunities: list[Opportunity] = []
