"""The home-page animation: an agent proposes a plan, GND checks it, the agent revises.

The story follows the packaged ``approvals`` example (docs/agents/plans.md):
reimbursing expense 41 directly fails the ``pre_submitted`` precondition and
warns on ``pre_has_approver``; the revised plan approves, submits and then
reimburses, and passes. The storyboard below is the single source of truth:
the same tracks produce the CSS keyframes of the animated SVG and the baked
frames of the GIF.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import pairwise

from svgkit import (
    Node,
    check_mark,
    circle,
    cross_mark,
    document,
    fmt,
    g,
    line,
    path,
    rect,
    spans,
    text,
    warn_mark,
)

WIDTH, HEIGHT = 800, 500
STORY = 16.0
CYCLE = 18.0  # the story plus a two-second hold on the final frame
FPS = 12
FADE = 0.35
FIGURE_ID = "gnd-hero"


@dataclass
class Track:
    """Piecewise-linear keyframes: (time, opacity, rise in px, horizontal scale)."""

    points: list[tuple[float, float, float, float]]
    final_visible: bool
    sweep_x: float | None = None  # left edge for horizontal-scale tracks

    def at(self, t: float) -> tuple[float, float, float]:
        pts = self.points
        if t <= pts[0][0]:
            return pts[0][1:]
        for (t0, *a), (t1, *b) in pairwise(pts):
            if t0 <= t <= t1:
                k = 0.0 if t1 == t0 else (t - t0) / (t1 - t0)
                return tuple(x + (y - x) * k for x, y in zip(a, b))
        return pts[-1][1:]


def appear(t0: float, rise: float = 8.0) -> Track:
    return Track([(0, 0, rise, 1), (t0, 0, rise, 1), (t0 + 0.4, 1, 0, 1),
                  (CYCLE - 0.5, 1, 0, 1), (CYCLE, 0, 0, 1)], final_visible=True)


def blip(t0: float, t1: float) -> Track:
    return Track([(0, 0, 0, 1), (t0, 0, 0, 1), (t0 + FADE, 1, 0, 1), (t1, 1, 0, 1),
                  (t1 + FADE, 0, 0, 1), (CYCLE, 0, 0, 1)], final_visible=False)


def sweep(t0: float, t1: float, x: float) -> Track:
    return Track([(0, 0, 0, 0), (t0, 1, 0, 0), (t1, 1, 0, 1), (t1 + FADE, 0, 0, 1),
                  (CYCLE, 0, 0, 1)], final_visible=False, sweep_x=x)


class Scene:
    """Collects positioned elements, each optionally animated by a track."""

    def __init__(self) -> None:
        self.items: list[tuple[Node, Track | None]] = []

    def add(self, *nodes: Node, track: Track | None = None) -> None:
        group = g(*nodes) if len(nodes) > 1 or track else nodes[0]
        self.items.append((group, track))


def storyboard() -> Scene:
    s = Scene()
    s.add(rect(0, 0, WIDTH, HEIGHT, "f-bg", rx=16))
    s.add(text(36, 40, "CODING AGENT", "sans f-muted", 12, weight=700, letter_spacing=2))
    s.add(text(436, 40, "GND · YOUR MODEL", "sans f-muted", 12, weight=700, letter_spacing=2))

    # Beat 1: the user asks.
    s.add(rect(36, 56, 328, 62, "f-bubble", rx=16),
          text(54, 82, "Reimburse Ada's €90 team dinner,", "sans f-bubble-ink", 15, weight=600),
          text(54, 104, "expense 41.", "sans f-bubble-ink", 15, weight=600), track=appear(0.6))
    s.add(*[circle(56 + 12 * i, 152, 3.5, "f-muted") for i in range(3)], track=blip(1.4, 2.4))

    # Beat 2: the agent answers with a plan, not prose.
    s.add(rect(36, 134, 328, 236, "f-card s-line", rx=12, stroke_width=1.5), track=appear(2.6, rise=0))
    s.add(text(54, 160, "plan.steps.json · draft 1", "mono f-muted", 13), track=blip(2.6, 10.2))
    s.add(text(54, 160, "plan.steps.json · draft 2", "mono f-muted", 13), track=appear(10.4, rise=0))
    s.add(line(50, 172, 350, 172, "s-line", stroke_width=1), track=appear(2.6, rise=0))
    s.add(spans(54, 198, [("f-primary", "pre:"), ("f-ink", "   state.pop.yaml")], 14), track=appear(2.9))
    s.add(spans(54, 222, [("f-primary", "then:"), ("f-ink", "  pay if accepted")], 14), track=appear(3.2))
    s.add(spans(54, 246, [("f-primary", "steps:")], 14), track=appear(3.5))
    s.add(spans(54, 270, [("f-muted", "  - "), ("f-accent", "reimburse_expense"), ("f-ink", "(41)")], 14),
          track=blip(3.8, 10.2))
    # Name the approver: Ada owns the expense, alice approves it. The longer line is set
    # at 12.5 so it stays inside the plan card.
    for index, (start, op, args, size) in enumerate([(10.6, "approve_expense", "(41, approver=alice)", 12.5),
                                                     (10.9, "submit_expense_to_workday", "(41)", 14)]):
        y = 270 + 24 * index
        s.add(rect(46, y - 16, 310, 22, "f-ok-bg", rx=4),
              text(42 + 8, y, "+", "mono f-ok", 14, weight=700),
              spans(54, y, [("f-muted", "  - "), ("f-accent", op), ("f-ink", args)], size), track=appear(start, rise=0))
    s.add(spans(54, 318, [("f-muted", "  - "), ("f-accent", "reimburse_expense"), ("f-ink", "(41)")], 14),
          track=appear(11.2, rise=0))

    # The model card: three operations and their preconditions.
    s.add(rect(436, 56, 328, 182, "f-card s-line", rx=12, stroke_width=1.5),
          text(454, 82, "approvals.orm.yaml", "mono f-muted", 13),
          text(746, 82, "3 operations", "sans f-muted", 12, anchor="end"),
          line(450, 94, 750, 94, "s-line", stroke_width=1))
    rows = [("approve_expense", "requires: draft"), ("submit_expense_to_workday", "requires: approved"),
            ("reimburse_expense", "requires: submitted · approver on file")]
    for index, (op, requires) in enumerate(rows):
        y = 118 + 42 * index
        s.add(text(454, y, op, "mono f-ink", 14, weight=600), text(454, y + 18, requires, "sans f-muted", 12),
              circle(744, y + 6, 9, "f-card s-line", stroke_width=1.5))
        s.add(circle(744, y + 6, 10, "f-ok-bg"), check_mark(744, y + 6), track=appear(13.0 + 0.15 * index, rise=0))
    s.add(circle(744, 210, 10, "f-fail-bg"), cross_mark(744, 210), track=blip(7.4, 12.9))

    # Beat 3: GND checks the plan.
    s.add(path("M368 262C398 262 402 266 430 266", "s-accent nofill", stroke_width=2),
          path("M424 261L432 266L424 271", "s-accent nofill", stroke_width=2, stroke_linejoin="round"),
          text(400, 252, "check", "sans f-accent", 11, weight=700, anchor="middle"), track=blip(5.0, 7.2))
    s.add(rect(436, 250, 328, 30, "f-code s-line", rx=15, stroke_width=1),
          text(452, 270, "$ gnd check --pre state --steps plan", "mono f-ink", 12.5), track=appear(5.2, rise=0))
    s.add(rect(436, 284, 328, 3, "f-accent", rx=1.5), track=sweep(5.4, 7.1, 436))
    s.add(rect(436, 284, 328, 3, "f-accent", rx=1.5), track=sweep(12.0, 12.8, 436))

    # Beat 4: the report names the failed precondition and the warning.
    s.add(rect(436, 296, 328, 130, "f-card s-line", rx=12, stroke_width=1.5),
          text(454, 318, "report", "mono f-muted", 13))
    s.add(cross_mark(462, 340),
          text(478, 345, "pre_submitted", "mono f-fail", 14, weight=700),
          text(478, 362, "step 1 · reimburse_expense · alethic", "sans f-muted", 12),
          warn_mark(462, 382),
          text(478, 387, "pre_has_approver", "mono f-warn", 14, weight=700),
          text(620, 387, "warning", "sans f-muted", 12),
          text(454, 414, "exit 1 · plan rejected", "sans f-fail", 13, weight=700), track=blip(7.4, 12.6))

    # Beat 5: closed feedback goes back; the agent revises.
    s.add(path("M432 352C398 352 400 304 370 304", "s-accent nofill", stroke_width=2, stroke_dasharray="5 4"),
          path("M377 299L369 304L377 309", "s-accent nofill", stroke_width=2, stroke_linejoin="round"),
          text(400, 374, "feedback", "sans f-accent", 11, weight=700, anchor="middle"), track=blip(9.8, 12.4))

    # Beat 6: accepted.
    s.add(check_mark(462, 340),
          text(478, 345, "3 steps · every precondition holds", "sans f-ok", 13.5, weight=650),
          text(478, 362, "post-state computed", "sans f-muted", 12),
          text(454, 414, "exit 0 · plan accepted", "sans f-ok", 13, weight=700), track=appear(13.0, rise=0))
    s.add(rect(36, 386, 328, 40, "f-ok-bg", rx=10), check_mark(58, 406),
          text(74, 411, "Paid: expense 41 reimbursed", "sans f-ok", 14, weight=650), track=appear(13.8))

    # Beat 7: the end card.
    s.add(text(400, 468, "Build agentic data apps that check themselves.", "sans f-ink", 22, weight=750,
               anchor="middle"),
          text(400, 490, "GND · Get Nick Done · inspired by GSD", "sans f-muted", 12, anchor="middle",
               letter_spacing=1), track=appear(14.4))
    return s


def _keyframes(name: str, track: Track) -> str:
    moving = any(dy or sx != 1 for _, _, dy, sx in track.points)
    frames = []
    for t, opacity, dy, sx in track.points:
        rule = f"opacity:{fmt(opacity)}"
        if moving:
            rule += f";transform:translate(0px,{fmt(dy)}px) scale({fmt(sx)},1)"
        frames.append(f"{fmt(100 * t / CYCLE)}%{{{rule}}}")
    return f"@keyframes {name}{{{''.join(frames)}}}"


def animated_svg() -> str:
    scene = storyboard()
    body: list[Node] = []
    css: list[str] = []
    for index, (node, track) in enumerate(scene.items):
        if track is None:
            body.append(node)
            continue
        name = f"gh-k{index}"
        node.attrs["class"] = f"{name}"
        if not track.final_visible:
            node.attrs["opacity"] = 0
        rule = f"#{FIGURE_ID} .{name}{{animation:{name} {fmt(CYCLE)}s linear infinite both"
        if track.sweep_x is not None:
            rule += ";transform-box:fill-box;transform-origin:0 50%"
        css.append(rule + "}")
        css.append(_keyframes(name, track))
        body.append(node)
    css.append(f"@media (prefers-reduced-motion: reduce){{#{FIGURE_ID} *{{animation:none !important}}}}")
    return document(FIGURE_ID, WIDTH, HEIGHT, "An agent's plan checked by GND",
                    "Asked to reimburse expense 41, the agent proposes a plan that pays it directly. GND "
                    "checks the plan against the model: the pre_submitted precondition fails and "
                    "pre_has_approver warns. With that feedback the agent adds the approval and Workday "
                    "steps; the revised plan passes and the expense is paid.", body, "".join(css))


def frame_svg(t: float) -> str:
    """The scene at time t, with animation resolved into attributes (for rasterizing)."""
    scene = storyboard()
    body: list[Node] = []
    for node, track in scene.items:
        if track is not None:
            opacity, dy, sx = track.at(t)
            if opacity <= 0.001:
                continue
            node.attrs["opacity"] = round(opacity, 3)
            if track.sweep_x is not None:
                x0 = track.sweep_x
                node.attrs["transform"] = f"translate({fmt(x0)} 0) scale({fmt(max(sx, 0.001))} 1) translate({fmt(-x0)} 0)"
            elif dy:
                node.attrs["transform"] = f"translate(0 {fmt(dy)})"
        body.append(node)
    return document(FIGURE_ID, WIDTH, HEIGHT, "GND hero frame", f"t={fmt(t)}", body)
