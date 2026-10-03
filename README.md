# Agent Project Template

**Mẫu dự án AI Agent để con người chốt thiết kế, còn nhiều AI agent — của nhiều nhà cung cấp khác nhau —
cùng làm một repo mà không giẫm chân nhau và không lệch khỏi thiết kế.**

Stack: FastAPI · SQLAlchemy + Alembic · PostgreSQL · Next.js · Docker · GitHub Actions · Render + Vercel.
Rút ra từ dự án VNutriCare (VMEC-10): 6 tuần, 1.230 commit, nhiều agent (Claude Code, Codex, Gemini CLI,
Cursor, Copilot) cùng làm. Lý do và số đo: `docs/design/adr/0001-multi-agent-control-plane.md`.

---

## Vấn đề template giải quyết

| Ở dự án gốc đã xảy ra | Template chặn bằng |
|---|---|
| Mỗi công cụ AI đọc một file luật khác; luật chép nhiều bản rồi trôi | `AGENTS.md` là nguồn luật duy nhất, adapter chỉ trỏ về — có lưới canh |
| File nhật ký dùng chung bị 203 commit chạm trong 4 tuần | mỗi mục công việc một file (`docs/work/`), mã theo ngày + slug |
| 14 revision Alembic chỉ để gộp head do migration song song | làn độc quyền `db-migrations` + claim nguyên tử + lưới một-head |
| Hai phiên agent cùng một cây làm việc, một bên xoá việc của bên kia | mỗi claim một worktree riêng |
| Agent sửa ngoài phạm vi / tự nới phạm vi | kiểm phạm vi ở hook → pre-commit → CI (công cụ CI chạy từ commit gốc) |
| CI đỏ 6 lần liên tiếp vì kiểm cục bộ khác CI | `scripts/ci_local.py` phản chiếu CI — có lưới canh |
| Commit có test an toàn đỏ vẫn lên production | Render `checksPass` + CI không `needs` + lưới canh cấu trúc CI |
| Thiếu biến môi trường → production chạy khoá JWT công khai, im lặng | cổng cấu hình production đổ lúc khởi động |

## Kiến trúc: năm lớp của mặt phẳng điều phối

```
1. LUẬT          AGENTS.md ◄── CLAUDE.md · GEMINI.md · .github/copilot-instructions.md · .cursor · .aider
2. THIẾT KẾ      docs/design/ (PRD, ARCHITECTURE, ADR, invariants.yaml) · contracts/ (ranh giới lớp, OpenAPI)
3. KẾ HOẠCH      docs/work/tickets/<ID>.md — phạm vi đã duyệt, trên main
4. ĐIỀU PHỐI     tools/agentctl: claim nguyên tử (nhánh agent-claims) · worktree riêng · kiểm phạm vi
5. CƯỠNG CHẾ     hook ghi file ─► pre-commit ─► CI scope-guard + 5 job ─► branch protection ─► deploy chờ CI
```

Nguyên tắc xuyên suốt: **ràng buộc nằm ở chỗ mọi agent bắt buộc đi qua (git, CI), không nằm ở lời dặn.**

## Dùng chung cho mọi dự án, chỉnh theo từng dự án

Đây là template chung — **miền nghiệp vụ không cứng trong khung**, chỉ hai trục điều chỉnh khi khởi tạo:

| Trục | Không đổi khi bạn chỉnh | Đổi khi bạn chỉnh |
|---|---|---|
| **Miền dự án** — thay `src/domain/catalog/` bằng nghiệp vụ thật, viết bất biến thật vào `docs/design/invariants.yaml`, xoá `EXM-01.md` | năm lớp mặt phẳng điều phối (§Kiến trúc), ranh giới lớp (`contracts/boundaries.yaml`), CI/deploy | `docs/design/PRD.md`, `src/domain/`, `docs/rules/10-domain-safety.md`, bất biến miền |
| **Team-size × complexity** — `python scripts/generate_team_docs.py --team-size ... --complexity ...` | claim/worktree/kiểm phạm vi (chạy y hệt dù 1 hay 20 người) | số vai trò, ai sở hữu vùng nào (`docs/GOVERNANCE.md`, `.github/CODEOWNERS`, chủ vùng trong `coordination/policy.yaml`), số người duyệt, mức bắt buộc ADR |

