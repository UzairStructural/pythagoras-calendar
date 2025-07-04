# gpt_assistant.py — GPT-powered Calendar Assistant (Refactored)

import streamlit as st
from supabase import create_client, Client
from openai import OpenAI
import os
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
        {
            "role": "system",
            "content": "You are a helpful calendar assistant that reviews daily and weekly tasks to find potential issues, overlaps, and give planning suggestions."
        },
        {
            "role": "user",
            "content": f"Here are the calendar events:\n{text_block}\n\nPlease summarize them and provide any suggestions."
        }
    ]

    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        temperature=0.4
    )

    return response.choices[0].message.content


# === Save GPT Suggestions to Supabase ===
def save_gpt_suggestion(day, hour, start, end, notes):
    suggestion = {
        "id": str(uuid.uuid4()),
        "day": day,
        "hour": hour,
        "start": start,
        "end": end,
        "notes": notes
    }
    supabase.table("gpt_suggestions").insert(suggestion).execute()

# === Generate Example Suggestions with GPT ===
def generate_gpt_suggestions(events):
    text_block = format_events(events)
    messages = [
        {"role": "system", "content": "You are an assistant that suggests new tasks to improve productivity based on user's calendar."},
        {"role": "user", "content": f"Here are the calendar events:\n{text_block}\n\nSuggest 2 new useful tasks. Return in JSON array like: [{\"day\":\"2025-07-03\",\"hour\":9,\"start\":\"9 AM\",\"end\":\"10 AM\",\"notes\":\"Team sync\"}, ...]"}
    ]

    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        temperature=0.4
    )

    try:
        suggestion_list = json.loads(response.choices[0].message.content)

        if not isinstance(suggestion_list, list):
            raise ValueError("GPT response is not a list.")

        for s in suggestion_list:
            required_keys = {"day", "hour", "start", "end", "notes"}
            if not required_keys.issubset(s):
                raise ValueError(f"Missing keys in suggestion: {s}")
            save_gpt_suggestion(s["day"], s["hour"], s["start"], s["end"], s["notes"])

    except Exception as e:
        st.error(f"Failed to parse suggestions: {e}")
