"""
Database layer — SQLite via the stdlib sqlite3 module.

Tables
------
annotators       id, username, password_hash, role ('annotator'|'adjudicator'), created_at
episodes         episode_id, + all non-sensitive episode columns
assignments      annotator_id, episode_id, is_calibration, completed_at
labels           id, annotator_id, episode_id, version, is_contestation, presence,
                 target, interaction_act, grounds, expected_response, notes,
                 is_skipped, time_spent_s, created_at
adjudications    id, episode_id, is_contestation, presence, target, interaction_act,
                 grounds, expected_response, adjudicator_id, reason,
                 disagreement_type, method ('auto'|'manual'), created_at,
                 source_label_ids (json list)
"""

import hashlib
import json
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "labels.db"


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

SCHEMA = """
CREATE TABLE IF NOT EXISTS annotators (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role          TEXT NOT NULL DEFAULT 'annotator',
    created_at    TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS episodes (
    episode_id          TEXT PRIMARY KEY,
    transcript_id       TEXT,
    participant_group   TEXT,
    explanation_format  TEXT,
    explanation_theme   TEXT,
    speaker             TEXT,
    text_pl             TEXT,
    text_en             TEXT,
    context_pl          TEXT,
    context_en          TEXT,
    en_source           TEXT,
    -- gold-only columns (NULL for episodes_to_label)
    is_contestation     TEXT,
    presence            TEXT,
    target              TEXT,
    interaction_act     TEXT,
    grounds             TEXT,
    expected_response   TEXT,
    gold_role           TEXT   -- 'example' | 'calibration' | NULL
);

CREATE TABLE IF NOT EXISTS assignments (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    annotator_id    INTEGER NOT NULL REFERENCES annotators(id),
    episode_id      TEXT    NOT NULL REFERENCES episodes(episode_id),
    is_calibration  INTEGER NOT NULL DEFAULT 0,
    completed_at    TEXT,
    UNIQUE(annotator_id, episode_id)
);

CREATE TABLE IF NOT EXISTS labels (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    annotator_id      INTEGER NOT NULL REFERENCES annotators(id),
    episode_id        TEXT    NOT NULL REFERENCES episodes(episode_id),
    version           INTEGER NOT NULL DEFAULT 1,
    is_contestation   TEXT,
    presence          TEXT,
    target            TEXT,
    interaction_act   TEXT,
    grounds           TEXT,
    expected_response TEXT,
    notes             TEXT,
    is_skipped        INTEGER NOT NULL DEFAULT 0,
    time_spent_s      REAL,
    created_at        TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS adjudications (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    episode_id        TEXT    NOT NULL REFERENCES episodes(episode_id),
    is_contestation   TEXT,
    presence          TEXT,
    target            TEXT,
    interaction_act   TEXT,
    grounds           TEXT,
    expected_response TEXT,
    adjudicator_id    INTEGER REFERENCES annotators(id),
    reason            TEXT,
    disagreement_type TEXT,   -- 'presence' | 'structured' | 'both' | NULL (auto)
    method            TEXT    NOT NULL DEFAULT 'manual',  -- 'auto' | 'manual'
    source_label_ids  TEXT,   -- JSON list of label.id values used
    created_at        TEXT    NOT NULL DEFAULT (datetime('now')),
    UNIQUE(episode_id)
);

CREATE INDEX IF NOT EXISTS idx_labels_episode   ON labels(episode_id);
CREATE INDEX IF NOT EXISTS idx_labels_annotator ON labels(annotator_id);
CREATE INDEX IF NOT EXISTS idx_assignments_ann  ON assignments(annotator_id);
"""


def init_db():
    with get_conn() as conn:
        conn.executescript(SCHEMA)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


# ---------------------------------------------------------------------------
# Annotator operations
# ---------------------------------------------------------------------------

def create_annotator(username: str, password: str, role: str = "annotator") -> int:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO annotators (username, password_hash, role) VALUES (?,?,?)",
            (username, _hash(password), role),
        )
        return cur.lastrowid


def verify_annotator(username: str, password: str):
    """Return the annotator row or None."""
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM annotators WHERE username=? AND password_hash=?",
            (username, _hash(password)),
        ).fetchone()
    return dict(row) if row else None


def get_all_annotators():
    with get_conn() as conn:
        return [dict(r) for r in conn.execute("SELECT * FROM annotators").fetchall()]


def annotator_exists(username: str) -> bool:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT 1 FROM annotators WHERE username=?", (username,)
        ).fetchone()
    return row is not None


def get_or_create_annotator(identifier: str) -> int:
    """Return the annotator id for the given free-text identifier, creating if needed."""
    identifier = identifier.strip()
    with get_conn() as conn:
        row = conn.execute(
            "SELECT id FROM annotators WHERE username=?", (identifier,)
        ).fetchone()
        if row:
            return row["id"]
        cur = conn.execute(
            "INSERT INTO annotators (username, password_hash, role) VALUES (?,?,?)",
            (identifier, "", "annotator"),
        )
        return cur.lastrowid


def get_all_work_episode_ids() -> list[str]:
    """All episode IDs that are not gold (gold_role IS NULL or empty)."""
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT episode_id FROM episodes WHERE (gold_role IS NULL OR gold_role = '') ORDER BY episode_id"
        ).fetchall()
    return [r["episode_id"] for r in rows]


