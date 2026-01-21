import warnings
import pathlib
import datetime as dt
from datetime import date
from st_on_hover_tabs import on_hover_tabs
import streamlit_shadcn_ui as ui
from auth import register_user, login_user
import re
from streamlit_cookies_manager import EncryptedCookieManager
import streamlit as st
from tasks import get_monthly_progress, get_task_count, get_checklist_tasks, add_draft_checklist_item, create_task, get_tasks, get_task_by_id, delete_task, update_task, add_checklist_item,  done_checklist, mark_overdue_tasks, get_checklist, calc_task_progress, add_edit_checklist_item
from database import init_db
from calendar_func import show_events_by_date, task_to_events
from dashboard import information_card, project_progress_card, today_tasks_card, monthly_progress_card
from mail import run_email_scheduler
from ai_engine import ai_assistant
import pytz

## page setup
st.set_page_config(page_title='Task & Project Management System', layout='wide')
warnings.filterwarnings("ignore", category=DeprecationWarning)
init_db()
## cookie management
cookies = EncryptedCookieManager(prefix="taskapp_", password="my_secret_key_123")
css_path = pathlib.Path(__file__).parent / "style.css"

if not cookies.ready():
    st.stop()

PK_TZ = pytz.timezone("Asia/Karachi")

today = dt.datetime.now(PK_TZ).date()

# initialize session state
if "last_email_date" not in st.session_state:
    st.session_state.last_email_date = None

# run email reminder only once per day
if st.session_state.last_email_date != today:
    try:
        run_email_scheduler()
        st.session_state.last_email_date = today
        print("Email reminder executed successfully")
    except Exception as e:
        print("Email reminder failed:", e)
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
if "draft_checklist" not in st.session_state:
    st.session_state.draft_checklist = []

if "checklist_input" not in st.session_state:
    st.session_state.checklist_input = ""
if "edit_checklist_input" not in st.session_state:
    st.session_state.edit_checklist_input = ""

if "edit_checklist" not in st.session_state:
    st.session_state.edit_checklist = []


## validation email
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(pattern, email) is not None

