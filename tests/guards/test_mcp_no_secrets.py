"""`.mcp.json` nằm trong git — không được chứa bí mật ở dạng thô.

Vì sao: cách thêm MCP server phổ biến nhất gắn thẳng khoá vào lệnh
(`claude mcp add ... --header "Authorization: Bearer rnd_..."`). Chạy ở phạm vi project là commit khoá
vào repo, và `git diff` chỉ hiện một dòng JSON trông vô hại. VNutriCare suýt gặp đúng chuyện này
(08/09/2026) — lần đó thoát chỉ vì lệnh không chạy được, không phải vì có gì chặn.

Khoá gì: không giá trị nào mang tiền tố khoá đã biết; header xác thực phải là tham chiếu `${TEN_BIEN}`.
Lỡ commit khoá: THU HỒI trước, xoá khỏi file sau — xoá khỏi lịch sử git không rút lại thứ đã đẩy.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MCP = ROOT / ".mcp.json"
KEY_PREFIXES = (
    "sk-",
    "sk_",
    "rnd_",
    "ghp_",
    "github_pat_",
    "sbp_",
    "AIza",
    "xoxb-",
    "eyJ",
    "postgres://",
    "postgresql://",
)
_ENV_REFERENCE = re.compile(r"\$\{?[A-Za-z_][A-Za-z0-9_]*\}?")


def _strings(node: object, path: str = "") -> list[tuple[str, str]]:
    if isinstance(node, dict):
        return [item for key, value in node.items() for item in _strings(value, f"{path}.{key}" if path else str(key))]
    if isinstance(node, list):
        return [item for index, value in enumerate(node) for item in _strings(value, f"{path}[{index}]")]
    return [(path, node)] if isinstance(node, str) else []


def secret_problems(data: object) -> list[str]:
    problems = [
        f"{where}: trông như khoá thô" for where, value in _strings(data) if any(p in value for p in KEY_PREFIXES)
    ]
    problems += [
        f"{where}: header xác thực phải là `${{TEN_BIEN}}`"
        for where, value in _strings(data)
        if any(word in where.lower() for word in ("authorization", "api_key", "token"))
        and not _ENV_REFERENCE.search(value)
    ]
    return problems


def test_mcp_json_khong_chua_bi_mat_tho() -> None:
    assert MCP.is_file(), "thiếu .mcp.json — lưới đang không kiểm gì"
    data = json.loads(MCP.read_text(encoding="utf-8"))
    assert "mcpServers" in data
    assert secret_problems(data) == []


def test_bo_do_bat_duoc_khoa_that() -> None:
    leaked = {"mcpServers": {"render": {"headers": {"Authorization": "Bearer rnd_abc123"}}}}
    clean = {"mcpServers": {"render": {"headers": {"Authorization": "Bearer ${RENDER_API_KEY}"}}}}
    assert secret_problems(leaked)
    assert secret_problems(clean) == []
