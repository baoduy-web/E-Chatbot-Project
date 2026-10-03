# AGENTS.md — Luật chung cho MỌI AI agent làm việc trên repo này

> Tự đọc bởi Codex, Cursor, GitHub Copilot, Gemini CLI (`.gemini/settings.json`), Aider (`.aider.conf.yml`),
> Windsurf, Zed, Jules…; Claude Code đọc qua `CLAUDE.md` (dòng `@AGENTS.md`).
> **Đây là nguồn luật DUY NHẤT cho agent.** File riêng của từng công cụ chỉ trỏ về đây, không thêm luật —
> có lưới canh ép điều đó (`tests/guards/test_agent_instructions.py`).
> Bạn không phải người quyết định thiết kế. Bạn làm việc **thay mặt một vai trò con người** (R1–R4,
> `docs/GOVERNANCE.md`) trong phạm vi họ đã duyệt, và người đó chịu trách nhiệm cho thứ bạn merge.

## 0. Dự án

**Agent Project Template** — mô tả sản phẩm trong 3 dòng khi khởi tạo dự án thật.
Phạm vi và không-mục-tiêu: `docs/design/PRD.md`. Kiến trúc: `docs/design/ARCHITECTURE.md`.

## 1. Đọc trước khi làm — theo thứ tự

1. File này, toàn bộ.
2. Ticket được giao `docs/work/tickets/<ID>.md` và MỌI file trong `design_refs` của nó.
3. `docs/design/invariants.yaml` — bất biến không được vi phạm.
4. Luật lĩnh vực trong `docs/rules/` (bảng ở §8).
5. `coordination/README.md` nếu đây là lần đầu bạn làm trên repo này.
6. **Bạn có thể là người nối tiếp, không phải người bắt đầu.** Chạy `git log --oneline -10`, `git status` và
   `python -m tools.agentctl board` — mục "bàn giao đang chờ người nhận" liệt kê `docs/work/handoffs/`
   chưa ai nhận. Có bàn giao cho việc của bạn thì đọc nó, đổi `status: taken`, làm tiếp từ "Còn dở".

## 2. Tám luật tối cao

1. **Thiết kế do người chốt là luật.** `docs/design/`, `contracts/boundaries.yaml`, `docs/rules/` chỉ
   đổi qua PR có người duyệt. Thấy thiết kế sai hay thiếu: đề xuất (câu hỏi hoặc ADR `Proposed`), không tự sửa.
2. **Một ticket · một claim · một nhánh · một worktree.** Bắt đầu bằng
   `python -m tools.agentctl start <ID> --role <Rn>`. Không làm trong checkout chính, không làm trong
   worktree của agent khác, không làm ticket chưa `ready` trên `main`.
3. **Chỉ sửa trong phạm vi ticket** (`scope.allow` + làn/vùng ticket khai). Cần thêm file: dừng phần đó,
   mở câu hỏi, làm tiếp phần còn lại. Không "tiện tay" refactor, đổi tên, dọn dẹp ngoài phạm vi.
4. **Không đoán — hỏi.** Ngưỡng nghiệp vụ, nguồn số liệu, hành vi thiết kế không nói tới, mâu thuẫn giữa
   tài liệu: tạo `python -m tools.agentctl new question ...` và dừng đúng phần bị chặn.
5. **Lưới canh là luật.** Không sửa, nới, xoá, `skip` hay `xfail` test trong `tests/guards/` để CI xanh.
   Không `continue-on-error`, không bật retry để che test đỏ. Thêm lưới mới thì luôn được.
6. **Bằng chứng thắng tự khai.** "Xong" = lệnh đã chạy + kết quả. Test mới phải được thấy ĐỎ trước khi
   có code (hoặc khi gỡ bản vá), rồi mới xanh. Test chưa từng đỏ không chứng minh gì.
7. **Không bí mật, không dữ liệu định danh** trong code, commit, log, prompt gửi mô hình, hay file cấu hình
   được commit (`.mcp.json` chỉ dùng `${TEN_BIEN}`). Lỡ lộ: báo người, thu hồi khoá trước, xoá sau.
