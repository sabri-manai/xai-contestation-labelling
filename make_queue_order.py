"""Fix the order in which the 250 episodes appear in the app. Run once; output is committed.

Positions 1-100 are the reliability block that every labeller codes first:
  - all 46 random_unflagged episodes (lexical-filter recall), and
  - 54 flagged episodes, drawn at random with proportional allocation over
    participant_group x explanation_format (largest-remainder rounding),
shuffled together so labellers cannot tell the two kinds apart by position.
Positions 101-250 are the remaining 150 flagged episodes in random order.

Uses only sample_batch and the group/format columns: no labels, no model scores.

    .venv/bin/python make_queue_order.py      # writes data/queue_order.csv
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

SEED = 20261031
N_BLOCK = 100
ROOT = Path(__file__).parent

eps = pd.read_csv(ROOT / "data" / "episodes_to_label.csv", keep_default_na=False)
rng = np.random.default_rng(SEED)

unflagged = eps[eps.sample_batch == "random_unflagged"]
flagged = eps[eps.sample_batch == "flagged"]
n_flagged = N_BLOCK - len(unflagged)

cells = flagged.groupby(["participant_group", "explanation_format"]).size()
quota = cells / cells.sum() * n_flagged
alloc = np.floor(quota).astype(int)
for cell in (quota - alloc).sort_values(ascending=False).index[: n_flagged - alloc.sum()]:
    alloc[cell] += 1

picked = []
for (g, f), k in alloc.items():
    pool = flagged[(flagged.participant_group == g) & (flagged.explanation_format == f)].episode_id.tolist()
    picked += list(rng.choice(pool, size=k, replace=False))

block = unflagged.episode_id.tolist() + picked
rng.shuffle(block)
rest = [e for e in flagged.episode_id if e not in set(picked)]
rng.shuffle(rest)

order = pd.DataFrame({"episode_id": block + rest, "queue_pos": range(1, len(eps) + 1)})
order["block"] = np.where(order.queue_pos <= N_BLOCK, "reliability_100", "rest")
assert order.episode_id.is_unique and len(order) == len(eps) == 250
order.to_csv(ROOT / "data" / "queue_order.csv", index=False)

chk = order.merge(eps, on="episode_id")
first = chk[chk.block == "reliability_100"]
print(f"wrote data/queue_order.csv (seed {SEED})")
print(first.sample_batch.value_counts().to_string())
print(pd.crosstab(first.participant_group, first.explanation_format).to_string())
