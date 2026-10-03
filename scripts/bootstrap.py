"""Khởi tạo dự án mới từ template: đổi tên dự án, rồi in danh sách việc NGƯỜI phải tự làm.

Mặc định CHẠY THỬ (chỉ in file sẽ đổi). Ghi thật thêm `--apply`.

    python scripts/bootstrap.py --name "Tên Dự Án" --slug ten-du-an
    python scripts/bootstrap.py --name "Tên Dự Án" --slug ten-du-an --apply
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_NAME = "Agent Project Template"
TEMPLATE_SLUG = "agent-project-template"
SKIP_DIRS = {".git", ".venv", "node_modules", ".next", ".worktrees", "__pycache__", ".mypy_cache", ".ruff_cache"}
TEXT_SUFFIXES = {".md", ".py", ".toml", ".yaml", ".yml", ".json", ".ts", ".tsx", ".mjs", ".txt", ".ini", ".example", ""}
_SLUG = re.compile(r"^[a-z][a-z0-9-]{2,40}$")

MANUAL_STEPS = """
Việc NGƯỜI phải làm sau khi khởi tạo (agent không làm thay được):
  1. Chọn hình dạng đội: `python scripts/generate_team_docs.py --team-size <solo|small|standard|large>
     --complexity <lite|standard|strict>` — sinh docs/GOVERNANCE.md + .github/CODEOWNERS + chủ vùng bảo
     vệ. Xem lựa chọn: docs/design/presets/README.md. Bỏ qua bước này = giữ mặc định standard/standard.
  2. docs/GOVERNANCE.md — điền người thật vào cột "Người"; quyết "Ghi công cụ AI: có/không".
  3. .github/CODEOWNERS — thay handle giả (@rN-...) bằng tài khoản thật; agent dùng tài khoản KHÔNG có
     trong đó.
  4. docs/design/PRD.md và docs/design/invariants.yaml — phạm vi, không-mục-tiêu, bất biến miền (+ lưới canh).
  5. Tạo repo trên git host; bật branch protection cho `main` (require PR, require status checks,
     require review from Code Owners — số approval theo GOVERNANCE.md §3); KHÔNG bảo vệ nhánh `agent-claims`.
  6. Mỗi bản clone: `make setup` (hoặc `git config core.hooksPath scripts/githooks`).
  7. Render: tạo từ render.yaml, đặt biến `sync: false`, bật "After CI Checks Pass".
  8. Vercel: Root Directory = web, đặt NEXT_PUBLIC_API_BASE_URL cho cả 3 môi trường,
     Deployment Checks chọn đủ job của ci.yml.
  9. Xoá ticket mẫu docs/work/tickets/EXM-01.md và miền mẫu src/domain/catalog khi có miền thật.
 10. Commit đầu tiên, rồi chạy `python scripts/ci_local.py` để xác nhận mọi thứ xanh.
"""


def _files() -> list[Path]:
    return [
        path
        for path in ROOT.rglob("*")
        if path.is_file()
        and not SKIP_DIRS.intersection(path.relative_to(ROOT).parts)
        and (path.suffix in TEXT_SUFFIXES or path.name in {"Dockerfile", "Makefile", "CODEOWNERS"})
        and path.resolve() != Path(__file__).resolve()
    ]


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--name", required=True, help="tên hiển thị của dự án")
    parser.add_argument("--slug", required=True, help="tên máy: chữ thường, số, gạch nối")
    parser.add_argument("--apply", action="store_true", help="ghi thật (mặc định chỉ chạy thử)")
    args = parser.parse_args()
    if not _SLUG.match(args.slug):
        print("🔴 --slug phải khớp ^[a-z][a-z0-9-]{2,40}$", file=sys.stderr)
        return 2

    changed: list[str] = []
    for path in _files():
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        updated = text.replace(TEMPLATE_NAME, args.name).replace(TEMPLATE_SLUG, args.slug)
        if updated != text:
            changed.append(path.relative_to(ROOT).as_posix())
            if args.apply:
                path.write_text(updated, encoding="utf-8", newline="\n")

    verb = "Đã đổi" if args.apply else "Sẽ đổi (chạy thử — thêm --apply để ghi)"
    print(f"{verb} {len(changed)} file:")
    print("\n".join(f"  - {rel}" for rel in changed))
    if args.apply:
        print("\nSau khi đổi tên: `python scripts/export_openapi.py` (tiêu đề API nằm trong hợp đồng).")
    print(MANUAL_STEPS)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
