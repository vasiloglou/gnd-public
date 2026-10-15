# How a rule becomes a PyRel check

Every rule in a GND model becomes PyRel code that GND writes for you. This page
follows one rule from the registrar's sentence to the two programs that check
it, and says what each program can and cannot do. PyRel is optional: GND's own
checker needs none of this. [What PyRel is, and when you need it](what-is-pyrel.md)
explains where PyRel runs and why you might want it.

!!! info "Files on GitHub"

    - [`pyrel_rules.py`](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/export/pyrel_rules.py): the code that writes both PyRel programs
    - [`course/model.orm.json`](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/examples/plan_apps/course/model.orm.json): the model used on this page
    - [this page's Markdown source](https://github.com/vasiloglou/gnd-public/blob/main/docs/explanation/rules-as-pyrel.md)

## One rule, three forms

The registrar wrote:

```text
A student can't take a course before passing every course it needs,
directly or through a chain of prerequisites.
```

The model states it as a guarded rule: *if* a student enrolls in a course and
the course needs another course, directly or through a chain, *then* the
student has passed that course. GND turns the model into two PyRel programs.
Export them and look at that one rule in each:

<!-- gnd-run expect=0 -->
```sh
python -c "import gnd, pathlib, shutil; shutil.copytree(pathlib.Path(gnd.__file__).parent / 'examples/plan_apps', 'plan_apps', ignore=shutil.ignore_patterns('recordings', 'skill-sessions', '__pycache__'), dirs_exist_ok=True)"
gnd export pyrel plan_apps/course/model.orm.json --rules lqp --out course_lqp.py > /dev/null
gnd export pyrel plan_apps/course/model.orm.json --rules duckdb --out course_duckdb.py > /dev/null
grep -h "require(passed(step, student, needs))$" course_lqp.py | grep -v "#" | sed 's/^ *//'
grep -h "found\['prerequisites_first'\]" course_duckdb.py | sed 's/^ *//'
```

```text
m.where(enrolls(step, student, course, term), prerequisite_chain(step, course, needs)).require(passed(step, student, needs))
found['prerequisites_first'] = rows(m.where(enrolls(step, student, course, term), prerequisite_chain(step, course, needs), not_(passed(step, student, needs))).select(step, course, needs, student, term))
```

| | The LQP program | The DuckDB program |
|---|---|---|
| What the rule looks like | `where(...)` the situation, `.require(...)` what must hold | the same `where`, with the requirement negated, and `select` |
| Where it runs | written for a RelationalAI engine | on your laptop, with no account |
| What it returns | what the engine reports for a requirement; not yet observed | every set of facts that breaks the rule: the witnesses |
| Status in GND | compiled and counted; not yet run on an engine | runs in the tests and checked every recorded plan; GND's checker agrees on each |

A requirement and its violation query say the same thing from two sides. The
`where` part picks the situations the rule is about; the requirement must hold
in each. The DuckDB program asks for the situations where it does not, and
those rows are the facts GND names in its feedback, like
`{"$course": "CS340", "$needs": "MATH220", ...}`.

## Rules that need more than one line

- **A chain.** `prerequisite_chain` is a derived fact, defined from
  `course_needs` and from itself. GND computes it before any rule reads it, in
  the order the definitions depend on each other.
- **A total.** "At most 18 credits" reads a derived sum, `term_credits`. Like
  GND, PyRel counts each distinct course and credit pair once.
- **A date.** "Not before the refill interval has passed" adds days to a date
  with `std_date.add(last, days(n))`. Dates are always facts in the input; the
  programs have no clock.
- **A plan.** Every relation also takes the state, `step`. A precondition reads
  the state before a step, `previous(step, before)`. A rule across a step reads
  both.
- **A judgement.** A textual rule has no PyRel line. It is reported as not
  checked on every run.

## What GND refuses to export

Some constructs have no faithful PyRel form yet, so GND refuses the export and
names the construct, rather than writing a program that checks something
different. The [PyRel runtime page](../runtimes/pyrel.md) lists them.

## See it in an app

Each plan app prints its rules this way: `python plan_apps/course/app.py rules`.
When a plan breaks a rule, the app shows that rule's PyRel line under the
failure, as in step 6 of the [course planner tutorial](../tutorials/course-planner.md).
