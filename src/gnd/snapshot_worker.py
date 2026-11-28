"""Local JSON Lines protocol for repeated ordinary Python snapshot checks."""
from __future__ import annotations

import json
import sys
from hashlib import sha256
from pathlib import Path

from gnd import api, input_policy
from gnd.anchors import read_regular_path
from gnd.errors import ModelLoadError, ModelValidationError, PopulationLoadError
from gnd.model import load_model_bytes
from gnd.population import load_population_bytes

LINE_LIMIT = 4 * 1024 * 1024


class RequestError(ValueError):
    """A fixed protocol code, suitable for returning across the process boundary."""


class Worker:
    def __init__(self):
        self.identity = None
        self.session = None
        self.model = None

    def close(self):
        if self.session is not None:
            self.session.close()
        self.identity = self.model = self.session = None

    def check(self, request):
        if type(request.get("version")) is not int or request["version"] != 1:
            raise RequestError("unsupported-version")
        if set(request) != {"version", "id", "model", "population"}:
            raise RequestError("invalid-request")
        if not isinstance(request["model"], str) or not isinstance(request["population"], dict):
            raise RequestError("invalid-request")
        path = Path(request["model"]).absolute()
        model_bytes = read_regular_path(path, label="worker model", max_bytes=input_policy.MAX_BYTES)
        identity = (str(path), sha256(model_bytes).hexdigest())
        reused = identity == self.identity
        if not reused:
            self.close()
            model = load_model_bytes(model_bytes, source=path)
            if model.reference_populations or model.includes:
                raise RequestError("external-model-dependencies")
            self.session = api.EvaluationSession(model)
            self.model, self.identity = model, identity
        population_bytes = json.dumps(request["population"], allow_nan=False).encode("utf-8")
        pop = load_population_bytes(population_bytes, source="request.json", model=self.model)
        report = self.session.check(pop)
        return {"model_sha256": identity[1], "model_reused": reused, "report": report}

    def reply(self, raw):
        request_id = None
        try:
            request = input_policy.loads(raw, max_bytes=LINE_LIMIT)
            if not isinstance(request, dict):
                raise RequestError("invalid-request")
            value = request.get("id")
            if not isinstance(value, str) or not 1 <= len(value) <= 128:
                raise RequestError("invalid-id")
            request_id = value
            return {"version": 1, "id": request_id, "status": "evaluated", **self.check(request)}
        except RequestError as error:
            code = str(error)
        except (ValueError, OSError, TypeError, RecursionError, ModelLoadError, ModelValidationError, PopulationLoadError):
            code = "invalid-input"
        except Exception:  # noqa: BLE001 -- isolate an unexpected evaluation failure to one request
            # The worker survives an unexpected checker failure without reusing its state.
            self.close()
            code = "evaluation-error"
        return {"version": 1, "id": request_id, "status": "error", "error": code}


def serve(incoming, outgoing):
    worker = Worker()
    try:
        while line := incoming.readline(LINE_LIMIT + 1):
            if len(line) > LINE_LIMIT:
                while line and not line.endswith(b"\n"):
                    line = incoming.readline(LINE_LIMIT + 1)
                response = {"version": 1, "id": None, "status": "error", "error": "request-too-large"}
            else:
                response = worker.reply(line)
            wire = json.dumps(response, ensure_ascii=True, allow_nan=False, separators=(",", ":"))
            outgoing.write(wire.encode("ascii") + b"\n")
            outgoing.flush()
    finally:
        worker.close()


if __name__ == "__main__":
    serve(sys.stdin.buffer, sys.stdout.buffer)
