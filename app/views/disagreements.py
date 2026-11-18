"""Disagreements screen: one episode at a time. A table with your label (one selector per field) next to
the other coders' labels; change any value or keep yours, then save. Saved to discussion/<code>.csv,
never to labels/. Logic and file format: app/discussion.py.
"""
from __future__ import annotations

import html
import sys
import time
from pathlib import Path

_ROOT = Path(__file__).parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st

from app import discussion as D
from app.db import get_episode
from app.sync import code_for
from app.views.label import _context_html

OPTIONS = {"is_contestation": ["yes", "no"], "explanation_request": ["yes", "no"],
           "presence": ["explicit", "implicit", "ambiguous"]}
DIFFERS = "background:rgba(240,173,78,0.28);"
SAME = "background:rgba(92,184,92,0.18);"


def render():
    email = st.session_state.get("identifier")
    if not email:
        st.info("Enter your email in the sidebar to begin.")
        return
    st.title("Disagreements")
    if not D.BASIS.exists():
        st.warning(f"`data/{D.BASIS.name}` is missing. Run `git pull` and restart the app.")
        return
    me = code_for(email)
    basis = D.load_basis()
    answers = {c: D.latest_answers(c) for c in set(basis.code)}
    ids = [it["episode_id"] for it in D.items_for(me)]
    if not ids:
        st.success("No disagreements for you.")
        return

    done = [e for e in ids if e in answers[me]]
    st.progress(len(done) / len(ids),
                text=f"**{len(ids)}** disagreements in your **{int((basis.code == me).sum())}** labels · "
                     f"**{len(done)}** of {len(ids)} done")

    if "_disc_next" in st.session_state:
        st.session_state.disc_sel = st.session_state.pop("_disc_next")
    if st.session_state.get("disc_sel") not in ids:
        st.session_state.disc_sel = next((e for e in ids if e not in done), ids[0])
    ep_id = st.selectbox("Episode", ids, key="disc_sel", label_visibility="collapsed",
                         format_func=lambda e: f"{'✓ ' if e in done else ''}{e}")
    if st.session_state.get("disc_start_ep") != ep_id:
        st.session_state.disc_start_ep, st.session_state.disc_start_time = ep_id, time.time()

    col_text, col_form = st.columns([4, 5], gap="large")
    with col_text:
        _text(ep_id)
    with col_form:
        _labels(ep_id, me, answers, ids, done)


def _text(ep_id):
    ep = get_episode(ep_id)
    if ep is None:
        st.error(f"Episode {ep_id} is not in your local database. Restart the app after `git pull`.")
        return
    lang = st.radio("Language", ["English", "Polish"], horizontal=True, key="disc_lang",
                    label_visibility="collapsed")
    col = "en" if lang == "English" else "pl"
    st.markdown(_context_html(ep[f"context_{col}"], ep[f"text_{col}"]), unsafe_allow_html=True)


def _labels(ep_id, me, answers, ids, done):
    round1 = D.basis_positions(ep_id)
    now = {c: D.current_position(p, answers[c].get(ep_id)) for c, p in round1.items()}
    num = {c: i for i, c in enumerate(sorted(set(answers) - {me}), 1)}   # same number on every episode
    others = sorted((c for c in round1 if c != me), key=num.get)
    widths = [3, 5] + [3] * len(others)

    head = st.columns(widths)
    head[1].markdown("**You**")
    for col, c in zip(head[2:], others):
        col.markdown(f"**Coder {num[c]}**")

    new = {}
    for f in D.FIELDS:
        row = st.columns(widths, vertical_alignment="center")
        row[0].markdown(f"**{D.FIELD_NAMES[f]}**")
        new[f] = _select(row[1], f, now[me][f], new, ep_id)
        for col, c in zip(row[2:], others):
            col.markdown(_other(f, round1[c][f], now[c], new), unsafe_allow_html=True)

    notes = []
    for c in others:
        if round1[c]["notes"].strip():
            notes.append(f"- Coder {num[c]}: {round1[c]['notes'].strip()}")
        a = answers[c].get(ep_id)
        if a and a.get("note", "").strip():
            notes.append(f"- Coder {num[c]} ({'changed' if a['decision'] == 'change' else 'kept'}): "
                         f"{a['note'].strip()}")
    if notes:
        st.markdown("\n".join(notes))

    mine = round1[me]
    prev = answers[me].get(ep_id)
    note = st.text_area("Note", value=(prev or {}).get("note", ""), key=f"dn_{ep_id}",
                        placeholder="Why you changed or kept your label")
    if st.button("Save", type="primary", use_container_width=True, key=f"dsave_{ep_id}"):
        missing = [D.FIELD_NAMES[f] for f in D.FIELDS if not new[f] and
                   (f in D.GATES or new["is_contestation"] == "yes")]
        if missing:
            st.error(f"Please choose: {', '.join(missing)}.")
        elif not note.strip() and all(new[f] == (mine[f] or "") for f in D.FIELDS):
            st.error("Change a value, or write a note saying why you keep your label.")
        else:
            spent = time.time() - st.session_state.get("disc_start_time", time.time())
            D.save_answer(me, ep_id, new, mine, note, sum(ep_id in answers[c] for c in others), spent)
            i = ids.index(ep_id)
            st.session_state._disc_next = next((e for e in ids[i + 1:] + ids[:i] if e not in done), ep_id)
            st.rerun()


def _select(col, f, value, new, ep_id) -> str:
    """Selector for your value of one field. Structure fields are off while contestation = no."""
    if f not in D.GATES and new["is_contestation"] != "yes":
        off = "absent" if f == "presence" else ""
        col.selectbox(f, [off or "—"], disabled=True, label_visibility="collapsed", key=f"v_{f}_{ep_id}_off")
        return off
    opts = OPTIONS.get(f) or D.merged_values(f)
    choice = col.selectbox(f, opts, index=opts.index(value) if value in opts else None,
                           placeholder="choose", label_visibility="collapsed", key=f"v_{f}_{ep_id}")
    return choice or ""


def _other(f, old, pos, new) -> str:
    """Another coder's value: orange if it differs from your selected value, green if the same."""
    cur = pos[f]
    if f in D.DIMS and pos["is_contestation"] != "yes":
        return '<div style="padding:4px 8px;opacity:0.5">—</div>'
    text = html.escape(cur or "·")
    if old != cur:
        text = (f"<s>{html.escape(old)}</s>" if old else "—") + f" → {text}"
    style = ""
    if f in D.COMPARED and (f in D.GATES or new["is_contestation"] == "yes"):
        style = SAME if cur == new[f] else DIFFERS
    return f'<div style="padding:4px 8px;border-radius:4px;font-size:0.9em;{style}">{text}</div>'
