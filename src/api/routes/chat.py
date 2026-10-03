"""Endpoint hội thoại Multi-Agent cho Bác sĩ, Bệnh nhân và Điều dưỡng."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from src.agents.healthcare.orchestrator import master_orchestrator
from src.domain.healthcare.models import TriageLevel, UserRole

router = APIRouter(prefix="/api/v1/chat", tags=["Chat Multi-Agent"])


class ChatMessageRequest(BaseModel):
    session_id: str = Field(default="default_session", description="ID phiên trò chuyện")
    message: str = Field(..., min_length=1, description="Nội dung tin nhắn")
    role: UserRole = Field(default=UserRole.PATIENT, description="Vai trò: patient, doctor, nurse, admin")
    user_name: str = Field(default="Người dùng", description="Tên người dùng")
    metadata: dict[str, Any] = Field(default_factory=dict)


class CitationResponse(BaseModel):
    title: str
    url: str
    category: str
    snippet: str
    confidence: float


class RedFlagAlertResponse(BaseModel):
    is_triggered: bool
    symptoms_detected: list[str] = Field(default_factory=list)
    emergency_guidance: str | None = None
    hotline: str = "115"
    nearest_emergency: str = "Khoa Cấp cứu 24/7 - Nhà C Bệnh viện E"


class ChatMessageResponse(BaseModel):
    session_id: str
    response: str
    agent_name: str
    triage_level: TriageLevel
    red_flag: RedFlagAlertResponse
    citations: list[CitationResponse] = Field(default_factory=list)
    suggested_specialty: str | None = None
    suggested_actions: list[str] = Field(default_factory=list)
    medical_disclaimer: str


@router.post("/message", response_model=ChatMessageResponse)
def handle_chat_message(payload: ChatMessageRequest) -> ChatMessageResponse:
    """Tiếp nhận tin nhắn, kiểm tra Red Flags cấp cứu, che PII và định tuyến tới Agent chuyên trách."""
    orchestrator_res = master_orchestrator.process_message(
        session_id=payload.session_id,
        message=payload.message,
        role=payload.role,
        user_name=payload.user_name,
    )

    red_flag_dto = RedFlagAlertResponse(
        is_triggered=orchestrator_res.red_flag.is_triggered,
        symptoms_detected=list(orchestrator_res.red_flag.symptoms_detected),
        emergency_guidance=orchestrator_res.red_flag.emergency_guidance,
        hotline=orchestrator_res.red_flag.hotline,
        nearest_emergency=orchestrator_res.red_flag.nearest_emergency,
    )

    citations_dto = [
        CitationResponse(
            title=c.title,
            url=c.url,
            category=c.category,
            snippet=c.snippet,
            confidence=c.confidence,
        )
        for c in orchestrator_res.citations
    ]

    return ChatMessageResponse(
        session_id=orchestrator_res.session_id,
        response=orchestrator_res.response,
        agent_name=orchestrator_res.agent_name,
        triage_level=orchestrator_res.triage_level,
        red_flag=red_flag_dto,
        citations=citations_dto,
        suggested_specialty=orchestrator_res.suggested_specialty,
        suggested_actions=list(orchestrator_res.suggested_actions),
        medical_disclaimer=orchestrator_res.medical_disclaimer,
    )
