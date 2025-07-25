# taskinteraction.py — Task Interaction UI and GPT Suggestion Renderer

import uuid
import streamlit as st
from supabase import create_client, Client
import datetime
import os

# === Supabase Setup ===
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# === Render Each Cell in Weekly Calendar Grid ===
def render_cell(day, hour):
    key = f"{day}_{hour}"
    notes = st.session_state.events.get(key, "")
    with st.expander("📝 Add/View Task", expanded=False):
        new_notes = st.text_area("Notes", value=notes, key=f"note_{key}")
        if st.button("💾 Save", key=f"save_{key}"):
            st.session_state.events[key] = new_notes
            save_to_supabase(day, hour, new_notes)

# === Save Event to Supabase ===
def save_to_supabase(day, hour, notes):
    try:
        event = {
            "id": str(uuid.uuid4()),
            "day": str(day),
            "hour": hour,
            "start": f"{hour % 12 or 12} {'AM' if hour < 12 else 'PM'}",
            "end": f"{(hour+1) % 12 or 12} {'AM' if hour+1 < 12 else 'PM'}",
            "notes": notes,
            "source": "manual"
        }
        result = supabase.table("events").upsert(event).execute()
        if result.data is None:
            st.error("Supabase insert failed: No response data")
    except Exception as e:
        st.error(f"Failed to save: {e}")

# === Show GPT Suggestions from 'events' Table Where source='gpt' ===
def show_gpt_suggestions():
    st.markdown("### 🤖 GPT Suggested Tasks")
    try:
        suggestions = supabase.table("events").select("*").eq("source", "gpt").execute()
        if not suggestions.data:
            st.info("No GPT suggestions available yet.")
            return

        for s in suggestions.data:
            st.markdown(f"📌 **{s['day']} at {s['start']}–{s['end']}**  \n📜 {s['notes']}")
    except Exception as e:
        st.error(f"Failed to load suggestions: {e}")
