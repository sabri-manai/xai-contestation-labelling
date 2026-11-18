"""Disagreement round: each coder sees the episodes where their label differs from another coder's
and may change any of their values, or keep them and write a note saying why.

Round 1 (the basis): data/human_labels_merged.csv, a frozen snapshot of every coder's labels with the
structure dimensions merged by the coders' own OR-merges (data/taxonomy_merges_v1.2.json, a copy of the
framework's file). The merge map is re-applied here, so rows the snapshot left unmerged are compared at
the merged level too; applying it to an already merged value changes nothing.

What counts as a disagreement, per episode and coder, over each coder's latest label in the basis:
  - both gates (contestation, explanation request);
  - target, interaction act, grounds, expected response at the merged level, among the coders who
    said contestation = yes. Presence is shown but not compared (no aggregation level uses it).
Episodes with an unclear transcript are left out (they are excluded from every number).

Round 2 (the answers): discussion/<code>.csv, one file per coder, append-only, shared through git like
labels/. Nothing is written to labels/: those files stay the independent round-1 labels that agreement
is computed on. Each row holds the decision (change: the fields in changed_fields differ from the round-1
label; keep: the round-1 label stands), the note, and the coder's full label after reviewing (dimensions
in merged terms).

Disagreement kinds, for one coder on one field:
  minority  a strict majority exists and the coder is not in it
  tie       no strict majority (1-1, 2-2, 2-1-1, ...)
  majority  the coder is in the majority, someone else differs
"""
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path

import pandas as pd

from app.sync import code_for

ROOT = Path(__file__).parent.parent
BASIS = ROOT / "data" / "human_labels_merged.csv"
MERGES = ROOT / "data" / "taxonomy_merges_v1.2.json"
TAXONOMY = ROOT / "taxonomy.json"
QUEUE = ROOT / "data" / "queue_order.csv"
DISC_DIR = ROOT / "discussion"

GATES = ["is_contestation", "explanation_request"]
DIMS = ["target", "interaction_act", "grounds", "expected_response"]
FIELDS = GATES + ["presence"] + DIMS     # a coder's position
COMPARED = GATES + DIMS                  # what makes a disagreement
FIELD_NAMES = {"is_contestation": "Contestation", "explanation_request": "Explanation request",
               "presence": "Presence", "target": "Target", "interaction_act": "Interaction act",
               "grounds": "Grounds", "expected_response": "Expected response"}
KINDS = {"minority": "You differ from the majority", "tie": "No majority",
         "majority": "Others differ from you"}
COLS = ["annotator_code", "episode_id", "version", "created_at", "decision", "changed_fields", *FIELDS,
        "note", "level", "basis", "others_answers_seen", "time_spent_s"]


# ----------------------------------------------------------------------------- vocabulary
@lru_cache(maxsize=1)
def _fine_values() -> dict[str, list[str]]:
    t = json.loads(TAXONOMY.read_text(encoding="utf-8"))
    return {d["name"]: d["values"] for d in t["dimensions"] if isinstance(d.get("values"), list)}


@lru_cache(maxsize=1)
def merge_map() -> dict[str, dict[str, str]]:
    """dim -> {value: merged value}. Fine values outside any merge, and merged names, map to themselves."""
    groups = json.loads(MERGES.read_text(encoding="utf-8"))["merges"]
    out = {}
    for d in DIMS:
        m = {f: f for f in _fine_values()[d]}
        for name, g in groups.get(d, {}).items():
            m.update({f: name for f in g["fine"]})
            m[name] = name
        out[d] = m
    return out


def merged_values(dim: str) -> list[str]:
    """Options at the merged level, in codebook order."""
    out = []
    for f in _fine_values()[dim]:
        v = merge_map()[dim][f]
        if v not in out:
            out.append(v)
    return out


# ----------------------------------------------------------------------------- round 1
def basis_id() -> str:
    return f"{BASIS.name}@{hashlib.sha256(BASIS.read_bytes()).hexdigest()[:10]}"


def load_basis() -> pd.DataFrame:
    """Latest label of every coder on every episode, one row per (code, episode), merged dimensions."""
    return _basis(BASIS.stat().st_mtime_ns)


@lru_cache(maxsize=2)
def _basis(_mtime: int) -> pd.DataFrame:
    d = pd.read_csv(BASIS, dtype=str, keep_default_na=False)
    d = d[(d.is_latest == "1") & (d.is_skipped != "1")].copy()
    q = pd.read_csv(QUEUE, dtype=str)
    d = d[~d.episode_id.isin(set(q.episode_id[q.block == "excluded_unclear_transcript"]))]
    d["code"] = d.coder.map(code_for)      # emails stop here; only codes leave this function
    for dim, m in merge_map().items():
        d[dim] = d[dim].map(lambda v, m=m: m.get(v, v))
    d["queue_pos"] = pd.to_numeric(d.queue_pos, errors="coerce")
    d = d[["code", "episode_id", "queue_pos", *FIELDS, "notes"]].reset_index(drop=True)
    assert not d.duplicated(["code", "episode_id"]).any(), "basis has two latest labels for one coder"
    return d


