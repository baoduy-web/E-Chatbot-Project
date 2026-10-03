# Pack kỹ năng

Skill **lõi** (`registry.yaml` mục `core:`) luôn cài — đó là cách template này vận hành. Phần còn lại
chia thành pack, bật theo loại dự án.

```bash
python scripts/packs.py --list              # pack nào có, đang bật cái nào, gợi ý theo loại dự án
python scripts/packs.py --install backend   # bật
python scripts/packs.py --remove backend    # tắt
python scripts/packs.py --check             # CI chạy lệnh này
```

## Vì sao chia pack thay vì cài hết

Mô tả của **mọi** skill được nạp vào ngữ cảnh ở **mọi** phiên của **mọi** agent. Một template 25 skill
bắt dự án CRUD trả giá ngữ cảnh vĩnh viễn cho kỹ năng finetune nó không bao giờ dùng. Chia pack giữ đúng
tinh thần opt-in của template: thứ gì không dùng thì không phải mang.

## Trạng thái pack

| Trạng thái | Nghĩa là |
|---|---|
| `ready` | Có nội dung trong `packs/<tên>/skills/`, cài được |
| `planned` | Đã chốt phạm vi và tên skill, **chưa có nội dung**. `--install` từ chối và nói rõ |

Hiện chỉ **`ai-llm`** là `ready` (17/09/2026); các pack còn lại `planned` — cố ý. **Viết nội dung một
pack khi có dự án thật cần nó**, không viết trước: skill viết khi chưa ai dùng thì không có gì kiểm chứng
nó đúng, và sẽ thành tài liệu chết đúng như mọi tài liệu viết trước nhu cầu.

`ai-llm` được viết trước vì dự án gốc của template (VNutriCare) là ứng dụng LLM thật. Số liệu về token,
cache, giá trong `token-economics` lấy từ tài liệu API chính thức kèm ngày kiểm — không lấy từ trí nhớ.

## Viết nội dung cho một pack đang `planned`

1. Tạo `packs/<pack>/skills/<tên-skill>/SKILL.md` cho **từng** skill mà `registry.yaml` khai — tên thư
   mục phải khớp `name` trong sổ đăng ký.
2. Frontmatter bắt buộc:
   ```markdown
   ---
   name: <trùng tên thư mục>
   description: <làm gì, và DÙNG KHI NÀO — câu "dùng khi" là thứ quyết định agent có gọi đúng lúc không>
   ---
   ```
3. Nội dung là **thủ tục**, không phải bài giảng: các bước chạy được, lệnh thật, bẫy cụ thể đã gặp. Nếu
   một đoạn không đổi được hành vi của người đọc thì bỏ.
4. Đổi `status: planned` → `ready` trong `registry.yaml`.
5. `python scripts/packs.py --install <pack>` rồi `python -m pytest tests/guards/test_packs.py -q`.

## Thêm một pack mới

Thêm mục vào `registry.yaml` với `label`, `status`, `suits` (loại dự án phù hợp) và danh sách `skills`
kèm `summary` một dòng. Cập nhật `project_types:` nếu pack nên được gợi ý cho một loại dự án.

`registry.yaml` và `docs/design/project-profile.yaml` đều nằm trong vùng bảo vệ `design`: bật thêm một
pack là đổi cách cả đội làm việc, cần người duyệt.

## Skill vs rule vs subagent

Ba thứ này hay bị lẫn:

| | Là gì | Ở đâu |
|---|---|---|
| **Rule** | Ràng buộc **không được vi phạm**. Luôn áp dụng, CI/lưới canh chặn | `docs/rules/` |
| **Subagent** | Một **vai trò** có góc nhìn và ngữ cảnh riêng (critic, architect) | `.claude/agents/`, `coordination/roles/` |
| **Skill** | Một **thủ tục** nhiều bước, chỉ cần khi đang làm đúng việc đó | `.claude/skills/` |

Nên "NLP" không phải skill (đó là một lĩnh vực). "Đo truy hồi của pipeline RAG trước khi chỉnh prompt"
mới là skill.
