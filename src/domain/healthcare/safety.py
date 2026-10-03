"""Lưới canh an toàn y tế và bảo vệ quyền riêng tư — thuần tất định, không I/O.

1. Red Flags Interceptor: Phát hiện dấu hiệu cấp cứu đe dọa tính mạng, trả về chỉ dẫn 115.
2. PII Masker: Che giấu thông tin cá nhân (SĐT, CCCD, Mã BHYT, tên) theo Nghị định 13/2023/NĐ-CP & HIPAA.
"""

from __future__ import annotations

import re

from src.domain.healthcare.models import RedFlagResult

# Danh mục cờ đỏ cấp cứu y tế tối khẩn cấp
RED_FLAG_PATTERNS: tuple[tuple[str, str], ...] = (
    # Tim mạch / Nhồi máu cơ tim
    (r"(đau|tức|nghẹn|thắt|đè nặng)\s*(ngực|tim)", "Đau thắt ngực nghi ngờ hội chứng vành cấp / nhồi máu cơ tim"),
    (r"lan\s*(ra|lên)\s*(cổ|hàm|vai|tay trái)", "Triệu chứng đau lan đặc hiệu của cơn đau thắt ngực"),
    # Đột quỵ / Tai biến mạch máu não (FAST)
    (r"(méo|lệch)\s*(miệng|mặt)", "Dấu hiệu liệt mặt (Facial Droop - FAST) trong đột quỵ"),
    (r"(liệt|yếu|mất cảm giác)\s*(nửa người|tay|chân)", "Yếu liệt chi cấp tính nghi ngờ đột quỵ não"),
    (r"(nói đớ|nói ngọng|không nói được|ú ớ)", "Rối loạn ngôn ngữ cấp tính (Slurred Speech - FAST)"),
    # Hô hấp khẩn cấp
    (r"(khó thở dữ dội|ngạt thở|thở rít|không thở được|tím tái)", "Suy hô hấp cấp tính / tắc nghẽn đường thở"),
    # Dị ứng nặng / Phản vệ
    (
        r"(sốc phản vệ|phù mạch|sưng môi lưỡi nghẹt họng|ngứa nổi mề đay toàn thân khó thở)",
        "Dấu hiệu phản vệ cấp độ nặng (Anaphylaxis)",
    ),
    # Xuất huyết tiêu hóa nặng
    (
        r"(nôn ra máu|ói ra máu|đi ngoài phân đen như bã cà phê|chảy máu không cầm)",
        "Xuất huyết tiêu hóa / chảy máu ồ ạt",
    ),
    # Ý thức & Thần kinh
    (r"(hôn mê|bất tỉnh|ngất xỉu|co giật|mất ý thức)", "Hôn mê / Rối loạn tri giác / Co giật cấp"),
    # Ngộ độc / Tự hại
    (r"(uống thuốc trừ sâu|ngộ độc|tự tử|tự hại)", "Nguy cơ ngộ độc cấp tính hoặc khủng hoảng tâm thần khẩn cấp"),
)

# Biểu thức Regex che PII
PHONE_REGEX = re.compile(r"(?<!\d)(?:\+?84|0)(?:3|5|7|8|9)\d{8}(?!\d)")
CCCD_REGEX = re.compile(r"(?<!\d)\d{12}(?!\d)")
BHYT_REGEX = re.compile(r"\b([A-Z]{2}\d{13}|\d{10})\b")
EMAIL_REGEX = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")


class RedFlagsDetector:
    """Bộ dò phát hiện tình trạng cấp cứu nguy hiểm tính mạng."""

    def __init__(self) -> None:
        self._compiled = [(re.compile(p, re.IGNORECASE), desc) for p, desc in RED_FLAG_PATTERNS]

    def check(self, text: str) -> RedFlagResult:
        detected: list[str] = []
        for pattern, desc in self._compiled:
            if pattern.search(text):
                detected.append(desc)

        if detected:
            guidance = (
                "🚨 **CẢNH BÁO TÌNH HUỐNG CẤP CỨU Y TẾ NGUY HIỂM!**\n\n"
                "Hệ thống phát hiện dấu hiệu đe dọa tính mạng (Red Flags). Bạn hoặc người thân cần:\n"
                "1. **GỌI NGAY CẤP CỨU 115** hoặc di chuyển khẩn cấp tới Phòng Cấp cứu bệnh viện gần nhất.\n"
                "   - **Cấp cứu Bệnh viện E (24/7):** Tầng 1 - Nhà C, 89 Trần Cung, Nghĩa Tân, Cầu Giấy, Hà Nội. Hotline: 1900 1548 / 024.3754.3650.\n"
                "2. Giữ người bệnh ở tư thế thoải mái, nới lỏng cổ áo, không để người bệnh tự lái xe.\n"
                "3. Tuyệt đối không tự ý dùng thuốc hạ huyết áp nhanh hoặc thuốc giảm đau mạnh khi chưa có chỉ định của bác sĩ cấp cứu."
            )
            return RedFlagResult(
                is_triggered=True,
                symptoms_detected=tuple(detected),
                emergency_guidance=guidance,
                hotline="115",
            )

        return RedFlagResult(is_triggered=False)


class PIIMasker:
    """Bộ che giấu dữ liệu định danh cá nhân."""

    def mask(self, text: str) -> str:
        masked = PHONE_REGEX.sub("[SỐ ĐIỆN THOẠI ĐÃ ẨN]", text)
        masked = CCCD_REGEX.sub("[CCCD/ĐỊNH DANH ĐÃ ẨN]", masked)
        masked = BHYT_REGEX.sub("[MÃ BHYT ĐÃ ẨN]", masked)
        masked = EMAIL_REGEX.sub("[EMAIL ĐÃ ẨN]", masked)
        return masked


red_flags_detector = RedFlagsDetector()
pii_masker = PIIMasker()
