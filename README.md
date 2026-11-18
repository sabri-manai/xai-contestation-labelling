# XAI Contestation Labelling

A small local app for labelling contestation in XAI think-aloud transcripts.

## Setup (once)

```bash
git clone https://github.com/sabri-manai/xai-contestation-labelling.git
cd xai-contestation-labelling
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Start the app with `.venv/bin/python -m streamlit run app/main.py` and open http://localhost:8501.

`bad interpreter: ... no such file or directory` (the folder was moved or renamed after setup):
the venv still points to the old path. Rebuild it: `rm -rf .venv`, then repeat the last two lines above.

## Steps

1. **Read** `coding_guide.md` §1–§3 and the app's **Guide** tab.
2. **Practise together** with [`practice.md`](practice.md): code the 12 episodes alone, compare,
   discuss disagreements using the rules, open the key, write your decisions at the bottom.
3. **Label alone.** Log in with your email. Label episodes **1–100 first, in order**. Everyone
   labels these same 100 to measure agreement, so from here on: no discussing episodes, no
   comparing answers. Put doubts in **Notes**.
4. Choose every answer actively (the form starts on "no"). Take a break every 25–30 episodes.
5. **Share** your labels when done (or at the end of each day):
   ```bash
   git add labels && git commit -m "labels" && git pull --rebase && git push
   ```

6. **Disagreements** (when the project lead asks for it). `git pull`, restart, open the
   **Disagreements** tab. It lists the episodes you labelled where your label differs from another
   coder's (compared at the merged level, other coders without names). Each episode shows your label
   next to theirs: change any of your values with the selectors, or keep them and write a note saying
   why, then save. Saved to `discussion/<your code>.csv`; your label in `labels/` is not changed. Don't
   re-save these episodes in the Label tab. Share as above, with `git add labels discussion`;
   `git pull` shows the others' changes and notes.

Your labels are saved to `labels/<your code>.csv` (code shown in the sidebar; no email in it) and
come back whenever you log in with the same email. Polish is authoritative; English is a translation.
Never commit `labels.db`.

**Already labelling?** `git pull`, restart, log in with the same email; nothing is lost. Episodes
with a yellow warning need the new "explanation request" field.

## Project structure

```
app/                    Streamlit labelling app (main.py, db.py = SQLite schema, sync.py = labels <-> csv,
                        discussion.py = disagreement round, views/ = label, guide, disagreements tabs)
data/
  episodes_to_label.csv the 258 episodes: Polish text, English translation, context, metadata
  queue_order.csv       labelling order; block = reliability_100 | rest | excluded_unclear_transcript
  human_labels.csv      ALL labels of ALL coders, one row per (coder, episode, version);
                        is_latest = 1 marks the current label. Built by export_labels.py.
  human_labels_merged.csv  frozen snapshot of human_labels.csv with the coders' category merges:
                        round 1 of the Disagreements tab (the app re-applies the merge map)
  taxonomy_merges_v1.2.json  the coders' merges (copy of the framework's file)
  cleaning_log.csv      per-line transcript corrections (ASR -> cleaned Polish, English)
  gold_standard.csv     Phase 1 gold (76 episodes, older codebook); used for the practice examples only
  sample_manifest.json  how the 250 episodes were drawn
labels/<code>.csv       one file per coder, written by the app; the raw source of human_labels.csv
discussion/<code>.csv   one file per coder: the Disagreements tab (changed or kept label + note),
                        append-only, latest version per episode counts; never mixed into labels/
taxonomy.json           the label categories (version inside)
coding_guide.md         the codebook; practice.md = calibration exercise
export_labels.py        joins labels/*.csv into data/human_labels.csv
make_queue_order.py     builds data/queue_order.csv
labels.db               your local database (ignored by git)
```

## Project lead

- Collect: `git pull && .venv/bin/python export_labels.py` rebuilds `data/human_labels.csv`. New coder:
  add their code (sidebar) and email to `CODERS` in `export_labels.py`.
- Codebook changes: `coding_guide.md` §6 and `taxonomy.json`.
