import streamlit as st
from streamlit_calendar import calendar
from auth import conn_db

def show_events_by_date(events):
    calendar_css = """
        <style>

       .fc {
            --fc-button-bg-color: #000000;
            --fc-button-border-color: #000000;
            --fc-button-text-color: #ffffff;

            --fc-button-hover-bg-color: #dc2626;
            --fc-button-hover-border-color: #dc2626;

            --fc-button-active-bg-color: #000000;
            --fc-button-active-border-color: #000000;
            }


        .fc .fc-prev-button{
            background: #000000 !important;
            box-shadow: none !important;
            border: 5px black;
            border-radius: 15px;
        }
        .fc .fc-next-button{
            background: #ffffff !important;
            color: #000000 !important;
            border: 5px #000000;
            border-radius: 15px;
        }
        .fc-button:active {
            border: none !important;
        }

        </style>
        """

    calendar_options = {
        "initialView": "dayGridMonth",
        "headerToolbar": {
            "right": "prev,next",
            "center": "title",
            "left": "",
        },
        "selectable": True,
    }

    return calendar(
        events=events,
        options=calendar_options,
        custom_css= calendar_css,
        key="task_calendar"
    )
def task_to_events(tasks):
    events = []

    for task_id, title, priority, due_date, status in tasks:
        
        color = "#D3D2D2"
        text_color = '#000000'
        if status == "OVERDUE":
            color = '#ff2b2b1a'
            text_color = "#bd4043"

        elif status == "✅️ COMPLETE" or status == "COMPLETE":
            color = "#21c3541a"
            text_color = "#158238"
        elif status == "🔵 IN PROGRESS" or status == 'IN PROGESS':
            color = "#1c83ff1a"
            text_color = "#0054a3"
        
        
        events.append({
            'id': task_id,
            'title': title,
            'start': due_date,
            'end': due_date,
            'color': color,
            'textColor': text_color
        })
    
    return events
