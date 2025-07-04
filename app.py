# app.py — Outlook-style Calendar with Editable Cells + Expandable Chat Panel

import streamlit as st
import datetime
import uuid
import json
from taskinteraction import render_cell
from gpt_assistant import render_chat_pane

# === SETUP ===
st.set_page_config(page_title="📆 Outlook-Style Calendar", layout="wide")

# === SESSION STATE SETUP ===
if "selected_date" not in st.session_state:
    st.session_state.selected_date = datetime.date.today()
if "view_mode" not in st.session_state:
    st.session_state.view_mode = "Work Week"
if "events" not in st.session_state:
    st.session_state.events = {}
if "chat_open" not in st.session_state:
    st.session_state.chat_open = False

# === STYLES ===
chat_css = """
<style>
.chat-panel {
    position: fixed;
    top: 0;
    right: 0;
    height: 100vh;
    background-color: #111827;
    transition: all 0.3s ease-in-out;
    overflow-y: auto;
    padding: 1rem;
    z-index: 9999;
    color: white;
    border-left: 2px solid #333;
}
.chat-panel.closed {
    width: 0;
    padding: 0;
    overflow: hidden;
}
.chat-panel.open {
    width: 20vw;
}
</style>
"""
st.markdown(chat_css, unsafe_allow_html=True)

# === SIDEBAR ===
st.sidebar.header("📅 Calendar Controls")
st.sidebar.date_input("Jump to Date", value=st.session_state.selected_date, key="date_input")

# Sync calendar to date input
if st.session_state.date_input != st.session_state.selected_date:
    st.session_state.selected_date = st.session_state.date_input

view_mode = st.sidebar.selectbox("View Mode", ["Month", "Work Week"], index=1 if st.session_state.view_mode == "Work Week" else 0)
st.session_state.view_mode = view_mode

# === HEADER NAVIGATION ===
col1, col2, col3, col4 = st.columns([1, 2, 1, 1])
with col1:
    if st.button("⬅️"):
        delta = datetime.timedelta(days=30) if view_mode == "Month" else datetime.timedelta(weeks=1)
        st.session_state.selected_date -= delta
with col3:
    if st.button("➡️"):
        delta = datetime.timedelta(days=30) if view_mode == "Month" else datetime.timedelta(weeks=1)
        st.session_state.selected_date += delta
with col4:
    if st.button("💬 Chat"):
        st.session_state.chat_open = not st.session_state.chat_open

st.markdown("### " + (st.session_state.selected_date.strftime("%B %Y") if view_mode == "Month" else st.session_state.selected_date.strftime("Week of %B %d, %Y")))

# === LAYOUT WITH OPTIONAL CHAT ===
if st.session_state.chat_open:
    layout = st.columns([0.8, 0.2])
    main_col, chat_col = layout[0], layout[1]
else:
    main_col = st.container()
    chat_col = None

with main_col:
    if view_mode == "Month":
        st.subheader("🗓️ Monthly View")
        start_date = st.session_state.selected_date.replace(day=1)
        total_days = (start_date.replace(month=start_date.month % 12 + 1, day=1) - datetime.timedelta(days=1)).day
        week = []
        rows = []
        for i in range(1, total_days + 1):
            current = start_date.replace(day=i)
            week.append(current)
            if len(week) == 7 or i == total_days:
                rows.append(week)
                week = []
        for row in rows:
            cols = st.columns(7)
            for i, day in enumerate(row):
                with cols[i]:
                    st.markdown(f"**{day.strftime('%a')} {day.day}**")
                    st.write("")
    else:
        st.subheader("🗓️ Weekly View")
        start = st.session_state.selected_date - datetime.timedelta(days=st.session_state.selected_date.weekday())
        days = [start + datetime.timedelta(days=i) for i in range(7)]
        times = [f"{h % 12 or 12} {'AM' if h < 12 else 'PM'}" for h in range(24)]
        header_cols = st.columns([1] + [1 for _ in days])
        with header_cols[0]:
            st.write("Time")
        for i, d in enumerate(days):
            with header_cols[i + 1]:
                st.markdown(f"**{d.strftime('%a')} {d.day}**")

        for h, hour in enumerate(times):
            row = st.columns([1] + [1 for _ in days])
            with row[0]:
                st.markdown(f"{hour}")
            for i in range(1, len(row)):
                with row[i]:
                    render_cell(days[i - 1], h)

if chat_col:
    with chat_col:
        try:
            render_chat_pane()
        except Exception as e:
            st.error("Chat panel failed to load.")
            st.text(str(e))
