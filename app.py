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
st.markdown("## 📅 Month View – August 2029")
toolbar_col1, toolbar_col2, toolbar_col3 = st.columns([1, 5, 1])
with toolbar_col1:
    st.button("⬅️")
    if st.button("Today"):
        st.session_state.selected_date = datetime.date.today()
    st.button("➡️")
with toolbar_col2:
    st.markdown("<h4 style='text-align: center;'>August 2029</h4>", unsafe_allow_html=True)
with toolbar_col3:
    st.selectbox("View Mode", ["Work Week", "Month"], index=1, key="view_mode")

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

# === FOOTER ===
st.markdown("---")
st.caption("🖥️ Outlook-Style Calendar inspired by Uzair's Pythagoras AI Project")