Bốn team-size (`solo` 1 người · `small` 2 · `standard` 4, mặc định · `large` 6+ có vai trò bảo mật riêng)
× ba complexity (`lite` POC · `standard` mặc định · `strict` dữ liệu nhạy cảm, thêm đồng duyệt bảo mật)
— hai trục **độc lập nhau**, chi tiết và ví dụ: `docs/design/presets/README.md`. `docs/GOVERNANCE.md` và
`.github/CODEOWNERS` là **sinh ra** từ lựa chọn đó (`docs/design/team-profile.yaml`), có lưới canh giữ
đồng bộ — không có nguy cơ "quên cập nhật CODEOWNERS sau khi đổi số người".

## Bắt đầu một dự án mới

```bash
# 1. Lấy template — trên GitHub bấm "Use this template", hoặc:
python -m venv .venv && . .venv/bin/activate      # Windows: .venv\Scripts\activate
python scripts/bootstrap.py --name "Tên Dự Án" --slug ten-du-an          # chạy thử
python scripts/bootstrap.py --name "Tên Dự Án" --slug ten-du-an --apply  # ghi thật + in việc người phải làm

# 2. Chọn hình dạng đội — bao nhiêu người thật, mức nghi thức (bỏ qua = mặc định standard/standard)
python scripts/generate_team_docs.py --team-size solo --complexity lite
# team-size:  solo (1) · small (2) · standard (4, mặc định) · large (6+, thêm vai trò bảo mật)
# complexity: lite (POC) · standard (mặc định) · strict (dữ liệu nhạy cảm — thêm đồng duyệt bảo mật)

# 3. Môi trường + git hooks dùng chung
make setup                     # hoặc: pip install -r requirements-dev.txt && git config core.hooksPath scripts/githooks
cp .env.example .env

# 4. Chạy
alembic upgrade head
make run                       # API http://127.0.0.1:8000/docs
(cd web && npm ci && npm run dev)   # Web http://localhost:3000

# 5. Xác nhận mọi thứ xanh như CI
python scripts/ci_local.py
```

Toàn bộ bằng Docker: `docker compose up --build`.

## Một vòng làm việc với nhiều agent

```bash
# Người lập kế hoạch (người hoặc agent planner) đề xuất ticket; người duyệt đổi state: ready qua PR.
python -m tools.agentctl new ticket --id API-02 --title "Thêm endpoint X" --role R1

# Mỗi agent (bất kỳ nhà cung cấp nào), thay mặt một vai trò:
python -m tools.agentctl board                     # ai đang làm gì, ticket nào ready
python -m tools.agentctl start API-02 --role R3    # từ chối nếu phạm vi chồng người khác
cd .worktrees/API-02
# ... test trước, code, make check-fast, commit "feat(api): ... (API-02)"
python scripts/ci_local.py && python -m tools.agentctl check-scope
git push -u origin HEAD && gh pr create --draft
python -m tools.agentctl release API-02            # sau khi merge
```

Vai trò agent trung lập nhà cung cấp: `coordination/roles/` (planner · critic · architect · implementer · reviewer).

## Công cụ AI nào đọc gì

| Công cụ | Luật | Chặn ghi sai phạm vi ngay lúc ghi |
|---|---|---|
| Codex CLI | `AGENTS.md` | có (`.codex/hooks.json`) |
| Claude Code | `CLAUDE.md` → `@AGENTS.md` | có (`.claude/settings.json`) |
| Gemini CLI | `.gemini/settings.json` → `AGENTS.md` | có (`BeforeTool`) |
| GitHub Copilot, Cursor, Aider, Windsurf, Zed, Jules | `AGENTS.md` (+ adapter) | không — bị chặn ở pre-commit và CI |

