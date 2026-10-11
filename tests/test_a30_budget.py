import json, tempfile, unittest
from pathlib import Path
from a30.budget import Book,BudgetStop,physical_totals


class BudgetTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        (self.root/'results/a30').mkdir(parents=True)
    def tearDown(self):self.tmp.cleanup()
    def gate(self):
        (self.root/'results/a30/E0_GATE.json').write_text(json.dumps({'status':'PASS'}))
    def test_e0_no_fixture(self):
        with self.assertRaises(BudgetStop):Book(self.root,stage='e0').reserve_state(resolution=8)
    def test_tests_no_fixture(self):
        with self.assertRaises(BudgetStop):Book(self.root,stage='tests').reserve_state(resolution=8)
    def test_gate_required(self):
        with self.assertRaises(BudgetStop):Book(self.root,stage='e1').reserve_state()
    def test_same_material_and_all_resolutions_paid(self):
        self.gate();b=Book(self.root,stage='e1',state_limit=3)
        b.reserve_state(resolution=8);b.reserve_state(resolution=24);b.reserve_state(resolution=24)
        with self.assertRaises(BudgetStop):b.reserve_state(resolution=8)
        self.assertEqual(physical_totals(self.root)['material_state_evaluations'],3)
    def test_unified_across_jobs(self):
        self.gate();Book(self.root,stage='e1',state_limit=2).reserve_state()
        b=Book(self.root,stage='e1',state_limit=2);b.reserve_state()
        with self.assertRaises(BudgetStop):b.reserve_state()
    def test_rhs_retries_paid(self):
        self.gate();b=Book(self.root,stage='e1',rhs_limit=16)
        b.reserve_rhs(8,'forward');b.reserve_rhs(8,'failed-forward-retry')
        with self.assertRaises(BudgetStop):b.reserve_rhs(1)
    def test_cap_cannot_expand(self):
        with self.assertRaises(ValueError):Book(self.root,stage='e1',state_limit=193)
    def test_e2_forbidden(self):
        with self.assertRaises(ValueError):Book(self.root,stage='e2')


if __name__=='__main__':unittest.main()
