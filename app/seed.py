"""
Seed script — creates (or resets) the SQLite database from the provided CSVs.

Usage
-----
  python -m app.seed [--reset]

  --reset   drop and recreate all tables (destructive)
"""
import argparse
import json
import random
import sys
from pathlib import Path

import pandas as pd

# Make sure the app package is importable when run as a script
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from app.db import DB_PATH, get_conn, init_db, create_annotator, annotator_exists

DATA = ROOT / "data"

# Columns from episode CSV that we store (excludes sensitive ones)
EPISODE_COLS = [
    "episode_id", "transcript_id", "participant_group",
    "explanation_format", "explanation_theme", "speaker",
    "text_pl", "text_en", "context_pl", "context_en", "en_source",
]
GOLD_EXTRA_COLS = [
    "is_contestation", "presence", "target",
    "interaction_act", "grounds", "expected_response", "gold_role",
]

# How many calibration items to mix into each annotator's queue
# (roughly 1 in 10 of the work items they see)
CALIBRATION_RATIO = 0.10
# Each work episode must be seen by at least this many annotators
MIN_ANNOTATORS_PER_EPISODE = 2


def _drop_tables(conn):
    conn.executescript("""
        DROP TABLE IF EXISTS adjudications;
        DROP TABLE IF EXISTS labels;
        DROP TABLE IF EXISTS assignments;
        DROP TABLE IF EXISTS episodes;
        DROP TABLE IF EXISTS annotators;
    """)


def load_episodes():
    """Return a combined DataFrame of work + gold episodes."""
    work = pd.read_csv(DATA / "episodes_to_label.csv", dtype=str).fillna("")
    gold = pd.read_csv(DATA / "gold_standard.csv", dtype=str).fillna("")

    work_rows = work[EPISODE_COLS].copy()
    for c in GOLD_EXTRA_COLS:
        work_rows[c] = ""

    gold_rows = gold[EPISODE_COLS + GOLD_EXTRA_COLS].copy()

    return pd.concat([work_rows, gold_rows], ignore_index=True), work, gold


def assign_episodes(annotator_ids: list[int], work_episode_ids: list[str],
                    calibration_episode_ids: list[str], rng: random.Random):
    """
    Assign work episodes to annotators ensuring each gets MIN_ANNOTATORS_PER_EPISODE
    coverage, and mix calibration items in at CALIBRATION_RATIO.

    Returns list of (annotator_id, episode_id, is_calibration) tuples.
    """
    n_ann = len(annotator_ids)
    if n_ann == 0:
        return []

    assignments = []

    # Round-robin work assignment so every episode gets MIN_ANNOTATORS_PER_EPISODE
    shuffled_work = work_episode_ids[:]
    rng.shuffle(shuffled_work)

    ep_ann_count: dict[str, int] = {ep: 0 for ep in shuffled_work}
    # Each annotator gets a slot list; fill round-robin
    ann_work: dict[int, list[str]] = {a: [] for a in annotator_ids}

    idx = 0
    while any(v < MIN_ANNOTATORS_PER_EPISODE for v in ep_ann_count.values()):
        for ep in shuffled_work:
            if ep_ann_count[ep] < MIN_ANNOTATORS_PER_EPISODE:
                ann_id = annotator_ids[idx % n_ann]
                if ep not in ann_work[ann_id]:
                    ann_work[ann_id].append(ep)
                    ep_ann_count[ep] += 1
                    idx += 1

    # Interleave calibration items into each annotator's queue
    for ann_id in annotator_ids:
        work_list = ann_work[ann_id][:]
        n_cal = max(1, round(len(work_list) * CALIBRATION_RATIO))
        cal_sample = rng.sample(calibration_episode_ids, min(n_cal, len(calibration_episode_ids)))

        # Interleave: insert one calibration item roughly every 10 work items
        combined = []
        cal_iter = iter(cal_sample)
        for i, ep in enumerate(work_list):
            combined.append((ann_id, ep, 0))
            if (i + 1) % 10 == 0:
                try:
                    combined.append((ann_id, next(cal_iter), 1))
                except StopIteration:
                    pass
        # Append any leftover calibration items
        for ep in cal_iter:
            combined.append((ann_id, ep, 1))

        assignments.extend(combined)

    return assignments


def seed(reset: bool = False, annotators: list[dict] | None = None):
    """
    annotators: list of dicts with keys username, password, role.
    If None, seeds two default annotators for local testing.
    """
    if reset and DB_PATH.exists():
        DB_PATH.unlink()

    init_db()

    all_ep, work_df, gold_df = load_episodes()

    # Upsert episodes
    with get_conn() as conn:
        for _, row in all_ep.iterrows():
            cols = list(row.index)
            vals = [row[c] if row[c] != "" else None for c in cols]
            placeholders = ",".join("?" * len(cols))
            col_names = ",".join(cols)
            conn.execute(
                f"INSERT OR REPLACE INTO episodes ({col_names}) VALUES ({placeholders})",
                vals,
            )

    print(f"  Loaded {len(work_df)} work episodes, {len(gold_df)} gold episodes.")

    # Create annotators
    if annotators is None:
        annotators = [
            {"username": "alice", "password": "alice123", "role": "annotator"},
            {"username": "bob",   "password": "bob123",   "role": "annotator"},
            {"username": "admin", "password": "admin123",  "role": "adjudicator"},
        ]

    created_ids = []
    for ann in annotators:
        if not annotator_exists(ann["username"]):
            aid = create_annotator(ann["username"], ann["password"], ann["role"])
            print(f"  Created annotator: {ann['username']} ({ann['role']})")
        else:
            with get_conn() as conn:
                row = conn.execute(
                    "SELECT id FROM annotators WHERE username=?", (ann["username"],)
                ).fetchone()
                aid = row["id"]
            print(f"  Annotator already exists: {ann['username']}")
        if ann["role"] == "annotator":
            created_ids.append(aid)

    # Assignments
    work_ids = work_df["episode_id"].tolist()
    cal_ids = gold_df[gold_df["gold_role"] == "calibration"]["episode_id"].tolist()

    rng = random.Random(42)
    assignment_rows = assign_episodes(created_ids, work_ids, cal_ids, rng)

    with get_conn() as conn:
        conn.executemany(
            "INSERT OR IGNORE INTO assignments (annotator_id, episode_id, is_calibration) VALUES (?,?,?)",
            assignment_rows,
        )

    print(f"  Created {len(assignment_rows)} assignments across {len(created_ids)} annotators.")
    print(f"  Database at: {DB_PATH}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true",
                        help="Drop and recreate all tables (destructive)")
    args = parser.parse_args()
    seed(reset=args.reset)
    print("Done.")
