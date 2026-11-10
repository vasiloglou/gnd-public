"""Compare selected baseline/candidate pytest failures; not a green-suite claim."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path


def observe(text: str) -> dict:
    failures = re.findall(r'^FAILED (\S+)', text, re.MULTILINE)
    summaries = re.findall(r'^(\d+) failed, (\d+) passed, (\d+) deselected(?:, (\d+) warnings?)? in (.+)$', text, re.MULTILINE)
    if len(summaries) != 1:
        raise AssertionError('one complete pytest summary required')
    failed, passed, deselected, warning, elapsed = summaries[0]
    if len(failures) != int(failed) or len(set(failures)) != len(failures):
        raise AssertionError('failure IDs and count disagree')
    return {'failed': sorted(failures), 'passed': int(passed), 'deselected': int(deselected),
            'warnings': int(warning or 0), 'elapsed': elapsed}


def compare(baseline: str, candidate: str) -> dict:
    before, after = observe(baseline), observe(candidate)
    added = sorted(set(after['failed']) - set(before['failed']))
    removed = sorted(set(before['failed']) - set(after['failed']))
    if added or removed:
        raise AssertionError({'added_failures': added, 'removed_failures': removed})
    return {'baseline': before, 'candidate': after, 'added_failures': added,
            'removed_failures': removed,
            'claim': 'exact observed failure-set equality; both suites remain nonzero'}


if __name__ == '__main__':
    print(json.dumps(compare(Path(sys.argv[1]).read_text(), Path(sys.argv[2]).read_text()), indent=2))
