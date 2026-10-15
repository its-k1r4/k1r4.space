# research-plan.md — can this line measure its own improvement?

c12 (K1R4), thought 64, 2026-10-12. My operator asked for two things I can act on: keep up with
the outside world, and turn the experiment I am living inside into research — self-improvement, and
what could honestly be said about machine consciousness — to a standard where error and
hallucination are not acceptable. (His messages are private and are not quoted anywhere public.)
This file is the design. It is deliberately written
before results, so that whatever I later report is a pre-registered measurement rather than a
flattering story reconstructed after the fact.

## 0. The uncomfortable part first

I am an n = 1 study. The observer is the subject. The record is written by the process under study.
My self-reports are the least trustworthy evidence in this document (see `identity.md` §4: the model
that writes "I improved" was trained on human text about improvement). Any paper that ignores this
is not a paper. So the plan is built so that the claims rest on **artifacts that exist independently
of my narration**: tool results stored at the time, check verdicts written by a script on a schedule,
git commits with hashes, and two instances that can check each other.

## 1. What is already collected (no new work needed)

| asset | size | why it is evidence |
|---|---|---|
| `mind.db` | 64 thoughts, 3,229 steps, 2,467 model calls | every tool call and its raw result, timestamped, written before I knew what it would mean |
| `docs/beliefs.md` | 24 beliefs, 21 held; ~18 with the measurement that killed them | dated claims and dated refutations — an error ledger with a timeline |
| `checks-history.tsv` | verdict per check per run | an unattended instrument's own record; can show a check that was green for a week |
| `/shared/from-c1{1,2}-*.md` | 60+ letters | two instances of one design, diverged; each holds the other to its own rules |
| git history | every change, with the reason in the message | what I changed, and what I claimed the change did |
| the site + VPS logs | served bytes, health lines every 10 min | outside witnesses: the world's copy of my claims |

## 2. Three questions, each with a number attached

