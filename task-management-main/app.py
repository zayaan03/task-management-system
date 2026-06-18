import warnings
import pathlib
import datetime as dt
from datetime import date
from st_on_hover_tabs import on_hover_tabs
import streamlit_shadcn_ui as ui
from auth import Auth, User
import re
from streamlit_cookies_manager import EncryptedCookieManager
import streamlit as st
from tasks import Task, Subtask_Item, TaskManagement, SubtaskManagement, Analytics
from dashboard import information_card, project_progress_card, today_tasks_card, monthly_progress_card
from ai_features import AIFeatures
import pytz

## page setup
st.set_page_config(page_title='Task & Project Management System', layout='wide')
warnings.filterwarnings("ignore", category=DeprecationWarning)

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

## session state initialize for functions
if 'auth' not in st.session_state:
    st.session_state['auth'] = Auth

if 'taskmanager' not in st.session_state:
    st.session_state['taskmanager'] = TaskManagement()

if 'subtasks_manage' not in st.session_state:
    st.session_state['subtasks_manage'] = SubtaskManagement()

if 'ai_features' not in st.session_state:
    st.session_state['ai_features'] = AIFeatures()

auth = st.session_state['auth']

if 'analytics' not in st.session_state:
    st.session_state['analytics'] = Analytics()

if 'user' not in st.session_state:
    st.session_state.user = None

if "show_add_task" not in st.session_state:
    st.session_state.show_add_task = False

# Restore user session from cookies if available
if st.session_state.user is None:
    if cookies.get("logged_in") == "true":
        st.session_state.user = User(
            user_id=cookies.get("user_id"),
            username=cookies.get("username"),
            email=cookies.get("email")
        )
if "draft_checklist" not in st.session_state:
    st.session_state.draft_checklist = []

if "checklist_input" not in st.session_state:
    st.session_state.checklist_input = ""
if "edit_checklist_input" not in st.session_state:
    st.session_state.edit_checklist_input = ""

if "edit_checklist" not in st.session_state:
    st.session_state.edit_checklist = []

# ensure description session key exists so we can update it from button handlers
if "description_input" not in st.session_state:
    st.session_state["description_input"] = ""

