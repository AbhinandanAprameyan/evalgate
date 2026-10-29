import sys
from rag import load_index, ask

version = sys.argv[1] if len(sys.argv) > 1 else "v1"
index = load_index()
result = ask(index, "How do I declare a path parameter in FastAPI?", version)

print(f"\nPROMPT VERSION: {result['prompt_version']}")
print("\nANSWER:\n", result["answer"])
print("\nSOURCES:")
for s in result["sources"]:
    print(f" - {s['file']} | similarity: {s['score']}")