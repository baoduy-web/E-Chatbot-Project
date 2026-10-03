---
name: ticket-flow
description: Thực hiện một ticket từ đầu đến cuối theo quy trình của template — đọc ticket, tạo nhánh, viết test trước, chạy cổng cục bộ, mở PR, ghi nhật ký. Dùng khi bắt đầu một việc mới có mã ticket, khi chuẩn bị mở PR, hoặc khi không chắc bước tiếp theo trong vòng đời một thay đổi.
---

# Vòng đời một thay đổi

Luật đầy đủ: `docs/rules/50-workflow.md`. Đây là thủ tục chạy.

## 1. Trước khi gõ dòng code nào

- Đọc ticket (mã, tiêu chí nghiệm thu). Không có tiêu chí nghiệm thu kiểm được bằng lệnh/test ⇒ hỏi lại,
  đừng tự đoán.
- Đọc `docs/design/ARCHITECTURE.md` phần liên quan + `docs/rules/` của lĩnh vực đang đụng.
- **Hỏi: việc này có chạy song song với agent/người khác không?** Có ⇒ dùng skill `multi-agent` trước khi
  sửa file. Không ⇒ nhánh thường, nhẹ hơn.
- **Hỏi: có đụng vùng bảo vệ hay làn độc quyền không?** (`coordination/policy.yaml`) Có ⇒ cần duyệt trước,
  biết sớm rẻ hơn biết lúc CI đỏ.

## 2. Nhánh

```bash
git checkout main && git pull
git checkout -b <loại>/<MÃ-TICKET>-<mô-tả-ngắn>
```

Tên nhánh mang mã ticket là thứ `tools/agentctl` và hook `commit-msg` dựa vào — đặt sai tên thì hook chặn
commit, không phải để làm khó mà để lịch sử truy được về ticket.

## 3. Test trước, code sau

Viết test thất bại trước khi viết cài đặt. Không hứa "test sau" — test sau gần như luôn thành test viết
vừa khít code vừa viết, không phải test viết theo yêu cầu.

Nếu thay đổi khoá một quyết định thiết kế hoặc bài học sự cố ⇒ đó là **lưới canh**, dùng skill `guard-net`
(có bước bắt buộc chứng minh đỏ).

## 4. Cổng cục bộ — chạy TRƯỚC khi đẩy

```bash
python scripts/ci_local.py        # chạy đúng bộ lệnh CI chạy, không phải bộ gần giống
```

Cổng cục bộ là cổng chính trong lúc làm. CI không phải nơi để thử xem code có chạy không — phút CI là
ngân sách có hạn (`docs/rules/50-workflow.md`).

Đổi schema ⇒ migration trong **cùng PR**. Đổi API ⇒ `python scripts/export_openapi.py`. Đổi ranh giới hay
vùng bảo vệ ⇒ `python scripts/generate_diagrams.py` (skill `diagram`).

## 5. Commit

`type(scope): mô tả (MÃ-TICKET)` — `feat|fix|docs|test|refactor|chore`. Hook `commit-msg` kiểm; khi nó
chặn, đọc thông điệp lỗi, nó nói đúng chỗ sai.

Commit ít nhất một lần mỗi buổi làm. Commit khổng lồ cuối tuần khiến review bất khả thi.

## 6. PR

- Mở **nháp** (`gh pr create --draft`) khi còn đang làm: PR nháp không chạy CI, đẩy thoải mái, 0 phút.
- Bấm "Ready for review" khi **đã xong thật** ⇒ CI chạy đầy đủ đúng một lần.
- Mô tả PR: **Thay đổi gì · Vì sao · Cách test · Checklist**. Phần "Cách test" phải là lệnh người khác
  chạy lại được, không phải "đã test kỹ".
- PR > 400 dòng ⇒ tách nhỏ.

## 7. Kết buổi

Ghi một mục vào nhật ký. Dùng `python -m tools.agentctl new decision|question|incident ...` cho mục cần
file riêng — mỗi mục một file là lý do nhiều agent ghi cùng lúc mà không xung đột.

## Khi CI đỏ

Phân biệt trước khi sửa:
- **Lỗi thật** — log có nội dung cụ thể, thời lượng job bình thường.
- **Lỗi hạ tầng** — log rỗng/`BlobNotFound`, bước treo `in_progress` trong khi job báo fail, hoặc job đỏ
  trên commit có **cây mã trùng hệt** một commit đã xanh (`git rev-parse <sha>^{tree}`). Chạy lại trước
  khi đi đọc code.
