"""Synthetic mechanical checks only; these never load development payloads."""
from __future__ import annotations

import inspect
import unittest

import numpy as np

from a30 import representations as r


def synthetic_train() -> np.ndarray:
    rng = np.random.default_rng(301011)
    train = np.zeros((64, 24, 24), dtype=np.complex128)
    field = np.tile(np.repeat([0.7, 1.3, 1.9], 4), (10, 1))
    for parent in range(64):
        amplitude = field + 0.004 * rng.normal(size=(10, 12))
        train[parent, 7:17, 6:18] = amplitude * (1 + 0.05j)
    return train.reshape(64, 576)


class RepresentationsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.train = synthetic_train()
        cls.model = r.prepare_train(cls.train)
        cls.background = np.full(576, 0.1 + 0.04j)

    def test_haar_24_orthogonality_and_real_imag_tail(self):
        analysis, metadata = r.haar24_transform()
        self.assertEqual(analysis.shape, (576, 576))
        np.testing.assert_allclose(analysis @ analysis.T, np.eye(576), atol=2e-15)
        self.assertEqual({entry["size"] for entry in metadata}, {3, 6, 12, 24})
        self.assertEqual(sum(entry["kind"] == "coarse_dct" for entry in metadata), 9)
        rng = np.random.default_rng(4)
        delta = rng.normal(size=576) + 1j * rng.normal(size=576)
        tail = r.offline_best_s_tail(self.model, self.background + delta, self.background, 16)
        coefficients = np.r_[analysis @ (delta.real / 24), analysis @ (delta.imag / 24)]
        support = np.argsort(-np.abs(coefficients), kind="stable")[:16]
        basis = r._sparse_basis(self.model, support)
        reconstructed = basis @ coefficients[support]
        error = np.sum(self.model.real_weights * (r._real(delta) - reconstructed) ** 2)
        self.assertAlmostEqual(error, tail["fixed_mass_squared_tail"], places=13)
        self.assertFalse(tail["online_candidate"])
        self.assertEqual(len(tail["truth_selected_support"]), 16)

    def test_train_rank_and_readonly_frozen_parameters(self):
        self.assertEqual(self.model.single_rank, 64)
        self.assertEqual(self.model.metadata["parents"], 64)
        self.assertEqual(self.model.metadata["centering"], "UNCENTERED")
        self.assertFalse(self.model.train_deltas.flags.writeable)
        for budget in r.BUDGETS:
            basis = self.model.single_basis[:, :budget]
            np.testing.assert_allclose(basis.T @ (self.model.real_weights[:, None] * basis),
                                       np.eye(budget), atol=2e-14)
            for method in ("atlas", "level_set"):
                eligible = [t.charts[method, budget] for t in self.model.templates
                            if t.charts[method, budget].eligible]
                self.assertTrue(eligible, (method, budget))
                for chart in eligible:
                    self.assertEqual(chart.intrinsic_rank, budget)
                    self.assertEqual(sum(chart.geometry_counts) + 6, budget)

    def test_freeze_is_target_free_and_exact_sparse_budget(self):
        self.assertNotIn("truth", inspect.signature(r.freeze_case).parameters)
        self.assertNotIn("truth", inspect.signature(r.prepare_train).parameters)
        for budget in r.BUDGETS:
            frozen = r.freeze_case(self.model, "sparse", budget, self.train[2],
                                   self.background, {"amplitude_scale": 1.2})
            self.assertEqual(len(frozen["starts"]), 8)
            self.assertEqual(frozen["starts"][0]["source"], "N3")
            for start in frozen["starts"]:
                self.assertEqual(len(start["support"]), budget)
                self.assertEqual(start["intrinsic_rank"], budget)
                basis = start["basis"]
                np.testing.assert_allclose(basis.T @ (self.model.real_weights[:, None] * basis),
                                           np.eye(budget), atol=2e-14)

    def test_geometry_analytic_derivative_and_pou_bound(self):
        template = next(t for t in self.model.templates if t.charts["atlas", 64].eligible)
        for method in ("atlas", "level_set"):
            chart = template.charts[method, 64]
            phases = len(template.masks)
            geometry = sum(chart.geometry_counts)
            params = np.r_[np.full(geometry, 0.03), np.arange(phases) * 0.3 + 0.8,
                           np.arange(phases) * 0.04 + 0.1]
            _, _, jac = r._geometry_decode(template, chart, params, True)
            for column in (0, geometry // 2, geometry, 63):
                plus, minus = params.copy(), params.copy()
                plus[column] += 1e-6
                minus[column] -= 1e-6
                a = r._geometry_decode(template, chart, plus)[0]
                b = r._geometry_decode(template, chart, minus)[0]
                finite = r._real((a - b) / 2e-6)
                np.testing.assert_allclose(jac[:, column], finite, rtol=2e-6, atol=2e-9)
            if method == "atlas":
                for basis in chart.basis:
                    self.assertTrue(np.all(basis >= 0))
                    np.testing.assert_allclose(basis.sum(axis=1), 1, atol=4e-16)
                    self.assertLessEqual(np.max(np.abs(basis @ np.full(basis.shape[1], 2))),
                                         2.000000000000001)

    def test_box_has_no_tolerance_and_ray_keeps_support(self):
        image = self.background.copy()
        image[0] = 4 + 0.1j
        self.assertTrue(r.box_feasibility(image)["feasible"])
        image[0] = np.nextafter(4.0, np.inf) + 0.1j
        self.assertFalse(r.box_feasibility(image)["feasible"])
        start = r.freeze_case(self.model, "sparse", 16, self.train[0], self.background)["starts"][0]
        params, repair = r._ray_repair(start["params"] * 100, start["basis"], self.background)
        repaired = self.background + r._complex(start["basis"] @ params)
        self.assertTrue(r.box_feasibility(repaired)["feasible"])
        self.assertTrue(repair["contracted"])
        np.testing.assert_allclose(params, start["params"] * 100 * repair["factor"])

    def test_convex_fixed_chart_unconstrained_certificate(self):
        params = np.zeros(16)
        params[0] = 0.03
        basis = self.model.single_basis[:, :16]
        delta = r._complex(basis @ params)
        target = self.background + 1.2 * delta
        result = r.fit_capacity(self.model, "single_chart", 16, delta,
                                self.background, target,
                                {"amplitude_scale": 1.2, "max_starts": 2})
        self.assertTrue(result["box"]["feasible"])
        self.assertLess(result["losses"]["delta_nrmse"], 1e-12)
        self.assertTrue(result["certificate"]["certified"])
        self.assertEqual(result["dimensions"]["feasible_affine_dimension"], 16)
        self.assertTrue(all(fit["iterations"] <= 100 for fit in result["fits"]))

    def test_convex_bound_active_solution_and_kkt(self):
        # An orthogonal chart with a +- two-pixel coordinate cannot reproduce
        # both legal target extrema; its unconstrained projection is illegal.
        basis = np.zeros((1152, 16))
        basis[0, 0], basis[1, 0] = 24 / np.sqrt(2), -24 / np.sqrt(2)
        for column in range(1, 16):
            basis[column + 1, column] = 24
        target = self.background.copy()
        target[0], target[1] = 4 + 0.04j, -0.5 + 0.04j
        frozen = {"settings": r._configuration(None), "background": self.background}
        start = {"id": 0, "basis": basis, "params": np.zeros(16)}
        fit = r._qp_fit(self.model, frozen, start, target)
        self.assertTrue(fit["box"]["feasible"])
        self.assertAlmostEqual(fit["image"][0].real, 0.7, places=12)
        self.assertAlmostEqual(fit["image"][1].real, -0.5, places=12)
        self.assertTrue(fit["certificate"]["certified"], fit["certificate"])
        self.assertLessEqual(fit["iterations"], 100)
        self.assertEqual(fit["optimizer"], "PRIMAL_ACTIVE_SET_CONVEX_QP_NO_FALLBACK")

    def test_zero_imaginary_dc_corner_reports_reduced_dimension(self):
        # No imaginary DC: nonnegative zero-mean imaginary material must be zero.
        support = np.array([0, 1] + list(range(576 + 9, 576 + 23)))
        basis = r._sparse_basis(self.model, support)
        dimension = r._box_dimension(basis, np.full(576, 0.1 + 0j), self.model.real_weights)
        self.assertEqual(dimension["unconstrained_material_rank"], 16)
        self.assertEqual(dimension["feasible_affine_dimension"], 2)
        self.assertFalse(dimension["zero_delta_actual_box_strict_interior"])

    def test_atlas_primary_preserves_digital_topology(self):
        delta = self.train[0]
        target = self.background + 1.2 * delta
        result = r.fit_capacity(self.model, "atlas", 16, delta, self.background, target,
                                {"amplitude_scale": 1.2, "max_starts": 1, "max_iterations": 5})
        self.assertEqual(result["status"], "ACHIEVED_OFFLINE_FIT")
        self.assertTrue(result["primary_topology_preserved"])
        self.assertTrue(result["box"]["feasible"])
        self.assertEqual(result["global_vs_local"], "ACHIEVED_LOCAL_NONCONVEX_UPPER_BOUND")
        self.assertFalse(result["certificate"]["certified"])
        for entry in result["trajectory"]:
            if entry["accepted_for_primary"]:
                self.assertTrue(entry["topology_preserved"])
                self.assertTrue(entry["box_feasible"])

    def test_svd_rank_deficiency_and_iteration_hard_limits(self):
        deficient = r.prepare_train(np.tile(self.train[0], (64, 1)))
        self.assertEqual(deficient.single_rank, 1)
        frozen = r.freeze_case(deficient, "single_chart", 64, self.train[0], self.background)
        self.assertTrue(all(not start["eligible"] for start in frozen["starts"]))
        for invalid in ({"max_iterations": 101}, {"max_starts": 9}):
            with self.assertRaises(ValueError):
                r.freeze_case(self.model, "sparse", 16, self.train[0], self.background, invalid)
        with self.assertRaises(ValueError):
            r.prepare_train(np.tile(self.train[0], (128, 1)))


if __name__ == "__main__":
    unittest.main()
