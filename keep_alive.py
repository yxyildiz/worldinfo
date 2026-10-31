
from playwright.sync_api import sync_playwright

URLS = [
    "https://worldinfo.streamlit.app/",
    "https://vpnstar.streamlit.app/",
]

failed = []

with sync_playwright() as p:
    browser = p.chromium.launch()

    for url in URLS:
        page = browser.new_page()
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=120_000)
            page.wait_for_timeout(5000)

            btn = page.get_by_role("button", name="Yes, get this app back up!")
            if btn.count() > 0:
                print(f"WAKE  {url} (was asleep, waking up)")
                btn.click()
                page.wait_for_timeout(60_000)
            else:
                print(f"OK    {url} (already awake)")
        except Exception as e:
            print(f"ERROR {url}: {e}")
            failed.append(url)
        finally:
            page.close()

    browser.close()

if failed:
    print(f"\nFailed: {failed}")
    raise SystemExit(1)
