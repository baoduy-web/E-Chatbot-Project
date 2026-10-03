---
id: META-02
title: Để board thấy bàn giao còn mở trên nhánh feature chưa merge
state: proposed
owner_role: R1
design_refs:
  - docs/rules/70-multi-agent-coordination.md
depends_on: []
scope:
  allow:
    - tests/tools/test_board_handoffs.py
  exclusive: []
  protected: [coordination, design, rules]
acceptance:
  - "`python -m pytest tests/tools/test_board_handoffs.py -q` xanh; test thấy bàn giao `open` trên nhánh chưa merge"
  - "Bàn giao đã `closed` trên `main` không bị bản `open` cũ trên nhánh làm sống lại"
  - "`board` (không `--offline`) kéo cả nhánh feature của remote, không chỉ `main`"
  - "`python -m pytest tests/guards tests/tools -q` xanh; `python -m tools.agentctl check-scope` không vi phạm"
---
# META-02 — Board thấy bàn giao trên nhánh chưa merge

## Bối cảnh

Hạn chế đã ghi ở META-01: `agentctl board` chỉ đọc `origin/main` và chỉ fetch đúng nhánh `main`. Bàn giao do agent
hết hạn mức ghi lại nằm trên nhánh feature của nó, nên agent kế tiếp chạy `board` thấy "(trống)" và làm lại từ đầu.

## Ngoài phạm vi

- Không áp cùng cơ chế cho `questions/` (hiện vẫn chỉ đọc `main`) — đề xuất riêng nếu cần.
- Không đổi định dạng file bàn giao hay sổ claim.

## Ghi chú cho người thực hiện

Ticket `proposed`: người duyệt đổi `state: ready`. `main` luôn thắng khi cùng mã bàn giao có ở cả hai nơi, để
nhánh cũ còn bản `open` không làm sống lại việc đã đóng. Lệnh fetch là best-effort: mất mạng thì dùng các ref đã có.
