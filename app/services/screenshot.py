# app/services/screenshot.py

import asyncio
from playwright.async_api import async_playwright
import logging

logger = logging.getLogger(__name__)

async def wait_for_panel_to_render(page, panel_id, max_wait_seconds=60):
    """
    Polls every second (up to `max_wait_seconds`) until the embeddable
    panel's `data-render-complete` attribute is 'true'.
    """
    panel_selector = f"#{panel_id} div[data-test-subj='embeddablePanel']"
    panel_locator = page.locator(panel_selector)

    for _ in range(max_wait_seconds):
        count = await panel_locator.count()
        if count == 0:
            await asyncio.sleep(1)
            continue

        render_complete = await panel_locator.get_attribute("data-render-complete")
        if render_complete == "true":
            await asyncio.sleep(2)  # small buffer
            return

        await asyncio.sleep(1)

    raise TimeoutError(f"Panel {panel_id} did not finish rendering in {max_wait_seconds} seconds.")

async def screenshot_panel(kibana_url, username, password, dashboard_id, panel_identifier, screenshot_path):
    dashboard_url = f"{kibana_url}/app/dashboards#/view/{dashboard_id}"
    panel_selector = f"[id='panel-{panel_identifier}']"

    logger.info(f"Dashboard URL: {dashboard_url}")
    logger.info(f"Panel selector: {panel_selector}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # 1. Login
        await page.goto(kibana_url)
        locator = page.locator('[data-test-subj="loginForm"]')
        await locator.wait_for(state='visible')
        await page.fill('[data-test-subj="loginUsername"]', username)
        await page.fill('[data-test-subj="loginPassword"]', password)
        await page.click('[data-test-subj="loginSubmit"]')
        await page.wait_for_url(f'{kibana_url}/app/home')

        # 2. Open dashboard
        dashboard_page = await context.new_page()
        await dashboard_page.goto(dashboard_url)

        # 3. Wait for the panel
        try:
            await dashboard_page.locator(panel_selector).wait_for()
        except:
            logger.error(f"Could not find panel with selector {panel_selector}.")
            await browser.close()
            return

        # 4. Wait for complete render
        panel_id = f"panel-{panel_identifier}"
        try:
            await wait_for_panel_to_render(dashboard_page, panel_id)
            logger.info("Panel is fully rendered!")
        except TimeoutError as e:
            logger.error(str(e))
            await browser.close()
            return

        # 5. Remove toast notifications if present
        await dashboard_page.evaluate("""
            () => {
                const toastList = document.querySelector("[data-test-subj='globalToastList']");
                if (toastList) {
                    toastList.remove();
                }
            }
        """)

        # 6. Screenshot the panel
        panel_element = await dashboard_page.query_selector(panel_selector)
        if not panel_element:
            logger.error(f"No panel found using selector: {panel_selector}")
            await browser.close()
            return

        await panel_element.screenshot(path=screenshot_path)
        logger.info(f"Screenshot saved to: {screenshot_path}")

        await browser.close()

def take_panel_screenshot(kibana_url, username, password, dashboard_id, panel_identifier, screenshot_path):
    """Synchronous wrapper for the asynchronous screenshot_panel function."""
    try:
        asyncio.run(
            screenshot_panel(kibana_url, username, password, dashboard_id, panel_identifier, screenshot_path)
        )
    except Exception as e:
        logger.error(f"Failed to take screenshot: {e}")
