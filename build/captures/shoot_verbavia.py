import asyncio, os
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/opt/pw-browsers/chromium", proxy={"server": os.environ.get("HTTPS_PROXY","")}, args=["--no-sandbox","--ssl-version-max=tls1.2","--disable-quic"])
        # mobile viewport for phone-frame shots, desktop for wide
        for name, url, w, h, full in [
            ("verbavia_home_m", "https://verbavia.com", 390, 844, False),
            ("verbavia_home_d", "https://verbavia.com", 1440, 900, False),
            ("verbavia_full",   "https://verbavia.com", 390, 844, True),
            ("duo_home_m",      "https://www.duolingo.com", 390, 844, False),
            ("duo_home_d",      "https://www.duolingo.com", 1440, 900, False),
        ]:
            try:
                ctx = await b.new_context(viewport={"width":w,"height":h},
                    user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1" if w<500 else None,
                    device_scale_factor=3 if w<500 else 2)
                pg = await ctx.new_page()
                await pg.goto(url, wait_until="networkidle", timeout=45000)
                await pg.wait_for_timeout(2500)
                await pg.screenshot(path=f"shots/{name}.png", full_page=full)
                print(name, "ok")
                await ctx.close()
            except Exception as e:
                print(name, "FAIL", str(e)[:120])
        await b.close()
asyncio.run(main())
