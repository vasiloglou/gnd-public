"""Compatibility strategy hooks for version-7/8 session execution."""
# isort: skip_file
import asyncio as asyncio  # noqa: PLC0414 -- compatibility binding
import json as json  # noqa: PLC0414 -- compatibility binding
import stat as stat  # noqa: PLC0414 -- compatibility binding
import tempfile as tempfile  # noqa: PLC0414 -- compatibility binding
import time as time  # noqa: PLC0414 -- compatibility binding
from pathlib import Path as Path  # noqa: PLC0414 -- compatibility binding
from gnd import input_policy as _rf7_input  # noqa: F401 -- compatibility binding
from gnd.admission_validation import constraint_annotations as constraint_annotations  # noqa: PLC0414 -- compatibility binding
from gnd.admission_validation import validate_reference_transport as validate_reference_transport  # noqa: PLC0414 -- compatibility binding
from gnd.agents import InvocationStatus as InvocationStatus  # noqa: PLC0414 -- compatibility binding
from gnd.artifacts import ArtifactError as ArtifactError  # noqa: PLC0414 -- compatibility binding
from gnd.artifacts import canonical_json_bytes as canonical_json_bytes  # noqa: PLC0414 -- compatibility binding
from gnd.artifacts import publish_directory_once as publish_directory_once  # noqa: PLC0414 -- compatibility binding
from gnd.artifacts import publish_leaf_atomic as publish_leaf_atomic  # noqa: PLC0414 -- compatibility binding
from gnd.artifacts import read_regular_bounded as read_regular_bounded  # noqa: PLC0414 -- compatibility binding
from gnd.artifacts import sha256_hex as _sha  # noqa: F401 -- compatibility binding
from gnd.exp.session_contract import ConstraintSatisfactionAcceptance as ConstraintSatisfactionAcceptance  # noqa: PLC0414 -- compatibility binding
from gnd.exp.session_contract import TestsAcceptance as TestsAcceptance  # noqa: PLC0414 -- compatibility binding
from gnd.exp.session_contract import TransitionAcceptance as TransitionAcceptance  # noqa: PLC0414 -- compatibility binding
from gnd.exp.session_contract import read_session_contract as read_session_contract  # noqa: PLC0414 -- compatibility binding
from gnd.exp.session_eval import AttemptEvaluation as AttemptEvaluation  # noqa: PLC0414 -- compatibility binding
from gnd.exp.session_eval import AttemptFeedback as AttemptFeedback  # noqa: PLC0414 -- compatibility binding
from gnd.exp.session_eval import _case_feedback as _case_feedback  # noqa: PLC0414 -- compatibility binding
from gnd.exp.session_eval import best_key as best_key  # noqa: PLC0414 -- compatibility binding
from gnd.exp.session_eval import case_decision as case_decision  # noqa: PLC0414 -- compatibility binding
from gnd.exp.session_eval import contract_accepts as contract_accepts  # noqa: PLC0414 -- compatibility binding
from gnd.exp.session_eval import normalized_verifier_signature as normalized_verifier_signature  # noqa: PLC0414 -- compatibility binding
from gnd.exp.session_eval import observe_expected_outputs as observe_expected_outputs  # noqa: PLC0414 -- compatibility binding
from gnd.exp.session_eval import ranking_observations as ranking_observations  # noqa: PLC0414 -- compatibility binding
from gnd.exp.session_eval import validate_tests_payload as validate_tests_payload  # noqa: PLC0414 -- compatibility binding
from gnd.exp.session_eval import validate_transition_payload as validate_transition_payload  # noqa: PLC0414 -- compatibility binding
from gnd.exp.session_eval import validate_verifier_payload as validate_verifier_payload  # noqa: PLC0414 -- compatibility binding
from gnd.exp.session_patch import PatchRefusal as PatchRefusal  # noqa: PLC0414 -- compatibility binding
from gnd.exp.session_patch import apply_candidate_patch as apply_candidate_patch  # noqa: PLC0414 -- compatibility binding
from gnd.exp.session_patch import proposal_mode as proposal_mode  # noqa: PLC0414 -- compatibility binding
from gnd.exp.session_patch import read_patch_document as read_patch_document  # noqa: PLC0414 -- compatibility binding
from gnd.exp.session_store import AttemptRecord as AttemptRecord  # noqa: PLC0414 -- compatibility binding
from gnd.exp.session_store import BestAttemptIdentity as BestAttemptIdentity  # noqa: PLC0414 -- compatibility binding
from gnd.exp.session_store import ResumeState as ResumeState  # noqa: PLC0414 -- compatibility binding
from gnd.exp.session_store import SessionResult as SessionResult  # noqa: PLC0414 -- compatibility binding
from gnd.exp.session_store import SessionStore as SessionStore  # noqa: PLC0414 -- compatibility binding
from gnd.exp.session_store import WalkFloorResult as WalkFloorResult  # noqa: PLC0414 -- compatibility binding
from gnd.exp.session_store import _collect_candidate as _collect_candidate  # noqa: PLC0414 -- compatibility binding
from gnd.exp.session_store import _evidence_entry as _evidence_entry  # noqa: PLC0414 -- compatibility binding
from gnd.model import load_model_bytes as load_model_bytes  # noqa: PLC0414 -- compatibility binding
from gnd.population import load_population as load_population  # noqa: PLC0414 -- compatibility binding
from gnd.references import bind_references as bind_references  # noqa: PLC0414 -- compatibility binding
from gnd.exp.session_replay import _read as _read  # noqa: PLC0414 -- strategy hook
from gnd.exp.session_replay import _entry as _entry  # noqa: PLC0414 -- strategy hook
from gnd.exp.session_replay import _model as _model  # noqa: PLC0414 -- strategy hook
from gnd.exp.session_replay import _evaluate as _evaluate  # noqa: PLC0414 -- strategy hook
from gnd.exp.session_replay import _project as _project  # noqa: PLC0414 -- strategy hook
from gnd.exp.session_replay import _feedback as _feedback  # noqa: PLC0414 -- strategy hook
from gnd.exp.session_replay import reconstruct as reconstruct  # noqa: PLC0414 -- strategy hook
from gnd.exp.session_runtime import _copy_files as _copy_files  # noqa: PLC0414 -- strategy hook
from gnd.exp.session_runtime import run as run  # noqa: PLC0414 -- strategy hook
