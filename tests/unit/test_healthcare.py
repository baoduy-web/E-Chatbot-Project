"""Kiểm thử đơn vị cho toàn bộ hệ thống Healthcare Multi-Agent & Bệnh viện E."""

from __future__ import annotations

from decimal import Decimal

from fastapi.testclient import TestClient

from src.agents.healthcare.orchestrator import master_orchestrator
from src.domain.healthcare.clinical import clinical_cds
from src.domain.healthcare.hospital_service import hospital_service
from src.domain.healthcare.models import TriageLevel, UserRole
from src.domain.healthcare.safety import pii_masker, red_flags_detector
from src.main import app

client = TestClient(app)


def test_red_flags_emergency_trigger() -> None:
    """Cờ đỏ cấp cứu bắt đúng tình huống nguy kịch và kích hoạt 115."""
    res1 = red_flags_detector.check("Bệnh nhân bị đau thắt ngực dữ dội lan lên vai và tay trái kèm vã mồ hôi")
    assert res1.is_triggered is True
    assert res1.hotline == "115"
    assert any("Đau thắt ngực" in s for s in res1.symptoms_detected)

    res2 = red_flags_detector.check("Người nhà tôi đột nhiên bị méo miệng và liệt nửa người bên phải")
    assert res2.is_triggered is True
    assert any("liệt mặt" in s.lower() or "đột quỵ" in s.lower() for s in res2.symptoms_detected)

    # Không báo động giả với triệu chứng thông thường
    res_normal = red_flags_detector.check("Tôi bị hắt hơi sổ mũi và đau đầu nhẹ 2 ngày nay")
    assert res_normal.is_triggered is False


def test_pii_masking() -> None:
    """Che giấu số điện thoại, CCCD 12 số và mã BHYT theo chuẩn an toàn thông tin."""
    raw = "Tôi tên Nguyễn Văn A, SĐT 0987654321, số CCCD 001234567890, mã thẻ BHYT GD4010123456789 đi khám"
    masked = pii_masker.mask(raw)
    assert "0987654321" not in masked
    assert "001234567890" not in masked
    assert "GD4010123456789" not in masked
    assert "[SỐ ĐIỆN THOẠI ĐÃ ẨN]" in masked
    assert "[CCCD/ĐỊNH DANH ĐÃ ẨN]" in masked


def test_hospital_department_lookup() -> None:
    """Tìm đúng chuyên khoa Bệnh viện E theo triệu chứng."""
    dept_cardio = hospital_service.find_department_by_symptom("Tôi bị đau tim khó thở và huyết áp cao")
    assert dept_cardio is not None
    assert dept_cardio.id == "tt-tim-mach"

    dept_gastro = hospital_service.find_department_by_symptom(
        "Tôi hay bị ợ chua trào ngược và đau vùng thượng vị dạ dày"
    )
    assert dept_gastro is not None
    assert dept_gastro.id == "tt-tieu-hoa"

    dept_rheuma = hospital_service.find_department_by_symptom(
        "Tôi bị sưng đau khớp gối đi lại kêu lạo xạo nghi thoái hóa"
    )
    assert dept_rheuma is not None
    assert dept_rheuma.id == "tt-co-xuong-khop"


def test_hospital_workflow_and_pricing() -> None:
    """Tra cứu quy trình khám BHYT và tính viện phí chuẩn xác."""
    wf = hospital_service.get_workflow("bhyt")
    assert wf is not None
    assert len(wf.steps) == 5
    assert wf.steps[0].step_number == 1
    assert "CỬA 3, 4, 5, 6" in wf.steps[0].detail

    estimate = hospital_service.estimate_fee(
        ("Siêu âm tim màu Doppler", "Chụp X-quang ngực thẳng kỹ thuật số"),
        is_bhyt=True,
    )
    assert estimate.examination_fee == Decimal("42100")
    assert estimate.total_estimated > Decimal("100000")


