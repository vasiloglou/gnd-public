"""The pharmacy: ask the bot for a refill plan, check it with GND or PyRel, execute it.

    python app.py rules                                  # the rules, as the PyRel requirements GND generates
    python app.py ask "Refill Sam's prescriptions today." --out next.pop.json
    python app.py ask "..." --backend pyrel             # the PyRel program GND generates checks the plan
    python app.py check plans/attempt-1.steps.json
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from core import main

if __name__ == "__main__":
    raise SystemExit(main(HERE))
