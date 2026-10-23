"""Example browser — shows the 12 gold 'example' episodes with their labels."""
from __future__ import annotations
import sys
from pathlib import Path

_ROOT = Path(__file__).parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st
from app.db import get_conn


def render():
    st.title("Training Examples")
    st.markdown(
        "These 12 episodes come from the adjudicated gold set and illustrate how to "
        "apply the taxonomy. Read these before labelling your first episode."
    )

    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT * FROM episodes
            WHERE gold_role='example'
            ORDER BY episode_id
            """
        ).fetchall()

    if not rows:
        st.warning("No example episodes found. Run `python -m app.seed` to load data.")
        return

    for row in rows:
        ep = dict(row)
        verdict = ep.get("is_contestation", "")
        colour = "#d4edda" if verdict == "yes" else "#f8d7da" if verdict == "no" else "#fff"
        badge = "✅ yes" if verdict == "yes" else "❌ no"

        with st.expander(
            f"**{ep['episode_id']}** — {ep['participant_group']} · "
            f"{ep['explanation_format']} · {ep['explanation_theme']}  —  {badge}",
            expanded=False,
        ):
            col_text, col_labels = st.columns([3, 2])

            with col_text:
                lang = st.radio("Language", ["English", "Polish", "Both"],
                                horizontal=True, key=f"ex_lang_{ep['episode_id']}")

                if lang in ("English", "Both"):
                    st.markdown("**English**")
                    _render_context(ep["context_en"], ep["text_en"])

                if lang in ("Polish", "Both"):
                    if lang == "Both":
                        st.markdown("---")
                    st.markdown("**Polish**")
                    _render_context(ep["context_pl"], ep["text_pl"])

            with col_labels:
                st.markdown("**Gold labels**")
                _label_row("Is contestation", ep.get("is_contestation"))
                if ep.get("is_contestation") == "yes":
                    _label_row("Presence", ep.get("presence"))
                    _label_row("Target", ep.get("target"))
                    _label_row("Interaction act", ep.get("interaction_act"))
                    _label_row("Grounds", ep.get("grounds"))
                    _label_row("Expected response", ep.get("expected_response"))


def _render_context(context: str, target: str):
    lines = [l.strip() for l in context.split("||") if l.strip()]
    for line in lines:
        if target.strip() and target.strip() in line:
            st.markdown(
                f'<div style="background:#fff3cd;border-left:4px solid #f0ad4e;'
                f'padding:6px 10px;border-radius:3px;">'
                f'<strong>▶ {line}</strong></div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div style="padding:4px 10px;color:#444;">{line}</div>',
                unsafe_allow_html=True,
            )


def _label_row(dim: str, val: str | None):
    if val:
        st.markdown(f"**{dim}:** `{val}`")
    else:
        st.markdown(f"**{dim}:** —")
