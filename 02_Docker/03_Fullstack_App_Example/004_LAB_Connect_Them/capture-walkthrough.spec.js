const { test, expect } = require("@playwright/test");
const path = require("path");

const baseURL = process.env.LAB004_URL || "http://localhost:8254";
const imageDir = path.join(__dirname, "images");

async function addMarker(page, label, step, caption) {
  const target = page.getByRole("link", { name: new RegExp(`^${label}`) }).first();
  await expect(target).toBeVisible();
  const box = await target.boundingBox();
  if (!box) throw new Error(`ไม่พบตำแหน่งของเมนู ${label}`);

  await page.evaluate(
    ({ box, step, caption }) => {
      document.getElementById("lab004-marker")?.remove();
      const marker = document.createElement("div");
      marker.id = "lab004-marker";
      marker.setAttribute("aria-hidden", "true");
      marker.innerHTML = `
        <div style="position:fixed;left:${box.x - 6}px;top:${box.y - 6}px;width:${box.width + 12}px;height:${box.height + 12}px;border:5px solid #ef174b;border-radius:13px;box-sizing:border-box"></div>
        <div style="position:fixed;left:${box.x + box.width + 24}px;top:${box.y + box.height / 2 - 24}px;background:#182238;color:#fff;padding:10px 16px;border-radius:9px;font:24px/1.2 Tahoma,sans-serif;white-space:nowrap;box-shadow:0 2px 8px #0004">${step} ${caption}</div>
        <div style="position:fixed;left:${box.x + box.width - 8}px;top:${box.y + box.height / 2 - 2}px;width:36px;height:4px;background:#ef174b;transform:rotate(-8deg);transform-origin:left center"></div>
      `;
      marker.style.cssText = "position:fixed;inset:0;z-index:2147483647;pointer-events:none";
      document.body.appendChild(marker);
    },
    { box, step, caption }
  );
}

async function capture(page, route, menu, step, caption, filename) {
  await page.goto(`${baseURL}${route}`, { waitUntil: "networkidle" });
  const target = page.getByRole("link", { name: new RegExp(`^${menu}`) }).first();
  await target.click();
  await page.waitForLoadState("networkidle");
  await addMarker(page, menu, step, caption);
  await page.screenshot({ path: path.join(imageDir, filename), fullPage: false });
}

test("บันทึก UI walkthrough พร้อม Marker", async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 900 });
  await capture(page, "/", "สรุปภาพรวม", "①", "คลิกสรุปภาพรวม", "ui-net-01-overview.png");
  await capture(page, "/", "กระดานงานซ่อม", "②", "คลิกกระดานงานซ่อม", "ui-net-02-tickets.png");
  await capture(page, "/tickets", "ยืม-คืนครุภัณฑ์", "③", "คลิกยืม-คืนครุภัณฑ์", "ui-net-03-loans.png");
  await capture(page, "/loans", "คลังอะไหล่", "④", "คลิกคลังอะไหล่", "ui-net-04-parts.png");
  await capture(page, "/parts", "สรุปภาพรวม", "⑤", "กลับหน้าสรุปภาพรวม", "ui-net-05-back.png");
});
