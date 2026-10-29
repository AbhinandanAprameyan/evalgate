"""Writes a Markdown report: a scorecard suitable for a pull request comment."""


def write_report(path, run, decision, reasons, cur=None, old=None):
    icon = {"PASS": "✅", "BLOCK": "❌", "NO BASELINE": "ℹ️"}[decision]
    L = [f"# EvalGate report: {run['version']}", "",
         f"**Decision: {icon} {decision}**", "",
         f"- Assistant: `{run['endpoint']}`",
         f"- Tests run: {len(run['results'])}",
         f"- Median answer time: {run['median_latency']:.1f} s", ""]
    if reasons:
        L += ["## Why", ""] + [f"- {r}" for r in reasons] + [""]
    if cur and old:
        L += ["## Scorecard (pass rate)", "", "| Category | Baseline | This version | Change |", "|---|---|---|---|"]
        L.append(f"| **Overall** | {old['overall']:.0f}% | {cur['overall']:.0f}% | {cur['overall']-old['overall']:+.0f} |")
        for cat in sorted(cur["categories"]):
            o = old["categories"].get(cat); n = cur["categories"][cat]
            L.append(f"| {cat} | {o:.0f}% | {n:.0f}% | {n-o:+.0f} |" if o is not None else f"| {cat} | - | {n:.0f}% | new |")
        L.append("")
    fails = [r for r in run["results"] if not r["passed"]]
    if fails:
        L += ["## Failing tests", ""]
        for r in fails:
            ans = r["answer"].replace("\n", " ")
            ans = ans[:300] + ("..." if len(ans) > 300 else "")
            L += [f"**{r['id']}** ({r['category']}): {r['question']}  ", f"Problem: {'; '.join(r['reasons'])}  ", f"Answer: _{ans}_", ""]
    open(path, "w").write("\n".join(L))
