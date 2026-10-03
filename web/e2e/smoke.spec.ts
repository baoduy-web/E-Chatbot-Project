import { expect, test } from "@playwright/test";

// Chờ TRẠNG THÁI THẬT từ API, không đếm phần tử ngay sau `goto`: lúc React còn đang tải, "không có phần tử lỗi"
// luôn đúng — một khẳng định rỗng đã từng làm dự án gốc tin nhầm một luồng an toàn đang chạy (04/09/2026).
test("trang chủ hiển thị trạng thái máy chủ lấy từ API thật", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByTestId("health-status")).toContainText("ok", { timeout: 30_000 });
});
