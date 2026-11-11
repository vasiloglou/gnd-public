# OS5 documentation candidate

The [approved spec](022-OS5-spec-gate.md) binds the explanation, refunds
how-to, README and packaged skill guidance. The explanation names the
Ossie 0.3.0.dev0 ontology scope and both pins, keeps PyRel optional and
reports the measured converter limits. The how-to shows the exported
many-to-one refund requester relationship and the restore commands.

The local replay exported and imported the refunds model. The export
contains `Refund.refund_by` with `Customer` as the second role and
`ManyToOne` multiplicity. The import reports
`source_identity_verified: true`. Both diff digests are
`sha256:599fb9814725de0af422670b7c6f09a8dc27a28951b9294734ec93985a45235c`;
all four entailment comparisons imply the corresponding rule.

```sh
.venv/bin/pytest -q tests/test_plan_app_docs.py -k ossie --tb=short
.venv/bin/zensical build --strict
.venv/bin/python tools/check_docs.py site
```

The focused docs checks passed with 6 tests and 86 deselections. The
strict local site build passed and the link checker checked 16,441
local links, assets and anchors. The full page-policy test also reports
a pre-existing 141-word paragraph in `grow-a-model.md`, which is
byte-identical to the OS5 base. The final affected-page tests passed
after adding the repository's required GitHub file callouts. The
independent review of the documentation diff remains pending.
