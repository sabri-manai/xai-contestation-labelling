"""Per-annotator label files, so labels travel through git without conflicts or emails.

Each annotator owns one file, labels/<code>.csv, holding every label they saved (all versions).
The code is a salted SHA-256 of the lowercased email, shortened: the same email gives the same
code on every machine, with nothing for the labeller to set up. Emails stay in the local database;
the committed CSV carries only the code.

Privacy level: the salt is in this (public) repository, so the code keeps emails out of the files
and out of search, but anyone who already knows a labeller's email can check whether a file is
theirs. If that is not acceptable, make the repository private.

- Email → code list: `labelers_private.csv` (gitignored), appended on every login on this machine;
  `python -m app.sync alice@x.pl bob@y.pl` prints the code for any email.
- On login: import_file() adds rows from the annotator's CSV that the local database lacks (labels
  made on another machine and pulled from git), then write_file() rewrites the CSV from the
  database, so labels made before this feature existed land in the file too.
- After every save or skip: write_file().

A row is identified by (episode_id, created_at); version numbers are renumbered by created_at
after an import so the latest label is always the most recent one.
"""
from __future__ import annotations

import csv
import hashlib
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from app.db import get_conn

ROOT = Path(__file__).parent.parent
LABELS_DIR = ROOT / "labels"
PRIVATE_MAP = ROOT / "labelers_private.csv"
SALT = "xai-contestation-labelling/v1"   # changing this changes every code; don't
COLS = ["annotator_code", "episode_id", "version", "created_at", "is_skipped", "time_spent_s",
        "is_contestation", "explanation_request", "presence", "target", "interaction_act",
        "grounds", "expected_response", "notes"]


def normalize_email(email: str) -> str:
    return email.strip().lower()


def code_for(email: str) -> str:
    digest = hashlib.sha256(f"{SALT}:{normalize_email(email)}".encode()).hexdigest()
    return f"c_{digest[:10]}"


def file_for(email: str) -> Path:
    return LABELS_DIR / f"{code_for(email)}.csv"


def _legacy_file(email: str) -> Path:
    """Email-named file from the short-lived pre-code version, if one exists locally."""
    return LABELS_DIR / f"{re.sub(r'[^a-z0-9@._+-]', '_', normalize_email(email))}.csv"


def remember(email: str) -> None:
    code = code_for(email)
    if PRIVATE_MAP.exists() and any(line.split(",")[1:2] == [code] for line in PRIVATE_MAP.read_text().splitlines()):
        return
    new = not PRIVATE_MAP.exists()
    with open(PRIVATE_MAP, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["email", "code", "first_seen_utc"])
        w.writerow([normalize_email(email), code, datetime.now(timezone.utc).isoformat(timespec="seconds")])


def write_file(annotator_id: int, email: str) -> Path:
    with get_conn() as conn:
        rows = conn.execute(
            f"SELECT {', '.join(COLS[1:])} FROM labels WHERE annotator_id=? ORDER BY episode_id, version",
            (annotator_id,),
        ).fetchall()
    path = file_for(email)
    if not rows and not path.exists():
        return path
    LABELS_DIR.mkdir(exist_ok=True)
    tmp = path.with_suffix(".csv.tmp")
    with open(tmp, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(COLS)
        code = code_for(email)
        for r in rows:
            w.writerow([code, *["" if r[c] is None else r[c] for c in COLS[1:]]])
    tmp.replace(path)
    return path


def _read(path: Path, owner: str, column: str) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        return [r for r in csv.DictReader(f) if r.get(column, "").strip().lower() == owner]


def import_file(annotator_id: int, email: str) -> int:
    rows = []
    if file_for(email).exists():
        rows += _read(file_for(email), code_for(email), "annotator_code")
    legacy = _legacy_file(email)
    if legacy.exists():
        rows += _read(legacy, normalize_email(email), "annotator_email")
    # A label is the same label when its time *and* content match: two different saves within
    # one second are both kept. Version numbers are not part of the identity (they get renumbered).
    content = ["episode_id", "created_at", "is_skipped", *COLS[6:]]
    ident = lambda r: tuple(str(r[c] if r[c] is not None else "").replace(".0", "") if c == "is_skipped"
                            else ("" if r[c] is None else str(r[c])) for c in content)
    added = 0
    with get_conn() as conn:
        known = {ident(dict(r)) for r in conn.execute(
            f"SELECT {', '.join(content)} FROM labels WHERE annotator_id=?", (annotator_id,))}
        episodes = {r["episode_id"] for r in conn.execute("SELECT episode_id FROM episodes")}
        touched = set()
        for r in rows:
            r = {c: r.get(c, "") for c in content} | {k: v for k, v in r.items() if k not in content}
            key = ident(r)
            if key in known or r["episode_id"] not in episodes:
                continue
            known.add(key)
            nullable = lambda c: r.get(c) or None
            conn.execute(
                """INSERT INTO labels (annotator_id, episode_id, version, is_contestation, explanation_request,
                       presence, target, interaction_act, grounds, expected_response, notes,
                       is_skipped, time_spent_s, created_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (annotator_id, r["episode_id"], 0, nullable("is_contestation"), nullable("explanation_request"),
                 nullable("presence"), nullable("target"), nullable("interaction_act"), nullable("grounds"),
                 nullable("expected_response"), nullable("notes"), int(r.get("is_skipped") or 0),
                 float(r["time_spent_s"]) if r.get("time_spent_s") else None, r["created_at"]),
            )
            if not int(r.get("is_skipped") or 0):
                conn.execute(
                    "UPDATE assignments SET completed_at=COALESCE(completed_at, ?) WHERE annotator_id=? AND episode_id=?",
                    (r["created_at"], annotator_id, r["episode_id"]),
                )
            touched.add(r["episode_id"])
            added += 1
        for ep in touched:   # versions follow time order, so the latest label is the newest one
            ids = [x["id"] for x in conn.execute(
                "SELECT id FROM labels WHERE annotator_id=? AND episode_id=? ORDER BY created_at, id",
                (annotator_id, ep))]
            for v, lid in enumerate(ids, start=1):
                conn.execute("UPDATE labels SET version=? WHERE id=?", (v, lid))
    return added


def sync(annotator_id: int, email: str) -> int:
    """Login-time sync. Returns the number of labels restored from file."""
    remember(email)
    added = import_file(annotator_id, email)
    write_file(annotator_id, email)
    legacy = _legacy_file(email)
    if legacy.exists():   # imported; keep it out of git (it names the email) but never delete it
        legacy.rename(legacy.with_name(legacy.name + ".migrated"))
    return added


if __name__ == "__main__":
    if not sys.argv[1:]:
        sys.exit("usage: python -m app.sync EMAIL [EMAIL ...]")
    for e in sys.argv[1:]:
        print(f"{normalize_email(e)},{code_for(e)}")
