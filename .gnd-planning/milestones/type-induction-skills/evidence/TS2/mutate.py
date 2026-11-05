"""Apply each TS2 mutation in place, run the TS2 tests, restore. Prints one line each."""
import subprocess, sys, pathlib
J, T, S, C = "src/gnd/discover/type_judgements.py", "src/gnd/discover/types.py", "src/gnd/discover/service.py", "src/gnd/commands/discover.py"
M = [
 ("M1 evidence-in size refusal gone", S, "if len(evidence_raw) > evidence.MAX_EVIDENCE_BYTES:", "if False:"),
 ("M2 model_sha256 not named", S, '_BOUND_KEYS = ("model_sha256", ', '_BOUND_KEYS = ('),
 ("M3 byte comparison gone", S, "if recomputed != evidence_raw:", "if False:"),
 ("M4 digest binding gone", J, 'if document["evidence_sha256"] != evidence_sha256:', "if False:"),
 ("M5 kind check gone", J, 'if document["kind"] != kind:', "if False:"),
 ("M6 truncated groups allowed", J, 'if evidence["truncated_groups"]:', "if False:"),
 ("M7 generic mismatch allowed", J, 'if entry["generic"] != group["generic"]:', "if False:"),
 ("M8 ineligible status allowed", J, 'if group["status"] not in ELIGIBLE[kind]:', "if False:"),
 ("M9 twice allowed", J, "if number in found:", "if False:"),
 ("M10 of not checked", J, 'if verdict == "duplicate" and of not in candidates:', "if False:"),
 ("M11 of on distinct allowed", J, 'if (verdict == "duplicate") != (of is not None):', "if False:"),
 ("M12 D4 origin generic ignored", J, 'and candidate["origin"]["generic"] == group["generic"]', ""),
 ("M13 D4 whole-model index ignored", J, "already = list((induced or {}).get(number, []))", "already = []"),
 ("M14 missing verdicts allowed", J, "        if missing:\n", "        if False:\n"),
 ("M15 skill not scanned", J, 'for field in ("agent", "skill"):', 'for field in ("agent",):'),
 ("M16 rationale not scanned", J, 'if matcher.occurs(_tokens(entry["rationale"])):', "if False:"),
 ("M17 boundary tags gone", J, 'tokens.append(f"{int(left)}{int(right)}{piece}")', "tokens.append(piece)"),
 ("M18 model exemption gone", J, "exempt = _Matcher(patterns).found(_tokens(model_text))", "exempt = set()"),
 ("M19 exemption wiring gone", S, 'judgements.scan_free_text(documents, hidden, result["model_bytes"].decode("utf-8"))', 'judgements.scan_free_text(documents, hidden, "")'),
 ("M20 digests not hidden under customer", S, "*(() if show_digests else (record.attribute_sha256,))", "*()"),
 ("M21 values not hidden", S, "for text in (types.cell_text(record.attribute), *record.values,", "for text in (types.cell_text(record.attribute),"),
 ("M22 duplicate not reported", T, 'if verdict is not None and verdict.verdict == "duplicate":', "if False:"),
 ("M23 distinct follows the signature", T, "if match is not None and verdict is None:", "if match is not None:"),
 ("M24 many-to-many keeps one role", T, 'spanned = len(group["pairs"]), len(group["rows"]), ["entity", "value"]', 'spanned = len(group["pairs"]), len(group["rows"]), ["entity"]'),
 ("M25 skip counted multi_valued", T, '                    skipped["judged_skip"] += 1', '                    skipped["multi_valued"] += 1'),
 ("M26 induced_from under customer", T, '**({"induced_from": {"generic": generic_id, "attribute_sha256": digest}} if show_digests else {}),', '"induced_from": {"generic": generic_id, "attribute_sha256": digest},'),
 ("M27 judged mark gone", T, '                entry["judged"] = True\n', '                pass\n'),
 ("M28 clash reading not suffixed", T, 'label = new_id.removeprefix(f"{generic_id}_induced_") if verdict is not None else number', "label = number"),
 ("M29 repeats not counterexamples", T, 'single, multiple = list(group["pairs"].values()), group["repeats"]', 'single, multiple = list(group["pairs"].values()), []'),
 ("M30 type-evidence with evidence-in allowed", S, "if judging and evidence_path is not None:", "if False:"),
 ("M31 judgements before model", S, "judgements.check_binding(documents[kind], kind=kind, evidence_sha256=evidence_sha256)", "pass"),
]
names = sys.argv[1:]
for name, path, old, new in M:
    if names and name.split()[0] not in names:
        continue
    p = pathlib.Path(path); src = p.read_text()
    assert src.count(old) == 1, (name, src.count(old))
    p.write_text(src.replace(old, new))
    try:
        done = subprocess.run([sys.executable, "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider",
                               "tests/test_discover_type_judgements.py", "-k", "not t28"],
                              capture_output=True, text=True, env={"PYTHONDONTWRITEBYTECODE": "1", "PATH": "/usr/bin:/bin"})
        last = [l for l in done.stdout.splitlines() if " passed" in l or " failed" in l or "error" in l][-1:]
        print(f"{name} -> {'KILLED' if done.returncode else 'SURVIVED'} {' '.join(last)}", flush=True)
    finally:
        p.write_text(src)
print("restored")
