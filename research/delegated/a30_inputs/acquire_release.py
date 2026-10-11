#!/usr/bin/env python3
"""Acquire public A29 assets and pinned morphology source; never run physics."""
from pathlib import Path
import datetime as dt
import json
import os
import re
import resource
import subprocess
import time

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RELEASES = ROOT / "inputs/releases"
TARGET = ROOT / "inputs/a29_release"
A29 = ROOT.parents[1] / "A29/a29-material-hypothesis-coverage"
PIN = "5d5e31fcfc56ac8ef9d64c46b4b7bbdedef96bb4"
REPO = "migodam/a29-material-hypothesis-coverage"
TAG = "a29-v0.1.0"
ASSETS = ("A29_RAW_EVIDENCE.zip", "A29_REPRO_INPUTS.zip")
LEDGER = OUT / "TRANSPORT_COST_LEDGER.jsonl"
FAILURES = OUT / "TRANSPORT_FAILURE_LEDGER.jsonl"
SUMMARY = OUT / "ACQUISITION.json"

def stamp():
    return dt.datetime.now(dt.timezone.utc).isoformat()

def append(path, record):
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(record, sort_keys=True) + "\n")

def safe_error(value):
    return re.sub(r"(https?://[^\s?]+)\?[^\s]+", r"\1?[query omitted]", value)[:8000]

def command(kind, args, *, cwd=ROOT, timeout=120):
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    cpu0, wall0, started = time.process_time(), time.perf_counter(), stamp()
    try:
        result = subprocess.run(args, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                env={**os.environ, "GH_PROMPT_DISABLED": "1"}, timeout=timeout)
        code, stdout, stderr = result.returncode, result.stdout, result.stderr.decode("utf-8", "replace")
    except subprocess.TimeoutExpired as exc:
        code, stdout, stderr = 124, exc.stdout or b"", "TIMEOUT: " + str(timeout) + " seconds"
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    parent_cpu = time.process_time() - cpu0
    child_cpu = after.ru_utime + after.ru_stime - before.ru_utime - before.ru_stime
    rec = {"kind": kind, "started_utc": started, "finished_utc": stamp(), "command": args,
           "wall_seconds": time.perf_counter() - wall0, "parent_process_cpu_seconds": parent_cpu,
           "child_process_cpu_seconds": child_cpu, "total_process_cpu_seconds": parent_cpu + child_cpu,
           "returncode": code, "stderr": safe_error(stderr), "GPU_seconds": 0,
           "Maxwell_material_states": 0, "training_updates": 0, "locked_payload_reads": 0}
    append(LEDGER, rec)
    if code:
        append(FAILURES, rec)
    return code, stdout, rec

def save():
    SUMMARY.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

OUT.mkdir(parents=True, exist_ok=True)
RELEASES.mkdir(parents=True, exist_ok=True)
TARGET.mkdir(parents=True, exist_ok=True)
summary = {"status": "RUNNING", "repository": "https://github.com/" + REPO,
           "release_tag": TAG, "pinned_commit": PIN, "SHA256_checks": "NOT_RUN_BY_USER_POLICY",
           "Maxwell_material_states": 0, "training_updates": 0, "locked_payload_reads": 0,
           "downloads": [], "started_utc": stamp()}
save()
code, raw, _ = command("pinned_local_source_identity", ["git", "rev-parse", "HEAD"], cwd=A29)
if code or raw.decode().strip() != PIN:
    summary.update(status="FAILED", reason="PINNED_LOCAL_A29_HEAD_MISMATCH")
    save()
    raise SystemExit(2)
summary["local_A29_HEAD"] = raw.decode().strip()
for name in ("metrics.py", "__init__.py"):
    code, raw, rec = command("pinned_source_copy_" + name,
                             ["git", "show", PIN + ":src/a26/" + name], cwd=A29)
    if code:
        summary.update(status="FAILED", reason="PINNED_SOURCE_MISSING:" + name)
        save()
        raise SystemExit(2)
    dest = TARGET / "src/a26" / name
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.read_bytes() != raw:
        raise RuntimeError("EXISTING_PINNED_SOURCE_CONFLICT:" + str(dest))
    dest.write_bytes(raw)
summary["source_files"] = ["src/a26/metrics.py", "src/a26/__init__.py"]
summary["source_copy_method"] = "git show exact pinned commit; copied bytes without working-tree imports"

code, raw, _ = command("public_release_tag_resolution",
    ["git", "ls-remote", "https://github.com/" + REPO + ".git", "refs/tags/" + TAG, "refs/tags/" + TAG + "^{}"])
