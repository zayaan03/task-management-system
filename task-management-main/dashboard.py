import streamlit as st
import streamlit.components.v1 as components
import math


def information_card(
        total_tasks:int,
        overdue_tasks:int,
        todo_tasks:int,
        in_progress_tasks:int,
        completed_tasks:int): 

        components.html(f"""
        <!DOCTYPE html>
        <html>
        <head>
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

        body {{
            margin: 0;
            padding: 0;
            height: 100%;
            font-family: 'Inter', sans-serif;
        }}

        .card {{
            background: linear-gradient(90deg, #1c1d1f, #161719);
            color: white;
            width: 90vw;
            height:85vh;
                    
            border-radius: 22px;
            padding: 20px 22px;
            box-shadow: 0 6px 20px rgba(0,0,0,0.2);
        }}

        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .header h3 {{
            font-size: 16px;
            font-weight: 600;
        }}

        .icons span {{
            margin-left: 10px;
            font-size: 18px;
            opacity: 0.8;
        }}

        .stats-top {{
            margin-top: 2px;
            display: flex;
            align-items: center;
            justify-content: space-around;
        }}

        .stat {{
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .stat h1 {{
            font-size: 38px;
            font-weight: 700;
            
        }}

        .stat p {{
            font-size: 12px;
            opacity: 0.7;
            margin-left: 10px;
        }}

        .stat span {{
            font-size: 11px;
        }}

        .divider {{
            width: 2px;
            height: 50px;
            background: #333;
        }}

        .stats-bottom {{
            display: flex;
            justify-content: space-between;
        }}

        .box {{
            background: #f8f8f8;
            color: #111;
            width: 30%;
            height: 63px;
            padding: 12px 0;
            border-radius: 14px;
            text-align: center;
        }}

        .circle {{
            font-size: 18px;
        }}

        .box h2 {{
            font-size: 20px;
            font-weight: 700;
            margin-top: 4px;
            margin-bottom: 0;
        }}

        .box p {{
            font-size: 11px;
            opacity: 0.6;
            margin: 0 0 0 0;
        }}
        </style>
        </head>

        <body>
        <div class="card">
            <div class="header">
                <h3>Overall Information</h3>
                <div class="icons">
                    <span>⤴</span>
                    <span>⋮</span>
                </div>
            </div>

            <div class="stats-top">
                <div class="stat">
                    <h1>{total_tasks}</h1>
                    <p>Tasks create<br><span>for all time</span></p>
                </div>
                <div class="divider"></div>
                <div class="stat">
                    <h1>{overdue_tasks}</h1>
                    <p>projects are<br><span>overdue</span></p>
                </div>
            </div>

            <div class="stats-bottom">
                <div class="box">
                    <div class="circle">◎</div>
                    <h2>{todo_tasks}</h2>
                    <p>TO DO</p>
                </div>
                <div class="box">
                    <div class="circle">◔</div>
                    <h2>{in_progress_tasks}</h2>
                    <p>In Progress</p>
                </div>
                <div class="box">
                    <div class="circle">◉</div>
                    <h2>{completed_tasks}</h2>
                    <p>Completed</p>
                </div>
            </div>
        </div>
        </body>
        </html>
        """, height=285)

def project_progress_card(task_name, task_percent):
    title = "Task Progress"

    task_rows = ""
    for i, task in enumerate(task_name):
            task_rows += f"""
            <div class="task-row">
                <div class="task-header">
                    <span class="task-name">{task_name[i]}</span>
                    <span class="task-percent">{task_percent[i]}%</span>
                </div>
                <div class="bar-track">
                    <div class="bar-fill" style="width:{task_percent[i]}%"></div>
                </div>
            </div>
            """

    components.html(f"""
        <!DOCTYPE html>
        <html>
        <head>
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        body {{
            margin: 0;
            padding: 0;
            display: flex;
            background: transparent;
            font-family: 'Inter', sans-serif;
        }}

        .card {{
            background: #f5f5f5;
            width: 100vw;
            height:89vh;
            border-radius: 22px;
            padding: 22px 24px;
            border: 1px solid #dbdbdb;
            box-shadow: 0 6px 20px rgba(0,0,0,0.05);
            box-sizing: border-box;
            overflow: hidden;
        }}

        .title {{
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 18px;
            margin-top: 4px;
            color: #111;
        }}

        .task-row {{
            margin-bottom: 16px;
        }}

        .task-header {{
            display: flex;
            justify-content: space-between;
            font-size: 14px;
            font-weight: 600;
            color: #111;
            margin-bottom: 6px;
        }}

        .bar-track {{
            width: 100%;
            height: 7px;
            background: #eee;
            border-radius: 10px;
            overflow: hidden;
        }}

        .bar-fill {{
            height: 100%;
            background: #111;
            border-radius: 10px;
            transition: width 0.4s ease;
        }}
        </style>
        </head>

        <body>
            <div class="card">
                <div class="title">{title}</div>
                {task_rows}
            </div>
        </body>
        </html>
        """, height=320)


