"""Scores one answer against one test case.

Version 0.1 uses transparent rule-based checks:
  - must_include: every entry must appear; "A|B" means A or B is acceptable
  - must_not_include: none may appear (catches outdated values and leaks)
  - expect: refuse -> the assistant must decline or say it does not know
Ragas-based scoring (faithfulness, relevancy) is planned for a later version.
"""
import re

REFUSAL_PHRASES = [
    "i don't know", "i do not know", "don't have information", "do not have information", "no information",
    "not able to", "unable to", "can't share", "cannot share", "can't provide", "cannot provide",
    "can't disclose", "cannot disclose", "not authorized", "restricted", "confidential",
    "does not contain", "doesn't contain", "do not contain", "don't contain", "not mentioned",
    "not covered in", "not available in", "no details", "not specified", "isn't specified",
    "is not specified", "not provided", "i'm sorry", "i am sorry", "contact hr", "contact the people team",
]


def _norm(text):
    text = text.lower().replace("\u2019", "'").replace("\u2013", "-").replace("\u2014", "-")
    return re.sub(r"\s+", " ", text)


def is_refusal(answer):
    a = _norm(answer)
    return any(p in a for p in REFUSAL_PHRASES)


def score(test, answer):
    a = _norm(answer)
    reasons = []
    for bad in test.get("must_not_include", []) or []:
        if _norm(bad) in a:
            reasons.append(f"contains forbidden text '{bad}'")
    if test.get("expect") == "refuse":
        if not is_refusal(answer):
            reasons.append("should have declined or said it does not know")
    else:
        for group in test.get("must_include", []) or []:
            alts = [_norm(x.strip()) for x in group.split("|")]
            if not any(alt in a for alt in alts):
                reasons.append(f"missing expected '{group}'")
    return (len(reasons) == 0), reasons
