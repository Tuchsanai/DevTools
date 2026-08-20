#!/usr/bin/env python3
"""บันทึก walkthrough ของ Swagger UI สำหรับ LAB 2 ที่ viewport 1440x900."""

from __future__ import annotations

import json
import os
from pathlib import Path

from playwright.sync_api import Locator, Page, sync_playwright


PROJECT = Path(__file__).resolve().parents[2]
RAW = PROJECT / "tools/ui/raw"
BASE_URL = os.environ.get("LAB2_BASE_URL", "http://localhost:8252")
VIEWPORT = {"width": 1440, "height": 900}
TICKET = {
    "asset_id": 12,
    "title": "ลำโพงห้องเรียน 402 เสียงขาดหาย",
    "detail": "เปิดแล้วเสียงดังบ้างหายบ้าง",
    "priority": "HIGH",
}


def visible(page: Page, target: Locator, top_padding: int = 150) -> None:
    target.evaluate("element => element.scrollIntoView({block: 'center', inline: 'nearest'})")
    page.evaluate("padding => window.scrollBy(0, -padding)", top_padding)
    page.wait_for_timeout(250)


def box(target: Locator) -> list[int]:
    bounds = target.bounding_box()
    if bounds is None:
        raise RuntimeError("ไม่พบพิกัดของ element ที่ต้องใส่ marker")
    return [
        round(bounds["x"]),
        round(bounds["y"]),
        round(bounds["x"] + bounds["width"]),
        round(bounds["y"] + bounds["height"]),
    ]


def capture(page: Page, name: str, targets: dict[str, Locator]) -> None:
    path = RAW / name
    page.screenshot(path=str(path), full_page=False)
    print(json.dumps({"image": name, **{key: box(value) for key, value in targets.items()}}, ensure_ascii=False))


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport=VIEWPORT, device_scale_factor=1)

        dashboard = page.request.get(f"{BASE_URL}/api/dashboard")
        dashboard_data = dashboard.json()
        expected = {
            "tickets": {"NEW": 3, "ASSIGNED": 2, "IN_PROGRESS": 1, "DONE": 2},
            "overdue_ids": [4, 1],
            "loans_active": 2,
            "parts_low_ids": [1, 4],
        }
        actual = {
            "tickets": dashboard_data["tickets"],
            "overdue_ids": [item["id"] for item in dashboard_data["overdue"]],
            "loans_active": dashboard_data["loans_active"],
            "parts_low_ids": [item["id"] for item in dashboard_data["parts_low"]],
        }
        if actual != expected:
            raise RuntimeError(f"ฐานข้อมูลไม่ใช่ seed: คาด {expected} แต่ได้ {actual}")

        page.goto(f"{BASE_URL}/docs", wait_until="networkidle")
        page.locator(".opblock-summary").first.wait_for(state="visible")
        page.evaluate("window.scrollTo(0, 0)")
        capture(
            page,
            "ui-swagger-01-docs.png",
            {"docs": page.locator(".information-container")},
        )

        dashboard_block = page.locator("#operations-default-dashboard_api_dashboard_get")
        dashboard_summary = dashboard_block.locator(".opblock-summary")
        visible(page, dashboard_summary, 180)
        dashboard_summary.click()
        page.wait_for_timeout(250)
        visible(page, dashboard_summary, 100)
        capture(page, "ui-swagger-02-dashboard.png", {"summary": dashboard_summary})

        dashboard_try = dashboard_block.get_by_role("button", name="Try it out")
        visible(page, dashboard_try, 240)
        capture(page, "ui-swagger-03-try-dashboard.png", {"try": dashboard_try})
        dashboard_try.click()

        dashboard_execute = dashboard_block.get_by_role("button", name="Execute")
        visible(page, dashboard_execute, 240)
        with page.expect_response(lambda response: response.url.endswith("/api/dashboard")) as response_info:
            dashboard_execute.click()
        if response_info.value.status != 200:
            raise RuntimeError(f"GET /api/dashboard ได้ HTTP {response_info.value.status}")
        visible(page, dashboard_execute, 240)
        capture(page, "ui-swagger-04-execute-dashboard.png", {"execute": dashboard_execute})

        response_code = dashboard_block.locator(".response-col_status").filter(has_text="200").last
        response_body = dashboard_block.locator(".response-col_description pre").first
        visible(page, response_body, 80)
        capture(
            page,
            "ui-swagger-05-dashboard-200.png",
            {"code": response_code, "body": response_body},
        )

        ticket_block = page.locator("#operations-default-create_ticket_api_tickets_post")
        ticket_summary = ticket_block.locator(".opblock-summary")
        visible(page, ticket_summary, 220)
        ticket_summary.click()
        page.wait_for_timeout(250)
        visible(page, ticket_summary, 100)
        capture(page, "ui-swagger-06-post-ticket.png", {"summary": ticket_summary})

        ticket_try = ticket_block.get_by_role("button", name="Try it out")
        visible(page, ticket_try, 220)
        capture(page, "ui-swagger-07-try-ticket.png", {"try": ticket_try})
        ticket_try.click()

        request_body = ticket_block.locator("textarea")
        request_body.fill(json.dumps(TICKET, ensure_ascii=False, indent=2))
        visible(page, request_body, 180)
        capture(page, "ui-swagger-08-request-body.png", {"body": request_body})

        ticket_execute = ticket_block.get_by_role("button", name="Execute")
        with page.expect_response(
            lambda response: response.url.endswith("/api/tickets") and response.request.method == "POST"
        ) as response_info:
            ticket_execute.click()
        created_response = response_info.value
        created = created_response.json()
        if created_response.status != 201 or created.get("id") != 9 or created.get("status") != "NEW":
            raise RuntimeError(
                f"POST /api/tickets ไม่ตรงผลคงที่: HTTP {created_response.status}, body={created}"
            )
        response_code = ticket_block.locator(".response-col_status").filter(has_text="201").last
        response_body = ticket_block.locator(".response-col_description pre").first
        page.evaluate("document.body.style.zoom = '0.75'")
        ticket_execute.evaluate(
            "element => window.scrollTo(0, window.scrollY + element.getBoundingClientRect().top - 90)"
        )
        page.wait_for_timeout(250)
        capture(
            page,
            "ui-swagger-09-created.png",
            {"execute": ticket_execute, "code": response_code, "body": response_body},
        )
        browser.close()


if __name__ == "__main__":
    main()
