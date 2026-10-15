# Schedule rent inside a lease

Use this when a bot writes dated entries that must fall inside a contract's
term. GND compares every due date with the lease's start and end, refuses dates
outside them, and warns about a payment due in the last week.

!!! info "Files on GitHub"

    - [`lease/rules.md`](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/examples/plan_apps/lease/rules.md): the rules as written
    - [`lease/model.orm.json`](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/examples/plan_apps/lease/model.orm.json): the model
    - [`lease/state.pop.json`](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/examples/plan_apps/lease/state.pop.json): the starting state
    - [`lease/app.py`](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/examples/plan_apps/lease/app.py): the example's app (not a GND command)
    - [`core.py`](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/examples/plan_apps/core.py): the code every example app shares
    - [`lease/stand_in_bot.py`](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/examples/plan_apps/lease/stand_in_bot.py): the scripted stand-in bot
    - [the recorded runs](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/examples/plan_apps/recordings/README.md): every model run, with caveats
    - [this page's Markdown source](https://github.com/vasiloglou/gnd-public/blob/main/docs/how-to/lease-schedule.md): replays and included files show only as include lines there; they render on the docs site

## Before you start

Set GND up first as the [course planner's "Before you start"](../tutorials/course-planner.md#what-youll-build)
shows: these pages need a GND newer than the 0.1.0 release, installed from a
checkout, and `python` must be that environment's Python.

<!-- gnd-run expect=0 -->
```sh
python -c "import gnd, pathlib, shutil; shutil.copytree(pathlib.Path(gnd.__file__).parent / 'examples/plan_apps', 'plan_apps', ignore=shutil.ignore_patterns('recordings', 'skill-sessions', '__pycache__'), dirs_exist_ok=True)"
gnd validate plan_apps/lease/model.orm.json
```

```text
OK: plan_apps/lease/model.orm.json is a valid GND ORM model
```

Optionally, the date rules in PyRel ([What PyRel is, and when you need it](../explanation/what-is-pyrel.md)):

```text
m.where(payment_due(step, l, a, due), lease_starts(step, l, start)).require(due >= start)
```

The lease itself is a document. Pulling its terms out of the signed PDF is the
`gnd-extract` skill's job, and `gnd verify` checks that each extracted fact
points at the sentence it came from; both run on GND only. In this example the
lease terms are typed in, so there is nothing to anchor; the schedule rules run
on GND and on PyRel.

## Ask for a schedule

```text
Set up the rent schedule for this lease.
```

## Read the refusal

No recorded lease plan was refused on one of the lease's own rules. The
refusals were malformed plans, answers that were not a plan, and steps that
cancelled a payment that did not exist. Claude Code's default model wrote the
rent as text, `'1450'`, in all five of its runs. The checker refused each plan
as malformed before it checked any rule, and the model fixed the type at the
next attempt. This is `claude-default/lease/run-1`:

<figure class="gnd-replay" tabindex="0" role="region" aria-label="Replay: Claude Code's default model sets up the rent schedule (recorded run 1)">
--8<-- "docs/assets/replays/lease-claude-default-run-1.svg"
</figure>

??? note "Transcript of the replay"

    ```text
    --8<-- "docs/assets/replays/lease-claude-default-run-1.txt"
    ```

No recorded lease run was refused on a date rule and then accepted. The
scripted stand-in bot shows that loop: its first schedule starts a month early.

<!-- gnd-run expect=0 -->
```sh
python plan_apps/lease/app.py ask "Set up the rent schedule for this lease." --out next-lease.pop.json
```

```text
attempt 1
  plan  schedule_payment(lease='apt-4b', amount=1450, due='2025-01-01')
  plan  schedule_payment(lease='apt-4b', amount=1450, due='2025-02-01')
  plan  schedule_payment(lease='apt-4b', amount=1450, due='2025-03-01')
  plan  schedule_payment(lease='apt-4b', amount=1450, due='2025-04-01')
  plan  schedule_payment(lease='apt-4b', amount=1450, due='2025-05-01')
  plan  schedule_payment(lease='apt-4b', amount=1450, due='2025-06-01')
  gnd check: exit 1
    states 1-6  due_after_start  violated  [{"$l": "apt-4b", "$a": 1450, "$due": "2025-01-01", "$start": "2025-02-01"}]
      the rule in PyRel: m.where(payment_due(step, l, a, due), lease_starts(step, l, start)).require(due >= start)
attempt 2
  plan  schedule_payment(lease='apt-4b', amount=1450, due='2025-02-01')
  plan  schedule_payment(lease='apt-4b', amount=1450, due='2025-03-01')
  plan  schedule_payment(lease='apt-4b', amount=1450, due='2025-04-01')
  plan  schedule_payment(lease='apt-4b', amount=1450, due='2025-05-01')
  plan  schedule_payment(lease='apt-4b', amount=1450, due='2025-06-01')
  plan  schedule_payment(lease='apt-4b', amount=1450, due='2025-07-01')
  gnd check: exit 0 (accepted)
  executed: the new state is in next-lease.pop.json
```

## The repaired plan

The second schedule runs from 1 February to 1 July and GND's checker accepts it. A
payment due on 31 July would also pass, with a warning: it is inside the lease
but less than a week before it ends.
