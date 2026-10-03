---
id: EXM-02
title: Đổi định dạng lỗi báo giá trong hợp đồng API
state: ready
owner_role: R4
design_refs:
  - docs/design/ARCHITECTURE.md
depends_on: []
scope:
  allow:
    - src/api/errors.py
    - tests/unit/test_api.py
  exclusive: [api-contract]
  protected: []
acceptance:
  - "Ticket mẫu cho audit đa agent — chồng làn api-contract với EXM-01 có chủ đích"
---
# EXM-02 — Ticket mẫu để thử va chạm làn độc quyền

> Tạo cho một lượt audit đa agent (16/09/2026): CỐ Ý khai cùng làn `api-contract` với `EXM-01` để
> kiểm chứng `agentctl` từ chối hai claim tranh cùng làn qua GitHub remote thật, không chỉ trên bare
> repo cục bộ như test đơn vị. Xoá ticket này sau khi audit xong nếu không dùng làm ticket thật.
