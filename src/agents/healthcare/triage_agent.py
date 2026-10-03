"""Agent điều phối tiếp nhận và phân luồng bệnh nhân (Triage & Dispatch Agent).

Trách nhiệm:
- Hướng dẫn điều dưỡng và tiếp tân phân luồng vào đúng cửa tiếp nhận.
- Kiểm tra các tiêu chuẩn ưu tiên (Cửa 2 Tầng 1 Nhà E dành cho người già > 75t, trẻ em < 2t, phụ nữ có thai).
- Hướng dẫn thủ tục BHYT điện tử (VNeID/VssID/CCCD gắn chip) theo quy định Bệnh viện E.
"""

from __future__ import annotations

from dataclasses import dataclass

from src.domain.healthcare.hospital_service import hospital_service
from src.domain.healthcare.models import TriageLevel


@dataclass(frozen=True)
class TriageAgentResponse:
    content: str
    target_counter: str
    target_department: str
    suggested_actions: tuple[str, ...] = ()
    triage_level: TriageLevel = TriageLevel.ROUTINE
    medical_disclaimer: str = "Lưu ý điều dưỡng: Mọi trường hợp nghi ngờ khẩn cấp hoặc sinh hiệu không ổn định phải chuyển ngay sang Cấp cứu Nhà C."


class TriageDispatchAgent:
    """Agent phân luồng tiếp nhận dành cho Điều dưỡng và Tiếp tân."""

    def __init__(self) -> None:
        self.name = "Triage & Dispatch Agent (Bệnh viện E)"

    def handle(self, message: str, *, is_priority_patient: bool = False) -> TriageAgentResponse:
        dept = hospital_service.find_department_by_symptom(message)
        dept_name = dept.name if dept else "Khoa Khám bệnh"

        if is_priority_patient:
            counter = "CỬA SỐ 2 - TẦNG 1 NHÀ E (Cửa tiếp nhận ưu tiên: Người cao tuổi > 75t, Trẻ < 2t, Phụ nữ mang thai, Người khuyết tật)"
        elif "chuyển tuyến" in message.lower() or "giấy chuyển" in message.lower():
            counter = "CỬA SỐ 3 - TẦNG 1 NHÀ E (Tiếp nhận người bệnh có giấy chuyển viện / chuyển tuyến)"
        else:
            counter = "CỬA SỐ 3, 4, 5, 6 - TẦNG 1 NHÀ E (Tiếp nhận đăng ký khám BHYT mới)"

        text = (
            f"🏥 **HƯỚNG DẪN PHÂN LUỒNG TIẾP NHẬN BỆNH NHÂN TẠI BỆNH VIỆN E:**\n\n"
            f"- **Phân loại chuyên khoa khuyến nghị:** **{dept_name}** ({dept.location if dept else 'Nhà E'})\n"
            f"- **Vị trí quầy tiếp nhận:** **{counter}**\n\n"
            f"📋 **Quy trình hành chính tại bàn điều dưỡng:**\n"
            f"1. Lấy số thứ tự tại Cây phát số tự động tại sảnh Tầng 1 Nhà E.\n"
            f"2. Tiếp nhận CCCD gắn chip hoặc thẻ BHYT trên ứng dụng VNeID / VssID.\n"
            f"3. Đo mạch, nhiệt độ, huyết áp (sinh hiệu ban đầu).\n"
            f"4. In Phiếu hướng dẫn khám chuyên khoa và chỉ dẫn người bệnh di chuyển đến phòng khám."
        )

        return TriageAgentResponse(
            content=text,
            target_counter=counter,
            target_department=dept_name,
            suggested_actions=("In phiếu số thứ tự", "Đo huyết áp & sinh hiệu", "Chuyển tiếp vào phòng khám"),
        )


triage_agent = TriageDispatchAgent()
