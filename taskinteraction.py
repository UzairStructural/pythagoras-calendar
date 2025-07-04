# taskinteraction.py (Supabase-enabled, with error handling)

import streamlit as st
import datetime
from supabase import create_client, Client
import uuid
from postgrest.exceptions import APIError

# --- Supabase Setup ---
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Utility function to generate a unique task ID
def get_event_key(day, hour):
    return f"{day}_{hour}"

# --- Save task to Supabase ---
def save_event_to_supabase(day, hour, start, end, notes):
    try:
        key = get_event_key(day, hour)

        if not start or not end:
            st.warning("Start and End time cannot be empty.")
            return

        event_data = {
            "id": str(uuid.uuid4()),
            "key": key,
            "day": day.strftime("%Y-%m-%d"),
            "hour": int(hour),
            "start": str(start),
            "end": str(end),
            "notes": notes or ""
        }

        existing = supabase.table("events").select("id").eq("key", key).execute()
        if existing.data:
            supabase.table("events").update(event_data).eq("key", key).execute()
        else:
            supabase.table("events").insert(event_data).execute()

    except APIError as e:
        st.error(f"Supabase insert failed: {e.message}")
        st.json(event_data)

# --- Load events from Supabase ---
def load_events():
    if "events" not in st.session_state:
        st.session_state.events = {}
        results = supabase.table("events").select("*").execute()
        for e in results.data:
            st.session_state.events[e["key"]] = e

def render_task_popup(day, hour):
    load_events()
    key = get_event_key(day, hour)
    existing = st.session_state.events.get(key, {})

    with st.popover(f"Edit Task: {day.strftime('%A')} {hour}"):
        start = st.selectbox(
            "Start Time",
            [f"{h % 12 or 12} {'AM' if h < 12 else 'PM'}" for h in range(24)],
            index=hour,
            key=f"start_{key}"
        )
        end = st.selectbox(
            "End Time",
            [f"{h % 12 or 12} {'AM' if h < 12 else 'PM'}" for h in range(hour+1, 24)],
            index=0,
            key=f"end_{key}"
        )
        notes = st.text_area("Notes", value=existing.get("notes", ""), key=f"notes_{key}")

        if st.button("💾 Save", key=f"save_{key}"):
            save_event_to_supabase(day, hour, start, end, notes)
            st.session_state.events[key] = {
                "start": start,
                "end": end,
                "notes": notes,
                "day": day.strftime("%Y-%m-%d"),
                "hour": hour
            }
            st.success("Task saved!")

def get_event(day, hour):
    load_events()
    key = get_event_key(day, hour)
    return st.session_state.events.get(key)

def render_cell(day, hour):
    key = get_event_key(day, hour)
    event = get_event(day, hour)
    style = "border:1px solid #ccc; padding:6px; cursor:pointer; height:48px; background:#fff;"

    if event:
        content = f"<div style='{style}'><b>{event['start']}–{event['end']}</b><br>{event['notes']}</div>"
    else:
        content = f"<div style='{style}'><i>(Click to add)</i></div>"

    if st.markdown(content, unsafe_allow_html=True):
        render_task_popup(day, hour)
