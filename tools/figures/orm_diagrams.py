"""ORM 2 notation diagrams for the documentation (static SVG).

Entity types are soft rectangles with their reference mode, value types are
dashed, fact types are adjacent role boxes, and constraints use the ORM 2
constraint colour: uniqueness bars, mandatory dots and the exclusion circle.
Run ``python tools/figures/build.py`` to regenerate every figure.
"""

from __future__ import annotations

from svgkit import (
    Node,
    circle,
    document,
    fmt,
    g,
    line,
    path,
    rect,
    text,
)

ROLE_W = 36
ROLE_H = 22
TYPE_W = 130
TYPE_H = 52


def background(width: int, height: int, label: str) -> list[Node]:
    return [rect(0, 0, width, height, "f-bg", rx=16),
            text(24, 32, label, "sans f-muted", 12, weight=600, letter_spacing=2)]


def object_type(x: float, y: float, name: str, ref: str | None = None, value: bool = False,
                w: float = TYPE_W) -> Node:
    box = rect(x, y, w, TYPE_H, "f-card s-primary", rx=12, stroke_width=2,
               stroke_dasharray="6 4" if value else None)
    if box.attrs.get("stroke-dasharray") is None:
        box.attrs.pop("stroke-dasharray", None)
    cx = x + w / 2
    if ref:
        return g(box, text(cx, y + 23, name, "sans f-ink", 16, weight=600, anchor="middle"),
                 text(cx, y + 41, ref, "sans f-muted", 12, anchor="middle"))
    return g(box, text(cx, y + 31, name, "sans f-ink", 16, weight=600, anchor="middle"))


def roles(x: float, cy: float, count: int = 2) -> Node:
    y = cy - ROLE_H / 2
    return g(*[rect(x + i * ROLE_W, y, ROLE_W, ROLE_H, "f-card s-ink", stroke_width=1.6)
               for i in range(count)])


def connector(x1: float, y1: float, x2: float, y2: float) -> Node:
    return line(x1, y1, x2, y2, "s-ink", stroke_width=1.6)


def uniqueness(x: float, cy: float, first: int, last: int, cls: str = "s-alethic") -> Node:
    y = cy - ROLE_H / 2 - 6
    return line(x + first * ROLE_W + 3, y, x + (last + 1) * ROLE_W - 3, y, cls,
                stroke_width=2.6, stroke_linecap="round")


def mandatory(cx: float, cy: float) -> Node:
    return circle(cx, cy, 4.5, "f-alethic")


def exclusion(cx: float, cy: float, r: float = 11) -> Node:
    d = (f"M{fmt(cx - r * .55)} {fmt(cy - r * .55)}L{fmt(cx + r * .55)} {fmt(cy + r * .55)}"
         f"M{fmt(cx + r * .55)} {fmt(cy - r * .55)}L{fmt(cx - r * .55)} {fmt(cy + r * .55)}")
    return g(circle(cx, cy, r, "f-card s-alethic", stroke_width=2),
             path(d, "s-alethic nofill", stroke_width=2))


def reading(cx: float, y: float, content: str) -> Node:
    return text(cx, y, content, "sans f-ink", 15, anchor="middle", font_style="italic")


def note(x: float, y: float, content: str, size: float = 13) -> Node:
    return text(x, y, content, "sans f-muted", size)


# ------------------------------------------------------------------ figures

def d1_fact_type() -> str:
    body = background(720, 240, "ORM 2 · OBJECT TYPES AND A FACT TYPE")
    body += [
        object_type(60, 94, "User", "(.id)"), object_type(530, 94, "Book", "(.id)"),
        connector(190, 120, 324, 120), connector(396, 120, 530, 120),
        roles(324, 120), uniqueness(324, 120, 0, 1),
        reading(360, 154, "… rated …"),
        note(60, 208, "One role box per participant. The bar across both roles: each (user, book) pair is stated once."),
    ]
    return document("gnd-orm-d1", 720, 240, "User rated Book in ORM 2 notation",
                    "Two entity types, User and Book, identified by id, joined by the binary fact type "
                    "'User rated Book'. A uniqueness bar spans both roles.", body)


def d2_exclusion() -> str:
    body = background(720, 320, "ORM 2 · EXCLUSION")
    body += [
        object_type(40, 124, "User", "(.id)"), object_type(550, 124, "Book", "(.id)"),
        connector(170, 150, 324, 70), connector(396, 70, 550, 150),
        connector(170, 150, 324, 230), connector(396, 230, 550, 150),
        roles(324, 70), roles(324, 230),
        reading(360, 48, "… is recommended …"), reading(360, 266, "… rated …"),
        line(360, 81, 360, 139, "s-alethic", stroke_width=1.8, stroke_dasharray="4 3"),
        line(360, 161, 360, 219, "s-alethic", stroke_width=1.8, stroke_dasharray="4 3"),
        exclusion(360, 150),
        note(40, 300, "The circled cross: no (user, book) pair may be both recommended and rated."),
    ]
    return document("gnd-orm-d2", 720, 320, "An exclusion constraint in ORM 2 notation",
                    "User and Book are joined by two fact types, 'is recommended' and 'rated'. A circled "
                    "cross connected to both role pairs says no pair may appear in both.", body)


