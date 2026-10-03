"""Các cấu trúc dữ liệu y tế & Bệnh viện E — thuần dữ liệu, không I/O.

Tuân thủ bất biến kiến trúc INV-004:
Tầng domain không import LLM, ORM hay Web framework.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any


class UserRole(StrEnum):
    PATIENT = "patient"
    DOCTOR = "doctor"
    NURSE = "nurse"
    ADMIN = "admin"


class TriageLevel(StrEnum):
    EMERGENCY = "emergency"  # Cấp cứu tối khẩn cấp (ESI Level 1-2)
    URGENT = "urgent"  # Khẩn cấp / Cần khám trong 24h (ESI Level 3)
    ROUTINE = "routine"  # Khám thông thường / Tư vấn sức khỏe (ESI Level 4-5)


@dataclass(frozen=True)
class DepartmentInfo:
    id: str
    name: str
    category: str
    location: str
    lead: str | None = None
    hotline: str | None = None
    services: tuple[str, ...] = ()
    keywords: tuple[str, ...] = ()
    description: str = ""


@dataclass(frozen=True)
class WorkflowStep:
    step_number: int
    title: str
    detail: str
    location: str


@dataclass(frozen=True)
class WorkflowInfo:
    code: str
    name: str
    location: str
    steps: tuple[WorkflowStep, ...]


@dataclass(frozen=True)
class ServicePriceItem:
    service_id: str
    name: str
    price_bhyt: Decimal | None
    price_ondemand: Decimal
    unit: str = "lần"
    source: str = "Bệnh viện E - QĐ 4411/QĐ-BVE"


@dataclass(frozen=True)
class HospitalEstimate:
    examination_fee: Decimal
    services: tuple[tuple[str, Decimal], ...]
    total_estimated: Decimal
    note: str


@dataclass(frozen=True)
class RedFlagResult:
    is_triggered: bool
    symptoms_detected: tuple[str, ...] = ()
    emergency_guidance: str | None = None
    hotline: str = "115"
    nearest_emergency: str = "Khoa Cấp cứu 24/7 - Tầng 1 Nhà C, Bệnh viện E (89 Trần Cung, Cầu Giấy, Hà Nội)"


@dataclass(frozen=True)
class DrugInteractionItem:
    drug_pair: tuple[str, str]
    severity: str  # Contraindicated, High, Moderate
    mechanism: str
    clinical_consequence: str
    recommendation: str


@dataclass(frozen=True)
class DrugCheckResult:
    interactions: tuple[DrugInteractionItem, ...]
    has_contraindication: bool
    summary: str


@dataclass
class SOAPSubjective:
    chief_complaint: str
    history_of_present_illness: str
    past_medical_history: list[str] = field(default_factory=list)
    allergies: list[str] = field(default_factory=list)
    current_medications: list[str] = field(default_factory=list)


@dataclass
class SOAPObjective:
    vital_signs: dict[str, Any] = field(default_factory=dict)
    physical_exam: str = "Bệnh nhân tỉnh táo, tiếp xúc tốt, niêm mạc hồng, tim đều, phổi thông khí rõ."
    lab_results: list[str] = field(default_factory=list)


@dataclass
class SOAPAssessment:
    primary_diagnosis: str
    icd10_code: str | None = None
    differential_diagnoses: list[str] = field(default_factory=list)
    clinical_reasoning: str = ""


@dataclass
class SOAPPlan:
    diagnostic_tests: list[str] = field(default_factory=list)
    prescriptions: list[str] = field(default_factory=list)
    patient_education: str = ""
    follow_up: str = "Tái khám sau 3 - 5 ngày hoặc khám ngay khi có dấu hiệu bất thường."


@dataclass
class SOAPNote:
    patient_id: str
    patient_name: str
    age: int | None
    gender: str | None
    doctor_id: str
    doctor_name: str
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    subjective: SOAPSubjective = field(default_factory=lambda: SOAPSubjective("", ""))
    objective: SOAPObjective = field(default_factory=SOAPObjective)
    assessment: SOAPAssessment = field(default_factory=lambda: SOAPAssessment(""))
    plan: SOAPPlan = field(default_factory=SOAPPlan)
    raw_summary: str = ""
    is_verified_by_doctor: bool = False
