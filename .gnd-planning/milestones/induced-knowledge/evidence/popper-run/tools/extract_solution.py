"""Print the clauses of Popper's final SOLUTION block, without logger timestamps.

Usage: python extract_solution.py POPPER_STDERR
"""
import re
import sys

lines = open(sys.argv[1]).read().splitlines()
start = max(i for i, line in enumerate(lines) if "SOLUTION" in line)
for line in lines[start + 1:]:
    body = re.sub(r"^\d+(\.\d+)?s ", "", line)
    if body.startswith("*"):
        break
    if body.startswith("Precision:"):
        continue
    print(body)
