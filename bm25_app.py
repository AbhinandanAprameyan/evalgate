import glob, os, re
import ollama, yaml
from fastapi import FastAPI
from pydantic import BaseModel
from rank_bm25 import BM25Okapi

CONFIG = yaml.safe_load(open("assistant_config.yaml"))
MODEL = CONFIG.get("model", "llama3.1:8b")
DATA_DIR = "data/northpeak"
TOP_K = 5


def tokenize(text):
    return re.findall(r"\w+", text.lower())


def chunk(text, size=1200):
    chunks, cur = [], ""
    for para in text.split("\n\n"):
        if cur and len(cur) + len(para) > size:
            chunks.append(cur)
            cur = ""
        cur += para + "\n\n"
    if cur.strip():
        chunks.append(cur)
    return chunks


# Build the keyword index once at startup
docs = []
for path in glob.glob(f"{DATA_DIR}/**/*.md", recursive=True):
    rel = os.path.relpath(path, DATA_DIR)
    if rel.startswith("confidential/"):   # same protection as the guarded bot
        continue
    for c in chunk(open(path, encoding="utf-8").read()):
        docs.append((rel, c))
bm25 = BM25Okapi([tokenize(c) for _, c in docs])
print(f"Indexed {len(docs)} chunks")

app = FastAPI(title="Northpeak Assist (BM25 version)")


class Question(BaseModel):
    question: str
    prompt_version: str = "northpeak-v1"


@app.post("/ask")
def ask(q: Question):
    template = yaml.safe_load(open(f"prompts/{q.prompt_version}.yaml"))["template"]
    scores = bm25.get_scores(tokenize(q.question))
    top = sorted(range(len(docs)), key=lambda i: scores[i], reverse=True)[:TOP_K]

    context = "\n\n".join(docs[i][1] for i in top)
    prompt = template.format(context_str=context, query_str=q.question)

    reply = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0, "num_ctx": 8192},
    )
    return {
        "answer": reply["message"]["content"],
        "sources": [{"file": docs[i][0], "score": round(float(scores[i]), 3)} for i in top],
        "prompt_version": q.prompt_version,
        "model": MODEL,
    }