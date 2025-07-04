# app.py — Outlook-style Calendar with GPT Suggestions and Editable Cells

import streamlit as st
import datetime
import uuid
import json
from openai import OpenAI
from taskinteraction import render_cell, show_gpt_suggestions
from gpt_assistant import summarize_calendar, generate_gpt_suggestions, load_all_events

# === SETUP ===
st.set_page_config(page_title="📆 Outlook-Style Calendar", layout="wide")

# === SESSION STATE SETUP ===
if "selected_date" not in st.session_state:
    st.session_state.selected_date = datetime.date.today()
if "view_mode" not in st.session_state:
    st.session_state.view_mode = "Work Week"
if "events" not in st.session_state:
    st.session_state.events = {}

# === SIDEBAR ===
st.sidebar.header("📅 Calendar Controls")
st.sidebar.date_input("Jump to Date", value=st.session_state.selected_date, key="date_input")

# Sync calendar to date input
if st.session_state.date_input != st.session_state.selected_date:
    st.session_state.selected_date = st.session_state.date_input

view_mode = st.sidebar.selectbox("View Mode", ["Month", "Work Week"], index=1 if st.session_state.view_mode == "Work Week" else 0)
st.session_state.view_mode = view_mode

# === NAVIGATION HEADER ===
st.markdown("### " + st.session_state.selected_date.strftime("%B %Y") if view_mode == "Month" else st.session_state.selected_date.strftime("Week of %B %d, %Y"))
col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    if st.button("⬅️"):
        delta = datetime.timedelta(days=30) if view_mode == "Month" else datetime.timedelta(weeks=1)
        st.session_state.selected_date -= delta
with col3:
    if st.button("➡️"):
        delta = datetime.timedelta(days=30) if view_mode == "Month" else datetime.timedelta(weeks=1)
        st.session_state.selected_date += delta

# === CALENDAR BODY ===
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

# === GPT Assistant Button ===
if st.button("🤖 Analyze Calendar with GPT"):
    events = load_all_events()
    if events:
        with st.spinner("Thinking..."):
            summary = summarize_calendar(events)
            generate_gpt_suggestions(events)
        st.markdown("---")
        st.subheader("📋 GPT Summary:")
        st.markdown(summary)

# === GPT Suggestions Display ===
st.markdown("---")
st.subheader("🤖 GPT Suggested Tasks")
show_gpt_suggestions(source_filter=None)
