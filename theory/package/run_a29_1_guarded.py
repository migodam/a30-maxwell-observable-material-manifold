#!/usr/bin/env python3
"""Guard the supplied A29.1 zero-physics audit against partial-pool statistics.
Usage: python run_a29_1_guarded.py --root /path/to/a29 --out /path/to/results
Only saved, exposed-development NPZ/CSV inputs are accepted.
"""
from __future__ import annotations
import argparse
import importlib.util
import json
import time
from pathlib import Path
import numpy as np

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--root',required=True,type=Path)
    p.add_argument('--out',required=True,type=Path)
    a=p.parse_args(); root=a.root.resolve(); out=a.out.resolve(); out.mkdir(parents=True,exist_ok=True)
    tic=time.perf_counter(); cpu=time.process_time()
    status={'status':'NOT_RUN','new_Maxwell_states':0,'network_training':False,'locked_evaluation':False,
            'expected_conditions':32,'expected_independent_parents':16,
            'expected_complex_independent_parents':12}
    required=[root/'results/a29/OFFLINE_TARGETS.npz',root/'results/a29/COVERAGE_CASES.csv']
    missing=[str(x) for x in required if not x.is_file()]
    if missing:
        status.update(status='FULL_A29_1_NOT_RUN_MISSING_RAW_INPUTS',missing=missing)
        status.update(wall_seconds=time.perf_counter()-tic,cpu_seconds=time.process_time()-cpu)
        (out/'A29_1_EXECUTION_STATUS.json').write_text(json.dumps(status,indent=2))
        print(json.dumps(status,indent=2)); return 2
    with np.load(required[0],allow_pickle=False) as z:
        targets={k:z[k].copy() for k in z.files}
    ids=[str(x) for x in targets['case_id']]
    parents=np.asarray(targets['parent_id'],int)
    backgrounds=[str(x) for x in targets['background_id']]
    if len(ids)!=32 or len(set(ids))!=32 or set(parents)!=set(range(250065,250081)):
        raise ValueError('Exactly the frozen 32 exposed cases and 16 parents are required; partial results are not campaign statistics.')
    for pid in range(250065,250081):
        ix=np.flatnonzero(parents==pid)
        if len(ix)!=2 or {backgrounds[j] for j in ix}!={'weak','ring'}:
            raise ValueError('Each parent must contain exactly weak and ring conditions.')
    for key in ['truth','background','N3']:
        if targets[key].shape[0]!=32 or targets[key].size!=32*576 or not np.isfinite(targets[key]).all():
            raise ValueError('Expected finite 32 x 576 saved full-grid materials: '+key)
    for case in ids:
        path=root/'results/a29/pools'/f'{case}.npz'
        with np.load(path,allow_pickle=False) as z:
            chi=z['chi']; small=np.asarray(z['small_indices'],int)
            if chi.ndim!=2 or chi.shape[1]!=576 or not np.isfinite(chi).all():
                raise ValueError('Invalid saved pool '+case)
            if len(small)!=12 or len(set(small))!=12 or 0 not in small or np.any(small<0) or np.any(small>=len(chi)):
                raise ValueError('Expected unique frozen 12-candidate small pool '+case)
            if float(np.asarray(z['sigma']).item())<=0:
                raise ValueError('The saved noisy likelihood must have positive sigma.')
    import sys
    sys.path.insert(0,str(root/'src'))
    spec=importlib.util.spec_from_file_location('provided_a29_1',Path(__file__).with_name('a29_1_convex_diagnostic.py'))
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    module.self_test(); module.run(root,out)
    import csv
    rows=list(csv.DictReader((out/'A29_1_CASES.csv').open()))
    certificates=[]
    for row in rows:
        for pool in ['full','small']:
            e=float(row[f'{pool}_convex_oracle_nrmse'])
            gap=float(row[f'{pool}_oracle_dual_gap'])
            if not np.isfinite(gap) or gap < -1e-12:
                raise ValueError('Invalid floating-point simplex gap')
            gap=max(0.,gap)
            lo=float(np.sqrt(max(0,e*e-2*gap)))
            certificates.append({'case_id':row['case_id'],'pool':pool,'achieved_error':e,
                'optimal_error_lower_bound':lo,'optimal_error_upper_bound':e,
                'error_interval_width':e-lo,'simplex_dual_gap':gap,
                'gap_pass':gap<=1e-8})
    status.update(status='COMPLETED_NUMERICALLY_CERTIFIED' if all(c['gap_pass'] for c in certificates) else 'COMPLETED_WITH_UNCERTIFIED_ORACLES',
                  observed_conditions=len(rows),certificates=certificates,
                  interpretation='Floating-point KKT/FW certificates, not interval-arithmetic proofs. Only offline capacity and data-dependent L weighted estimators; not calibrated posterior or F selection.',
                  wall_seconds=time.perf_counter()-tic,cpu_seconds=time.process_time()-cpu)
    (out/'A29_1_EXECUTION_STATUS.json').write_text(json.dumps(status,indent=2))
    print(status['status'])
    return 0 if status['status']=='COMPLETED_NUMERICALLY_CERTIFIED' else 3

if __name__=='__main__':
    raise SystemExit(main())