8. **Git an toàn.** Cấm `push --force`, `--no-verify`, đẩy thẳng `main`, `alembic stamp` để chữa head.
   Không `git stash` / `checkout --` / `reset --hard` khi có tiến trình khác đang chạy trong cùng cây.
   Merge bằng nút Merge của nền tảng (tạo commit mới), không fast-forward tay vào `main`.

## 3. Bất biến đỏ — tóm tắt (nguồn đầy đủ: `docs/design/invariants.yaml`)

| Mã | Bất biến | Nếu vi phạm |
|---|---|---|
| INV-001 | Agent không sửa vùng người sở hữu khi chưa có người duyệt | thiết kế bị đổi lặng lẽ |
| INV-002 | Không hai claim còn hạn chồng phạm vi hay giữ cùng làn độc quyền | xung đột merge, nhiều head migration |
| INV-004 | `src/domain` không import LLM/web/ORM; SDK LLM chỉ ở `src/llm` | con số đi qua mô hình ngôn ngữ |
| INV-005 | Mô hình ngôn ngữ chỉ CHỌN (id, số lượng); mọi con số do code tính và có nguồn | số sai không test nào bắt được |
| INV-006 | Hành động rủi ro cao cần vai trò người duyệt; hành động chưa khai coi là rủi ro cao | nội dung chưa duyệt tới người dùng |
| INV-008 | Schema chỉ đổi qua migration; đồ thị migration đúng một head | production đổ khi deploy |
| INV-010 | Deploy chỉ sau khi mọi check CI qua | commit đỏ lên production |

### Bất biến miền — dự án điền

Thêm vào `docs/design/invariants.yaml` (vùng bảo vệ), tóm tắt ở đây. Ví dụ từ dự án gốc VNutriCare (dinh
dưỡng lâm sàng): *LLM chỉ chọn món + gram, Python tính mọi chỉ số bằng SQL* · *không con số nào không có
nguồn* · *thực đơn chưa được chuyên gia duyệt không bao giờ tới bệnh nhân*. Luật miền: `docs/rules/10-domain-safety.md`.

## 4. Làm một ticket

```bash
python -m tools.agentctl board                        # xem ticket ready, ai đang giữ gì
python -m tools.agentctl start ABC-01 --role R3       # claim nguyên tử + worktree .worktrees/ABC-01
cd .worktrees/ABC-01                                  # MỌI thao tác của phiên diễn ra ở đây
# viết test trước → thấy đỏ → viết code → thấy xanh
make check-fast                                       # hoặc: python scripts/ci_local.py --fast
git commit -m "feat(api): mô tả ngắn (ABC-01)"         # hook kiểm phạm vi + thông điệp
python scripts/ci_local.py                            # đủ bước như CI, trước khi mở PR
python -m tools.agentctl check-scope                  # phạm vi so với ticket trên origin/main
git push -u origin HEAD && gh pr create --draft       # PR nháp; xong thì "Ready for review"
python -m tools.agentctl release ABC-01               # sau khi merge (hoặc khi bỏ việc)
```

Làm lâu hơn lease (mặc định 24 giờ): `python -m tools.agentctl renew`. Dừng giữa chừng: ghi bàn giao (§9).

## 5. Khi nào DỪNG

Dừng phần việc liên quan, mở câu hỏi, và báo người khi:

- Cần sửa file ngoài phạm vi, vùng bảo vệ, hoặc làn độc quyền ticket không khai.
- Cần một con số nghiệp vụ (ngưỡng, hệ số, giá, liều…) mà không có nguồn trong repo.
- Tài liệu mâu thuẫn nhau hoặc mâu thuẫn code (xem thứ bậc §10) — không tự chọn bên.
- Lưới canh đỏ và cách làm xanh là nới lưới.
- Yêu cầu của người mâu thuẫn một bất biến: **nói thẳng là không nên và vì sao**, đừng lặng lẽ làm theo.

## 6. Ranh giới kiến trúc — tóm tắt (nguồn: `contracts/boundaries.yaml`)

```
api ──► agents ──► llm (cửa ngõ duy nhất tới mô hình; SDK nhà cung cấp chỉ ở đây)
 │        └──────► domain (TẤT ĐỊNH: tính mọi con số, có nguồn; không I/O)
 └──► db ─────────► domain
core: cấu hình + cổng production, không phụ thuộc lớp nào
```

