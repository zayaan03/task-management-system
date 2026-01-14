import warnings
import pathlib
import datetime as dt
from st_on_hover_tabs import on_hover_tabs
import streamlit_shadcn_ui as ui
from auth import register_user, login_user
import re
from streamlit_cookies_manager import EncryptedCookieManager
import streamlit as st
from tasks import create_task, get_tasks, get_task_by_id, delete_task, update_task, mark_overdue_tasks
from database import init_db
from ui import show_events_by_date

## page setup
st.set_page_config(page_title='Task & Project Management System', layout='wide')
warnings.filterwarnings("ignore", category=DeprecationWarning)
init_db()
mark_overdue_tasks()
## cookie management
cookies = EncryptedCookieManager(prefix="taskapp_", password="my_secret_key_123")
css_path = pathlib.Path(__file__).parent / "style.css"

if not cookies.ready():
    st.stop()

# session state initialize
if 'user' not in st.session_state:
    st.session_state.user = None

if "show_add_task" not in st.session_state:
    st.session_state.show_add_task = False

if st.session_state.user is None:
    if cookies.get("logged_in") == "true":
        st.session_state.user = {
            "id": cookies.get("user_id"),
            "username": cookies.get("username"),
            "email": None
        }

## validation email
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(pattern, email) is not None

## =======================
## APP (AFTER LOGIN)
## =======================
if st.session_state.user:

    st.markdown(
    f"<style>{css_path.read_text()}</style>",
    unsafe_allow_html=True
    )

    st.markdown("""
        <style>
        .task-row {
            padding: 10px 0;
            display: flex;
            align-items: center;
        }
        .task-row-btn{
            padding: 2px 0;
            display: flex;
            align-items: center;
                }
        </style>
        """, unsafe_allow_html=True)

    ## sidebar
    with st.sidebar:

        tabs = on_hover_tabs(
            tabName=['Home', 'Tasks', 'Ai assist', 'Logout'],
            iconName=['home', 'dashboard', 'economy', 'logout'],
            default_choice=0
        )


    if tabs == 'Home':
        st.title("Welcome",st.session_state.user["username"])
        

    ## TASKS PAGE
    elif tabs == 'Tasks':
        st.title("Tasks Management")

        if "show_add_task" not in st.session_state:
            st.session_state.show_add_task = False
        col1, col2,col3,col4,col5,col6  = st.columns(6)
        with col1: 
            tabs = ui.tabs(options=['List', 'Calendar'], default_value='List', key="kanaries")
        with col6:
            task_btn = ui.button("➕ Add Task", key='clk_btn')
        if tabs == 'List':
                    with st.container(border=True):
                        tasks = get_tasks(st.session_state.user["id"])
                        if tasks:
                            
                            col1, col2, col3, col4, col5, col6 = st.columns([3,2,2,2,1,1])
                            col1.markdown("**Task Title**")
                            col3.markdown("**Priority**")
                            col2.markdown("**Due Date**")
                            col4.markdown("**Status**")
                            col5.markdown("Edit")
                            col6.markdown("Delete")

                            for task in tasks:
                                task_id, title, due_date, priority, status = task

                                with col1:
                                    st.markdown("<div class='task-row'>", unsafe_allow_html=True)
                                    if status == 'OVERDUE':
                                        st.write(f':red[{title}]')
                                    elif status == "✅️ COMPLETE" or status == "COMPLETE":
                                        st.write(f':green[{title}]') 
                                    else:
                                        st.write(title)
                                    st.markdown("</div>", unsafe_allow_html=True)
                                with col2: 
                                    st.markdown("<div class='task-row'>", unsafe_allow_html=True)
                                    if status == 'OVERDUE':
                                        st.write(f':red[{priority}]')
                                    elif status == "✅️ COMPLETE" or status == "COMPLETE":
                                        st.write(f':green[{priority}]') 
                                    else:
                                        st.write(priority)
                                    st.markdown("</div>", unsafe_allow_html=True)
                                with col3: 
                                    st.markdown("<div class='task-row'>", unsafe_allow_html=True)
                                    if status == 'OVERDUE':
                                        st.write(f':red[{due_date}]')
                                    elif status == "✅️ COMPLETE" or status == "COMPLETE":
                                        st.write(f':green[{due_date}]') 
                                    else:
                                        st.write(due_date)
                                    st.markdown("</div>", unsafe_allow_html=True)


                                with col4:
                                    st.markdown("<div class='task-row'>", unsafe_allow_html=True)
                                    if status == "TO DO" or status == "⚫ TO DO":
                                        st.badge('TO DO',icon=":material/radio_button_unchecked:", color = 'gray')
                                    elif status == "✅️ COMPLETE" or status == "COMPLETE":
                                        st.badge('Completed', icon=":material/check:", color = 'green')
                                    elif status == "🔵 IN PROGRESS" or status == 'IN PROGESS':
                                        st.badge('In Progress', icon=":material/radio_button_checked:", color = 'blue')
                                    elif status == 'OVERDUE':
                                        st.badge('Overdue', icon=":material/close_small:", color = 'red')
                                    st.markdown("</div>", unsafe_allow_html=True)

                                ## edit task

                                with col5:
                                    st.markdown("<div class='task-row-btn'>", unsafe_allow_html=True)
                                    edit_btn = ui.button("Edit", key=f"styled_btn_tailwind-{task_id}", className="bg-yellow-300 text-white h-5")
                                    st.markdown("</div>", unsafe_allow_html=True)
                                    if edit_btn:
                                            st.session_state.edit_task_id = task_id
                                            st.rerun()
                                    
                                    
                                ## delete task
                                with col6:
                                    st.markdown("<div class='task-row-btn'>", unsafe_allow_html=True)
                                    if ui.button("Delete", key=f"tyled_btn_tailwind-{task_id}", className = "bg-red-600 text-white h-5"):
                                        delete_task(task_id, st.session_state.user["id"])
                                        st.rerun()
                                    st.markdown("</div>", unsafe_allow_html=True)

                        else:
                            st.info("No tasks found.")

        if st.session_state.get("edit_task_id"):

            task_id = st.session_state.edit_task_id
            edit_task = get_task_by_id(task_id, st.session_state.user["id"])

            if edit_task:
                title, description, priority, due_date, status = edit_task

                with st.container(border=True):
                    st.subheader("Edit Task")

                    new_title = st.text_input("Task Name", value=title)

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        new_due_date = st.date_input(
                            "Due Date",
                            dt.datetime.strptime(due_date, "%Y-%m-%d").date()
                        )

                    with col2:
                        
                        valid_priority = ["Low", "Normal", "High", "Urgent"]
                        new_priority = st.selectbox(
                            "Priority",
                            valid_priority,
                            index=valid_priority.index(priority)
                        )

                    with col3:
                        valid_status = ["⚫ TO DO", "🔵 IN PROGRESS", "✅️ COMPLETE"]
                        if status == 'OVERDUE':
                            valid_status = ["⚫ TO DO", "🔵 IN PROGRESS", "✅️ COMPLETE",'OVERDUE']
                        new_status = st.selectbox(
                            "Status",
                            valid_status,
                            index=valid_status.index(status)
                        )

                    c1, c2 = st.columns(2)

                    with c1:
                        if st.button("Cancel"):
                            st.session_state.edit_task_id = None
                            st.rerun()

                    with c2:
                        if st.button("Confirm", type="secondary"):
                            if not new_title:
                                st.error("Task name is required")
                            else:
                                update_task(
                                    task_id,
                                    st.session_state.user["id"],
                                    new_title,
                                    description,                     # keep description
                                    new_priority,
                                    new_due_date.isoformat(),         # FIXED
                                    new_status
                                )
                                st.session_state.edit_task_id = None
                                st.success("Task updated")
                                st.rerun()
                            
                        
        if tabs == 'Calendar':
            show_events_by_date() 
        
        # ADD TASK BUTTON (NATIVE — RELIABLE) stLayoutWrapper
        if task_btn:
            st.session_state.show_add_task = True

        # TASK CARD
        if st.session_state.show_add_task:

            with st.container(border=True):
                st.subheader("Task Details")

                task_title = st.text_input(
                    "Task Name",
                    placeholder="Enter task name"
                )

                col1, col2, col3 = st.columns(3)

                with col1:
                    task_due_date = st.date_input("Due Date")

                with col2:
                    task_priority = st.selectbox(
                        "Priority",
                        ["Low", "Normal", "High", "Urgent"],
                        index=1
                    )

                with col3:
                    task_status = st.selectbox(
                        "Status",
                        ["⚫ TO DO", "🔵 IN PROGRESS", "✅️ COMPLETE"]
                    )

                c1, c2 = st.columns(2)

                with c1:
                    if st.button("Cancel"):
                        st.session_state.show_add_task = False
                        st.rerun()

                with c2:
                    if st.button("Save Task", type="primary"):
                        if not task_title:
                            st.error("Task name is required")
                        else:
                            create_task(
                                st.session_state.user["id"],
                                task_title,
                                "",
                                task_priority,
                                task_due_date,
                                task_status

                            )
                            st.session_state.show_add_task = False
                            st.success("Task added")
                            st.rerun()
    elif tabs == 'Ai Assist': 
        st.title("Tom")
        st.write('Name of option is {}'.format(tabs)) 
    
    ## logout 
    elif tabs == 'Logout': 
        cookies["logged_in"] = "false" 
        cookies["user_id"] = "" 
        cookies["username"] = "" 
        cookies.save() 
        st.session_state.user = None 
        st.rerun()

    st.stop()

