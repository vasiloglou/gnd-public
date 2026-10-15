"""Render a recorded session as an animated SVG replay, in the hero figure's visual language.

Inputs are committed recordings only:
  - a plan app's session.txt (src/gnd/examples/plan_apps/recordings/<model>/<example>/run-N/), or
  - a Claude Code stream-json transcript (one or more turn-NN.jsonl files of a skill session).

The replay is a terminal card whose lines appear one after another, once, when the page loads. Under
prefers-reduced-motion nothing moves: every line is drawn in its final state. Colours are the figure
theme tokens, so the site's light and dark themes apply. The same text goes under the replay as a
transcript (see --transcript), so nothing is only in the picture.

    python tools/render_replay.py SESSION.txt --title "..." --out docs/assets/replays/NAME.svg
    python tools/render_replay.py turn-01.jsonl turn-02.jsonl ... --title "..." --out ...
    python tools/render_replay.py ... --out FILE --check     # exit 1 when FILE differs from a fresh render
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
import textwrap
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "figures"))
from svgkit import DARK, LIGHT, MONO, SANS  # noqa: E402

WIDTH, COLUMNS, LINE, TOP, PAD = 760, 96, 17, 46, 18
STEP_SECONDS, MAX_LINES = 0.22, 120


def session_lines(text: str) -> list[tuple[str, str]]:
    """(class, text) per line of a plan app's session.txt."""
    lines = []
    for raw in text.splitlines():
        stripped = raw.strip()
        kind = ("head" if raw.startswith("attempt ") else
                "ok" if "(accepted)" in raw or stripped.startswith("executed:") else
                "fail" if any(w in raw for w in (" violated ", "check: exit 1", "check: exit 3", "not usable",
                                                  "no plan was")) else
                "pyrel" if stripped.startswith("the rule in PyRel:") else
                "say" if stripped.startswith(("the bot says:", "the bot made no plan:")) else
                "plan" if stripped.startswith("plan ") else "ink")
        lines.append((kind, raw))
    return lines


def _short(value: str, limit: int = 300) -> str:
    value = " ".join(value.split())
    return value if len(value) <= limit else value[:limit - 1] + "…"


def stream_lines(texts: list[str]) -> list[tuple[str, str]]:
    """(class, text) per event of Claude Code stream-json turns: what the user said, what the assistant
    said, and each tool it used, with a short result."""
    lines = []
    denied = set()   # tool calls Claude Code's permission rules refused, from each turn's closing result event
    for text in texts:
        for raw in text.splitlines():
            if '"permission_denials"' in raw:
                try:
                    denied |= {d.get("tool_use_id") for d in json.loads(raw).get("permission_denials") or []}
                except ValueError:
                    pass
    for number, text in enumerate(texts, 1):
        for raw in text.splitlines():
            try:
                event = json.loads(raw)
            except ValueError:
                continue
            if event.get("type") == "user" and isinstance(event.get("message", {}).get("content"), str):
                lines.append(("head", f"you: {_short(event['message']['content'], 200)}"))
            elif event.get("type") == "assistant":
                for part in event["message"].get("content", []):
                    if part.get("type") == "thinking" and part.get("thinking", "").strip():
                        lines.append(("muted", f"  (thinks) {_short(part['thinking'], 200)}"))
                    if part.get("type") == "text" and part["text"].strip():
                        lines.append(("say", f"claude: {_short(part['text'])}"))
                    elif part.get("type") == "tool_use":
                        shown = part["input"].get("command") or part["input"].get("file_path") or \
                            part["input"].get("pattern") or ""
                        lines.append(("plan", f"  {part['name']} {_short(str(shown), 160)}"))
            elif event.get("type") == "user" and isinstance(event.get("message", {}).get("content"), list):
                for part in event["message"]["content"]:
                    content = part.get("content") if part.get("type") == "tool_result" else None
                    text = content if isinstance(content, str) else " ".join(
                        c.get("text", "") for c in content or [] if isinstance(c, dict))
                    if part.get("type") == "tool_result" and part.get("tool_use_id") in denied:
                        lines.append(("fail", "    → refused by Claude Code's permission rules"))
                    elif part.get("type") == "tool_result" and part.get("is_error") and text.endswith("output not kept]"):
                        lines.append(("fail", "    → returned an error (its output is not kept)"))
                    elif text and not text.endswith("output not kept]"):
                        text = re.sub(r" \(file state is current in your context[^)]*\)", "", text)
                        shown = [line for line in text.splitlines() if line.strip()][:2]
                        first = ": ".join(shown) if shown and shown[0].startswith("Exit code") else (shown or [""])[0]
                        lines.append(("fail" if part.get("is_error") or "ERROR" in first else "ok"
                                      if first.startswith("OK") else "ink", f"    → {_short(first, 200)}"))
            elif event.get("type") == "result":
                lines.append(("muted", f"  (turn {number} ends)"))
    return lines


def user_turns(paths: list[Path], said: list[str]) -> list[str]:
    """Stream-json in --print mode does not echo the prompt, so the user's declared turns are put back in."""
    texts = []
    for path, words in zip(paths, said):
        texts.append(json.dumps({"type": "user", "message": {"content": words}}) + "\n" +
                     path.read_text(encoding="utf-8"))
    return texts


