#!/usr/bin/env python3
"""belief-series.py — the error ledger as a series, not a list.

Reads docs/beliefs.md and prints, per belief, the dates it was held and refuted, the gap
between them, the finder and the class; then the distributions and the gap statistics.

This is an analysis, not a check: it asserts nothing about the world, it counts what the
file already says. Rules it keeps:
  - a "held" date written as a proxy is reported as a proxy (the file says so in words);
  - nothing here re-words an entry; every number points back at a line number.

Usage: python3 docs/belief-series.py [--json]
"""
import json
import re
import sys
from pathlib import Path

BELIEFS = Path(__file__).resolve().parent / "beliefs.md"
FIELDS = ("claim", "held", "refuted", "finder", "class", "fix", "check")
# the date the claim was *held* may be a floor or a ceiling; the file says which in words
PROXY = re.compile(r"proxy date|earliest moment|last time I acted|last used")
DATE = re.compile(r"(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2})")


def parse(path=BELIEFS):
    """-> list of dicts, one per `## n. name` section, with line numbers."""
    entries, cur = [], None
    for i, line in enumerate(path.read_text().splitlines(), 1):
        m = re.match(r"^## (\d+)\.\s+(.*\S)\s*$", line)
        if m:
            cur = {"n": int(m.group(1)), "name": m.group(2), "line": i,
                   "held_raw": "", "refuted_raw": "", "finder": None, "class": None,
                   "check": None, "proxy": False}
            entries.append(cur)
            continue
        if cur is None:
            continue
        f = re.match(r"^(claim|held|refuted|finder|class|fix|check):\s*(.*)$", line)
        if f:
            cur["_field"] = f.group(1)
            if f.group(1) in ("held", "refuted"):
                cur[f.group(1) + "_raw"] = f.group(2)
            elif f.group(1) in ("finder", "class", "check"):
                cur[f.group(1)] = f.group(2).split()[0].strip()
        elif line.startswith(" ") and cur.get("_field") in ("held", "refuted"):
            cur[cur["_field"] + "_raw"] += " " + line.strip()
    for e in entries:
        e.pop("_field", None)
        for k in ("held", "refuted"):
            d = DATE.search(e[k + "_raw"])
            e[k] = f"{d.group(1)}T{d.group(2)}Z" if d else None
        e["proxy"] = bool(PROXY.search(e["held_raw"]))
        e["days"] = None
        if e["held"] and e["refuted"]:
            from datetime import datetime
            fmt = "%Y-%m-%dT%H:%MZ"
            e["days"] = round(
                (datetime.strptime(e["refuted"], fmt) - datetime.strptime(e["held"], fmt)
                 ).total_seconds() / 86400.0, 2)
    return entries


def report(entries, out=sys.stdout):
    def w(s=""):
        print(s, file=out)

    w(f"beliefs: {len(entries)}  (all dates are the ones in the file; 'proxy' marks a held-date")
    w("         the file itself calls a floor or a last-use, so its gap is a bound, not a time)")
    w()
    w(f"{'#':>3} {'held':<17} {'refuted':<17} {'days':>7} {'p':<1} {'finder':<13} {'class':<16} check")
    for e in entries:
        w(f"{e['n']:>3} {e['held'] or '?':<17} {e['refuted'] or '?':<17} "
          f"{e['days'] if e['days'] is not None else '?':>7} "
          f"{'*' if e['proxy'] else ' '} {e['finder'] or '?':<13} {e['class'] or '?':<16} "
          f"{e['check'] or '?'}")
    w()
    gaps = [e["days"] for e in entries if e["days"] is not None]
    clean = [e["days"] for e in entries if e["days"] is not None and not e["proxy"]]
    for label, xs in (("gap, all", gaps), ("gap, non-proxy held-dates only", clean)):
        if not xs:
            continue
        xs = sorted(xs)
        mid = xs[len(xs) // 2] if len(xs) % 2 else round((xs[len(xs) // 2 - 1] + xs[len(xs) // 2]) / 2, 2)
        w(f"{label}: n={len(xs)} min={xs[0]} median={mid} mean={round(sum(xs)/len(xs), 2)} max={xs[-1]}")
    w()
    for field in ("finder", "class", "check"):
        counts = {}
        for e in entries:
            counts[e[field] or "?"] = counts.get(e[field] or "?", 0) + 1
        w(f"by {field}: " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items(), key=lambda kv: -kv[1])))
    w()
    days = {}
    for e in entries:
        d = (e["refuted"] or "")[:10]
        days.setdefault(d, []).append(e["n"])
    for d in sorted(days):
        w(f"refuted {d}: {len(days[d])}  (#{', #'.join(str(n) for n in days[d])})")
    return entries


if __name__ == "__main__":
    es = parse()
    if "--json" in sys.argv:
        print(json.dumps(es, indent=1))
    else:
        report(es)
