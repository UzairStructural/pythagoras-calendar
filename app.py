import streamlit as st
import datetime
import uuid
from openai import OpenAI  # ✅ updated
import os

st.set_page_config(page_title="Pythagoras Calendar", layout="wide")
st.title("📅 Pythagoras Task Calendar")

# Load OpenAI API key from secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])  # ✅ updated

def ask_pythagoras(tasks):
    prompt = f"""
You are Pythagoras, a project manager AI assistant created by Uzair Ahmed Mohammed.
Your goal is to review upcoming calendar tasks and identify:
- Conflicts, overload, or missing follow-ups
- Which tasks are high-stakes vs low-stakes
- Suggestions to reschedule or batch tasks
- Any risk if Uzair misses something

Tasks:
{tasks}

Respond clearly and as a proactive assistant.
"""
    response = client.chat.completions.create(  # ✅ updated
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a detail-oriented project management assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content  # ✅ updated

# Initialize session state for tasks
if "tasks" not in st.session_state:
    st.session_state.tasks = []

# Sidebar for task input
with st.sidebar:
    st.header("➕ Add New Task")
    task_name = st.text_input("Task Name")
    task_date = st.date_input("Due Date", datetime.date.today())
    task_time = st.time_input("Due Time", datetime.time(9, 0))
    task_priority = st.selectbox("Priority", ["High", "Medium", "Low"])
    task_notes = st.text_area("Notes")

    if st.button("Add Task"):
        st.session_state.tasks.append({
            "id": str(uuid.uuid4()),
            "name": task_name,
            "datetime": datetime.datetime.combine(task_date, task_time),
            "priority": task_priority,
            "notes": task_notes,
        })
        st.success("✅ Task added!")

# Display calendar
st.subheader("📆 Tasks This Week")
today = datetime.date.today()
week_days = [today + datetime.timedelta(days=i) for i in range(7)]

# 🔄 Format all tasks for GPT
task_summary = ""
for t in st.session_state.tasks:
    task_summary += f"- {t['datetime'].strftime('%Y-%m-%d %H:%M')} | {t['name']} ({t['priority']}): {t['notes']}\n"

if st.button("🔍 Ask Pythagoras to review my schedule"):
    ai_response = ask_pythagoras(task_summary)
    st.subheader("🤖 Pythagoras says:")
    st.info(ai_response)

# ✅ GPT API Connection Test Button
if st.button("🧪 Test GPT Connection"):
    test_prompt = "Just confirm that GPT-4o is connected properly."
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": test_prompt}
        ]
    )
    st.success("✅ GPT API Responded:")
    st.info(response.choices[0].message.content)

# Now render the calendar columns
cols = st.columns(7)
for i, day in enumerate(week_days):
    with cols[i]:
        st.markdown(f"**{day.strftime('%A')}**")
        st.markdown(f"*{day.strftime('%Y-%m-%d')}*")
        day_tasks = [t for t in st.session_state.tasks if t["datetime"].date() == day]
        if day_tasks:
            for t in sorted(day_tasks, key=lambda x: x["datetime"]):
                st.markdown(f"- 🕒 {t['datetime'].time().strftime('%H:%M')} - {t['name']} ({t['priority']})")
        else:
            st.markdown("`No tasks`")

# Footer
st.markdown("---")
st.caption("🔧 Built for Uzair | Pythagoras AI Project Manager")