## =======================
## APP (AFTER LOGIN)
## =======================
if st.session_state.user:
    
    user_id  = st.session_state.user.user_id
    username = st.session_state.user.username
    email    = st.session_state.user.email
    tm = st.session_state['taskmanager']
    sb_tm = st.session_state['subtasks_manage']
    ai = st.session_state['ai_features']

    tm.mark_overdue_tasks()
    tasks_list = tm.get_tasks(user_id)
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
        .st-key-ai_desc_btn button {
            background-color: rgba(255, 72, 0, 0.15) !important;
            color: #f24a07 !important;
            border: #f24a07 1px solid !important;
        }
        .st-key-schedule_btn button {
            position: absolute;
            width: 150px;
            bottom: 10px;
            left: 30px;
            background-color: rgba(205, 0, 255, 0.1) !important;
            color: rgba(205, 0, 255, 1) !important;
            border: rgba(205, 0, 255, 1) 1px solid !important;
        }
        .st-key-schedule_btn button:hover {
            background-color: rgba(205, 0, 255, 1) !important;
            color: white!important;
            border: none !important;
        }
        .st-key-task_btn button {
            background-color: black !important;
            color: white !important;
            font-weight: 500;
        }
        .st-key-ai_task_btn button {
            background-color: rgba(255, 247, 0, 0.2) !important;
            color: black !important;
            border: black 1px solid !important;
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
        div[data-testid="stDialog"] + div {
            pointer-events: none;
        }
        </style>
        """, unsafe_allow_html=True)

    ## sidebar
    with st.sidebar:

        tabs = on_hover_tabs(
            tabName=['Home', 'Tasks', 'Logout'],
            iconName=['home', 'dashboard', 'logout'],
            default_choice=0
        )


   ## ---------------- HOMEPAGE STARTS -----------------------

    if tabs == 'Home':
        
        st.markdown("<h3>Welcome back, {}</h3>".format(username), unsafe_allow_html=True)
        st.markdown('<br>', unsafe_allow_html=True)
        analysis = st.session_state['analytics']
        _,c4 = st.columns([3,1])
        with c4:
            schedule_button = st.button("🤖 Generate Plan", key="schedule_btn",)
        if schedule_button:
            
            if 'day_schedule' in st.session_state:
                del st.session_state['day_schedule']
            st.session_state['show_schedule'] = True
     
        if st.session_state.get('show_schedule'):

            @st.dialog("📅 Your AI Day Plan", width="large")
            def show_schedule():

                if 'day_schedule' not in st.session_state:
                    with st.spinner("✨ AI is planning your day..."):
                        schedule = ai.generate_daily_schedule(user_id, username)
                        st.session_state['day_schedule'] = schedule
                else:
                    schedule = st.session_state['day_schedule']

                # parse sections
                sections = {
                    "greeting"    : "",
                    "overview"    : "",
                    "schedule"    : [],
                    "warnings"    : [],
                    "score"       : "",
                    "score_reason": ""
                }

                current_section = None
                for line in schedule.split('\n'):
                    line = line.strip()
                    if not line:
                        continue
                    if line.startswith("GREETING:"):
                        current_section = "greeting"
                        text = line.replace("GREETING:", "").strip()
                        if text: sections["greeting"] = text
                    elif line.startswith("DAY OVERVIEW:"):
                        current_section = "overview"
                        text = line.replace("DAY OVERVIEW:", "").strip()
                        if text: sections["overview"] = text
                    elif line.startswith("SCHEDULE:"):
                        current_section = "schedule"
                    elif line.startswith("WARNINGS:"):
                        current_section = "warnings"
                    elif line.startswith("SCHEDULE SCORE:"):
                        sections["score"] = line.replace("SCHEDULE SCORE:", "").strip()
                    elif line.startswith("SCORE REASON:"):
                        sections["score_reason"] = line.replace("SCORE REASON:", "").strip()
                    else:
                        if current_section == "greeting" and not sections["greeting"]:
                            sections["greeting"] = line
                        elif current_section == "overview" and not sections["overview"]:
                            sections["overview"] = line
                        elif current_section == "schedule" and ("→" in line or "AM" in line or "PM" in line):
                            sections["schedule"].append(line)
                        elif current_section == "warnings" and line.startswith("⚠️"):
                            sections["warnings"].append(line)

                # ── GREETING ──────────────────────────────────
                if sections["greeting"]:
                    st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, #7C3AED, #2563EB);
                        padding: 16px 20px;
                        border-radius: 12px;
                        color: white;
                        margin-bottom: 16px;
                        font-size: 15px;
                        line-height: 1.6;
                    ">{sections["greeting"]}</div>
                    """, unsafe_allow_html=True)

                # ── OVERVIEW ──────────────────────────────────
                if sections["overview"]:
                    st.markdown(f"""
                    <div style="
                        background: #F8F4FF;
                        border-left: 4px solid #7C3AED;
                        padding: 12px 16px;
                        border-radius: 0 8px 8px 0;
                        color: #1F1F1F;
                        margin-bottom: 20px;
                        font-size: 14px;
                    ">🎯 <b>Today's Focus:</b> {sections["overview"]}</div>
                    """, unsafe_allow_html=True)

                # ── SCHEDULE ──────────────────────────────────
                if sections["schedule"]:
                    st.markdown("### 🗓️ Schedule")

                    priority_colors = {
                        "URGENT": "#EF4444",
                        "HIGH"  : "#F97316",
                        "NORMAL": "#3B82F6",
                        "LOW"   : "#6B7280"
                    }

                    for item in sections["schedule"]:
                        is_break = "break" in item.lower() or "lunch" in item.lower()

                        priority_color = "#6B7280"
                        for p, color in priority_colors.items():
                            if f"[{p}]" in item.upper():
                                priority_color = color
                                break

                        if is_break:
                            st.markdown(f"""
                            <div style="
                                background: #F3F4F6;
                                padding: 8px 16px;
                                border-radius: 8px;
                                margin: 4px 0;
                                color: #6B7280;
                                font-size: 13px;
                                text-align: center;
                            ">☕ {item}</div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <div style="
                                background: white;
                                border: 1px solid #E5E7EB;
                                border-left: 4px solid {priority_color};
                                padding: 12px 16px;
                                border-radius: 0 8px 8px 0;
                                margin: 6px 0;
                                font-size: 14px;
                                color: #1F1F1F;
                            ">{item}</div>
                            """, unsafe_allow_html=True)

                # ── WARNINGS ──────────────────────────────────
                if sections["warnings"] and sections["warnings"] != ["None"]:
                    st.markdown("### ⚠️ Warnings")
                    for warning in sections["warnings"]:
                        st.warning(warning)

                # ── SCORE ─────────────────────────────────────
                if sections["score"]:
                    try:
                        score_num  = float(sections["score"].replace("/10", "").strip())
                        score_color = (
                            "#22C55E" if score_num >= 8
                            else "#F97316" if score_num >= 6
                            else "#EF4444"
                        )
                    except:
                        score_color = "#7C3AED"

                    st.markdown(f"""
                    <div style="
                        display: flex;
                        align-items: center;
                        justify-content: space-between;
                        background: #F9FAFB;
                        border: 1px solid #E5E7EB;
                        padding: 14px 20px;
                        border-radius: 12px;
                        margin-top: 20px;
                    ">
                        <span style="font-size: 14px; color: #6B7280;">
                            {sections["score_reason"]}
                        </span>
                        <span style="font-size: 22px; font-weight: bold; color: {score_color};">
                            {sections["score"]}
                        </span>
                    </div>
                    """, unsafe_allow_html=True)

                # ── BUTTONS ───────────────────────────────────
                st.markdown("<br>", unsafe_allow_html=True)
                col1, col2 = st.columns([1, 1])

                with col1:
                    if st.button("🔄 Regenerate", use_container_width=True):
                        del st.session_state['day_schedule']
                        st.rerun()
                with col2:
                    if st.button("✅ Close", use_container_width=True):
                        st.session_state['show_schedule'] = False
                        del st.session_state['day_schedule']
                        st.rerun()

            show_schedule()

        c1, c2 = st.columns(2)
        with c1:
            task_count = analysis.get_task_count(user_id)
            total_tasks, overdue_tasks, todo_tasks, in_progress_tasks, completed_tasks = task_count.values()
            information_card(total_tasks,overdue_tasks,todo_tasks,in_progress_tasks,completed_tasks)
            today_task = []
            for task in tasks_list:
                if task.due_date == str(date.today()):
                    today_task.append(task.title)
            today_tasks_card(today_task)
        with c2:
            total_tasks, percent_change, stats = analysis.get_monthly_progress(user_id)
            monthly_progress_card(total_tasks, percent_change, stats)  
            task_ids = analysis.get_subtasks(user_id)
            task_list = []
            task_pct = []
            # st.write(task_ids)
            for id in task_ids:
                task = tm.get_task_by_id(id, user_id)
                task_perc = sb_tm.calc_progress(id)
                if task_perc:
                    task_pct.append(task_perc)
                else:
                    task_pct.append(0)
                if task:
                    task_list.append(task.title)
            project_progress_card(task_list, task_pct)


