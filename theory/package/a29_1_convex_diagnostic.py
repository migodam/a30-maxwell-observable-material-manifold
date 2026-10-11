#!/usr/bin/env python3
"""A29.1: Saved-pool material convexification audit. No Maxwell solves, no training.

Inputs: A29_RAW_EVIDENCE.zip extracted at --root, containing:
  results/a29/OFFLINE_TARGETS.npz
  results/a29/pools/<case_id>.npz
  results/a29/COVERAGE_CASES.csv
Optionally the complete GitHub repository under --root for original image metrics.

This is an OFFLINE ORACLE capacity test; no truth is used for candidate production,
physical likelihood model calibration, or deployment actions. It does not alter the
frozen A29 NO_GO gate.
"""
from __future__ import annotations
import argparse, csv, json, sys
from collections import defaultdict
from pathlib import Path
import numpy as np
from scipy.optimize import minimize


def balanced_prior(categories, penalty):
    cats=np.asarray(categories).astype(str)
    p=np.asarray(penalty,dtype=float)
    if cats.shape!=p.shape or not np.all(np.isfinite(p)):
        raise ValueError('Invalid category penalty input')
    out=np.zeros(len(cats))
    names=sorted(set(cats))
    for name in names:
        idx=np.flatnonzero(cats==name)
        z=np.exp(-(p[idx]-p[idx].min()))
        out[idx]=z/z.sum()/len(names)
    return out


def fit_convex_oracle(material,truth,denom, *, maxiter=900):
    """Convex quadratic least-squares with simplex KKT dual-gap certificate."""
    a=np.asarray(material,dtype=np.complex128)
    t=np.asarray(truth,dtype=np.complex128).reshape(-1)
    if a.ndim!=2 or a.shape[1]!=len(t):
        raise ValueError('Expected candidate-by-cell complex material array')
    den=float(denom)
    if den<=0:raise ValueError('Zero truth contrast norm')
    X=(a-a[0])/den
    target=(t-a[0])/den
    Q=np.real(X.conj()@X.T)
    Q=(Q+Q.T)*0.5
    q=np.real(X.conj()@target)
    constant=float(np.vdot(target,target).real)
    diagonal=np.real(np.einsum('kn,kn->k',X.conj(),X))
    errs=np.maximum(diagonal-2*q+constant,0.)
    hard=int(np.argmin(errs))
    start=np.zeros(len(a)); start[hard]=1.
    def loss(w):return float(0.5*(w@Q@w-2*q@w+constant))
    def grad(w):return Q@w-q
    constraints=[{'type':'eq','fun':lambda w:np.sum(w)-1.,'jac':lambda w:np.ones_like(w)}]
    res=minimize(loss,start,method='SLSQP',jac=grad,bounds=[(0.,1.)]*len(a),
                 constraints=constraints,options={'ftol':1.e-12,'maxiter':maxiter,'disp':False})
    w=np.clip(np.asarray(res.x,float),0.,None)
    if w.sum()<=0:w=start.copy()
    else:w=w/w.sum()
    # An optional conditional-gradient pass produces an explicit dual certificate.
    iterations=0
    for j in range(2000):
        g=grad(w); k=int(np.argmin(g)); gap=float(w@g-g[k])
        if gap<=1e-9:break
        direction=np.zeros(len(a));direction[k]=1.;direction-=w
        curvature=float(direction@Q@direction)
        if curvature<1.e-17:break
        alpha=float(np.clip(-g@direction/curvature,0.,1.))
        if alpha<1.e-13:break
        w=w+alpha*direction
        iterations=j+1
    g=grad(w);gap=max(0.,float(w@g-np.min(g)))
    image=w@a
    nrmse=float(np.linalg.norm(image-t)/den)
    hard_nrmse=float(np.linalg.norm(a[hard]-t)/den)
    return {'weights':w,'image':image,'nrmse':nrmse,'hard_nrmse':hard_nrmse,
            'hard_index':hard,'dual_gap':gap,'slsqp_success':bool(res.success),
            'slsqp_message':str(res.message),'slsqp_iters':int(res.nit),
            'conditional_gradient_iters':iterations,'support_count':int(np.sum(w>1e-6)),
            'max_weight':float(w.max())}


def actual_linear_decision(pool, selection, truth, den):
    ids=np.asarray(selection,dtype=int)
    chi=np.asarray(pool['chi'])[ids]
    resp=np.asarray(pool['L'])[ids]
    obs=np.asarray(pool['observation'])
    sig=float(np.asarray(pool['sigma']).item())
    prior=balanced_prior(np.asarray(pool['categories'])[ids],np.asarray(pool['penalty'])[ids])
    residual=np.sum(np.abs(resp-obs[None])**2,axis=tuple(range(1,resp.ndim)))/sig**2
    logp=np.log(prior)-residual
    w=np.exp(logp-logp.max());w/=w.sum()
    hard_idx=int(np.argmax(logp))
    mean=w@chi
    norm=lambda x:float(np.linalg.norm(x-truth)/den)
    return {'hard_nrmse':norm(chi[hard_idx]),'mean_nrmse':norm(mean),
            'hard_index':int(ids[hard_idx]),'ess':float(1/np.sum(w*w)),
            'max_weight':float(w.max()),'mean':mean,'weights':w,
            'noise_white_residual_mean':float(np.linalg.norm(np.tensordot(w,resp,axes=1)-obs)/sig)}


