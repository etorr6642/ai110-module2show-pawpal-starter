import streamlit as st
import pawpal_system as ps

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

# --- Session state init ---
if "owner" not in st.session_state:
    st.session_state.owner = None
if "pet" not in st.session_state:
    st.session_state.pet = None

st.divider()

# --- Add a Pet ---
st.subheader("Add a Pet")

owner_name = st.text_input("Owner name", value="Jordan")
available_minutes = st.number_input("Your available minutes per day", min_value=1, max_value=480, value=120)
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Create Owner & Pet"):
    existing_owner = st.session_state.owner
    existing_pet = st.session_state.pet
    if (
        existing_owner is not None
        and existing_owner.name == owner_name
        and existing_pet is not None
        and existing_pet.name == pet_name
        and existing_pet.pet_type == species
    ):
        st.warning("This owner and pet already exist.")
    else:
        owner = ps.Owner(
            name=owner_name,
            email="",
            available_minutes_per_day=int(available_minutes),
        )
        pet = ps.Pet(name=pet_name, breed="Unknown", pet_type=species)
        owner.add_pet(pet)
        st.session_state.owner = owner
        st.session_state.pet = pet
        st.success(f"Created owner {owner.name} with pet {pet.name}.")

st.divider()

# --- Schedule a Task ---
st.subheader("Add a Task")

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority (1=low, 5=high)", [1, 2, 3, 4, 5], index=4)

col4, col5 = st.columns(2)
with col4:
    category = st.selectbox("Time of day", ["morning", "afternoon", "evening"])
with col5:
    frequency_label = st.selectbox("Frequency", ["Daily", "Weekly", "Monthly", "As Needed"])

frequency_map = {
    "Daily": ps.Frequency.DAILY,
    "Weekly": ps.Frequency.WEEKLY,
    "Monthly": ps.Frequency.MONTHLY,
    "As Needed": ps.Frequency.AS_NEEDED,
}
required = st.checkbox("Required task", value=True)

if st.button("Add Task"):
    if st.session_state.pet is None:
        st.error("Create an owner and pet first.")
    else:
        duplicate = any(
            t.description == task_title and t.category == category
            for t in st.session_state.pet.tasks
        )
        if duplicate:
            st.warning(f"A '{task_title}' task in '{category}' already exists.")
        else:
            task = ps.Task(
                description=task_title,
                duration_minutes=int(duration),
                frequency=frequency_map[frequency_label],
                priority=priority,
                category=category,
                required=required,
            )
            st.session_state.pet.add_task(task)
            st.success(f"Added task: {task_title}")

# Show current tasks sorted by priority descending
if st.session_state.pet and st.session_state.pet.tasks:
    st.write("Current tasks (sorted by priority):")
    sorted_tasks = sorted(st.session_state.pet.tasks, key=lambda t: -t.priority)
    st.table([
        {
            "Task": t.description,
            "Duration (min)": t.duration_minutes,
            "Priority": t.priority,
            "Frequency": t.frequency.value,
            "Category": t.category,
            "Required": "Yes" if t.required else "No",
        }
        for t in sorted_tasks
    ])
else:
    st.info("No tasks yet. Add one above.")

st.divider()

# --- Generate Schedule ---
st.subheader("Build Schedule")

if st.button("Generate Schedule"):
    if st.session_state.owner is None:
        st.error("Create an owner and pet first.")
    else:
        scheduler = ps.Scheduler(st.session_state.owner)
        schedule = scheduler.generate_daily_schedule()

        st.markdown("### Today's Schedule")

        if not schedule:
            st.warning(
                f"No tasks fit in {st.session_state.owner.available_minutes_per_day} "
                "available minutes. Consider extending your available time or deferring "
                "lower-priority tasks."
            )
        else:
            total_time = sum(task.duration_minutes for _, task in schedule)
            st.success(
                f"Scheduled {len(schedule)} task(s) — {total_time} min total out of "
                f"{st.session_state.owner.available_minutes_per_day} min available."
            )
            st.table([
                {
                    "Pet": pet.name,
                    "Task": task.description,
                    "Duration (min)": task.duration_minutes,
                    "Priority": task.priority,
                    "Category": task.category,
                    "Required": "Yes" if task.required else "No",
                }
                for pet, task in schedule
            ])

        # Remaining tasks that didn't fit
        remaining = scheduler.get_remaining_tasks(schedule)
        if remaining:
            st.markdown("**Tasks that didn't fit:**")
            st.table([
                {
                    "Pet": pet.name,
                    "Task": task.description,
                    "Duration (min)": task.duration_minutes,
                    "Priority": task.priority,
                    "Required": "Yes" if task.required else "No",
                }
                for pet, task in remaining
            ])

        # Conflict warnings from Scheduler.detect_conflicts
        conflicts = scheduler.detect_conflicts(schedule)
        if conflicts:
            st.markdown("**Warnings:**")
            for conflict in conflicts:
                st.warning(conflict)
