"""MG3 review probes (scratch only). Run: uv run pytest -p no:cacheprovider -s <this>"""
import copy, json, sys, time
from pathlib import Path
REPO = Path("/Users/nikolaosvasiloglou/github-repos/gnd-public/.claude/worktrees/intelligent-pasteur-df4027")
sys.path.insert(0, str(REPO / "tests"))
import test_evolve_shape_matches as T  # noqa: E402
from support.cli_runner import run_main  # noqa: E402


def _try(label, fn):
    try:
        r = fn()
        print(f"[{label}] OK ->", str(r)[:120])
        return r
    except Exception as e:  # noqa: BLE001
        print(f"[{label}] RAISED {type(e).__name__}: {str(e)[:300]}")


def test_p1_role_name_collision(tmp_path):
    from gnd.model import load_model
    import tempfile
    doc = T._doc()
    doc["fact_types"].append({"id": "order_pairs_order", "reading": "{Order} follows {Order}",
                              "roles": [{"object_type": "order", "role_name": "x"},
                                        {"object_type": "order", "role_name": "x"}]})
    from ruamel.yaml import YAML
    import io
    buf = io.StringIO(); YAML().dump(doc, buf)
    d = Path(tempfile.mkdtemp()); p = d / "m.orm.yaml"; p.write_text(buf.getvalue())
    _try("P1 load_model dup role_name", lambda: load_model(p) and "accepted")
    ft = {"id": "order_pairs_order", "reading": "{Order} follows {Order}", "roles": [{"object_type": "order", "role_name": "x"}, {"object_type": "order", "role_name": "x"}]}
    r = _try("P1 preview add dup role_name", lambda: T._preview(tmp_path, (T._op("add", "fact_types", ft["id"], after=ft),), shape_report=True))
    if r: print("P1 entries", T._entries(r))
    _try("P1 service preview", lambda: None)


def test_p2_add_then_modify(tmp_path):
    ft = T._fact_type("order_has_note", "{Order} has {Note}", ("order", "order"), ("note", "note"))
    after = T._fact_type("order_has_note", "{Order} has {Amount}", ("order", "order"), ("amount", "amount"))
    ops = (T._op("add", "fact_types", ft["id"], after=ft, operation_id="a"),
           T._op("modify", "fact_types", ft["id"], before=ft, after=after, operation_id="b"))
    p = _try("P2 add+modify", lambda: T._preview(tmp_path, ops, shape_report=True))
    if p: print("entries", json.dumps(T._entries(p)))


def test_p3_add_then_rename(tmp_path):
    from gnd.evolve import EvolutionOperation, EvolutionOperationKind, ElementLocator
    a = T._fact_type("order_has_note", "{Order} has {Note}", ("order", "order"), ("note", "note"))
    b = T._fact_type("order_has_note2", "{Order} has2 {Note}", ("order", "order"), ("note", "note"))
    ops = (T._op("add", "fact_types", a["id"], after=a, operation_id="a"),
           T._op("add", "fact_types", b["id"], after=b, operation_id="b"),
           T._op("delete", "fact_types", a["id"], before=a, operation_id="c"),
           T._op("delete", "fact_types", b["id"], before=b, operation_id="d"))
    p = _try("P3 add+delete x2", lambda: T._preview(tmp_path / "d", ops, shape_report=True))
    if p: print("entries", json.dumps(T._entries(p)))


def test_p4_delete_then_readd_same_id(tmp_path):
    memo = T._fact(T._doc(), "order_has_memo")
    readd = copy.deepcopy(memo); readd["reading"] = "{Order} carries {Memo}"
    d1, d2 = T._delete_memo()
    ops = (d1, d2, T._op("add", "fact_types", "order_has_memo", after=readd, operation_id="z"))
    p = _try("P4 delete+readd same id", lambda: T._preview(tmp_path, ops, shape_report=True))
    if p: print("entries", json.dumps(T._entries(p)))