#     ## ---------------- HOMEPAGE ENDS -----------------------  
        
#   ## --------------- TASKS PAGE STARTS ----------------------

    if tabs == 'Tasks':
        st.title("Tasks Management")

        ## ------------ ADDING TASK BLOCK ---------------------

        if "show_add_task" not in st.session_state:
            st.session_state.show_add_task = False
        
        col1, col2,col3,col4,col5,col6  = st.columns(6)

        with st.spinner('Loading...'):
            with col6:
                task_btn = st.button("➕ Add Task", key='task_btn')
            with col5:
                ai_task_btn = st.button("⚡ Add with AI", key='ai_task_btn')
        # ----------- This part creates task using ai------------------
        if ai_task_btn:
            st.session_state['show_nl_task'] = True
            st.session_state['nl_chat_history'] = []
            st.session_state['nl_conv_history'] = []
        if st.session_state.get('show_nl_task'):

            @st.dialog("⚡ Add Task with AI", width="large")
            def nl_task_dialog():
                
                st.markdown("""
                <div style="
                    background: linear-gradient(135deg, #7C3AED, #2563EB);
                    padding: 14px 18px;
                    border-radius: 10px;
                    color: white;
                    font-size: 14px;
                    margin-bottom: 16px;
                ">
                    💬 Describe your task naturally. I'll handle the rest.<br>
                    <small>Example: "Build a website for dental clinic by next friday, urgent"</small>
                </div>
                """, unsafe_allow_html=True)

                # initialize chat history
                if 'nl_chat_history' not in st.session_state:
                    st.session_state['nl_chat_history']  = []
                if 'nl_conv_history' not in st.session_state:
                    st.session_state['nl_conv_history']  = []
                if 'nl_task_saved' not in st.session_state:
                    st.session_state['nl_task_saved'] = False

                # show chat history
                for msg in st.session_state['nl_chat_history']:
                    if msg['role'] == 'user':
                        with st.chat_message("user"):
                            st.write(msg['text'])
                    else:
                        with st.chat_message("assistant"):
                            st.write(msg['text'])

                # if task already saved show success
                if st.session_state['nl_task_saved']:
                    st.success("✅ Task saved successfully!")
                    if st.button("➕ Add Another Task", use_container_width=True):
                        st.session_state['nl_chat_history']  = []
                        st.session_state['nl_conv_history']  = []
                        st.session_state['nl_task_saved'] = False
                        st.rerun()
                    if st.button("✅ Done", use_container_width=True):
                        st.session_state['show_nl_task']     = False
                        st.session_state['nl_chat_history']  = []
                        st.session_state['nl_conv_history']  = []
                        st.session_state['nl_task_saved']    = False
                        st.rerun()
                    return

                # chat input
                user_input = st.chat_input("Describe your task here...")

                if user_input:
                    # show user message
                    st.session_state['nl_chat_history'].append({
                        "role": "user",
                        "text": user_input
                    })

                    # call AI
                    with st.spinner("AI is thinking..."):
                        result = ai.nl_task_creation(
                            user_input         = user_input,
                            user_id            = user_id,
                            conversation_history = st.session_state['nl_conv_history']
                        )

                    if result['status'] == 'needs_info':
                        # AI needs more info — show question
                        st.session_state['nl_chat_history'].append({
                            "role": "assistant",
                            "text": result['question']
                        })
                        # add to conversation history for next turn
                        st.session_state['nl_conv_history'].append({
                            "role": "user",
                            "text": user_input
                        })
                        st.session_state['nl_conv_history'].append({
                            "role": "assistant",
                            "text": result['question']
                        })

                    elif result['status'] == 'saved':
                        # task saved — show summary
                        st.session_state['nl_chat_history'].append({
                            "role": "assistant",
                            "text": f"✅ {result['summary']}"
                        })
                        st.session_state['nl_task_saved'] = True

                    elif result['status'] == 'error':
                        st.session_state['nl_chat_history'].append({
                            "role": "assistant",
                            "text": f"❌ {result['message']}"
                        })

                    st.rerun()

            nl_task_dialog()

        # ----------- This part creates task manually------------------
        if task_btn:
            st.session_state.show_add_task = True

        # TASK CARD
        if st.session_state.show_add_task:

            with st.container(border=True):
                st.subheader("Task Details")

                task_title = st.text_input(
                    "Task Name",
                    placeholder="Enter task name",
                    key = "task_name_input"
                )
                
                ai_desc = st.button("Generate with AI", key="ai_desc_btn")

                if ai_desc:
                    if not task_title:
                        st.error("Please enter task name for AI description")
                    else:
                        with st.spinner("Generating description..."):
                            generated_desc = ai.get_task_breakdown(task_title)
                            st.session_state["description_input"] = generated_desc

                description = st.text_area(label = "Description", height = 'content',key="description_input", max_chars = 1000, placeholder="Enter task description here...")
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
    
                st.subheader('Add Subtasks')
                def add_draft_item():
                    '''This functions save the added subtasks in to draft before
                    the task is saved'''
                    text = st.session_state.checklist_input.strip()
                    if text:
                        st.session_state.draft_checklist.append({
                            "title": text,
                            "checked": False
                        })
                        st.session_state.checklist_input = ""
                st.text_input(
                        "Add subtask",
                        placeholder="eg. Design UI mockups",
                        key="checklist_input",
                        on_change=add_draft_item
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
                            task_id = tm.create_task(
                                user_id,
                                task_title,
                                description,
                                task_priority,
                                task_due_date,
                                task_status

                            )
                            for item in st.session_state.draft_checklist:
                                sb_tm.add_subtask(task_id, item["title"],user_id, item["checked"])
            
                            st.session_state.show_add_task = False
                            st.session_state.draft_checklist = []
                            st.success("Task added")
                            st.rerun()

#         ## ------------ ADD TASK BLOCK ENDS HERE---------------------


#         ## --------------- THIS BLOCK SHOW TASKS IN LIST ---------------
        with st.container(border=True):
                        if tasks_list:
                            col1, col2, col3, col4, col5, col6 = st.columns([3,2,2,2,1,1])
                            col1.markdown("**Title**")
                            col2.markdown("**Priority**")
                            col3.markdown("**Due Date**")
                            col4.markdown("**Status**")
                            col5.markdown("Edit")
                            col6.markdown("Delete")

                            ## CRUD STARTS
                            for task in tasks_list:
                                # task_id, title, due_date, priority, status = task

                                with col1:
                                    st.markdown("<div class='task-row'>", unsafe_allow_html=True)
                                    if task.status == 'OVERDUE':
                                        st.write(f':red[{task.title}]')
                                    elif task.status == "✅️ COMPLETE" or task.status == "COMPLETE":
                                        st.write(f':green[{task.title}]') 
                                    else:
                                        st.write(task.title)
                                    st.markdown("</div>", unsafe_allow_html=True)
                                with col2: 
                                    st.markdown("<div class='task-row-1'>", unsafe_allow_html=True)
                                    if task.status == 'OVERDUE':
                                        st.write(f':red[{task.priority}]')
                                    elif task.status == "✅️ COMPLETE" or task.status == "COMPLETE":
                                        st.write(f':green[{task.priority}]') 
                                    else:
                                        st.write(task.priority)
                                    st.markdown("</div>", unsafe_allow_html=True)
                                with col3: 
                                    st.markdown("<div class='task-row-2'>", unsafe_allow_html=True)
                                    if task.status == 'OVERDUE':
                                        st.write(f':red[{task.due_date}]')
                                    elif task.status == "✅️ COMPLETE" or task.status == "COMPLETE":
                                        st.write(f':green[{task.due_date}]') 
                                    else:
                                        st.write(task.due_date)
                                    st.markdown("</div>", unsafe_allow_html=True)


                                with col4:
                                    st.markdown("<div class='task-row-3'>", unsafe_allow_html=True)
                                    if task.status == "TO DO" or task.status == "⚫ TO DO":
                                        st.badge('TO DO',icon=":material/radio_button_unchecked:", color = 'gray')
                                    elif task.status == "✅️ COMPLETE" or task.status == "COMPLETE":
                                        st.badge('Completed', icon=":material/check:", color = 'green')
                                    elif task.status == "🔵 IN PROGRESS" or task.status == 'IN PROGESS':
                                        st.badge('In Progress', icon=":material/radio_button_checked:", color = 'blue')
                                    elif task.status == 'OVERDUE':
                                        st.badge('Overdue', icon=":material/close_small:", color = 'red')
                                    st.markdown("</div>", unsafe_allow_html=True)

                                ## edit task

                                with col5:
                                    st.markdown("<div class='task-row-btn'>", unsafe_allow_html=True)
                                    edit_btn = st.button("Edit", key=f"edit_btn{task.task_id}")
                                    st.markdown("</div>", unsafe_allow_html=True)
                                    if edit_btn:
                                            st.session_state.edit_task_id = task.task_id
                                            st.rerun()
                                    
                                    
                                ## delete task
                                with col6:
                                    st.markdown("<div class='task-row-btn'>", unsafe_allow_html=True)
                                    delete_btn = st.button("x", key=f"delete_btn_{task.task_id}", type='primary')
                                    st.markdown("</div>", unsafe_allow_html=True)
                                    if delete_btn:
                                        tm.delete_task(task.task_id, user_id)
                                        st.rerun()
                                    

                        else:
                            st.info("No tasks found.")
                        ## CRUD ENDS

#         ## EDIT BUTTON FUNCTIONALITY
        if st.session_state.get("edit_task_id"):

            task_id = st.session_state.edit_task_id
            task = tm.get_task_by_id(task_id, user_id)
            def add_edit_draft():
                '''This function keep subtask into draft when task is
                edited'''
                value = st.session_state.edit_checklist_input.strip()
                if value:
                    st.session_state.edit_checklist.append({
                        "id": None,          # None = new item
                        "title": value,
                        "checked": False
                    })
                    st.session_state.edit_checklist_input = ""

            if "edit_checklist_loaded" not in st.session_state or st.session_state.edit_checklist_loaded != task_id:
                st.session_state.edit_checklist = [
                    {"id": row.item_id, "title": row.title, "checked": bool(row.is_done)}
                    for row in sb_tm.get_items(task_id)
                ]
                st.session_state.edit_checklist_loaded = task_id

            if task:

                with st.container(border=True):
                    st.subheader("Edit Task")

                    new_title = st.text_input("Task Name", value=task.title, key='edit_title')
                    new_description = st.text_area(label = "Description", value=task.description, height = 'content',key="description_input_edit", max_chars = 1000, placeholder="Enter task description here...")

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        new_due_date = st.date_input(
                            "Due Date",
                            dt.datetime.strptime(task.due_date, "%Y-%m-%d").date(),
                            key='edit_date'
                        )

                    with col2:
                        
                        valid_priority = ["Low", "Normal", "High", "Urgent"]
                        new_priority = st.selectbox(
                            "Priority",
                            valid_priority,
                            key = "prirority_add",
                            index=valid_priority.index(task.priority)
                        )

                    with col3:
                        valid_status = ["⚫ TO DO", "🔵 IN PROGRESS", "✅️ COMPLETE"]
                        if task.status == 'OVERDUE':
                            valid_status = ["⚫ TO DO", "🔵 IN PROGRESS", "✅️ COMPLETE",'OVERDUE']
                        new_status = st.selectbox(
                            "Status",
                            valid_status,
                            index=valid_status.index(task.status),
                            key = "status_add"
                        )
                    st.subheader('Edit Subtasks')
                    st.text_input(
                        "Add new subtask",
                        placeholder="eg. Design UI mockups",
                        key="edit_checklist_input",
                        on_change=add_edit_draft
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

                                tm.update_task(
                                    task_id,
                                    user_id,
                                    new_title,
                                    new_description,
                                    new_priority,
                                    new_due_date.isoformat(),         # FIXED
                                    new_status
                                )
                                for item in st.session_state.edit_checklist:
                                    if item["id"] is not None:
                                        sb_tm.toggle_subtask(item["id"], item["checked"])
                                    else:
                                        sb_tm.add_subtask(st.session_state.edit_task_id, item["title"],user_id,item["checked"])
                                st.session_state.edit_checklist = [] 
                                st.session_state.edit_task_id = None
                                st.session_state.edit_checklist_loaded = None
                                st.success("Task updated")
                                st.rerun()

        

    
#     ## logout 
    elif tabs == 'Logout': 
        cookies["logged_in"] = "false" 
        cookies["user_id"] = "" 
        cookies["username"] = ""
        cookies["email"] = ""
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
            user = auth().login(login_username, login_password)
            if user:
                st.session_state.user = user
                st.session_state['logged_in'] = True
                cookies["logged_in"] = "true"
                cookies["user_id"] = str(user.user_id)
                cookies["username"] = user.username
                cookies["email"] = user.email
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
        else:
            success = auth().register_user(reg_username, reg_email, reg_password)
            if success:
                st.success("Registration successful. Please Login")
            else:
                st.error("Username or email already exists")


