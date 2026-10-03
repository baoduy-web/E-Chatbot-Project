"""Bật/tắt pack kỹ năng cho dự án — trục thứ ba bên cạnh team-size × complexity.

    python scripts/packs.py --list              # pack nào có, pack nào đang bật, gợi ý theo loại dự án
    python scripts/packs.py --install ai-llm    # cài skill của pack vào .claude/skills/ + ghi profile
    python scripts/packs.py --remove ai-llm     # gỡ
    python scripts/packs.py --check             # CI: đỏ nếu .claude/skills/ lệch project-profile.yaml

Vì sao có trục này: mô tả của MỌI skill được nạp vào ngữ cảnh ở MỌI phiên. Cài hết cho mọi dự án là bắt
dự án CRUD trả giá ngữ cảnh cho kỹ năng finetune nó không bao giờ dùng. Xem `packs/README.md`.
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.agentctl.errors import AgentctlError  # noqa: E402
from tools.agentctl.policy import yaml_error_message  # noqa: E402

REGISTRY_PATH = ROOT / "packs" / "registry.yaml"
PROFILE_PATH = ROOT / "docs" / "design" / "project-profile.yaml"
SKILLS_DIR = ROOT / ".claude" / "skills"


class PackError(AgentctlError):
    """Sổ đăng ký hoặc hồ sơ dự án sai cấu trúc, hoặc pack không cài được."""


def _load_yaml(path: Path, ten: str) -> Any:
    """YAML hỏng phải thành thông điệp đọc được, không phải traceback — cùng cách `policy.py` làm."""
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise PackError(yaml_error_message(ten, exc)) from exc


def load_registry() -> dict[str, Any]:
    if not REGISTRY_PATH.is_file():
        raise PackError("không thấy packs/registry.yaml")
    data = _load_yaml(REGISTRY_PATH, "packs/registry.yaml")
    if not isinstance(data, dict) or not isinstance(data.get("packs"), dict):
        raise PackError("packs/registry.yaml phải có mapping `packs`")
    if not isinstance(data.get("core"), list):
        raise PackError("packs/registry.yaml phải có danh sách `core`")
    return data


def load_profile() -> dict[str, Any]:
    if not PROFILE_PATH.is_file():
        raise PackError("không thấy docs/design/project-profile.yaml")
    data = _load_yaml(PROFILE_PATH, "docs/design/project-profile.yaml")
    if not isinstance(data, dict):
        raise PackError("project-profile.yaml phải là mapping")
    data.setdefault("packs", [])
    if not isinstance(data["packs"], list):
        raise PackError("project-profile.yaml: `packs` phải là danh sách")
    return data


def write_enabled(packs: list[str]) -> None:
    """Ghi lại danh sách pack, GIỮ NGUYÊN chú thích trong file (yaml.dump sẽ xoá sạch chúng)."""
    text = PROFILE_PATH.read_text(encoding="utf-8")
    value = "[]" if not packs else "[" + ", ".join(sorted(packs)) + "]"
    new_text, count = re.subn(r"(?m)^packs:.*$", f"packs: {value}", text, count=1)
    if count != 1:
        raise PackError("project-profile.yaml thiếu dòng `packs:` — thêm lại rồi chạy lệnh này")
    PROFILE_PATH.write_text(new_text, encoding="utf-8", newline="\n")


def write_project_type(kind: str) -> None:
    """Ghi loại dự án, giữ nguyên chú thích. Chỉ ghi loại — KHÔNG tự bật pack: bật pack là quyết định người."""
    text = PROFILE_PATH.read_text(encoding="utf-8")
    new_text, count = re.subn(r"(?m)^project_type:.*$", f"project_type: {kind}", text, count=1)
    if count != 1:
        raise PackError("project-profile.yaml thiếu dòng `project_type:`")
    PROFILE_PATH.write_text(new_text, encoding="utf-8", newline="\n")


def pack_skills(registry: dict[str, Any], name: str) -> list[str]:
    pack = registry["packs"].get(name)
    if pack is None:
        có = ", ".join(sorted(registry["packs"]))
        raise PackError(f"không có pack `{name}` — pack hiện có: {có}")
    return [str(s["name"]) for s in pack.get("skills", [])]


def expected_skills(registry: dict[str, Any], profile: dict[str, Any]) -> set[str]:
    names = {str(s) for s in registry["core"]}
    for pack in profile["packs"]:
        names |= set(pack_skills(registry, str(pack)))
    return names


def installed_skills() -> set[str]:
    if not SKILLS_DIR.is_dir():
        return set()
    return {p.name for p in SKILLS_DIR.iterdir() if p.is_dir() and (p / "SKILL.md").is_file()}


def _cmd_list(registry: dict[str, Any], profile: dict[str, Any]) -> int:
    enabled = set(profile["packs"])
    print(f"Loại dự án: {profile.get('project_type', 'unspecified')}")
    print(f"Skill lõi (luôn cài): {', '.join(registry['core'])}\n")
    for name, pack in registry["packs"].items():
        mark = "✅ đang bật" if name in enabled else ("· sẵn sàng" if pack.get("status") == "ready" else "· chưa viết")
        print(f"{name:<10} {mark:<14} {pack.get('label', '')}")
        for skill in pack.get("skills", []):
            print(f"             - {skill['name']}: {skill.get('summary', '')}")
    suggestions = registry.get("project_types") or {}
    current = profile.get("project_type")
    if current in suggestions:
        print(f"\nGợi ý cho `{current}`: {', '.join(suggestions[current]) or '(chỉ lõi)'}")
    else:
        print("\nGợi ý theo loại dự án:")
        for kind, packs in suggestions.items():
            print(f"  {kind:<14} {', '.join(packs) or '(chỉ lõi)'}")
    return 0


def _cmd_install(registry: dict[str, Any], profile: dict[str, Any], name: str) -> int:
    pack = registry["packs"].get(name)
    if pack is None:
        raise PackError(f"không có pack `{name}` — pack hiện có: {', '.join(sorted(registry['packs']))}")
    if pack.get("status") != "ready":
        raise PackError(
            f"pack `{name}` mới chốt phạm vi, CHƯA có nội dung (status: {pack.get('status')}).\n"
            f"   Viết nội dung trước: packs/README.md nói cách thêm, rồi đổi status thành `ready`."
        )
    source = ROOT / "packs" / name / "skills"
    if not source.is_dir():
        raise PackError(f"pack `{name}` khai `ready` nhưng thiếu thư mục {source.relative_to(ROOT).as_posix()}")
    SKILLS_DIR.mkdir(parents=True, exist_ok=True)
    for skill in pack_skills(registry, name):
        src = source / skill
        if not (src / "SKILL.md").is_file():
            raise PackError(f"pack `{name}` khai skill `{skill}` nhưng thiếu {skill}/SKILL.md")
        shutil.copytree(src, SKILLS_DIR / skill, dirs_exist_ok=True)
        print(f"   + {skill}")
    if name not in profile["packs"]:
        write_enabled([*profile["packs"], name])
    print(f"✅ Đã bật pack `{name}`. Ghi vào docs/design/project-profile.yaml.")
    return 0


def _cmd_remove(registry: dict[str, Any], profile: dict[str, Any], name: str) -> int:
    if name not in profile["packs"]:
        raise PackError(f"pack `{name}` không đang bật")
    core = {str(s) for s in registry["core"]}
    còn_lại = [p for p in profile["packs"] if p != name]
    # Skill mà pack KHÁC vẫn cần thì giữ lại — hai pack chia nhau một skill là hợp lệ.
    giữ = core | {s for p in còn_lại for s in pack_skills(registry, p)}
    for skill in pack_skills(registry, name):
        if skill in giữ:
            continue
        target = SKILLS_DIR / skill
        if target.is_dir():
            shutil.rmtree(target)
            print(f"   - {skill}")
    write_enabled(còn_lại)
    print(f"✅ Đã tắt pack `{name}`.")
    return 0


def _cmd_check(registry: dict[str, Any], profile: dict[str, Any]) -> int:
    expected = expected_skills(registry, profile)
    installed = installed_skills()
    thiếu = sorted(expected - installed)
    thừa = sorted(installed - expected)
    if thiếu or thừa:
        print("🔴 .claude/skills/ lệch docs/design/project-profile.yaml:", file=sys.stderr)
        if thiếu:
            print(f"   thiếu (profile bật nhưng chưa cài): {', '.join(thiếu)}", file=sys.stderr)
        if thừa:
            print(f"   thừa (đã cài nhưng profile không bật): {', '.join(thừa)}", file=sys.stderr)
        print("   Sửa: python scripts/packs.py --install <pack> / --remove <pack>", file=sys.stderr)
        return 1
    print(f"✅ {len(installed)} skill khớp project-profile.yaml.")
    return 0


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--list", action="store_true", help="liệt kê pack và trạng thái")
    group.add_argument("--install", metavar="PACK", help="bật một pack")
    group.add_argument("--remove", metavar="PACK", help="tắt một pack")
    group.add_argument("--check", action="store_true", help="CI: đỏ nếu skill đã cài lệch profile")
    group.add_argument("--set-type", metavar="LOẠI", help="ghi loại dự án (không tự bật pack)")
    args = parser.parse_args()

    try:
        registry = load_registry()
        if args.set_type:
            hợp_lệ = set(registry.get("project_types") or {})
            if args.set_type not in hợp_lệ:
                raise PackError(f"loại dự án `{args.set_type}` không có — chọn: {', '.join(sorted(hợp_lệ))}")
            write_project_type(args.set_type)
            print(f"✅ project_type = `{args.set_type}`")
            gợi_ý = registry["project_types"][args.set_type]
            print(f"   Pack gợi ý: {', '.join(gợi_ý) or '(chỉ lõi)'} — bật bằng `--install <pack>` khi cần.")
            return 0
        profile = load_profile()
        if args.list:
            return _cmd_list(registry, profile)
        if args.install:
            return _cmd_install(registry, profile, args.install)
        if args.remove:
            return _cmd_remove(registry, profile, args.remove)
        return _cmd_check(registry, profile)
    except AgentctlError as exc:
        print(f"🔴 {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
