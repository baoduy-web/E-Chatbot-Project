"""Sinh mục công việc — mỗi mục là MỘT file riêng, tên duy nhất theo ngày + slug.

Vì sao không dùng một file nhật ký chung
----------------------------------------
Ở VNutriCare, `DEVLOG.md` (1,2 MB) bị sửa 203 lần trong 4 tuần bởi nhiều người và nhiều agent —
mọi nhánh cùng nối vào CUỐI một file nên gần như mọi merge đều đụng nhau. Một file cho một mục thì
hai agent ghi cùng lúc tạo hai file khác nhau: không có gì để xung đột.

Vì sao mã theo ngày + slug, không theo số thứ tự
------------------------------------------------
"Lấy số tiếp theo" (DEC-299 → DEC-300) là một cuộc đua: hai agent cùng đọc 299 và cùng cấp 300.
Mã `DEC-20260915-ten-quyet-dinh` không cần biết ai khác đang cấp mã gì.
"""

from __future__ import annotations

import json
import re
import unicodedata
from collections.abc import Mapping, Sequence
from datetime import datetime
from pathlib import Path

from tools.agentctl.errors import AgentctlError

WORK_DIR = "docs/work"
KINDS = ("log", "decision", "question", "incident", "handoff")
QUESTION_STATUSES = ("open", "answered", "withdrawn")
HANDOFF_STATUSES = ("open", "taken", "closed")

_LOG = """---
kind: log
date: {date}
role: {role}
tickets: []
---
# {title}

- **Làm:**
- **Bằng chứng:** (lệnh đã chạy + kết quả rút gọn — không có bằng chứng thì chưa phải "xong")
- **Vướng:**
- **Tiếp theo:**
"""

_DECISION = """---
id: {id}
kind: decision
date: {date}
role: {role}
status: accepted
supersedes: null
tickets: []
---
# {title}

> Quyết định làm ĐỔI thiết kế đã chốt (`docs/design/`) không ghi ở đây — mở ADR ở `docs/design/adr/`.

## Bối cảnh

## Phương án đã cân nhắc

## Quyết định

## Hệ quả
"""

_QUESTION = """---
id: {id}
kind: question
status: open
asked_by: {role}
answer_by: {answer_by}
blocking: [{blocking}]
created: {date}
---
# {title}

## Câu hỏi

(Một câu hỏi đóng, trả lời được bằng một quyết định.)

## Vì sao agent không tự quyết

(Thiết kế/luật nào không phủ trường hợp này; đoán sai thì hại gì.)

## Phương án agent thấy — không chọn thay người

## Trả lời

(Người được hỏi điền, đổi `status: answered`. Quyết định đáng kể thì chuyển thành DEC hoặc ADR.)
"""

_INCIDENT = """---
id: {id}
kind: incident
date: {date}
role: {role}
severity: medium
---
# {title}

## Chuyện gì xảy ra

## Tác động

## Nguyên nhân gốc

## Đã làm gì

## Phòng ngừa

(Lưới canh hoặc quy tắc nào được thêm để lớp sự cố này không lặp lại — ghi đường dẫn test.)
"""

_HANDOFF = """---
id: {id}
kind: handoff
status: open
date: {date}
from_role: {role}
ticket: {ticket}
branch: {branch}
head: {head}
---
# {title}

> Bàn giao để agent kế tiếp (có thể khác nhà cung cấp) làm tiếp mà không làm lại từ đầu. Phần "Máy ghi
> sẵn" do `agentctl` điền từ git — KHÔNG sửa. Hết hạn mức giữa chừng thì chỉ cần giữ nguyên file này và
> điền dòng đầu mục "Còn dở". Người nhận đổi `status: taken`; xong việc đổi `closed`.

## Máy ghi sẵn (từ git, lúc bàn giao)

- Nhánh: `{branch_raw}` · commit cuối: `{head_raw}` {subject}
- Commit chưa đẩy lên upstream: {unpushed}
- File chưa commit ({dirty_count}):

```text
{dirty}
```

## Đã làm + bằng chứng

(Lệnh đã chạy + kết quả rút gọn. Phần đã commit chỉ cần trỏ hash.)

## Còn dở

(Nói thật. Chưa đạt tiêu chí nào thì ghi tiêu chí đó — không báo "xong" khi còn dở.)

## Đã thử và SAI — đừng làm lại

## Câu hỏi mở / cần người quyết

## Lệnh đầu tiên cho agent kế tiếp

```bash
git log --oneline -10 && git status
```
"""