- Thêm endpoint = thêm file trong `src/api/routes/` (tự khám phá). Thêm bảng = thêm module trong
  `src/db/models/` (tự khám phá) + migration trong làn `db-migrations`. Không sửa file đăng ký tập trung.
- Cấu hình mới: lớp settings của đúng miền, cập nhật `.env.example` trong cùng PR.
- Dữ liệu ngoài vào prompt phải qua `sanitize_untrusted` + `fence`; văn bản ra mô hình qua `assert_no_egress`.

## 7. Lệnh hay dùng

| Việc | Lệnh |
|---|---|
| Cài môi trường + git hooks | `make setup` |
| Kiểm nhanh trước commit | `make check-fast` |
| Chạy đúng như CI | `python scripts/ci_local.py` |
| Chỉ chạy lưới canh | `python -m pytest tests/guards tests/tools -q` |
| Cập nhật hợp đồng API | `python scripts/export_openapi.py` |
| Tạo migration | `alembic revision --autogenerate -m "..."` rồi ĐỌC LẠI file sinh ra |
| Nhật ký / quyết định / sự cố | `python -m tools.agentctl new log\|decision\|incident --role Rn --title "..."` |
| Bàn giao khi dừng giữa chừng | `python -m tools.agentctl new handoff --role Rn --title "..."` |

## 8. Bản đồ repo

| Cần gì | Ở đâu |
|---|---|
| Phạm vi sản phẩm | `docs/design/PRD.md` |
| Kiến trúc, luồng, dữ liệu | `docs/design/ARCHITECTURE.md` · ADR: `docs/design/adr/` |
| Luật cốt lõi / miền / backend / frontend / dữ liệu | `docs/rules/00-core.md` · `10-domain-safety.md` · `20-backend.md` · `30-frontend.md` · `40-data.md` |
| Quy trình, CI, deploy | `docs/rules/50-workflow.md` · `docs/DEPLOY.md` |
| Bảo mật agent sản phẩm | `docs/rules/60-agent-security.md` |
| Điều phối nhiều agent | `docs/rules/70-multi-agent-coordination.md` · `coordination/` |
| Cách viết lưới canh | `docs/rules/80-guard-nets.md` |
| Vai trò agent (planner/critic/architect/implementer/reviewer/supervisor) | `coordination/roles/` |
| Ai quyết gì, bao nhiêu vai trò | `docs/GOVERNANCE.md` (sinh ra từ `docs/design/team-profile.yaml`, xem `docs/design/presets/README.md`) |
| Ticket, nhật ký, câu hỏi, sự cố | `docs/work/` |
| Frontend | `web/` (luật riêng: `web/AGENTS.md`) |

## 9. Báo cáo cuối phiên và bàn giao

Kết thúc mỗi phiên bằng một mục nhật ký (`new log`) và báo cáo có đủ:

1. **Đã làm** — file nào, vì sao (trỏ ticket).
2. **Bằng chứng** — lệnh đã chạy và kết quả rút gọn; test nào đã thấy đỏ trước.
3. **Chưa làm / còn dở** — nói thật; không báo "xong" khi còn dở.
4. **Câu hỏi mở và quyết định cần người** — đường dẫn file câu hỏi.
5. **Bàn giao** — trạng thái nhánh/claim, lệnh để agent kế tiếp (có thể khác nhà cung cấp) tiếp tục.
   Dừng giữa chừng (hết hạn mức, hết phiên) thì **commit phần đã chạy được và xanh test**, rồi chạy
   `python -m tools.agentctl new handoff --role Rn --title "..."`: git được điền sẵn (nhánh, commit cuối, file
   chưa commit, commit chưa đẩy); bạn chỉ cần thêm mục "Còn dở".

Không ghi tên công cụ hay mô hình AI làm tác giả trong commit/PR/nhật ký nếu `docs/GOVERNANCE.md` của
dự án không yêu cầu — tác giả là vai trò con người mà bạn làm thay.

## 10. Khi tài liệu mâu thuẫn — thứ bậc

`docs/design/invariants.yaml` và ADR `Accepted` > `docs/design/*` > `AGENTS.md` > `docs/rules/*` >
ticket > comment trong code. Tài liệu cao hơn thắng — nhưng mâu thuẫn là lỗi: mở câu hỏi để người sửa
tài liệu thấp hơn, đừng lặng lẽ theo bên nào.
