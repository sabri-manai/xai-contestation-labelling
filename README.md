# Multi-annotator Labelling Tool for Contestation in XAI Transcripts

**Technology:** Python, Streamlit or FastAPI, pandas, SQLite

## Background

XAI-FUNGI (Bobek et al., *Scientific Data* 12, 2025) is a think-aloud corpus. In it, 39
participants — mycology experts, data-science/IT people, and social-science and humanities
participants — interpret explanations of a mushroom-edibility classifier. The explanations
are descriptive statistics, SHAP, LIME, Anchor and counterfactuals. The transcripts are in Polish.

Participants often push back on what they are shown. They reject a prediction, challenge its
evidence, or dispute whether a chart represents the model at all. We call this **contestation**:

> an explicit or implicit challenge to an AI system's conclusion, reasoning, evidence,
> explanation, or epistemic authority that calls for justification, correction,
> reconsideration, or acknowledgment of uncertainty.

Contestation is **not** the same as misunderstanding. A participant who says "I don't know how
to read this chart" has not understood it. A participant who says "this makes no sense, given
what I know about this species" is contesting it. Telling these two apart is the hard part of
the task. In a first pilot, two trained coders agreed on only 64% of yes/no decisions.

A pilot of 76 episodes has already been labelled and adjudicated. This project scales that
pilot up to several annotators.

## Goals

1. **Build an online labelling tool** where several annotators label transcript episodes
   independently, agreement is measured, and disagreements are resolved by adjudication into a
   single final label per episode — not just collected.
2. **Use it to label the provided batch** (`data/episodes_to_label.csv`, 250 episodes) and
   reconcile it into a final, adjudicated gold set in the same shape as `gold_standard.csv`.
   Each episode should be labelled by at least two annotators. The result is training data for
   ML models that detect contestation, and an estimate of how much contestation the pilot's
   word-list filter misses.

## Provided resources

| File | What it is |
|---|---|
| `data/episodes_to_label.csv` | 250 unlabelled episodes, the work to be done |
| `data/gold_standard.csv` | 76 episodes with final, adjudicated labels (44 yes / 32 no) |
| `taxonomy.json` | The label schema: definition, boundary rules, allowed values, constraints |
| `coding_guide.md` | The full annotation guide with worked examples (required reading for annotators) |
| `data/sample_manifest.json` | How the batch was drawn: seed, per-cell cap, pool and sample per cell |

### Episode columns (both CSVs)

| Column | Meaning |
|---|---|
| `episode_id` | Unique id, `<transcript>:<utterance>` (e.g. `PK_DE_04:189`) |
| `transcript_id` | Pseudonymous session code; the middle part is the group (`DE`, `IT`, `SSH`) |
| `participant_group` | `DE` mycology experts, `IT` data-science/IT, `SSH` social sciences and humanities |
| `explanation_format` | Descriptive statistics, SHAP, LIME, Anchor, Counterfactual |
| `explanation_theme` | Finer slide type (e.g. bee swarm vs. waterfall for SHAP) |
| `speaker` | Who said the target line (always `Participant` here) |
| `sample_batch` | `flagged` (picked by the word list) or `random_unflagged` (a random line the word list did not pick). Do **not** show this to annotators |
| `challenge_hits`, `incomprehension_hits` | How many lexicon markers matched. Do **not** show these to annotators, as they would bias them |
| `text_pl` / `text_en` | The target line: Polish original / English translation |
| `context_pl` / `context_en` | Up to 4 utterances either side, separated by ` \|\| `. Each line is prefixed `P:` (participant) or `INT:` (interviewer) |
| `en_source` | Where the English came from (`claude`: translated directly with Claude, line by line) |

`gold_standard.csv` adds the label columns `is_contestation`, `presence`, `target`,
`interaction_act`, `grounds` and `expected_response`. It also adds `gold_role`:
- `example`: 12 episodes that annotators may see as training examples.
- `calibration`: 64 episodes that must stay hidden and are mixed into annotators' queues to
  check their quality.

## The labelling task

