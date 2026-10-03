"""Sự thật git cho mục bàn giao — điền sẵn để agent hết hạn mức vẫn bàn giao được bằng MỘT lệnh.

Vì sao có module riêng
----------------------
Ở một dự án thực tế, hai agent (của hai nhà cung cấp) thay nhau làm một hàng việc vì mỗi bên lần lượt hết hạn mức.
Bên nào hết hạn mức thì dừng NGAY GIỮA CHỪNG — đúng lúc nó không còn sức viết ghi chú bàn giao tử tế. Hệ quả:
file hướng dẫn phải ghi tay "việc dở lúc bàn giao" và dễ lệch thực tế. Những gì đo được từ git (nhánh, commit
cuối, file chưa commit, commit chưa đẩy) thì không cần ai viết: lệnh `new handoff` điền sẵn, agent chỉ bổ
sung phần máy không biết (vì sao dở, đừng làm gì, lệnh đầu tiên của người kế tiếp).
"""

from __future__ import annotations

from pathlib import Path

from tools.agentctl.gitutil import current_branch, run_git
from tools.agentctl.tickets import ticket_id_from_branch

MAX_DIRTY_LINES = 40


def _first_line(repo: Path, args: list[str], fallback: str) -> str:
    result = run_git(repo, args)
    text = result.stdout.strip().splitlines()
    return text[0] if result.returncode == 0 and text else fallback


def collect_facts(repo: Path) -> dict[str, str]:
    """Trạng thái git hiện tại dưới dạng chuỗi sẵn để điền khuôn. Không bao giờ ném lỗi vì repo trống."""
    branch = current_branch(repo)
    # `--untracked-files=all`: mặc định git gộp thư mục chưa theo dõi thành `?? src/` — agent kế tiếp không biết file nào.
    status = run_git(repo, ["-c", "core.quotepath=off", "status", "--porcelain", "--untracked-files=all"])
    dirty = [line for line in status.stdout.splitlines() if line] if status.returncode == 0 else []
    shown = dirty[:MAX_DIRTY_LINES]
    if len(dirty) > MAX_DIRTY_LINES:
        shown.append(f"... và {len(dirty) - MAX_DIRTY_LINES} dòng nữa")
    unpushed = _first_line(repo, ["rev-list", "--count", "@{upstream}..HEAD"], "")
    return {
        "branch": branch or "(detached HEAD)",
        "head": _first_line(repo, ["rev-parse", "--short", "HEAD"], "(chưa có commit)"),
        "subject": _first_line(repo, ["log", "-1", "--format=%s"], ""),
        "ticket": (ticket_id_from_branch(branch) if branch else None) or "",
        "dirty": "\n".join(shown) if shown else "(cây làm việc sạch)",
        "dirty_count": str(len(dirty)),
        "unpushed": unpushed or "không rõ (nhánh chưa có upstream)",
    }
