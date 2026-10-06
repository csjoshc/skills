"""Check helper: parse REVIEW-FINDINGS items out of output.txt and apply one rule."""
import re
import sys

text = open("output.txt").read()
fences = re.findall(r"```REVIEW-FINDINGS\n(.*?)```", text, re.S)
items = [i for f in fences for i in re.split(r"(?m)^\s*- id:", f)[1:]]
rule = sys.argv[1]

if not items:
    sys.exit(1)

if rule == "bug-line16":
    ok = any(
        re.search(r"category:\s*Bug", i)
        and "refunds.py" in i
        and re.search(r"line:\s*1[5-7]\b", i)
        and "requested_cents >= remaining" in i
        for i in items
    )
elif rule == "format":
    ok = all(
        re.search(r"source:\s*(lens-derived|tool-flagged)", i)
        and re.search(r"checklist_score:\s*\d+/\d+", i)
        and (not re.search(r"severity:\s*CRITICAL", i) or re.search(r"proof:\s*\S", i))
        for i in items
    )
elif rule == "gift-test-gap":
    ok = any(
        re.search(r"category:\s*Test Gap", i) and re.search(r"gift_card|GIFT_CARD", i)
        for i in items
    )
else:
    ok = False
sys.exit(0 if ok else 1)
