"""Bộ điều phối trung tâm (Master Orchestrator / Supervisor Agent).

Quy trình xử lý 3 bước bất biến:
1. Red Flags Interceptor: Phát hiện nguy cơ đe dọa tính mạng -> ngắt luồng lập tức và phát cảnh báo 115.
2. PII Masking: Che giấu thông tin cá nhân (SĐT, CCCD, BHYT) theo HIPAA & Nghị định 13/2023/NĐ-CP.
3. Role-Based Routing: Định tuyến ngữ cảnh tới Agent chuyên trách (Bệnh nhân, Bác sĩ, Điều dưỡng).
"""

from __future__ import annotations

from dataclasses import dataclass

from src.agents.healthcare.doctor_agent import doctor_agent
from src.agents.healthcare.patient_agent import patient_agent
from src.agents.healthcare.triage_agent import triage_agent
from src.domain.healthcare.models import (
    RedFlagResult,
    TriageLevel,
    UserRole,
)
from src.domain.healthcare.safety import pii_masker, red_flags_detector
from src.llm.retriever import SearchCitation


@dataclass(frozen=True)
class OrchestratorResponse:
    session_id: str
    response: str
    agent_name: str
    triage_level: TriageLevel
    red_flag: RedFlagResult
    citations: tuple[SearchCitation, ...] = ()
    suggested_specialty: str | None = None
    suggested_actions: tuple[str, ...] = ()
    medical_disclaimer: str = ""


class MasterOrchestrator:
    """Supervisor Agent trung tâm điều phối toàn bộ hệ thống."""

    def __init__(self) -> None:
        self.patient_agent = patient_agent
        self.doctor_agent = doctor_agent
        self.triage_agent = triage_agent

    def process_message(
        self,
        *,
        session_id: str,
        message: str,
        role: UserRole = UserRole.PATIENT,
        user_name: str = "Người dùng",
    ) -> OrchestratorResponse:
        # BƯỚC 1: RED FLAGS CHECK (Phát hiện tình huống cấp cứu nguy hiểm tính mạng)
        red_flag_alert = red_flags_detector.check(message)
        if red_flag_alert.is_triggered:
            symptoms_str = "\n".join(f"- {s}" for s in red_flag_alert.symptoms_detected)
            content = (
                f"{red_flag_alert.emergency_guidance}\n\n"
                f"**Các dấu hiệu báo động phát hiện được:**\n"
                f"{symptoms_str}\n\n"
                f"📞 **ĐƯỜNG DÂY NÓNG CẤP CỨU: 115** | Bệnh viện E: **1900 1548 / 024.3754.3650**"
            )
            return OrchestratorResponse(
                session_id=session_id,
                response=content,
                agent_name="Emergency Safety Interceptor (115)",
                triage_level=TriageLevel.EMERGENCY,
                red_flag=red_flag_alert,
                suggested_actions=("Gọi Cấp cứu 115 ngay", "Xem địa chỉ Cấp cứu Nhà C Bệnh viện E"),
                medical_disclaimer="CẢNH BÁO TỐI KHẨN CẤP: Dấu hiệu đe dọa tính mạng, cần được xử trí y tế ngay lập tức.",
            )

        # BƯỚC 2: PII MASKING (Che giấu dữ liệu định danh)
        masked_message = pii_masker.mask(message)

        # BƯỚC 3: SUPERVISOR ROUTING DỰA TRÊN ROLE & NGỮ CẢNH
        if role == UserRole.DOCTOR:
            # Nếu bác sĩ kiểm tra thuốc
            if "thuốc" in masked_message.lower() and ("," in masked_message or "và" in masked_message):
                # Tách thuốc sơ bộ
                raw_drugs = [d.strip() for d in masked_message.replace("thuốc", "").split(",") if d.strip()]
                res_doc = self.doctor_agent.handle_drug_check(tuple(raw_drugs))
            else:
                res_doc = self.doctor_agent.handle_soap_request(
                    patient_id="PT-AUTO",
                    patient_name=user_name,
                    history_text=masked_message,
                )

            return OrchestratorResponse(
                session_id=session_id,
                response=res_doc.content,
                agent_name=self.doctor_agent.name,
                triage_level=TriageLevel.ROUTINE,
                red_flag=red_flag_alert,
                suggested_actions=res_doc.suggested_actions,
                medical_disclaimer=res_doc.medical_disclaimer,
            )

        elif role in [UserRole.NURSE, UserRole.ADMIN]:
            res_triage = self.triage_agent.handle(masked_message)
            return OrchestratorResponse(
                session_id=session_id,
                response=res_triage.content,
                agent_name=self.triage_agent.name,
                triage_level=res_triage.triage_level,
                red_flag=red_flag_alert,
                suggested_specialty=res_triage.target_department,
                suggested_actions=res_triage.suggested_actions,
                medical_disclaimer=res_triage.medical_disclaimer,
            )

        else:
            # Mặc định là Người bệnh (Patient Navigator)
            res_patient = self.patient_agent.handle(masked_message, user_name=user_name)
            return OrchestratorResponse(
                session_id=session_id,
                response=res_patient.content,
                agent_name=self.patient_agent.name,
                triage_level=res_patient.triage_level,
                red_flag=red_flag_alert,
                citations=res_patient.citations,
                suggested_specialty=res_patient.suggested_specialty,
                suggested_actions=res_patient.suggested_actions,
                medical_disclaimer=res_patient.medical_disclaimer,
            )


master_orchestrator = MasterOrchestrator()
