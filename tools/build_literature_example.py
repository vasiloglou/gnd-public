"""Build the LI1 literature regression corpus over src/gnd/examples/literature/.

    uv run python tools/build_literature_example.py src/gnd/examples/literature
    uv run python tools/build_literature_example.py src/gnd/examples/literature \
        --heldout-labels HELDOUT.json --heldout-out DIR

The texts below are synthetic paraphrases of public works, written for
regression testing (spec: .gnd-planning/milestones/literature-identity/notes/
phase-LI1-spec.md). Every identifier was checked against its public record on
2026-11-15. Every other byte is computed here: spans, occurrences, digests,
populations, sidecars, renderer manifests, the composition and the answer
key. Nothing is pasted.

The development labels live in this file and in answers/, never in the
corpus entry point. The held-out labels are not in this repository branch:
pass --heldout-labels to build the held-out answer key elsewhere and record
its digest; without it the committed digest is kept.

Deterministic: fixed texts, canonical key order, two-space JSON.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

from gnd.anchors import canonical_document_text, lexical_ranges, vocabulary_digest
from gnd.extract.identity import anchor_normalize
from gnd.model import load_model

MODEL_ID = "urn:gnd-example:literature-flat@1"
MODEL_FILE = "model.orm.yaml"
EXECUTING_MODEL = "claude-opus-5-5 (hand-authored fixture)"
ANCHORED = {
    "work_introduces_method": ("method",),
    "method_builds_on_method": ("method", "base_method"),
    "method_is_used_in_field": ("method",),
}
DERIVED = "work_builds_on_method"
NOTE = "A synthetic paraphrase written for regression testing; it is not the text of the work."

# --- The corpus: one document per work ----------------------------------------------
# Each passage is one line. A document's facts name the passages that support them.

DOCUMENTS = {
    "vampnets": {
        "work": {"identifier": "arXiv:1710.06012", "title": "VAMPnets: Deep learning of molecular kinetics", "year": 2017},
        "domain": "molecular-dynamics", "split": "dev",
        "passages": [
            "The authors introduce the VAMPnet, a neural network that learns molecular kinetics end to end.",
            "A VAMPnet maps molecular coordinates straight to a few Markov states, replacing a hand-built pipeline of features, reduction and clustering.",
            "The VAMPnet is used in molecular dynamics to summarize long simulations as interpretable kinetic models.",
        ],
        "facts": [
            ("work_introduces_method", {"work": "arXiv:1710.06012", "method": "VAMPnet"}, [1]),
            ("method_is_used_in_field", {"method": "VAMPnet", "field": "molecular dynamics"}, [3]),
        ],
    },
    "vampnet": {
        "work": {"identifier": "arXiv:2307.04686", "title": "VampNet: Music Generation via Masked Acoustic Token Modeling", "year": 2023},
        "domain": "music", "split": "dev",
        "passages": [
            "The paper introduces VampNet, a model that makes music by predicting acoustic tokens that have been masked out.",
            "VampNet is built on a bidirectional transformer, so every token is visible to the model in a single forward pass.",
            "Prompting VampNet with different masks lets it compress, inpaint, continue or loop a piece of music.",
            "VampNet is used in music generation as a tool for co-creating music with people.",
        ],
        "facts": [
            ("work_introduces_method", {"work": "arXiv:2307.04686", "method": "VampNet"}, [1]),
            ("method_builds_on_method", {"method": "VampNet", "base_method": "bidirectional transformer"}, [2]),
            ("method_is_used_in_field", {"method": "VampNet", "field": "music generation"}, [4]),
        ],
    },
    "wham-whale": {
        "work": {"identifier": "arXiv:2512.02206", "title": "WhAM: Towards A Translative Model of Sperm Whale Vocalization", "year": 2025},
        "domain": "bioacoustics", "split": "dev",
        "passages": [
            "The authors present WhAM, a model that produces synthetic sperm whale codas from an audio prompt.",
            "WhAM was made by fine-tuning VampNet, a masked acoustic token model first trained on music, on about ten thousand coda recordings.",
            "Marine biologists rated the synthetic codas, and the representations WhAM learns also help classify rhythm, social unit and vowel.",
            "WhAM is used in bioacoustics to study how sperm whales communicate.",
        ],
        "facts": [
            ("work_introduces_method", {"work": "arXiv:2512.02206", "method": "WhAM"}, [1]),
            ("method_builds_on_method", {"method": "WhAM", "base_method": "VampNet"}, [2]),
            ("method_is_used_in_field", {"method": "WhAM", "field": "bioacoustics"}, [4]),
        ],
    },
    "wham-pose": {
        "work": {"identifier": "arXiv:2312.07531", "title": "WHAM: Reconstructing World-grounded Humans with Accurate 3D Motion", "year": 2023},
        "domain": "computer-vision", "split": "dev",
        "passages": [
            "The paper introduces WHAM, which recovers 3D human motion from video in a world coordinate frame rather than the camera's.",
            "WHAM takes the camera's angular velocity from a SLAM system and combines it with the person's motion to recover where the body travels.",
            "A refinement step that is aware of foot contact lets WHAM follow people who climb stairs.",
            "WHAM is used in computer vision to recover human motion from ordinary video.",
        ],
        "facts": [
            ("work_introduces_method", {"work": "arXiv:2312.07531", "method": "WHAM"}, [1]),
            ("method_builds_on_method", {"method": "WHAM", "base_method": "SLAM"}, [2]),
            ("method_is_used_in_field", {"method": "WHAM", "field": "computer vision"}, [4]),
        ],
    },
    "opencap-monocular": {
        "work": {"identifier": "arXiv:2603.24733", "title": "OpenCap Monocular: 3D Human Kinematics and Musculoskeletal Dynamics from a Single Smartphone Video", "year": 2026},
        "domain": "biomechanics", "split": "dev",
        "passages": [
            "The authors introduce OpenCap Monocular, which estimates skeletal kinematics and kinetics from one smartphone video.",
            "OpenCap Monocular starts from the 3D pose estimates of the monocular model WHAM and refines them by optimization.",
            "During walking its ground reaction forces were about as accurate as those of the earlier two-camera OpenCap system.",
            "Against a computer-vision baseline that only regresses poses, it was far more accurate in both rotation and translation.",
            "OpenCap Monocular is used in biomechanics for assessing movement in clinics.",
        ],
        "facts": [
            ("work_introduces_method", {"work": "arXiv:2603.24733", "method": "OpenCap Monocular"}, [1]),
            ("method_builds_on_method", {"method": "OpenCap Monocular", "base_method": "WHAM"}, [2]),
            ("method_is_used_in_field", {"method": "OpenCap Monocular", "field": "biomechanics"}, [5]),
        ],
    },
    "apinn": {
        "work": {"identifier": "arXiv:2211.08939", "title": "Augmented Physics-Informed Neural Networks (APINNs): A gating network-based soft domain decomposition methodology", "year": 2022},
        "domain": "scientific-ml", "split": "dev",
        "spelling_note": "This paraphrase writes the method's name as $PINN, the LaTeX-residue spelling a host extractor produced; the work itself writes APINN.",
        "passages": [
            "The paper proposes $PINN, an augmented physics-informed network whose domain decomposition is soft and trainable.",
            "$PINN improves on XPINN by replacing its hard split into subdomains with a gate network that can be fine-tuned.",
            "XPINN itself extends PINNs by splitting the domain into subdomains that are joined by interface conditions.",
            "$PINN is used in scientific machine learning for solving partial differential equations.",
        ],
        "facts": [
            ("work_introduces_method", {"work": "arXiv:2211.08939", "method": "$PINN"}, [1]),
            ("method_builds_on_method", {"method": "$PINN", "base_method": "XPINN"}, [2]),
            ("method_builds_on_method", {"method": "XPINN", "base_method": "PINNs"}, [3]),
            ("method_is_used_in_field", {"method": "$PINN", "field": "scientific machine learning"}, [4]),
        ],
    },
    "pinn-failure-modes": {
        "work": {"identifier": "arXiv:2109.01050", "title": "Characterizing possible failure modes in physics-informed neural networks", "year": 2021},
        "domain": "scientific-ml", "split": "dev",
        "passages": [
            "The study shows that physics-informed neural networks, or PINNs, can fail on only slightly harder problems such as convection.",
            "It traces the failures to the soft PDE regularization, which makes the loss landscape hard to optimize, not to a lack of expressivity.",
            "The authors introduce curriculum regularization, which starts PINNs on a simple PDE term and makes the term harder as training goes on.",
            "The remedy cut the error by one to two orders of magnitude compared with the regular training baseline.",
            "Curriculum regularization is used in scientific machine learning for training PINNs on hard equations.",
        ],
        "facts": [
            ("work_introduces_method", {"work": "arXiv:2109.01050", "method": "curriculum regularization"}, [3]),
            ("method_builds_on_method", {"method": "curriculum regularization", "base_method": "PINNs"}, [3]),
            ("method_is_used_in_field", {"method": "curriculum regularization", "field": "scientific machine learning"}, [5]),
        ],
    },
    "boltz-1": {
        "work": {"identifier": "doi:10.1101/2024.11.19.624167", "title": "Boltz-1: Democratizing Biomolecular Interaction Modeling", "year": 2024},
        "domain": "structural-biology", "split": "dev",
        "passages": [
            "The authors introduce Boltz-1, an open-source model that predicts the 3D structures of biomolecular complexes.",
            "Boltz-1 reaches accuracy at the level of AlphaFold3 and matches commercial models on a range of benchmark sets.",
            "The paper also introduces Boltz-steering, a steering method applied to Boltz-1 at inference time that repairs hallucinated or non-physical predictions.",
            "Boltz-1 is used in structural biology for modelling how biomolecules interact.",
        ],
        "facts": [
            ("work_introduces_method", {"work": "doi:10.1101/2024.11.19.624167", "method": "Boltz-1"}, [1]),
            ("work_introduces_method", {"work": "doi:10.1101/2024.11.19.624167", "method": "Boltz-steering"}, [3]),
            ("method_builds_on_method", {"method": "Boltz-steering", "base_method": "Boltz-1"}, [3]),
            ("method_is_used_in_field", {"method": "Boltz-1", "field": "structural biology"}, [4]),
        ],
    },
    "posex": {
        "work": {"identifier": "arXiv:2505.01700", "title": "PoseX: AI Defeats Physics Approaches on Protein-Ligand Cross Docking", "year": 2025},
        "domain": "structural-biology", "split": "dev",
        "passages": [
            "The authors build PoseX, an open benchmark of protein-ligand docking in both the self-docking and the cross-docking setting.",
            "PoseX evaluates 23 docking methods, among them physics-based tools, AI docking and AI co-folding models such as AlphaFold3 and the Boltz-1 family.",
            "Among the co-folding models only Boltz-1x avoided ligand chirality errors, which the authors credit to its physics-inspired potentials.",
            "PoseX is used in drug discovery for comparing docking methods.",
        ],
        "facts": [
            ("work_introduces_method", {"work": "arXiv:2505.01700", "method": "PoseX"}, [1]),
            ("method_is_used_in_field", {"method": "PoseX", "field": "drug discovery"}, [4]),
        ],
    },
    "flows-review": {
        "work": {"identifier": "arXiv:1912.02762", "title": "Normalizing Flows for Probabilistic Modeling and Inference", "year": 2019},
        "domain": "probabilistic-ml", "split": "dev",
        "passages": [
            "The review explains how a normalizing flow turns a simple base distribution into an expressive one through a series of invertible maps.",
            "It sets out principles for designing flows and weighs their expressive power against their computational cost.",
            "The normalizing flow is used in probabilistic modeling for generative modelling and approximate inference.",
        ],
        "facts": [
            ("method_is_used_in_field", {"method": "normalizing flow", "field": "probabilistic modeling"}, [3]),
        ],
    },
    "sbi-frontier": {
        "work": {"identifier": "arXiv:1911.01429", "title": "The frontier of simulation-based inference", "year": 2019},
        "domain": "statistics", "split": "dev",
        "passages": [
            "The review surveys simulation-based inference, which fits the parameters of scientific simulators whose likelihood cannot be computed.",
            "It credits much of the field's new momentum to machine learning, and describes neural density estimators such as normalizing flows among its tools.",
            "Simulation-based inference is used in scientific simulation for inverse problems posed by detailed simulators.",
        ],
        "facts": [
            ("method_is_used_in_field", {"method": "simulation-based inference", "field": "scientific simulation"}, [3]),
        ],
    },
    "sensor-placement": {
        "work": {"identifier": "arXiv:2410.12036", "title": "Deep Optimal Sensor Placement for Black Box Stochastic Simulations", "year": 2024},
        "domain": "statistics", "split": "dev",
        "passages": [
            "The paper proposes deep optimal sensor placement, which models the joint distribution of parameters and solutions with an energy-based model trained on simulations.",
            "Unlike existing simulation-based inference approaches, which are tied to fixed point evaluations, it learns a functional representation that can be conditioned on any set of points.",
            "Deep optimal sensor placement is used in experimental design for choosing informative sensor locations at lower cost.",
        ],
        "facts": [
            ("work_introduces_method", {"work": "arXiv:2410.12036", "method": "deep optimal sensor placement"}, [1]),
            ("method_is_used_in_field", {"method": "deep optimal sensor placement", "field": "experimental design"}, [3]),
        ],
    },
    # --- held out: inputs only; their labels are not in this branch -------------------
    "roberta": {
        "work": {"identifier": "arXiv:1907.11692", "title": "RoBERTa: A Robustly Optimized BERT Pretraining Approach", "year": 2019},
        "domain": "nlp", "split": "heldout",
        "passages": [
            "The study introduces RoBERTa, a replication of BERT pretraining that measures how much hyperparameters and training data matter.",
            "RoBERTa keeps the BERT recipe but trains longer on more data, and finds that BERT had been undertrained.",
            "BERT itself is built on the Transformer encoder.",
            "Unlike XLNet, which changes the pretraining objective, RoBERTa keeps masked language modelling and changes only how it is trained.",
            "RoBERTa is used in natural language processing as a pretrained encoder.",
        ],
        "facts": [],
    },
    "xlnet": {
        "work": {"identifier": "arXiv:1906.08237", "title": "XLNet: Generalized Autoregressive Pretraining for Language Understanding", "year": 2019},
        "domain": "nlp", "split": "heldout",
        "passages": [
            "The paper proposes XLNet, which pretrains a language model autoregressively over every permutation of the factorization order.",
            "XLNet carries ideas from Transformer-XL, an autoregressive model, into pretraining.",
            "It argues that masking in BERT ignores how masked positions depend on one another.",
            "XLNet is used in natural language processing for tasks such as question answering.",
        ],
        "facts": [],
    },
    "segment-anything": {
        "work": {"identifier": "arXiv:2304.02643", "title": "Segment Anything", "year": 2023},
        "domain": "computer-vision", "split": "heldout",
        "passages": [
            "The project introduces SAM, the Segment Anything Model, which segments images in response to prompts.",
            "The image encoder of SAM is a Vision Transformer pretrained as a masked autoencoder.",
            "SAM was trained in a data loop that also produced a dataset of more than a billion masks.",
            "SAM is used in computer vision for zero-shot segmentation.",
        ],
        "facts": [],
    },
    "asam": {
        "work": {"identifier": "arXiv:2102.11600", "title": "ASAM: Adaptive Sharpness-Aware Minimization for Scale-Invariant Learning of Deep Neural Networks", "year": 2021},
        "domain": "optimization", "split": "heldout",
        "passages": [
            "The paper proposes ASAM, adaptive sharpness-aware minimization, built on a generalization bound for adaptive sharpness.",
            "ASAM makes sharpness-aware minimization, known as SAM, invariant to rescaling the parameters.",
            "ASAM is used in deep learning optimization to improve generalization.",
        ],
        "facts": [],
    },
}

# --- Development labels (the answer key's authored half) ---------------------------
# A passage reference is (document id, passage number counted from 1).

ASSERTIONS = [
    # id, passage, participants, predicate in plain words, support label, flat-model fact
    ("a01", ("vampnet", 2), ["VampNet", "bidirectional transformer"], "is built on", "supported",
     {"method": "VampNet", "base_method": "bidirectional transformer"}),
    ("a02", ("wham-whale", 2), ["WhAM", "VampNet"], "is made by fine-tuning", "supported",
     {"method": "WhAM", "base_method": "VampNet"}),
    ("a03", ("wham-pose", 2), ["WHAM", "SLAM"], "uses the output of", "supported",
     {"method": "WHAM", "base_method": "SLAM"}),
    ("a04", ("opencap-monocular", 2), ["OpenCap Monocular", "WHAM"], "refines the estimates of", "supported",
     {"method": "OpenCap Monocular", "base_method": "WHAM"}),
    ("a05", ("apinn", 3), ["XPINN", "PINNs"], "extends", "supported",
     {"method": "XPINN", "base_method": "PINNs"}),
    ("a06", ("apinn", 2), ["$PINN", "XPINN"], "improves on", "supported",
     {"method": "$PINN", "base_method": "XPINN"}),
    ("a07", ("pinn-failure-modes", 3), ["curriculum regularization", "PINNs"], "changes how it trains", "supported",
     {"method": "curriculum regularization", "base_method": "PINNs"}),
    ("a08", ("boltz-1", 3), ["Boltz-steering", "Boltz-1"], "is applied at inference time to", "supported",
     {"method": "Boltz-steering", "base_method": "Boltz-1"}),
    ("a09", ("posex", 2), ["PoseX", "Boltz-1"], "evaluates", "stretched",
     {"method": "PoseX", "base_method": "Boltz-1"}),
    ("a10", ("sbi-frontier", 2), ["simulation-based inference", "normalizing flows"], "lists among its tools", "stretched",
     {"method": "simulation-based inference", "base_method": "normalizing flows"}),
    ("a11", ("sensor-placement", 2), ["deep optimal sensor placement", "simulation-based inference"], "is contrasted with", "contradicted",
     {"method": "deep optimal sensor placement", "base_method": "simulation-based inference"}),
    ("a12", ("opencap-monocular", 3), ["OpenCap Monocular", "OpenCap"], "is compared in accuracy with", "insufficient-evidence",
     {"method": "OpenCap Monocular", "base_method": "OpenCap"}),
]

IDENTITY_PAIRS = [
    ("i01", ("vampnets", "VAMPnet"), ("wham-whale", "VampNet"), "different", [("vampnets", 1), ("wham-whale", 2)]),
    ("i02", ("wham-whale", "WhAM"), ("opencap-monocular", "WHAM"), "different", [("wham-whale", 1), ("opencap-monocular", 2)]),
    ("i03", ("apinn", "$PINN"), ("pinn-failure-modes", "PINNs"), "different", [("apinn", 1), ("pinn-failure-modes", 1)]),
    ("i04", ("vampnet", "VampNet"), ("wham-whale", "VampNet"), "same", [("vampnet", 1), ("wham-whale", 2)]),
    ("i05", ("wham-pose", "WHAM"), ("opencap-monocular", "WHAM"), "same", [("wham-pose", 1), ("opencap-monocular", 2)]),
    ("i06", ("apinn", "PINNs"), ("pinn-failure-modes", "PINNs"), "same", [("apinn", 3), ("pinn-failure-modes", 1)]),
]

CHAINS = [
    # id, label, story, domains, edges (assertion ids), merges (identity pair ids), path, reason
    ("c01", "supported", "transformer-to-whale", "cross", ["a01", "a02"], [],
     ["bidirectional transformer", "VampNet", "WhAM"],
     "Music model to whale bioacoustics: each link is stated in its own paper, and the names are the same method."),
    ("c02", "supported", "pinn-lineage", "same", ["a05", "a06"], [],
     ["PINNs", "XPINN", "$PINN"],
     "Each step is a stated extension within one method family."),
    ("c03", "supported", "slam-to-biomechanics", "cross", ["a03", "a04"], [],
     ["SLAM", "WHAM", "OpenCap Monocular"],
     "Computer vision to biomechanics: WHAM uses SLAM output, and OpenCap Monocular refines WHAM."),
    ("c04", "false", "whale", "cross", ["a02", "a04"], ["i01", "i02"],
     ["VAMPnet", "WhAM", "OpenCap Monocular"],
     "True sentences joined by two false merges: VAMPnet (molecular kinetics) is not VampNet (music), and WhAM (whales) is not WHAM (human pose)."),
    ("c05", "false", "dollar-pinn-chain", "same", ["a06", "a07"], ["i03"],
     ["XPINN", "PINNs", "curriculum regularization"],
     "Filing $PINN as PINNs makes curriculum regularization a descendant of XPINN; no passage says so."),
    ("c06", "false", "dollar-pinn-loop", "same", ["a05", "a06"], ["i03"],
     ["PINNs", "XPINN", "PINNs"],
     "Filing $PINN as PINNs closes a loop: PINNs would build on XPINN, which builds on PINNs."),
    ("c07", "false", "boltz-1-as-ancestry", "same", ["a09"], [],
     ["Boltz-1", "PoseX"],
     "PoseX evaluates the Boltz-1 family; evaluation is not ancestry."),
    ("c08", "false", "contrast-as-builds-on", "same", ["a10", "a11"], [],
     ["normalizing flows", "simulation-based inference", "deep optimal sensor placement"],
     "The sensor-placement paper contrasts itself with simulation-based inference, and the review only lists flows among the field's tools."),
]

REUSE_CASES = [
    ("u01", "VampNet", "real", [("vampnet", 1), ("wham-whale", 2)]),
    ("u02", "WHAM", "real", [("wham-pose", 1), ("opencap-monocular", 2)]),
    ("u03", "PINNs", "real", [("apinn", 3), ("pinn-failure-modes", 1)]),
    ("u04", "simulation-based inference", "real", [("sbi-frontier", 1), ("sensor-placement", 2)]),
    ("u05", "benchmark", "generic-word", [("boltz-1", 2), ("posex", 1)]),
    ("u06", "baseline", "generic-word", [("opencap-monocular", 4), ("pinn-failure-modes", 4)]),
    ("u07", "vampnet", "homonym", [("vampnets", 1), ("vampnet", 1)]),
    ("u08", "wham", "homonym", [("wham-whale", 1), ("wham-pose", 1)]),
]

NAME_PAIRS = [
    ("n01", "VAMPnet", "VampNet", "homonym", [("vampnets", 1), ("vampnet", 1)]),
    ("n02", "WhAM", "WHAM", "homonym", [("wham-whale", 1), ("wham-pose", 1)]),
    ("n03", "normalizing flow", "normalizing flows", "synonym", [("flows-review", 1), ("sbi-frontier", 2)]),
    ("n04", "$PINN", "PINNs", "family", [("apinn", 1), ("pinn-failure-modes", 1)]),
]

# Near-miss entities named in each document, for the renderer manifest's distractors.
NEAR_MISS = {
    "vampnets": "Markov states", "vampnet": "acoustic tokens", "wham-whale": "sperm whale codas",
    "wham-pose": "foot contact", "opencap-monocular": "two-camera OpenCap system", "apinn": "gate network",
    "pinn-failure-modes": "convection", "boltz-1": "AlphaFold3", "posex": "Boltz-1x",
    "flows-review": "base distribution", "sbi-frontier": "neural density estimators", "sensor-placement": "energy-based model",
}
# Facts a document does not support, for documents with no labelled unsupported assertion.
ABSENT = {
    "vampnets": ("method_is_used_in_field", {"method": "VAMPnet", "field": "music generation"}, "molecular dynamics"),
    "vampnet": ("method_builds_on_method", {"method": "VampNet", "base_method": "WhAM"}, "VampNet"),
    "wham-whale": ("method_is_used_in_field", {"method": "WhAM", "field": "music generation"}, "bioacoustics"),
    "wham-pose": ("method_builds_on_method", {"method": "WHAM", "base_method": "OpenCap Monocular"}, "WHAM"),
    "apinn": ("method_builds_on_method", {"method": "PINNs", "base_method": "XPINN"}, "XPINN"),
    "pinn-failure-modes": ("method_builds_on_method", {"method": "PINNs", "base_method": "curriculum regularization"}, "curriculum regularization"),
    "boltz-1": ("method_builds_on_method", {"method": "Boltz-1", "base_method": "AlphaFold3"}, "AlphaFold3"),
    "flows-review": ("method_is_used_in_field", {"method": "normalizing flow", "field": "computer vision"}, "normalizing flow"),
}


# --- Byte helpers --------------------------------------------------------------------

def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _dump(value) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")


def document_text(doc_id: str, doc: dict) -> str:
    work = doc["work"]
    lines = [f"# {work['title']} ({work['year']})",
             f"Work {work['identifier']}. {NOTE}" + (f" {doc['spelling_note']}" if doc.get("spelling_note") else "")]
    lines.extend(doc["passages"])
    return "\n".join(lines) + "\n"


def passage_spans(text: str) -> list[tuple[int, int]]:
    """Spans of every line after the two header lines, in order."""
    spans, start = [], 0
    for number, line in enumerate(text.split("\n")[:-1]):
        if number >= 2:
            spans.append((start, start + len(line)))
        start += len(line) + 1
    return spans


def passage_id(doc_id: str, number: int) -> str:
    return f"{doc_id}.p{number}"


def _occurrence(text: str, value: str, span: tuple[int, int]) -> int:
    key = anchor_normalize(value)
    ranges = lexical_ranges(text, {key})[key]
    for index, (start, end) in enumerate(ranges):
        if span[0] <= start and end <= span[1]:
            return index
    raise ValueError(f"{value!r} does not occur in span {span}")


def with_derived(facts: dict) -> dict:
    """The asserted facts plus the derived rows they imply, in canonical key order.

    The one home of the local derivation rule: a work builds on every base method
    of a method it introduces. Any claimed derived rows passed in are replaced.
    """
    facts = {fact_type: rows for fact_type, rows in facts.items() if fact_type != DERIVED}
    derived = sorted(
        ({"work": i["work"], "method": b["base_method"]}
         for i in facts.get("work_introduces_method", [])
         for b in facts.get("method_builds_on_method", []) if b["method"] == i["method"]),
        key=lambda row: (row["work"], row["method"]))
    if derived:
        facts[DERIVED] = derived
    return {fact_type: facts[fact_type] for fact_type in sorted(facts)}


def source_facts(doc: dict) -> dict:
    facts: dict[str, list] = {}
    for fact_type, roles, _ in doc["facts"]:
        facts.setdefault(fact_type, []).append(dict(roles))
    return with_derived(facts)


def population_bytes(facts: dict, *, source: str = "agent-output") -> bytes:
    return _dump({"population": {"model": MODEL_FILE, "model_id": MODEL_ID, "source": source,
                                 "covers": sorted(facts)},
                  "instances": {}, "facts": facts})


def anchors_for(text: str, doc: dict) -> list[dict]:
    spans = passage_spans(text)
    anchors = []
    for fact_type, roles, numbers in doc["facts"]:
        for role in ANCHORED.get(fact_type, ()):
            for number in numbers:
                start, end = spans[number - 1]
                anchors.append({"fact_key": {"fact_type": fact_type, "roles": dict(roles)}, "role": role,
                                "span": {"start": start, "end": end},
                                "occurrence": _occurrence(text, roles[role], (start, end)),
                                "excerpt_sha256": _sha(text[start:end].encode("utf-8"))})
    return anchors


# --- Writers -------------------------------------------------------------------------

def _gnd(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-m", "gnd", *args], capture_output=True, text=True, check=False, cwd=cwd)


def write_corpus(root: Path) -> dict:
    corpus_dir = root / "corpus"
    if corpus_dir.exists():
        shutil.rmtree(corpus_dir)
    (corpus_dir / "documents").mkdir(parents=True)
    artifacts = corpus_dir / "artifacts"
    # Run from the example root so the bundle index records the model as "model.orm.yaml".
    made = _gnd("extract", MODEL_FILE, "--out", "corpus/artifacts", cwd=root)
    if made.returncode != 0:
        raise SystemExit(made.stdout + made.stderr)
    documents, passages = [], []
    for doc_id, doc in DOCUMENTS.items():
        raw = document_text(doc_id, doc).encode("utf-8")
        (corpus_dir / "documents" / f"{doc_id}.md").write_bytes(raw)
        documents.append({"id": doc_id, "path": f"corpus/documents/{doc_id}.md", "sha256": _sha(raw),
                          "domain": doc["domain"], "split": doc["split"], "paraphrase": True,
                          "work": dict(doc["work"])})
        text = canonical_document_text(raw)
        for number, (start, end) in enumerate(passage_spans(text), 1):
            passages.append({"id": passage_id(doc_id, number), "document": doc_id,
                             "span": {"start": start, "end": end}})
    corpus = {"schema": "literature-corpus/1", "model": MODEL_FILE,
              "model_sha256": _sha((root / MODEL_FILE).read_bytes()),
              "artifacts": {"path": "corpus/artifacts",
                            "applicable_sha256": _sha((artifacts / "model.applicable.json").read_bytes()),
                            "projection_sha256": _sha((artifacts / "model.projection.schema.json").read_bytes())},
              "documents": documents, "passages": passages}
    (corpus_dir / "corpus.json").write_bytes(_dump(corpus))
    return corpus


def _ref(doc_id: str, number: int) -> str:
    return passage_id(doc_id, number)


def write_gold(root: Path, corpus: dict, split: str, out: Path) -> dict:
    """Gold source populations and renderer manifests for one split."""
    gold, render = out / "gold", out / "render"
    for folder in (gold, render):
        if folder.exists():
            shutil.rmtree(folder)
        folder.mkdir(parents=True)
    by_id = {d["id"]: d for d in corpus["documents"]}
    unsupported = {}
    for assertion in ASSERTIONS:
        if assertion[4] != "supported":
            unsupported.setdefault(assertion[1][0], []).append(assertion)
    digests = {}
    for doc_id, doc in DOCUMENTS.items():
        if doc["split"] != split:
            continue
        population = population_bytes(source_facts(doc), source="synthetic")
        (gold / f"{doc_id}.population.json").write_bytes(population)
        text = canonical_document_text((root / by_id[doc_id]["path"]).read_bytes())
        spans = passage_spans(text)
        absent = []
        for _, (_, number), _, _, _, fact in unsupported.get(doc_id, []):
            start, end = spans[number - 1]
            absent.append({"kind": "absent-fact", "text": text[start:end], "fact_type": "method_builds_on_method",
                           "roles": dict(fact)})
        if not absent and doc_id in ABSENT:
            fact_type, roles, mention = ABSENT[doc_id]
            absent.append({"kind": "absent-fact", "text": mention, "fact_type": fact_type, "roles": dict(roles)})
        manifest = {"schema_version": 1, "document": "document.md", "document_sha256": by_id[doc_id]["sha256"],
                    "model": MODEL_FILE, "model_sha256": corpus["model_sha256"],
                    "source_population": "source.population.json", "source_population_sha256": _sha(population),
                    "applicable_sha256": corpus["artifacts"]["applicable_sha256"],
                    "renderer_skill": "gnd-render-doc", "renderer_skill_version": "0.1.0",
                    "executing_model": EXECUTING_MODEL,
                    "distractors": [{"kind": "out-of-model", "text": "regression testing"},
                                    {"kind": "near-miss-entity", "text": NEAR_MISS[doc_id]}, *absent]}
        (render / f"{doc_id}.manifest.json").write_bytes(_dump(manifest))
        digests[doc_id] = _sha(population)
    return digests


def answer_key(corpus_raw: bytes, heldout_sha256: str, root: Path) -> dict:
    corpus = json.loads(corpus_raw)
    by_id = {d["id"]: d for d in corpus["documents"]}
    anchored, populations = [], []
    for doc_id, doc in DOCUMENTS.items():
        if doc["split"] != "dev":
            continue
        text = canonical_document_text((root / by_id[doc_id]["path"]).read_bytes())
        spans = passage_spans(text)
        for fact_type, roles, numbers in doc["facts"]:
            for role in ANCHORED.get(fact_type, ()):
                for number in numbers:
                    start, end = spans[number - 1]
                    anchored.append({"id": f"f{len(anchored) + 1:02d}", "source": doc_id,
                                     "fact": {"fact_type": fact_type, "roles": dict(roles)}, "role": role,
                                     "passage": _ref(doc_id, number), "span": {"start": start, "end": end}})
        # Plain gnd check (route R1) has no anchor sidecar, so every anchored rule
        # is unchecked and the measured exit is 4 for every source (LI1 finding).
        populations.append({"source": doc_id, "expected_check_exit": 4})
    return {
        "schema": "literature-answer-key/1",
        "corpus_sha256": _sha(corpus_raw),
        "labeller": {"kind": "single-author", "independent": False,
                     "note": ("Labels were written by the corpus author from the public works; "
                              "they are not independent expert ground truth.")},
        "assertions": [{"id": aid, "passage": _ref(*ref), "participants": parts, "predicate": predicate,
                        "support": support, "fact": {"fact_type": "method_builds_on_method", "roles": fact},
                        "label_disagreement": None}
                       for aid, ref, parts, predicate, support, fact in ASSERTIONS],
        "anchored_facts": anchored,
        "populations": populations,
        "chains": [{"id": cid, "label": label, "story": story, "domains": domains, "edges": edges,
                    "merges": merges, "path": path, "reason": reason,
                    "passages": sorted({_ref(*a[1]) for a in ASSERTIONS if a[0] in edges})}
                   for cid, label, story, domains, edges, merges, path, reason in CHAINS],
        "reuse_cases": [{"id": uid, "name": name, "kind": kind, "passages": [_ref(*r) for r in refs]}
                        for uid, name, kind, refs in REUSE_CASES],
        "identity_pairs": [{"id": iid, "left": {"source": left[0], "object_type": "method", "value": left[1]},
                            "right": {"source": right[0], "object_type": "method", "value": right[1]},
                            "label": label, "passages": [_ref(*r) for r in refs]}
                           for iid, left, right, label, refs in IDENTITY_PAIRS],
        "name_pairs": [{"id": nid, "left": left, "right": right, "kind": kind, "passages": [_ref(*r) for r in refs]}
                       for nid, left, right, kind, refs in NAME_PAIRS],
        "heldout": {"sha256": heldout_sha256, "chains": {"supported": 1, "false": 2}},
    }


def reference_sources(root: Path, corpus: dict) -> dict:
    """Per-source facts and anchors of the faithful run: exactly the gold facts, at the gold spans."""
    by_id = {d["id"]: d for d in corpus["documents"]}
    sources = {}
    for doc_id, doc in DOCUMENTS.items():
        if doc["split"] != "dev":
            continue
        text = canonical_document_text((root / by_id[doc_id]["path"]).read_bytes())
        sources[doc_id] = {"facts": source_facts(doc), "anchors": anchors_for(text, doc)}
    return sources


def write_run(root: Path, corpus: dict, corpus_raw: bytes, run: Path, sources: dict, *,
              abstentions: tuple = (), resolution: dict | None = None,
              renamings: list | None = None) -> subprocess.CompletedProcess:
    """Write a literature-run/1 directory, bind every sidecar to the bytes written, and compose.

    Returns the compose result. When compose refuses, the run has no composed/ directory.
    """
    if run.exists():
        shutil.rmtree(run)
    composition = run / "composition"
    vocabulary = vocabulary_digest(load_model(root / MODEL_FILE))
    by_id = {d["id"]: d for d in corpus["documents"]}
    for doc_id, source in sources.items():
        folder = composition / doc_id
        folder.mkdir(parents=True)
        document = (root / by_id[doc_id]["path"]).read_bytes()
        (folder / "document.txt").write_bytes(document)
        population = source.get("population_bytes") or population_bytes(source["facts"])
        (folder / "population.json").write_bytes(population)
        (folder / "population.json.anchors.json").write_bytes(_dump({
            "schema_version": 2, "population_sha256": _sha(population), "vocabulary_digest": vocabulary,
            "document_sha256": _sha(document), "anchors": source["anchors"]}))
        (folder / "population.json.extraction.json").write_bytes(_dump({
            "schema_version": 1, "population": "population.json", "population_sha256": _sha(population),
            "model": MODEL_FILE, "model_sha256": corpus["model_sha256"],
            "projection_sha256": corpus["artifacts"]["projection_sha256"],
            "document": "document.txt", "document_sha256": _sha(document),
            "skill": "gnd-extract", "skill_version": "0.1.0", "executing_model": EXECUTING_MODEL}))
    ids = list(sources)
    manifest = {"schema": "gnd-composition-manifest/1", "sources": ids, "renamings": list(renamings or []),
                "deduplications": "identical-rows",
                "scope_tags": [{"source": s, "tag": DOCUMENTS[s]["domain"]} for s in ids]}
    if resolution is not None:
        # LI2 (spec D8): the run's sense-resolution decisions, bound by digest.
        raw = _dump(resolution)
        (composition / "resolution.json").write_bytes(raw)
        manifest["resolution"] = {"path": "resolution.json", "sha256": _sha(raw)}
    (composition / "manifest.json").write_bytes(_dump(manifest))
    (run / "run.json").write_bytes(_dump({"schema": "literature-run/1", "corpus_sha256": _sha(corpus_raw),
                                          "sources": ids, "abstentions": list(abstentions)}))
    composed = run / "composed"
    composed.mkdir()
    made = _gnd("compose", str(root / MODEL_FILE), str(composition),
                "--out", str(composed / "population.json"), "--record", str(composed / "record.json"))
    if made.returncode != 0:
        shutil.rmtree(composed)
    return made


# --- LI2: the run's resolution decisions (spec phase-LI2 §6.7, D8) ----------------------

METHOD_ROLES = {"work_introduces_method": ("method",), "method_builds_on_method": ("method", "base_method"),
                "method_is_used_in_field": ("method",)}


def _evidence(source_id: str, source: dict, key: int, value: str) -> dict | None:
    """The first asserted coordinate whose method role holds value, with its anchor span.

    Derived fact types are claims, not mentions, so they never supply keys or evidence
    (LI2 corpus-step amendment B1).
    """
    for fact_type in sorted(source["facts"]):
        for fact_index, row in enumerate(source["facts"][fact_type]):
            for role in METHOD_ROLES.get(fact_type, ()):
                if row.get(role) != value:
                    continue
                spans = [a["span"] for a in source["anchors"]
                         if a["fact_key"]["fact_type"] == fact_type and a["fact_key"]["roles"] == row and a["role"] == role]
                if not spans:
                    return None
                return {"key": key, "source": source_id, "fact_type": fact_type, "fact_index": fact_index,
                        "role": role, "span": dict(spans[0])}
    return None


def resolution_for(sources: dict, pairs: list | None = None) -> dict:
    """Decisions for the identity pairs whose two keys still exist in the run's sources.

    pairs defaults to the answer key's labelled pairs, each decided as labelled. A pair
    whose key or evidence is gone (because a mutation removed its fact) is dropped.
    """
    decisions = []
    for _, left, right, label, _ in (pairs if pairs is not None else IDENTITY_PAIRS):
        if left[0] not in sources or right[0] not in sources:
            continue
        found = [_evidence(left[0], sources[left[0]], 0, left[1]), _evidence(right[0], sources[right[0]], 1, right[1])]
        if None in found:
            continue
        digests = {}
        for source_id in sorted({left[0], right[0]}):
            source = sources[source_id]
            digests[source_id] = _sha(source.get("population_bytes") or population_bytes(source["facts"]))
        decisions.append({"decision": label,
                          "keys": [{"source": left[0], "object_type": "method", "value": left[1]},
                                   {"source": right[0], "object_type": "method", "value": right[1]}],
                          "evidence": found, "producer": {"kind": "reviewer", "id": "corpus-author"},
                          "input_sha256": digests, "placeholders": None})
    return {"schema": "gnd-resolution/1", "object_types": ["method"], "decisions": decisions}


def write_reference_run(root: Path, corpus: dict, corpus_raw: bytes) -> None:
    made = write_run(root, corpus, corpus_raw, root / "runs" / "reference", reference_sources(root, corpus))
    if made.returncode != 0:
        raise SystemExit(made.stdout + made.stderr)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("root")
    parser.add_argument("--heldout-labels", help="held-out labels JSON (kept outside this branch)")
    parser.add_argument("--heldout-out", help="directory for the held-out answer key, gold and manifests")
    args = parser.parse_args(argv)
    root = Path(args.root)
    corpus = write_corpus(root)
    corpus_raw = (root / "corpus" / "corpus.json").read_bytes()
    answers = root / "answers"
    answers.mkdir(exist_ok=True)
    write_gold(root, corpus, "dev", answers)
    digest_file = answers / "heldout.sha256"
    if args.heldout_labels:
        if not args.heldout_out:
            parser.error("--heldout-labels needs --heldout-out")
        heldout = json.loads(Path(args.heldout_labels).read_text(encoding="utf-8"))
        heldout["corpus_sha256"] = _sha(corpus_raw)
        out = Path(args.heldout_out)
        out.mkdir(parents=True, exist_ok=True)
        heldout_raw = _dump(heldout)
        (out / "heldout-answer-key.json").write_bytes(heldout_raw)
        digest_file.write_text(_sha(heldout_raw) + "\n", encoding="ascii")
    heldout_sha256 = digest_file.read_text(encoding="ascii").strip()
    (answers / "answer-key.json").write_bytes(_dump(answer_key(corpus_raw, heldout_sha256, root)))
    write_reference_run(root, corpus, corpus_raw)
    # LI2 corpus gate: the decisions the reference run will carry once composition
    # understands a resolution (spec phase-LI2 D8). Data only until then.
    (root / "resolution").mkdir(exist_ok=True)
    (root / "resolution" / "li1-reference.resolution.json").write_bytes(
        _dump(resolution_for(reference_sources(root, corpus))))


if __name__ == "__main__":
    main()
