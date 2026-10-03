"""Bảng trạng thái SUY RA — không ai sửa tay, nên không bao giờ lệch sự thật và không sinh xung đột.

- `ready`        : ticket đã duyệt, chưa ai claim.
- `đang làm`     : có claim còn hạn.
- `claim quá hạn`: lease hết mà chưa release — agent có thể đã dừng giữa chừng.
- `đã merge`     : mã ticket xuất hiện trong lịch sử nhánh gốc.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from tools.agentctl.claims import Claim, ClaimRegistry
from tools.agentctl.entries import WORK_DIR
from tools.agentctl.gitutil import list_files, show_file
from tools.agentctl.lifecycle import load_context
from tools.agentctl.tickets import TicketError, load_ticket, merged_ticket_ids, split_front_matter


def render_board(repo: Path, *, fetch: bool, moment: datetime) -> str:
    policy, base_ref = load_context(repo, fetch=fetch)
    registry = ClaimRegistry(repo, policy)
    claims: dict[str, Claim] = registry.read(registry.fetch() if fetch else registry.local_tip())
    merged = merged_ticket_ids(repo, base_ref)

    rows: dict[str, list[str]] = {"đang làm": [], "claim quá hạn": [], "ready": [], "proposed": [], "đã merge": []}
    broken: list[str] = []
    for path in list_files(repo, base_ref, f"{policy.tickets_dir}/"):
        name = path.rsplit("/", 1)[-1]
        if not name.endswith(".md") or name.startswith("_") or name == "README.md":
            continue
        try:
            ticket = load_ticket(repo, policy, name[:-3], base_ref)
        except TicketError as exc:
            broken.append(str(exc))
            continue
        if ticket is None or ticket.state == "cancelled":
            continue
        claim = claims.get(ticket.id)
        label = f"{ticket.id} — {ticket.title} [{ticket.owner_role}]"
        if claim and not claim.expired(moment):
            rows["đang làm"].append(f"{label} · {claim.on_behalf_of} · `{claim.branch}` · hạn {claim.lease_until}")
        elif claim:
            rows["claim quá hạn"].append(f"{label} · {claim.on_behalf_of} · hết hạn {claim.lease_until}")
        elif ticket.id in merged:
            rows["đã merge"].append(label)
        else:
            rows[ticket.state].append(label)

    open_questions: list[str] = []
    for path in list_files(repo, base_ref, f"{WORK_DIR}/questions/"):
        text = show_file(repo, base_ref, path)
        if not text or path.endswith("README.md"):
            continue
        try:
            data, _body = split_front_matter(text)
        except TicketError:
            continue
        if data.get("status") == "open":
            open_questions.append(
                f"{data.get('id', path)} → {data.get('answer_by', '?')} · chặn {data.get('blocking') or []}"
            )

    lines = [f"Bảng công việc tại `{base_ref}`" + ("" if fetch else " (chưa kéo mới)")]
    for title, items in rows.items():
        lines.append(f"\n## {title} ({len(items)})")
        lines += [f"- {item}" for item in items] or ["- (trống)"]
    lines.append(f"\n## câu hỏi đang mở ({len(open_questions)})")
    lines += [f"- {item}" for item in open_questions] or ["- (trống)"]
    if broken:
        lines.append(f"\n## ticket hỏng ({len(broken)}) — sửa trước khi ai claim")
        lines += [f"- {item}" for item in broken]
    return "\n".join(lines)
