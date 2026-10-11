"""Generic small-matrix arithmetic/accounting tests: zero Maxwell fixtures.

Fixtures are seeded nongeometric complex matrices of size 4 or 5.  The test
book records simulated reservations only; the production Book refuses real
physics in stage='tests'.  These checks make no scientific E0/E1 claim.
"""
from collections import Counter
from contextlib import contextmanager
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import numpy as np
import scipy.linalg as la

from a30 import physics
from a30.physics import FrozenMaxwellAdapter, NumericalFailure, torch_pivots_to_scipy


class SyntheticBudgetStop(RuntimeError):
    pass


class SyntheticBook:
    def __init__(self, *, state_limit=100, rhs_limit=1000):
        self.counts = Counter()
        self.events = []
        self.states = self.rhs = 0
        self.state_limit, self.rhs_limit = state_limit, rhs_limit

    def reserve_state(self, material, *, resolution, purpose):
        if self.states >= self.state_limit:
            raise SyntheticBudgetStop("SYNTHETIC_STATE_LIMIT")
        self.states += 1
        self.events.append(("state", resolution, purpose, np.shape(material)))

    def reserve_rhs(self, count, role):
        if self.rhs + count > self.rhs_limit:
            raise SyntheticBudgetStop("SYNTHETIC_RHS_LIMIT")
        self.rhs += count
        self.events.append(("rhs", count, role))

    @contextmanager
    def span(self, label, **counts):
        self.counts.update(counts)
        self.events.append(("span", label))
        yield


def synthetic_arrays(n=5, s=2, q=3, *, identity_green=False):
    rng = np.random.default_rng(301011)
    G = (np.eye(n, dtype=np.complex128) if identity_green else
         .025 * (rng.normal(size=(n, n)) + 1j * rng.normal(size=(n, n))))
    S = rng.normal(size=(q, n)) + 1j * rng.normal(size=(q, n))
    incident = rng.normal(size=(n, s)) + 1j * rng.normal(size=(n, s))
    chi_b = (np.zeros(n, dtype=np.complex128) if identity_green else
             rng.uniform(.1, .3, n) + 1j * rng.uniform(.02, .04, n))
    matrix = np.eye(n, dtype=np.complex128) - chi_b[:, None] * G
    current = np.linalg.solve(matrix, chi_b[:, None] * incident)
    return dict(chi_b=chi_b, eb=incident + G @ current, yb=S @ current,
                Db=np.linalg.solve(matrix.conj().T, S.conj().T).conj().T,
                G=G, S=S, incident=incident)


def material(n=5):
    return np.linspace(.2, .8, n) + 1j * np.linspace(.025, .09, n)


def cache_payload(adapter, state):
    mass = physics._contracts.mass_pack(state.chi, adapter.volume)[None]
    return dict(mass=mass, chi=state.chi[None], current=state.current[None],
                field=state.field[None], w=((state.chi - adapter.chi_b)[:, None] * state.field)[None],
                data=state.data[None], lu=state.factor[0][None],
                pivots=(state.factor[1] + 1)[None], residual=np.asarray([state.residual]),
                background=adapter.chi_b, cache_protocol=np.asarray("A28-EXACT-STATE-v1"))


