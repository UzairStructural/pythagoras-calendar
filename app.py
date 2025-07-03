import streamlit as st
import datetime
import uuid
from openai import OpenAI  # ✅ updated
import os
import json

st.set_page_config(page_title="Pythagoras Calendar", layout="wide")
st.title("📅 Pythagoras Task Calendar")

# Load OpenAI API key from secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])  # ✅ updated

TASKS_FILE = "tasks.json"

# 🔄 Load tasks from file if available
def load_tasks():
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, "r") as f:
            return json.load(f)
    return []

# 💾 Save tasks to file
def save_tasks(tasks):
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f, default=str)

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
    raw_tasks = load_tasks()
    # Convert datetime strings back to objects
    for task in raw_tasks:
        task["datetime"] = datetime.datetime.fromisoformat(task["datetime"])
    st.session_state.tasks = raw_tasks

# Sidebar for task input
with st.sidebar:
    st.header("➕ Add New Task")
    task_name = st.text_input("Task Name")
    task_date = st.date_input("Due Date", datetime.date.today())
    task_time = st.time_input("Due Time", datetime.time(9, 0))
    task_priority = st.selectbox("Priority", ["High", "Medium", "Low"])
    task_notes = st.text_area("Notes")

    if st.button("Add Task"):
        new_task = {
            "id": str(uuid.uuid4()),
            "name": task_name,
            "datetime": datetime.datetime.combine(task_date, task_time),
            "priority": task_priority,
            "notes": task_notes,
        }
        st.session_state.tasks.append(new_task)
        save_tasks(st.session_state.tasks)
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
# ------------------ New: Calendar View Settings ------------------

view_mode = st.radio("View Mode", ["Weekly", "Daily"], horizontal=True)
search_query = st.text_input("🔍 Search tasks")
priority_filter = st.selectbox("Filter by Priority", ["All", "High", "Medium", "Low"])

filtered_tasks = [
    t for t in st.session_state.tasks
    if (search_query.lower() in t["name"].lower() or search_query.lower() in t["notes"].lower())
    and (priority_filter == "All" or t["priority"] == priority_filter)
]

hours_range = list(range(8, 22))  # 8 AM to 10 PM

# Priority color map
priority_color = {
    "High": "#ff4d4d",     # red
    "Medium": "#FFD700",   # yellow
    "Low": "#90ee90"       # green
}

# ------------------ Selected Task Editor ------------------
if "edit_task_id" in st.session_state:
    edit_task = next((t for t in st.session_state.tasks if t["id"] == st.session_state["edit_task_id"]), None)
    if edit_task:
        with st.expander("✏️ Edit Task", expanded=True):
            new_name = st.text_input("Task Name", edit_task["name"])
            new_date = st.date_input("Due Date", edit_task["datetime"].date())
            new_time = st.time_input("Due Time", edit_task["datetime"].time())
            new_priority = st.selectbox("Priority", ["High", "Medium", "Low"], index=["High", "Medium", "Low"].index(edit_task["priority"]))
            new_notes = st.text_area("Notes", edit_task["notes"])
            col1, col2 = st.columns(2)
            if col1.button("✅ Save Changes"):
                edit_task["name"] = new_name
                edit_task["datetime"] = datetime.datetime.combine(new_date, new_time)
                edit_task["priority"] = new_priority
                edit_task["notes"] = new_notes
                save_tasks(st.session_state.tasks)
                st.success("Task updated!")
                del st.session_state["edit_task_id"]
            if col2.button("🗑️ Delete Task"):
                st.session_state.tasks = [t for t in st.session_state.tasks if t["id"] != edit_task["id"]]
                save_tasks(st.session_state.tasks)
                st.warning("Task deleted.")
                del st.session_state["edit_task_id"]

# ------------------ New: Calendar Grid ------------------

if view_mode == "Weekly":
    cols = st.columns(7)
    for i, day in enumerate(week_days):
        with cols[i]:
            st.markdown(f"### {day.strftime('%a')}")
            st.markdown(f"**{day.strftime('%Y-%m-%d')}**")
            for hour in hours_range:
                time_label = f"{hour:02d}:00"
                st.markdown(f"<div style='font-size:10px; color:gray'>{time_label}</div>", unsafe_allow_html=True)
                block_tasks = [t for t in filtered_tasks if t["datetime"].date() == day and t["datetime"].hour == hour]
                for t in block_tasks:
                    color = priority_color[t["priority"]]
                    button_key = f"edit-{t['id']}"
                    if st.button(f"🕒 {t['datetime'].strftime('%H:%M')} - {t['name']}", key=button_key):
                        st.session_state["edit_task_id"] = t["id"]
                    st.markdown(
                        f"<div style='background-color:{color}; padding:4px; border-radius:6px; font-size:11px'>{t['priority']} | {t['notes']}</div>",
                        unsafe_allow_html=True
                    )

else:  # Daily View
    day = today
    st.markdown(f"## 📆 {day.strftime('%A, %Y-%m-%d')}")
    for hour in hours_range:
        time_label = f"{hour:02d}:00"
        st.markdown(f"<div style='font-size:10px; color:gray'>{time_label}</div>", unsafe_allow_html=True)
        block_tasks = [t for t in filtered_tasks if t["datetime"].date() == day and t["datetime"].hour == hour]
        for t in block_tasks:
            color = priority_color[t["priority"]]
            button_key = f"edit-{t['id']}"
            if st.button(f"🕒 {t['datetime'].strftime('%H:%M')} - {t['name']}", key=button_key):
                st.session_state["edit_task_id"] = t["id"]
            st.markdown(
                f"<div style='background-color:{color}; padding:4px; border-radius:6px; font-size:11px'>{t['priority']} | {t['notes']}</div>",
                unsafe_allow_html=True
            )

# ------------------ New: Color Legend ------------------
with st.sidebar:
    st.markdown("### 🔵 Priority Colors")
    st.markdown("- 🔴 High")
    st.markdown("- 🟡 Medium")
    st.markdown("- 🟢 Low")
