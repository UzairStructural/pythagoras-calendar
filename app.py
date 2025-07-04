# === Updated app.py for Outlook-style Calendar with GPT Assistant Integration ===

import streamlit as st
import datetime
import uuid
import json
import os
from taskinteraction import render_cell, show_gpt_suggestions
from gpt_assistant import run_gpt_summary

# === SETUP ===
st.set_page_config(page_title="📆 Outlook-Style Calendar", layout="wide")

# === STYLING & JS FOR GRID + CLICK COORDINATE TRACKER ===
st.markdown("""
    <style>
    body {
        background-color: #f9f9f9;
        color: #333;
        font-family: 'Segoe UI', Arial, sans-serif;
    }
    .hour-cell {
        height: 48px;
        border-bottom: 1px dotted #ccc;
        padding: 2px;
        cursor: pointer;
    }
    .day-header {
        font-weight: bold;
        background-color: #f5f5f5;
        text-align: center;
        padding: 8px 0;
        border-bottom: 2px solid #ccc;
        border-right: 1px solid #ddd;
    }
    .selected-day {
        border: 2px solid #0078d7;
        border-radius: 4px;
        padding: 4px;
        background-color: #e6f0fb;
    }
    .calendar-cell {
        height: 120px;
        border: 1px solid #ddd;
        padding: 4px;
        font-size: 13px;
        position: relative;
    }
    .date-label {
        position: absolute;
        top: 4px;
        right: 8px;
        font-size: 11px;
        color: #999;
    }
    .grid-overlay {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: repeating-linear-gradient(
            to right,
            rgba(0,0,0,0.05) 0px,
            rgba(0,0,0,0.05) 1px,
            transparent 1px,
            transparent 20px
        ),
        repeating-linear-gradient(
            to top,
            rgba(0,0,0,0.05) 0px,
            rgba(0,0,0,0.05) 1px,
            transparent 1px,
            transparent 10px
        );
        z-index: 0;
        pointer-events: none;
    }
    .axis-labels {
        position: fixed;
        bottom: 0;
        left: 0;
        color: rgba(0,0,0,0.2);
        font-size: 10px;
        z-index: 1;
    }
    #click-coords {
        position: fixed;
        top: 20px;
        right: 20px;
        background-color: rgba(255,255,255,0.95);
        padding: 8px 12px;
        border: 1px solid #ccc;
        border-radius: 6px;
        font-size: 13px;
        color: #111;
        z-index: 10000;
        cursor: move;
        font-family: Arial, sans-serif;
        box-shadow: 2px 2px 6px rgba(0,0,0,0.1);
    }
    </style>
    <div class="grid-overlay"></div>
    <div class="axis-labels">
        <div style="position:absolute; bottom:0; left:0">0,0</div>
    </div>
    <div id="click-coords">X: 0, Y: 0</div>
    <script>
        const box = document.getElementById('click-coords');
        let isDragging = false, offsetX, offsetY;

        box.addEventListener('mousedown', function(e) {
            isDragging = true;
            offsetX = e.offsetX;
            offsetY = e.offsetY;
        });

        document.addEventListener('mouseup', () => isDragging = false);

        document.addEventListener('mousemove', function(e) {
            if (isDragging) {
                box.style.left = (e.clientX - offsetX) + 'px';
                box.style.top = (e.clientY - offsetY) + 'px';
            }
        });

        document.addEventListener('click', function(e) {
            const x = e.clientX;
            const y = window.innerHeight - e.clientY;
            box.innerText = `X: ${x}, Y: ${y}`;
        });
    </script>
""", unsafe_allow_html=True)

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

# Sync calendar to date input
if st.session_state.date_input != st.session_state.selected_date:
    st.session_state.selected_date = st.session_state.date_input

view_mode = st.sidebar.selectbox("View Mode", ["Month", "Work Week"], index=0 if st.session_state.view_mode == "Month" else 1)
st.session_state.view_mode = view_mode

# === NAVIGATION & HEADER ===
st.markdown("### " + st.session_state.selected_date.strftime("%B %Y") if view_mode == "Month" else st.session_state.selected_date.strftime("Week of %B %d, %Y"))

col1, col2, col3 = st.columns([1,2,1])
with col1:
    if st.button("⬆️"):
        if view_mode == "Month":
            st.session_state.selected_date -= datetime.timedelta(days=30)
        else:
            st.session_state.selected_date -= datetime.timedelta(weeks=1)
with col2:
    st.markdown(f"### :calendar: {'Month of ' + st.session_state.selected_date.strftime('%B %Y') if view_mode == 'Month' else st.session_state.selected_date.strftime('%m/%d/%y')} – {(st.session_state.selected_date + datetime.timedelta(days=6)).strftime('%m/%d/%y') if view_mode == 'Work Week' else ''}")
with col3:
    if st.button("⬇️"):
        if view_mode == "Month":
            st.session_state.selected_date += datetime.timedelta(days=30)
        else:
            st.session_state.selected_date += datetime.timedelta(weeks=1)

# === CALENDAR BODY RENDERING ===
if view_mode == "Month":
    st.markdown("#### 🗓️ Monthly View")
    start_date = st.session_state.selected_date.replace(day=1)
    start_day = start_date.weekday()
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

# === GPT Assistant Button and Suggestions ===

st.write("---")
if st.button("🤖 Run GPT Assistant"):
    run_gpt_summary()

show_gpt_suggestions()
