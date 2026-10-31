from playwright.sync_api import sync_playwright

URL = "https://worldinfo.streamlit.app/"  # change this

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(URL, wait_until="domcontentloaded", timeout=120_000)
    page.wait_for_timeout(5000)
    btn = page.get_by_role("button", name="Yes, get this app back up!")
    if btn.count() > 0:
        print("App was asleep, waking it up...")
        btn.click()
        page.wait_for_timeout(60_000)
    else:
        print("App is already awake.")
    browser.close()
