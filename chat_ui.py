
import streamlit as st

from agent import build_agent


def extract_answer(message):
    """Extract readable text from a LangChain assistant message."""

    content = getattr(message, "content", "")

    if isinstance(content, str):
        return content.strip() or "I couldn't generate a text response."

    if isinstance(content, list):
        parts = []

        for item in content:
            if isinstance(item, dict):
                text = item.get("text")
                if text:
                    parts.append(str(text))
            elif isinstance(item, str):
                parts.append(item)

        return "\n".join(parts).strip() or (
            "I couldn't generate a text response."
        )

    return str(content)


def show_ai_booking_assistant(access_token, user_id):
    """Display SmartBook AI for the authenticated user."""

    st.header("🤖 SmartBook AI Assistant")
    st.write(
        "Find professional services, check available appointment slots, "
        "and review your bookings."
    )

    if not access_token or not user_id:
        st.warning("Please log in to use SmartBook AI.")
        return

    history_key = f"smartbook_chat_{user_id}"

    if history_key not in st.session_state:
        st.session_state[history_key] = []

    history = st.session_state[history_key]

    if st.button("🗑️ Clear chat", key=f"clear_chat_{user_id}"):
        st.session_state[history_key] = []
        st.rerun()

    # Display previous messages.
    for message in history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input(
        "Ask about services, availability, or your bookings..."
    )

    if not prompt or not prompt.strip():
        return

    prompt = prompt.strip()

    # Display the new user message.
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        with st.chat_message("assistant"):
            with st.spinner("SmartBook AI is thinking..."):
                agent = build_agent(access_token)

                # Send recent conversation history to the agent.
                recent_history = history[-10:] + [
                    {"role": "user", "content": prompt}
                ]

                result = agent.invoke({
                    "messages": recent_history
                })

                messages = result.get("messages", [])

                if not messages:
                    raise ValueError(
                        "The assistant returned no messages."
                    )

                answer = extract_answer(messages[-1])

                st.markdown(answer)

        # Save messages only after a successful response.
        history.extend([
            {
                "role": "user",
                "content": prompt
            },
            {
                "role": "assistant",
                "content": answer
            }
        ])

    except Exception:
        st.error(
            "SmartBook AI couldn't complete that request. "
            "Please try again. If the problem continues, check your "
            "Groq API key, installed packages, and Supabase connection."
        )
