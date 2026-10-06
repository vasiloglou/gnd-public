from __future__ import annotations


def _cmd_conformance(model_path: str, project_dir: str, output_format: str) -> int:
    """``gnd conformance MODEL DIR`` — does the generated code still match?

    GEN-02's headline. The reusable conformance service invokes all four
    standalone assertions; this controller only renders its raw payload. That
    keeps command and programmatic callers on one partial-run and exit-band
    contract without making the service import this controller.

    **What a green result means, and what it does not.** Exit 0 says every
    DERIVED file still hashes to what the manifest recorded, the model has not
    moved since generation, and the emitted surface names every fact type the
    model declares, and declared architecture agrees with static observations.
    Extension bytes are not integrity-digest-gated, and architecture may inspect
    explicit declarations. It says nothing about a
    derived file co-edited together with its manifest entry, and nothing about
    what a tool's BODY computes — assertion #3 binds names and signatures. All
    of those bounds travel in the payload's ``limits`` block and the
    ``unexamined`` list rather than only in this docstring, because the payload
    is what a CI job reads.

    **A model that will not LOAD is band 3, never 13.** The structural assertion
    needs the parsed model, and a model that fails validation means the
    obligations could not be EVALUATED — reporting drift there would claim the
    code disagrees with a model that does not exist in a checkable form. This is
    RESEARCH §2.2's case C0 arriving as a band rather than as a traceback, and it
    is why plan 06's mutation #3 has to be a CONSISTENT rename: the naive
    one-line version lands here and reds for a reason that has nothing to do with
    the gate.

    Bands, and why each is the one it is: see
    :func:`gnd.conformance.service.run_conformance`.
    """
    from gnd.conformance.report import canonical, render_conformance
    from gnd.conformance.service import run_conformance

    result = run_conformance(model_path, project_dir)

    if output_format == "json":
        print(canonical(result.payload))
    else:
        print(render_conformance(result.payload))

    return result.exit_code

_cmd_conformance.__module__ = "gnd.cli"
