"""Join every coder's labels/<code>.csv into one file: data/human_labels.csv.

Usage:
    .venv/bin/python export_labels.py

One row per (coder, episode, version), so the history is kept; `is_latest` marks the row that
counts. Coders are named by the email they log in with. Nothing is adjudicated here: reconciling
disagreements is a separate step on top of this file.
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).parent
OUT = ROOT / "data" / "human_labels.csv"

# labels/<code>.csv -> coder (code = app/sync.py code_for(email))
CODERS = {
    "c_433b209090": "szymon.bobek@uj.edu.pl",
    "c_bf6244ebdc": "magdalena.kiszka@student.uj.edu.pl",
    "c_01534ba437": "maciej.szelazek@uj.edu.pl",
    "c_b59a2c33e1": "maria.j.tyrpa@student.uj.edu.pl",
}
LABELS = ["is_contestation", "explanation_request", "presence", "target",
          "interaction_act", "grounds", "expected_response", "notes"]


def main() -> None:
    frames = []
    for code, coder in CODERS.items():
        d = pd.read_csv(ROOT / "labels" / f"{code}.csv", dtype=str, keep_default_na=False)
        d["coder"] = coder
        frames.append(d)
    df = pd.concat(frames, ignore_index=True)

    order = pd.read_csv(ROOT / "data" / "queue_order.csv", dtype={"queue_pos": int})
    df = df.merge(order, on="episode_id", how="left")

    df["is_skipped"] = df["is_skipped"].isin(["1", "1.0"]).astype(int)
    df["version"] = df["version"].astype(int)
    df = df.sort_values(["coder", "episode_id", "version"])
    latest = (df[df.is_skipped == 0].groupby(["coder", "episode_id"]).version.max()
              .rename("latest").reset_index())
    df = df.merge(latest, on=["coder", "episode_id"], how="left")
    df["is_latest"] = ((df.is_skipped == 0) & (df.version == df.latest)).astype(int)
    # codebook v1.1 added explanation_request; rows saved before it have the field empty
    df["codebook"] = df.apply(
        lambda r: "" if r.is_skipped else ("v1.0" if r.explanation_request == "" else "v1.2"), axis=1)

    cols = (["coder", "episode_id", "block", "queue_pos", "version", "is_latest", "is_skipped",
             "created_at", "time_spent_s"] + LABELS + ["codebook"])
    df = df[cols].sort_values(["queue_pos", "coder", "version"])
    df.to_csv(OUT, index=False)

    cur = df[df.is_latest == 1]
    print(f"wrote {len(df)} rows ({len(cur)} current labels) to {OUT}")
    print(cur.groupby("coder").size().rename("episodes").to_string())
    k = cur.groupby("episode_id").coder.nunique().value_counts().sort_index()
    print("episodes by number of coders:\n" + k.rename("episodes").to_string())


if __name__ == "__main__":
    main()
