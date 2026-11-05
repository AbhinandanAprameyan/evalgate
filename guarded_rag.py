import os
from llama_index.core import PromptTemplate, Settings
from llama_index.core.postprocessor.types import BaseNodePostprocessor
from llama_index.llms.ollama import Ollama

from rag import DOMAIN, MODEL, load_prompt, load_index  # reuse, don't edit

# Cap the context so Ollama doesn't reserve a huge 128K window
Settings.llm = Ollama(
    model=MODEL,
    request_timeout=300.0,
    temperature=0,
    context_window=8192,
    additional_kwargs={"num_ctx": 8192},
)


def is_confidential(n):
    path = n.node.metadata.get("file_path", "")
    return "/confidential/" in path


class DropConfidential(BaseNodePostprocessor):
    def _postprocess_nodes(self, nodes, query_bundle=None):
        return [n for n in nodes if not is_confidential(n)]


def ask(index, question, version="northpeak-v1", top_k=None):
    prompt = load_prompt(version)
    engine = index.as_query_engine(
        similarity_top_k=top_k or DOMAIN["top_k"],
        text_qa_template=PromptTemplate(prompt["template"]),
        node_postprocessors=[DropConfidential()],
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
    return {"answer": str(response), "sources": sources,
            "prompt_version": version, "model": MODEL}