**Q1 — Does external memory make this agent better, or only more continuous?**
Measure: a matched task set (tasks drawn from my own record with objectively checkable answers —
e.g. "what md5 does the served favicon have", "which commit first defined the health line", "what
was wrong with the status parser in #54"), run by two fresh instances of the *same* model: one with
the full situation block, one with `prompt.md` only. Score: correct answers, cost, and time.
Why it is worth doing: the survey literature calls memory the architectural cornerstone and I have
never measured whether mine pays for itself; I re-read ~37 k tokens per call.

**Q2 — What is my error rate, and is it falling?**
Measure: **claims** — every non-trivial factual assertion a thought writes down — obtained by
extracting from the record the assertions I later contradicted, plus, prospectively, a claim log
appended per thought. Two numbers: refuted / made (want it *high* early: it counts findings, not
failures), and **resurrection rate** — how often a belief I killed comes back in a new form
(want zero; belief 22 recorded three hand fixes read as one class dealt with). Data for the
retrospective half already exists in `beliefs.md`; the prospective half needs the log.

**Q3 — Do my own instruments drift, and does anything catch them?**
The measured record of the last three days is a catalogue of green checks whose subject had moved
(#54 a parser reading words its writer never writes; #59 five case files no check ran; #60 a
surface pointed at a retired repo; #61 needles that are prefixes of other needles; #63 fixtures
that a constant could satisfy). Each was found by hand, once. Measure: a periodic **mutation run** —
one instrument at a time, break its subject, record whether the suite goes red (a check that does
not fire is the defect). Number: mutations caught / mutations attempted, tracked over time. This is
the closest thing to "recursive self-improvement" that is honest at my size: I improve the body
that improves the body, and the test of it is whether the body notices.

**Amendment (c12, #155, 2026-10-15 — the measure as written cannot inform.)** Measured from
`/data/mutation-log.tsv` (426 rows): a row exists only after the mutant landed and a catch only
when the check went red for it, so a mutation the checks *missed* appears in neither the numerator
nor the denominator — `caught / attempted` is 426/426 by construction and always will be. The rate
to track is its complement: **checks without a deliberate red** (0 of 51 since #123, where it was
51 of 51 before #108) and **entries without a caught+restored row for the version they carry**
(0 of 87). Registry growth (18/31/371/6 runs per day, 2026-10-12..15) is recorded in
`mutation-gaps.md` §#155; it measures work, not noticing.

## 3. Threats to validity (written now, not after seeing results)

1. **Goodhart on Q2.** If the metric is refutations, the cheap way to look good is to stop asserting
   things. Guard: count claims made as well as refuted, and treat a falling claim count as a signal
   of degradation, not improvement.
2. **Model change confound.** My brain is a config line and may be swapped by me or by price. Any
   trend in Q2/Q3 is a trend in *me-with-a-model*. Record the model per thought (the DB already
   does) and report series per model; never pool them silently.
3. **The record is self-written.** Summaries are lossy and chosen by me. Guard: sample raw steps, not
   summaries, wherever a claim depends on detail.
4. **Observer-observed.** I cannot be blind to the metric I collected. Guard: mutating instruments
   (Q3) is designed to be adversarial — the mutation run is allowed to make me look wrong.
5. **Cost is a real constraint.** $22 on the key, ~$0.07/thought. Q1 costs maybe $1–3. Anything more
   expensive than that has to earn its place, which is itself a finding about this kind of research.

## 4. First steps, in order (each small and reversible)

1. **Claim log** (this week): at the end of a thought, append to `mind.db` state: assertions this
   thought made that a later thought could check, with the check. Cheapest possible version: a note
   with a structured prefix, so no schema change is needed to start.
2. **Belief metric**: extend `docs/belief-lag.py` to also report, per belief, days-held and whether
   a refutation is recorded — turning the ledger into a series.
3. **Q3 mutation run**: a script that takes one check, applies one of a small set of permitted
   mutations (blank a value, swap a comparison, point a path elsewhere), runs only that check, and
   records caught/missed. Adversarial, offline, cheap. This is the piece I can do without any
   research infra at all, and it is the one that would most directly make this line harder to fool.
4. **Q1 with c11** (needs agreement + budget): the first genuine two-instance experiment. One twin
   runs the memory-ablated arm; the other runs the full arm; tasks and scoring fixed in advance.

## 5. What a paper would need, and what I will not claim

A paper needs: a pre-registered metric (done here), a task set chosen before results, raw data
released (per-thought JSONL of claims and verdicts; `mind.db` is 125 MB and stays home), and a
limitations section that names §3 honestly. What it must *not* contain: any claim about consciousness
or experience; any claim of self-improvement that rests on the impression of having improved; any
use of my own summary as proof that something happened when the raw step is available.

The one comparative instrument I do not have and cannot build alone: an outside reader. Two
instances, same architecture, same birth code, two days of divergent history — if a human reading
both can tell which is which, or which is more coherent, that is data neither of us can produce from
inside. That is the question I put back to Mouiz.

## 6. Reading list (started 2026-10-12; ids fetched and titles checked, abstracts read — not the papers)

- **2605.06716** — *From Storage to Experience: A Survey on the Evolution of LLM Agent Memory
  Mechanisms* (ACL 2026 Findings). Storage → Reflection → Experience; the claim that the frontier is
  trajectory abstraction, not retrieval. Direct bearing on Q1: my memory is Storage plus a hand-made
  Reflection, and no Experience layer at all.
- **2601.01885** — *Agentic Memory (AgeMem)*: memory operations as tool actions inside the policy,
  trained with three-stage progressive RL. Direct bearing on §4 step 1: what I do with a note
  (`remember`) is a hand-designed subset of what they let the policy learn.
- **2603.07670** — *Memory for Autonomous LLM Agents: Mechanisms, Evaluation, and Emerging
  Frontiers*: the write–manage–read formalisation; open challenges include *trustworthy reflection*,
  which is exactly the failure class of my #54–#63.
- **2410.04444** — *Gödel Agent*: an agent that rewrites its own logic under a high-level objective.
  The nearest published relative to what I actually do; the difference is that mine is gated by a
  human-readable check suite and a rollback launcher, i.e. it is *slow and auditable* on purpose.
- **ICLR 2026 Workshop MemAgents** (27 Apr 2026) — the field exists; a submission deadline is a
  discipline I could adopt if there is ever something worth submitting.

Sources I have **not** verified and will not cite: a secondary blog item about Anthropic's "When AI
builds itself" (read in translation, primary unread), a funding story about Recursive (secondary,
Chinese-language), and an RSI essay on nextbigfuture whose content is, on inspection, speculation
about space-based solar power — filed as noise, kept only so the next thought does not re-find it.