def test_p5_modify_existing_collides(tmp_path):
    # modify order_has_memo to play (order, note); add order_has_note (order, note).
    memo = T._fact(T._doc(), "order_has_memo")
    after = copy.deepcopy(memo)
    after["reading"] = "{Order} has {Note}"
    after["roles"] = [{"object_type": "order", "role_name": "order"}, {"object_type": "note", "role_name": "note"}]
    ops = (T._op("modify", "fact_types", "order_has_memo", before=memo, after=after, operation_id="a"),
           T._op("add", "fact_types", T.LONELY["id"], after=T.LONELY, operation_id="b"))
    p = _try("P5 modify existing into collision", lambda: T._preview(tmp_path, ops, shape_report=True))
    if p: print("P5 entries", json.dumps(T._entries(p)))
    # and the converse: add (order, memo) while modifying memo away -> reports a match the candidate lacks
    ft = T._fact_type("order_keeps_memo", "{Order} keeps {Memo}", ("order", "order"), ("memo", "memo"))
    ops2 = (T._op("modify", "fact_types", "order_has_memo", before=memo, after=after, operation_id="a"),
            T._op("add", "fact_types", ft["id"], after=ft, operation_id="b"))
    p2 = _try("P5b modify existing away", lambda: T._preview(tmp_path / "b", ops2, shape_report=True))
    if p2: print("P5b entries", json.dumps(T._entries(p2)))


def test_p6_retry_with_stripped_report(tmp_path):
    paths = T._cli_workspace(tmp_path, T.ADD_VISIT)
    assert run_main(T._preview_argv(paths, "--shape-report")).returncode == 0
    r = run_main(T._apply_argv(paths)); print("[P6] first apply", r.returncode)
    # re-run apply with the same (reported) preview: retry branch
    r2 = run_main(T._apply_argv(paths)); print("[P6] retry same preview", r2.returncode, r2.stderr[-300:])
    T._rewrite(paths, lambda d: d.pop("shape_matches"))
    r3 = run_main(T._apply_argv(paths)); print("[P6] retry stripped preview", r3.returncode, r3.stderr[-400:])


def test_p7_reader_accepts_inconsistent_report(tmp_path):
    from gnd.evolve import EvolutionPreview, canonical_sha256
    p = T._preview(tmp_path, T.ADD_VISIT, shape_report=True)
    def reread(mut, label):
        doc = p.model_dump(mode="json"); mut(doc["shape_matches"])
        doc["preview_sha256"] = canonical_sha256({k: v for k, v in doc.items() if k != "preview_sha256"})
        _try(label, lambda: EvolutionPreview.model_validate(doc) and "accepted")
    reread(lambda e: e[0].update(operation_index=99), "P7a op index beyond operations")
    reread(lambda e: e[0].update(fact_type="nonexistent"), "P7b fact_type not in candidate")
    reread(lambda e: e[0].update(signature=["zzz"]), "P7c signature inconsistent")
    reread(lambda e: e[0]["matches"].append(dict(e[0]["matches"][0], fact_type="phantom")), "P7d phantom match")
    reread(lambda e: e.append(dict(e[0], operation_index=1)), "P7e extra entry")
    reread(lambda e: e[0]["references"][0].update(identity="composite", value_type="customer_id"), "P7f composite with value_type")
    reread(lambda e: e[0]["references"][0].update(value_type=None), "P7g direct without value_type")
    reread(lambda e: e[0].update(signature=["a", "a"]), "P7h dup signature")
    reread(lambda e: e[0]["matches"][0].update(inverse_reading=""), "P7i empty inverse")


