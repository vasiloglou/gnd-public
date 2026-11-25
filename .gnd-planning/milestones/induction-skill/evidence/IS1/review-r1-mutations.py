"""Re-run each review mutation against the repaired tests; every one must now fail."""
import sys, re, subprocess
from pathlib import Path
SKILL = Path("src/gnd/skills/gnd-induce/SKILL.md"); orig = Path(sys.argv[1]).read_text()
IDX = Path("docs/agents/index.md"); idx = IDX.read_text()
def run(label, mutate, tests, target=SKILL, base=None):
    base = orig if base is None else base
    target.write_text(mutate(base))
    try:
        r = subprocess.run(["uv","run","-q","pytest","-q","-p","no:cacheprovider","--tb=no",*tests], capture_output=True, text=True)
    finally:
        target.write_text(base)
    last = r.stdout.strip().splitlines()[-1]
    print(f"{'CAUGHT ' if 'failed' in last else 'MISSED '} {label}: {last}")
J, M = "(../gnd-judge-fact-types/SKILL.md)", "(../gnd-model-multivalued/SKILL.md)"
T = ["tests/test_induce_skill.py"]
run("F6 swap the two judge links", lambda t: t.replace(J, "@@").replace(M, J).replace("@@", M), T)
RE_ = "Covered sets come only from the learner's output"
run("F7 R-e a second time in the same file", lambda t: t + "\n" + t[t.index(RE_):t.index("including refusal text.")+24] + "\n", T)
RC = "It never writes, edits or re-binds a label manifest; labels come from the user."
run("F7 R-c hidden in an HTML comment", lambda t: t.replace(RC, f"<!-- {RC} -->"), T)
run("F8 LLM route reversed", lambda t: t.replace("outside this conversation; name it and stop.", "here: answer the prompt and construct its run record."), T)
run("F8 handoff condition negated", lambda t: t.replace("Only after the command that wrote a proposal exited 0 and the proposal file exists", "Even if no command exited 0 or wrote a file"), T)
run("F8 exit-11 row deleted", lambda t: re.sub(r"\n\| 11 \|[^\n]*", "", t), T)
run("F9 mined-rules line replaced by a second check", lambda t: re.sub(r"gnd import mined-rules MODEL[^\n]*", "gnd check MODEL POPULATION", t), T)
run("F9 --families shortened to --fam", lambda t: t.replace("--families uniqueness,mandatory", "--fam uniqueness,mandatory"), T)
run("F10 trailing spaces on the Learn heading", lambda t: t.replace("## Learn\n", "## Learn  \n"), T)
run("F11 fixed actor", lambda t: t.replace("--actor ACTOR", "--actor operator"), T)
run("F11 git var for the actor", lambda t: t + "\nGet the actor with git var GIT_AUTHOR_IDENT.\n", T)
run("F11 pip3 install", lambda t: t + "\npip3 install popper\n", T)
run("F11 /srv path", lambda t: t + "\nSee /srv/reviewer/runs/april.\n", T)
run("F10 index row moved into a fence", lambda t: t.replace(next(l for l in t.splitlines() if "`gnd-induce`" in l), "```text\n" + next(l for l in t.splitlines() if "`gnd-induce`" in l) + "\n```"), T, IDX, idx)
run("F10 index command gnd check -> gnd checker", lambda t: t.replace("`gnd check` | 3 a named refusal", "`gnd checker` | 3 a named refusal"), T, IDX, idx)
