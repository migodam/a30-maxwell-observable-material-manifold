# A30 frozen backend adapter

Scope: reusable E1 adapter implementation only. This worker has executed no real Maxwell state, 8x8 Maxwell fixture, TRAIN/development scoring, training, CUDA job, or remote job. The arithmetic suite uses seeded nongeometric 4x4 and 5x5 complex matrices. It does not establish an E0/E1 scientific gate.

`src/a30/physics.py` exports `FrozenMaxwellAdapter` (alias `MaxwellAdapter`) and `AnchorState`. It imports an exact byte copy of A29 commit `5d5e31fcfc56ac8ef9d64c46b4b7bbdedef96bb4`. The default fresh-state path is unchanged `a24.Physics2D.full_state`; an adapter initializes its saved G, S, incident, and dimensions without calling `Physics2D.__init__` or the A2 geometry/Green builder. Optional existing Torch CPU/CUDA uses unchanged `a27.ExactMaxwell` and the saved-array matrix actions from `a25.TorchReference`, with no background factorization. There is no changed Green model, pseudoinverse, jitter, new daemon, or CUDA installation.

Construction:

```python
adapter = FrozenMaxwellAdapter.from_background_npz(
    background_path, book,
    allowed_cache_paths=[paid_n3_cache_path],
    device="cpu",                 # optional existing device="cuda:0"
)
```

The background path must be an explicit `background/weak.npz` or `background/ring.npz`. The constructor reads only registered saved-background keys, checks complex128, 24x24, mass volume 1/576, fixed geometry/aperture order, known material, and saved equation identities. It does not search any data directory. The parent must whitelist cache paths from authenticated already-paid A28/N3 inputs. The historical cache lacks its own payment receipt/source-commit field, so file whitelisting is an upstream provenance responsibility, not a claim that the adapter can independently prove payment from its contents.

Interfaces:

| Method | Output / accounting |
| --- | --- |
| `full_state(chi, purpose="endpoint")` | `AnchorState`; every attempted evaluation reserves a state before matrix/LU construction, then s RHS before the forward solve. Repeated identical material is still a new paid invocation. |
| `cached_anchor(chi, path)` | Read-only exact same-mass state; 0 new state calls, s new RHS for saved-LU audit. Missing, unlisted, stale, corrupt, wrong-background, or wrong-precision input raises. It never builds a replacement cache. |
| `L_response(chi)` | Complex (q,s), saved known-background affine response `yb + Db @ ((chi-chi_b)*eb)`; 0 LU RHS. |
| `anchor_jvp(dchi, state)` | Eq. (1), raw complex-material direction: (q,s), or (q,s,k) for k columns; s*k new LU RHS. |
| `solve_anchor(rhs, state, adjoint=False, role="certificate")` | Apply existing same-state LU or its conjugate adjoint; reserve each complex column before solving. Audit the backward residual against 1e-10. |
| `receiver_transfer(state)` | Read-only `S L_chi^-1`; q new adjoint RHS on first construction, cached thereafter. |
| `cached_material_dot_identity(dchi, load, state)` | Real adjoint dot agreement in raw material and fixed mass coordinates; saved field and receiver-transfer application only. Creates receiver transfer if absent, with its q RHS. |

Fresh states and cache audits preserve the scalar contrast law and real material box [-0.5,4], imaginary [0,0.5] with numerical tolerance 1e-10. The box acts on actual chi; a candidate-background increment may have negative imaginary part. State and background public arrays have immutable backing bytes. Foreign states are rejected. Tensor computation exports complex128 NumPy layouts; any transfer cost belongs to the measured call.

The A28 cache contains packed Torch/LAPACK LU and one-based successive pivot swaps. SciPy uses the same packed LU and zero-based swaps: `scipy_pivots = torch_pivots - 1`, with bounds and integer-type checks. The test suite verifies both forward and conjugate-adjoint solves with an actual Torch LU of a pivoted synthetic 4x4 matrix. No real cache is used to establish this conversion. Cache audits subsequently test each admitted saved factor with its original source RHS.

`book.reserve_rhs` means actual LU-solve columns. Matrix-only saved L, field, data, and receiver-transfer reuse are separately counted by `span`/`counts` and remain timed; they introduce no fresh LU RHS. Failed/repeated solves retain reservations. The parent owns E0/E1 authorization, material/chart generation, compensation, uniform bounds and certificate gates, statistics, scientific interpretation, and publication.

Vendor source and optional dependencies are self-contained under `vendor/frozen_a29/`; no source path outside the A30 package is needed at runtime. `PROVENANCE.json` records the required source commit, selected file paths, and exact byte copies. No file digests were computed or recorded. Runtime rejects conflicting preloaded A20/A24/A25/A27 modules so that an installed or adjacent unfrozen module cannot silently replace the vendored source.

Verification entry: `tests/test_a30_physics_arithmetic.py`, standard-library unittest. Execute only through the parent's `tools/a30_job.py` accounted launcher. Test status is recorded in `TEST_SUMMARY.json` after completion; optional CUDA/RTX4060 performance and real Maxwell consistency remain NOT_RUN.
