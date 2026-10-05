"""A loopback OpenAI-compatible gateway that lets a small hosted model drive a GND session.

GND's ``openai-compatible`` adapter sends the model one prompt that names the
session contract and, on a retry, carries the previous attempt's closed
feedback. A model without file tools cannot open that contract. This gateway
supplies the context a tool-using agent would read for itself (the task, the
model and the current state), forwards one request to
OpenRouter, and returns the reply as the base64 file bundle GND expects.

The OpenRouter key lives only in this process's environment. GND never sees
it: the session policy names a placeholder variable for the loopback hop.

    OPENROUTER_API_KEY=... python tools/openrouter_gateway.py --port 8765

It is an example gateway, not a supported component.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

UPSTREAM = "https://openrouter.ai/api/v1/chat/completions"
SYSTEM = (
    "You write plans for GND, a checker of operation walks. Reply with ONLY one JSON object "
    "of the form {\"steps_schema\": 1, \"model\": \"../model.orm.yaml\", \"model_digest\": ..., "
    "\"operations_digest\": ..., \"steps\": [{\"op\": ..., \"bindings\": {...}}]}. "
    "No prose and no code fences. Use only operations declared in the model and bind exactly "
    "their parameters."
)


def context(prompt: str) -> str:
    contract_path = Path(re.search(r"contract at (\S+?)\.(?:\s|$)", prompt).group(1))
    root = contract_path.parent
    parts = [
        (root / "input/TASK.md").read_text(),
        "model.orm.yaml:\n" + (root / "model.orm.yaml").read_text(),
        "input/state.pop.yaml:\n" + (root / "input/state.pop.yaml").read_text(),
    ]
    encoded = re.search(r"\(RFC 4648 base64\):\n(\S+)", prompt)
    if encoded:
        feedback = base64.b64decode(encoded.group(1)).decode()
        parts.append("Your previous plan was checked by GND. Closed feedback (no answer is included):\n"
                     + feedback + "\nWrite a corrected plan.")
    return "\n\n".join(parts)


def ask(model: str, text: str) -> str:
    body = json.dumps({"model": model, "messages": [
        {"role": "system", "content": SYSTEM}, {"role": "user", "content": text}]}).encode()
    request = urllib.request.Request(UPSTREAM, body, {
        "Authorization": "Bearer " + os.environ["OPENROUTER_API_KEY"], "Content-Type": "application/json"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=120) as reply:
                return json.load(reply)["choices"][0]["message"]["content"] or ""
        except urllib.error.HTTPError as error:
            if error.code not in {429, 500, 502, 503} or attempt == 3:
                raise
            time.sleep(4 * (attempt + 1))
    return ""


def bundle(reply: str) -> str:
    plan = re.sub(r"^```(?:json)?\s*|\s*```$", "", reply.strip())
    files = [{"path": "steps.json", "content_base64": base64.b64encode(plan.encode()).decode()}]
    return json.dumps({"schema_version": 1, "files": files})


class Gateway(BaseHTTPRequestHandler):
    log: Path | None = None

    def do_POST(self) -> None:
        request = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        prompt = request["messages"][-1]["content"]
        reply = ask(request["model"], context(prompt))
        if self.log:
            with self.log.open("a") as handle:
                handle.write(json.dumps({"model": request["model"], "reply": reply}) + "\n")
        payload = json.dumps({"choices": [{"message": {"role": "assistant", "content": bundle(reply)}}]}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, *args: object) -> None:
        pass


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--log", type=Path, help="append each model reply to this file")
    args = parser.parse_args()
    Gateway.log = args.log
    HTTPServer(("127.0.0.1", args.port), Gateway).serve_forever()


if __name__ == "__main__":
    main()
