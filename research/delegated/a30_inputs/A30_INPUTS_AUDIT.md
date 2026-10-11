# A30 E0 release acquisition and metadata audit

Status: **PASS_METADATA_AND_RELEASE_ACQUISITION**. This resolves the release-availability problem described in the A30 package. It supplies inputs for the parent's guarded offline analysis; it makes no new material-quality or scientific-gate claim.

## Source and acquisition

The local read-only A29 repository HEAD and the public `a29-v0.1.0` tag both resolve to `5d5e31fcfc56ac8ef9d64c46b4b7bbdedef96bb4`. GitHub release metadata also records that commit as `targetCommitish`. The local A29 checkout's `origin` points to the older A24 repository, so every network command used the explicit A29 repository name.

Source: [A29 release](https://github.com/migodam/a29-material-hypothesis-coverage/releases/tag/a29-v0.1.0). The two public assets were acquired through `gh release download`, each on its first attempt. `RELEASE_METADATA.json`, `ACQUISITION.json`, and `TRANSPORT_COST_LEDGER.jsonl` preserve asset URLs, byte sizes, pinned refs, commands, timestamps, actual wall times and process CPU times. No SHA256 checks were run.

| Asset | Downloaded bytes | Expected GitHub bytes | Attempts | Download wall s | Download process CPU s |
|---|---:|---:|---:|---:|---:|
| A29_RAW_EVIDENCE.zip | 13,502,709 | 13,502,709 | 1 | 3.668161 | 0.182289 |
| A29_REPRO_INPUTS.zip | 283,117,157 | 283,117,157 | 1 | 31.078290 | 1.312849 |

The archive files are under `inputs/releases/`. Both were inspected before extraction. Their 337 entries contain 309,839,716 uncompressed bytes, with no traversal, absolute path, drive path, symlink, special entry, encrypted entry, duplicate destination or locked-path entry. `ZIP_ENTRIES.csv` preserves the entry inventory. Extraction preserved the archive-relative paths and did not overwrite existing files.

The root to pass to the supplied A29.1 guard is:

```text
/Volumes/migodam's-external-brain/Research/Inv_SLAM/Gaussian/A30/a30-maxwell-material-manifold/inputs/a29_release
```

Important paths relative to that root:

```text
results/a29/OFFLINE_TARGETS.npz
results/a29/COVERAGE_CASES.csv
results/a29/pools/<32 frozen case ids>.npz
results/a29/pools/<32 frozen case ids>.json
results/a29/TRAIN_TEMPLATES.npz
src/a26/metrics.py
src/a26/__init__.py
inputs/a25/train.npz
inputs/a25/validation.npz
inputs/a25/manifest.json
inputs/a25/geometry.json
inputs/a25/background/{weak,ring}.npz
inputs/a26/results/a26/evaluation/261009/PREDICTIONS.npz
inputs/a26/results/a26/learning/261009/N3/best.pt
inputs/a28/results/a28/anatomy/<32 frozen case ids>.npz
inputs/a28/results/a28/exact_states/<32 frozen case ids>.npz
```

`metrics.py` and `__init__.py` were acquired with `git show` at the exact pinned A29 commit rather than copying the working-tree versions. No project source or configuration was modified. The checkpoint is present and was not deserialized.

## Metadata and fields

TRAIN has exactly 64 parents, `250001–250064`, with eight original conditions per parent: 512 rows. Development is the already-exposed 16-parent set, `250065–250080`, also with eight conditions per parent: 128 rows. Split roles, family blocks, case IDs, variant IDs, backgrounds, amplitudes, noise metadata, manifest identity and geometry identity match the frozen rules. The portable public manifest contains only these 80 parents and the train/validation splits.

The E0 whitelist contains exactly 32 cases: `p<250065–250080>_<weak|ring>_a1_snr20`. The targets, coverage CSV identities, 32 pool files and 32 pool provenance files align. Families contain four parents each; shell, asymmetric_piecewise and mixed_scale provide 12 complex parents, while smooth provides four parents.

| Archive | Main fields and shapes | dtype |
|---|---|---|
| TRAIN | `chi (512,576)`, `data (512,32,8)` | complex128 |
| Development | `chi (128,576)`, `data (128,32,8)` | complex128 |
| OFFLINE_TARGETS | `truth`, `N3`, `background`, each `(32,576)`; case/parent/family/background metadata `(32,)` | complex128 material; int64 parents; Unicode identity strings |
| Each pool | `chi (n,576)`, `L (n,32,8)`, `observation (32,8)`, `n3 (576,)`, `background (576,)`; ids/categories/penalty/prior `(n,)`; small indices `(12,)`; scalar sigma | complex128 material/response; numeric or Unicode metadata |
| N3 prediction archive | `N3`, `COMMON_BP_INITIAL`, each `(128,576)`; development metadata aligned | complex128 material |
| Known backgrounds | `chi_b (576,)`, `J (512,1152)` | complex128 chi_b; float64 J |
| Paid exact-state caches | `chi (1,576)`, `mass (1,1152)`; lu/pivots/current/field/data present | complex128 chi; float64 mass |

The 32 full pools contain 58–91 candidates, below the cap of 256. Every small pool has 12 distinct in-range indices and includes candidate zero. Pool candidate IDs are distinct and saved provenance records `truth_access=false`.

`POOL_AUDIT.csv` gives per-case counts and shapes. `ARRAY_HEADERS.json` records every inspected NPZ field header. No object/pickle array was accepted. `METADATA_READS.json` records the identity and condition fields actually loaded. The paid A28 cache protocol metadata agrees with `A28-EXACT-STATE-v1`; cache equations and material equality were not evaluated here.

## Boundaries and missing evidence

No required release input is missing at the metadata/shape level. Development truth, TRAIN chi labels, current arrays and clean-response arrays were not loaded as numerical values. Their headers were inspected. No new label, physics call, training update, material score, cache-equation check or morphology score was computed. Locked payload reads remain zero. All scientific decisions remain with the parent.

The input audit does not establish finiteness or numerical agreement of material arrays. Those belong to the guarded offline scoring and any separately authorized cache audit. The current cohort remains exposed development; obtaining the release does not turn it into a blind holdout.

## Resource record

The seven acquisition commands consumed 36.020962 seconds of measured native wall time and 1.637551 seconds of measured parent-plus-child process CPU time. The timestamp span of the acquisition runner was 36.027470 seconds. Process CPU between acquisition command spans and Python startup was not measured; the ledger states that coverage explicitly.

The safe-extraction and metadata-audit runner consumed 1.063531 seconds wall and 0.407959 seconds inclusive parent-plus-child process CPU. Its internal timing is nested evidence and is not charged again. Charging `max(wall, process CPU)` once per outer category gives **37.091001 CPU-charged seconds** for the recorded acquisition and audit work, with GPU time and Maxwell state calls both zero. Interactive file review, preparatory probes and assistant work are outside these native timing spans and should remain visible in the parent's orchestration accounting.

`COST_LEDGER.jsonl` and `COST_SUMMARY.json` identify the two chargeable outer categories and the nested records that must not be added again. There were no network download failures or retries. Three resolved preparatory probe failures are retained in `PREPARATION_FAILURES.json`; they involved missing NumPy in system Python, shell path quoting, and checking Git status at the non-repository Inv_SLAM root. Existing `Gaussian/.venv_nn` supplied NumPy 2.5.3 without installation or environment changes.
