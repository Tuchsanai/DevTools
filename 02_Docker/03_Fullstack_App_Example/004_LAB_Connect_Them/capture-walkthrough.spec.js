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
        <div style="position:fixed;left:${box.x - 5}px;top:${box.y - 5}px;width:${box.width + 10}px;height:${box.height + 10}px;border:3px solid #ef3340;border-radius:11px;box-sizing:border-box;box-shadow:0 0 0 3px #fff"></div>
        <div style="position:fixed;left:${Math.max(8, box.x - 16)}px;top:${Math.max(8, box.y - 16)}px;width:34px;height:34px;display:grid;place-items:center;background:#ef3340;color:#fff;border:3px solid #fff;border-radius:999px;font:800 18px/1 Tahoma,sans-serif;box-shadow:0 4px 12px #0f172a48">${step}</div>
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
  await page.setViewportSize({ width: 1920, height: 1080 });
  await capture(page, "/", "สรุปภาพรวม", "①", "คลิกสรุปภาพรวม", "ui-net-01-overview.png");
  await capture(page, "/", "กระดานงานซ่อม", "②", "คลิกกระดานงานซ่อม", "ui-net-02-tickets.png");
  await capture(page, "/tickets", "ยืม-คืนครุภัณฑ์", "③", "คลิกยืม-คืนครุภัณฑ์", "ui-net-03-loans.png");
  await capture(page, "/loans", "คลังอะไหล่", "④", "คลิกคลังอะไหล่", "ui-net-04-parts.png");
  await capture(page, "/parts", "สรุปภาพรวม", "⑤", "กลับหน้าสรุปภาพรวม", "ui-net-05-back.png");
});
