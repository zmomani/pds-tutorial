"""
Execute every lesson's code in CPython, mirroring what the browser does:

* each ```python run block runs in a fresh namespace (must not raise);
* each exercise: starter + check must FAIL (otherwise the check is vacuous),
  reference solution + check must PASS.

Run from the repository root:  python tests/run_lessons.py
"""
from __future__ import annotations

import io
import json
import os
import re
import sys
import traceback
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
from solutions import SOLUTIONS  # noqa: E402

os.chdir(ROOT)  # lessons refer to data/… relative to the site root

try:
    import matplotlib
    matplotlib.use("agg")
except ImportError:
    pass

EX_RE = re.compile(r"^:::exercise\s+([^\n]*)\n([\s\S]*?)^:::\s*$", re.M)
FENCE_RE = re.compile(r"```python\s*(check)?\s*\n([\s\S]*?)```")
RUN_RE = re.compile(r"```python run\s*\n([\s\S]*?)```")


import signal


class Timeout(Exception):
    pass


def _alarm(*_):
    raise Timeout("block ran for more than 60 s")


signal.signal(signal.SIGALRM, _alarm)


def run(code: str) -> tuple[bool, str]:
    ns: dict = {}
    buf = io.StringIO()
    signal.alarm(60)
    try:
        with redirect_stdout(buf), redirect_stderr(buf):
            exec(compile(code, "<lesson>", "exec"), ns)
        return True, buf.getvalue()
    except Exception:
        return False, buf.getvalue() + traceback.format_exc()
    finally:
        signal.alarm(0)


def main() -> int:
    manifest = json.loads((ROOT / "lessons" / "manifest.json").read_text())
    failures = 0
    for lesson in manifest:
        md = (ROOT / "lessons" / lesson["file"]).read_text(encoding="utf-8")
        exercises = []
        body = EX_RE.sub(lambda m: (exercises.append(m), "")[1], md)

        n_run = 0
        for m in RUN_RE.finditer(body):
            n_run += 1
            ok, out = run(m.group(1))
            if not ok:
                failures += 1
                print(f"✗ {lesson['id']} example #{n_run} FAILED\n{out}")

        n_ex = 0
        for m in exercises:
            n_ex += 1
            header, ex_body = m.group(1), m.group(2)
            ex_id = re.search(r"id=([\w-]+)", header).group(1)
            starter = check = ""
            for f in FENCE_RE.finditer(ex_body):
                if f.group(1):
                    check = f.group(2)
                else:
                    starter = f.group(2)
            key = f"{lesson['id']}/{ex_id}"
            if not check:
                failures += 1
                print(f"✗ {key}: no check block")
                continue
            ok, _ = run(starter + "\n" + check)
            if ok:
                failures += 1
                print(f"✗ {key}: the untouched starter already passes the check (vacuous test)")
            sol = SOLUTIONS.get(key)
            if sol is None:
                failures += 1
                print(f"✗ {key}: no reference solution")
                continue
            ok, out = run(sol + "\n" + check)
            if not ok:
                failures += 1
                print(f"✗ {key}: reference solution FAILED the check\n{out}")

        print(f"✓ {lesson['id']:12s} {n_run:2d} examples, {n_ex} exercises")
    print("\nALL GOOD" if not failures else f"\n{failures} problem(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
