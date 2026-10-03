"""Endpoint nghiệp vụ lâm sàng dành cho Bác sĩ."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from src.agents.healthcare.doctor_agent import doctor_agent

router = APIRouter(prefix="/api/v1/doctor", tags=["Lâm sàng Bác sĩ"])


class SOAPGenerateRequest(BaseModel):
    patient_id: str = Field(..., description="Mã bệnh nhân hoặc mã hồ sơ")
    patient_name: str = Field(..., description="Họ và tên bệnh nhân")
    history_text: str = Field(..., min_length=5, description="Lời khai bệnh nhân / bệnh sử tóm tắt")
    doctor_id: str = Field(default="DOC-E01", description="Mã bác sĩ khám")
    doctor_name: str = Field(default="Bác sĩ lâm sàng Bệnh viện E", description="Tên bác sĩ")


class SOAPSubjectiveDTO(BaseModel):
    chief_complaint: str
    history_of_present_illness: str
    past_medical_history: list[str] = Field(default_factory=list)


class SOAPObjectiveDTO(BaseModel):
    vital_signs: dict[str, Any] = Field(default_factory=dict)
    physical_exam: str
    lab_results: list[str] = Field(default_factory=list)


class SOAPAssessmentDTO(BaseModel):
    primary_diagnosis: str
    icd10_code: str | None = None
    differential_diagnoses: list[str] = Field(default_factory=list)
    clinical_reasoning: str


class SOAPPlanDTO(BaseModel):
    diagnostic_tests: list[str] = Field(default_factory=list)
    prescriptions: list[str] = Field(default_factory=list)
    patient_education: str
    follow_up: str


class SOAPNoteResponse(BaseModel):
    content: str
    patient_id: str
    patient_name: str
    doctor_id: str
    subjective: SOAPSubjectiveDTO
    objective: SOAPObjectiveDTO
    assessment: SOAPAssessmentDTO
    plan: SOAPPlanDTO
    suggested_actions: list[str] = Field(default_factory=list)
    medical_disclaimer: str


class DrugInteractionRequest(BaseModel):
    drugs: list[str] = Field(..., min_length=2, description="Danh sách tối thiểu 2 tên thuốc/hoạt chất cần kiểm tra")


class DrugInteractionItemDTO(BaseModel):
    drug_pair: list[str]
    severity: str
    mechanism: str
    clinical_consequence: str
    recommendation: str


class DrugInteractionResponse(BaseModel):
    content: str
    has_contraindication: bool
    summary: str
    interactions: list[DrugInteractionItemDTO]
    suggested_actions: list[str] = Field(default_factory=list)
    medical_disclaimer: str


@router.post("/soap-note", response_model=SOAPNoteResponse)
def generate_soap_note(payload: SOAPGenerateRequest) -> SOAPNoteResponse:
    """Tự động sinh cấu trúc bệnh án SOAP Note và khuyến nghị cận lâm sàng theo phác đồ."""
    res = doctor_agent.handle_soap_request(
        patient_id=payload.patient_id,
        patient_name=payload.patient_name,
        history_text=payload.history_text,
        doctor_id=payload.doctor_id,
        doctor_name=payload.doctor_name,
    )
    soap = res.soap_note
    assert soap is not None

    return SOAPNoteResponse(
        content=res.content,
        patient_id=soap.patient_id,
        patient_name=soap.patient_name,
        doctor_id=soap.doctor_id,
        subjective=SOAPSubjectiveDTO(
            chief_complaint=soap.subjective.chief_complaint,
            history_of_present_illness=soap.subjective.history_of_present_illness,
            past_medical_history=soap.subjective.past_medical_history,
        ),
        objective=SOAPObjectiveDTO(
            vital_signs=soap.objective.vital_signs,
            physical_exam=soap.objective.physical_exam,
            lab_results=soap.objective.lab_results,
        ),
        assessment=SOAPAssessmentDTO(
            primary_diagnosis=soap.assessment.primary_diagnosis,
            icd10_code=soap.assessment.icd10_code,
            differential_diagnoses=soap.assessment.differential_diagnoses,
            clinical_reasoning=soap.assessment.clinical_reasoning,
        ),
        plan=SOAPPlanDTO(
            diagnostic_tests=soap.plan.diagnostic_tests,
            prescriptions=soap.plan.prescriptions,
            patient_education=soap.plan.patient_education,
            follow_up=soap.plan.follow_up,
        ),
        suggested_actions=list(res.suggested_actions),
        medical_disclaimer=res.medical_disclaimer,
    )


@router.post("/drug-interactions", response_model=DrugInteractionResponse)
def check_drug_interactions(payload: DrugInteractionRequest) -> DrugInteractionResponse:
    """Rà soát tương tác thuốc nguy cơ cao theo Dược thư Quốc gia Việt Nam."""
    res = doctor_agent.handle_drug_check(tuple(payload.drugs))
    check = res.drug_check
    assert check is not None

    return DrugInteractionResponse(
        content=res.content,
        has_contraindication=check.has_contraindication,
        summary=check.summary,
        interactions=[
            DrugInteractionItemDTO(
                drug_pair=list(item.drug_pair),
                severity=item.severity,
                mechanism=item.mechanism,
                clinical_consequence=item.clinical_consequence,
                recommendation=item.recommendation,
            )
            for item in check.interactions
        ],
        suggested_actions=list(res.suggested_actions),
        medical_disclaimer=res.medical_disclaimer,
    )
