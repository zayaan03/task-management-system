import streamlit as st
from streamlit_calendar import calendar

def show_events_by_date():
    events = [
        {
            "title": "Project Deadline",
            "start": "2026-01-20",
            "end": "2026-01-20",
            "color": "#FF4B4B",
        },
        {
            "title": "Meeting",
            "start": "2026-01-15T10:00:00",
            "end": "2026-01-15T11:00:00",
            "color": "#4CAF50",
        }
    ]

    calendar_options = {
        "initialView": "dayGridMonth",
        "headerToolbar": {
            "left": "prev,next today",
            "center": "title",
            "right": "dayGridMonth,timeGridWeek,timeGridDay",
        },
        "selectable": True,
    }

    state = calendar(
        events=events,
        options=calendar_options,
        key="task_calendar"
    )

    # st.write(state)
