import sys
from rag import load_index, ask

# Usage: python ask.py <prompt-version> "<question>"
version = sys.argv[1] if len(sys.argv) > 1 else "northpeak-v1"
question = sys.argv[2] if len(sys.argv) > 2 else "What is the daily meal limit for international travel?"

index = load_index()
result = ask(index, question, version)

print(f"\nPROMPT VERSION: {result['prompt_version']}")
print(f"QUESTION: {question}")
print("\nANSWER:\n", result["answer"])
print("\nSOURCES:")
for s in result["sources"]:
    print(f" - {s['file']} | similarity: {s['score']}")
