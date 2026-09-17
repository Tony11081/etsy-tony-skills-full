from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


HARNESS = Path(__file__).resolve().parent.parent / "harness"


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the local eRank CLI-Anything harness.")
    parser.add_argument("args", nargs=argparse.REMAINDER, help="Arguments after -- are passed to cli_anything.erank.")
    parsed = parser.parse_args()

    args = parsed.args
    if args and args[0] == "--":
        args = args[1:]
    if not args:
        args = ["--help"]

    if not HARNESS.exists():
        print(f"Harness not found: {HARNESS}", file=sys.stderr)
        return 2

    command = [sys.executable, "-m", "cli_anything.erank", *args]
    completed = subprocess.run(command, cwd=HARNESS)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