## =======================
## AUTH SCREENS
## =======================
st.title("Task & Project Management System")

tab1, tab2 = st.tabs(["Login", "Register"])

## login tab
with tab1:
    st.subheader("Login")

    login_username = st.text_input("Username")
    login_password = st.text_input("Password", type="password")

    if st.button("Login"):
        if not login_username or not login_password:
            st.error("Please fill in all fields")
        else:
            user = login_user(login_username, login_password)
            if user:
                st.session_state.user = {
                    "id": user[0],
                    "username": user[1],
                    "email": user[2]
                }

                cookies["logged_in"] = "true"
                cookies["user_id"] = str(user[0])
                cookies["username"] = user[1]
                cookies.save()

                st.success("Login successful")
                st.rerun()
            else:
                st.error("Invalid username or password")

## register tab
with tab2:
    st.subheader("Register")

    reg_username = st.text_input("Enter Username").lower()
    reg_email = st.text_input("Enter Email")
    reg_password = st.text_input("Enter Password", type="password")

    if st.button("Register"):
        if not reg_username or not reg_email or not reg_password:
            st.error("All fields are required")
        elif not is_valid_email(reg_email):
            st.error("Please enter a valid email address")
        else:
            success = register_user(reg_username, reg_email, reg_password)
            if success:
                st.success("Registration successful. Please Login")
            else:
                st.error("Username or email already exists")








