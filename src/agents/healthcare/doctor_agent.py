"""Trợ lý lâm sàng dành cho Bác sĩ (Doctor Clinical Copilot Agent).

Trách nhiệm:
- Sinh cấu trúc bệnh án SOAP Note (Subjective, Objective, Assessment, Plan).
- Rà soát tương tác thuốc nguy cơ cao theo Dược thư Quốc gia Việt Nam.
- Gợi ý chỉ định cận lâm sàng và phác đồ theo hướng dẫn của Bệnh viện E & Bộ Y tế.
- Tra cứu mã ICD-10.
"""

from __future__ import annotations

from dataclasses import dataclass

from src.domain.healthcare.clinical import clinical_cds
from src.domain.healthcare.models import (
    DrugCheckResult,
    SOAPNote,
)


@dataclass(frozen=True)
class DoctorAgentResponse:
    content: str
    soap_note: SOAPNote | None = None
    drug_check: DrugCheckResult | None = None
    suggested_actions: tuple[str, ...] = ()
    medical_disclaimer: str = (
        "Cảnh báo hỗ trợ lâm sàng (CDS): Bệnh án SOAP và khuyến nghị điều trị chỉ mang tính tham khảo. "
        "Bác sĩ điều trị chịu trách nhiệm toàn bộ đối với y lệnh và đơn thuốc ký duyệt."
    )


class DoctorCopilotAgent:
    """Agent hỗ trợ bác sĩ lâm sàng Bệnh viện E."""

    def __init__(self) -> None:
        self.name = "Doctor Clinical Copilot (Bệnh viện E)"

    def handle_soap_request(
        self,
        *,
        patient_id: str,
        patient_name: str,
        history_text: str,
        doctor_id: str = "DOC-E01",
        doctor_name: str = "Bác sĩ lâm sàng",
    ) -> DoctorAgentResponse:
        soap = clinical_cds.generate_clinical_soap(
            patient_id=patient_id,
            patient_name=patient_name,
            history_text=history_text,
            doctor_id=doctor_id,
            doctor_name=doctor_name,
        )

        tests_formatted = "\n".join(f"  - {t}" for t in soap.plan.diagnostic_tests)
        presc_formatted = "\n".join(f"  - {p}" for p in soap.plan.prescriptions)

        text = (
            f"📋 **BỆNH ÁN SOAP ĐƯỢC TỔNG HỢP CHO BỆNH NHÂN: {patient_name.upper()} (MÃ: {patient_id})**\n\n"
            f"**1. Subjective (Lời khai bệnh nhân):**\n"
            f"- Lý do vào viện: {soap.subjective.chief_complaint}\n"
            f"- Bệnh sử: {soap.subjective.history_of_present_illness}\n\n"
            f"**2. Objective (Thăm khám & Cận lâm sàng):**\n"
            f"- Huyết áp: {soap.objective.vital_signs.get('blood_pressure', '120/80 mmHg')}, "
            f"Mạch: {soap.objective.vital_signs.get('heart_rate', '75 bpm')}\n"
            f"- Khám: {soap.objective.physical_exam}\n\n"
            f"**3. Assessment (Chẩn đoán sơ bộ & ICD-10):**\n"
            f"- **Chẩn đoán chính:** **{soap.assessment.primary_diagnosis}** (Mã ICD-10: `{soap.assessment.icd10_code}`)\n"
            f"- Chẩn đoán phân biệt: {', '.join(soap.assessment.differential_diagnoses)}\n\n"
            f"**4. Plan (Kế hoạch điều trị & Chỉ định):**\n"
            f"*Chỉ định cận lâm sàng khuyến nghị:*\n{tests_formatted}\n"
            f"*Hướng phác đồ dùng thuốc:*\n{presc_formatted}\n"
            f"*Dặn dò bệnh nhân:* {soap.plan.patient_education}\n\n"
            f"⚠️ *Trạng thái:* Chờ Bác sĩ ({doctor_name}) kiểm tra, ký duyệt."
        )

        return DoctorAgentResponse(
            content=text,
            soap_note=soap,
            suggested_actions=("Ký duyệt SOAP Note", "Chỉnh sửa đơn thuốc", "Kiểm tra tương tác thuốc"),
        )

    def handle_drug_check(self, drugs: tuple[str, ...]) -> DoctorAgentResponse:
        result = clinical_cds.check_drug_interactions(drugs)
        lines = [
            f"💊 **KẾT QUẢ RÀ SOÁT TƯƠNG TÁC THUỐC ({len(drugs)} THUỐC ĐÃ KIỂM TRA):**",
            f"- Tình trạng: {result.summary}",
            "",
        ]

        for item in result.interactions:
            icon = "🚨" if item.severity in ["Contraindicated", "High"] else "⚠️"
            lines.extend(
                [
                    f"{icon} **Cặp thuốc: {item.drug_pair[0]} + {item.drug_pair[1]}** (Mức độ: **{item.severity}**)",
                    f"  - Cơ chế: {item.mechanism}",
                    f"  - Hậu quả lâm sàng: {item.clinical_consequence}",
                    f"  - Khuyến nghị: *{item.recommendation}*",
                    "",
                ]
            )

        return DoctorAgentResponse(
            content="\n".join(lines),
            drug_check=result,
            suggested_actions=("Đổi thuốc khác", "Theo dõi xét nghiệm đông máu/men gan", "In biên bản cảnh báo dược"),
        )


doctor_agent = DoctorCopilotAgent()
