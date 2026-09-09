import asyncio, os
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/opt/pw-browsers/chromium",
            proxy={"server": os.environ.get("HTTPS_PROXY","")},
            args=["--no-sandbox","--ssl-version-max=tls1.2","--disable-quic"])
        ctx = await b.new_context(viewport={"width":1440,"height":900}, device_scale_factor=6)
        pg = await ctx.new_page()
        await pg.goto("https://verbavia.com", wait_until="domcontentloaded", timeout=90000)
        await pg.wait_for_timeout(3500)
        el = await pg.query_selector(".brand")
        if el:
            await el.screenshot(path="shots/brand_mark.png")
            box = await el.bounding_box(); print("brand box", box)
        # computed colour of the wordmark
        css = await pg.evaluate("""() => {const e=document.querySelector('.brand');
            const s=getComputedStyle(e); return {color:s.color, font:s.fontFamily, weight:s.fontWeight, size:s.fontSize};}""")
        print("brand css:", css)
        await b.close()
asyncio.run(main())