def test_drug_interaction_check() -> None:
    """Kiểm tra tương tác thuốc phát hiện đúng cặp chống chỉ định Warfarin + Aspirin."""
    res = clinical_cds.check_drug_interactions(("Warfarin", "Aspirin"))
    assert res.has_contraindication is True
    assert len(res.interactions) >= 1
    assert res.interactions[0].severity == "Contraindicated"


def test_clinical_soap_note_generation() -> None:
    """Sinh cấu trúc bệnh án SOAP chuẩn cho bác sĩ."""
    soap = clinical_cds.generate_clinical_soap(
        patient_id="PT-001",
        patient_name="Bệnh nhân Test",
        history_text="Đau vùng thượng vị dạ dày âm ỉ kèm ợ hơi ợ chua sau ăn",
    )
    assert soap.patient_id == "PT-001"
    assert "dạ dày" in soap.assessment.primary_diagnosis.lower() or "viêm" in soap.assessment.primary_diagnosis.lower()
    assert len(soap.plan.diagnostic_tests) > 0


def test_master_orchestrator_emergency_interception() -> None:
    """Orchestrator phải ngắt luồng ngay lập tức khi phát hiện tình trạng cấp cứu."""
    res = master_orchestrator.process_message(
        session_id="session-emerg",
        message="Tôi đang bị đau thắt tim nghẹt thở không thở được lan lên cổ",
        role=UserRole.PATIENT,
    )
    assert res.triage_level == TriageLevel.EMERGENCY
    assert res.red_flag.is_triggered is True
    assert "115" in res.response
    assert "Emergency Safety Interceptor" in res.agent_name


def test_api_chat_endpoint() -> None:
    """Gọi thử endpoint /api/v1/chat/message."""
    response = client.post(
        "/api/v1/chat/message",
        json={
            "session_id": "test-session",
            "message": "Tôi muốn hỏi quy trình khám bảo hiểm y tế tại Bệnh viện E",
            "role": "patient",
            "user_name": "Anh Hùng",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == "test-session"
    assert data["red_flag"]["is_triggered"] is False
    assert "Bệnh viện E" in data["response"]


def test_api_hospital_endpoints() -> None:
    """Gọi thử các endpoints tra cứu Bệnh viện E."""
    resp_depts = client.get("/api/v1/hospital/departments")
    assert resp_depts.status_code == 200
    depts = resp_depts.json()
    assert len(depts) >= 4

    resp_wf = client.get("/api/v1/hospital/workflows/bhyt")
    assert resp_wf.status_code == 200
    wf = resp_wf.json()
    assert wf["code"] == "bhyt"
    assert len(wf["steps"]) == 5

    resp_est = client.post(
        "/api/v1/hospital/estimate",
        json={
            "services": ["Siêu âm ổ bụng tổng quát"],
            "is_bhyt": True,
            "exam_type": "Khám Bảo hiểm Y tế (BHYT)",
        },
    )
    assert resp_est.status_code == 200
    est = resp_est.json()
    assert est["examination_fee"] == "42100"


def test_api_doctor_endpoints() -> None:
    """Gọi thử các endpoints dành cho bác sĩ."""
    resp_soap = client.post(
        "/api/v1/doctor/soap-note",
        json={
            "patient_id": "BN-12345",
            "patient_name": "Trần Thị Mai",
            "history_text": "Bệnh nhân đau tức ngực trái từng cơn khi gắng sức, huyết áp đo tại nhà 150/90",
        },
    )
    assert resp_soap.status_code == 200
    soap = resp_soap.json()
    assert soap["patient_id"] == "BN-12345"
    assert "I20" in (soap["assessment"]["icd10_code"] or "")

    resp_drugs = client.post(
        "/api/v1/doctor/drug-interactions",
        json={"drugs": ["Simvastatin", "Amiodarone"]},
    )
    assert resp_drugs.status_code == 200
    drugs_res = resp_drugs.json()
    assert drugs_res["has_contraindication"] is True
