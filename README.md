# XAI Contestation Labelling

A small local app for labelling contestation in XAI think-aloud transcripts.

## Setup (once)

```bash
git clone https://github.com/sabri-manai/xai-contestation-labelling.git
cd xai-contestation-labelling
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

Start the app with `.venv/bin/python -m streamlit run app/main.py` and open http://localhost:8501.

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

Your labels are saved to `labels/<your code>.csv` (code shown in the sidebar; no email in it) and
come back whenever you log in with the same email. Polish is authoritative; English is a translation.
Never commit `labels.db`.

**Already labelling?** `git pull`, restart, log in with the same email; nothing is lost. Episodes
with a yellow warning need the new "explanation request" field.

## Project lead

- Collect: `git pull && .venv/bin/python export_labels.py` → `../xai-contestation-framework/data/human_labels.csv`
  (prints agreement between labellers).
- Who is who: `.venv/bin/python -m app.sync alice@x.pl bob@y.pl` prints each email's code.
- Episode order: `data/queue_order.csv` (from `make_queue_order.py`); codebook changes: `coding_guide.md` §6.
