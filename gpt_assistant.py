# gpt_assistant.py — Calendar AI Summary Assistant (OpenAI v1-compatible)

import streamlit as st
from supabase import create_client, Client
from openai import OpenAI
import os

# === Setup OpenAI & Supabase ===
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# === Load Events from Supabase ===
def load_all_events():
    response = supabase.table("events").select("*").order("day").execute()
    return response.data

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

    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        temperature=0.4
    )

    return response.choices[0].message.content

# === Streamlit UI ===
st.title("🧠 GPT Calendar Assistant")

if st.button("📥 Analyze My Calendar"):
    events = load_all_events()
    if events:
        with st.spinner("Thinking..."):
            summary = summarize_calendar(events)
        st.markdown("---")
        st.subheader("📋 Calendar Summary:")
        st.markdown(summary)
    else:
        st.info("No events found in your Supabase calendar.")
