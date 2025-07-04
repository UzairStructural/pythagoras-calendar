# taskinteraction.py

import streamlit as st
import datetime

# Temporary in-memory event store
if "events" not in st.session_state:
    st.session_state.events = {}

def render_task_popup(day, hour):
    key = f"{day}_{hour}"
    existing = st.session_state.events.get(key, {})

    with st.popover(f"Edit Task: {day.strftime('%A')} {hour}"):
        start = st.selectbox("Start Time", [f"{h % 12 or 12} {'AM' if h < 12 else 'PM'}" for h in range(24)], index=hour)
        end = st.selectbox("End Time", [f"{h % 12 or 12} {'AM' if h < 12 else 'PM'}" for h in range(hour+1, 24)], index=0)
        notes = st.text_area("Notes", value=existing.get("notes", ""))

        if st.button("💾 Save"):
            st.session_state.events[key] = {
                "start": start,
                "end": end,
                "notes": notes,
                "day": day.strftime("%Y-%m-%d"),
                "hour": hour
            }
            st.success("Task saved!")

def get_event(day, hour):
    key = f"{day}_{hour}"
    return st.session_state.events.get(key)

def render_cell(day, hour):
    key = f"{day}_{hour}"
    event = get_event(day, hour)
    style = "border:1px solid #ccc; padding:6px; cursor:pointer; height:48px; background:#fff;"

    if event:
        content = f"<div style='{style}'><b>{event['start']}–{event['end']}</b><br>{event['notes']}</div>"
    else:
        content = f"<div style='{style}'><i>(Click to add)</i></div>"

    if st.markdown(content, unsafe_allow_html=True):
        render_task_popup(day, hour)
