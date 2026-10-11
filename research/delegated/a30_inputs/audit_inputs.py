#!/usr/bin/env python3
"""Metadata-first audit of public release arrays. No material scoring or solver."""
import time
WALL0 = time.perf_counter()
from pathlib import Path, PurePosixPath
from collections import Counter
import csv
import datetime as dt
import json
import os
import re
import shutil
import stat
import traceback
import zipfile
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
TARGET = ROOT / "inputs/a29_release"
RELEASES = ROOT / "inputs/releases"
FAMILIES = ("shell", "asymmetric_piecewise", "smooth", "mixed_scale")
PARENTS = tuple(range(250065, 250081))
CASES = tuple(f"p{p}_{bg}_a1_snr20" for p in PARENTS for bg in ("weak", "ring"))
ROW_META = {"parent_id", "background_id", "split", "family", "ood_type", "variant_id",
            "case_id", "amplitude", "noise_db", "status", "sigma"}
SCALAR_META = {"manifest_id", "geometry_descriptor"}
header_records, metadata_reads, zip_records, checks, issues = [], [], [], [], []

def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()

def write_json(path, obj):
    path.write_text(json.dumps(obj, indent=2, allow_nan=False) + "\n", encoding="utf-8")

def write_csv(path, rows):
    keys = list(dict.fromkeys(k for row in rows for k in row))
    with path.open("w", newline="", encoding="utf-8") as stream:
        w = csv.DictWriter(stream, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)

def require(ok, name, detail=None):
    checks.append({"check": name, "status": "PASS" if ok else "FAIL", "detail": detail})
    if not ok:
        issues.append({"check": name, "detail": detail})
        raise ValueError(name + ":" + str(detail))

def path_locked(path):
    return any(part.lower() == "locked" or part.lower().startswith(("locked_id", "locked_ood"))
               for part in Path(path).parts)

def safe_zip_member(info):
    name = info.filename
    path = PurePosixPath(name)
    mode = info.external_attr >> 16
    why = []
    if not name or name.startswith(("/", "\\")) or "\\" in name or "\x00" in name:
        why.append("invalid_absolute_or_separator")
    if any(part in ("", ".", "..") for part in path.parts) or re.match(r"^[A-Za-z]:", name):
        why.append("traversal_or_drive")
    if stat.S_ISLNK(mode) or (stat.S_IFMT(mode) and not (stat.S_ISREG(mode) or stat.S_ISDIR(mode))):
        why.append("symlink_or_nonregular_entry")
    if info.flag_bits & 1:
        why.append("encrypted_entry")
    if path_locked(path):
        why.append("locked_path")
    destination = TARGET.joinpath(*path.parts)
    if not destination.resolve().is_relative_to(TARGET.resolve()):
        why.append("escaped_target")
    return why

def inspect_and_extract():
    definitions = json.loads((OUT / "RELEASE_METADATA.json").read_text())
    sizes = {x["name"]: int(x["size"]) for x in definitions["assets"]}
    planned, names = [], set()
    for name in ("A29_RAW_EVIDENCE.zip", "A29_REPRO_INPUTS.zip"):
        path = RELEASES / name
        require(path.is_file() and path.stat().st_size == sizes[name], "ASSET_SIZE:" + name)
        with zipfile.ZipFile(path) as archive:
            local_names = set()
            for info in archive.infolist():
                why = safe_zip_member(info)
                if info.filename in local_names or info.filename in names:
                    why.append("duplicate_entry")
                local_names.add(info.filename)
                names.add(info.filename)
                zip_records.append({"asset": name, "member": info.filename, "bytes": info.file_size,
                    "compressed_bytes": info.compress_size, "unix_mode": oct(info.external_attr >> 16),
                    "unsafe_reasons": ";".join(why), "compression": info.compress_type})
                require(not why, "SAFE_ZIP_ENTRY", {"asset": name, "member": info.filename, "reasons": why})
            planned.append((path, archive.infolist()))
    write_csv(OUT / "ZIP_ENTRIES.csv", zip_records)
    for path, infos in planned:
        with zipfile.ZipFile(path) as archive:
            for info in infos:
                dest = TARGET / info.filename
                if info.is_dir():
                    dest.mkdir(parents=True, exist_ok=True)
                    continue
                require(not dest.exists(), "NO_EXTRACTION_OVERWRITE", str(dest.relative_to(ROOT)))
                dest.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(info) as source, dest.open("xb") as stream:
                    shutil.copyfileobj(source, stream, 1024 * 1024)
                require(dest.stat().st_size == info.file_size, "EXTRACTED_SIZE", info.filename)
    return {"asset_count": 2, "entries": len(zip_records), "uncompressed_bytes": sum(x["bytes"] for x in zip_records),
            "unsafe_entries": 0, "locked_path_entries": 0, "symlinks": 0,
            "extract_root": str(TARGET.relative_to(ROOT)), "extraction_numeric_interpretation": False}