def d3_uniqueness_mandatory() -> str:
    body = background(720, 240, "ORM 2 · UNIQUENESS AND MANDATORY")
    body += [
        object_type(60, 94, "Book", "(.id)"), object_type(530, 94, "Genre", value=True),
        connector(190, 120, 324, 120), connector(396, 120, 530, 120),
        roles(324, 120), uniqueness(324, 120, 0, 0), mandatory(194.5, 120),
        reading(360, 154, "… has primary genre …"),
        note(60, 196, "Bar over the Book role: at most one primary genre per book."),
        note(60, 216, "Dot where the line meets Book: at least one. Together: exactly one."),
    ]
    return document("gnd-orm-d3", 720, 240, "Uniqueness and mandatory constraints in ORM 2 notation",
                    "Book (entity) and Genre (value type, dashed) joined by 'has primary genre'. A uniqueness "
                    "bar covers the Book role and a mandatory dot sits on the Book end.", body)


def d4_modality() -> str:
    body = background(720, 270, "ORM 2 · MUST VERSUS SHOULD")
    body += [
        object_type(60, 52, "User", "(.id)"), object_type(530, 52, "Book", "(.id)"),
        connector(190, 78, 324, 78), connector(396, 78, 530, 78),
        roles(324, 78), reading(360, 112, "… is recommended …  ¹ ²"),
        rect(40, 136, 310, 104, "f-card s-alethic", rx=12, stroke_width=2),
        text(56, 160, "¹ age_appropriate · alethic", "sans f-alethic", 14, weight=700),
        text(56, 182, "Never recommend an adult-rated", "sans f-ink", 14),
        text(56, 200, "book to a minor.", "sans f-ink", 14),
        text(56, 226, "Violated → the check fails (band 1)", "sans f-fail", 13, weight=600),
        rect(370, 136, 310, 104, "f-card s-deontic", rx=12, stroke_width=2, stroke_dasharray="6 4"),
        circle(392, 155, 5, "nofill s-deontic", stroke_width=2),
        text(404, 160, "² preferred_genre · deontic", "sans f-deontic", 14, weight=700),
        text(386, 182, "A recommendation should match", "sans f-ink", 14),
        text(386, 200, "a preferred genre.", "sans f-ink", 14),
        text(386, 226, "Violated → a warning; still accepted", "sans f-warn", 13, weight=600),
        note(40, 258, "Footnoted textual constraints; the small circle marks the deontic (should) modality.", 12),
    ]
    return document("gnd-orm-d4", 720, 270, "Alethic and deontic constraints",
                    "The fact type 'User is recommended Book' carries two footnoted rules: an alethic rule "
                    "that fails the check and a deontic rule that only warns.", body)


def d5_derived() -> str:
    body = background(720, 290, "ORM 2 · DERIVED FACT TYPE")
    body += [
        object_type(60, 52, "Book", "(.id)"), object_type(530, 52, "User", "(.id)"),
        connector(190, 78, 324, 78), connector(396, 78, 530, 78),
        roles(324, 78), uniqueness(324, 78, 0, 1),
        reading(360, 112, "… is eligible for … *"),
        rect(40, 136, 640, 100, "f-card s-line", rx=12, stroke_width=1.5),
        text(58, 162, "* Book is eligible for User if", "sans f-ink", 14, weight=600),
        text(58, 184, "User prefers some Genre and Book has primary genre that Genre,", "sans f-ink", 14),
        text(58, 206, "and Book is not blocked for User, and User has not rated Book.", "sans f-ink", 14),
        text(58, 226, "(negation is stratified)", "sans f-muted", 12),
        note(40, 266, "Computed by the rule, never supplied. Unknown inputs yield cannot-decide, not yes or no."),
    ]
    return document("gnd-orm-d5", 720, 290, "A derived fact type in ORM 2 notation",
                    "The fact type 'Book is eligible for User' is marked with an asterisk and defined by a "
                    "rule using preferences, genres, blocking and ratings.", body)