def today_tasks_card(tasks):
    tasks_html = ""
    # tasks = ['Submit pf assignment', 'Prepare for meeting with team', 'Design new logo concepts', 'Update project documentation', 'Review code for module X', 'Design new ui mockups']
    for i,task in enumerate(tasks):
        tasks_html += f"""
        <div class="task-item">{i+1}) {task}</div>
        """

    components.html(f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

    body {{
        margin: 0;
        padding: 0;
        background: transparent;
        font-family: 'Inter', sans-serif;
        display: flex;
        justify-content: center;
        align-items: center;
    }}

    .card {{
        width: 100vw;
        background: #f5f5f5;
        border-radius: 22px;
        padding: 18px;
        color: white;
        height: 290px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.05);
        border: 1px solid #dbdbdb;
        box-sizing: border-box;
    }}

    .title {{
        font-size: 16px;
        font-weight: 600;
        color: #111;
        margin-bottom: 18px;
        margin-top: 4px;
    }}

    .task-item {{
        padding: 8px 10px;
        border-radius: 8px;
        color: #111;
        font-size: 14px;
        font-weight: 600;
        background: #eaeaea;
        margin-bottom: 8px;
    }}

    .task-item:last-child {{
        margin-bottom: 0;
    }}
    </style>
    </head>

    <body>
        <div class="card">
            <div class="title">Work for Today</div>
            {tasks_html}
        </div>
    </body>
    </html>
    """, height=350)

def monthly_progress_card(total_tasks, percent_change, stats):


    # Circle geometry
    r = 58
    circumference = 2 * math.pi * r

    completed_pct = stats["completed"]
    overdue_pct = stats["overdue"]

    # Dash offsets
    completed_offset = circumference - (completed_pct / 100) * circumference
    overdue_offset = circumference - ((completed_pct + overdue_pct) / 100) * circumference

    components.html(f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    body {{
        margin:0;
        padding:0;
        background:transparent;
        font-family:'Inter', sans-serif;
        display:flex;
        justify-content:center;
        align-items:center;
    }}

    .card {{
        width:92vw;
        background:#1c1c1c;
        border-radius:22px;
        padding:20px 22px;
        color:white;
        box-shadow: 0 6px 20px rgba(0,0,0,0.2);
        box-sizing:border-box;
        height: 285px;
    }}

    .header {{
        display:flex;
        flex-direction:column;
        margin-bottom:18px;
    }}

    .title {{
        font-size:16px;
        font-weight:600;
        margin-top:10px;
    }}

    .change {{
        font-size:12px;
        color:#09ff00;
        font-weight:400;
        margin-top:8px;
    }}

    .main {{
        display:flex;
        align-items:center;
        justify-content:space-between;
    }}

    .chart-wrap {{
        margin-top:20px;
        position:relative;
        width:140px;
        height:140px;
    }}

    svg {{
        transform: rotate(-90deg);
    }}

    circle {{
        fill:none;
        stroke-width:10;
        stroke-linecap:round;
    }}

    .track {{
        stroke:#2a2a2a;
    }}

    .center-text {{
        position:absolute;
        top:50%;
        left:50%;
        transform:translate(-50%, -50%);
        text-align:center;
    }}

    .center-text h1 {{
        margin:0;
        font-size:26px;
        font-weight:700;
    }}

    .center-text p {{
        margin:0;
        font-size:11px;
        color:#aaaaaa;
    }}

    .legend {{
        font-size:13px;
    }}

    .legend div {{
        margin-bottom:8px;
        display:flex;
        justify-content:space-between;
        width:160px;
    }}

    .dot {{
        width:8px;
        height:8px;
        border-radius:50%;
        margin-right:8px;
        display:inline-block;
    }}
    </style>
    </head>

    <body>
      <div class="card">
        <div class="header">
            <div class="title">Monthly Progress</div>
            <div class="change">{percent_change}% more than previous month</div>
        </div>

        <div class="main">

            <div class="chart-wrap">
                <svg width="140" height="140">
                    <!-- Background track -->
                    <circle class="track" cx="70" cy="70" r="{r}"></circle>

                    <!-- Completed Arc (Black) -->
                    <circle cx="70" cy="70" r="{r}"
                        stroke="#000000"
                        stroke-dasharray="{circumference}"
                        stroke-dashoffset="{completed_offset}">
                    </circle>

                    <!-- Overdue Arc (Light Gray) -->
                    <circle cx="70" cy="70" r="{r}"
                        stroke="#b5b5b5"
                        stroke-dasharray="{circumference}"
                        stroke-dashoffset="{overdue_offset}">
                    </circle>
                </svg>

                <div class="center-text">
                    <h1>{total_tasks}</h1>
                    <p>Total Tasks</p>
                </div>
            </div>

            <div class="legend">
                <div><span><span class="dot" style="background:#777777"></span>Todo</span> {stats['todo']}%</div>
                <div><span><span class="dot" style="background:#999999"></span>In Progress</span> {stats['inprogress']}%</div>
                <div><span><span class="dot" style="background:#000000"></span>Completed</span> {stats['completed']}%</div>
                <div><span><span class="dot" style="background:#b5b5b5"></span>Overdue</span> {stats['overdue']}%</div>
            </div>

        </div>
      </div>
    </body>
    </html>
    """, height=285)


