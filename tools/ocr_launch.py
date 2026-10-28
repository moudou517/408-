"""Spawn one OCR worker process per garbled PDF (file-redirected stdio, no pipes)."""

import os
import subprocess
import sys
import time

ROOT = r"E:\CST\408"
PY = sys.executable
WORKER = os.path.join(ROOT, "tools", "ocr_worker.py")
LOGDIR = os.path.join(ROOT, "work", "logs")
os.makedirs(LOGDIR, exist_ok=True)

YEARS = sys.argv[1:] or ["2009", "2010", "2013", "2015", "2016", "2018", "2023"]

env = dict(os.environ)
env["PYTHONPATH"] = os.path.join(ROOT, ".pylibs")
env["PYTHONWARNINGS"] = "ignore"
env["PYTHONIOENCODING"] = "utf-8"
env["TEMP"] = os.path.join(ROOT, ".tmp")
env["TMP"] = os.path.join(ROOT, ".tmp")
env["OMP_NUM_THREADS"] = "3"
env["ORT_NUM_THREADS"] = "3"
env["OPENBLAS_NUM_THREADS"] = "3"

procs = []
for y in YEARS:
    log = open(os.path.join(LOGDIR, f"ocr_{y}.log"), "w", encoding="utf-8")
    p = subprocess.Popen(
        [PY, WORKER, y],
        stdout=log,
        stderr=subprocess.STDOUT,
        env=env,
        cwd=ROOT,
        creationflags=getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0),
    )
    procs.append((y, p, log))
    print(f"spawned {y} pid={p.pid}", flush=True)

t0 = time.time()
pending = {y: p for y, p, _ in procs}
while pending:
    time.sleep(10)
    for y in list(pending):
        rc = pending[y].poll()
        if rc is not None:
            print(f"[{y}] exited rc={rc} after {time.time()-t0:.0f}s", flush=True)
            del pending[y]
            # tail its log
            lp = os.path.join(LOGDIR, f"ocr_{y}.log")
            tail = open(lp, encoding="utf-8", errors="replace").read().strip().splitlines()[-3:]
            for t in tail:
                print(f"    {y}| {t}", flush=True)

for _, _, log in procs:
    log.close()
print("ALL DONE", flush=True)
