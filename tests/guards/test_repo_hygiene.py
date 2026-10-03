"""Repo không chứa bí mật, CSDL, phụ thuộc, bảng theo dõi nhị phân; có đủ file của mặt phẳng điều phối.

Vì sao: một `git add -A` là đẩy nguyên `.env.bak` (khoá thật) lên remote — VNutriCare phải chặn thêm cả họ
`.env.*` sau một lần xoay khoá (02/09/2026). Bảng Excel theo dõi việc bị 45 commit chạm trong 4 tuần và không
merge được.
"""

from __future__ import annotations

from scripts.check_structure import FORBIDDEN, REQUIRED, candidate_files, problems


def test_repo_sach() -> None:
    files = candidate_files()
    assert len(files) >= 50, "quét được quá ít file — lưới đang không kiểm gì"
    assert problems(files) == []


def test_bo_do_bat_duoc_file_cam_that() -> None:
    samples = [".env", "backend/.env.production", "docs/work/tien-do.xlsx", "data/app.db", "home/claude/x.py"]
    flagged = [path for path in samples if any(pattern.search(path) for pattern, _ in FORBIDDEN)]
    assert flagged == samples
    assert not any(pattern.search(".env.example") for pattern, _ in FORBIDDEN)
    assert "AGENTS.md" in REQUIRED
