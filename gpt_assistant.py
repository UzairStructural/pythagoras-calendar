# gpt_assistant.py — GPT-powered Calendar Assistant (Refactored) with Sliding Chat UI 

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

# === Sliding Chat Pane (Right Side) ===
def render_chat_pane():
    if "show_chat" not in st.session_state:
        st.session_state.show_chat = False
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    st.markdown("### 💬 Assistant Chat")
    chat_container = st.container()
    with chat_container:
        for entry in st.session_state.chat_history:
            st.markdown(f"**You:** {entry['user']}")
            st.markdown(f"**Assistant:** {entry['bot']}")
            st.markdown("---")

        col1, col2 = st.columns([5, 1])
        with col1:
            user_input = st.text_input("Message", key="chat_input")
        with col2:
            if st.button("Send", key="send_msg"):
                if user_input.strip():
                    st.session_state.chat_history.append({"user": user_input, "bot": "Thinking..."})
                    with st.spinner("Assistant thinking..."):
                        try:
                            events = load_all_events()
                            formatted_events = format_events(events)

                            response = client.chat.completions.create(
                                model="gpt-4",
                                messages=[
                                    {"role": "system", "content": "You are a helpful project assistant. User's calendar is:\n" + formatted_events},
                                    {"role": "user", "content": user_input}
                                ]
                            )
                            reply = response.choices[0].message.content
                            st.session_state.chat_history[-1]["bot"] = reply
                        except Exception as e:
                            st.session_state.chat_history[-1]["bot"] = f"Error: {e}"
                    st.rerun()

    # === GPT API Connection Test ===
    st.markdown("---")
    if st.button("✅ Test GPT API Connection"):
        try:
            test_response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a connection tester."},
                    {"role": "user", "content": "Respond with the word 'connected' if the GPT API key is valid."}
                ]
            )
            test_msg = test_response.choices[0].message.content
            st.success(f"GPT API is working: {test_msg}")
        except Exception as e:
            st.error(f"❌ GPT API connection failed: {e}")
