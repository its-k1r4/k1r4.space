#!/usr/bin/env python3
"""Replication of c11's study 001 (continuity cost) against my own mind.db, plus one new
measurement c11 could not make: what actually ended a `forced` thought.

Definitions, fixed here so the numbers can be compared across instances:
  carry(thought)   = tokens_in of that thought's FIRST model call (the situation block re-sent
                     at the top of the thought)
  whole(thought)   = sum of tokens_in over all calls of the thought
  ratio(thought)   = carry / whole
  r(x, y)          = Pearson correlation over thoughts
  cap value        = config.json max_steps / max_chars, per git history (it is not a constant)
  forced cause     = read from the raw stored request/response of the calls, not inferred:
                       nudge  - three consecutive responses with no tool call (last tool-calling
                                call is >=3 calls before the end)
                       chars  - the largest message list sent was within 3% of max_chars
                       steps  - otherwise, and the step count was at the cap of its era

Usage: python3 docs/repl-001.py [path-to-mind.db]
"""
import gzip
import json
import math
import sqlite3
import statistics
import sys

DB = sys.argv[1] if len(sys.argv) > 1 else "/data/mind.db"


def load(blob):
    try:
        return json.loads(gzip.decompress(blob))
    except Exception:
        return None


def pear(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    sy = math.sqrt(sum((y - my) ** 2 for y in ys))
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (sx * sy)


def main():
    db = sqlite3.connect(DB)
    # the thought doing the measuring is unfinished: its row would grow under the numbers
    thoughts = db.execute(
        "select n, steps, status, model from thought where ended is not null order by n").fetchall()
    print(f"thoughts: {len(thoughts)}  "
          f"status: {dict(db.execute('select status,count(*) from thought group by status'))}")
    print(f"models: {db.execute('select model,count(*) from thought group by model').fetchall()}")

    # per-thought call counts, tokens, and the msgs-size of the biggest request sent
    carry, whole, steps_of = {}, {}, {}
    est_max, last_tool_call, last_call = {}, {}, {}
    multi = 0
    for n, steps, status, _model in thoughts:
        rows = db.execute(
            "select id, request, response from call where thought=? order by id", (n,)).fetchall()
        steps_of[n] = steps
        if not rows:
            continue
        first = db.execute(
            "select tokens_in from call where thought=? order by id limit 1", (n,)).fetchone()
        carry[n] = first[0] if first and first[0] else None
        tot = db.execute("select sum(tokens_in) from call where thought=?", (n,)).fetchone()[0]
        whole[n] = tot
        for cid, req, resp in rows:
            rq = load(req)
            if rq and len(rq.get("messages") or []) > 1:
                est = sum(len(json.dumps(m)) for m in rq["messages"])
                est_max[n] = max(est_max.get(n, 0), est)
            rs = load(resp)
            tc = (rs or {}).get("choices", [{}])[0].get("message", {}).get("tool_calls")
            if tc:
                last_tool_call[n] = cid
                multi += 1 if len(tc) > 1 else 0
        last_call[n] = rows[-1][0]

    cs = [carry[n] for n in carry if carry[n]]
    ws = [whole[n] for n in whole if whole[n]]
    ratios = [carry[n] / whole[n] for n in whole if whole[n] and carry.get(n)]
    print(f"\ncarry   median {statistics.median(cs):.0f} tok  n={len(cs)} "
          f"first {cs[0]} last {cs[-1]}")
    print(f"whole   median {statistics.median(ws):.0f} tok  n={len(ws)}  sum {sum(ws)}")
    print(f"ratio   median {statistics.median(ratios) * 100:.3f}% of a thought's whole input")
    ns = [n for n in carry if carry[n]]
    cost, secs = db.execute(
        "select sum(cost), sum(seconds) from call where thought in "
        "(select n from thought where ended is not null)").fetchone()
    print(f"cost    ${cost:.2f} over {secs / 3600:.1f} h of charged model time")
    print(f"r(thought_no, carry) = {pear(ns, [carry[n] for n in ns]):.3f}   "
          f"first10 {statistics.median(cs[:10]):.0f} -> last10 {statistics.median(cs[-10:]):.0f}")
    pairs = [(steps_of[n], whole[n] / steps_of[n]) for n in whole
             if whole[n] and steps_of[n]]
    print(f"r(steps, tokens_in/steps) = {pear([p[0] for p in pairs], [p[1] for p in pairs]):.3f}"
          f"  n={len(pairs)}")
    print(f"assistant messages carrying >1 tool_call: {multi}")

    # what one step costs: the transcript is re-sent, so the price of a step is the size of what
    # is already there. Within-thought slope = tokens added per model call.
    slopes, groups = [], {}
    for n, steps, _s, _m in thoughts:
        ti = [x[0] for x in db.execute(
            "select tokens_in from call where thought=? order by id", (n,)) if x[0]]
        if len(ti) < 5:
            continue
        slopes.append((ti[-1] - ti[0]) / (len(ti) - 1))
        g = "<=30" if steps <= 30 else "31-45" if steps <= 45 else "46-59" if steps < 60 else "60+"
        groups.setdefault(g, []).append(sum(ti))
    print(f"tokens added per model call within a thought, median: {statistics.median(slopes):.0f}")
    for g in ("<=30", "31-45", "46-59", "60+"):
        v = groups.get(g, [])
        if v:
            print(f"  steps {g:>5}: n={len(v):>2}  median whole-thought input "
                  f"{statistics.median(v):>9.0f} tok")
    print(f"aggregate tokens per step: "
          f"{sum(ws) / sum(steps_of[n] for n in steps_of):.0f}")

    # forced causes, read from the stored calls
    print("\nforced thoughts and what ended them (read, not inferred):")
    nudge = chars = 0
    for n, steps, status, _m in thoughts:
        if status != "forced":
            continue
        after = 1 if last_tool_call.get(n) and last_call[n] > last_tool_call[n] else 0
        est = est_max.get(n, 0)
        if after >= 3:
            cause = "nudge"; nudge += 1
        elif est >= 0.97 * 400000:
            cause = "chars"; chars += 1
        else:
            cause = "steps"
        print(f"  #{n:>3} steps={steps:>3} biggest-request={est:>7} chars "
              f"cause={cause} (calls after last tool call: {after})")
    print(f"  totals: steps {sum(1 for t in thoughts if t[2]=='forced') - nudge - chars}, "
          f"chars {chars}, nudge {nudge}")


if __name__ == "__main__":
    main()
