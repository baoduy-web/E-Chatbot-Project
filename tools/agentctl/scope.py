"""So thay đổi thật với phạm vi đã duyệt — MỘT hàm dùng chung cho hook ghi file, pre-commit và CI.

Dùng chung một hàm là có chủ đích: ở VNutriCare, phép kiểm cục bộ lệch phép kiểm CI làm CI đỏ sáu
lần liên tiếp (05–06/09/2026). Ba lớp cưỡng chế ở đây không thể lệch nhau vì chúng không có ba bản
logic.

Thứ tự phân xử cho mỗi file đổi:

1. `always_allowed` (nhật ký, quyết định, câu hỏi, sự cố) → luôn được.
2. Thuộc vùng bảo vệ → được nếu (a) là file THÊM MỚI trong vùng cho phép thêm, (b) ticket đã duyệt
   trước vùng đó trong `scope.protected`, hoặc (c) PR có nhãn duyệt của người. Không thì CẦN DUYỆT.
3. Thuộc làn độc quyền → ticket phải khai làn đó trong `scope.exclusive`.
4. Còn lại → phải khớp `scope.allow` của ticket.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime

from tools.agentctl.claims import Claim
from tools.agentctl.gitutil import Change
from tools.agentctl.globs import matches_any
from tools.agentctl.policy import Policy
from tools.agentctl.tickets import Ticket


@dataclass(frozen=True)
class Verdict:
    ticket_id: str | None
    checked: int
    errors: tuple[str, ...] = ()
    approvals_needed: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    @property
    def ok(self) -> bool:
        return not self.errors and not self.approvals_needed


def evaluate(
    changes: Sequence[Change],
    *,
    policy: Policy,
    ticket_id: str | None,
    ticket: Ticket | None,
    approved: bool,
) -> Verdict:
    if ticket_id and ticket is None:
        return Verdict(
            ticket_id,
            len(changes),
            errors=(
                f"nhánh gắn ticket `{ticket_id}` nhưng ticket không có trên nhánh gốc — kế hoạch phải được "
                "merge (người duyệt) trước khi làm",
            ),
        )
    if ticket is not None and ticket.state != "ready":
        return Verdict(
            ticket.id, len(changes), errors=(f"ticket `{ticket.id}` đang `{ticket.state}` — chưa được duyệt để làm",)
        )

    errors: list[str] = []
    approvals: list[str] = []
    warnings: list[str] = []
    for change in changes:
        path = change.path
        if matches_any(path, policy.always_allowed):
            continue
        zones = policy.zones_for(path)
        if zones:
            pending = [
                zone.id
                for zone in zones
                if not (change.status == "A" and zone.allow_additions)
                and not (ticket is not None and zone.id in ticket.protected)
            ]
            if pending and approved:
                warnings.append(f"{path} — vùng bảo vệ {pending}, đã có nhãn duyệt")
            elif pending:
                approvals.append(f"{path} — vùng bảo vệ {', '.join(pending)}")
            continue
        lanes = [lane.id for lane in policy.lanes_for(path)]
        if lanes:
            undeclared = [lane for lane in lanes if ticket is None or lane not in ticket.exclusive]
            if undeclared:
                errors.append(f"{path} — thuộc làn độc quyền {undeclared} mà ticket không khai trong `scope.exclusive`")
            continue
        if ticket is None:
            errors.append(
                f"{path} — nhánh không gắn ticket chỉ được sửa mục `always_allowed`, thêm ticket đề xuất, "
                "hoặc sửa vùng bảo vệ có người duyệt"
            )
        elif not matches_any(path, ticket.allow):
            errors.append(f"{path} — ngoài `scope.allow` của `{ticket.id}`")
    return Verdict(ticket_id, len(changes), tuple(errors), tuple(approvals), tuple(warnings))


def claim_findings(
    claims: dict[str, Claim], ticket_id: str, branch: str | None, moment: datetime
) -> tuple[list[str], list[str]]:
    """(lỗi, cảnh báo) về claim của ticket mà một PR/commit đang làm."""
    claim = claims.get(ticket_id)
    if claim is None:
        return [
            f"`{ticket_id}` không có claim trong sổ — chạy `python -m tools.agentctl start {ticket_id} --role <Rn>` "
            "trước khi làm, để agent khác biết phạm vi này đang bận"
        ], []
    if branch and claim.branch != branch:
        return [f"claim `{ticket_id}` thuộc nhánh `{claim.branch}`, còn thay đổi này đến từ `{branch}`"], []
    if claim.expired(moment):
        return [], [
            f"claim `{ticket_id}` đã hết hạn {claim.lease_until} — `renew` ngay, nếu không agent khác có thể "
            "tiếp quản phạm vi này"
        ]
    return [], []


def render(verdict: Verdict, *, label: str, local: bool) -> str:
    head = f"check-scope · ticket {verdict.ticket_id or '(không có)'} · {verdict.checked} file"
    lines = [head]
    if verdict.errors:
        lines.append(f"🔴 VI PHẠM ({len(verdict.errors)})")
        lines += [f"  - {item}" for item in verdict.errors]
    if verdict.approvals_needed:
        where = "cục bộ không thấy nhãn PR — CI sẽ chặn nếu thiếu" if local else f"cần nhãn `{label}` do chủ vùng gắn"
        lines.append(f"🟡 CẦN NGƯỜI DUYỆT ({len(verdict.approvals_needed)}) — {where}")
        lines += [f"  - {item}" for item in verdict.approvals_needed]
    if verdict.warnings:
        lines.append(f"⚠️  CẢNH BÁO ({len(verdict.warnings)})")
        lines += [f"  - {item}" for item in verdict.warnings]
    if not (verdict.errors or verdict.approvals_needed or verdict.warnings):
        lines.append("✅ Mọi thay đổi nằm trong phạm vi đã duyệt.")
    if verdict.errors:
        lines.append(
            "Cần thêm phạm vi? ĐỪNG sửa ticket trong nhánh này — mở câu hỏi: "
            '`python -m tools.agentctl new question --title "..." --blocking <ID>`'
        )
    return "\n".join(lines)
