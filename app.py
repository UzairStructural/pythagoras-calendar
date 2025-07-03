import streamlit as st
import datetime
import uuid
import json
import os
from openai import OpenAI

# === SETUP ===
st.set_page_config(page_title="🧠 Pythagoras Calendar", layout="wide")
import streamlit as st
import datetime
import uuid
from openai import OpenAI
import os
import json

st.set_page_config(page_title="Pythagoras Calendar", layout="wide")

# ⬛ Custom styling from top controls
if "bg_color" not in st.session_state:
    st.session_state.bg_color = "#1c1c1e"
if "hour_height" not in st.session_state:
    st.session_state.hour_height = 60
if "time_divisions" not in st.session_state:
    st.session_state.time_divisions = 10
if "view_mode" not in st.session_state:
    st.session_state.view_mode = "Week"

# Top Ribbon Menu
with st.container():
    st.markdown("## 📅 Pythagoras Calendar View")
    col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 2, 2])

    with col1:
        st.session_state.view_mode = st.selectbox("View", ["Week", "Month"], key="view_mode_toggle")

    with col2:
        year = st.selectbox("Year", list(range(datetime.datetime.now().year - 5, datetime.datetime.now().year + 6)))
        month = st.selectbox("Month", list(range(1, 13)), format_func=lambda x: datetime.date(1900, x, 1).strftime('%B'))

    with col3:
        st.session_state.bg_color = st.color_picker("🎨 Background", st.session_state.bg_color)

    with col4:
        st.session_state.hour_height = st.slider("🔼 Hour Height (px)", 10, 100, st.session_state.hour_height)

    with col5:
        st.session_state.time_divisions = st.selectbox("📏 Time Divisions / Hour", [4, 6, 10])

st.markdown("---")

st.markdown("<style>body { background-color: #1c1c1e; color: #e0e0e0; font-family: Inter, sans-serif; }</style>", unsafe_allow_html=True)

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
TASKS_FILE = "tasks.json"

# === UTILITIES ===
def load_tasks():
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, "r") as f:
            return json.load(f)
    return []

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
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a detail-oriented project management assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

# === SESSION INIT ===
if "tasks" not in st.session_state:
    raw_tasks = load_tasks()
    for t in raw_tasks:
        t["datetime"] = datetime.datetime.fromisoformat(t["datetime"])
    st.session_state.tasks = raw_tasks

# === SIDEBAR INPUT ===
with st.sidebar:
    st.header("➕ Add New Task")
    name = st.text_input("Task Name")
    date = st.date_input("Due Date", datetime.date.today())
    time = st.time_input("Due Time", datetime.time(9, 0))
    priority = st.selectbox("Priority", ["High", "Medium", "Low"])
    notes = st.text_area("Notes")
    if st.button("Add Task"):
        new_task = {
            "id": str(uuid.uuid4()),
            "name": name,
            "datetime": datetime.datetime.combine(date, time),
            "priority": priority,
            "notes": notes
        }
        st.session_state.tasks.append(new_task)
        save_tasks(st.session_state.tasks)
        st.success("✅ Task added!")

# === HEADER NAVIGATION ===
st.markdown("<h2 style='text-align: center;'>📅 Weekly Calendar - {}</h2>".format(datetime.date.today().strftime("%B %Y")), unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 5, 1])
with col1:
    if st.button("Today"):
        st.experimental_rerun()
with col3:
    view = st.radio("View Mode", ["Week", "Day", "Month"], horizontal=True, label_visibility="collapsed")

# === WEEK SETUP ===
today = datetime.date.today()
start = today - datetime.timedelta(days=today.weekday())  # Monday
days = [start + datetime.timedelta(days=i) for i in range(7)]
hour_range = [datetime.time(h, 0) for h in range(8, 21)]  # 8AM to 8PM

# === SEARCH BAR ===
search = st.text_input("🔍 Search events...", "")
# === TASK EDIT POPUP PANEL ===
if "selected_task_id" in st.session_state and st.session_state["selected_task_id"]:
    task_to_edit = next((t for t in st.session_state.tasks if t["id"] == st.session_state["selected_task_id"]), None)
    if task_to_edit:
        st.markdown("### ✏️ Edit Task")
        new_name = st.text_input("Task Name", task_to_edit["name"])
        new_date = st.date_input("Due Date", task_to_edit["datetime"].date())
        new_time = st.time_input("Due Time", task_to_edit["datetime"].time())
        new_priority = st.selectbox("Priority", ["High", "Medium", "Low"], index=["High", "Medium", "Low"].index(task_to_edit["priority"]))
        new_notes = st.text_area("Notes", task_to_edit["notes"])

        col_save, col_delete = st.columns(2)
        with col_save:
            if st.button("💾 Save"):
                task_to_edit["name"] = new_name
                task_to_edit["datetime"] = datetime.datetime.combine(new_date, new_time)
                task_to_edit["priority"] = new_priority
                task_to_edit["notes"] = new_notes
                save_tasks(st.session_state.tasks)
                st.session_state["selected_task_id"] = None
                st.success("✅ Task updated!")
                st.experimental_rerun()
        with col_delete:
            if st.button("🗑️ Delete"):
                st.session_state.tasks = [t for t in st.session_state.tasks if t["id"] != task_to_edit["id"]]
                save_tasks(st.session_state.tasks)
                st.session_state["selected_task_id"] = None
                st.success("🗑️ Task deleted.")
                st.experimental_rerun()


# === CALENDAR GRID ===
st.markdown("---")
grid = st.columns([1] + [1 for _ in days])
with grid[0]:
    for t in hour_range:
        st.markdown(f"<div style='height:60px;border-bottom:1px solid #2e2e30;'>{t.strftime('%I:%M %p')}</div>", unsafe_allow_html=True)

for i, day in enumerate(days):
    with grid[i + 1]:
        st.markdown(f"<div style='text-align:center;font-weight:bold;'>{day.strftime('%a')}<br>{day.day}</div>", unsafe_allow_html=True)
        col_tasks = [t for t in st.session_state.tasks if t["datetime"].date() == day and search.lower() in t["name"].lower()]
        for t in col_tasks:
            hour = t["datetime"].time().hour
            offset = (hour - 8) * 60  # top offset in px
            color = {"High": "#e74c3c", "Medium": "#f1c40f", "Low": "#2ecc71"}[t["priority"]]
            block = f"""
            <div style="
                background-color:{color};
                padding:6px;
                margin-top:{offset}px;
                border-radius:6px;
                font-size:13px;
                color:white;
                position:relative;
            ">
                <b>{t['name']}</b><br>
                {t['datetime'].strftime('%I:%M %p')} - {t['priority']}
            </div>
            """
           if st.button(f"🟩 {t['name']} ({t['priority']}) - {t['datetime'].strftime('%I:%M %p')}", key=t["id"]):
    st.session_state["selected_task_id"] = t["id"]


# === ASK PYTHAGORAS REVIEW ===
task_summary = ""
for t in st.session_state.tasks:
    task_summary += f"- {t['datetime'].strftime('%Y-%m-%d %H:%M')} | {t['name']} ({t['priority']}): {t['notes']}\n"
if st.button("🔍 Ask Pythagoras to review my schedule"):
    ai_response = ask_pythagoras(task_summary)
    st.subheader("🤖 Pythagoras says:")
    st.info(ai_response)

# === GPT API TEST ===
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

# === FOOTER ===
st.markdown("---")
st.caption("🔧 Built for Uzair | Pythagoras AI Project Manager")
