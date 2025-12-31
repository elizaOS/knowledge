#!/usr/bin/env python3
"""Minimal screenshot utility using Playwright with anti-detection.

Usage:
    python scripts/posters/utils/screenshot.py https://cryptobubbles.net -o bubbles.png
    python scripts/posters/utils/screenshot.py https://dexscreener.com/solana --width 1280 --height 720
    python scripts/posters/utils/screenshot.py URL --full-page
"""

import argparse
import asyncio
from pathlib import Path

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("Error: playwright not installed. Run:")
    print("  pip install playwright")
    print("  playwright install chromium")
    exit(1)

# Realistic Chrome user agent (update periodically)
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/131.0.0.0 Safari/537.36"
)


async def screenshot(
    url: str,
    output: Path,
    width: int = 1920,
    height: int = 1080,
    full_page: bool = False,
    timeout: int = 30000,
) -> bool:
    """Take screenshot of URL with anti-detection measures.

    Args:
        url: URL to screenshot
        output: Output PNG path
        width: Viewport width (default 1920)
        height: Viewport height (default 1080)
        full_page: Capture full scrollable page
        timeout: Navigation timeout in ms

    Returns:
        True if successful
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        # Create context with realistic browser fingerprint
        context = await browser.new_context(
            viewport={"width": width, "height": height},
            user_agent=USER_AGENT,
            locale="en-US",
            timezone_id="America/New_York",
            extra_http_headers={
                "Accept-Language": "en-US,en;q=0.9",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
            },
        )

        page = await context.new_page()

        # Disable webdriver detection flag
        await context.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', { get: () => undefined })"
        )

        try:
            await page.goto(url, wait_until="networkidle", timeout=timeout)
            await page.screenshot(path=str(output), full_page=full_page)
            print(f"Saved: {output}")
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False
        finally:
            await browser.close()


def main():
    parser = argparse.ArgumentParser(
        description="Screenshot a URL with anti-detection",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s https://cryptobubbles.net -o bubbles.png
  %(prog)s https://dexscreener.com/solana --width 1280 --height 720
  %(prog)s https://defillama.com/ --full-page -o defi.png
        """,
    )
    parser.add_argument("url", help="URL to screenshot")
    parser.add_argument(
        "-o", "--output", default="screenshot.png", help="Output path (default: screenshot.png)"
    )
    parser.add_argument("--width", type=int, default=1920, help="Viewport width (default: 1920)")
    parser.add_argument("--height", type=int, default=1080, help="Viewport height (default: 1080)")
    parser.add_argument("--full-page", action="store_true", help="Capture full scrollable page")
    parser.add_argument(
        "--timeout", type=int, default=30000, help="Navigation timeout in ms (default: 30000)"
    )
    args = parser.parse_args()

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    success = asyncio.run(
        screenshot(
            args.url,
            output_path,
            args.width,
            args.height,
            args.full_page,
            args.timeout,
        )
    )
    exit(0 if success else 1)


if __name__ == "__main__":
    main()
