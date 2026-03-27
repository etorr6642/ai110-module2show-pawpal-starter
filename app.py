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

category = st.selectbox("Time of day", ["morning", "afternoon", "evening"])
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
                frequency=ps.Frequency.DAILY,
                priority=priority,
                category=category,
                required=required,
            )
            st.session_state.pet.add_task(task)
            st.success(f"Added task: {task_title}")

# Show current tasks
if st.session_state.pet and st.session_state.pet.tasks:
    st.write("Current tasks:")
    st.table([
        {
            "Task": t.description,
            "Duration (min)": t.duration_minutes,
            "Priority": t.priority,
            "Category": t.category,
            "Required": t.required,
        }
        for t in st.session_state.pet.tasks
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
        summary = scheduler.get_schedule_summary(schedule)
        st.markdown("### Today's Schedule")
        st.text(summary)
