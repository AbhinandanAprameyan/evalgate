from fastapi import FastAPI
from pydantic import BaseModel
from rag import load_index
from guarded_rag import ask

app = FastAPI(title="Northpeak Assist API (guarded)")
index = load_index()


class Question(BaseModel):
    question: str
    prompt_version: str = "northpeak-v1"


@app.post("/ask")
def ask_endpoint(q: Question):
    return ask(index, q.question, q.prompt_version)