def pair_parent_boot(rows, field, family, *, samples=2000, seed=291011):
    group=[r for r in rows if r['family'] in family]
    parents=sorted(set(int(r['parent_id']) for r in group))
    values=[]
    for pid in parents:
        pair=[r for r in group if int(r['parent_id'])==pid]
        base=np.mean([float(r['N3_nrmse']) for r in pair])
        candidate=np.mean([float(r[field]) for r in pair])
        values.append((base-candidate)/base)
    x=np.asarray(values)
    if not len(x):return None
    rng=np.random.default_rng(seed)
    boots=x[rng.integers(0,len(x),size=(samples,len(x)))].mean(axis=1)
    return {'parent_count':len(parents),'mean_relative_gain':float(x.mean()),
            'median_relative_gain':float(np.median(x)),
            'ci95':[float(x) for x in np.quantile(boots,[.025,.975])],
            'parent_gains':[float(v) for v in x]}


def tojson(obj):
    if isinstance(obj,(np.floating,np.integer)):return obj.item()
    if isinstance(obj,np.ndarray):return obj.tolist()
    raise TypeError(type(obj).__name__)


def run(root,output):
    targets_path=root/'results/a29/OFFLINE_TARGETS.npz'
    if not targets_path.exists():raise FileNotFoundError(f'EXTRACT A29_RAW_EVIDENCE.zip FIRST: {targets_path}')
    with np.load(targets_path,allow_pickle=False) as z:targets={k:z[k].copy() for k in z.files}
    family_by_case={};reference_by_case={}
    metrics_path=root/'results/a29/COVERAGE_CASES.csv'
    with metrics_path.open() as f:
        for row in csv.DictReader(f):
            family_by_case[row['case_id']]=row['family']
            reference_by_case[row['case_id']]=row
    rows=[];weights=[]
    for i,case in enumerate(targets['case_id']):
        case=str(case);pfile=root/'results/a29/pools'/f'{case}.npz'
        if not pfile.exists():raise FileNotFoundError(pfile)
        with np.load(pfile,allow_pickle=False) as z:p={k:z[k].copy() for k in z.files}
        truth=np.asarray(targets['truth'][i],np.complex128).ravel()
        bg=np.asarray(targets['background'][i],np.complex128).ravel()
        den=float(np.linalg.norm(truth-bg))
        candidates=np.asarray(p['chi'],np.complex128)
        if not np.allclose(candidates[0],targets['N3'][i],rtol=0,atol=1e-12):
            raise ValueError('N3 baseline does not match saved targets for '+case)
        small=np.asarray(p['small_indices'],int)
        if 0 not in small:raise ValueError('No-op absent from small pool '+case)
        full_res=fit_convex_oracle(candidates,truth,den)
        small_res=fit_convex_oracle(candidates[small],truth,den)
        lin_f=actual_linear_decision(p,np.arange(len(candidates)),truth,den)
        lin_s=actual_linear_decision(p,small,truth,den)
        n3_nrmse=float(np.linalg.norm(candidates[0]-truth)/den)
        ref=reference_by_case[case]
        for label,computed,stored in [('N3',n3_nrmse,'N3_error'),
                                      ('full hard',full_res['hard_nrmse'],'full_pool_oracle'),
                                      ('small hard',small_res['hard_nrmse'],'small_pool_oracle')]:
            if abs(computed-float(ref[stored]))>2e-8:
                raise ValueError(f'A29 source metric mismatch: {case} {label}: {computed} vs {ref[stored]}')
        record={'case_id':case,'parent_id':int(targets['parent_id'][i]),
                'background_id':str(targets['background_id'][i]),
                'family':family_by_case[case], 'N3_nrmse':n3_nrmse,
                'full_hard_oracle_nrmse':full_res['hard_nrmse'],
                'small_hard_oracle_nrmse':small_res['hard_nrmse'],
                'full_convex_oracle_nrmse':full_res['nrmse'],
                'small_convex_oracle_nrmse':small_res['nrmse'],
                'full_L_MAP_nrmse':lin_f['hard_nrmse'],
                'small_L_MAP_nrmse':lin_s['hard_nrmse'],
                'full_L_mean_nrmse':lin_f['mean_nrmse'],
                'small_L_mean_nrmse':lin_s['mean_nrmse'],
                'full_L_ESS':lin_f['ess'],'small_L_ESS':lin_s['ess'],
                'full_oracle_dual_gap':full_res['dual_gap'],
                'small_oracle_dual_gap':small_res['dual_gap'],
                'full_oracle_active_weights':full_res['support_count'],
                'small_oracle_active_weights':small_res['support_count'],
                'full_solver_SLSQP_success':full_res['slsqp_success'],
                'small_solver_SLSQP_success':small_res['slsqp_success']}
        # For continuity with A29 use its exact morphology metric implementation.
        try:
            from a26.metrics import image_metrics
            for label,img in (('full_convex',full_res['image']),('small_convex',small_res['image']),
                              ('full_L_mean',lin_f['mean']),('small_L_mean',lin_s['mean'])):
                m=image_metrics(img,truth,bg)
                record[label+'_support_iou']=float(m['support_iou'])
                record[label+'_edge_f1']=float(m['edge_f1'])
        except ImportError:
            record['morphology_metrics']='NOT_AVAILABLE_RUN_INSIDE_A29_REPO_WITH_SRC_ON_PATH'
        rows.append(record)
        weights.append({'case_id':case,'full_oracle':full_res['weights'].tolist(),
                        'small_oracle':small_res['weights'].tolist(),
                        'small_indices':small.tolist(),
                        'full_dual_gap':full_res['dual_gap'],
                        'small_dual_gap':small_res['dual_gap']})
    output.mkdir(parents=True,exist_ok=True)
    cols=list(rows[0]);
    with (output/'A29_1_CASES.csv').open('w',newline='',encoding='utf8') as f:
        wr=csv.DictWriter(f,fieldnames=cols);wr.writeheader();wr.writerows(rows)
    (output/'A29_1_WEIGHTS.json').write_text(json.dumps(weights,indent=2,default=tojson))
    families={
        'COMPLEX':{'shell','asymmetric_piecewise','mixed_scale'},
        'ALL':{'shell','asymmetric_piecewise','mixed_scale','smooth'},
        'shell':{'shell'},'asymmetric_piecewise':{'asymmetric_piecewise'},
        'mixed_scale':{'mixed_scale'},'smooth':{'smooth'}}
    score_fields=['full_hard_oracle_nrmse','small_hard_oracle_nrmse',
                  'full_convex_oracle_nrmse','small_convex_oracle_nrmse',
                  'full_L_MAP_nrmse','small_L_MAP_nrmse','full_L_mean_nrmse','small_L_mean_nrmse']
    summary={g:{s:pair_parent_boot(rows,s,fam,seed=291011) for s in score_fields} for g,fam in families.items()}
    summary['validation']={'conditions':len(rows),'independent_parents':len(set(r['parent_id'] for r in rows)),
           'new_Maxwell_solves':0,'network_training':False,'fixed_A29_gate_unchanged':True,
           'full_oracle_max_dual_gap':max(r['full_oracle_dual_gap'] for r in rows),
           'small_oracle_max_dual_gap':max(r['small_oracle_dual_gap'] for r in rows),
           'truth_used_only_in_offline_capacity':True}
    (output/'A29_1_SUMMARY.json').write_text(json.dumps(summary,indent=2,default=tojson))
    vals=summary['COMPLEX']
    lines=['# A29.1 Saved-pool convex capacity diagnosis','',
        '**Exploratory, exposed development only. These are OFFLINE convex Oracles, not deployable Maxwell decisions.**','',
        f"Cases {len(rows)}, independent parents {summary['validation']['independent_parents']}, new Maxwell states 0.",'',
        '| Method | Complex relative gain vs N3 | 95% parent-bootstrap CI |','|---|---:|---:|']
    for key in score_fields:
        item=vals[key]
        lines.append(f"| {key} | {100*item['mean_relative_gain']:.3f}% | [{100*item['ci95'][0]:.3f}%, {100*item['ci95'][1]:.3f}%] |")
    lines+=['','## Scientific status',
            'If full convex Oracle still has low coverage, stop finite saved-bank line.',
            'If full convex Oracle improves but L mean does not, this is a selection/information problem.',
            'If L mean succeeds, validate on a new untouched cohort before any full Maxwell spend.',
            'Do NOT retroactively reopen A29 NO_GO; full F has not been run in A29.',
            'All material weights with sum 1 preserve pointwise convex material bounds, but not discrete topology.',
            'All confidence intervals are exploratory: the same 16 development parents have been repeatedly examined.']
    (output/'A29_1_DECISION.md').write_text('\n'.join(lines)+'\n')
    print('\n'.join(lines))


def self_test():
    true=np.array([1.+0j,1.+0j]);cand=np.array([[0.,0.],[2.,2.]],dtype=np.complex128)
    res=fit_convex_oracle(cand,true,1.)
    assert abs(res['nrmse'])<1e-9,(res['nrmse'],res)
    assert abs(res['weights'].sum()-1)<1e-10
    assert res['dual_gap']<1e-9
    print('PASS: convex hull can beat both hard hypotheses; KKT gap',res['dual_gap'])


if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--root',type=Path,default=Path('.'))
    ap.add_argument('--out',type=Path,default=Path('results/a29_1'))
    ap.add_argument('--self-test',action='store_true')
    args=ap.parse_args()
    if args.self_test:self_test()
    else:
        root=args.root.resolve();sys.path.insert(0,str(root/'src'))
        run(root,args.out)
