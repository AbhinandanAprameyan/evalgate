"""Talks to the assistant through its HTTP API, like any external client would."""
import json, time, urllib.request, urllib.error


class AssistantClient:
    def __init__(self, cfg, version):
        self.endpoint = cfg["endpoint"]
        self.question_field = cfg.get("question_field", "question")
        self.answer_field = cfg.get("answer_field", "answer")
        self.sources_field = cfg.get("sources_field")
        self.extra = {k: str(v).replace("{version}", version) for k, v in (cfg.get("extra_fields") or {}).items()}
        self.timeout = cfg.get("timeout_seconds", 180)

    def ask(self, question):
        body = {self.question_field: question, **self.extra}
        req = urllib.request.Request(self.endpoint, data=json.dumps(body).encode(),
                                     headers={"Content-Type": "application/json"}, method="POST")
        start = time.time()
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                data = json.loads(r.read().decode())
        except urllib.error.URLError as e:
            raise SystemExit(f"\nCould not reach the assistant at {self.endpoint} ({e}).\n"
                             "Is it running? Start it with: uvicorn app:app\n")
        latency = time.time() - start
        answer = str(data.get(self.answer_field, ""))
        sources = data.get(self.sources_field, []) if self.sources_field else []
        return answer, sources, latency