def headers(relative):
    path = TARGET / relative
    require(path.is_file() and not path.is_symlink() and not path_locked(path), "HEADER_INPUT_PATH", relative)
    result = {}
    with zipfile.ZipFile(path) as archive:
        for info in archive.infolist():
            require(info.filename.endswith(".npy") and not safe_zip_member(info), "SAFE_NPZ_MEMBER",
                    {"file": relative, "member": info.filename})
            field = info.filename[:-4]
            require(field not in result, "DISTINCT_NPZ_FIELD", {"file": relative, "field": field})
            with archive.open(info) as stream:
                version = np.lib.format.read_magic(stream)
                if version == (1, 0):
                    shape, order, dtype = np.lib.format.read_array_header_1_0(stream)
                elif version == (2, 0):
                    shape, order, dtype = np.lib.format.read_array_header_2_0(stream)
                else:
                    raise ValueError("UNSUPPORTED_NPY_HEADER_VERSION:" + str(version))
            require(not dtype.hasobject, "NO_OBJECT_PICKLE_FIELD", {"file": relative, "field": field})
            record = {"archive": relative, "field": field, "shape": list(shape), "dtype": dtype.str,
                      "fortran_order": bool(order), "array_values_read": False}
            result[field] = record
            header_records.append(record)
    return result

def metadata(relative, keys):
    require(not path_locked(relative), "METADATA_NO_LOCKED_PATH", relative)
    with np.load(TARGET / relative, allow_pickle=False) as archive:
        result = {key: archive[key].copy() for key in keys}
    metadata_reads.append({"archive": relative, "fields": sorted(keys), "role": "identity_condition_metadata_only",
                           "truth_or_chi_or_current_or_clean_values_read": False})
    return result

def shape_is(h, field, shape, dtype=None):
    return field in h and h[field]["shape"] == list(shape) and (dtype is None or h[field]["dtype"] == np.dtype(dtype).str)

