"""OCR years with a bounded pool of 4 subprocesses (avoid thread thrashing)."""

import os
import subprocess
import sys
import time

ROOT = r"E:\CST\408"
PY = sys.executable
WORKER = os.path.join(ROOT, "tools", "ocr_worker.py")
LOGDIR = os.path.join(ROOT, "work", "logs")
os.makedirs(LOGDIR, exist_ok=True)

MAXW = int(os.environ.get("OCR_WORKERS", "4"))
YEARS = sys.argv[1:] or ["2009", "2010", "2013", "2015", "2016", "2018", "2023",
                         "2012", "2017", "2019", "2020", "2021", "2022"]

env = dict(os.environ)
env["PYTHONPATH"] = os.path.join(ROOT, ".pylibs")
env["PYTHONWARNINGS"] = "ignore"
env["PYTHONIOENCODING"] = "utf-8"
env["TEMP"] = os.path.join(ROOT, ".tmp")
env["TMP"] = os.path.join(ROOT, ".tmp")

queue = list(YEARS)
running = {}
done = []
t0 = time.time()

while queue or running:
    while queue and len(running) < MAXW:
        y = queue.pop(0)
        log = open(os.path.join(LOGDIR, f"p_{y}.log"), "w", encoding="utf-8")
        p = subprocess.Popen([PY, WORKER, y], stdout=log, stderr=subprocess.STDOUT,
                             env=env, cwd=ROOT)
        running[y] = (p, log)
        print(f"[{time.time()-t0:6.0f}s] start {y} (pid {p.pid})", flush=True)
    time.sleep(5)
    for y in list(running):
        p, log = running[y]
        if p.poll() is not None:
            log.close()
            print(f"[{time.time()-t0:6.0f}s] done  {y} rc={p.returncode}", flush=True)
            done.append(y)
            del running[y]

print(f"ALL DONE in {time.time()-t0:.0f}s: {done}", flush=True)
