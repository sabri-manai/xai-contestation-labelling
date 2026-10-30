"""Export human labels (labels/<email>.csv files + local labels.db) to CSV for the framework repo.

Usage:
    .venv/bin/python export_labels.py [--out PATH] [--silver PATH]

Writes the latest non-skipped label per (annotator, episode), one row each, and prints
per-annotator counts, human–human agreement on the overlap, and agreement with the Jev
silver labels if a silver CSV is given. Run it whenever the coders have saved more work;
the framework reads the CSV, never the database.
"""
from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).parent
DEFAULT_OUT = ROOT.parent / "xai-contestation-framework" / "data" / "human_labels.csv"
DEFAULT_SILVER = ROOT.parent / "xai-contestation-framework" / "data" / "silver_250.csv"
LABEL_COLS = ["is_contestation", "explanation_request", "presence", "target",
              "interaction_act", "grounds", "expected_response", "notes"]


def kappa(a: pd.Series, b: pd.Series) -> float:
    from sklearn.metrics import cohen_kappa_score
    return cohen_kappa_score(a, b) if len(a) > 1 and a.nunique() + b.nunique() > 2 else float("nan")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--silver", type=Path, default=DEFAULT_SILVER)
    args = ap.parse_args()

    # Sources: every annotator's committed file labels/<email>.csv, plus the local labels.db
    # (labels saved here but not yet written to a file). Same label in both → counted once.
    # Annotators are identified by code only (app/sync.py); emails never reach the output.
    from app.sync import code_for
    frames = []
    for f in sorted((ROOT / "labels").glob("c_*.csv")):
        d = pd.read_csv(f, keep_default_na=False, dtype=str)
        frames.append(d.rename(columns={"annotator_code": "annotator"}))
    db_path = ROOT / "labels.db"
    if db_path.exists():
        with sqlite3.connect(db_path) as conn:
            d = pd.read_sql_query(
                """SELECT lower(a.username) AS annotator, l.episode_id, l.version, l.created_at,
                          l.time_spent_s, l.is_skipped, l.is_contestation, l.explanation_request,
                          l.presence, l.target, l.interaction_act, l.grounds, l.expected_response, l.notes
                   FROM labels l JOIN annotators a ON a.id = l.annotator_id""",
                conn,
            ).astype(object).where(lambda x: x.notna(), "").astype(str)
        d["annotator"] = d["annotator"].map(code_for)
        frames.append(d)
    df = pd.concat(frames, ignore_index=True)
    df = df[df["is_skipped"].astype(str).isin(["0", "0.0", ""])]
    df = (df.drop_duplicates(["annotator", "episode_id", "created_at"])
            .sort_values(["annotator", "episode_id", "created_at"])
            .drop_duplicates(["annotator", "episode_id"], keep="last")
            .drop(columns=["is_skipped"]))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out, index=False)
    print(f"wrote {len(df)} labels to {args.out}")
    print(df.groupby("annotator").size().rename("labels").to_string())

    coders = [c for c in df.annotator.unique()]
    for i, c1 in enumerate(coders):
        for c2 in coders[i + 1:]:
            m = df[df.annotator == c1].merge(df[df.annotator == c2], on="episode_id", suffixes=("_1", "_2"))
            if len(m):
                print(f"{c1} vs {c2}: n={len(m)} "
                      f"contestation acc={(m.is_contestation_1 == m.is_contestation_2).mean():.2f} "
                      f"kappa={kappa(m.is_contestation_1, m.is_contestation_2):.2f} | "
                      f"request acc={(m.explanation_request_1 == m.explanation_request_2).mean():.2f} "
                      f"kappa={kappa(m.explanation_request_1, m.explanation_request_2):.2f}")

    if args.silver.exists():
        s = pd.read_csv(args.silver, keep_default_na=False)
        for c in coders:
            m = df[df.annotator == c].merge(s, on="episode_id", suffixes=("_h", "_s"))
            if len(m):
                print(f"{c} vs silver (Jev): n={len(m)} "
                      f"contestation kappa={kappa(m.is_contestation_h, m.is_contestation_s):.2f} "
                      f"request kappa={kappa(m.explanation_request_h, m.explanation_request_s):.2f}")


if __name__ == "__main__":
    main()
