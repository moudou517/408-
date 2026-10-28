import os
import tempfile

d = tempfile.mkdtemp(prefix="pip-unpack-", dir=r"E:\CST\408\.tmp")
print("dir:", d)
p = os.path.join(d, "pymupdf-2.0-cp311-abi3-win_amd64.whl")
try:
    with open(p, "wb") as f:
        f.write(b"x" * 1024)
    print("write .whl OK", os.path.getsize(p))
except Exception as e:
    print("write .whl FAILED:", type(e).__name__, e)

p2 = os.path.join(d, "plain.txt")
try:
    with open(p2, "wb") as f:
        f.write(b"y" * 16)
    print("write .txt OK")
except Exception as e:
    print("write .txt FAILED:", type(e).__name__, e)
