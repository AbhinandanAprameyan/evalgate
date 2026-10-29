import json
import pandas as pd
from llama_index.llms.ollama import Ollama
from ragas import evaluate, EvaluationDataset
from ragas.llms import LlamaIndexLLMWrapper
from ragas.embeddings import LlamaIndexEmbeddingsWrapper
from ragas.metrics import Faithfulness, FactualCorrectness, LLMContextRecall

from index_store import get_index
from llama_index.core import Settings

# 1. Load the golden set
with open("eval/golden_set.json") as f:
    golden = json.load(f)

# 2. Run every question through the pipeline
engine = get_index().as_query_engine(similarity_top_k=4)

samples = []
hits = 0
for i, item in enumerate(golden, 1):
    print(f"[{i}/{len(golden)}] {item['question']}")
    response = engine.query(item["question"])
    files = [n.metadata.get("file_name") for n in response.source_nodes]
    hit = item["expected_source"] in files
    hits += hit
    samples.append({
        "user_input": item["question"],
        "response": str(response),
        "retrieved_contexts": [n.get_content() for n in response.source_nodes],
        "reference": item["ground_truth"],
    })

print(f"\nRetrieval hit rate: {hits}/{len(golden)}")

# 3. Score with Ragas, using local Llama as the judge
judge = Ollama(model="llama3.1:8b", request_timeout=600.0, temperature=0)
result = evaluate(
    dataset=EvaluationDataset.from_list(samples),
    metrics=[Faithfulness(), FactualCorrectness(), LLMContextRecall()],
    llm=LlamaIndexLLMWrapper(judge),
    embeddings=LlamaIndexEmbeddingsWrapper(Settings.embed_model),
)

df = result.to_pandas()
df.to_csv("eval/results.csv", index=False)
print(df.drop(columns=["retrieved_contexts", "reference"], errors="ignore").to_string())
print("\nAverages:\n", df.select_dtypes("number").mean())