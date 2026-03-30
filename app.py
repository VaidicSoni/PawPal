import streamlit as st
from datetime import datetime, timedelta
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# --- INITIALIZE SESSION STATE ---
if "owner" not in st.session_state:
    # Stretch Goal 2: Try to load from JSON first, otherwise create new
    loaded_owner = Owner.load_from_json()
    if loaded_owner:
        st.session_state.owner = loaded_owner
    else:
        st.session_state.owner = Owner("Default Owner")

owner = st.session_state.owner
scheduler = Scheduler(owner)

def save_data():
    owner.save_to_json()
    st.toast("Data saved successfully!", icon="💾")

# --- UI LAYOUT ---
st.title("🐾 PawPal+ Dashboard")
st.markdown("Manage your pet care routines intelligently. Uses priority-based sorting and conflict detection.")

# 1. Add Pet Section
with st.expander("🐶 Add a Pet"):
    with st.form("add_pet_form"):
        p_name = st.text_input("Pet Name")
        p_species = st.selectbox("Species", ["Dog", "Cat", "Bird", "Reptile", "Other"])
        p_age = st.number_input("Age", min_value=0, max_value=50, step=1)
        if st.form_submit_button("Add Pet"):
            if p_name:
                owner.add_pet(Pet(p_name, p_species, p_age))
                save_data()
                st.success(f"Added {p_name} to the family!")
            else:
                st.error("Pet name is required.")

# 2. Add Task Section
with st.expander("📅 Schedule a Task", expanded=True):
    if not owner.pets:
        st.warning("Please add a pet first!")
    else:
        with st.form("add_task_form"):
            pet_names = [p.name for p in owner.pets]
            selected_pet = st.selectbox("Select Pet", pet_names)
            
            t_desc = st.text_input("Task Description")
            
            col1, col2 = st.columns(2)
            with col1:
                t_date = st.date_input("Date")
                t_duration = st.number_input("Duration (mins)", min_value=1, value=15)
            with col2:
                t_time = st.time_input("Time")
                t_priority = st.selectbox("Priority", ["High", "Medium", "Low"])
                t_freq = st.selectbox("Frequency", ["Once", "Daily", "Weekly"])
                
            if st.form_submit_button("Schedule Task"):
                if t_desc:
                    due_datetime = datetime.combine(t_date, t_time)
                    new_task = Task(t_desc, due_datetime, t_duration, t_priority, t_freq)
                    
                    # Find pet and add task
                    for p in owner.pets:
                        if p.name == selected_pet:
                            p.add_task(new_task)
                            break
                    save_data()
                    st.success("Task scheduled!")
                else:
                    st.error("Description is required.")

st.divider()

# 3. Schedule View & Conflict Detection
st.subheader("📋 Your Upcoming Schedule")

# Detect Conflicts
conflicts = scheduler.check_conflicts()
if conflicts:
    for c in conflicts:
        st.error(c, icon="🚨")

# Display Tasks
upcoming_tasks = scheduler.get_upcoming_tasks()

if not upcoming_tasks:
    st.info("No upcoming tasks! Enjoy your free time with your pets.")
else:
    # Stretch Goal 4: Professional UI Formatting
    priority_colors = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}
    
    for pet_name, task in upcoming_tasks:
        with st.container(border=True):
            col1, col2, col3 = st.columns([1, 4, 1])
            
            with col1:
                st.write(f"**{task.due_time.strftime('%I:%M %p')}**")
                st.caption(task.due_time.strftime('%b %d'))
            
            with col2:
                st.markdown(f"{priority_colors[task.priority]} **{task.description}** ({pet_name})")
                st.caption(f"⏱️ {task.duration_mins} mins | 🔄 {task.frequency}")
                
            with col3:
                # Mark Complete Button
                if st.button("Complete", key=task.id):
                    if scheduler.complete_and_reschedule(pet_name, task.id):
                        save_data()
                        st.rerun()

st.divider()

# Advanced Feature: Find Next Slot
st.subheader("🤖 Smart Assistant: Find Free Slot")
colA, colB = st.columns([3, 1])
with colA:
    slot_duration = st.number_input("Task Duration needed (minutes)", min_value=5, value=30)
with colB:
    st.write("") # spacing
    st.write("")
    if st.button("Find Slot"):
        now = datetime.now()
        start_search = now.replace(second=0, microsecond=0)
        next_slot = scheduler.find_next_available_slot(start_search, slot_duration)
        st.success(f"Best available slot starts at: **{next_slot.strftime('%A, %b %d at %I:%M %p')}**")