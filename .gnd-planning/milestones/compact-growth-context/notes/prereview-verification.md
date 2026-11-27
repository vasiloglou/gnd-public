# Verification of the pre-existing implementation

Baseline deed51bb4866a3cf4771d299f487b30ee929e212, Python 3.14.3. These measurements precede formal phase acceptance.

- The full-vocabulary fixture contained 16,927 source bytes. The ordinary rendering used 31,742 UTF-8 bytes and the growth rendering used 7,505. This measures schema context on that fixture.
- Installed the built wheel in a new virtual environment. Both public entry points returned the same 455 bytes for the include-backed seed. The packaged example recovered work_has_version on its second query and recorded reuse and defer.
- Whole-tree Ruff passed in the isolated topic checkout.
- The direct checks and repository guards produced 1 failed, 919 passed, 2 deselected in 126.74s. The failing disclosure parity guard ran the frozen CLI grammar tests. Their independently declared model verbalization parser lacks the new flag. GC2 needs to declare --for-growth in the expected parser and rerun the guard and CLI grammar tests.
- The loader rejects an include file that itself declares includes. The plan wording about transitive pins needs correction to the root and its directly declared pins.
