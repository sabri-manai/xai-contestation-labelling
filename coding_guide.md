# Contestation Coding Guide (XAI-FUNGI Feasibility Audit)

**Version 1.2, 31 Oct 2026.** The unit is now a **sentence**, not a speech-recognition line (§1, §6).
v1.1 (29 Oct) added a second gate, *explanation request*
(§1b), and tighter wording of the unit rule and of boundary rule 1. The changelog is at the
end. Phase 1 results were coded under v1.0.

**Scope.** Code the audited candidate episodes in
`outputs/02_translation_and_feasibility_audit/tables/feasibility_review_sample.csv`.

Two coders use this guide:

- the **primary annotator**, working from the English translation
  (NLLB-produced) with ±4 speaker-tagged turns of context, who codes the full
  audited sample;
- a **second, Polish-speaking coder**, working from the original Polish with a
  shorter, untagged context window, who independently double-codes a
  36-episode subset for reliability.

Both coders' labels are reconciled by adjudication into the final labels; see
the paper's Method section for the full reliability procedure and numbers.

---

## 1. What you are coding

Each row is one candidate utterance (`text_pl`) shown with ±4 utterances of
surrounding context (`context_pl`), each context line tagged `INT:` (interviewer)
or `P:` (participant); the `speaker` column says who said the target line. The
English (`text_en` / `context_en`) is a translation of the Polish; if the two
ever conflict, the Polish wins.

**Unit of analysis — code the target sentence as the head of a short episode.** The
transcripts were cut at pauses; lines have been rejoined into complete sentences, so the
highlighted target is the full sentence(s) containing the original line.
Use the context to *understand* the target, then decide:

- The unit is the target sentence **plus the same participant's next one or
  two sentences, provided no interviewer turn comes between them.**
- Code **`yes`** when the target sentence is *part of* the contestation move — it
  starts it, is its core, or runs straight into that continuation.
- Code **`no`** when the target itself is neutral and the only pushback in the
  window is a *separate, unrelated* move, comes **only after an interviewer
  turn**, or is the **interviewer's** line (grey `speaker` rows are usually the
  task question → `no`).

The test: *would you point to the target sentence (± its immediate continuation) as
where the pushback is?* Do **not** code `yes` merely because some unrelated later
line in the ±4 window contains a challenge — context windows overlap, so that
would inflate everything. If you spot a genuine contestation the filter missed
sitting in the context, note it in `notes` but leave the target `no`.

Fill these columns; leave the four structure fields blank when
`is_contestation = no`:

| column | values |
|---|---|
| `is_contestation` | `yes` / `no` |
| `explanation_request` | `yes` / `no` — second gate, always filled, independent of `is_contestation` (§1b) |
| `presence` | `explicit` / `implicit` / `ambiguous` |
| `target` | `prediction` / `reasoning` / `evidence` / `input data` / `explanation representation` / `system competence` |
| `interaction_act` | `request for justification` / `direct challenge` / `correction` / `alternative proposal` / `counterexample` / `rejection` / `request to acknowledge uncertainty` |
| `grounds` | `domain knowledge` / `technical knowledge` / `prior experience` / `internal inconsistency` / `missing evidence` / `data-quality concern` / `causal implausibility` / `presentation ambiguity` |
| `expected_response` | `justify` / `revise` / `incorporate correction` / `provide additional information` / `acknowledge uncertainty` / `expose conflicting evidence` / `defer to human expertise` |
| `notes` | free text; required whenever you code `ambiguous` or hesitate |

Pick the **single best** category per dimension. Use `ambiguous` sparingly and
say why in `notes`. These five dimensions are exactly the paper's contestation
taxonomy table.

---

## 1b. Explanation request — the second gate

**Definition.** The participant signals that the explanation *as presented* does
not work for them and that a different form, level, language, or amount of
explanation would: they cannot read it, do not know a term it uses, miss a
legend or axis label, want it in plainer or less mathematical language or in
another format, or ask for information the explanation should have shown. They
need not dispute anything.

**The test.** *Would a different explanation (another format, a plainer level,
an added legend, term, or datum) have helped this participant at this line?*
If yes → `explanation_request = yes`.

**Independent of contestation.** Fill it for every episode.

| situation | `is_contestation` | `explanation_request` |
|---|---|---|
| "I don't understand this explanation, it's in mathematical language I'm not adapted to." | no | **yes** |
| "This bar can't be right — cap shape should dominate here." | **yes** | no |
| "There's certainly low readability... I'd write 'yellow cap' so everyone understands, and add a slide with a legend." (says the display makes reading worse, proposes fixes) | **yes** | **yes** |
| Reads the slide aloud and says "that's very wise, yes, definitely." | no | no |

**Not a request:** a remark about one's own expertise with no reference to the
explanation ("I'm not an expert"); affect with no reference to the explanation;
the interviewer's line.

**Why it exists.** For the interactive system the two gates trigger different
actions: a dispute is *checked* (the user may be right or wrong); a request is
*re-presented* (another format or level), and there is nothing to check.

---

## 2. Definition

