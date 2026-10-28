"""Download a PyPI wheel from the Tsinghua mirror and extract it into a target dir.

Needed because pip's own temp-dir handling is blocked in this sandbox.
"""

import os
import re
import sys
import urllib.request
import zipfile

MIRROR = "https://pypi.tuna.tsinghua.edu.cn/simple"
TARGET = r"E:\CST\408\.pylibs"
DLDIR = r"E:\CST\408\.tmp\dl"


def index_links(pkg):
    url = f"{MIRROR}/{pkg}/"
    req = urllib.request.Request(url, headers={"User-Agent": "pip/24"})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read().decode("utf-8", "replace")
    base = f"{MIRROR}/{pkg}/"
    out = []
    for h in re.findall(r'href="([^"]+)"', data):
        h = h.split("#")[0]
        if not h.endswith(".whl"):
            continue
        if not h.startswith("http"):
            h = urllib.parse.urljoin(base, h)
        out.append(h)
    return out


def pick(links, want_tags):
    """Return the last link whose filename contains all want_tags."""
    cands = [l for l in links if all(t in l.rsplit("/", 1)[-1] for t in want_tags)]
    return cands[-1] if cands else None


def fetch(url, dest):
    print(f"  GET {url}")
    req = urllib.request.Request(url, headers={"User-Agent": "pip/24"})
    with urllib.request.urlopen(req, timeout=300) as r, open(dest, "wb") as f:
        while True:
            chunk = r.read(1 << 20)
            if not chunk:
                break
            f.write(chunk)
    return os.path.getsize(dest)


def install(wheel_path, target):
    os.makedirs(target, exist_ok=True)
    with zipfile.ZipFile(wheel_path) as z:
        z.extractall(target)
    return len(z.namelist())


def main():
    os.makedirs(DLDIR, exist_ok=True)
    os.makedirs(TARGET, exist_ok=True)
    import urllib.parse  # noqa: F401  (used by index_links)

    for pkg, tags in [
        ("pymupdf", ["win_amd64", "cp311-abi3"]),
        ("pypdf", ["py3-none-any"]),
    ]:
        try:
            links = index_links(pkg)
            url = pick(links, tags)
            if not url:
                url = pick(links, tags[1:]) or (links[-1] if links else None)
            if not url:
                print(f"{pkg}: no wheel found")
                continue
            name = url.rsplit("/", 1)[-1]
            dest = os.path.join(DLDIR, name)
            if not os.path.exists(dest):
                size = fetch(url, dest)
                print(f"    {name}  {size/1e6:.1f} MB")
            n = install(dest, TARGET)
            print(f"  {pkg}: extracted {n} members -> {TARGET}")
        except Exception as e:
            print(f"{pkg}: FAILED {type(e).__name__}: {e}")
    print("done")


if __name__ == "__main__":
    main()
