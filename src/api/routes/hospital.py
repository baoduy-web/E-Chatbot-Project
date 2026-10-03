"""Endpoint tra cứu thông tin khoa phòng, quy trình và viện phí Bệnh viện E."""

from __future__ import annotations

from decimal import Decimal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.domain.healthcare.hospital_service import hospital_service

router = APIRouter(prefix="/api/v1/hospital", tags=["Bệnh viện E Tri thức"])


class DepartmentResponse(BaseModel):
    id: str
    name: str
    category: str
    location: str
    lead: str | None = None
    hotline: str | None = None
    services: list[str] = Field(default_factory=list)
    description: str


class WorkflowStepResponse(BaseModel):
    step_number: int
    title: str
    detail: str
    location: str


class WorkflowResponse(BaseModel):
    code: str
    name: str
    location: str
    steps: list[WorkflowStepResponse]


class EstimateRequest(BaseModel):
    services: list[str] = Field(default_factory=list, description="Danh sách tên các xét nghiệm/chụp chiếu cần làm")
    is_bhyt: bool = Field(default=True, description="Có sử dụng thẻ BHYT hay không")
    exam_type: str = Field(default="Khám Bảo hiểm Y tế (BHYT)", description="Hình thức khám")


class EstimateResponse(BaseModel):
    examination_fee: Decimal
    services: list[dict[str, object]]
    total_estimated: Decimal
    note: str


@router.get("/departments", response_model=list[DepartmentResponse])
def get_departments() -> list[DepartmentResponse]:
    """Lấy danh sách các trung tâm, khoa phòng tại Bệnh viện E."""
    depts = hospital_service.list_departments()
    return [
        DepartmentResponse(
            id=d.id,
            name=d.name,
            category=d.category,
            location=d.location,
            lead=d.lead,
            hotline=d.hotline,
            services=list(d.services),
            description=d.description,
        )
        for d in depts
    ]


@router.get("/workflows/{code}", response_model=WorkflowResponse)
def get_workflow(code: str) -> WorkflowResponse:
    """Lấy chi tiết quy trình khám bệnh (bhyt, on_demand, emergency)."""
    wf = hospital_service.get_workflow(code)
    if not wf:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy quy trình với mã `{code}`")

    return WorkflowResponse(
        code=wf.code,
        name=wf.name,
        location=wf.location,
        steps=[
            WorkflowStepResponse(
                step_number=s.step_number,
                title=s.title,
                detail=s.detail,
                location=s.location,
            )
            for s in wf.steps
        ],
    )


@router.post("/estimate", response_model=EstimateResponse)
def estimate_cost(payload: EstimateRequest) -> EstimateResponse:
    """Ước tính chi phí khám và cận lâm sàng theo bảng giá Bệnh viện E."""
    res = hospital_service.estimate_fee(
        tuple(payload.services),
        is_bhyt=payload.is_bhyt,
        exam_type=payload.exam_type,
    )
    return EstimateResponse(
        examination_fee=res.examination_fee,
        services=[{"service_name": name, "price": price} for name, price in res.services],
        total_estimated=res.total_estimated,
        note=res.note,
    )
