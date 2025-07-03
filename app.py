# === Updated app.py for Outlook-style Calendar with Weekly & Monthly Enhancements and Interactive Task Popup ===

import streamlit as st
import datetime
import uuid
import json
import os
from openai import OpenAI

# === SETUP ===
st.set_page_config(page_title="📆 Outlook-Style Calendar", layout="wide")

# === STYLING & JS FOR GRID + COORDINATE TRACKER ===
st.markdown("""
    <style>
    body {
        background-color: #f9f9f9;
        color: #333;
        font-family: 'Segoe UI', Arial, sans-serif;
    }
    .hour-cell {
        height: 60px;
        border-bottom: 1px solid #ddd;
        padding: 5px;
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
            transparent 20px
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
    #cursor-coords {
        position: fixed;
        top: 10px;
        right: 20px;
        background-color: rgba(0,0,0,0.05);
        padding: 6px 10px;
        border: 1px solid #ccc;
        border-radius: 4px;
        font-size: 12px;
        color: #000;
        z-index: 10000;
        font-family: Arial, sans-serif;
    }
    </style>
    <div class="grid-overlay"></div>
    <div class="axis-labels">
        <div style="position:absolute; bottom:0; left:0">0,0</div>
    </div>
    <div id="cursor-coords">X: 0, Y: 0</div>
    <script>
        document.addEventListener('mousemove', function(e) {
            const x = e.clientX;
            const y = window.innerHeight - e.clientY;
            document.getElementById('cursor-coords').innerText = `X: ${x}, Y: ${y}`;
        });
    </script>
""", unsafe_allow_html=True)

# === STATE DEFAULTS ===
if "selected_date" not in st.session_state:
    st.session_state.selected_date = datetime.date(2029, 8, 9)
if "task_popup" not in st.session_state:
    st.session_state.task_popup = False
if "popup_datetime" not in st.session_state:
    st.session_state.popup_datetime = None
if "tasks" not in st.session_state:
    st.session_state.tasks = []

# === TOOLBAR ===
view_mode = st.session_state.get("view_mode", "Month")
selected_date = st.session_state.selected_date

if view_mode == "Month":
    title_display = selected_date.strftime("%B %Y")
else:
    start_of_week = selected_date - datetime.timedelta(days=selected_date.weekday())
    end_of_week = start_of_week + datetime.timedelta(days=6)
    title_display = f"{start_of_week.strftime('%m/%d/%y')} – {end_of_week.strftime('%m/%d/%y')}"

st.markdown(f"## 📅 {view_mode} View – {title_display}")
toolbar_col1, toolbar_col2, toolbar_col3 = st.columns([1, 5, 1])
with toolbar_col1:
    if st.button("⬆️"):
        if view_mode == "Month":
            new_month = selected_date.month - 1 or 12
            new_year = selected_date.year - 1 if new_month == 12 else selected_date.year
            new_year = max(2024, new_year)
            st.session_state.selected_date = selected_date.replace(year=new_year, month=new_month, day=1)
        else:
            new_date = selected_date - datetime.timedelta(weeks=1)
            st.session_state.selected_date = max(datetime.date(2024, 1, 1), new_date)
    if st.button(title_display):
        st.session_state.selected_date = datetime.date.today()
    if st.button("⬇️"):
        if view_mode == "Month":
            new_month = selected_date.month + 1 if selected_date.month < 12 else 1
            new_year = selected_date.year + 1 if new_month == 1 else selected_date.year
            new_year = min(2040, new_year)
            st.session_state.selected_date = selected_date.replace(year=new_year, month=new_month, day=1)
        else:
            new_date = selected_date + datetime.timedelta(weeks=1)
            st.session_state.selected_date = min(datetime.date(2040, 12, 31), new_date)

with toolbar_col3:
    st.selectbox("View Mode", ["Work Week", "Month"], index=1 if view_mode == "Month" else 0, key="view_mode")

# === LEFT SIDEBAR ===
with st.sidebar:
    st.subheader("🗓️ Calendar Navigation")
    st.date_input("Jump to Date", value=st.session_state.selected_date)

# === MAIN CALENDAR VIEW ===
st.markdown("---")

if st.session_state.view_mode == "Month":
    # === MONTHLY VIEW ===
    days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    day_headers = st.columns(7)
    for i, day in enumerate(days):
        with day_headers[i]:
            st.markdown(f"<div class='day-header'>{day}</div>", unsafe_allow_html=True)

    first_day = selected_date.replace(day=1)
    start_day = first_day - datetime.timedelta(days=first_day.weekday() + 1 if first_day.weekday() < 6 else 0)
    dates_grid = [start_day + datetime.timedelta(days=i) for i in range(42)]
    grid_rows = [dates_grid[i:i + 7] for i in range(0, len(dates_grid), 7)]

    for week in grid_rows:
        cols = st.columns(7)
        for idx, day in enumerate(week):
            with cols[idx]:
                selected_style = "selected-day" if day == selected_date else "calendar-cell"
                st.markdown(f"""
                    <div class='{selected_style}'>
                        <div class='date-label'>{day.day}</div>
                    </div>
                """, unsafe_allow_html=True)
else:
    # === WEEKLY VIEW ===
    start_of_week = selected_date - datetime.timedelta(days=selected_date.weekday())
    days = [(start_of_week + datetime.timedelta(days=i)) for i in range(7)]

    day_headers = st.columns(8)
    day_headers[0].markdown("**Time**")
    for i, day in enumerate(days):
        day_headers[i+1].markdown(f"<div class='day-header'>{day.strftime('%A %d')}</div>", unsafe_allow_html=True)

    time_range = [datetime.time(h, 0) for h in range(24)]  # Full day: 12AM–12AM

    for t in time_range:
        row = st.columns(8)
        row[0].markdown(f"{t.strftime('%-I %p')}")
        for i in range(1, 8):
            block_id = f"{days[i-1]} {t}"
            if st.button(" ", key=block_id):
                st.session_state.task_popup = True
                st.session_state.popup_datetime = datetime.datetime.combine(days[i-1], t)
            row[i].markdown("<div class='hour-cell'></div>", unsafe_allow_html=True)

# === TASK CREATION POPUP ===
if st.session_state.task_popup and st.session_state.popup_datetime:
    st.markdown("---")
    st.subheader("📝 New Task")
    start_time = st.time_input("Start Time", value=st.session_state.popup_datetime.time(), key="start_time")
    end_time = st.time_input("End Time", value=(datetime.datetime.combine(datetime.date.today(), st.session_state.popup_datetime.time()) + datetime.timedelta(hours=1)).time(), key="end_time")
    notes = st.text_area("Notes", key="notes")
    if st.button("💾 Save Task"):
        st.session_state.tasks.append({
            "datetime": st.session_state.popup_datetime,
            "start": start_time,
            "end": end_time,
            "notes": notes
        })
        st.session_state.task_popup = False
        st.success("Task saved!")

# === FOOTER ===
st.markdown("---")
st.caption("🖥️ Outlook-Style Calendar inspired by Uzair's Pythagoras AI Project")
