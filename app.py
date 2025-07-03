# === Updated app.py for Outlook-style Calendar ===
# Mirrors the visual behavior and layout of Outlook (light mode, month view, sidebars, toolbar, etc.)

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
        background-color: #ffffff;
        color: #333;
        font-family: 'Segoe UI', sans-serif;
    }
    .hour-cell {
        height: 40px;
        border-bottom: 1px solid #ccc;
        padding-left: 5px;
    }
    .day-header {
        font-weight: bold;
        background-color: #f5f5f5;
        text-align: center;
        padding: 10px 0;
        border-bottom: 2px solid #ccc;
    }
    .event {
        border: 1px dashed red;
        background-color: #ffe6e6;
        padding: 5px;
        border-radius: 4px;
        margin: 5px;
        color: #b30000;
        font-size: 12px;
    }
    .meeting {
        border: 1px dashed #cc0000;
        background-color: #ffe0cc;
        padding: 5px;
        border-radius: 4px;
        margin: 5px;
        font-size: 12px;
    }
    .selected-day {
        background-color: #0078d7;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# === STATE DEFAULTS ===
if "selected_date" not in st.session_state:
    st.session_state.selected_date = datetime.date(2029, 8, 9)

# === TOOLBAR ===
st.markdown("## 🧭 Outlook Calendar Toolbar")
t1, t2, t3, t4, t5 = st.columns(5)
with t1:
    st.button("📝 New Appointment")
    st.button("📅 New Meeting")
with t2:
    st.button("🧘 Add Focus Time")
    st.button("➕ New Items")
with t3:
    st.button("📞 Meet Now")
    st.button("📹 Teams Meeting")
with t4:
    if st.button("Today"):
        st.session_state.selected_date = datetime.date.today()
    st.button("Next 7 Days")
with t5:
    st.selectbox("View", ["Day", "Week", "Work Week", "Month", "Schedule View"], index=3)
    st.selectbox("Manage", ["Add Calendar", "Share Calendar", "New Group", "Browse Groups"])

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
st.markdown("### 📆 Month View – August 2029")

# Create 7 columns (Sunday to Saturday)
days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
day_columns = st.columns(7)
for i, day in enumerate(days):
    with day_columns[i]:
        st.markdown(f"<div class='day-header'>{day}</div>", unsafe_allow_html=True)

# Create 6 weeks of blank rows to simulate Outlook's grid
dates_august = [datetime.date(2029, 7, 29) + datetime.timedelta(days=i) for i in range(42)]  # Sunday start
grid_rows = [dates_august[i:i + 7] for i in range(0, len(dates_august), 7)]

# Events
meetings = [datetime.date(2029, 7, 30), datetime.date(2029, 8, 6), datetime.date(2029, 8, 13),
            datetime.date(2029, 8, 20), datetime.date(2029, 8, 27)]
cancellations = [datetime.date(2029, 8, 3), datetime.date(2029, 8, 31)]

# Render rows
for week in grid_rows:
    cols = st.columns(7)
    for idx, day in enumerate(week):
        with cols[idx]:
            style = "selected-day" if day == st.session_state.selected_date else ""
            st.markdown(f"<div class='{style}'><b>{day.day}</b></div>", unsafe_allow_html=True)
            if day in meetings:
                st.markdown("""
                <div class='meeting'>
                    9:00 AM<br>Weekly Scheduling<br>Microsoft Teams<br>Kendall Eberhardt
                </div>
                """, unsafe_allow_html=True)
            if day in cancellations:
                st.markdown("""
                <div class='event'>
                    Canceled:<br>N.Garon – Treatment
                </div>
                """, unsafe_allow_html=True)

# === FOOTER ===
st.markdown("---")
st.caption("🖥️ Outlook-Style Calendar inspired by Uzair's Pythagoras AI Project")

