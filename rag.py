import os
import chromadb
import yaml
from llama_index.core import (SimpleDirectoryReader, VectorStoreIndex, Settings,
                              StorageContext, PromptTemplate)
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore

CONFIG = yaml.safe_load(open("assistant_config.yaml"))
DOMAIN = CONFIG["domains"][CONFIG["active"]]

MODEL = CONFIG.get("model", "llama3.1:8b")
Settings.llm = Ollama(model=MODEL, request_timeout=180.0, temperature=0)
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
Settings.chunk_size = DOMAIN["chunk_size"]


def load_index():
    """Load the saved index for the active domain, or build it the first time."""
    db = chromadb.PersistentClient(path="chroma_db")
    collection = db.get_or_create_collection(DOMAIN["collection"], metadata={"hnsw:space": "cosine"})
    vector_store = ChromaVectorStore(chroma_collection=collection)

    if collection.count() == 0:
        print(f"No saved index for '{CONFIG['active']}'. Building it now...")
        documents = SimpleDirectoryReader(DOMAIN["data_dir"], recursive=True, required_exts=[".md"]).load_data()
        print(f"Loaded {len(documents)} documents")
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        return VectorStoreIndex.from_documents(documents, storage_context=storage_context, show_progress=True)

    print(f"Loaded saved '{CONFIG['active']}' index with {collection.count()} chunks.")
    return VectorStoreIndex.from_vector_store(vector_store)


def load_prompt(version):
    with open(f"prompts/{version}.yaml") as f:
        return yaml.safe_load(f)


def ask(index, question, version="northpeak-v1", top_k=None):
    prompt = load_prompt(version)
    engine = index.as_query_engine(
        similarity_top_k=top_k or DOMAIN["top_k"],
        text_qa_template=PromptTemplate(prompt["template"]),
    )
    response = engine.query(question)
    sources = []
    for n in response.source_nodes:
        path = n.metadata.get("file_path", n.metadata.get("file_name", ""))
        try:
            path = os.path.relpath(path, DOMAIN["data_dir"])
        except ValueError:
            pass
        sources.append({"file": path, "score": round(n.score or 0, 3)})
    return {"answer": str(response), "sources": sources, "prompt_version": version, "model": MODEL}
