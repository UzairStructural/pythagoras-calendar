import streamlit as st
import datetime
import uuid

st.set_page_config(page_title="Pythagoras Calendar", layout="wide")
st.title("📅 Pythagoras Task Calendar")

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