## =======================
## APP (AFTER LOGIN)
## =======================
if st.session_state.user:
    mark_overdue_tasks()
    tasks_list = get_tasks(st.session_state.user["id"])
    st.markdown(
    f"<style>{css_path.read_text()}</style>",
    unsafe_allow_html=True
    )

    st.markdown("""
        <style>
        .task-row {
            padding: 14px 0;
            display: flex;
            align-items: center;
        }
        .task-row-1 {
            padding: 14px 0;
            display: flex;
            align-items: center;
        }
        .task-row-2 {
            padding: 14px 0;
            display: flex;
            align-items: center;
        }
        .task-row-3 {
            padding: 14px 0;
            display: flex;
            align-items: center;
        }
        .task-row-btn{
            padding: 0 0;
            display: flex;
            align-items: center;
            font-size: 8px;
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


   ## ---------------- HOMEPAGE STARTS -----------------------

    if tabs == 'Home':
        username = st.session_state.user["username"]
        st.markdown("<h3>Welcome back, {}</h3>".format(username), unsafe_allow_html=True)
        st.markdown('<br>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            task_count = get_task_count(st.session_state.user["id"])
            total_tasks, overdue_tasks, todo_tasks, in_progress_tasks, completed_tasks = task_count.values()
            information_card(total_tasks,overdue_tasks,todo_tasks,in_progress_tasks,completed_tasks)
            today_task = []
            for task in tasks_list:
                if task[3] == str(date.today()):
                    today_task.append(task[1])
            today_tasks_card(today_task)  
        with c2:
            total_tasks, percent_change, stats = get_monthly_progress(st.session_state.user["id"])
            monthly_progress_card(total_tasks, percent_change, stats)  
            task_ids = get_checklist_tasks(st.session_state.user["id"])
            task_list = []
            task_pct = []
            # st.write(task_ids)
            for id in task_ids:
                task = get_task_by_id(id[0], st.session_state.user["id"])
                task_perc = calc_task_progress(id[0])
                if task_perc:
                    task_pct.append(task_perc)
                else:
                    task_pct.append(0)
                if task:
                    task_list.append(task[0])
            project_progress_card(task_list, task_pct)


    ## ---------------- HOMEPAGE ENDS -----------------------  
        
  ## --------------- TASKS PAGE STARTS ----------------------

    elif tabs == 'Tasks':
        st.title("Tasks Management")

        ## ------------ ADDING TASK BLOCK ---------------------

        if "show_add_task" not in st.session_state:
            st.session_state.show_add_task = False
        col1, col2,col3,col4,col5,col6  = st.columns(6)

        ## CREATING COLUMNS FOR TAB AND ADD TASK
        with st.spinner('Loading...'):
            # with col1: 
            #     tabs = ui.tabs(options=['List'], default_value='List', key="kanaries")
            with col6:
                task_btn = ui.button("➕ Add Task", key='task_btn')

        # ----------- This part creates task ------------------
        if task_btn:
            st.session_state.show_add_task = True

        # TASK CARD
        if st.session_state.show_add_task:

            with st.container(width=900, height=400, border=True):
                st.subheader("Task Details")

                task_title = st.text_input(
                    "Task Name",
                    placeholder="Enter task name",
                    key = "task_name_input"
                )

                col1, col2, col3 = st.columns(3)

                with col1:
                    task_due_date = st.date_input("Due Date", key='task_date_input')

                with col2:
                    task_priority = st.selectbox(
                        "Priority",
                        ["Low", "Normal", "High", "Urgent"],
                        key = "priority_add",
                        index=1
                    )

                with col3:
                    task_status = st.selectbox(
                        "Status",
                        ["⚫ TO DO", "🔵 IN PROGRESS", "✅️ COMPLETE"],
                        key = "status_add"
                    )

                st.subheader('Add Checklist')

                st.text_input(
                        "Add checklist item",
                        placeholder="eg. Design UI mockups",
                        key="checklist_input",
                        on_change=add_draft_checklist_item
                    )
                for i, item in enumerate(st.session_state.draft_checklist):
                    checked = st.checkbox(
                        item["title"],
                        value=item["checked"],
                        key=f"draft_checkbox_{i}"
                    )
                    st.session_state.draft_checklist[i]["checked"] = checked
                c1, c2,_ = st.columns([1,1,6])

                with c1:
                    st.markdown('<div class="task-actions">', unsafe_allow_html=True)
                    cancel_btn = ui.button("Cancel", variant='secondary', key="cancel_task_btn")
                    st.markdown('</div>', unsafe_allow_html=True)
                    if cancel_btn:
                        st.session_state.show_add_task = False
                        st.session_state.draft_checklist = []
                        st.rerun()

                with c2:
                    st.markdown('<div class="task-actions">', unsafe_allow_html=True)
                    save_btn = ui.button("Save", key="save_task_btn")
                    st.markdown('</div>', unsafe_allow_html=True)
                    if save_btn:
                        if not task_title:
                            st.error("Task name is required")
                        else:
                            task_id =create_task(
                                st.session_state.user["id"],
                                task_title,
                                "",
                                task_priority,
                                task_due_date,
                                task_status

                            )
                            for item in st.session_state.draft_checklist:
                                add_checklist_item(task_id, item["title"],st.session_state.user["id"], item["checked"])
            
                            st.session_state.show_add_task = False
                            st.session_state.draft_checklist = []
                            st.success("Task added")
                            st.rerun()

        ## ------------ ADD TASK BLOCK ENDS HERE---------------------


        ## --------------- THIS BLOCK SHOW TASKS IN LIST ---------------
        # if tabs == 'List':
        with st.container(width=1200,border=True):
                        if tasks_list:
                            
                            col1, col2, col3, col4, col5, col6 = st.columns([3,2,2,2,1,1])
                            col1.markdown("**Title**")
                            col3.markdown("**Priority**")
                            col2.markdown("**Due Date**")
                            col4.markdown("**Status**")
                            col5.markdown("Edit")
                            col6.markdown("Delete")

                            ## CRUD STARTS
                            for task in tasks_list:
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
                                    st.markdown("<div class='task-row-1'>", unsafe_allow_html=True)
                                    if status == 'OVERDUE':
                                        st.write(f':red[{priority}]')
                                    elif status == "✅️ COMPLETE" or status == "COMPLETE":
                                        st.write(f':green[{priority}]') 
                                    else:
                                        st.write(priority)
                                    st.markdown("</div>", unsafe_allow_html=True)
                                with col3: 
                                    st.markdown("<div class='task-row-2'>", unsafe_allow_html=True)
                                    if status == 'OVERDUE':
                                        st.write(f':red[{due_date}]')
                                    elif status == "✅️ COMPLETE" or status == "COMPLETE":
                                        st.write(f':green[{due_date}]') 
                                    else:
                                        st.write(due_date)
                                    st.markdown("</div>", unsafe_allow_html=True)


                                with col4:
                                    st.markdown("<div class='task-row-3'>", unsafe_allow_html=True)
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
                                    edit_btn = st.button("Edit", key=f"edit_btn{task_id}")
                                    st.markdown("</div>", unsafe_allow_html=True)
                                    if edit_btn:
                                            st.session_state.edit_task_id = task_id
                                            st.rerun()
                                    
                                    
                                ## delete task
                                with col6:
                                    st.markdown("<div class='task-row-btn'>", unsafe_allow_html=True)
                                    delete_btn = st.button("x", key=f"delete_btn_{task_id}", type='primary')
                                    st.markdown("</div>", unsafe_allow_html=True)
                                    if delete_btn:
                                        delete_task(task_id, st.session_state.user["id"])
                                        st.rerun()
                                    

                        else:
                            st.info("No tasks found.")
                        ## CRUD ENDS

        ## EDIT BUTTON FUNCTIONALITY
        if st.session_state.get("edit_task_id"):

            task_id = st.session_state.edit_task_id
            edit_task = get_task_by_id(task_id, st.session_state.user["id"])
            if "edit_checklist_loaded" not in st.session_state or st.session_state.edit_checklist_loaded != task_id:
                st.session_state.edit_checklist = [
                    {"id": row[0], "title": row[1], "checked": bool(row[2])}
                    for row in get_checklist(task_id)
                ]
                st.session_state.edit_checklist_loaded = task_id

            if edit_task:
                title, description, priority, due_date, status = edit_task

                with st.container(border=True):
                    st.subheader("Edit Task")

                    new_title = st.text_input("Task Name", value=title, key='edit_title')

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        new_due_date = st.date_input(
                            "Due Date",
                            dt.datetime.strptime(due_date, "%Y-%m-%d").date(),
                            key='edit_date'
                        )

                    with col2:
                        
                        valid_priority = ["Low", "Normal", "High", "Urgent"]
                        new_priority = st.selectbox(
                            "Priority",
                            valid_priority,
                            key = "prirority_add",
                            index=valid_priority.index(priority)
                        )

                    with col3:
                        valid_status = ["⚫ TO DO", "🔵 IN PROGRESS", "✅️ COMPLETE"]
                        if status == 'OVERDUE':
                            valid_status = ["⚫ TO DO", "🔵 IN PROGRESS", "✅️ COMPLETE",'OVERDUE']
                        new_status = st.selectbox(
                            "Status",
                            valid_status,
                            index=valid_status.index(status),
                            key = "status_add"
                        )
                    st.subheader('Edit Checklist')
                    st.text_input(
                        "Add checklist item",
                        placeholder="eg. Design UI mockups",
                        key="edit_checklist_input",
                        on_change=add_edit_checklist_item
                    )
                    for i, item in enumerate(st.session_state.edit_checklist):
                        st.session_state.edit_checklist[i]["checked"] = st.checkbox(
                            item["title"],
                            value=item["checked"],
                            key=f"edit_checkbox_{i}"
                        )
                    c1, c2,_ = st.columns([1,1,6])

                    with c1:
                        if st.button("Cancel", key='cancel_edit'):
                            st.session_state.edit_checklist = []
                            st.session_state.edit_task_id = None
                            st.session_state.edit_checklist_loaded = None
                            st.rerun()

                    with c2:
                        if st.button("Confirm", type="secondary", key='confirm_edit'):
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
                                for item in st.session_state.edit_checklist:
                                    if item["id"] is not None:
                                        done_checklist(item["id"], item["checked"])
                                    else:
                                        add_checklist_item(st.session_state.edit_task_id, item["title"], st.session_state.user["id"], item["checked"])
                                st.session_state.edit_checklist = [] 
                                st.session_state.edit_task_id = None
                                st.session_state.edit_checklist_loaded = None
                                st.success("Task updated")
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

    login_username = st.text_input("Username", key='get_username').lower()
    login_password = st.text_input("Password", type="password", key='get_password')

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

    reg_username = st.text_input("Enter Username", key='register_user').lower()
    reg_email = st.text_input("Enter Email", key='get_mail')
    reg_password = st.text_input("Enter Password", type="password", key='reg_password')

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

































