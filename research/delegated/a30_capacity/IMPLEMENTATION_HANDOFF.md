# A30 capacity implementation handoff

Status: implementation ready; synthetic mechanical checks passed. Development capacity fitting and scientific gates are NOT_RUN by this worker and belong to parent Codex. No physics calls, neural training, development-label file reads, locked payload access, installs, hashes, backups, or probes were performed.

Owned outputs:

- `src/a30/representations.py`
- `tests/test_a30_representations.py`
- `research/delegated/a30_capacity/design_summary.json` (parent-reviewed design before development scoring)
- `research/delegated/a30_capacity/SYNTHETIC_TEST_RECEIPT.json`

Use the existing A25 `.venv_a25` and `PYTHONPATH=src`. NumPy 2.5.3 and SciPy 1.18.1 are already available. Tests use the standard-library unittest runner; pytest is not installed or required.

## API

`prepare_train(train_deltas, *, cell_weights=None)` accepts exactly 64 independent-parent normalized complex increment vectors of length 576 and returns a frozen dataclass model. Default fixed mass weights are 1/576 per cell, counted once in each real and imaginary channel. Model metadata includes uncentered TRAIN SVD rank, per-template phase partition, digital topology, bias, and each method/budget's parameter counts/rank/eligibility.

`freeze_case(model, method, budget, baseline_delta, background, config)` is target-free. Methods are `atlas`, `level_set`, `sparse`, `single_chart` (`pca` aliases the last). The output contains the eight or fewer fixed N3/TRAIN source choices, geometry template selections, sparse supports, initial parameters, bounds and reasons for ineligibility. All returned basis and source arrays are read-only.

`fit_capacity(model, method, budget, baseline_delta, background, truth, config)` is explicitly OFFLINE. TRAIN and baseline increments use normalized coordinates; background and truth are actual materials. The parent uses `amplitude_scale=1.2`. Accepted config fields include `max_starts` (1..8), `max_iterations` (1..100), and numerical `certificate_tolerance` (default 1e-8). This tolerance does not relax physical feasibility.

Main return keys: `status`, `scope`, `method`, `budget`, `real_intrinsic_budget`, `frozen_starts`, `fits`, `settings`, `selection_scope`, `image`, `delta`, `params`, `losses`, `box`, `certificate`, `dimensions`, `global_vs_local`, `trajectory`, `primary_topology_preserved`, and `cost`. Failed/ineligible fits keep their records and never produce a fabricated material. Sparse additionally supplies `offline_best_s_tail` and `fixed_support_box_vs_best_s_mse_gap`.

Loss fields are `delta_nrmse`, `fixed_mass_squared_error`, `real_squared_error`, `imag_squared_error`, and `target_delta_squared_norm`. The worker does not compute morphology, parent statistics or research gates.

Every per-start fit stores parameters and material loss along the trajectory, optimizer iteration/evaluation counts, its stopping status, best feasible iterate and strict actual-box comparisons. The top-level cost records wall seconds, CPU seconds, start count, total optimizer iterations, and zero physics calls. Parent persistence should retain all `fits`, including failed starts, and exclude dense bases from human-readable summary tables.

## Implementation details relevant to interpretation

1. Exact real budgets 16/32/64 include every geometry control and both independent real/imaginary regional contrast coordinates. Numerical rank-deficient charts are ineligible, never padded.
2. The atlas uses TRAIN normal-boundary Gaussian partition-of-unity controls, not a B-spline claim. The fixed 0.5-pixel softmax rasterization is an explicit mixture. The primary atlas image is the best exact-box-feasible iterate preserving the frozen TRAIN support/per-phase 4/8 digital signatures and phase adjacency. Zero-geometry smoothing changes make a chart ineligible. Other topology-changing iterates remain OFFLINE diagnostics.
3. Level-set uses low-frequency DCT signed-distance perturbations and may change topology. Both geometric methods report TRAIN phase quantization, rasterization bias, and the achieved soft-versus-hard material discrepancy. Neither establishes continuous reach/topology or global capacity.
4. Geometry uses a conservative common regional contrast box derived from known background extrema. Its eight-ULP inward guard is recorded; every returned actual image is still checked against Re[-0.5,4], Im[0,0.5] with zero feasibility tolerance.
5. Sparse uses the exact 24->12->6->3 Haar hierarchy, completed by an orthonormal 3x3 coarse DCT. Its actual top-s real-coordinate supports come only from N3/TRAIN. The separate truth-selected best-s coefficient tail is OFFLINE unconstrained capacity, produces no candidate image, and cannot be the actual frozen support.
6. Sparse and uncentered TRAIN SVD fits use a convex active-set QP with actual-material linear bounds. Any rounding repair contracts coefficients toward zero within the same support/chart; material pixels are never clipped. Basic primal/KKT numerical residuals and the fixed-chart error interval are diagnostic, not a new scientific gate or interval-arithmetic proof. There is no alternate optimizer fallback.
7. Nonconvex achieved fits are upper bounds on best chart error. Finite frozen chart/support selection is OFFLINE achieved capacity and does not validate online selection. Independent complex contrasts do not validate an independent-phase label distribution.
8. The zero-imaginary-background sparse corner reports reduced feasible dimension when a zero-mean imaginary channel is forced to zero. The parent's actual weak/ring backgrounds are strictly inside the imaginary box, so the frozen literal top-s rule is unchanged.

## Verification receipt

The 10 synthetic unittest checks passed in 0.932 s of reported test-run elapsed time. CPU time for that initial invocation was not measured. No extra test or certificate matrix was added after the latest user steering. Checks cover Haar/W orthogonality and tail reconstruction, exact real budget/rank, target-free freezes, analytic geometry gradients, exact material bounds, coefficient-ray support preservation, constrained QP KKT, atlas digital topology acceptance, and the zero-imaginary-background dimension corner. These are mechanical checks only, not empirical scientific validation.
