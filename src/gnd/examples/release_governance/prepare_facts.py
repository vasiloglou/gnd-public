"""Write readable Souffle facts from one supplied synthetic scenario."""
import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('snapshot', type=Path)
    parser.add_argument('destination', type=Path)
    args = parser.parse_args()
    data = json.loads(args.snapshot.read_text())
    args.destination.mkdir()
    relations = {'Edge': data['dependencies'],
                 'Deployable': [[s] for s in data['services']],
                 'Vulnerable': [[s] for s in data['vulnerable']],
                 'Request': [[r, s] for r, s, _ in data['requests']]}
    for name, rows in relations.items():
        with (args.destination / f'impact.{name}.facts').open('x') as handle:
            for row in rows:
                if any(not isinstance(cell, str) or any(c in cell for c in '\t\r\n') for cell in row):
                    raise ValueError('facts require one-line string cells')
                handle.write('\t'.join(row) + '\n')


if __name__ == '__main__':
    main()
