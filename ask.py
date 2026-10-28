from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# 1. Choose the models
Settings.llm = Ollama(model="llama3.1:8b", request_timeout=120.0, temperature=0)
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

# 2. Load the docs
documents = SimpleDirectoryReader(
    "data/fastapi_docs", recursive=True, required_exts=[".md"]
).load_data()
print(f"Loaded {len(documents)} documents")

# 3. Chunk, embed, and index them
index = VectorStoreIndex.from_documents(documents, show_progress=True)

# 4. Ask a question
query_engine = index.as_query_engine(similarity_top_k=4)
question = "How do I declare a path parameter in FastAPI?"
response = query_engine.query(question)

print("\nANSWER:\n", response)
print("\nSOURCES:")
for node in response.source_nodes:
    print(" -", node.metadata.get("file_name"), "| similarity:", round(node.score, 3))