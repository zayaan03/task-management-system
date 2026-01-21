import streamlit as st
from google import genai
from auth import conn_db
import os

# ---------------- CONFIG ----------------
GEMINI_API_KEY = "AIzaSyBenLJ-br-W1wrUhKwvBwlZ15cgezOpcZg"

client = genai.Client(api_key=GEMINI_API_KEY)
# models = client.models.list()
# for m in models:
#     print(m.name)

MODEL_NAME = "gemini-2.5-flash"   

def  ai_assistant(user_id: int):
    """
    Run the AI Task Assistant inside Streamlit for a given user_id.
    Displays chat in the Streamlit app and returns the session chat.
    """
    st.title("🤖 AI Task Assistant")
    # ---------- FETCH USER DATA ----------
    def get_user_context(user_id):
        conn = conn_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT title, priority, due_date, status
            FROM tasks
            WHERE user_id = ?
        """, (user_id,))
        tasks = cursor.fetchall()
        conn.close()

        if not tasks:
            return "User has no tasks."

        summary = []
        for t in tasks:
            title, priority, due, status = t
            summary.append(
                f"Task: {title}, Priority: {priority}, Due: {due}, Status: {status}"
            )

        return "\n".join(summary)

    # ---------- SYSTEM PROMPT ----------
    def build_prompt(user_tasks, user_question):
        return f"""
        You are an AI task assistant for a productivity app.

        STRICT RULES:
        - Answer ONLY about task management, productivity, scheduling, or planning.
        - If question is irrelevant, say: "I can only help with tasks and productivity."
        - Never mention other users.
        - Never reveal names, emails, or personal info.
        - Give short, practical answers.

        USER TASK DATA:
        {user_tasks}

        USER QUESTION:
        {user_question}
        """

    # ---------- INIT CHAT MEMORY ----------
    if "chat" not in st.session_state:
        st.session_state.chat = []

    # ---------- DISPLAY INPUT ----------
    user_input = st.text_input("Ask about your tasks, priorities, or schedule", key=f"ai_input_{user_id}")

    if st.button("Send", key=f"ai_send_{user_id}") and user_input:

        user_tasks = get_user_context(user_id)
        prompt = build_prompt(user_tasks, user_input)

        with st.spinner("AI thinking..."):
            # Use generate_content (if using gemini-2.5-flash) or generate_text if text-bison
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )

        # Append to chat session
        st.session_state.chat.append(("You", user_input))
        st.session_state.chat.append(("AI", response.text))

    # ---------- DISPLAY CHAT ----------
    for role, msg in st.session_state.chat:
        if role == "You":
            st.markdown(f"**🧑 You:** {msg}")
        else:
            st.markdown(f"**🤖 AI:** {msg}")

    return st.session_state.chat
