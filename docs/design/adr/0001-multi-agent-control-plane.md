# ADR-0001: Mặt phẳng điều phối trong repo cho nhiều AI agent khác nhà cung cấp

- Status: Accepted — quyết định nền của template; dự án mới xác nhận lại ở buổi khởi động
- Date: 2026-09-15
- Owner: R1 — Architecture Owner
- Reviewers: R2, R3, R4
- Supersedes: N/A

## Bối cảnh

Template này rút từ VNutriCare (VMEC-10): 6 tuần, 4 người, nhiều AI agent của nhiều nhà cung cấp cùng làm
một repo (có hook ghi log cho Claude Code, Codex, Gemini CLI, Cursor, Copilot). Số đo từ lịch sử git và nhật
ký của dự án đó:

| Quan sát | Số đo | Lớp vấn đề |
|---|---|---|
| File nhật ký dùng chung `DEVLOG.md` (1,2 MB) | bị 203 commit chạm trong 20/08–15/09/2026 | điểm nóng nối-cuối-file |
| File ticket dùng chung `TICKETS.md`, bảng Excel theo dõi việc | 44 và 45 commit cùng giai đoạn; Excel không merge được | trạng thái ghi tay dùng chung |
| File model một khối `models.py`; migration song song | 38 commit; 14 revision Alembic chỉ để gộp head | tài nguyên tuần tự bị làm song song |
| Chỉ có `CLAUDE.md` ở gốc | Codex đọc `AGENTS.md`, Gemini CLI mặc định đọc `GEMINI.md` — không nạp luật của dự án | luật không tới mọi agent |
| Cảnh báo "chưa có nguồn" rơi khi chép từ nhật ký sang `CLAUDE.md` | 09/09/2026 | luật bị chép thành nhiều bản rồi trôi |
| Phiên agent song song trên CÙNG cây làm việc | 15/08/2026 `git checkout --` xoá việc chưa commit của phiên kia | không cách ly không gian làm việc |
| Kiểm cục bộ khác CI | CI đỏ 6 lần liên tiếp 05–06/09/2026, mỗi lần một lỗi khác | hai bản logic kiểm |
| Deploy không chờ CI | commit `a4c694e2` có test cổng duyệt ĐỎ vẫn lên production (13/09/2026) | cổng an toàn không nối vào deploy |

Không lỗi nào ở trên là lỗi khó. Tất cả có chung một gốc: **ràng buộc nằm ở lời dặn, không nằm ở chỗ mọi
agent bắt buộc phải đi qua.** Agent khác nhà cung cấp đọc file khác nhau, nhớ khác nhau, không chia sẻ trí
nhớ — nên lời dặn không phải là cơ chế phối hợp.

## Tiêu chí quyết định

1. Chạy được với MỌI agent có quyền đọc/ghi git — không phụ thuộc nhà cung cấp, IDE hay git host.
2. Con người giữ quyền quyết thiết kế và kế hoạch; agent không tự nới được phạm vi của mình.
3. Xung đột được NGĂN trước khi code được viết, không chỉ phát hiện lúc merge.
4. Mỗi ràng buộc quan trọng được kiểm bằng máy và có bằng chứng từng đỏ.
5. Không thêm dịch vụ phải vận hành.

## Phương án đã cân nhắc

### A. Một file hướng dẫn + tin agent tự giác (hiện trạng VNutriCare)

Rẻ nhất. Thất bại ở tiêu chí 1, 3, 4 — chính là các số đo trong bảng Bối cảnh.

### B. Chép luật vào file riêng của từng công cụ

Mọi agent đọc được luật, nhưng N bản luật trôi khỏi nhau (đã quan sát được). Không giải quyết xung đột.

### C. Điều phối bằng GitHub Issues/Projects + nhãn

Có giao diện sẵn. Nhưng phụ thuộc một git host và token API trong môi trường agent; không có khái niệm
"phạm vi file" nên không phát hiện hai việc chạm cùng file; gán issue không nguyên tử với việc bắt đầu làm.

### D. Mặt phẳng điều phối trong repo (chọn)

1. **Một nguồn luật:** `AGENTS.md` (chuẩn chung được phần lớn công cụ tự đọc) + adapter mỏng chỉ trỏ về nó;
   lưới canh cấm adapter chứa luật riêng.
2. **Kế hoạch là dữ liệu có phạm vi:** ticket một-file có `scope.allow`, làn độc quyền, vùng bảo vệ duyệt
   trước; chỉ ticket `ready` trên `main` mới claim được, và mọi phân xử đọc ticket từ `main`.
3. **Sổ claim nguyên tử trên nhánh git mồ côi:** `git push` từ chối lần ghi không fast-forward, nên hai agent
   claim cùng lúc thì đúng một người thắng. Không dịch vụ ngoài, không token API.
4. **Cách ly:** mỗi claim một worktree + nhánh không track `main`.
5. **Một hàm kiểm phạm vi dùng ở ba lớp:** hook ghi file (Claude Code/Codex/Gemini) → pre-commit (mọi agent) →
   CI. Trên CI, công cụ chạy từ commit GỐC để PR không tự sửa được bộ kiểm.
6. **Triệt tiêu điểm nóng:** mục công việc một-file-một-mục, mã theo ngày+slug; router/model tự khám phá;
   settings theo miền; trạng thái suy ra, không ghi tay.
7. **Bất biến là test:** `docs/design/invariants.yaml` trỏ tới lưới canh thật; lưới canh tự kiểm chính nó.

## Quyết định

Chọn **D**. Xem lại nếu: một nền tảng cung cấp khoá file/phạm vi nguyên tử độc lập nhà cung cấp; hoặc đội
dưới 2 người và không dùng quá một agent cùng lúc (khi đó phần claim là thừa, phần luật và lưới canh vẫn giữ).

## Hệ quả

- Tích cực: xung đột chặn ở lúc claim thay vì lúc merge; mọi agent gặp cùng luật ở cùng chỗ; người duyệt
  thấy mọi thay đổi thiết kế trong diff; bảng công việc không lệch sự thật.
- Đánh đổi: lập kế hoạch tốn công hơn (phải viết phạm vi); claim cần mạng tới remote; phạm vi viết hẹp quá
  thì agent phải hỏi thêm — cái giá chọn có chủ đích.
- Giới hạn trung thực: nhãn duyệt không phải ranh giới bảo mật nếu agent có quyền gắn nhãn; hook chặn chỉ có ở
  công cụ hỗ trợ — luật thật nằm ở CI và branch protection.

## Kiểm chứng

`tests/tools/` (claim trên git thật, kể cả ghi đồng thời; kiểm phạm vi đọc từ gốc; hook ba công cụ) và
`tests/guards/` (một nguồn luật, ranh giới lớp, migration, hợp đồng API, deploy chờ CI). Mỗi cơ chế chính đã
được phá thử (force-push thay CAS, bỏ kiểm chồng, đọc ticket từ cây cục bộ, bỏ `--no-track`...) và test tương
ứng đỏ.

## Rút lui

Mọi thành phần độc lập: bỏ claim vẫn giữ được luật một nguồn và lưới canh; bỏ hook vẫn còn pre-commit và CI.
Dữ liệu (ticket, nhật ký, quyết định) là Markdown thường, không khoá vào công cụ nào.