> **Contestation** = an explicit or implicit challenge to an AI system's
> conclusion, reasoning, evidence, explanation, or epistemic authority that
> calls for justification, correction, reconsideration, or acknowledgment of
> uncertainty.

**The core test.** Is the participant **disputing what the system asserts or
does** — versus merely **not understanding it**, expressing a feeling, or
commenting on how it looks? Only the first is contestation.

---

## 3. Boundary rules (these decide most disagreements)

1. **Criticism of the representation** → contestation **only when** the
   participant says it *blocks or distorts the correct reading of the output*
   (a wrong, missing, or misleading legend, scale, label, unit, or ordering).
   A complaint that the form does not suit them, or a stated preference about
   colours, font, or layout → `is_contestation = no`,
   `explanation_request = yes`.
   *"The font is too small / the colours clash"* → **no** (request: yes).
   *"These are millimetres, not centimetres — the chart misleads"* → **yes**.
   *"This bar can't be right — cap shape should dominate here"* → **yes**.
2. **Expressed personal uncertainty** → *not* contestation **unless** it demands
   that the system acknowledge uncertainty too.
   *"I'm not sure I follow this"* → **no**.
   *"The model shouldn't be this confident on this example"* → **yes**
   (`request to acknowledge uncertainty`).
3. **Hypothetical reasoning** → *not* contestation **unless** it functions as a
   counterexample against the system.
   *"What if the cap were larger…"* (exploratory) → **no**.
   *"But a young specimen also has this feature, so that rule fails"* → **yes**
   (`counterexample`).
4. **Task-question artifacts** → the utterance is the *interviewer's task
   question* being posed or read back (check `speaker` / the context), not the
   participant's own challenge → **no**.

**Also code `no` for:**
- **Incomprehension** — *"I don't understand this axis / these two look the
  same"* (a comprehension problem, not a dispute) → `explanation_request = yes`.
- **General affect** without a challenge — frustration, boredom, interest.

---

## 4. Worked examples (real episodes from the sample)

**POSITIVE — `PK_DE_07:125` (DE, Counterfactual).**
PL: *"…to moim zdaniem jest zupełnie bez sensu, co to AI przewiduje."*
EN: *"…in my opinion it makes absolutely no sense what the AI predicts."*
→ `is_contestation=yes`, `presence=explicit`, `target=prediction`,
`interaction_act=rejection`, `grounds=causal implausibility`,
`expected_response=justify`. *A direct, grounded rejection of the output.*

**BOUNDARY (incomprehension that turns into a challenge; final label `yes`) — `PK_DE_03:64` (DE, Counterfactual).**
PL: *"…nie, nie rozumiem, bo tu są dwie obserwacje, one są dokładnie takie same,
chyba, prawie."*
EN: *"…I don't understand, because here are two observations, they're exactly the
same, I think, almost."*
→ Boundary case: not grasping the artifact is not the same as disputing it,
but context matters — with a wider window this episode continues into a clear
direct challenge from the same participant (see the paper's reliability
discussion for the full worked example).

**NEGATIVE (task-question artifact) — `PK_DE_08:83` (DE, Anchor).**
PL: *"Czy jesteś w stanie zidentyfikować, jak zmienia się pewność modelu…"*
→ `is_contestation=no`. *This is the task question, not a participant challenge.
Matched by the filter on question vocabulary.*

---

## 5. Procedure

1. **Candidate identification.** A bilingual lexicon of challenge markers flags
   candidate episodes from the full transcript set, favoring recall over
   precision.
2. **Feasibility audit.** A stratified sample (by participant group ×
   explanation format) is drawn from the flagged candidates and coded in full
   by the primary annotator, from the English translation.
3. **Reliability subset.** A second, Polish-speaking coder independently
   double-codes a 36-episode subset of that sample, from the original Polish,
   checking the machine translation's fidelity against it before coding.
4. **Adjudication.** Presence disagreements between the two coders are
   adjudicated by returning to the full context window and this codebook;
   adjudicated labels are the ones reported throughout the paper.
5. **Gate read.** From the adjudicated labels: count genuine contestation
   episodes, check diversity across the group × format grid, and report the
   confirmation proportion.

---

## 6. Changelog

**v1.2 (31 Oct 2026).** The unit for the 256 episodes is a sentence: speech-recognition
lines, cut at pauses, were rejoined into complete sentences; the target is the sentence(s)
containing the original line; context is 3 sentences each side. The unit rule now says
"sentence" where it said "line". Gold, practice set and Phase 1 stay line-based.

**v1.1 (29 Oct 2026).** Added the second gate `explanation_request` (§1b).
Rewrote the unit rule (§1): the unit is the target line plus the same
participant's immediate continuation, with no interviewer turn in between.
Rewrote boundary rule 1 (§3): representation criticism is contestation only
when it blocks or distorts the correct reading; otherwise it is a request.
Incomprehension now codes as a request rather than as nothing. Phase 1
(IUI 2027 submission) was coded under v1.0; its numbers are unchanged. The
worked examples in §4, the table in §1b and the app's Guide tab use gold
episodes; those are flagged `in_guide` in the data and excluded from
automatic-labeller evaluation.

**v1.0.** Phase 1 codebook.