def d6_operation() -> str:
    body = background(800, 320, "GND EXTENSION TO ORM 2 · OPERATIONS")
    body += [
        rect(30, 56, 300, 228, "f-card s-accent", rx=12, stroke_width=2),
        text(48, 84, "approve_expense", "mono f-ink", 15, weight=700),
        text(48, 104, "(expense, approver)", "mono f-muted", 13),
        text(48, 132, "REQUIRES", "sans f-muted", 11, weight=700, letter_spacing=1.5),
        text(48, 151, "Expense has status 'draft'", "sans f-ink", 13),
        text(48, 179, "RETRACTS · ASSERTS", "sans f-muted", 11, weight=700, letter_spacing=1.5),
        text(48, 198, "Expense has status 'approved'", "sans f-ink", 13),
        text(48, 217, "Expense is approved by Approver", "sans f-ink", 13),
        text(48, 245, "FRAME", "sans f-muted", 11, weight=700, letter_spacing=1.5),
        text(48, 264, "alethic: nothing else may change", "sans f-ink", 13),
        object_type(400, 134, "Expense", "(.id)", w=120),
        connector(520, 160, 560, 80), connector(520, 160, 560, 240),
        roles(560, 80), uniqueness(560, 80, 0, 0), connector(632, 80, 660, 80),
        object_type(660, 54, "Status", value=True, w=120),
        roles(560, 240), uniqueness(560, 240, 0, 0), connector(632, 240, 660, 240),
        object_type(660, 214, "Approver", "(.name)", w=120),
        reading(596, 120, "… has status …"), reading(596, 280, "… is approved by …"),
        path("M330 151C400 151 470 96 556 84", "s-accent nofill", stroke_width=1.6, stroke_dasharray="5 4"),
        path("M330 205C420 205 480 236 556 238", "s-accent nofill", stroke_width=1.6, stroke_dasharray="5 4"),
    ]
    return document("gnd-orm-d6", 800, 320, "An operation over ORM fact types",
                    "The operation approve_expense requires a draft status, retracts the old status, asserts "
                    "'approved' and the approver, and declares an alethic frame.", body)


def _box(x: float, y: float, w: float, h: float, title: str, sub: str, mono_title: bool = False) -> Node:
    return g(rect(x, y, w, h, "f-card s-line", rx=10, stroke_width=1.5),
             text(x + 14, y + 19, title, ("mono" if mono_title else "sans") + " f-ink", 13.5, weight=650),
             text(x + 14, y + 35, sub, "sans f-muted", 11.5))


def d7_intermediate_representation() -> str:
    body = background(800, 360, "ONE MODEL IN THE MIDDLE")
    inputs = [("Requirements in text", "gnd-model-from-text"), ("Existing code", "gnd-model-from-code"),
              ("A GSD project", "gnd-adopt"), ("An existing ORM model", "gnd import rai-orm")]
    outputs = [("check · verify", "facts, plans, derived claims"), ("synth · measure", "test data, verifier rates"),
               ("codegen · conformance", "the Python project"), ("verbalize", "rules as sentences"),
               ("evolve · diff", "reviewed change"), ("export", "Soufflé · Lean · PyRel")]
    for index, (title, sub) in enumerate(inputs):
        y = 66 + index * 64
        body.append(_box(24, y, 210, 46, title, sub))
        body.append(path(f"M234 {y + 23}C267 {y + 23} 267 180 296 180", "s-primary nofill", stroke_width=1.6))
    for index, (title, sub) in enumerate(outputs):
        y = 48 + index * 50
        body.append(_box(566, y, 210, 42, title, sub, mono_title=True))
        body.append(path(f"M504 180C535 180 535 {y + 21} 562 {y + 21}", "s-primary nofill", stroke_width=1.6))
    body += [
        rect(300, 92, 200, 176, "f-primary", rx=16),
        text(400, 128, "model.orm.yaml", "mono f-bubble-ink", 15, weight=700, anchor="middle"),
        text(400, 150, "the executable ontology", "sans f-bubble-ink", 13, anchor="middle"),
        line(330, 166, 470, 166, "s-line", stroke_width=1, opacity=0.5),
        text(400, 190, "facts · constraints", "sans f-bubble-ink", 13, anchor="middle"),
        text(400, 210, "modality · provenance", "sans f-bubble-ink", 13, anchor="middle"),
        text(400, 230, "operations · derivations", "sans f-bubble-ink", 13, anchor="middle"),
        text(400, 252, "ORM 2", "sans f-bubble-ink", 11, anchor="middle", letter_spacing=2, opacity=0.8),
    ]
    return document("gnd-orm-d7", 800, 360, "ORM as the intermediate representation",
                    "Requirements text, existing code, a GSD project or an existing ORM model become one "
                    "model.orm.yaml. Checking, synthetic data, code generation, verbalization, evolution "
                    "and exports all read that model.", body)


FIGURES = {
    "orm-d1-fact-type.svg": d1_fact_type,
    "orm-d2-exclusion.svg": d2_exclusion,
    "orm-d3-uniqueness-mandatory.svg": d3_uniqueness_mandatory,
    "orm-d4-modality.svg": d4_modality,
    "orm-d5-derived.svg": d5_derived,
    "orm-d6-operation.svg": d6_operation,
    "orm-d7-intermediate-representation.svg": d7_intermediate_representation,
}
