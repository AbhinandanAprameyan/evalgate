from fastapi import FastAPI
from pydantic import BaseModel
from rag import load_index, ask

app = FastAPI(title="EvalGate")
index = load_index()


class Question(BaseModel):
    question: str
    prompt_version: str = "v1"


@app.post("/ask")
def ask_endpoint(q: Question):
    return ask(index, q.question, q.prompt_version)