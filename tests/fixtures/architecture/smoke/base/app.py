"""The corpus entry point. One module, one behaviour per subcommand.

Kept deliberately small and dependency-free: every case's story is told by the
contract that drives it, not by this file. Declared exits are 0, 1, 3 and 7.
"""

from __future__ import annotations

import os
import subprocess
import sys
import time


def main(argv: list[str]) -> int:
    if not argv:
        return 2
    command, rest = argv[0], argv[1:]
    if command == "ok":
        print("ok")
        return 0
    if command == "refuse":
        print("refused", file=sys.stderr)
        return 3
    if command == "boom":
        raise ValueError("boom")
    if command == "write":
        with open(rest[0], "w", encoding="utf-8") as handle:
            handle.write("written\n")
        return 0
    if command == "readfile":
        with open(rest[0], encoding="utf-8") as handle:
            print(handle.read().strip())
        return 0
    if command == "sleep":
        time.sleep(float(rest[0]))
        return 0
    if command == "spawn-and-sleep":
        subprocess.Popen([sys.executable, "-c", "import time; time.sleep(45)"])
        time.sleep(45)
        return 0
    if command == "flood":
        chunk = b"x" * 4096
        for _ in range(int(rest[0])):
            sys.stdout.buffer.write(chunk)
        sys.stdout.buffer.flush()
        return 0
    if command == "badbytes":
        sys.stdout.buffer.write(b"\xff\xfe not utf-8 \xc3\x28")
        sys.stdout.buffer.flush()
        return 0
    if command == "pid":
        print(os.getpid())
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
