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
from app.sync import normalize_email, sync, file_for, code_for

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
    init_db()   # apply the labelling order to the freshly seeded episodes

st.sidebar.title("🍄 XAI Labelling")

email = st.sidebar.text_input(
    "Email",
    value=st.session_state.get("identifier", ""),
    placeholder="your@email.com",
)
email = normalize_email(email)

if email:
    st.session_state.identifier = email
    annotator_id = get_or_create_annotator(email)
    st.session_state.annotator_id = annotator_id

    # Once per session and email: restore labels from labels/<code>.csv (e.g. after git pull)
    # and write any local-only labels into it.
    if st.session_state.get("_synced_email") != email:
        restored = sync(annotator_id, email)
        st.session_state._synced_email = email
        st.session_state.pop("ep_num_val", None)
        if restored:
            st.sidebar.success(f"Restored {restored} label(s) from {file_for(email).name}")

    all_ids = get_all_work_episode_ids()
    done_ids = get_labels_by_annotator(annotator_id)
    total = len(all_ids)

    if total == 0:
        st.sidebar.warning("No episodes found. Run `python -m app.seed`.")
    else:
        st.sidebar.caption(f"{len(done_ids)} / {total} labelled · your code {code_for(email)}")

        # _pending_ep is written by _go() during a save/skip/back.
        # We consume it here (before any widget), then clear it.
        if "ep_num_val" not in st.session_state:
            # resume at the first episode this annotator has not labelled yet
            st.session_state.ep_num_val = next(
                (i + 1 for i, e in enumerate(all_ids) if e not in done_ids), 1)
        if "_pending_ep" in st.session_state:
            st.session_state.ep_num_val = st.session_state.pop("_pending_ep")

        ep_num = st.sidebar.number_input(
            "Episode #", min_value=1, max_value=total, step=1,
            value=int(st.session_state.ep_num_val),
        )
        st.session_state.ep_num_val = ep_num
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
