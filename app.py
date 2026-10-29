import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000/ask"

st.title("EvalGate: FastAPI Docs Assistant")

question = st.text_input("Ask a question about FastAPI")

if st.button("Ask") and question.strip():
    with st.spinner("Thinking..."):
        try:
            res = requests.post(API_URL, json={"question": question}, timeout=180)
            res.raise_for_status()
            data = res.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Could not reach the API. Is uvicorn running? ({e})")
        else:
            st.subheader("Answer")
            st.write(data["answer"])

            st.subheader("Sources")
            for s in data["sources"]:
                st.write(f"- {s['file']} (similarity: {s['score']})")