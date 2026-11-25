# The Ossie oracle lane, first run over the relational files

**Run 2026-11-25** on the owner's request ([gate](../018-OB5-checkpoint-gate.md)),
at commit `717f47e8`. It discharges OB3-Q3 and OB5 H7.

## Setup

A scratch root prepared from the OS0 receipt
(`.gnd-planning/milestones/ossie-interchange/evidence/OS0/README.md`):

| Item | Value |
|---|---|
| `apache/ossie` | `ee89dbdc2844d8b7d293ed42c8613928bb99505f` |
| `apache/ossie-converters` | `83ddc294c8840f5f497a2bdbec2348a128fc2254` |
| `ontology/ontology.json`, `ontology/mapping.json`, `validation/validate.py` | sha256 equal to `pins.json` |
| Environment `a` (validator) | Python 3.11.15, PyYAML 6.0.3, jsonschema 4.26.0, sqlglot 30.31.0 and the receipt's other pins |
| Environment `b` (parser) | `converters/ontology` installed |

Environments `c` and `d` (the RelationalAI consumer) were not built, so the
one consumer test was deselected.

## Command and result

```text
GND_OSSIE_ORACLE_ROOT=<scratch> uv run pytest -q -m ossie_oracle tests/test_ossie_external_oracle.py -k "not consumer"
1 failed, 86 passed, 1 deselected in 17.83s
```

| Test | Result |
|---|---|
| `test_external_census` (the ontology, validator and parser) | passed |
| `test_external_relational_census` (OB3 T11: semantic model and mapping of every census model) | **passed** |
| `test_external_physical_binding_cases` (OB4 T13) | **failed** on case V2 |
| the refusal, YAML, OS2 corpus and keyword tests | passed |

So the upstream validator accepts the quoted upper-case identifiers and the
`CASE WHEN` expressions that OB3 could not confirm.

## The failure

Case V2 has tables named `uni.student`, `uni.enrolled` and `uni.course`. The
validator reports eight errors of this form:

```text
[Reference] ...: expression names '"UNI.STUDENT"."NR"' but the semantic model declares no dataset '"UNI.STUDENT"'
```

**Cause.** GND writes every identifier quoted and upper-cased (OB3 E5). The
validator upper-cases a declared name only when it is a *regular*
identifier, one that can be written without quotes. Any other name "can only
be written quoted and is kept as written" (`validate.py`,
`declared_name`; Ossie `core-spec/expression_language.md`, "normalized
identifier"). `uni.student` contains a dot, so it is kept as written, and
the reference must be `"uni.student"`.

**Measured with the pinned validator** (every character from U+0020 to
U+2FFF, inside and at the start of a name; 266 keyword-like words):

- Kept as written: a name with white space or one of
  ``! " # % & ' ( ) * + , - . / : ; < = > ? @ [ \ ] ^ ` { | } ~``, a name that
  starts with a digit, and the two words `not` and `select`.
- Upper-cased: everything else, including `$`, non-ASCII letters, and
  keywords such as `from`, `order`, `group` and `table`.

**Reach.**

- The built-in mapping passes for all census models.
- A binding whose table or column name is not regular fails upstream today.
  A schema-qualified name such as `fin.refunds` is one.
- In the approved corpora, only `physical_binding/V2/expected.mapping.yaml`
  holds such names (six expressions). The OB5 example binding uses dotted
  names too.

**Not changed.** No code or corpus file is changed by this run. V2's
expected mapping is an approved answer, so changing it goes to the owner.