For each episode the annotator reads the target line in its context. They then fill in:

- `is_contestation`: `yes` / `no`. Always required.
- If `yes`, one value each for `presence` (explicit / implicit / ambiguous), `target`,
  `interaction_act`, `grounds` and `expected_response`.
- `notes`: free text. Required when `presence = ambiguous`.

The allowed values and the rules are in `taxonomy.json`. The tool should load them from that
file rather than hard-coding them. The judgement is about the **target line**: the context is
there only to help interpret it. Where the Polish and English disagree, the Polish wins.

## Requirements for the tool

**Must have**

1. **Accounts.** Every annotator logs in with a personal id. Every label is stored with
   annotator id, episode id, timestamp and the label values.
2. **Import.** Load episodes from the provided CSVs. Do not hard-code the columns beyond those
   listed above.
3. **Labelling screen.**
   - Show the target line clearly highlighted inside its context, with the speaker tags
     visible. Let the annotator switch between Polish and English, or show both.
   - Use dropdowns limited to the values in `taxonomy.json`.
   - Enforce the constraints: `no` means `presence = absent` and the other four fields empty;
     `yes` requires all five fields; `ambiguous` requires a note.
4. **Independent labelling.** Annotators must not see each other's labels, the gold labels of
   calibration items, the lexicon hit counts, or `sample_batch`. Flagged and random episodes
   must look identical in the queue.
5. **Assignment.** Each episode in `episodes_to_label.csv` is assigned to at least two
   annotators. Show progress per annotator and overall.
6. **Calibration.** Mix the hidden `calibration` gold episodes into each annotator's queue
   (for example, about 1 in 10 items). Report each annotator's agreement with gold on
   `is_contestation`.
7. **Raw labels are never overwritten.** If an annotator edits a label, keep the history.
   Adjudicated final labels go in a separate table, not on top of the annotators' labels.
8. **Disagreement detection.** Once an episode has labels from all its assigned annotators,
   decide automatically whether it needs adjudication:
   - Agreement on `is_contestation` → the episode is auto-finalized. If every annotator who
     said `yes` also agrees on a structured dimension, carry that value through; otherwise
     leave that one dimension open for adjudication even though presence is settled.
   - Disagreement on `is_contestation`, or agreement on `yes` with no agreement on a structured
     dimension → the episode is queued for adjudication (this is most of the work: in the
     pilot, 14 of 36 double-coded episodes disagreed on presence alone).
9. **Adjudication view.** For each queued episode, show every annotator's full label set and
   notes side by side with the original text and context. Let a designated adjudicator (a role,
   not just any annotator) record one final label per dimension plus a short reason, following
   the same `taxonomy.json` constraints as ordinary labelling. Record *why* annotators split —
   at minimum, which disagreement is on presence (yes/no) vs. only on a structured dimension —
   since that distinction is what the pilot's own write-up turned on.
10. **Adjudication record is separate from raw labels.** Adjudicated labels (automatic or
    manual) live in their own table, keyed by episode, pointing back at the annotator labels
    they resolved. Never overwrite an annotator's raw label with the adjudicated one.
11. **Export.** Export to CSV:
    - every annotator's raw labels, one row per (episode, annotator);
    - the adjudicated final labels, with the same columns as `gold_standard.csv` (including
      which episodes were auto-finalized vs. manually adjudicated), so the two files can be
      concatenated for model training.

**Should have**

12. **Agreement report.**
    - For `is_contestation`: Cohen's κ for each pair of annotators, and Krippendorff's α across
      all of them, computed *before* adjudication — this is the number the pilot's 64% figure
      is compared against.
    - For each of the four structured dimensions: agreement on the episodes where both
      annotators said `yes`.
    - The share of contestation separately for `flagged` and `random_unflagged` episodes. The
      random share shows how much contestation the word list misses.
    - How often the adjudicated label matched each individual annotator (so no annotator looks
      systematically over- or under-permissive without it showing up).
13. **Example browser.** A page showing the 12 `example` gold episodes with their labels, to
    train new annotators before they start.

**Nice to have**

