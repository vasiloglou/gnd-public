"""The trip planner: ask the bot for bookings, check them with GND or PyRel, execute them.

    python app.py rules                                  # the rules, as the PyRel requirements GND generates
    python app.py ask "Plan three days in Lisbon under 900 EUR." --out next.pop.json
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