def test_p8_scale_with_entities():
    from gnd.documents import Model
    from gnd.evolve.shapes import shape_matches
    ots = []
    for i in range(100):
        ots.append({"id": f"v{i}", "name": f"V{i}", "kind": "value", "primitive": "String"})
        ots.append({"id": f"e{i}", "name": f"E{i}", "kind": "entity", "reference": {"mode": "popular", "value_type": f"v{i}"}})
    def fact(i, prefix):
        return {"id": f"{prefix}{i}", "reading": "{A} r {B}",
                "roles": [{"object_type": f"e{i % 100}", "role_name": "a"},
                          {"object_type": f"e{(i * 7) % 100}", "role_name": "b"}]}
    existing = [fact(i, "f") for i in range(5000)]
    added = [fact(i, "n") for i in range(500)]
    before = Model.model_validate({"version": 1, "model_id": "s", "object_types": ots, "fact_types": existing})
    cand = Model.model_validate({"version": 1, "model_id": "s", "object_types": ots, "fact_types": existing + added})
    prop = type("P", (), {"operations": tuple(T._op("add", "fact_types", f["id"], after=f, operation_id=f"o{n}") for n, f in enumerate(added))})()
    t = time.perf_counter(); e = shape_matches(before, cand, prop); dt = time.perf_counter() - t
    print(f"[P8] entity players: {len(e)} entries, {dt:.2f}s, matches[0]={len(e[0].matches)}")
    # composite / external refs w/ many constraints
    ots2 = list(ots) + [{"id": "c", "name": "C", "kind": "entity", "reference": {"mode": "external"}}]
    ex = existing + [{"id": "c_a", "reading": "{C} a {E0}", "roles": [{"object_type": "c", "role_name": "c"}, {"object_type": "e0", "role_name": "e"}]},
                     {"id": "c_b", "reading": "{C} b {E1}", "roles": [{"object_type": "c", "role_name": "c"}, {"object_type": "e1", "role_name": "e"}]}]
    cons = [{"type": "uniqueness", "scope": "external", "role_refs": [{"fact_type": "c_a", "role": "e"}, {"fact_type": "c_b", "role": "e"}]}]
    add2 = [{"id": f"m{i}", "reading": "{C} m {E0}", "roles": [{"object_type": "c", "role_name": "c"}, {"object_type": "e0", "role_name": "e"}]} for i in range(500)]
    b2 = Model.model_validate({"version": 1, "model_id": "s", "object_types": ots2, "fact_types": ex, "constraints": cons})
    c2 = Model.model_validate({"version": 1, "model_id": "s", "object_types": ots2, "fact_types": ex + add2, "constraints": cons})
    prop2 = type("P", (), {"operations": tuple(T._op("add", "fact_types", f["id"], after=f, operation_id=f"o{n}") for n, f in enumerate(add2))})()
    t = time.perf_counter(); e2 = shape_matches(b2, c2, prop2); dt = time.perf_counter() - t
    print(f"[P8b] composite players: {len(e2)} entries, {dt:.2f}s, refs={e2[0].references}, matches[0]={len(e2[0].matches)}")
    # output size: 500 adds all same shape, 5000 existing same shape -> 500*5499 matches
    same = [{"id": f"g{i}", "reading": "{A} r {B}", "roles": [{"object_type": "e0", "role_name": "a"}, {"object_type": "e1", "role_name": "b"}]} for i in range(5000)]
    sadd = [{"id": f"h{i}", "reading": "{A} r {B}", "roles": [{"object_type": "e0", "role_name": "a"}, {"object_type": "e1", "role_name": "b"}]} for i in range(500)]
    b3 = Model.model_validate({"version": 1, "model_id": "s", "object_types": ots, "fact_types": same})
    c3 = Model.model_validate({"version": 1, "model_id": "s", "object_types": ots, "fact_types": same + sadd})
    prop3 = type("P", (), {"operations": tuple(T._op("add", "fact_types", f["id"], after=f, operation_id=f"o{n}") for n, f in enumerate(sadd))})()
    t = time.perf_counter(); e3 = shape_matches(b3, c3, prop3); dt = time.perf_counter() - t
    print(f"[P8c] one-bucket worst case: {len(e3)} entries, {sum(len(x.matches) for x in e3)} matches, {dt:.2f}s")


def test_p3b_add_then_delete_with_other_change(tmp_path):
    a = T._fact_type("order_has_note", "{Order} has {Note}", ("order", "order"), ("note", "note"))
    b = T._fact_type("order_has_note2", "{Order} has2 {Note}", ("order", "order"), ("note", "note"))
    base_ops = (T._op("add", "fact_types", a["id"], after=a, operation_id="a"),
                T._op("add", "fact_types", b["id"], after=b, operation_id="b"),
                T._op("delete", "fact_types", a["id"], before=a, operation_id="c"),
                T._op("delete", "fact_types", b["id"], before=b, operation_id="d"))
    _try("P3 add+delete x2 no report", lambda: T._preview(tmp_path / "n", base_ops))
    ops = (*base_ops, T._op("add", "fact_types", T.VISIT["id"], after=T.VISIT, operation_id="e"))
    p = _try("P3b +visit no report", lambda: T._preview(tmp_path / "x", ops))
    p = _try("P3b +visit report", lambda: T._preview(tmp_path / "y", ops, shape_report=True))
    if p: print("P3b entries", json.dumps(T._entries(p)))
    from gnd.evolve.shapes import shape_matches
    from gnd.model import load_model
    # direct call (bypassing replay validation) for the branch candidate_signatures.get(..., ())
    before = load_model(T.BASE)
    prop = T._proposal(T.BASE.read_text(), (T._op("add", "fact_types", T.VISIT["id"], after=T.VISIT),))
    fake = type("P", (), {"operations": prop.operations + (T._op("add", "fact_types", "ghost1", after={}), T._op("add", "fact_types", "ghost2", after={}))})()
    cand = load_model(T.BASE)  # candidate lacking all added ids
    _try("P3c ghosts", lambda: [e.model_dump(mode="json") for e in shape_matches(before, cand, fake)])
