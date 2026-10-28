import re
import ssl
import sys
import urllib.request

MIRRORS = [
    "https://pypi.tuna.tsinghua.edu.cn/simple/pymupdf/",
    "https://mirrors.aliyun.com/pypi/simple/pymupdf/",
    "https://pypi.org/simple/pymupdf/",
]

for url in MIRRORS:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "pip/24"})
        with urllib.request.urlopen(req, timeout=45) as r:
            data = r.read().decode("utf-8", "replace")
        hrefs = re.findall(r'href="([^"]+)"', data)
        win = [h for h in hrefs if "win_amd64" in h]
        print(f"OK   {url}  bytes={len(data)}  whl_links={len(hrefs)}  win_amd64={len(win)}")
        for h in win[-3:]:
            print("     ", h.split("#")[0])
        break
    except Exception as e:
        print(f"FAIL {url}  {type(e).__name__}: {e}")

print("\n--- ssl default verify paths ---")
try:
    import certifi

    print("certifi:", certifi.where())
except Exception as e:
    print("no certifi:", e)
print("default_verify_paths:", ssl.get_default_verify_paths())
print("python:", sys.version)
