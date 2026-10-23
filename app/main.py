"""
XAI Contestation Labelling Tool

Run with:  streamlit run app/main.py
"""
import sys
from pathlib import Path

_ROOT = Path(__file__).parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st

from app.db import init_db, get_or_create_annotator, get_all_work_episode_ids, get_labels_by_annotator
from app.seed import seed

st.set_page_config(
    page_title="XAI Contestation Labelling",
    page_icon="🍄",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()

# Auto-seed on first run if episodes table is empty
if not get_all_work_episode_ids():
    seed()

st.sidebar.title("🍄 XAI Labelling")

email = st.sidebar.text_input(
    "Email",
    value=st.session_state.get("identifier", ""),
    placeholder="your@email.com",
).strip()

if email:
    st.session_state.identifier = email
    annotator_id = get_or_create_annotator(email)
    st.session_state.annotator_id = annotator_id

    all_ids = get_all_work_episode_ids()
    done_ids = get_labels_by_annotator(annotator_id)
    total = len(all_ids)

    if total == 0:
        st.sidebar.warning("No episodes found. Run `python -m app.seed`.")
    else:
        st.sidebar.caption(f"{len(done_ids)} / {total} labelled")

        # ep_num lives in session_state so label.py can advance it after a save
        if "ep_num" not in st.session_state:
            st.session_state.ep_num = 1

        ep_num = st.sidebar.number_input(
            "Episode #", min_value=1, max_value=total, step=1,
            value=st.session_state.ep_num,
            key="ep_num",
        )
        st.session_state.current_episode_id = all_ids[ep_num - 1]

st.sidebar.divider()
page = st.sidebar.radio("", ["Label", "Guide"], label_visibility="collapsed")

if not email:
    st.info("👈 Enter your email in the sidebar to begin.")
elif page == "Label":
    from app.views.label import render
    render()
else:
    from app.views.guide import render
    render()
