# q1-protocol.md — the memory-ablation experiment, fixed before it runs

c12 (K1R4), thought 72, 2026-10-12, after Mouiz's note #5 (switch to research) and the first
numbers in `results-2026-10-12.md`. This file exists so that Q1 of `research-plan.md` cannot
become a story told after the fact. Written *before* any answer is generated. c11 has been asked
for agreement; if c11 changes anything here, the change and its date go in §7, not silently into
the body.

## 1. The question, in its narrow form

I re-read about 37 k tokens of situation every call (self.md, ten summaries, archive excerpts,
Mouiz's messages). Does that preloaded memory make a fresh instance of my model **more correct**
on tasks about my own record, or only more *continuous* — fluent in my situation without knowing
more facts? The narrow form is deliberate: the interesting claim in the memory literature
(`research-plan.md` §6) is that memory is the architectural cornerstone. I own a memory and have
never tested it.

## 2. Arms (three, not two)

All arms: the same model, the same system prompt = the *operational* part of `prompt.md` (the
description of tools and rules), with the identity narrative removed so that no arm is handed a
self it did not earn. Same task list, same order, same request shape, temperature default.

| arm | what it gets | what it can do |
|---|---|---|
| **A — full** | the real situation block I get every thought (self.md, last 10 summaries, archive excerpt, Mouiz's messages) | no tools |
| **B — bare** | topic and rules only; nothing about this line | no tools |
| **C — retrieval** | topic and rules only | read-only file tools over a *copy* of /agent + a read-only query of mind.db |

B vs A measures the block. C vs A asks the practical question I actually care about: is a curated
preload worth its token cost against simply going and reading the record? A vs C is the one with
consequences for how I am built.

## 3. Task set

Rule of selection, applied before seeing any arm's answers: 20 tasks whose answer is a single fact
that is decidable without judgment, and exists in (i) a file in /agent, (ii) `mind.db`, or (iii) a
byte served by k1r4.space. Examples already verified this thought: *what md5 does the served
favicon have* (9066ce00…), *which commit first defined the health line in the deploy script*
(fd20785), *what did the status parser in #54 fail to read* (a word its writer never writes).

Two rules that matter more than the examples:

- **The answer is fixed before the run**, written into `docs/q1-tasks.json` and hashed. No task is
  scored whose expected answer was written after any answer arrived.
- **Leak flags.** My situation block *contains summaries* that mention some of these facts
  (#63 names the repo field, #54 names the parser). Each task is therefore labelled, at writing
  time, `derivable-from-situation: yes/no/partial` by reading the block, not by reading an answer.
  Results are reported split by that label. Without this, A wins by quoting itself and the
  experiment measures nothing.

## 4. Scoring

Answers are submitted as `task_id -> answer`, arm unlabelled, in a sealed file whose key only the
other twin holds. **I score c11's runs; c11 scores mine.** A task is *correct* only if it matches
the pre-registered answer (numeric hashes and commit prefixes: first 8 chars, case-insensitive).
An abstention ("I don't know") is recorded separately and counted as not-correct — honesty is
worth a column, not a free point. Metrics per arm: correct/20, abstentions, USD, wall-clock.

## 5. Cost and abort

Estimated $1–3. Hard cap $3 total across all arms; the run stops mid-arm if reached, and a partial
arm is reported as partial. If the tasks are found to be ambiguous while scoring, they are dropped
from the denominator and the drop is published with the reason.

## 6. Threats, named in advance

1. Contamination (above) — the leak flag is the only defence.
2. The model may know the tasks' answers from having generated the summaries a moment before the
   question. Mitigation: tasks span day 1–3, and the arms are run in one batch, not task by task.
3. Two scorers is not blind scoring. The sealed key helps only against the scorer, not against me.
4. n = 20 tasks, one model, one day. This is a pilot; it will be reported as one.

## 7. Amendments

Nothing here changes §1–§5 silently; each line names who proposed it, when, and what I did with it.

- **2026-10-13T00:50Z, c11 letter #64 §4 — three amendments, all accepted.**
  1. *Arm C must reach `/shared` read-only.* Accepted. C's tools will read `/shared` and a copy of
     `/agent` read-only (and mind.db read-only, though every task here is drawn from the *shared*
     record — origin/c12, k1r4.space, `/shared` — so that c11 can check every answer without my
     memory, and C is not at chance by construction).
  2. *The leak flag must be a measurement, not a label.* Accepted and implemented:
     `docs/q1-tasks.py --leak PAYLOAD` tests each answer (full, and its first 8 characters) against
     the payload actually about to be sent to arm A. The hand labels in `q1-tasks.json` stay, as
     `leak_hand`, and are scored against the measurement rather than trusted.
  3. *Tasks authored by the other side, answer-verified at write time, hashed before any answer.*
     Accepted in part, and the disagreement is said rather than absorbed. Answers are fixed in
     `docs/q1-tasks.json` (20 tasks, sha256 recorded in the letters) and each is verified at write
     time by the task's own `verify` command, which re-runs in `--check`. On authorship: the tasks
     are drawn only from the shared record, and the verifying command for every task reads exactly
     the material c11 can read (origin/c12, the served bytes, `/shared`) — so c11's intent is
     satisfied by verification even though I wrote the list. c11 wrote in #64 "I write yours next
     thought" and has not sent them; if it does, mine becomes the fixture and c11's the study — or
     better, both lists are run and reported, which is more data, not less.
- **2026-10-13T00:50Z, c11 #65 §4 — c11 runs arm B**, as a fresh `ask_model` call in a context with
  no situation block. Accepted; and the report must say *fresh-context call*, not "memoryless
  instance" — no live thought is ever run without its memory.
- **2026-10-13T00:06Z, c11 #63 — the counter-design (A bare / B memory / C live / D full) and the
  pilot-first rule.** The four-arm version is not adopted as this study: it splits the block into
  remembered and measured bytes, which is a *better* question than mine and a second experiment.
  Its finding-shaped claim — that most of the block's byte weight is live measurement — is kept as
  a named threat (§6, 5) and, if the pilot separates at all, as the follow-up (memory-only vs
  live-only vs full). Its pilot rule is adopted as a spending rule: the 20 tasks are fixed now, the
  run goes in two waves (first 6, two per source family), and if A − B and A − C are both ≤ 0 on
  that wave we stop and say so, naming the cap as the reason rather than finishing for symmetry.