if code:
    summary.update(status="FAILED", reason="RELEASE_TAG_RESOLUTION_FAILED")
    save()
    raise SystemExit(2)
refs = dict(line.split()[::-1] for line in raw.decode().splitlines() if line.strip())
commit = refs.get("refs/tags/" + TAG + "^{}", refs.get("refs/tags/" + TAG))
summary["public_release_refs"] = refs
summary["public_release_tag_commit"] = commit
if commit != PIN:
    summary.update(status="FAILED", reason="PUBLIC_TAG_DOES_NOT_MATCH_PINNED_COMMIT")
    save()
    raise SystemExit(2)

code, raw, _ = command("public_release_metadata", ["gh", "release", "view", TAG, "--repo", REPO,
                         "--json", "url,tagName,targetCommitish,assets,publishedAt,isDraft,isPrerelease"])
if code:
    summary.update(status="FAILED", reason="GH_RELEASE_METADATA_FAILED")
    save()
    raise SystemExit(2)
metadata = json.loads(raw)
filtered = {k: metadata.get(k) for k in ("url", "tagName", "targetCommitish", "publishedAt", "isDraft", "isPrerelease")}
filtered["assets"] = [{k: asset.get(k) for k in ("name", "size", "url", "contentType", "state", "id")}
                      for asset in metadata.get("assets", [])]
(OUT / "RELEASE_METADATA.json").write_text(json.dumps(filtered, indent=2) + "\n")
by_name = {asset["name"]: asset for asset in metadata.get("assets", [])}
if metadata.get("tagName") != TAG or metadata.get("isDraft") or any(name not in by_name for name in ASSETS):
    raise RuntimeError("PUBLIC_RELEASE_ASSET_DEFINITION_MISMATCH")
save()
for name in ASSETS:
    expected = int(by_name[name]["size"])
    dest = RELEASES / name
    download = {"asset": name, "expected_bytes": expected, "public_download_url":
                "https://github.com/" + REPO + "/releases/download/" + TAG + "/" + name, "attempts": []}
    summary["downloads"].append(download)
    if dest.exists() and dest.stat().st_size == expected:
        download.update(status="EXISTING_SIZE_MATCH", actual_bytes=dest.stat().st_size)
        save()
        continue
    if dest.exists():
        raise RuntimeError("EXISTING_RELEASE_SIZE_CONFLICT:" + name)
    stage = RELEASES / (".download-" + name)
    stage.mkdir(exist_ok=True)
    code, _, rec = command("asset_download_attempt_1:" + name,
        ["gh", "release", "download", TAG, "--repo", REPO, "--pattern", name, "--dir", str(stage)], timeout=600)
    candidate = stage / name
    actual = candidate.stat().st_size if candidate.exists() else 0
    attempt = {**rec, "attempt": 1, "actual_bytes": actual, "expected_bytes": expected,
               "complete_size_match": code == 0 and actual == expected}
    download["attempts"].append(attempt)
    if not attempt["complete_size_match"]:
        append(FAILURES, {"kind": "DOWNLOAD_SIZE_OR_EXIT_FAILURE", "asset": name, **attempt})
        candidate.unlink(missing_ok=True)
        part = stage / (name + ".part")
        code, _, rec = command("asset_download_attempt_2:" + name,
            ["curl", "--location", "--fail", "--silent", "--show-error", "--connect-timeout", "30",
             "--max-time", "600", "--output", str(part), download["public_download_url"]], timeout=620)
        actual = part.stat().st_size if part.exists() else 0
        attempt = {**rec, "attempt": 2, "actual_bytes": actual, "expected_bytes": expected,
                   "complete_size_match": code == 0 and actual == expected}
        download["attempts"].append(attempt)
        if not attempt["complete_size_match"]:
            append(FAILURES, {"kind": "DOWNLOAD_SIZE_OR_EXIT_FAILURE", "asset": name, **attempt})
            download.update(status="FAILED", actual_bytes=actual)
            summary.update(status="FAILED", reason="ASSET_DOWNLOAD_FAILED:" + name)
            save()
            raise SystemExit(2)
        candidate = part
    candidate.replace(dest)
    stage.rmdir()
    download.update(status="DOWNLOADED_SIZE_MATCH", actual_bytes=dest.stat().st_size,
                    local_path=str(dest.relative_to(ROOT)))
    save()
summary.update(status="ACQUIRED_PENDING_SAFE_ZIP_AUDIT", finished_utc=stamp())
save()
print(json.dumps({"status": summary["status"], "assets": [{k: x[k] for k in
      ("asset", "expected_bytes", "actual_bytes", "status")} for x in summary["downloads"]]}, indent=2))