def get_labels_by_annotator(annotator_id: int) -> set[str]:
    """Set of episode_ids this annotator has already labelled (non-skipped latest)."""
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT DISTINCT episode_id FROM labels
            WHERE annotator_id=? AND is_skipped=0
            """,
            (annotator_id,),
        ).fetchall()
    return {r["episode_id"] for r in rows}


# ---------------------------------------------------------------------------
# Episode / assignment operations
# ---------------------------------------------------------------------------

def get_episode(episode_id: str):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM episodes WHERE episode_id=?", (episode_id,)
        ).fetchone()
    return dict(row) if row else None


def get_next_episode_for_annotator(annotator_id: int):
    """Return the next incomplete, non-skipped assignment for this annotator."""
    with get_conn() as conn:
        row = conn.execute(
            """
            SELECT a.episode_id FROM assignments a
            LEFT JOIN (
                SELECT episode_id, MAX(version) AS mv
                FROM labels WHERE annotator_id=?
                GROUP BY episode_id
            ) l ON a.episode_id = l.episode_id
            WHERE a.annotator_id=?
              AND a.completed_at IS NULL
            ORDER BY a.id
            LIMIT 1
            """,
            (annotator_id, annotator_id),
        ).fetchone()
    return row["episode_id"] if row else None


def get_annotator_queue(annotator_id: int):
    """All assignments (with completion status) for an annotator."""
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT a.episode_id, a.is_calibration, a.completed_at,
                   e.participant_group, e.explanation_format
            FROM assignments a
            JOIN episodes e ON a.episode_id = e.episode_id
            WHERE a.annotator_id=?
            ORDER BY a.id
            """,
            (annotator_id,),
        ).fetchall()
    return [dict(r) for r in rows]


def count_assignments(annotator_id: int):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT COUNT(*) AS total, SUM(CASE WHEN completed_at IS NOT NULL THEN 1 ELSE 0 END) AS done "
            "FROM assignments WHERE annotator_id=?",
            (annotator_id,),
        ).fetchone()
    return dict(row)


# ---------------------------------------------------------------------------
# Label operations
# ---------------------------------------------------------------------------

def save_label(
    annotator_id: int,
    episode_id: str,
    is_contestation: str,
    presence: str | None,
    target: str | None,
    interaction_act: str | None,
    grounds: str | None,
    expected_response: str | None,
    notes: str | None,
    is_skipped: bool = False,
    time_spent_s: float | None = None,
):
    with get_conn() as conn:
        # Compute next version
        row = conn.execute(
            "SELECT MAX(version) AS mv FROM labels WHERE annotator_id=? AND episode_id=?",
            (annotator_id, episode_id),
        ).fetchone()
        version = (row["mv"] or 0) + 1

        lid = conn.execute(
            """INSERT INTO labels
               (annotator_id, episode_id, version, is_contestation, presence,
                target, interaction_act, grounds, expected_response,
                notes, is_skipped, time_spent_s)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                annotator_id, episode_id, version,
                is_contestation, presence, target,
                interaction_act, grounds, expected_response,
                notes, int(is_skipped), time_spent_s,
            ),
        ).lastrowid

        # Mark assignment complete (only if not a skip)
        if not is_skipped:
            conn.execute(
                "UPDATE assignments SET completed_at=datetime('now') "
                "WHERE annotator_id=? AND episode_id=?",
                (annotator_id, episode_id),
            )
        return lid


def get_latest_label(annotator_id: int, episode_id: str):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM labels WHERE annotator_id=? AND episode_id=? ORDER BY version DESC LIMIT 1",
            (annotator_id, episode_id),
        ).fetchone()
    return dict(row) if row else None


def get_all_labels_for_episode(episode_id: str):
    """All non-skip latest-version labels from every annotator for one episode."""
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT l.* FROM labels l
            INNER JOIN (
                SELECT annotator_id, MAX(version) AS mv
                FROM labels WHERE episode_id=? AND is_skipped=0
                GROUP BY annotator_id
            ) latest ON l.annotator_id=latest.annotator_id AND l.version=latest.mv
            WHERE l.episode_id=?
            """,
            (episode_id, episode_id),
        ).fetchall()
    return [dict(r) for r in rows]


def get_adjudication(episode_id: str):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM adjudications WHERE episode_id=?", (episode_id,)
        ).fetchone()
    return dict(row) if row else None


def save_adjudication(
    episode_id: str,
    is_contestation: str,
    presence: str | None,
    target: str | None,
    interaction_act: str | None,
    grounds: str | None,
    expected_response: str | None,
    adjudicator_id: int | None,
    reason: str | None,
    disagreement_type: str | None,
    method: str,
    source_label_ids: list[int],
):
    with get_conn() as conn:
        conn.execute(
            """INSERT OR REPLACE INTO adjudications
               (episode_id, is_contestation, presence, target, interaction_act,
                grounds, expected_response, adjudicator_id, reason,
                disagreement_type, method, source_label_ids)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                episode_id, is_contestation, presence, target,
                interaction_act, grounds, expected_response,
                adjudicator_id, reason, disagreement_type, method,
                json.dumps(source_label_ids),
            ),
        )
