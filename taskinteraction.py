# taskinteraction.py

import streamlit as st
import datetime
import uuid
from supabase import create_client, Client

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_event_key(day, hour):
    return f"{day}_{hour}"

def save_event_to_supabase(day, hour, start, end, notes):
    key = get_event_key(day, hour)
    event_data = {
        "id": str(uuid.uuid4()),
        "key": key,
        "day": day.strftime("%Y-%m-%d"),
        "hour": hour,
        "start": start,
        "end": end,
        "notes": notes,
    }
    existing = supabase.table("events").select("id").eq("key", key).execute()
    if existing.data:
        supabase.table("events").update(event_data).eq("key", key).execute()
    else:
        supabase.table("events").insert(event_data).execute()

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

def show_gpt_suggestions():
    st.subheader("🤖 GPT Suggested Tasks")
    suggestions = supabase.table("gpt_suggestions").select("*").execute()

    if not suggestions.data:
        st.info("No GPT suggestions yet. Run GPT Assistant above.")
        return

    for suggestion in suggestions.data:
        with st.expander(f"{suggestion['day']} @ {suggestion['start']} – {suggestion['notes'][:30]}..."):
            st.write(f"**Start:** {suggestion['start']}")
            st.write(f"**End:** {suggestion['end']}")
            st.write(f"**Notes:** {suggestion['notes']}")
            if st.button("✅ Approve & Add to Calendar", key=f"approve_{suggestion['id']}"):
                save_event_to_supabase(
                    day=datetime.datetime.strptime(suggestion["day"], "%Y-%m-%d"),
                    hour=int(suggestion["hour"]),
                    start=suggestion["start"],
                    end=suggestion["end"],
                    notes=suggestion["notes"]
                )
                st.success("Added to calendar!")
