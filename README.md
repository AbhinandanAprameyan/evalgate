# EvalGate

A RAG chatbot over the FastAPI docs, with an evaluation gate that blocks prompt or config changes that make answers worse.

## Setup (Mac)

1. Install [Ollama](https://ollama.com), then download the model:
   ```
   ollama pull llama3.1:8b
   ```
2. Install Python 3.12, then in this folder:
   ```
   python3.12 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Run the first pipeline:
   ```
   python ask.py
   ```