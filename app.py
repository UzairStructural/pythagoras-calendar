# === Updated app.py with GPT Assistant Integration and Suggestion Handling ===

import streamlit as st
import datetime
from taskinteraction import render_cell, show_gpt_suggestions
from gpt_assistant import summarize_calendar, generate_gpt_suggestions, load_all_events

# === SETUP ===
st.set_page_config(page_title="📆 Outlook-Style Calendar", layout="wide")

# === SESSION STATE SETUP ===
if "selected_date" not in st.session_state:
    st.session_state.selected_date = datetime.date.today()
if "view_mode" not in st.session_state:
    st.session_state.view_mode = "Month"
if "events" not in st.session_state:
    st.session_state.events = {}

# === SIDEBAR ===
st.sidebar.header("📅 Calendar Controls")
st.sidebar.date_input("Jump to Date", value=st.session_state.selected_date, key="date_input")

if st.session_state.date_input != st.session_state.selected_date:
    st.session_state.selected_date = st.session_state.date_input

view_mode = st.sidebar.selectbox("View Mode", ["Month", "Work Week"], index=0 if st.session_state.view_mode == "Month" else 1)
st.session_state.view_mode = view_mode

# === HEADER ===
st.markdown("### " + st.session_state.selected_date.strftime("%B %Y") if view_mode == "Month" else st.session_state.selected_date.strftime("Week of %B %d, %Y"))

col1, col2, col3 = st.columns([1,2,1])
with col1:
    if st.button("⬆️"):
        delta = datetime.timedelta(days=30 if view_mode == "Month" else 7)
        st.session_state.selected_date -= delta
with col2:
    st.markdown(f"### :calendar: {'Month of ' + st.session_state.selected_date.strftime('%B %Y') if view_mode == 'Month' else st.session_state.selected_date.strftime('%m/%d/%y')} – {(st.session_state.selected_date + datetime.timedelta(days=6)).strftime('%m/%d/%y') if view_mode == 'Work Week' else ''}")
with col3:
    if st.button("⬇️"):
        delta = datetime.timedelta(days=30 if view_mode == "Month" else 7)
        st.session_state.selected_date += delta

# === CALENDAR BODY ===
if view_mode == "Month":
    st.markdown("#### 🗓️ Monthly View")
    start_date = st.session_state.selected_date.replace(day=1)
    total_days = (start_date.replace(month=start_date.month % 12 + 1, day=1) - datetime.timedelta(days=1)).day
    grid = []
    week = []
    for day in range(1, total_days + 1):
        curr = start_date.replace(day=day)
        if (day == 1 and curr.weekday() != 0) or len(week) == 7:
            grid.append(week)
            week = []
        week.append(curr)
    grid.append(week)
    for row in grid:
        cols = st.columns(7)
        for i, day in enumerate(row):
            with cols[i]:
                st.markdown(f"**{day.strftime('%a')} {day.day}**")
                st.write("")
else:
    st.markdown("#### 🗓️ Weekly View")
    start = st.session_state.selected_date - datetime.timedelta(days=st.session_state.selected_date.weekday())
    days = [start + datetime.timedelta(days=i) for i in range(7)]
    times = [f"{h % 12 or 12} {'AM' if h < 12 else 'PM'}" for h in range(24)]
    st.write("---")
    headers = st.columns([1] + [1 for _ in days])
    with headers[0]:
        st.write("Time")
    for i, day in enumerate(days):
        with headers[i+1]:
            st.markdown(f"**{day.strftime('%a')} {day.day}**")

    for h, hour in enumerate(times):
        row = st.columns([1] + [1 for _ in days])
        with row[0]:
            st.markdown(f"<div class='hour-cell'>{hour}</div>", unsafe_allow_html=True)
        for i in range(1, len(row)):
            with row[i]:
                render_cell(days[i-1], h)

# === GPT ASSISTANT ===
st.write("---")
if st.button("🤖 Run GPT Assistant"):
    with st.spinner("Thinking with GPT..."):
        events = load_all_events()
        st.session_state.events = {event['key']: event for event in events}
        summary = summarize_calendar(events)
        generate_gpt_suggestions(events)
    st.subheader("📋 Summary")
    st.markdown(summary)
    st.success("Suggestions added below for approval.")

show_gpt_suggestions()