class PhysicsArithmetic(unittest.TestCase):
    def adapter(self, *, arrays=None, book=None, paths=(), backend="scipy"):
        return FrozenMaxwellAdapter.for_synthetic_matrices(
            synthetic_arrays() if arrays is None else arrays,
            SyntheticBook() if book is None else book,
            volume=.25, allowed_cache_paths=paths, backend=backend)

    def assertNear(self, left, right, tolerance=1e-10):
        error = np.linalg.norm(np.asarray(left) - np.asarray(right)) / max(1., np.linalg.norm(right))
        self.assertLessEqual(error, tolerance)

    def test_frozen_cpu_path_and_no_geometry_constructor(self):
        with mock.patch.object(physics._cpu, "_vendor", side_effect=AssertionError("GEOMETRY_FORBIDDEN")):
            adapter = self.adapter()
            state = adapter.full_state(material())
        self.assertIs(physics._SavedPhysics2D.full_state, physics._cpu.Physics2D.full_state)
        self.assertIn("vendor/frozen_a29/src/a24/physics.py", physics._cpu.__file__)
        expected = np.linalg.solve(state.matrix, state.chi[:, None] * adapter.incident)
        self.assertNear(state.current, expected)
        self.assertNear(state.field, adapter.incident + adapter.G @ expected)
        self.assertNear(state.data, adapter.S @ expected)

    def test_state_and_rhs_reservations_precede_operations(self):
        book = SyntheticBook()
        adapter = self.adapter(book=book)
        book.events.clear()
        adapter.full_state(material())
        labels = [event[1] if event[0] == "span" else event[0] for event in book.events]
        self.assertLess(labels.index("state"), labels.index("full_material_assembly"))
        self.assertLess(labels.index("state"), labels.index("full_LU_factor"))
        self.assertLess(labels.index("rhs"), labels.index("full_forward_solve"))
        self.assertEqual((book.states, book.rhs), (1, adapter.s))

    def test_repeated_material_evaluations_are_each_paid(self):
        book = SyntheticBook()
        adapter = self.adapter(book=book)
        adapter.full_state(material(), purpose="first")
        adapter.full_state(material(), purpose="timing_repeat")
        self.assertEqual((book.states, book.rhs), (2, 2 * adapter.s))

    def test_state_limit_stops_before_matrix_or_lu(self):
        book = SyntheticBook(state_limit=0)
        adapter = self.adapter(book=book)
        book.events.clear()
        with mock.patch.object(physics._cpu.la, "lu_factor", side_effect=AssertionError("UNRESERVED_LU")):
            with self.assertRaises(SyntheticBudgetStop):
                adapter.full_state(material())
        self.assertEqual((book.states, book.rhs), (0, 0))
        self.assertFalse(any(event == ("span", "full_material_assembly") for event in book.events))

    def test_rhs_limit_stops_before_solve_and_state_stays_paid(self):
        book = SyntheticBook(rhs_limit=0)
        adapter = self.adapter(book=book)
        with mock.patch.object(physics._cpu.la, "lu_solve", side_effect=AssertionError("UNRESERVED_SOLVE")):
            with self.assertRaises(SyntheticBudgetStop):
                adapter.full_state(material())
        self.assertEqual((book.states, book.rhs), (1, 0))

    def test_singular_failure_has_no_jitter_or_pinv(self):
        book = SyntheticBook()
        adapter = self.adapter(arrays=synthetic_arrays(identity_green=True), book=book)
        with mock.patch.object(np.linalg, "pinv", side_effect=AssertionError("PINV_FORBIDDEN")):
            with self.assertRaises(NumericalFailure):
                adapter.full_state(np.ones(adapter.n, dtype=np.complex128))
        self.assertEqual(book.states, 1)
        self.assertEqual(book.rhs, 0)

    def test_physical_box_applies_to_material_not_background_difference(self):
        adapter = self.adapter()
        legal = material()
        legal[0] = -.5 + 0j
        legal[-1] = 4. + .5j
        self.assertEqual(adapter.full_state(legal).chi[0], -.5)
        self.assertTrue(np.any((legal - adapter.chi_b).imag < 0))
        for illegal in (-.500001 + .1j, 4.000001 + .1j, .1 - .000001j, .1 + .500001j):
            value = material()
            value[0] = illegal
            with self.assertRaises(NumericalFailure):
                adapter.full_state(value)

    def test_background_L_is_cached_and_affine(self):
        book = SyntheticBook()
        adapter = self.adapter(book=book)
        chi = material()
        expected = adapter.yb + adapter.Db @ ((chi - adapter.chi_b)[:, None] * adapter.eb)
        self.assertNear(adapter.L_response(chi), expected)
        self.assertNear(adapter.L_response(adapter.chi_b), adapter.yb)
        self.assertEqual((book.states, book.rhs), (0, 0))

    def test_forward_and_conjugate_adjoint_solve(self):
        book = SyntheticBook()
        adapter = self.adapter(book=book)
        state = adapter.full_state(material())
        rhs = adapter.incident[:, 0]
        self.assertNear(adapter.solve_anchor(rhs, state), np.linalg.solve(state.matrix, rhs))
        self.assertNear(adapter.solve_anchor(rhs, state, adjoint=True), np.linalg.solve(state.matrix.conj().T, rhs))
        self.assertEqual(book.rhs, adapter.s + 2)

    def test_anchor_jvp_multiple_raw_complex_directions(self):
        book = SyntheticBook()
        adapter = self.adapter(book=book)
        state = adapter.full_state(material())
        directions = np.column_stack((material() / 10, (1j * material()) / 15))
        value = adapter.anchor_jvp(directions, state)
        self.assertEqual(value.shape, (adapter.q, adapter.s, 2))
        for i in range(2):
            expected = adapter.S @ np.linalg.solve(state.matrix, directions[:, i, None] * state.field)
            self.assertNear(value[:, :, i], expected)
        self.assertEqual(book.rhs, adapter.s * 3)

    def test_finite_secant_and_remainder_identities(self):
        adapter = self.adapter()
        first = adapter.full_state(material())
        h = .025 * material()
        second = adapter.full_state(first.chi + h)
        secant = adapter.solve_anchor(h[:, None] * first.field, second, role="synthetic_secant")
        self.assertNear(second.current - first.current, secant)
        tangent_current = adapter.solve_anchor(h[:, None] * first.field, first, role="synthetic_tangent")
        remainder = adapter.S @ adapter.solve_anchor(
            h[:, None] * (adapter.G @ tangent_current), second, role="synthetic_remainder")
        self.assertNear(second.data - first.data - adapter.S @ tangent_current, remainder)

    def test_receiver_transfer_and_mass_dot_identity_reuse(self):
        book = SyntheticBook()
        adapter = self.adapter(book=book)
        state = adapter.full_state(material())
        transfer = adapter.receiver_transfer(state)
        self.assertNear(transfer @ state.matrix, adapter.S)
        self.assertEqual(book.rhs, adapter.s + adapter.q)
        load = np.arange(adapter.q * adapter.s).reshape(adapter.q, adapter.s) * (1. + .25j)
        identity = adapter.cached_material_dot_identity(.1j * material(), load, state)
        self.assertLess(identity["relative_error"], 1e-10)
        self.assertEqual(book.rhs, adapter.s + adapter.q)
        self.assertIs(adapter.receiver_transfer(state), transfer)
        self.assertFalse(transfer.flags.writeable)

    def test_saved_arrays_are_copied_and_read_only(self):
        arrays = synthetic_arrays()
        adapter = self.adapter(arrays=arrays)
        expected = adapter.G.copy()
        arrays["G"][:] = 999
        self.assertNear(adapter.G, expected)
        state = adapter.full_state(material())
        for array in (adapter.G, adapter.chi_b, state.chi, state.current, state.field,
                      state.data, state.matrix, state.factor[0], state.factor[1]):
            self.assertFalse(array.flags.writeable)
        with self.assertRaises(ValueError):
            state.field[0, 0] = 1

    def test_foreign_state_is_rejected(self):
        first = self.adapter()
        second = self.adapter()
        state = first.full_state(material())
        for action in (lambda: second.solve_anchor(second.incident, state),
                       lambda: second.anchor_jvp(material(), state),
                       lambda: second.receiver_transfer(state)):
            with self.assertRaises(ValueError):
                action()

    def test_paid_cache_has_zero_new_states_and_paid_lu_audit(self):
        with tempfile.TemporaryDirectory(prefix="a30_synthetic_cache_") as directory:
            path = Path(directory) / "paid.npz"
            producer = self.adapter()
            state = producer.full_state(material())
            np.savez(path, **cache_payload(producer, state))
            book = SyntheticBook()
            adapter = self.adapter(book=book, paths=(path,))
            with mock.patch.object(physics._cpu.la, "lu_factor", side_effect=AssertionError("CACHE_REFACTOR_FORBIDDEN")):
                cached = adapter.cached_anchor(material(), path)
            self.assertTrue(cached.cached)
            self.assertNear(cached.data, state.data)
            self.assertEqual((book.states, book.rhs), (0, adapter.s))

    def test_missing_stale_unlisted_cache_never_falls_back(self):
        with tempfile.TemporaryDirectory(prefix="a30_synthetic_cache_") as directory:
            path = Path(directory) / "paid.npz"
            book = SyntheticBook()
            adapter = self.adapter(book=book, paths=(path,))
            with self.assertRaises(FileNotFoundError):
                adapter.cached_anchor(material(), path)
            with self.assertRaises(ValueError):
                adapter.cached_anchor(material(), Path(directory) / "unlisted.npz")
            producer = self.adapter()
            payload = cache_payload(producer, producer.full_state(material()))
            payload["mass"] = payload["mass"].copy()
            payload["mass"][0, 0] += 1e-5
            np.savez(path, **payload)
            with self.assertRaises(ValueError):
                adapter.cached_anchor(material(), path)
            self.assertEqual((book.states, book.rhs), (0, 0))

    def test_corrupt_saved_lu_is_a_paid_failure(self):
        with tempfile.TemporaryDirectory(prefix="a30_synthetic_cache_") as directory:
            path = Path(directory) / "paid.npz"
            producer = self.adapter()
            payload = cache_payload(producer, producer.full_state(material()))
            payload["lu"] = payload["lu"].copy()
            payload["lu"][0, 0, 0] *= .75
            np.savez(path, **payload)
            book = SyntheticBook()
            adapter = self.adapter(book=book, paths=(path,))
            with self.assertRaises(NumericalFailure):
                adapter.cached_anchor(material(), path)
            self.assertEqual((book.states, book.rhs), (0, adapter.s))

    def test_invalid_pivots_and_label_paths_fail(self):
        for values in (np.array([0, 2, 3]), np.array([1, 1, 3]), np.array([1, 2, 4]), np.array([1., 2., 3.])):
            with self.assertRaises(ValueError):
                torch_pivots_to_scipy(values, 3)
        adapter = self.adapter()
        for path in ("/tmp/locked_ID/paid.npz", "/tmp/labels/paid.npz", "/tmp/oracle/paid.npz"):
            with self.assertRaises(ValueError):
                adapter.cached_anchor(material(), path)
        arrays = synthetic_arrays()
        arrays["truth"] = material()
        with self.assertRaises(ValueError):
            self.adapter(arrays=arrays)

    @unittest.skipUnless(importlib.util.find_spec("torch") is not None, "OPTIONAL_TORCH_UNAVAILABLE")
    def test_actual_torch_pivot_conversion_on_synthetic_matrix(self):
        import torch
        matrix = np.asarray([[.01 + .03j, 2., .2j, 1.], [3., .3j, 2., -.1j],
                             [1.j, 1., 4., .5], [2., -.1j, .5, 5.]], dtype=np.complex128)
        rhs = np.asarray([[1., 2.j], [3.j, 4.], [5., 6.j], [7.j, 8.]], dtype=np.complex128)
        tensor = torch.tensor(matrix)
        lu, pivots = torch.linalg.lu_factor(tensor)
        self.assertTrue(np.any(pivots.numpy() != np.arange(1, 5)))
        factor = (lu.numpy(), torch_pivots_to_scipy(pivots.numpy(), 4))
        for adjoint in (False, True):
            scipy_value = la.lu_solve(factor, rhs, trans=2 if adjoint else 0)
            torch_value = torch.linalg.lu_solve(lu, pivots, torch.tensor(rhs), adjoint=adjoint).numpy()
            self.assertNear(scipy_value, torch_value)
            self.assertNear((matrix.conj().T if adjoint else matrix) @ scipy_value, rhs)

    @unittest.skipUnless(importlib.util.find_spec("torch") is not None, "OPTIONAL_TORCH_UNAVAILABLE")
    def test_optional_frozen_torch_cpu_matches_scipy_and_counts(self):
        scipy_adapter = self.adapter()
        book = SyntheticBook()
        torch_adapter = self.adapter(book=book, backend="torch")
        first = scipy_adapter.full_state(material())
        second = torch_adapter.full_state(material())
        self.assertNear(first.data, second.data)
        self.assertNear(scipy_adapter.anchor_jvp(.1 * material(), first),
                        torch_adapter.anchor_jvp(.1 * material(), second))
        self.assertNear(torch_adapter.receiver_transfer(second) @ second.matrix, torch_adapter.S)
        self.assertEqual((book.states, book.rhs), (1, 2 * torch_adapter.s + torch_adapter.q))


if __name__ == "__main__":
    unittest.main(verbosity=2)