def basis_positions(episode_id: str) -> dict[str, dict]:
    """code -> {field: value, 'notes': ...} for every coder who labelled the episode in round 1."""
    b = load_basis()
    return {r["code"]: {f: r[f] for f in [*FIELDS, "notes"]}
            for r in b[b.episode_id == episode_id].to_dict("records")}


# ----------------------------------------------------------------------------- comparison
def _compared_values(field: str, positions: list[dict]) -> list[str]:
    if field in DIMS:
        positions = [p for p in positions if p["is_contestation"] == "yes"]
    return [p[field] for p in positions if p[field]]


def _kind(mine: str, values: list[str]) -> str | None:
    if not mine or len(values) < 2 or len(set(values)) == 1:
        return None
    (top, k), *rest = Counter(values).most_common()
    if (rest and rest[0][1] == k) or 2 * k <= len(values):
        return "tie"
    return "majority" if mine == top else "minority"


def kinds_for(code: str, positions: dict[str, dict]) -> dict[str, str]:
    """field -> kind of disagreement for this coder; fields without one are absent."""
    me = positions[code]
    out = {}
    for f in COMPARED:
        if f in DIMS and me["is_contestation"] != "yes":
            continue
        k = _kind(me[f], _compared_values(f, list(positions.values())))
        if k:
            out[f] = k
    return out


def _worst(kinds) -> str | None:
    present = set(kinds)
    return next((k for k in KINDS if k in present), None)


def _rank(kinds: dict[str, str]) -> int:
    g = _worst(kinds[f] for f in GATES if f in kinds)
    d = _worst(kinds[f] for f in DIMS if f in kinds)
    if g == "minority":
        return 0
    if g == "tie":
        return 1
    if d == "minority":
        return 2
    if d == "tie":
        return 3
    return 4


def items_for(code: str) -> list[dict]:
    """Episodes this coder labelled in round 1 where some coder differs, most urgent first:
    you alone on a gate, gate tie, you alone on a dimension, dimension tie, then others differ from you."""
    if not BASIS.exists():
        return []
    return _items(code, BASIS.stat().st_mtime_ns)


@lru_cache(maxsize=8)
def _items(code: str, _mtime: int) -> list[dict]:
    b = load_basis()
    mine = b[b.code == code].set_index("episode_id").queue_pos.to_dict()
    out = []
    for ep, qpos in mine.items():
        kinds = kinds_for(code, basis_positions(ep))
        if kinds:
            out.append({"episode_id": ep, "queue_pos": None if pd.isna(qpos) else int(qpos),
                        "kinds": kinds, "kind": _worst(kinds.values()), "rank": _rank(kinds)})
    out.sort(key=lambda it: (it["rank"], it["queue_pos"] or 10**6, it["episode_id"]))
    return out


def in_discussion(code: str, episode_id: str) -> bool:
    return any(it["episode_id"] == episode_id for it in items_for(code))


# ----------------------------------------------------------------------------- round 2
def answers_file(code: str) -> Path:
    return DISC_DIR / f"{code}.csv"


def read_answers(code: str) -> list[dict]:
    p = answers_file(code)
    if not p.exists():
        return []
    with open(p, newline="", encoding="utf-8") as f:
        return [r for r in csv.DictReader(f) if r.get("annotator_code") == code]


def latest_answers(code: str) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for r in read_answers(code):
        cur = out.get(r["episode_id"])
        if cur is None or int(r["version"]) >= int(cur["version"]):
            out[r["episode_id"]] = r
    return out


def current_position(round1: dict, answer: dict | None) -> dict:
    return {f: (answer if answer else round1)[f] or "" for f in FIELDS}


def save_answer(code: str, episode_id: str, position: dict, round1: dict, note: str,
                others_answers_seen: int, time_spent_s: float | None) -> dict:
    changed = [f for f in FIELDS if (position.get(f) or "") != (round1.get(f) or "")]
    rows = read_answers(code)
    row = {"annotator_code": code, "episode_id": episode_id,
           "version": 1 + sum(r["episode_id"] == episode_id for r in rows),
           "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
           "decision": "change" if changed else "keep", "changed_fields": ";".join(changed),
           **{f: position.get(f) or "" for f in FIELDS}, "note": note.strip(),
           "level": "merged", "basis": basis_id(), "others_answers_seen": others_answers_seen,
           "time_spent_s": "" if time_spent_s is None else round(time_spent_s, 1)}
    DISC_DIR.mkdir(exist_ok=True)
    path = answers_file(code)
    tmp = path.with_suffix(".csv.tmp")
    with open(tmp, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS, restval="", extrasaction="ignore")
        w.writeheader()
        w.writerows([*rows, row])
    tmp.replace(path)
    return row