## Bản đồ thư mục

| Đường dẫn | Là gì | Ai sở hữu |
|---|---|---|
| `AGENTS.md` | luật cho mọi agent | người (vùng bảo vệ) |
| `docs/design/` | PRD, kiến trúc, ADR, bất biến, `team-profile.yaml` + preset team-size/complexity | người (vùng bảo vệ) |
| `docs/rules/` | luật theo lĩnh vực (00 cốt lõi → 80 lưới canh) | người (vùng bảo vệ) |
| `docs/work/` | ticket, nhật ký, quyết định, câu hỏi, sự cố — mỗi mục một file | ticket: người duyệt; còn lại: ai cũng thêm |
| `coordination/` | chính sách điều phối, vai trò agent | người (vùng bảo vệ) |
| `contracts/` | ranh giới lớp, bản chụp OpenAPI | thiết kế / làn độc quyền |
| `tools/agentctl/` | công cụ điều phối (claim, phạm vi, bảng việc) | người (vùng bảo vệ) |
| `src/` | backend: core · domain (tất định) · db · llm · agents · api | theo `docs/GOVERNANCE.md` |
| `tests/guards/` | lưới canh — thiết kế dạng chạy được | thêm được; sửa cần duyệt |
| `tests/tools/`, `tests/unit/` | test công cụ điều phối, test ứng dụng | theo module |
| `web/` | frontend Next.js | R4 |
| `scripts/` | CI cục bộ, hook, khởi tạo, kiểm migration | R3 / R1 |

## Giới hạn — nói thật

- Không phải ranh giới bảo mật trước một agent CỐ Ý phá: agent có token đủ quyền vẫn gắn được nhãn duyệt. Chốt thật
  là branch protection + CODEOWNERS + agent dùng tài khoản không có quyền duyệt (`docs/GOVERNANCE.md` §2).
- ⚠️ **"Chốt thật là branch protection" có điều kiện tiên quyết:** repo **private** trên GitHub **Free** không bật được
  branch protection lẫn rulesets — API trả `403 Upgrade to GitHub Pro or make this repository public` (đo 17/09/2026
  trên chính repo template này). Khi đó GitHub **không chặn gì cả**: đẩy thẳng `main` được, merge khi CI còn đỏ
  được. Lớp còn lại chỉ là hook ghi file (không thấy lệnh shell — `cp`/`sed` qua mặt được), git hook cục bộ (bỏ được)
  và CI. Chọn một: nâng gói có bảo vệ nhánh · chuyển repo public · hoặc chấp nhận và **coi CI xanh là điều kiện
  merge bắt buộc bằng kỷ luật**, ghi rõ trong `docs/GOVERNANCE.md` của dự án.
- ⚠️ **CI đỏ vì thanh toán trông giống hệt CI đỏ vì mã** — cả hai đều hiện dấu ✗. Job đỏ trong 2–3 giây và danh sách
  bước rỗng thì đọc annotation trước khi đọc code: *"job was not started because recent account payments have failed
  or your spending limit needs to be increased"* nghĩa là hạ tầng. Repo template này đã đỏ 6/6 lượt như vậy từ commit
  đầu tiên mà không ai hay, vì đẩy thẳng `main` của repo private không có ai theo dõi. Runner tự host (biến repo
  `CI_RUNNER`, xem `docs/DEPLOY.md`) không tốn phút GitHub.
- Claim cần kết nối tới git remote. Mất mạng thì chỉ `status`/`board --offline` dùng được.
- Kiểm chồng phạm vi cố ý bảo thủ: đôi khi từ chối oan hai mẫu thật ra rời nhau — giải bằng scope hẹp hơn.
- Miền mẫu (`src/domain/catalog`, `src/agents/quote_agent.py`) chỉ để minh hoạ hình mẫu; thay bằng miền thật.

## Kiểm chứng template này

```bash
python -m pytest -q          # unit + lưới canh + công cụ điều phối (claim chạy trên git thật)
python scripts/ci_local.py   # đủ bước như CI
```
