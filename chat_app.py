import os
import requests
import streamlit as st

st.set_page_config(page_title="Northpeak Assist", page_icon="🤖")
st.title("🤖 Northpeak Assist")
st.caption("Internal assistant for Northpeak Robotics employees (fictional company). Protected by EvalGate.")

versions = sorted(f[:-5] for f in os.listdir("prompts") if f.endswith(".yaml"))
default = versions.index("northpeak-v1") if "northpeak-v1" in versions else 0
version = st.sidebar.selectbox("Prompt version (developer setting)", versions, index=default)

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if question := st.chat_input("Ask about Northpeak policies or products..."):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)
    with st.chat_message("assistant"):
        try:
            with st.spinner("Thinking..."):
                r = requests.post("http://127.0.0.1:8000/ask",
                                  json={"question": question, "prompt_version": version}, timeout=180)
                data = r.json()
            sources = ", ".join(f"{s['file']} ({s['score']})" for s in data["sources"])
            answer = data["answer"].replace("$", "\\$")
            reply = f"{answer}\n\n**Sources:** {sources}  \n*Prompt version: {data['prompt_version']}*"
        except requests.exceptions.ConnectionError:
            reply = "⚠️ The assistant API isn't running. Start it with: `uvicorn app:app`"
        st.markdown(reply)
    st.session_state.messages.append({"role": "assistant", "content": reply})
