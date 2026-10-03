---
id: META-01
title: Bổ sung bàn giao, supervisor, cổng đẩy tùy chọn và luật dữ liệu cho bộ điều phối
state: proposed
owner_role: R1
design_refs:
  - docs/rules/70-multi-agent-coordination.md
  - docs/design/adr/0001-multi-agent-control-plane.md
depends_on: []
scope:
  allow:
    - README.md
    - docs/work/README.md
    - docs/work/handoffs/.gitkeep
    - scripts/check_structure.py
    - tests/tools/test_handoff.py
  exclusive: []
  protected: [constitution, design, rules, coordination, work-plan, guard-nets]
acceptance:
  - "`python -m pytest tests/guards tests/tools -q` xanh, gồm test_handoff.py và test_push_gate.py"
  - "`python -m tools.agentctl new handoff --role R3 --title x` sinh file qua `check-work`, git điền sẵn nhánh/commit/file dở"
  - "`scripts/check_structure.py` chặn `data/` (trừ .gitkeep) và tệp parquet/pkl/npy…"
  - "Hook pre-push tắt mặc định; bật thì chặn trừ ALLOW_PUSH=1 và luôn cho nhánh agent-claims qua"
  - "`python -m tools.agentctl check-scope` không vi phạm"
---
# META-01 — Bổ sung bộ điều phối từ kinh nghiệm vận hành nhiều agent thay phiên

## Bối cảnh

Rút từ một dự án thực tế nơi hai agent của hai nhà cung cấp thay nhau làm khi hết hạn mức, có một người duyệt
độc lập. Template còn thiếu: bàn giao có sự thật git điền sẵn, vai trò kiểm độc lập cả khoảng lịch sử, cổng đẩy
tùy chọn, chặn dữ liệu vào git, luật số đo trung thực, bẫy Windows, quy ước trao đổi giữa các làn song song.

## Ngoài phạm vi

- Không thêm công cụ chạy nền kiểu supervise.py hay dashboard (gắn chặt với từng dự án).
- Không đổi hành vi mặc định của luồng agent tự mở PR (cổng đẩy tắt mặc định).
- Không đổi `agentctl board` để đọc bàn giao từ nhánh chưa merge — đề xuất riêng.

## Ghi chú cho người thực hiện

Ticket `proposed`: người duyệt đổi `state: ready` sau khi xem. `scope.allow` chỉ có file ngoài vùng bảo vệ; các
file còn lại (AGENTS.md, coordination/, tools/, docs/rules/, docs/design/, tests/guards/, .claude/agents/,
scripts/githooks/, mẫu ticket) thuộc 6 vùng khai trong `scope.protected` — duyệt ticket này là phê duyệt trước
cho các vùng đó, thay cho nhãn `human-approved`.
