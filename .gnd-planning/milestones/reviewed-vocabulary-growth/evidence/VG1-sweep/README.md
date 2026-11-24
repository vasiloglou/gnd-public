# VG1 scaling sweep

The experiment of the VG1 spec ("An experiment, recorded before it runs"),
run on beast-3 (Apple M5 Pro, 18 cores, macOS, uv-managed Python 3.13.18),
once at the base and once at the head, from the same built interop fixture.

| File | What |
|---|---|
| `vg1_sweep.py` | the driver: each run is a fresh process; a run over 120 s is recorded as `over`, not repeated, and ends its series |
| `vg1_once.py` | one in-process route over a grown copy of the fixture; prints one JSON line |
| `vg1_grow.py` | the five shapes and the deep chain, as `tests/test_vg1_object_type_scaling.py` builds them |
| `base-sweep.jsonl` | the run at `1f403b07` (`main` before VG1) |
| `head-sweep.jsonl` | the run at `5427e8fe` (VG1's last code commit) |

Command, from each checkout: `uv run python ../vg1_sweep.py ../interop OUT.jsonl`,
where `../interop` is `gnd.examples.literature.interop.build(out)` written
once. The judgments route reuses `bind` from
`tests/test_ir1_judgments_includes.py`. Each row is one size of one series;
`min_seconds` is the fastest of three runs, or null when a run went over.
