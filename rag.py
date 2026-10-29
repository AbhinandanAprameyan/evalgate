import chromadb
import yaml
from llama_index.core import (SimpleDirectoryReader, VectorStoreIndex, Settings,
                              StorageContext, PromptTemplate)
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore

Settings.llm = Ollama(model="llama3.1:8b", request_timeout=120.0, temperature=0)
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")


def load_index():
    """Load the saved index from disk, or build it the first time."""
    db = chromadb.PersistentClient(path="chroma_db")
    collection = db.get_or_create_collection("fastapi_docs", metadata={"hnsw:space": "cosine"})
    vector_store = ChromaVectorStore(chroma_collection=collection)

    if collection.count() == 0:
        print("No saved index found. Building it now...")
        documents = SimpleDirectoryReader(
            "data/fastapi_docs", recursive=True, required_exts=[".md"]
        ).load_data()
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        return VectorStoreIndex.from_documents(
            documents, storage_context=storage_context, show_progress=True
        )

    print(f"Loaded saved index with {collection.count()} chunks.")
    return VectorStoreIndex.from_vector_store(vector_store)


def load_prompt(version):
    """Read a prompt version from the prompts folder."""
    with open(f"prompts/{version}.yaml") as f:
        return yaml.safe_load(f)


def ask(index, question, version="v1", top_k=4):
    """Answer a question using a chosen prompt version."""
    prompt = load_prompt(version)
    engine = index.as_query_engine(
        similarity_top_k=top_k,
        text_qa_template=PromptTemplate(prompt["template"]),
    )
    response = engine.query(question)
    sources = [
        {"file": n.metadata.get("file_name"), "score": round(n.score, 3)}
        for n in response.source_nodes
    ]
    return {"answer": str(response), "sources": sources, "prompt_version": version}