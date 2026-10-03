# RULE 40 — Dữ liệu

> Owner: **R2**.

## R40.1 — Dữ liệu có cấu trúc dùng truy vấn chính xác; văn bản dùng truy hồi

Con số nghiệp vụ tra bằng SQL theo khoá, không qua tìm kiếm ngữ nghĩa (sai số của truy hồi không được chảy vào
con số). Tìm kiếm vector chỉ cho văn bản phi cấu trúc — và mọi đoạn truy hồi vào prompt là dữ liệu KHÔNG tin cậy.

## R40.2 — Không dòng dữ liệu nào thiếu nguồn

Mỗi dòng: `source` (cơ quan/bộ dữ liệu), `source_ref` (bảng/trang/mã cụ thể — người khác kiểm lại được), và cờ
`is_estimated` + độ tin cậy khi là ước tính. Script kiểm dữ liệu chặn dòng thiếu nguồn ở CI.

## R40.3 — Dữ liệu mới phải làm sạch trước khi dùng

Chuẩn hoá mã hoá (UTF-8, không BOM), đơn vị, khoảng trắng, danh mục viết nhiều kiểu (`rau` / `rau củ`), khoá
trùng. Không giả định file mới "đã sẵn sàng". Sửa dữ liệu seed ⇒ chạy script kiểm dữ liệu trước khi commit.

## R40.4 — Lọc theo hai lưới khi trường phân loại không đáng tin

Trường nhập tay (danh mục, loại) thường trống hoặc lệch cách viết. Phân nhóm dựa trên nó thì kiểm thêm lưới thứ
hai (từ khoá trong tên) — lưới đơn đã sót dòng thật ở VNutriCare.

## R40.5 — Ước tính phải trung thực

Không làm tròn độ tin cậy lên, không ẩn nhãn ước tính cho gọn. Một con số ước tính được trình bày như đo thật là
vi phạm R40.2.

## R40.6 — Kiểm chứng số liệu trước khi công bố

Mọi số liệu trong tài liệu, slide, giao diện: có nguồn sơ cấp truy được. Không tìm thấy nguồn ⇒ xoá số đó,
không giữ "cho đẹp". Nguồn thứ cấp (blog phổ biến kiến thức) phải ghi rõ là thứ cấp.

## R40.7 — Bản quyền và giấy phép

Ghi giấy phép của từng bộ dữ liệu. PDF/tài liệu gốc có bản quyền không vào git — chỉ bản trích dẫn/đã chuẩn hoá
được phép.

## R40.8 — Dữ liệu cá nhân

Dữ liệu người thật chỉ dùng đúng mục đích đã cam kết, đã khử định danh khi dùng cho phát triển; mã định danh gốc
không vào prompt, log hay tên file. Sao lưu CSDL chứa dữ liệu người dùng không vào git.

## R40.9 — Phiên bản hoá dữ liệu

Bản dữ liệu dùng ở production có mã phát hành và người ký duyệt; production từ chối dữ liệu chưa ký nếu dự án
bật cơ chế này. Thay đổi dữ liệu dùng chung là hành động HIGH.