_TICKET = """---
id: {id}
title: {title}
state: proposed
owner_role: {role}
design_refs: []
depends_on: []
scope:
  allow:
    - TODO/duong-dan/**
  exclusive: []
  protected: []
acceptance:
  - TODO — tiêu chí kiểm được bằng lệnh hoặc test
---
# {id} — {title}

## Bối cảnh

## Ghi chú cho người thực hiện

> Ticket `proposed` chưa claim được. Người duyệt đổi `state: ready` trong một PR riêng sau khi
> kiểm phạm vi `scope` không chồng ticket đang mở.
"""


def slugify(text: str, max_length: int = 48) -> str:
    folded = text.replace("đ", "d").replace("Đ", "D")
    ascii_text = unicodedata.normalize("NFKD", folded).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-")
    return slug[:max_length].rstrip("-") or "khong-ten"


def _handoff_fields(facts: Mapping[str, str]) -> dict[str, str]:
    """Trường điền khuôn bàn giao. Giá trị vào front matter đi qua `json.dumps` (JSON là YAML hợp lệ) để
    tên nhánh hay mã commit toàn chữ số không bị YAML hiểu thành kiểu khác."""
    branch, head = facts.get("branch", "?"), facts.get("head", "?")
    subject = facts.get("subject", "")
    return {
        "ticket": json.dumps(facts.get("ticket") or None),
        "branch": json.dumps(branch),
        "head": json.dumps(head),
        "branch_raw": branch,
        "head_raw": head,
        "subject": f"— {subject}" if subject else "",
        "unpushed": facts.get("unpushed", "không rõ"),
        "dirty": facts.get("dirty", "(không ghi)"),
        "dirty_count": facts.get("dirty_count", "?"),
    }


def _unique(path: Path) -> Path:
    if not path.exists():
        return path
    for counter in range(2, 100):
        candidate = path.with_name(f"{path.stem}-{counter}{path.suffix}")
        if not candidate.exists():
            return candidate
    raise AgentctlError(f"quá nhiều file trùng tên với {path.name}")


def create_entry(
    root: Path,
    kind: str,
    *,
    title: str,
    role: str,
    moment: datetime,
    blocking: Sequence[str] = (),
    answer_by: str = "R1",
    facts: Mapping[str, str] | None = None,
) -> Path:
    if kind not in KINDS:
        raise AgentctlError(f"loại mục `{kind}` không hỗ trợ, chọn trong {KINDS}")
    date, ymd, slug = moment.strftime("%Y-%m-%d"), moment.strftime("%Y%m%d"), slugify(title)
    if kind == "log":
        path = (
            root / WORK_DIR / "log" / moment.strftime("%Y") / moment.strftime("%m") / f"{date}-{role.lower()}-{slug}.md"
        )
        content = _LOG.format(date=date, role=role, title=title)
    else:
        prefix, template, folder = {
            "decision": ("DEC", _DECISION, "decisions"),
            "question": ("Q", _QUESTION, "questions"),
            "incident": ("INC", _INCIDENT, "incidents"),
            "handoff": ("HND", _HANDOFF, "handoffs"),
        }[kind]
        path = _unique(root / WORK_DIR / folder / f"{prefix}-{ymd}-{slug}.md")
        content = template.format(
            id=path.stem,
            date=date,
            role=role,
            title=title,
            answer_by=answer_by,
            blocking=", ".join(blocking),
            **_handoff_fields(facts or {}),
        )
    path = _unique(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def create_ticket(root: Path, tickets_dir: str, *, ticket_id: str, title: str, role: str) -> Path:
    path = root / tickets_dir / f"{ticket_id}.md"
    if path.exists():
        raise AgentctlError(f"{path.relative_to(root).as_posix()} đã tồn tại — mã ticket phải duy nhất")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_TICKET.format(id=ticket_id, title=title, role=role), encoding="utf-8")
    return path
