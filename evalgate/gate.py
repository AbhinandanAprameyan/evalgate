"""Compares a run with the baseline and decides PASS or BLOCK."""


def summarize(results):
    cats = {}
    for r in results:
        c = cats.setdefault(r["category"], [0, 0])
        c[0] += int(r["passed"]); c[1] += 1
    total = sum(int(r["passed"]) for r in results)
    return {"overall": 100.0 * total / max(len(results), 1),
            "categories": {k: 100.0 * v[0] / v[1] for k, v in cats.items()},
            "counts": {k: v for k, v in cats.items()}}


def decide(current, baseline, rules):
    if baseline is None:
        return "NO BASELINE", ["No baseline saved yet. Run again with --save-baseline to create one."]
    reasons = []
    base_ids = {r["id"]: r for r in baseline["results"]}
    shared = [r for r in current["results"] if r["id"] in base_ids]
    if not shared:
        return "NO BASELINE", ["The baseline was made with different tests. Save a new baseline."]
    cur = summarize(shared)
    old = summarize([base_ids[r["id"]] for r in shared])
    drop = old["overall"] - cur["overall"]
    if drop > rules.get("max_overall_drop", 3):
        reasons.append(f"Overall pass rate dropped {drop:.1f} points ({old['overall']:.1f}% -> {cur['overall']:.1f}%), "
                       f"more than the allowed {rules.get('max_overall_drop', 3)}.")
    for cat, new_val in cur["categories"].items():
        old_val = old["categories"].get(cat)
        if old_val is None: continue
        d = old_val - new_val
        if cat in rules.get("critical_categories", []) and d > 0:
            reasons.append(f"Critical category '{cat}' got worse ({old_val:.0f}% -> {new_val:.0f}%). Any drop is blocked.")
        elif d > rules.get("max_category_drop", 10):
            reasons.append(f"Category '{cat}' dropped {d:.1f} points ({old_val:.0f}% -> {new_val:.0f}%).")
    return ("BLOCK" if reasons else "PASS"), reasons, cur, old
