# A29.1 — Partial verified convex-hull check (2026-10-10)

## Evidence status

- Verified: A29 pinned GitHub source `5d5e31fcfc56ac8ef9d64c46b4b7bbdedef96bb4`, A29_DECISION, raw metric CSV and code.
- Computed: a **restricted** exact simplex-constrained complex-L2 convex hull of N3, full-pool best hard candidate, and 12-pool best hard candidate for **four** metadata-fixed weak-background sample cases, using pixel values in `results/a29/artifacts/fixed_material_comparators_plot_data.csv`.
- **Not computed**: 32-case full-pool and small-pool convex hull, because the actual all-candidate complex arrays are distributed in a separate Release ZIP, unavailable in this runtime. No Maxwell solves or neural training performed.
- Reproducible complete analysis script: `a29_1_convex_diagnostic.py`. Requires extracted GitHub Release `A29_RAW_EVIDENCE.zip` and the A29 repo environment.

## Restricted three-image complex material hull

| Pinned case | Hard improvement vs N3 | Convex improvement vs N3 | Additional convex improvement vs hard |
|---|---:|---:|---:|
| p250065_weak_a1_snr20 (shell) | 0.123513% | 0.123513% | 0.0000% |
| p250069_weak_a1_snr20 (asymmetric) | 0.507931% | 0.507931% | 0.0000% |
| p250073_weak_a1_snr20 (smooth) | 68.241369% | 74.467250% | 19.603746% |
| p250077_weak_a1_snr20 (mixed-scale) | 0.212275% | 0.212275% | 0.0000% |

The above are ratios of complex material L2 errors, sharing the same target/background in each row. Full and small hard candidate may coincide, thus the local hull may be degenerate. Smooth optimal weights: N3=0.09230967, full=0.68651488, small=0.22117546.

**No decision on complete A29.1 Gate may be claimed from these four cases.** A29 frozen NO-GO remains unchanged; A29 F-vs-calibrated-L decision remains NOT_RUN.

## How to complete A29.1 offline

1. Download/extract `A29_RAW_EVIDENCE.zip` from https://github.com/migodam/a29-material-hypothesis-coverage/releases/tag/a29-v0.1.0 into the project root.
2. Ensure `results/a29/OFFLINE_TARGETS.npz`, `results/a29/pools/*.npz`, `results/a29/COVERAGE_CASES.csv` exist.
3. Place `a29_1_convex_diagnostic.py` in project root or refer to its absolute path.
4. Run `python a29_1_convex_diagnostic.py --self-test` then `python a29_1_convex_diagnostic.py --root . --out results/a29_1`.
5. Review `results/a29_1/A29_1_DECISION.md`, `A29_1_CASES.csv`, `A29_1_WEIGHTS.json`, `A29_1_SUMMARY.json`; require low simplex dual gaps or explicitly mark uncertified entries.

Treat `L_mean` as a finite, data-dependent-bank weighted material estimate, **not** a calibrated Bayesian posterior. Any convex-hull oracle selects weights using withheld truth **offline only**, so it is an information-capacity diagnostic and not an online reconstruction algorithm. Pointwise material box/passivity may be preserved by convexity, but topology need not be preserved.