def family(parent, role="validation"):
    first, size = (250001, 16) if role == "train" else (250065, 4)
    return FAMILIES[(int(parent) - first) // size]

def audit_split(role, manifest, geometry):
    first, end = (250001, 250065) if role == "train" else (250065, 250081)
    expected = tuple(range(first, end))
    relative = "inputs/a25/" + role + ".npz"
    h = headers(relative)
    n = 8 * len(expected)
    require(shape_is(h, "chi", (n, 576), np.complex128) and shape_is(h, "data", (n, 32, 8), np.complex128),
            "SPLIT_MATERIAL_MEASUREMENT_HEADERS:" + role)
    m = metadata(relative, ROW_META | SCALAR_META)
    require(m["parent_id"].dtype == np.int64 and m["parent_id"].shape == (n,) and
            Counter(m["parent_id"].tolist()) == Counter({p: 8 for p in expected}), "EXACT_PARENT_WHITELIST:" + role)
    require(all(np.asarray(m[k]).shape == (n,) for k in ROW_META), "ALIGNED_ROW_METADATA:" + role)
    require(all(str(x) == role for x in m["split"]), "SPLIT_ROLE:" + role)
    require(str(m["manifest_id"].item()) == manifest["manifest_id"] and
            json.loads(str(m["geometry_descriptor"].item())) == geometry, "MANIFEST_GEOMETRY_IDENTITY:" + role)
    require(all(str(x) == "OK" for x in m["status"]), "RETAINED_STATUS_ROWS:" + role)
    expected_conditions = set((p, bg, ai, ni) for p in expected for bg in ("weak", "ring") for ai in (0, 1) for ni in (0, 1))
    seen = []
    for i, pid in enumerate(m["parent_id"]):
        pid, bg = int(pid), str(m["background_id"][i])
        require(str(m["family"][i]) == family(pid, role) and str(m["ood_type"][i]) == "ID", "SPLIT_FAMILY_OOD:" + role)
        amplitude = float(m["amplitude"][i])
        require(amplitude in (.3, 1.2), "FROZEN_AMPLITUDE:" + role)
        ai = (.3, 1.2).index(amplitude)
        db, sigma = float(m["noise_db"][i]), float(m["sigma"][i])
        ni = 0 if np.isnan(db) else 1
        require((ni == 0 and sigma == 0) or (ni == 1 and db == 20 and sigma > 0), "NOISE_METADATA:" + role)
        case = f"p{pid}_{bg}_a{ai}_" + ("clean" if ni == 0 else "snr20")
        require(str(m["case_id"][i]) == case and str(m["variant_id"][i]) == f"{bg}:a{ai}:n{ni}", "CONDITION_ID:" + role)
        seen.append((pid, bg, ai, ni))
    require(set(seen) == expected_conditions and len(set(seen)) == n, "EXACT_EIGHT_CONDITIONS:" + role)
    return m, {"role": role, "rows": n, "parents": len(expected), "parent_ids": list(expected),
               "material_header": h["chi"], "measurement_header": h["data"],
               "label_values_read": False, "current_values_read": False, "clean_values_read": False}

def audit_all():
    extraction = inspect_and_extract()
    manifest = json.loads((TARGET / "inputs/a25/manifest.json").read_text())
    geometry = json.loads((TARGET / "inputs/a25/geometry.json").read_text())
    scope = json.loads((TARGET / "INPUT_SCOPE.json").read_text())
    require(manifest["splits"] == {"train": list(range(250001, 250065)), "validation": list(PARENTS)}, "PUBLIC_MANIFEST_WHITELISTS")
    require(manifest["parent_count"] == 80 and len(manifest["parents"]) == 80, "PUBLIC_MANIFEST_80_PARENTS")
    require(geometry["grid"] == 24 and geometry["sources"] == 8 and geometry["receivers"] == 32 and
            geometry["volume"] == 1 / 576 and geometry["precision"] == "complex128/float64", "FROZEN_GEOMETRY")
    require(scope["locked_ID_OOD_payload"] == "EXCLUDED" and scope["anatomy_files"] == 32 and
            scope["paid_exact_state_files"] == 32, "DECLARED_INPUT_SCOPE")
    train, train_summary = audit_split("train", manifest, geometry)
    dev, dev_summary = audit_split("validation", manifest, geometry)
    selected = [i for i in range(len(dev["case_id"])) if float(dev["amplitude"][i]) == 1.2 and float(dev["sigma"][i]) > 0]
    selected_cases = {str(dev["case_id"][i]) for i in selected}
    require(selected_cases == set(CASES) and len(selected) == 32, "FROZEN_A29_32_CONDITIONS")

    target_rel = "results/a29/OFFLINE_TARGETS.npz"
    target_headers = headers(target_rel)
    for field in ("truth", "N3", "background"):
        require(shape_is(target_headers, field, (32, 576), np.complex128), "TARGET_HEADER:" + field)
    target_meta = metadata(target_rel, {"case_id", "parent_id", "family", "background_id"})
    require(tuple(map(str, target_meta["case_id"])) == CASES, "OFFLINE_TARGET_EXACT_ORDER")
    for i, case in enumerate(CASES):
        p = PARENTS[i // 2]
        require(int(target_meta["parent_id"][i]) == p and str(target_meta["family"][i]) == family(p) and
                str(target_meta["background_id"][i]) == ("weak", "ring")[i % 2], "OFFLINE_TARGET_METADATA", case)
    with (TARGET / "results/a29/COVERAGE_CASES.csv").open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        coverage_columns = list(reader.fieldnames)
        coverage = [{k: row[k] for k in ("case_id", "parent_id", "family", "background_id")} for row in reader]
    require(len(coverage) == 32 and {x["case_id"] for x in coverage} == set(CASES), "COVERAGE_CSV_32_IDENTITIES")
    require(all(int(x["parent_id"]) in PARENTS and x["family"] == family(int(x["parent_id"])) and
                x["case_id"] == f"p{x['parent_id']}_{x['background_id']}_a1_snr20" for x in coverage), "COVERAGE_CSV_METADATA")
    pool_dir = TARGET / "results/a29/pools"
    require({p.stem for p in pool_dir.glob("*.npz")} == set(CASES) and
            {p.stem for p in pool_dir.glob("*.json")} == set(CASES), "EXACT_32_POOL_FILES")
    pool_rows = []
    for i, case in enumerate(CASES):
        relative = "results/a29/pools/" + case + ".npz"
        h = headers(relative)
        n = h["chi"]["shape"][0]
        require(1 <= n <= 256 and shape_is(h, "chi", (n, 576), np.complex128) and
                shape_is(h, "L", (n, 32, 8), np.complex128), "POOL_COMPLEX_HEADERS", case)
        for field in ("ids", "categories", "penalty", "prior"):
            require(shape_is(h, field, (n,)), "POOL_ROW_HEADER", case + ":" + field)
        for field in ("n3", "background"):
            require(shape_is(h, field, (576,), np.complex128), "POOL_MATERIAL_HEADER", case + ":" + field)
        require(shape_is(h, "observation", (32, 8), np.complex128) and shape_is(h, "sigma", ()), "POOL_OBSERVATION_HEADER", case)
        m = metadata(relative, {"small_indices", "ids", "categories", "sigma"})
        small = m["small_indices"].tolist()
        require(len(small) == 12 and len(set(small)) == 12 and all(0 <= j < n for j in small) and 0 in small,
                "FROZEN_SMALL_POOL_INDICES", case)
        require(len(set(map(str, m["ids"]))) == n and float(m["sigma"]) > 0, "POOL_IDS_SIGMA", case)
        provenance = json.loads((pool_dir / (case + ".json")).read_text())
        meta = provenance["meta"]
        p = PARENTS[i // 2]
        require(meta == {"case_id": case, "parent_id": p, "family": family(p), "background_id": ("weak", "ring")[i % 2]}
                and provenance["truth_access"] is False, "POOL_ONLINE_PROVENANCE", case)
        pool_rows.append({**meta, "pool_count": n, "small_count": len(small), "chi_shape": str(h["chi"]["shape"]),
                          "L_shape": str(h["L"]["shape"]), "fields": ";".join(h), "truth_access_in_release": False})
    write_csv(OUT / "POOL_AUDIT.csv", pool_rows)

    predictions_rel = "inputs/a26/results/a26/evaluation/261009/PREDICTIONS.npz"
    prediction_headers = headers(predictions_rel)
    require(shape_is(prediction_headers, "N3", (128, 576), np.complex128) and
            shape_is(prediction_headers, "COMMON_BP_INITIAL", (128, 576), np.complex128), "N3_BP_PREDICTION_HEADERS")
    prediction_meta = metadata(predictions_rel, {"case_id", "parent_id", "family", "background_id", "sigma", "split", "amplitude"})
    require(all(np.array_equal(prediction_meta[k], dev[k]) for k in prediction_meta), "PREDICTION_DEVELOPMENT_METADATA_ALIGNMENT")
    headers("results/a29/TRAIN_TEMPLATES.npz")
    background_headers = {}
    for bg in ("weak", "ring"):
        h = headers("inputs/a25/background/" + bg + ".npz")
        require(shape_is(h, "chi_b", (576,), np.complex128) and shape_is(h, "J", (512, 1152), np.float64), "BACKGROUND_CHART_HEADERS", bg)
        background_headers[bg] = {k: h[k] for k in ("chi_b", "J")}
    for case in CASES:
        anatomy = "inputs/a28/results/a28/anatomy/" + case + ".npz"
        exact = "inputs/a28/results/a28/exact_states/" + case + ".npz"
        ah, eh = headers(anatomy), headers(exact)
        require("CNN_CENTERED_DATA_ONLY_chi" in ah and shape_is(eh, "chi", (1, 576), np.complex128) and
                shape_is(eh, "mass", (1, 1152), np.float64) and {"lu", "pivots", "current", "field", "data"}.issubset(eh),
                "PAID_A28_CACHE_HEADERS", case)
        am, em = metadata(anatomy, {"case_id"}), metadata(exact, {"cache_protocol"})
        require(str(am["case_id"].item()) == case and str(em["cache_protocol"].item()) == "A28-EXACT-STATE-v1", "PAID_CACHE_METADATA", case)
    checkpoint = TARGET / "inputs/a26/results/a26/learning/261009/N3/best.pt"
    require(checkpoint.is_file() and not checkpoint.is_symlink(), "FROZEN_N3_CHECKPOINT_PRESENT")
    source = {name: {"bytes": (TARGET / "src/a26" / name).stat().st_size,
                     "pinned_commit": "5d5e31fcfc56ac8ef9d64c46b4b7bbdedef96bb4"}
              for name in ("metrics.py", "__init__.py")}
    return {"status": "PASS_METADATA_AND_RELEASE_ACQUISITION", "extraction": extraction,
            "source": source, "train": train_summary, "exposed_development": dev_summary,
            "E0_case_ids": list(CASES), "E0_parent_ids": list(PARENTS), "complex_parents": 12, "smooth_parents": 4,
            "pools": {"count": len(pool_rows), "min_candidates": min(x["pool_count"] for x in pool_rows),
                      "max_candidates": max(x["pool_count"] for x in pool_rows), "small_count": 12},
            "offline_target_headers": target_headers, "coverage_csv_columns": coverage_columns,
            "background_headers": background_headers, "frozen_checkpoint": "present; unopened",
            "historical_paid_caches": "32 present; headers/protocol metadata only; no cache equations or material matching computed",
            "boundary": {"locked_payload_reads": 0, "development_truth_values_read": 0, "TRAIN_label_values_read": 0,
                         "physics_calls": 0, "training_updates": 0, "material_scores_computed": 0,
                         "scope": "Release size/path/split/identity/shape audit; no numerical evidence claim"},
            "missing": [], "issues": issues, "SHA256_checks": "NOT_RUN_BY_USER_POLICY"}

try:
    result = audit_all()
except Exception as exc:
    result = {"status": "FAIL", "error": str(exc), "traceback": traceback.format_exc(), "issues": issues,
              "locked_payload_reads": 0, "physics_calls": 0, "training_updates": 0,
              "material_scores_computed": 0}
finally:
    write_json(OUT / "ARRAY_HEADERS.json", header_records)
    write_json(OUT / "METADATA_READS.json", metadata_reads)
    write_json(OUT / "AUDIT_CHECKS.json", checks)
    write_csv(OUT / "ZIP_ENTRIES.csv", zip_records)
    result["timing"] = {"wall_seconds": time.perf_counter() - WALL0,
                        "process_cpu_seconds": time.process_time(), "nested_not_extra_charge": True,
                        "GPU_seconds": 0, "finished_utc": now()}
    write_json(OUT / "INPUT_AUDIT.json", result)
    print(json.dumps({"status": result["status"], "issues": result.get("issues", []), "timing": result["timing"]}, indent=2))
if result["status"] == "FAIL":
    raise SystemExit(2)
