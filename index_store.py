#Save the document index with ChromaDB, so it is built once instead of on every run
import chromadb
from llama_index.core import (
    SimpleDirectoryReader,
    VectorStoreIndex,
    StorageContext,
    Settings,
)
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore

# Models are configured here so every script uses the same ones
Settings.llm = Ollama(model="llama3.1:8b", request_timeout=120.0, temperature=0)
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")


def get_index():
    db = chromadb.PersistentClient(path="chroma_db")
    collection = db.get_or_create_collection("fastapi_docs")
    vector_store = ChromaVectorStore(chroma_collection=collection)

    # Already built? Load it from disk, no re-embedding
    if collection.count() > 0:
        print("Loading saved index...")
        return VectorStoreIndex.from_vector_store(vector_store)

    # First run: load docs, embed them, and save into Chroma
    print("Building index (first run)...")
    documents = SimpleDirectoryReader(
        "data/fastapi_docs", recursive=True, required_exts=[".md"]
    ).load_data()
    print(f"Loaded {len(documents)} documents")

    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    return VectorStoreIndex.from_documents(
        documents, storage_context=storage_context, show_progress=True
    )