14. An "I'm unsure / skip" option, plus time spent per episode.
15. Filters by group, format or annotator. A dashboard of label distributions.

## Constraints

- **Data stays local.** Participants are identified only by pseudonymous session codes. The tool
  must not send transcript text to external services (cloud translation, hosted LLM APIs,
  analytics) unless the project supervisors approve it. Do not try to identify participants.
- Use SQLite as the store. Ship a script that recreates the database from the CSVs.

## Deliverables

1. Source code with a README explaining how to install and run it locally, and how to load the
   provided data.
2. The SQLite database after labelling, and the exports described in requirement 11: raw
   annotator labels, and the adjudicated final labels for all 250 episodes.
3. A short report:
   - number of annotators and labels collected;
   - pre-adjudication agreement figures (requirement 12) and each annotator's calibration
     scores (requirement 6);
   - how many episodes were auto-finalized vs. sent to manual adjudication, and how often the
     adjudicated label matched each annotator;
   - the distribution of final labels;
   - a few disagreements you found hard to adjudicate, and why.

## Caveats about the provided data

- **The English is a translation.** All English was translated directly from the Polish with
  Claude, one utterance at a time, keeping hesitations and hedges. The gold set uses the same
  translation the pilot coder labelled from. The transcripts themselves come from
  speech-to-text and are garbled in places, and the translation keeps that. Treat the Polish as
  authoritative. Known speech-to-text quirks:
  - *nielegalny* ("illegal") often stands for *niejadalny* ("inedible"). The English keeps
    "illegal".
  - "szarfa"/"szar" ("sash"/"gray") is usually SHAP.
  - A line consisting only of `~` is an inaudible placeholder.
  - A few lines are tagged with the wrong speaker (e.g. `PK_DE_09:63`–`64` read like the
    interviewer).
- **Gold quality differs by dimension.** In the gold set, only `is_contestation` was labelled by
  two coders and adjudicated. The other four dimensions were labelled by one coder. Use them as
  a reference, not as a strict benchmark.
- **Expect many `no` labels.** In the pilot, a little over half (44 of 76) of the word-list
  candidates turned out to be contestation. The random unflagged episodes will be mostly `no`.
  That is the point of including them, so don't treat those labels as wasted effort.
- **One cell has no new flagged episodes.** IT × Counterfactual has none, because all of its
  candidates are already in the gold set. Several other cells are small (IT × Anchor and
  IT × LIME have 2 each).

## How the resources were produced

The 250 episodes come in two parts, shuffled together (seed 42 throughout).

**Flagged (204 episodes).** This part repeats the pilot's sampling method at a larger scale:
- A bilingual lexicon of challenge markers flagged 667 candidate utterances across all
  transcripts.
- The draw kept only participants' own lines on genuine explanation slides. That leaves 331,
  of which 76 are the gold episodes.
- The 76 gold episodes and the three examples quoted in the coding guide were removed, leaving
  254.
- These were stratified by group × explanation format, and up to 25 per cell were drawn at
  random.

**Random unflagged (46 episodes).** These were drawn uniformly at random from the 4,614
participant lines on explanation slides that the lexicon did **not** flag and that have at
least 5 words. Shorter lines are mostly back-channel ("Mhm", "Tak."). This part brings the
total to 250. Because the draw is uniform, it follows the pool's own group mix: 63% SSH, 27% IT
and 10% DE. That works out to 24 SSH, 17 IT and 5 DE episodes.

Every episode's context is rebuilt from the transcripts in the same ±4-utterance,
speaker-tagged form the pilot coders saw.

To regenerate the batch, or to draw a different size, run this from the research repository:

```bash
.venv/bin/python notebooks/07_build_labelling_project.py                         # 204 flagged + 46 random = 250
.venv/bin/python notebooks/07_build_labelling_project.py --per-cell 20 --total 250  # 184 flagged + 66 random
```

New utterances need English first. The script writes them to
`outputs/07_labelling_project/translation_todo.csv`, then stops until their translations are in
`outputs/07_labelling_project/translations/*.json`.
