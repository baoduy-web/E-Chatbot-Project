"""Kiểm cấu trúc mọi mục công việc trong cây làm việc: ticket, câu hỏi, quyết định, sự cố, nhật ký.

Chạy trong CI (job `guards`) và trong lưới canh `tests/guards/test_work_items.py`. Một ticket hỏng
cú pháp phát hiện ở đây rẻ hơn nhiều so với phát hiện lúc một agent claim nó.
"""

from __future__ import annotations

from pathlib import Path

from tools.agentctl.entries import HANDOFF_STATUSES, QUESTION_STATUSES, WORK_DIR
from tools.agentctl.policy import Policy
from tools.agentctl.tickets import TICKET_ID, TicketError, split_front_matter, validate_tickets_dir


def _front_matter_problems(root: Path, folder: str, *, needs_id: bool) -> list[str]:
    problems: list[str] = []
    directory = root / WORK_DIR / folder
    for file in sorted(directory.rglob("*.md")) if directory.is_dir() else []:
        if file.name == "README.md" or file.name.startswith("_"):
            continue
        rel = file.relative_to(root).as_posix()
        try:
            data, _body = split_front_matter(file.read_text(encoding="utf-8"))
        except TicketError as exc:
            problems.append(f"{rel}: {exc}")
            continue
        if needs_id and data.get("id") != file.stem:
            problems.append(f"{rel}: `id` phải trùng tên file (`{file.stem}`)")
        if folder == "questions":
            if data.get("status") not in QUESTION_STATUSES:
                problems.append(f"{rel}: `status` phải thuộc {QUESTION_STATUSES}")
            blocking = data.get("blocking") or []
            if not isinstance(blocking, list) or not all(isinstance(b, str) and TICKET_ID.match(b) for b in blocking):
                problems.append(f"{rel}: `blocking` phải là danh sách mã ticket")
        if folder == "handoffs":
            if data.get("status") not in HANDOFF_STATUSES:
                problems.append(f"{rel}: `status` phải thuộc {HANDOFF_STATUSES}")
            ticket = data.get("ticket")
            if ticket is not None and not (isinstance(ticket, str) and TICKET_ID.match(ticket)):
                problems.append(f"{rel}: `ticket` phải là mã ticket hoặc null")
    return problems


def validate_work_items(root: Path, policy: Policy) -> list[str]:
    problems = validate_tickets_dir(root, policy)
    problems += _front_matter_problems(root, "questions", needs_id=True)
    problems += _front_matter_problems(root, "decisions", needs_id=True)
    problems += _front_matter_problems(root, "incidents", needs_id=True)
    problems += _front_matter_problems(root, "handoffs", needs_id=True)
    problems += _front_matter_problems(root, "log", needs_id=False)
    return problems
