"""Optional browser acceptance against tests/ui_server.py; no model/GPU required.

Run with a separate Playwright installation, never through the ASR test runner.
"""

import argparse
from pathlib import Path

from playwright.sync_api import expect, sync_playwright


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--browser", help="Optional existing Chromium/Brave executable")
    parser.add_argument("--url", default="http://127.0.0.1:8765")
    parser.add_argument("--output", type=Path, default=Path("artifacts/ui"))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            executable_path=args.browser,
            args=[
                "--disable-gpu",
                "--renderer-process-limit=2",
                "--use-fake-device-for-media-stream",
                "--use-fake-ui-for-media-stream",
            ],
        )
        context = browser.new_context(
            viewport={"width": 1440, "height": 1000}, permissions=["microphone"]
        )
        page = context.new_page()
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto(args.url)
        initial_count = len(context.request.get(args.url + "/api/recordings").json())
        expect(page.locator("#startStop")).to_be_enabled()
        page.screenshot(path=str(args.output / "desktop.png"), full_page=True)
        for name, width, height in [("tablet", 768, 1024), ("mobile", 390, 844)]:
            page.set_viewport_size({"width": width, "height": height})
            assert page.evaluate(
                "document.documentElement.scrollWidth <= innerWidth"
            ), name
            page.screenshot(path=str(args.output / f"{name}.png"), full_page=True)
        page.set_viewport_size({"width": 1440, "height": 1000})
        page.locator("#sessionTitle").fill("Tâm lý học · Kết nối ý tưởng")
        page.locator("#saveRecording").check()
        page.locator("#startStop").click()
        expect(page.locator("#sessionStatus")).to_have_text("Đang lắng nghe")
        expect(page.locator(".transcript-line").first).to_be_visible(timeout=10000)
        page.locator("[data-mode=both]").click()
        expect(page.locator(".translation").first).to_be_visible(timeout=10000)
        assert (
            page.locator(".transcript-line").first.locator(".translation").count() == 0
        )
        page.screenshot(path=str(args.output / "live-bilingual.png"), full_page=True)
        page.locator("#startStop").click()
        expect(page.locator("#sessionStatus")).to_have_text(
            "Phiên học đã hoàn tất", timeout=10000
        )
        assert page.evaluate('document.querySelector("#micLevel").value') == 0
        page.locator("#libraryNav").click()
        expect(page.locator(".recording-card")).to_have_count(initial_count + 1)
        page.locator(".recording-card").first.click()
        expect(page.locator("#detailTitle")).to_have_text(
            "Tâm lý học · Kết nối ý tưởng"
        )
        expect(page.locator("#audioPlayer")).to_be_visible()
        page.locator("#detailTranscript .transcript-time").first.click()
        page.wait_for_function(
            '() => document.querySelector("#audioPlayer").readyState >= 2'
        )
        page.screenshot(path=str(args.output / "library.png"), full_page=True)
        for element in ["#downloadAudio", "#downloadTxt", "#downloadJson"]:
            with page.expect_download() as download:
                page.locator(element).click()
            assert download.value.failure() is None
        page.locator("#renameRecording").click()
        page.locator("#editTitle").fill("Bài học đã đổi tên")
        page.locator(
            "#editForm button[type=submit], #editForm button.primary-button"
        ).click()
        expect(page.locator("#detailTitle")).to_have_text("Bài học đã đổi tên")
        page.locator("#mobileSettings").click()
        page.locator("#themeSelect").select_option("dark")
        page.locator("#closeSettings").click()
        page.screenshot(path=str(args.output / "dark-library.png"), full_page=True)
        page.locator("#deleteRecording").click()
        page.locator("#confirmDelete").click()
        expect(page.locator(".recording-card")).to_have_count(initial_count)
        page.locator("#liveNav").click()
        page.locator("#saveRecording").uncheck()
        page.locator("[data-mode=en]").click()
        page.locator("#startStop").click()
        expect(page.locator("#sessionStatus")).to_have_text("Đang lắng nghe")
        expect(page.locator(".transcript-line").first).to_be_visible(timeout=10000)
        page.locator("#startStop").click()
        expect(page.locator("#sessionStatus")).to_have_text("Phiên học đã hoàn tất")
        page.locator("#libraryNav").click()
        expect(page.locator(".recording-card")).to_have_count(initial_count)
        assert not errors, errors
        context.close()
        denied = browser.new_context()
        denied.add_init_script(
            "navigator.mediaDevices.getUserMedia = async () => { throw new DOMException('denied', 'NotAllowedError'); }"
        )
        page = denied.new_page()
        page.goto(args.url)
        page.locator("#startStop").click()
        expect(page.locator("#sessionMessage")).to_contain_text(
            "Microphone chưa được cho phép"
        )
        expect(page.locator("#startStop")).to_be_enabled()
        denied.close()
        browser.close()
    print(
        "Browser acceptance passed: responsive UI, PCM capture, translation switch, stop, library, exports, rename/delete, opt-out, denied microphone; no models or GPU."
    )


if __name__ == "__main__":
    main()
