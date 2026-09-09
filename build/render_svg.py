import asyncio, os, sys, re
from playwright.async_api import async_playwright
async def main(src, out, px):
    svg = open(src).read()
    svg = re.sub(r'width="\d+" height="\d+"', 'width="%d" height="%d"' % (px, px), svg, count=1)
    html = ("<body style='margin:0;background:transparent'><div style='width:%dpx;height:%dpx'>%s</div></body>"
            % (px, px, svg))
    open("_r.html", "w").write(html)
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/opt/pw-browsers/chromium",
                                    args=["--no-sandbox","--ssl-version-max=tls1.2","--disable-quic"])
        pg = await (await b.new_context(viewport={"width":px,"height":px}, device_scale_factor=1)).new_page()
        await pg.goto("file://" + os.path.abspath("_r.html"))
        await pg.wait_for_timeout(600)
        await pg.screenshot(path=out, omit_background=True)
        await b.close()
asyncio.run(main(sys.argv[1], sys.argv[2], int(sys.argv[3])))