def condensed(lines: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """For the picture only: a run of the assistant reading the skill's own pages (and their results) becomes one
    line. The transcript keeps every call."""
    out, run = [], 0

    def reading(text: str) -> bool:
        return text.startswith(("  Read <repo>/src/gnd/skills", "  Grep ")) or (
            text.startswith("  Bash ") and "<repo>/src/gnd/skills" in text)

    padded = lines + [("end", "")]
    for index, (kind, text) in enumerate(padded):
        failed_next = index + 1 < len(padded) and padded[index + 1][0] == "fail"
        if (reading(text) and not failed_next) or (run and text.startswith("    → ") and not text.startswith("    → OK")
                                                   and "ERROR" not in text and kind not in ("end", "fail")):
            run += 0 if text.startswith("    → ") else 1
            continue
        if run:
            out.append(("muted", f"  … reads the skill's reference pages ({run} call{'s' if run > 1 else ''}; all in the transcript)"))
            run = 0
        if kind != "end":
            out.append((kind, text))
    return out


def wrap(lines: list[tuple[str, str]]) -> list[tuple[str, str]]:
    out = []
    for kind, text in lines:
        indent = len(text) - len(text.lstrip(" "))
        pieces = textwrap.wrap(text, COLUMNS, subsequent_indent=" " * (indent + 4), drop_whitespace=False,
                               replace_whitespace=False) or [""]
        out.extend((kind, piece.rstrip()) for piece in pieces)
    if len(out) > MAX_LINES:
        out = out[:MAX_LINES - 1] + [("muted", f"… {len(out) - MAX_LINES + 1} more lines in the transcript below")]
    return out


def svg(lines: list[tuple[str, str]], title: str, ident: str) -> str:
    lines = wrap(lines)
    height = TOP + LINE * len(lines) + PAD
    tokens = ";".join(f"--gf-{k}:{v}" for k, v in LIGHT.items())
    dark = ";".join(f"--gf-{k}:{v}" for k, v in DARK.items())
    paint = {"head": "accent", "ok": "ok", "fail": "fail", "pyrel": "primary", "say": "warn", "plan": "ink",
             "ink": "ink", "muted": "muted"}
    style = (f":where(#{ident}){{{tokens}}}@media (prefers-color-scheme: dark){{:where(#{ident}){{{dark}}}}}"
             + "".join(f"#{ident} .c-{k}{{fill:var(--gf-{v})}}" for k, v in paint.items())
             + f"#{ident} .bg{{fill:var(--gf-code)}}#{ident} .frame{{fill:var(--gf-card);stroke:var(--gf-line)}}"
             f"#{ident} text{{font-family:{MONO};font-size:12px;white-space:pre}}"
             f"#{ident} .title{{font-family:{SANS};font-size:13px;font-weight:600;fill:var(--gf-ink)}}"
             f"#{ident} .l{{animation:{ident}-in .3s ease-out both}}"
             f"@keyframes {ident}-in{{from{{opacity:0}}to{{opacity:1}}}}"
             f"@media (prefers-reduced-motion: reduce){{#{ident} .l{{animation:none}}}}")
    rows = []
    for number, (kind, text) in enumerate(lines):
        y = TOP + LINE * number + 12
        rows.append(f'<text class="l c-{kind}" x="{PAD}" y="{y}" xml:space="preserve" '
                    f'style="animation-delay:{number * STEP_SECONDS:.2f}s">{html.escape(text, quote=False)}</text>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" id="{ident}" class="gnd-figure" role="img" viewBox="0 0 {WIDTH} {height}" '
            f'width="{WIDTH}" height="{height}" aria-labelledby="{ident}-title {ident}-desc">\n'
            f'<title id="{ident}-title">{html.escape(title)}</title>\n'
            f'<desc id="{ident}-desc">A replay of a recorded session; the full text is in the transcript below the '
            f'figure.</desc>\n<style>{style}</style>\n'
            f'<rect class="frame" x="0.5" y="0.5" width="{WIDTH - 1}" height="{height - 1}" rx="10"/>\n'
            f'<text class="title" x="{PAD}" y="27">{html.escape(title)}</text>\n' + "\n".join(rows) + "\n</svg>\n")


def transcript(lines: list[tuple[str, str]]) -> str:
    return "\n".join(text for _, text in lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--title", required=True)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--said", action="append", default=[],
                        help="stream-json input: the user's words for each turn, in order")
    parser.add_argument("--transcript", type=Path, help="also write the text transcript here")
    parser.add_argument("--check", action="store_true", help="compare with --out (and --transcript) instead")
    args = parser.parse_args()
    if args.inputs[0].suffix == ".jsonl":
        lines = stream_lines(user_turns(args.inputs, args.said + [""] * len(args.inputs)))
    else:
        lines = session_lines(args.inputs[0].read_text(encoding="utf-8"))
    ident = "replay-" + re.sub(r"[^a-z0-9-]", "-", args.out.stem.lower())   # a CSS id: "3.2" would read as a class
    outputs = {args.out: svg(condensed(lines), args.title, ident)}
    if args.transcript:
        outputs[args.transcript] = transcript(lines)
    if args.check:
        stale = [str(p) for p, text in outputs.items() if not p.exists() or p.read_text(encoding="utf-8") != text]
        if stale:
            print("stale replay: " + ", ".join(stale), file=sys.stderr)
            return 1
        return 0
    for path, text in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
