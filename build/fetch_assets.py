"""Re-download every source asset for the UNREAD edit. Nothing is shot; all of it is public
domain / CC on the open web. Run this first, then render_full.py."""
import json, os, subprocess, urllib.parse, sys

DEST = os.environ.get("UNREAD_ASSETS", "./assets")
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/120.0 Safari/537.36")
os.makedirs(f"{DEST}/src", exist_ok=True); os.makedirs(f"{DEST}/wm", exist_ok=True)

def curl(url, out):
    r = subprocess.run(["curl", "-sSL", "--max-time", "120", "-H", f"User-Agent: {UA}",
                        "-o", out, url, "-w", "%{http_code}"], capture_output=True, text=True)
    return r.stdout.strip()

# ---- 1. Voynich Manuscript, Beinecke MS 408, from Yale's IIIF endpoint ----
# Public domain. Native 2793x3761; the server refuses widths above ~2600.
VOYNICH = {"f78r": 1006214, "f71r": 1006202, "f75r": 1006208, "f33v": 1006139}
print("Voynich (Yale IIIF, public domain)")
for folio, oid in VOYNICH.items():
    url = f"https://collections.library.yale.edu/iiif/2/{oid}/full/2600,/0/default.jpg"
    print(f"  {folio:6s} {curl(url, f'{DEST}/src/{folio}_hi.jpg')}")

# To rebuild the folio -> id map for other folios:
#   curl https://collections.library.yale.edu/manifests/2002046
#   then read items[].label and items[].items[].items[].body.service[].@id

# ---- 2. Wikimedia Commons plates ----
COMMONS = {
 "phaistos_a":  "File:Phaistos Disc — Side A.jpg",
 "phaistos_b":  "File:Phaistos Disc — Side B.jpg",
 "roro_champ":  "File:Tablette rongo-rongo - musée Champollion.JPG",
 "lineara_1":   "File:Minoan Linear A, Crete, AMH, 145099.jpg",
 "indus_eleph": "File:Elephant seal of Indus Valley, Indian Museum, Kolkata.jpg",
 "moai_rano":   "File:Moai Rano raraku.jpg",
}
API = "https://commons.wikimedia.org/w/api.php"
print("Wikimedia Commons (see ATTRIBUTION.md for licences)")
for key, title in COMMONS.items():
    # NOTE: batching many titles into one `titles=` call returns empty pages here;
    # query one at a time via the search generator, which is reliable.
    q = urllib.parse.urlencode({"action": "query", "format": "json", "generator": "search",
                                "gsrnamespace": "6", "gsrsearch": title.replace("File:", ""),
                                "gsrlimit": "8", "prop": "imageinfo",
                                "iiprop": "url|size|extmetadata", "iiurlwidth": "2400"})
    try:
        d = json.loads(subprocess.run(["curl", "-sSL", "--max-time", "60", "-H",
                                       f"User-Agent: {UA}", f"{API}?{q}"],
                                      capture_output=True, text=True).stdout)
        pages = d.get("query", {}).get("pages", {})
        hit = next((p for p in pages.values() if p.get("title") == title), None)
        if hit is None:
            print(f"  {key:12s} NOT FOUND — find it by hand on Commons"); continue
        ii = hit["imageinfo"][0]
        code = curl(ii.get("thumburl") or ii["url"], f"{DEST}/wm/{key}.jpg")
        lic = ii.get("extmetadata", {}).get("LicenseShortName", {}).get("value", "?")
        print(f"  {key:12s} {code}  {lic}")
    except Exception as e:
        print(f"  {key:12s} FAILED {e}")

print(f"\nAssets in {DEST}. Point VOY/WM in render_full.py at {DEST}/src and {DEST}/wm.")
