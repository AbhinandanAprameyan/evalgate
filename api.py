from contextlib import asynccontextmanager
from fastapi import FastAPI
from pydantic import BaseModel
from index_store import get_index

state = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs once at startup: load the saved index and create the query engine
    index = get_index()
    state["engine"] = index.as_query_engine(similarity_top_k=4)
    yield


app = FastAPI(lifespan=lifespan)


class Question(BaseModel):
    question: str


@app.post("/ask")
def ask(q: Question):
    response = state["engine"].query(q.question)
    sources = [
        {"file": node.metadata.get("file_name"), "score": round(node.score, 3)}
        for node in response.source_nodes
    ]
    return {"answer": str(response), "sources": sources}