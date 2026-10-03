"""Agent tư vấn và điều hướng người bệnh tại Bệnh viện E (Patient Navigator Agent).

Trách nhiệm:
- Lắng nghe triệu chứng, gợi ý chuyên khoa Bệnh viện E phù hợp.
- Hướng dẫn quy trình khám BHYT / Khám theo yêu cầu / Vị trí phòng khám (Nhà E, F, I, C).
- Bổ sung trích dẫn chứng cứ y tế (Grounded Citations) từ website benhviene.com.
- Đính kèm tuyên bố miễn trừ trách nhiệm y tế (Medical Disclaimer).
"""

from __future__ import annotations

from dataclasses import dataclass

from src.domain.healthcare.hospital_service import hospital_service
from src.domain.healthcare.models import TriageLevel
from src.llm.retriever import SearchCitation, knowledge_retriever


@dataclass(frozen=True)
class PatientAgentResponse:
    content: str
    suggested_specialty: str | None = None
    suggested_location: str | None = None
    citations: tuple[SearchCitation, ...] = ()
    suggested_actions: tuple[str, ...] = ()
    triage_level: TriageLevel = TriageLevel.ROUTINE
    medical_disclaimer: str = (
        "Lưu ý y tế: Thông tin từ Chatbot chỉ mang tính chất hướng dẫn và tham khảo quy trình. "
        "Người bệnh cần đến thăm khám trực tiếp với bác sĩ tại Bệnh viện E để được chẩn đoán và điều trị chính xác."
    )


class PatientNavigatorAgent:
    """Agent định hướng và chăm sóc bệnh nhân."""

    def __init__(self) -> None:
        self.name = "Patient Navigator Agent (Bệnh viện E)"

    def handle(self, message: str, user_name: str = "Người bệnh") -> PatientAgentResponse:
        # 1. Tìm chuyên khoa phù hợp theo triệu chứng
        dept = hospital_service.find_department_by_symptom(message)
        dept_name = dept.name if dept else "Khoa Khám bệnh (Nhà E)"
        location = dept.location if dept else "Tầng 1 - Nhà E"

        # 2. Truy xuất tài liệu dẫn chứng từ kho tri thức
        citations = knowledge_retriever.search(message, top_k=2)

        # 3. Lắp ráp nội dung trả lời
        parts = [
            f"Chào bạn {user_name},",
            "",
            f"Dựa trên nội dung bạn chia sẻ, hệ thống gợi ý bạn nên đăng ký khám tại: **{dept_name}**.",
            f"📍 **Địa điểm tiếp nhận:** {location}.",
            "",
            "📋 **Hướng dẫn khám bệnh tại Bệnh viện E (89 Trần Cung, Cầu Giấy, Hà Nội):**",
            "1. **Khám có thẻ BHYT:** Đến Cây phát số tự động lấy số -> Đăng ký tại Cửa 3, 4, 5, 6 Tầng 1 Nhà E (Người già > 75t, phụ nữ có thai ưu tiên tại Cửa 2).",
            "2. **Khám theo yêu cầu:** Đăng ký tại Cửa 10, 11 Nhà E hoặc Quầy F114 Tầng 1 Nhà F để được chọn khám chuyên gia/tiến sĩ.",
            "3. **Giấy tờ cần mang:** Thẻ BHYT (hoặc ứng dụng VNeID/VssID trên điện thoại) + Căn cước công dân gắn chip.",
        ]

        if dept and dept.description:
            parts.extend(["", f"ℹ️ *Thông tin chuyên khoa:* {dept.description}"])

        actions = (
            f"Xem quy trình khám tại {dept_name}",
            "Tra cứu bảng giá viện phí",
            "Hướng dẫn tích hợp BHYT trên VNeID",
        )

        return PatientAgentResponse(
            content="\n".join(parts),
            suggested_specialty=dept_name,
            suggested_location=location,
            citations=citations,
            suggested_actions=actions,
            triage_level=TriageLevel.ROUTINE,
        )


patient_agent = PatientNavigatorAgent()
