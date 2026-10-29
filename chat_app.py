import requests
import streamlit as st

st.set_page_config(page_title="EvalGate", page_icon="⚡")
st.title("⚡ EvalGate")
st.caption("Ask questions about the FastAPI documentation")

# Developer toggle for the demo: which prompt version to use
version = st.sidebar.selectbox("Prompt version (developer setting)", ["v1", "v2"])

# Remember the conversation while the page is open
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# The chat box at the bottom
if question := st.chat_input("Ask about FastAPI..."):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        try:
            with st.spinner("Thinking..."):
                r = requests.post(
                    "http://127.0.0.1:8000/ask",
                    json={"question": question, "prompt_version": version},
                    timeout=180,
                )
                data = r.json()
            sources = ", ".join(f"{s['file']} ({s['score']})" for s in data["sources"])
            reply = (f"{data['answer']}\n\n**Sources:** {sources}  \n"
                     f"*Prompt version: {data['prompt_version']}*")
        except requests.exceptions.ConnectionError:
            reply = "⚠️ The EvalGate API isn't running. Start it with: `uvicorn app:app`"
        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})