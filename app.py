# === Updated app.py for Outlook-style Calendar with Weekly & Monthly Enhancements ===

import streamlit as st
import datetime
import uuid
import json
import os
from openai import OpenAI

# === SETUP ===
st.set_page_config(page_title="📆 Outlook-Style Calendar", layout="wide")

# === STYLING ===
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
    </style>
""", unsafe_allow_html=True)

# === STATE DEFAULTS ===
if "selected_date" not in st.session_state:
    st.session_state.selected_date = datetime.date(2029, 8, 9)

# === TOOLBAR ===
st.markdown(f"## 📅 {'Month' if st.session_state.get('view_mode', 'Month') == 'Month' else 'Work Week'} View – {st.session_state.selected_date.strftime('%B %Y')}")
toolbar_col1, toolbar_col2, toolbar_col3 = st.columns([1, 5, 1])
with toolbar_col1:
    st.button("⬅️")
    if st.button("Today"):
        st.session_state.selected_date = datetime.date.today()
    st.button("➡️")
with toolbar_col2:
    st.markdown(f"<h4 style='text-align: center;'>{st.session_state.selected_date.strftime('%B %Y')}</h4>", unsafe_allow_html=True)
with toolbar_col3:
    st.selectbox("View Mode", ["Work Week", "Month"], index=1 if st.session_state.get("view_mode") == "Month" else 0, key="view_mode")

# === LEFT SIDEBAR ===
with st.sidebar:
    st.subheader("🗓️ Calendar Navigation")
    st.date_input("Jump to Date", value=st.session_state.selected_date)
    st.write("#### 📁 My Calendars")
    st.checkbox("✅ Calendar - UAhmed@falcon…", value=True)
    st.checkbox("United States Holidays")
    st.checkbox("Birthdays")
    st.checkbox("Calendar - Falcon Contacts")

# === MAIN CALENDAR VIEW ===
st.markdown("---")

if st.session_state.view_mode == "Month":
    # === MONTHLY VIEW ===
    days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    day_headers = st.columns(7)
    for i, day in enumerate(days):
        with day_headers[i]:
            st.markdown(f"<div class='day-header'>{day}</div>", unsafe_allow_html=True)

    dates_august = [datetime.date(2029, 7, 29) + datetime.timedelta(days=i) for i in range(42)]
    grid_rows = [dates_august[i:i + 7] for i in range(0, len(dates_august), 7)]

    for week in grid_rows:
        cols = st.columns(7)
        for idx, day in enumerate(week):
            with cols[idx]:
                selected_style = "selected-day" if day == st.session_state.selected_date else "calendar-cell"
                st.markdown(f"""
                    <div class='{selected_style}'>
                        <div class='date-label'>{day.day}</div>
                    </div>
                """, unsafe_allow_html=True)
else:
    # === WEEKLY VIEW ===
    start_of_week = st.session_state.selected_date - datetime.timedelta(days=st.session_state.selected_date.weekday())
    days = [(start_of_week + datetime.timedelta(days=i)) for i in range(7)]

    day_headers = st.columns(8)
    day_headers[0].markdown("**Time**")
    for i, day in enumerate(days):
        day_headers[i+1].markdown(f"<div class='day-header'>{day.strftime('%A %d')}</div>", unsafe_allow_html=True)

    time_range = [datetime.time(h, 0) for h in range(8, 21)]  # 8AM to 8PM

    for t in time_range:
        row = st.columns(8)
        row[0].markdown(f"{t.strftime('%-I %p')}")
        for i in range(1, 8):
            row[i].markdown("""
                <div class='hour-cell'>
                </div>
            """, unsafe_allow_html=True)

# === FOOTER ===
st.markdown("---")
st.caption("🖥️ Outlook-Style Calendar inspired by Uzair's Pythagoras AI Project")
