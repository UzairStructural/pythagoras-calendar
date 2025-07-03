# === Updated app.py for Outlook-style Calendar with Interactive Task Popup and Click-Based Draggable Coordinate Tracker ===

import streamlit as st
import datetime
import uuid
import json
import os
from openai import OpenAI

# === SETUP ===
st.set_page_config(page_title="📆 Outlook-Style Calendar", layout="wide")

# === FORCE STATIC DATE INPUT VALUE TO SYNC WITH STATE ===
# Ensure st.date_input is linked to state correctly in sidebar

# === STYLING & JS FOR GRID + CLICK COORDINATE TRACKER ===
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

# === STATE DEFAULTS ===
if "selected_date" not in st.session_state:
    st.session_state.selected_date = datetime.date(2029, 8, 9)
if "task_popup" not in st.session_state:
    st.session_state.task_popup = False
if "popup_datetime" not in st.session_state:
    st.session_state.popup_datetime = None
if "tasks" not in st.session_state:
    st.session_state.tasks = []

# === LEFT SIDEBAR ===
with st.sidebar:
    st.subheader("🗓️ Calendar Navigation")
    picked = st.date_input("Jump to Date", value=st.session_state.selected_date)
    if picked != st.session_state.selected_date:
        st.session_state.selected_date = picked

# === CONTINUE AS NORMAL ===
# ...rest of your code (unchanged)...
