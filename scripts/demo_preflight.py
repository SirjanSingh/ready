"""Check everything the demo video depends on, live, before recording.

    uv run python scripts/demo_preflight.py [--alan-pin 89912c2]

Each line is PASS or FAIL with the reason. Nothing is changed: it only reads GitHub and
starts the MCP server once to time it.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import time
from pathlib import Path

import yaml

DEMO = "SirjanSingh/ready-demo"
LABEL = {"agent_ready": "agent-ready", "needs_human": "needs-human"}
ISSUES = yaml.safe_load((Path(__file__).parent.parent / "docs" / "demo-issues.yaml").read_text(encoding="utf-8"))


def gh(*args: str) -> str:
    return subprocess.run(["gh", *args], capture_output=True, text=True, check=True).stdout.strip()


def report(ok: bool, what: str, why: str = "") -> bool:
    print(f"{'PASS' if ok else 'FAIL'}  {what}" + (f": {why}" if why else ""))
    return ok


def check_pin() -> bool:
    pin = gh("variable", "get", "READY_SOURCE", "-R", DEMO)
    repo, _, ref = pin.partition("@")
    try:
        sha = gh("api", f"repos/{repo}/commits/{ref or 'HEAD'}", "-q", ".sha")[:7]
        return report(True, "Action pin", f"{pin} -> {sha}")
    except subprocess.CalledProcessError:
        return report(False, "Action pin", f"{pin} does not resolve on GitHub")


def check_runs() -> bool:
    runs = json.loads(gh("run", "list", "-R", DEMO, "-L", "5", "--json", "conclusion,event,createdAt"))
    bad = [r for r in runs if r["conclusion"] not in ("success", "skipped", "")]
    return report(not bad, "last 5 Action runs", "all succeeded" if not bad else f"{len(bad)} failed: {bad}")


def check_labels() -> bool:
    ok = True
    for i in ISSUES:
        if not i.get("number"):
            continue
        want = LABEL[i.get("expect_live", i["expect"])]
        got = json.loads(gh("issue", "view", str(i["number"]), "-R", DEMO, "--json", "labels"))["labels"]
        names = [lb["name"] for lb in got]
        ok &= report(want in names, f"#{i['number']} {i['id']}", f"label {names or 'none'}, want {want} ({i['beat']})")
    return ok


def check_mcp(pin: str) -> bool:
    init = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
        "protocolVersion": "2025-03-26", "capabilities": {}, "clientInfo": {"name": "preflight", "version": "0"}}}) + "\n"
    pin = gh("api", f"repos/SirjanSingh/ready/commits/{pin}", "-q", ".sha")  # a short sha makes uv fetch every time
    cmd = ["uvx", "--from", f"git+https://github.com/SirjanSingh/ready@{pin}", "ready-mcp"]
    t = time.time()
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    p.stdin.write(init)
    p.stdin.flush()
    line = p.stdout.readline()
    p.kill()
    secs = time.time() - t
    return report('"result"' in line and secs < 5, "MCP server start (Alan's limit is 5 s)", f"{secs:.1f} s with the connector's pin @{pin}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--alan-pin", default="89912c2", help="commit the Alan connector is pinned to")
    args = ap.parse_args()
    results = [check_pin(), check_runs(), check_labels(), check_mcp(args.alan_pin)]
    print("\nREADY TO RECORD" if all(results) else "\nFIX THE FAILS ABOVE BEFORE RECORDING")
    raise SystemExit(0 if all(results) else 1)


if __name__ == "__main__":
    main()
