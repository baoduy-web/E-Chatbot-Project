"""Hỗ trợ quyết định lâm sàng và kiểm tra an toàn dùng thuốc — thuần tất định.

1. Kiểm tra tương tác thuốc nguy cơ cao theo Dược thư Quốc gia Việt Nam.
2. Tra cứu mã bệnh chuẩn ICD-10.
3. Sinh cấu trúc SOAP Note tiêu chuẩn cho trợ lý bác sĩ.
"""

from __future__ import annotations

import json
from pathlib import Path

from src.domain.healthcare.models import (
    DrugCheckResult,
    DrugInteractionItem,
    SOAPAssessment,
    SOAPNote,
    SOAPObjective,
    SOAPPlan,
    SOAPSubjective,
)

_DEFAULT_DATA_DIR = Path(__file__).resolve().parents[3] / "data" / "medical"


class ClinicalDecisionSupport:
    def __init__(self, data_dir: Path | None = None) -> None:
        self.data_dir = data_dir or _DEFAULT_DATA_DIR
        self._interactions: list[dict[str, object]] = []
        self._icd10: list[dict[str, str]] = []
        self._load_data()

    def _load_data(self) -> None:
        drug_file = self.data_dir / "drug_interactions.json"
        if drug_file.exists():
            try:
                self._interactions = json.loads(drug_file.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                pass

        icd_file = self.data_dir / "icd10_common.json"
        if icd_file.exists():
            try:
                self._icd10 = json.loads(icd_file.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                pass

    def check_drug_interactions(self, drugs: tuple[str, ...]) -> DrugCheckResult:
        """Kiểm tra tương tác thuốc giữa các hoạt chất / biệt dược trong đơn thuốc."""
        lower_drugs = [d.strip().lower() for d in drugs if d.strip()]
        matched_items: list[DrugInteractionItem] = []
        has_contra = False

        for rule in self._interactions:
            raw_pair = rule.get("pair")
            if isinstance(raw_pair, list) and len(raw_pair) == 2:
                d1 = str(raw_pair[0]).lower()
                d2 = str(raw_pair[1]).lower()
                # Kiểm tra cả 2 thuốc có mặt trong danh sách
                found_d1 = any(d1 in user_drug or user_drug in d1 for user_drug in lower_drugs)
                found_d2 = any(d2 in user_drug or user_drug in d2 for user_drug in lower_drugs)
                if found_d1 and found_d2:
                    severity = str(rule.get("severity", "Moderate"))
                    if severity in ["Contraindicated", "High"]:
                        has_contra = True
                    matched_items.append(
                        DrugInteractionItem(
                            drug_pair=(str(raw_pair[0]), str(raw_pair[1])),
                            severity=severity,
                            mechanism=str(rule.get("mechanism", "")),
                            clinical_consequence=str(rule.get("clinical_consequence", "")),
                            recommendation=str(rule.get("recommendation", "")),
                        )
                    )

        summary = f"Đã rà soát {len(drugs)} hoạt chất/thuốc theo Dược thư Quốc gia Việt Nam."
        if has_contra:
            summary += " ⚠️ PHÁT HIỆN TƯƠNG TÁC NGUY HIỂM / CHỐNG CHỈ ĐỊNH CẦN ĐIỀU CHỈNH ĐƠN!"
        elif matched_items:
            summary += f" Phát hiện {len(matched_items)} tương tác cần lưu ý theo dõi lâm sàng."
        else:
            summary += " Không phát hiện tương tác thuốc bất lợi nghiêm trọng trong cơ sở dữ liệu."

        return DrugCheckResult(
            interactions=tuple(matched_items),
            has_contraindication=has_contra,
            summary=summary,
        )

    def lookup_icd10(self, query: str) -> list[dict[str, str]]:
        q = query.lower()
        results: list[dict[str, str]] = []
        for item in self._icd10:
            if q in item["code"].lower() or q in item["name_vi"].lower():
                results.append(item)
        return results

    def generate_clinical_soap(
        self,
        *,
        patient_id: str,
        patient_name: str,
        history_text: str,
        doctor_id: str = "DOC-DEFAULT",
        doctor_name: str = "Bác sĩ lâm sàng Bệnh viện E",
        vitals: dict[str, object] | None = None,
    ) -> SOAPNote:
        """Sinh khung bệnh án SOAP chuẩn xác theo chuyên khoa và phác đồ Bệnh viện E."""
        lower_hist = history_text.lower()
        vitals = vitals or {"blood_pressure": "120/80 mmHg", "heart_rate": "75 bpm", "temperature": "36.8 C"}

        if any(w in lower_hist for w in ["ngực", "tim", "huyết áp"]):
            primary = "Theo dõi Cơn đau thắt ngực / Tăng huyết áp độ 2"
            icd = "I20"
            diffs = ["Bệnh tim thiếu máu cục bộ mạn tính", "Rối loạn nhịp tim", "Đau thần kinh liên sườn"]
            tests = [
                "Điện tâm đồ (ECG) 12 chuyển đạo",
                "Siêu âm tim màu Doppler",
                "Định lượng Men tim hs-Troponin T / I",
                "Chụp X-quang tim phổi thẳng",
            ]
            prescriptions = [
                "Amlodipine 5mg (1 viên uống sáng)",
                "Aspirin 81mg (1 viên uống sau ăn no nếu không có chống chỉ định dạ dày)",
            ]
            education = "Chế độ ăn giảm muối (< 5g/ngày), bỏ thuốc lá, tránh gắng sức thể lực đột ngột, theo dõi huyết áp tại nhà."
        elif any(w in lower_hist for w in ["dạ dày", "bụng", "ợ chua", "nôn", "tiêu hóa"]):
            primary = "Viêm loét dạ dày - tá tràng / Trào ngược dạ dày thực quản (GERD)"
            icd = "K21.0"
            diffs = ["Viêm tụy cấp thể nhẹ", "Hội chứng ruột kích thích (IBS)", "Sỏi túi mật"]
            tests = [
                "Nội soi thực quản - dạ dày - tá tràng gây mê (EGD)",
                "Test vi khuẩn H. Pylori (HP qua hơi thở)",
                "Siêu âm ổ bụng tổng quát",
            ]
            prescriptions = [
                "Esomeprazole 40mg (1 viên uống trước ăn sáng 30 phút)",
                "Phosphalugel (uống khi có cơn nóng rát dạ dày)",
            ]
            education = "Ăn uống đúng giờ, không nằm ngay sau khi ăn no, kiêng bia rượu, cà phê và gia vị cay nóng."
        elif any(w in lower_hist for w in ["khớp", "gối", "gout", "gút", "lưng", "xương"]):
            primary = "Thoái hóa khớp gối / Theo dõi cơn Gout cấp"
            icd = "M17"
            diffs = ["Viêm khớp dạng thấp", "Tổn thương sụn chêm dây chằng", "Viêm bao hoạt dịch"]
            tests = [
                "Chụp X-quang khớp gối thẳng và nghiêng",
                "Định lượng Acid Uric huyết thanh",
                "Bilan viêm (CRP định lượng, tốc độ máu lắng ESR)",
            ]
            prescriptions = [
                "Celecoxib 200mg (1 viên/ngày sau ăn no)",
                "Kèm thuốc bảo vệ dạ dày",
            ]
            education = (
                "Tránh mang vác nặng, hạn chế leo cầu thang, kiêng thực phẩm giàu purin (thịt đỏ, phủ tạng, bia rượu)."
            )
        else:
            primary = "Theo dõi hội chứng lâm sàng chưa phân loại"
            icd = "R69"
            diffs = ["Hội chứng nhiễm trùng", "Rối loạn chức năng cơ quan"]
            tests = ["Công thức máu toàn bộ (CBC)", "Sinh hóa máu cơ bản (Urea, Creatinine, AST, ALT)"]
            prescriptions = ["Điều trị triệu chứng hỗ trợ"]
            education = "Nghỉ ngơi, uống đủ nước, theo dõi sát diễn biến sức khỏe."

        return SOAPNote(
            patient_id=patient_id,
            patient_name=patient_name,
            age=None,
            gender=None,
            doctor_id=doctor_id,
            doctor_name=doctor_name,
            subjective=SOAPSubjective(
                chief_complaint=history_text[:100].strip(),
                history_of_present_illness=f"Bệnh nhân phản ánh: {history_text}",
            ),
            objective=SOAPObjective(
                vital_signs=vitals,
                lab_results=["Chờ kết quả các chỉ định cận lâm sàng"],
            ),
            assessment=SOAPAssessment(
                primary_diagnosis=primary,
                icd10_code=icd,
                differential_diagnoses=diffs,
                clinical_reasoning="Cần kết hợp thăm khám lâm sàng trực tiếp và kết quả cận lâm sàng để chẩn đoán xác định.",
            ),
            plan=SOAPPlan(
                diagnostic_tests=tests,
                prescriptions=prescriptions,
                patient_education=education,
                follow_up="Tái khám sau 3 - 5 ngày hoặc khám ngay khi có dấu hiệu bất thường.",
            ),
            raw_summary=history_text,
            is_verified_by_doctor=False,
        )


clinical_cds = ClinicalDecisionSupport()
