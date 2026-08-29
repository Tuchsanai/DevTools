const { test, expect } = require("@playwright/test");

const baseURL = process.env.LAB_BASE_URL || "http://localhost:3000";

async function markAndCapture(page, step, label, locators, output) {
  for (const locator of locators) await locator.scrollIntoViewIfNeeded();

  const boxes = [];
  for (const locator of locators) {
    const box = await locator.boundingBox();
    if (!box) throw new Error(`ไม่พบขอบเขต element สำหรับภาพ ${step}`);
    boxes.push(box);
  }

  await page.evaluate(
    ({ boxes, step, label }) => {
      document.querySelectorAll("[data-lab-marker]").forEach((node) => node.remove());
      const layer = document.createElement("div");
      layer.dataset.labMarker = "layer";
      Object.assign(layer.style, {
        position: "fixed",
        inset: "0",
        zIndex: "2147483647",
        pointerEvents: "none",
      });

      boxes.forEach((box) => {
        const frame = document.createElement("div");
        Object.assign(frame.style, {
          position: "absolute",
          left: `${Math.max(4, box.x - 5)}px`,
          top: `${Math.max(4, box.y - 5)}px`,
          width: `${Math.min(innerWidth - box.x - 8, box.width + 10)}px`,
          height: `${Math.min(innerHeight - box.y - 8, box.height + 10)}px`,
          border: "4px solid #ef3340",
          borderRadius: "10px",
          boxShadow: "0 0 0 3px rgba(255,255,255,.92), 0 12px 28px rgba(15,23,42,.32)",
        });
        layer.appendChild(frame);
      });

      const first = boxes[0];
      const badge = document.createElement("div");
      badge.textContent = `${step} ${label}`;
      const badgeTop = first.y > 62 ? first.y - 54 : first.y + first.height + 16;
      Object.assign(badge.style, {
        position: "absolute",
        left: `${Math.min(Math.max(16, first.x), innerWidth - 360)}px`,
        top: `${Math.min(Math.max(12, badgeTop), innerHeight - 54)}px`,
        padding: "9px 14px",
        color: "#fff",
        background: "#111827",
        borderLeft: "8px solid #ef3340",
        borderRadius: "7px",
        boxShadow: "0 8px 24px rgba(15,23,42,.34)",
        font: "700 21px/1.2 system-ui, sans-serif",
        whiteSpace: "nowrap",
      });
      layer.appendChild(badge);
      document.body.appendChild(layer);
    },
    { boxes, step, label },
  );

  await page.screenshot({ path: output, animations: "disabled" });
}

test("บันทึก walkthrough Web UI ครบ 10 ขั้น", async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.goto(baseURL, { waitUntil: "networkidle" });

  const overviewLink = page.locator('aside nav a[href="/"]');
  await expect(overviewLink).toBeVisible();
  await markAndCapture(page, "①", "เปิดหน้าสรุป", [overviewLink], "../images/ui-web-01-overview.png");

  const ticketsLink = page.locator('aside nav a[href="/tickets"]');
  await ticketsLink.click();
  await page.waitForLoadState("networkidle");
  await markAndCapture(page, "②", "กระดานงานซ่อม", [ticketsLink], "../images/ui-web-02-tickets.png");

  const asset = page.locator("#asset_id");
  await asset.selectOption({ label: "A-003 · กล้อง Sony ZV-1" });
  await markAndCapture(page, "③", "เลือกครุภัณฑ์", [asset], "../images/ui-web-03-asset.png");

  const title = page.locator("#title");
  const detail = page.locator("#detail");
  await title.fill("กล้องถ่ายวิดีโอเปิดไม่ติด");
  await detail.fill("กดปุ่มเปิดแล้วไฟสถานะไม่ทำงาน");
  await markAndCapture(page, "④", "กรอกหัวข้อและรายละเอียด", [title, detail], "../images/ui-web-04-details.png");

  const priority = page.locator("#priority");
  await priority.selectOption("HIGH");
  await markAndCapture(page, "⑤", "เลือกเร่งด่วน", [priority], "../images/ui-web-05-priority.png");

  const createButton = page.getByRole("button", { name: "แจ้งซ่อม", exact: true });
  await markAndCapture(page, "⑥", "กดแจ้งซ่อม", [createButton], "../images/ui-web-06-submit.png");
  await createButton.click();
  await page.waitForLoadState("networkidle");

  const newColumn = page.locator("section").filter({ has: page.getByRole("heading", { name: "รอรับเรื่อง" }) });
  const newCard = newColumn.locator("article").filter({ hasText: "กล้องถ่ายวิดีโอเปิดไม่ติด" });
  await expect(newCard).toContainText("#9");
  await markAndCapture(page, "⑦", "จำนวน 4 และการ์ดใหม่", [newColumn], "../images/ui-web-07-new-card.png");

  const assignee = page.getByLabel("ชื่อช่างสำหรับใบ #9");
  await assignee.fill("TECH-04");
  await markAndCapture(page, "⑧", "กรอกชื่อช่าง", [assignee], "../images/ui-web-08-assignee.png");

  const assignButton = newCard.getByRole("button", { name: "มอบหมาย", exact: true });
  await markAndCapture(page, "⑨", "กดมอบหมาย", [assignButton], "../images/ui-web-09-assign.png");
  await assignButton.click();
  await page.waitForLoadState("networkidle");

  const assignedColumn = page.locator("section").filter({ has: page.getByRole("heading", { name: "มอบหมายแล้ว" }) });
  const assignedCard = assignedColumn.locator("article").filter({ hasText: "กล้องถ่ายวิดีโอเปิดไม่ติด" });
  await expect(assignedCard).toContainText("TECH-04");
  await markAndCapture(page, "⑩", "สถานะและการ์ดย้ายแล้ว", [assignedColumn], "../images/ui-web-10-assigned.png");
});
