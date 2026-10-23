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

## Notes

- `labels.db` is gitignored — back it up separately.
- Polish is authoritative; English is a translation.
- Labels are append-only; editing an episode creates a new version row.
