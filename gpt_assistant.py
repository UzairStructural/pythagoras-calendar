# gpt_assistant.py — GPT-powered Calendar Assistant (Refactored) with Chat UI

import streamlit as st
from supabase import create_client, Client
from openai import OpenAI
import datetime
import uuid
import json

# === Setup OpenAI & Supabase ===
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# === Load Events from Supabase ===
def load_all_events():
    try:
        response = supabase.table("events").select("*").order("day").execute()
        return response.data
    except Exception as e:
        st.error(f"Failed to load events: {e}")
        return []

# === Format Calendar Events as Text ===
def format_events(events):
    lines = []
    for event in events:
        line = f"{event['day']} at {event['start']}–{event['end']}: {event['notes']}"
        lines.append(line)
    return "\n".join(lines)

# === Ask GPT to Summarize or Provide Suggestions ===
def summarize_calendar(events):
    text_block = format_events(events)
    messages = [
        {"role": "system", "content": "You are a helpful calendar assistant that reviews daily and weekly tasks to find potential issues, overlaps, and give planning suggestions."},
        {"role": "user", "content": f"Here are the calendar events:\n{text_block}\n\nPlease summarize them and provide any suggestions."}
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.4
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"GPT summary failed: {e}")
        return ""

# === Save GPT Suggestions to Events Table ===
def save_gpt_suggestion(day, hour, start, end, notes):
    try:
        suggestion = {
            "id": str(uuid.uuid4()),
            "day": day,
            "hour": hour,
            "start": start,
            "end": end,
            "notes": notes,
            "source": "gpt"
        }
        result = supabase.table("events").insert(suggestion).execute()
        if result.status_code >= 400:
            st.error(f"Supabase insert failed: {result.data}")
    except Exception as e:
        st.error(f"Failed to save suggestion: {e}")

# === Generate Example Suggestions with GPT ===
def generate_gpt_suggestions(events):
    text_block = format_events(events)
    prompt_json = '[{"day":"2025-07-03","hour":9,"start":"9 AM","end":"10 AM","notes":"Team sync"}, ...]'
    messages = [
        {"role": "system", "content": "You are an assistant that suggests new tasks to improve productivity based on user's calendar."},
        {"role": "user", "content": f"Here are the calendar events:\n{text_block}\n\nSuggest 2 new useful tasks. Return in JSON array like: {prompt_json}"}
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.4
        )

        suggestion_list = json.loads(response.choices[0].message.content)

        if not isinstance(suggestion_list, list):
            raise ValueError("GPT response is not a list.")

        for s in suggestion_list:
            required_keys = {"day", "hour", "start", "end", "notes"}
            if not required_keys.issubset(s):
                raise ValueError(f"Missing keys in suggestion: {s}")
            save_gpt_suggestion(s["day"], s["hour"], s["start"], s["end"], s["notes"])

    except Exception as e:
        st.error(f"Failed to parse or insert suggestions: {e}")

# === Sliding Chat Pane ===
def render_chat_pane():
    toggle = st.session_state.get("show_chat", False)

    col1, col2 = st.columns([10, 1])
    with col2:
        if st.button("💬", key="chat_toggle"):
            st.session_state.show_chat = not toggle

    if st.session_state.get("show_chat", False):
        with st.sidebar.expander("💬 Chat Assistant", expanded=True):
            if "chat_history" not in st.session_state:
                st.session_state.chat_history = []

            for chat in st.session_state.chat_history:
                st.markdown(f"**You:** {chat['user']}")
                st.markdown(f"**Assistant:** {chat['bot']}")
                st.markdown("---")

            user_input = st.text_input("Message", key="chat_input")
            if st.button("Send", key="send_button"):
                if user_input.strip():
                    st.session_state.chat_history.append({"user": user_input, "bot": "Thinking..."})
                    with st.spinner("Assistant thinking..."):
                        try:
                            response = client.chat.completions.create(
                                model="gpt-4",
                                messages=[
                                    {"role": "system", "content": "You are a helpful project assistant."},
                                    {"role": "user", "content": user_input}
                                ]
                            )
                            reply = response.choices[0].message.content
                            st.session_state.chat_history[-1]["bot"] = reply
                        except Exception as e:
                            st.session_state.chat_history[-1]["bot"] = f"Error: {e}"
                    st.rerun()
