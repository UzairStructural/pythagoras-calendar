# gpt_assistant.py – lightweight GPT-based Calendar Interaction

import openai
import os
from supabase import create_client, Client
import datetime

# === 1. Supabase Setup ===
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# === 2. OpenAI Setup ===
openai.api_key = os.environ.get("OPENAI_API_KEY")

def fetch_all_calendar_events():
    response = supabase.table("events").select("*").execute()
    return response.data

def summarize_calendar(events):
    messages = [
        {"role": "system", "content": "You are a helpful assistant that summarizes calendar schedules and suggests improvements."},
        {"role": "user", "content": f"Here are this week's tasks: {events}\n\nSummarize key days, detect overloads, and suggest better scheduling."}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        temperature=0.4
    )

    return response.choices[0].message['content']

def run_summary():
    events = fetch_all_calendar_events()
    summary = summarize_calendar(events)
    print("\n===== AI SUMMARY =====")
    print(summary)

if __name__ == "__main__":
    run_summary()
