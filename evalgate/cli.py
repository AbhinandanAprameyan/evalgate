"""Command line: python -m evalgate run --version <prompt-version> [--sample N] [--save-baseline]"""
import argparse, json, os, statistics, sys, time
import yaml
from evalgate.client import AssistantClient
from evalgate.scoring import score
from evalgate.gate import decide
from evalgate.report import write_report


def stratified_sample(tests, n):
    by_cat = {}
    for t in tests: by_cat.setdefault(t["category"], []).append(t)
    picked, i = [], 0
    while len(picked) < min(n, len(tests)):
        for cat in sorted(by_cat):
            if i < len(by_cat[cat]) and len(picked) < n: picked.append(by_cat[cat][i])
        i += 1
    return picked


def cmd_run(args):
    cfg = yaml.safe_load(open(args.config))
    tests = yaml.safe_load(open(cfg["tests"]))["tests"]
    if args.category: tests = [t for t in tests if t["category"] == args.category]
    if args.sample: tests = stratified_sample(tests, args.sample)
    client = AssistantClient(cfg["assistant"], args.version)
    print(f"EvalGate: testing version '{args.version}' on {len(tests)} questions at {client.endpoint}\n")
    results = []
    for n, t in enumerate(tests, 1):
        answer, sources, latency = client.ask(t["question"])
        ok, reasons = score(t, answer)
        results.append({**{k: t[k] for k in ("id", "category", "question")}, "passed": ok, "reasons": reasons,
                        "answer": answer, "latency": round(latency, 2),
                        "sources": [s.get("file") if isinstance(s, dict) else s for s in sources][:5]})
        print(f"  [{n:>3}/{len(tests)}] {'PASS' if ok else 'FAIL'}  {t['id']:<24} {latency:5.1f}s")
    run = {"version": args.version, "endpoint": client.endpoint, "time": time.strftime("%Y-%m-%d %H:%M:%S"),
           "median_latency": statistics.median([r["latency"] for r in results]) if results else 0, "results": results}
    import datetime
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S-%f")[:-3]
    os.makedirs("evalgate/runs", exist_ok=True); os.makedirs("evalgate/reports", exist_ok=True)
    json.dump(run, open(f"evalgate/runs/{stamp}_{args.version}.json", "w"), indent=2)
    baseline_path = cfg["baseline"]
    baseline = json.load(open(baseline_path)) if os.path.exists(baseline_path) and not args.save_baseline else None
    out = decide(run, baseline, cfg.get("gate", {}))
    decision, reasons = out[0], out[1]
    cur, old = (out[2], out[3]) if len(out) == 4 else (None, None)
    report_path = f"evalgate/reports/{stamp}_{args.version}.md"
    passed = sum(r["passed"] for r in results)
    if args.save_baseline:
        os.makedirs(os.path.dirname(baseline_path), exist_ok=True)
        json.dump(run, open(baseline_path, "w"), indent=2)
        decision, reasons = "NO BASELINE", [f"Saved this run as the new baseline ({baseline_path})."]
    write_report(report_path, run, decision, reasons, cur, old)
    print(f"\nPassed {passed}/{len(results)} ({100*passed/max(len(results),1):.0f}%)")
    print(f"Decision: {decision}")
    for r in reasons: print(f"  - {r}")
    print(f"Report: {report_path}")
    if decision == "BLOCK": sys.exit(1)


def cmd_impact(args):
    reg = yaml.safe_load(open(args.registry))["facts"]
    f = next((x for x in reg if x["id"] == args.fact), None)
    if not f: raise SystemExit(f"Unknown fact '{args.fact}'. Known facts: " + ", ".join(x["id"] for x in reg))
    print(f"Fact '{f['id']}' (current value {f['value']})\n\nDocuments to update:")
    for d in f["mentioned_in"]: print(f"  - {d}")
    print(f"\nTests to re-run and review ({len(f['tests_using_these_docs'])}):")
    for t in f["tests_using_these_docs"]: print(f"  - {t}")


def main():
    p = argparse.ArgumentParser(prog="evalgate", description="EvalGate: a quality gate for document-based assistants")
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run", help="test an assistant version and decide PASS or BLOCK")
    r.add_argument("--config", default="evalgate.yaml")
    r.add_argument("--version", required=True, help="prompt version to test, e.g. northpeak-v1")
    r.add_argument("--sample", type=int, help="run a balanced sample of N tests (faster)")
    r.add_argument("--category", help="run only one category")
    r.add_argument("--save-baseline", action="store_true", help="save this run as the baseline")
    r.set_defaults(func=cmd_run)
    i = sub.add_parser("impact", help="show which documents and tests a fact change affects")
    i.add_argument("fact"); i.add_argument("--registry", default="evalgate/facts/northpeak_facts.yaml")
    i.set_defaults(func=cmd_impact)
    a = p.parse_args(); a.func(a)
