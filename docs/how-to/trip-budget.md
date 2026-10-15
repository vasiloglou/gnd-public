# Keep a trip under budget

Use this when a bot books several things that share one budget. GND sums the
bookings in each state of the plan and refuses the step that goes over, and it
refuses two activities booked for the same time.

## Before you start

<!-- gnd-run expect=0 -->
```sh
python -c "import gnd, pathlib, shutil; shutil.copytree(pathlib.Path(gnd.__file__).parent / 'examples/plan_apps', 'plan_apps', ignore=shutil.ignore_patterns('recordings', 'skill-sessions', '__pycache__'), dirs_exist_ok=True)"
gnd validate plan_apps/trip/model.orm.json
```

```text
OK: plan_apps/trip/model.orm.json is a valid GND ORM model
```

The rules in PyRel, from `python plan_apps/trip/app.py rules`:

```text
m.where(hotel_total(step, t, h), activity_total(step, t, a), budget(step, t, b)).require((h + a) <= b)
m.where(booked_slot(step, trip, activity_1, day, period), booked_slot(step, trip, activity_2, day, period)).require(activity_1 == activity_2)
```

`hotel_total` and `activity_total` are sums the model derives. Nobody stores
them, so they can't drift from the bookings.

## Ask for a trip

```text
Plan three days in Lisbon under 900 EUR.
```

## Read the refusal

<figure class="gnd-replay" tabindex="0" role="region" aria-label="Replay: Llama 3.1 8B plans three days in Lisbon (recorded run 2)">
--8<-- "docs/assets/replays/trip-llama-3.1-8b-run-2.svg"
</figure>

??? note "Transcript of the replay"

    ```text
    --8<-- "docs/assets/replays/trip-llama-3.1-8b-run-2.txt"
    ```

Llama 3.1 8B stays inside the budget but books the Sintra day trip and the
Belém walk for the same morning. The checker, here the DuckDB program GND
generates, refuses the plan from state 4, where the
second booking lands, and names both activities, the day and the period.

## The repaired plan

The model swaps in different activities and the checker accepts the plan: 880
euros in all. It was the first trip run, in the order of the results table
(`llama-3.1-8b/trip/run-2`), refused on a rule and then
accepted.

GND checks the rules, not the wish behind them. In another recorded run,
Llama 3.2 3B repaired an overlap by booking one night and one activity for a
three-day trip, and GND accepted it, because no rule asks for three nights. If
it matters, write it as a rule.

To try the loop without a model provider:

<!-- gnd-run expect=0 -->
```sh
python plan_apps/trip/app.py ask "Plan three days in Lisbon under 900 EUR." --out next-trip.pop.json
```

```text
attempt 1
  plan  book_hotel(trip='lisbon', hotel='palacio', night='2025-05-12')
  plan  book_hotel(trip='lisbon', hotel='palacio', night='2025-05-13')
  plan  book_hotel(trip='lisbon', hotel='palacio', night='2025-05-14')
  plan  book_activity(trip='lisbon', activity='tram-28-tour')
  plan  book_activity(trip='lisbon', activity='fado-night')
  plan  book_activity(trip='lisbon', activity='sintra-day')
  gnd check: exit 1
    state 4  within_budget  violated  [{"$t": "lisbon", "$h": 900, "$a": 40, "$b": 900}]
      the rule in PyRel: m.where(hotel_total(step, t, h), activity_total(step, t, a), budget(step, t, b)).require((h + a) <= b)
    state 5  within_budget  violated  [{"$t": "lisbon", "$h": 900, "$a": 100, "$b": 900}]
    state 6  within_budget  violated  [{"$t": "lisbon", "$h": 900, "$a": 190, "$b": 900}]
attempt 2
  plan  book_hotel(trip='lisbon', hotel='alfama-inn', night='2025-05-12')
  plan  book_hotel(trip='lisbon', hotel='alfama-inn', night='2025-05-13')
  plan  book_hotel(trip='lisbon', hotel='alfama-inn', night='2025-05-14')
  plan  book_activity(trip='lisbon', activity='tram-28-tour')
  plan  book_activity(trip='lisbon', activity='fado-night')
  plan  book_activity(trip='lisbon', activity='sintra-day')
  plan  book_activity(trip='lisbon', activity='belem-walk')
  gnd check: exit 1
    state 7  no_overlap  violated  [{"trip": "lisbon", "activity": "belem-walk", "day": "2025-05-13", "period": "morning"}, {"trip": "lisbon", "activity": "sintra-day", "day": "2025-05-13", "period": "morning"}]
      the rule in PyRel: m.where(booked_slot(step, trip, activity_1, day, period), booked_slot(step, trip, activity_2, day, period)).require(activity_1 == activity_2)
attempt 3
  plan  book_hotel(trip='lisbon', hotel='alfama-inn', night='2025-05-12')
  plan  book_hotel(trip='lisbon', hotel='alfama-inn', night='2025-05-13')
  plan  book_hotel(trip='lisbon', hotel='alfama-inn', night='2025-05-14')
  plan  book_activity(trip='lisbon', activity='tram-28-tour')
  plan  book_activity(trip='lisbon', activity='fado-night')
  plan  book_activity(trip='lisbon', activity='sintra-day')
  plan  book_activity(trip='lisbon', activity='oceanarium')
  gnd check: exit 0 (accepted)
  executed: the new state is in next-trip.pop.json
```
