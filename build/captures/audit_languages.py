import asyncio, os, json
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path="/opt/pw-browsers/chromium",
            proxy={"server": os.environ.get("HTTPS_PROXY","")},
            args=["--no-sandbox","--ssl-version-max=tls1.2","--disable-quic"])
        pg=await (await b.new_context(viewport={"width":1440,"height":1200})).new_page()
        await pg.goto("https://verbavia.com", wait_until="domcontentloaded", timeout=90000)
        await pg.wait_for_timeout(3500)
        info = await pg.evaluate("""() => {
          const out={badge:null, cards:[], other:[]};
          const b=document.querySelector('.hero-badge,[class*=badge]');
          if(b) out.badge=b.textContent.trim();
          document.querySelectorAll('.language-card').forEach(e=>{
            out.cards.push({name:(e.textContent||'').trim().split('\\n')[0],
                            tag:e.tagName, href:e.getAttribute('href')||null,
                            cls:e.className, disabled:e.getAttribute('aria-disabled')});
          });
          document.querySelectorAll('*').forEach(e=>{
            const t=(e.textContent||'').trim();
            if(/soon|coming|planned|waitlist|progress/i.test(t) && t.length<90 && e.children.length===0)
               out.other.push(t);
          });
          out.other=[...new Set(out.other)].slice(0,12);
          return out;}""")
        print("badge:", info["badge"])
        print("live .language-card count:", len(info["cards"]))
        for c in info["cards"]: print("   ", c["name"], "| href:", c["href"])
        print("soon/coming mentions:", info["other"])
        await b.close()
asyncio.run(main())
