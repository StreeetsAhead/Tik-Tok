import asyncio, os
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/opt/pw-browsers/chromium",
            proxy={"server": os.environ.get("HTTPS_PROXY","")},
            args=["--no-sandbox","--ssl-version-max=tls1.2","--disable-quic"])
        for name,url,w,h,full,wait in [
            ("duo_home_m","https://www.duolingo.com",390,844,False,6000),
            ("duo_home_d","https://www.duolingo.com",1440,900,False,6000),
            ("duo_full_m","https://www.duolingo.com",390,844,True,6000),
        ]:
            try:
                ctx=await b.new_context(viewport={"width":w,"height":h},
                    device_scale_factor=3 if w<500 else 2)
                pg=await ctx.new_page()
                await pg.goto(url, wait_until="domcontentloaded", timeout=90000)
                await pg.wait_for_timeout(wait)
                await pg.screenshot(path=f"shots/{name}.png", full_page=full)
                print(name,"ok"); await ctx.close()
            except Exception as e: print(name,"FAIL",str(e)[:100])
        await b.close()
asyncio.run(main())
