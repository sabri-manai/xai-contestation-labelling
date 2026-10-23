"""Labelling screen."""
from __future__ import annotations
import sys
import json
import time
from pathlib import Path

_ROOT = Path(__file__).parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st

from app.db import get_episode, get_latest_label, save_label

# Load taxonomy once
_TAXONOMY_PATH = Path(__file__).parent.parent.parent / "taxonomy.json"
with open(_TAXONOMY_PATH) as f:
    TAXONOMY = json.load(f)

_DIM_VALUES: dict[str, list[str]] = {
    d["name"]: d["values"]
    for d in TAXONOMY["dimensions"]
    if isinstance(d.get("values"), list)
}


def _context_html(context: str, target: str) -> str:
    """Render context with the target line highlighted."""
    lines = [l.strip() for l in context.split("||") if l.strip()]
    parts = []
    for line in lines:
        escaped = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        if target.strip() and target.strip() in line:
            parts.append(
                f'<div style="border-left:3px solid #f0ad4e;'
                f'padding:4px 10px;margin:4px 0;">'
                f'<strong>{escaped}</strong></div>'
            )
        else:
            parts.append(
                f'<div style="padding:4px 10px;margin:2px 0;opacity:0.75;">{escaped}</div>'
            )
    return "\n".join(parts)


def render():
    annotator_id: int | None = st.session_state.get("annotator_id")
    ep_id: str | None = st.session_state.get("current_episode_id")

    if not annotator_id:
        st.info("Enter your initials or email in the sidebar to begin.")
        return

    if not ep_id:
        st.info("Use the sidebar to pick an episode.")
        return

    ep = get_episode(ep_id)
    if ep is None:
        st.error(f"Episode {ep_id} not found.")
        return

    if st.session_state.get("episode_start_ep") != ep_id:
        st.session_state.episode_start_time = time.time()
        st.session_state.episode_start_ep = ep_id

    lang = st.radio("Language", ["English", "Polish", "Both"],
                    horizontal=True, index=0, key="lang_toggle")

    col_text, col_form = st.columns([3, 2], gap="large")

    # ------------------------------------------------------------------
    # Context display
    # ------------------------------------------------------------------
    with col_text:
        st.subheader("Context & Target Line")

        if lang in ("English", "Both"):
            if lang == "Both":
                st.markdown("**English**")
            st.markdown(_context_html(ep["context_en"], ep["text_en"]),
                        unsafe_allow_html=True)

        if lang in ("Polish", "Both"):
            if lang == "Both":
                st.markdown("---")
                st.markdown("**Polish** *(authoritative)*")
            st.markdown(_context_html(ep["context_pl"], ep["text_pl"]),
                        unsafe_allow_html=True)

        st.caption(
            f"`{ep['episode_id']}` · {ep['participant_group']} · "
            f"{ep['explanation_format']} · {ep['explanation_theme']}"
        )

    # ------------------------------------------------------------------
    # Labelling form
    # ------------------------------------------------------------------
    with col_form:
        st.subheader("Label")

        prev = get_latest_label(annotator_id, ep_id)

        with st.form(key=f"label_form_{ep_id}"):
            is_contestation = st.radio(
                "Is this **contestation**?",
                ["yes", "no"],
                index=0 if (prev and prev.get("is_contestation") == "yes") else 1,
                help=TAXONOMY.get("core_test", ""),
            )

            st.markdown("*Fill dimensions below only if **yes**.*")

            presence = st.selectbox(
                "Presence", [""] + _DIM_VALUES["presence"],
                index=_dim_index("presence", prev),
            )
            target = st.selectbox(
                "Target", [""] + _DIM_VALUES["target"],
                index=_dim_index("target", prev),
            )
            interaction_act = st.selectbox(
                "Interaction act", [""] + _DIM_VALUES["interaction_act"],
                index=_dim_index("interaction_act", prev),
            )
            grounds = st.selectbox(
                "Grounds", [""] + _DIM_VALUES["grounds"],
                index=_dim_index("grounds", prev),
            )
            expected_response = st.selectbox(
                "Expected response", [""] + _DIM_VALUES["expected_response"],
                index=_dim_index("expected_response", prev),
            )

            notes = st.text_area(
                "Notes",
                value=(prev.get("notes") or "") if prev else "",
                placeholder="Required when presence = ambiguous. Also use when you hesitate.",
            )

            bcol1, bcol2, bcol3 = st.columns(3)
            with bcol1:
                back = st.form_submit_button("← Back", use_container_width=True)
            with bcol2:
                submitted = st.form_submit_button("Save ✓", use_container_width=True,
                                                  type="primary")
            with bcol3:
                skip = st.form_submit_button("Skip →", use_container_width=True)

        if back:
            _go(-1)
            st.rerun()

        elif skip:
            save_label(annotator_id, ep_id, None, None, None, None, None, None,
                       notes or None, is_skipped=True)
            _advance()
            st.rerun()

        elif submitted:
            error = _validate(is_contestation, presence, target, interaction_act,
                              grounds, expected_response, notes)
            if error:
                st.error(error)
            else:
                time_spent = time.time() - st.session_state.episode_start_time
                final_presence = "absent" if is_contestation == "no" else (presence or None)
                save_label(
                    annotator_id, ep_id, is_contestation,
                    final_presence, target or None,
                    interaction_act or None, grounds or None,
                    expected_response or None, notes or None,
                    time_spent_s=time_spent,
                )
                _advance()
                st.rerun()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _dim_index(dim: str, prev: dict | None) -> int:
    if prev is None:
        return 0
    val = prev.get(dim)
    opts = [""] + _DIM_VALUES.get(dim, [])
    return opts.index(val) if val in opts else 0


def _validate(is_contestation, presence, target, interaction_act,
              grounds, expected_response, notes) -> str | None:
    if is_contestation == "yes":
        missing = [
            name for name, val in [
                ("Presence", presence), ("Target", target),
                ("Interaction act", interaction_act), ("Grounds", grounds),
                ("Expected response", expected_response),
            ] if not val
        ]
        if missing:
            return f"Please fill in: {', '.join(missing)}."
        if presence == "ambiguous" and not notes.strip():
            return "Notes are required when presence = ambiguous."
    return None


def _go(delta: int):
    """Move ep_num by delta, clamped to valid range."""
    from app.db import get_all_work_episode_ids
    total = len(get_all_work_episode_ids())
    current = st.session_state.get("ep_num", 1)
    st.session_state.ep_num = max(1, min(total, current + delta))
    st.session_state.current_episode_id = None
    st.session_state.pop("episode_start_ep", None)
    st.session_state.pop("episode_start_time", None)


def _advance():
    _go(1)
