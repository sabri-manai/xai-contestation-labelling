# XAI Contestation Labelling

A minimal local tool for annotating contestation in XAI think-aloud transcripts.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
streamlit run app/main.py
```

Open [http://localhost:8501](http://localhost:8501). The database is created and
populated automatically on first run.

## Usage

1. Enter your **email** in the sidebar — progress is saved and restored on return.
2. Use **Episode #** to jump to any episode or pick up where you left off.
3. **Label** — read the target line in context, fill in the form, hit **Save ✓**.
   - **← Back** / **Skip →** to navigate without saving.
4. **Guide** — taxonomy reference (EN/PL) with three labelled examples.

## Files

```
app/
  main.py        entry point
  db.py          SQLite helpers
  seed.py        loads CSVs into labels.db
  views/
    label.py     annotation screen
    guide.py     taxonomy + examples
data/
  episodes_to_label.csv   250 episodes to label
  gold_standard.csv       76 adjudicated gold episodes
taxonomy.json             label schema
coding_guide.md           full annotation guide
```

## Codebook v1.1 (29 Oct 2026)

The form has a second gate, **explanation request**, filled for every episode independently
of contestation (see the Guide tab, "Second gate"). The unit rule and boundary rule 1 were
tightened; `coding_guide.md` §6 has the changelog. `labels.db` gains the column on first start
(additive migration, nothing is rewritten).

## Your labels live in `labels/<your code>.csv`

**Order matters:** label episodes **1–100 first**, in order, without skipping ahead. Everyone
labels these same 100; they are used to measure agreement between labellers.

**Already labelling?** `git pull` in the same folder, restart the app, log in with the same
email. Everything you labelled is still there. Episodes with a yellow warning need the new
"explanation request" field.

The app saves all your labels to `labels/<your code>.csv` (code shown in the sidebar; the file
never contains your email). To share progress:

```bash
git add labels && git commit -m "labels" && git pull --rebase && git push
```

Never commit `labels.db`.

**Project lead:** `labelers_private.csv` (not committed) lists email → code for logins on this
machine; `.venv/bin/python -m app.sync alice@x.pl bob@y.pl` prints the code for any email.

## Hand-off to the framework

```bash
git pull
.venv/bin/python export_labels.py     # labels/*.csv + labels.db → ../xai-contestation-framework/data/human_labels.csv
```

The Jev notebook moved to `../xai-contestation-framework/benchmark/jev_detect.ipynb`;
`jev/` here keeps run 1 (codebook v1.0) and the disagreement review for reference.

## Notes

- `labels.db` is gitignored — back it up separately.
- Polish is authoritative; English is a translation.
- Labels are append-only; editing an episode creates a new version row.
