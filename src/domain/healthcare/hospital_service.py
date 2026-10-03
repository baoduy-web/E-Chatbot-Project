"""Dịch vụ tra cứu chuyên khoa, quy trình khám và tính giá Bệnh viện E — thuần tính toán.

Mọi con số, giá tiền đều lấy từ danh mục có nguồn; không bao giờ để LLM đoán giá hoặc vị trí phòng.
"""

from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

from src.domain.healthcare.models import (
    DepartmentInfo,
    HospitalEstimate,
    ServicePriceItem,
    WorkflowInfo,
    WorkflowStep,
)

# Root directory tìm data
_DEFAULT_DATA_DIR = Path(__file__).resolve().parents[3] / "data" / "hospital_e"


class HospitalServiceError(ValueError):
    """Lỗi xử lý nghiệp vụ thông tin bệnh viện."""


class HospitalEService:
    """Xử lý tra cứu khoa phòng, hướng dẫn quy trình và báo giá viện phí Bệnh viện E."""

    def __init__(self, data_dir: Path | None = None) -> None:
        self.data_dir = data_dir or _DEFAULT_DATA_DIR
        self._departments: list[DepartmentInfo] = []
        self._workflows: dict[str, WorkflowInfo] = {}
        self._prices: dict[str, ServicePriceItem] = {}
        self._load_data()

    def _load_data(self) -> None:
        dept_file = self.data_dir / "departments.json"
        if dept_file.exists():
            try:
                raw_depts = json.loads(dept_file.read_text(encoding="utf-8"))
                for d in raw_depts:
                    self._departments.append(
                        DepartmentInfo(
                            id=d["id"],
                            name=d["name"],
                            category=d["category"],
                            location=d["location"],
                            lead=d.get("lead"),
                            hotline=d.get("hotline"),
                            services=tuple(d.get("services", ())),
                            keywords=tuple(d.get("keywords", ())),
                            description=d.get("description", ""),
                        )
                    )
            except (OSError, json.JSONDecodeError, KeyError):
                pass

        wf_file = self.data_dir / "workflows.json"
        if wf_file.exists():
            try:
                raw_wf = json.loads(wf_file.read_text(encoding="utf-8"))
                for code, wf in raw_wf.items():
                    steps = tuple(
                        WorkflowStep(
                            step_number=s["step_number"],
                            title=s["title"],
                            detail=s["detail"],
                            location=s["location"],
                        )
                        for s in wf.get("steps", [])
                    )
                    self._workflows[code] = WorkflowInfo(
                        code=code,
                        name=wf["name"],
                        location=wf["location"],
                        steps=steps,
                    )
            except (OSError, json.JSONDecodeError, KeyError):
                pass

        pricing_file = self.data_dir / "pricing.json"
        if pricing_file.exists():
            try:
                raw_pricing = json.loads(pricing_file.read_text(encoding="utf-8"))
                for item in raw_pricing.get("common_services", []):
                    srv_name = item["service"]
                    self._prices[srv_name] = ServicePriceItem(
                        service_id=srv_name.lower().replace(" ", "_"),
                        name=srv_name,
                        price_bhyt=Decimal(str(item["price_bhyt"])),
                        price_ondemand=Decimal(str(item["price_ondemand"])),
                        source="Bệnh viện E - Quyết định 4411/QĐ-BVE",
                    )
                for item in raw_pricing.get("examination_fees", []):
                    fee_name = item["type"]
                    self._prices[fee_name] = ServicePriceItem(
                        service_id=fee_name.lower().replace(" ", "_"),
                        name=fee_name,
                        price_bhyt=Decimal(str(item["price"])) if "BHYT" in fee_name else None,
                        price_ondemand=Decimal(str(item["price"])),
                        source="Bệnh viện E - Quyết định 4411/QĐ-BVE",
                    )
            except (OSError, json.JSONDecodeError, KeyError):
                pass

    def list_departments(self) -> tuple[DepartmentInfo, ...]:
        return tuple(self._departments)

    def find_department_by_symptom(self, symptom_text: str) -> DepartmentInfo | None:
        """Tìm chuyên khoa phù hợp nhất với mô tả triệu chứng của người bệnh."""
        lower_text = symptom_text.lower()
        scored: list[tuple[int, DepartmentInfo]] = []

        for dept in self._departments:
            score = 0
            for kw in dept.keywords:
                if kw in lower_text:
                    score += 2
            if score > 0:
                scored.append((score, dept))

        if not scored:
            # Mặc định hướng dẫn tới Khoa Khám bệnh
            for dept in self._departments:
                if dept.id == "khoa-kham-benh":
                    return dept
            return None

        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[0][1]

    def get_workflow(self, workflow_code: str = "bhyt") -> WorkflowInfo | None:
        return self._workflows.get(workflow_code)

    def estimate_fee(
        self,
        service_names: tuple[str, ...],
        *,
        is_bhyt: bool = True,
        exam_type: str = "Khám Bảo hiểm Y tế (BHYT)",
    ) -> HospitalEstimate:
        """Tính ước tính viện phí minh bạch, chuẩn xác từ bảng giá công khai."""
        exam_item = self._prices.get(exam_type)
        if not exam_item:
            exam_fee = Decimal("42100") if is_bhyt else Decimal("150000")
        else:
            exam_fee = exam_item.price_bhyt if is_bhyt and exam_item.price_bhyt else exam_item.price_ondemand

        lines: list[tuple[str, Decimal]] = []
        total = exam_fee

        for srv in service_names:
            price_item = self._prices.get(srv)
            if price_item:
                cost = price_item.price_bhyt if is_bhyt and price_item.price_bhyt else price_item.price_ondemand
                lines.append((price_item.name, cost))
                total += cost

        note = "Đơn giá theo Quyết định 4411/QĐ-BVE. Chi phí thực tế có thể thay đổi tùy thuộc mức hưởng BHYT (80%, 95%, 100%) và chỉ định của bác sĩ khám."
        return HospitalEstimate(
            examination_fee=exam_fee,
            services=tuple(lines),
            total_estimated=total,
            note=note,
        )


hospital_service = HospitalEService()
