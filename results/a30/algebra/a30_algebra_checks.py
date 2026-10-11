#!/usr/bin/env python3
"""A30 independent finite-matrix checks. NOT a physical Maxwell backend.
No repository solvers, no Green-function fixtures, no data labels, no training.
Run: OPENBLAS_NUM_THREADS=1 python a30_algebra_checks.py
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
from scipy.linalg import eigh
from scipy.optimize import lsq_linear

rng = np.random.default_rng(301010)
checks = []
def record(name, value, tolerance, note=''):
    passed = bool(np.isfinite(value) and abs(value) <= tolerance)
    checks.append(dict(name=name, value=float(value), tolerance=float(tolerance), passed=passed, note=note))
    if not passed:
        raise AssertionError(checks[-1])
def rel(a, b):
    return float(np.linalg.norm(a-b)/max(np.linalg.norm(a), np.linalg.norm(b), 1e-15))
def packed(y):
    return np.concatenate([np.r_[y[:,s].real,y[:,s].imag] for s in range(y.shape[1])])
def real_material(x):
    return np.r_[x.real,x.imag]
def cplx(x):
    return x[:len(x)//2]+1j*x[len(x)//2:]

n,m,ns=7,4,3
G0=rng.normal(size=(n,n))+1j*rng.normal(size=(n,n))
G=.035*(G0+G0.T)/2
S=rng.normal(size=(m,n))+1j*rng.normal(size=(m,n))
E=rng.normal(size=(n,ns))+1j*rng.normal(size=(n,ns))
x=.1+rng.uniform(0,.1,n)+.04j
h=.02*(rng.normal(size=n)+1j*rng.normal(size=n))
k=.02*(rng.normal(size=n)+1j*rng.normal(size=n))
algebraic_evaluations=0

def state(x):
    global algebraic_evaluations
    algebraic_evaluations+=1
    L=np.eye(n)-x[:,None]*G
    c=np.linalg.solve(L,x[:,None]*E)
    e=E+G@c
    return L,c,e,S@c

def jvp(x,h):
    L,c,e,y=state(x)
    return S@np.linalg.solve(L,h[:,None]*e)

L,c,e,y=state(x)
L2,c2,e2,y2=state(x+h)
secant=S@np.linalg.solve(L2,h[:,None]*e)
record('finite_secant_right_endpoint',rel(y2-y,secant),1e-12)
record('finite_secant_left_endpoint',rel(y2-y,S@np.linalg.solve(L,h[:,None]*e2)),1e-12)
eps=1e-5
fd=(state(x+eps*h)[3]-state(x-eps*h)[3])/(2*eps)
record('real_directional_derivative',rel(fd,jvp(x,h)),2e-8)
uh=np.linalg.solve(L,h[:,None]*e)
uk=np.linalg.solve(L,k[:,None]*e)
hess=S@np.linalg.solve(L,h[:,None]*(G@uk)+k[:,None]*(G@uh))
fd2=(jvp(x+eps*k,h)-jvp(x-eps*k,h))/(2*eps)
record('symmetric_second_derivative',rel(hess,fd2),2e-7)
K=np.linalg.solve(L,h[:,None]*G)
r=np.linalg.solve(L,h[:,None]*e)
rem=S@np.linalg.solve(np.eye(n)-K,K@r)
record('anchor_feedback_remainder_identity',rel(y2-y-S@r,rem),1e-10)
q=float(np.linalg.norm(K,2))
bound=float(np.linalg.norm(S,2)*q/(1-q)*np.linalg.norm(r))
record('feedback_remainder_bound_excess',max(0,float(np.linalg.norm(rem))-bound),1e-14)

# Real material coordinates, source-wise real/imaginary observation packing.
J=np.column_stack([packed(jvp(x,cplx(np.eye(2*n)[:,j]))) for j in range(2*n)])
T=rng.normal(size=(2*n,4))
W=np.diag(np.linspace(.6,1.4,2*n))
whitener=np.diag(np.linspace(.7,1.3,2*m*ns))
A=whitener@J
H=T.T@A.T@A@T
Mt=T.T@W@T
change=np.diag([.05,2.,10.,.5])
eig0=eigh(H,Mt,eigvals_only=True)
eig1=eigh(change.T@H@change,change.T@Mt@change,eigvals_only=True)
record('material_metric_reparameterization_invariance',rel(eig0,eig1),1e-10)

# Exact conditional-moment closure, with bilinear (not Hermitian) covariance.
xs=[x,x+h,x+k]
ss=[state(z) for z in xs]
w=np.array([.2,.5,.3])
mu=sum(a*b for a,b in zip(w,xs))
mc=sum(a*b[1] for a,b in zip(w,ss))
me=sum(a*b[2] for a,b in zip(w,ss))
my=sum(a*b[3] for a,b in zip(w,ss))
kappa=sum(a*(z-mu)[:,None]*(b[2]-me) for a,z,b in zip(w,xs,ss))
record('bilinear_constitutive_covariance',rel(mc,mu[:,None]*me+kappa),1e-13)
Lm,cm,em,ym=state(mu)
record('mean_response_commutator',rel(ym-my,-S@np.linalg.solve(Lm,kappa)),1e-9)
a=real_material(mu)+.05*rng.normal(size=2*n)
mean_real=real_material(mu)
risk=lambda v:sum(ww*((v-real_material(z))@W@(v-real_material(z))) for ww,z in zip(w,xs))
record('conditional_squared_material_risk_identity',abs(risk(a)-risk(mean_real)-(a-mean_real)@W@(a-mean_real)),1e-12)

# Rank-one algebraic scattering response: different patterns, same total contrast.
g=.12+.01j
Ga=g*np.ones((3,3));Sa=np.ones((1,3));Ea=np.ones(3)
p0=np.array([1.,0.,1.]);p1=np.array([.5,1.,.5]);amp=.2+.05j
Fa=lambda z:Sa@np.linalg.solve(np.eye(3)-z[:,None]*Ga,z*Ea)
f0=Fa(amp*p0);f1=Fa(amp*p1)
record('different_pattern_same_algebraic_scattering',rel(f0,f1),1e-13,
       'Generic rank-one matrix example, NOT a physical Green geometry.')

# Fixed-pair versus compensated separation, in already whitened coordinates.
delta=np.array([10.,.01]);B=np.array([[-1.,1.],[0.,0.]])
sol=lsq_linear(B,-delta,bounds=(-5*np.ones(2),5*np.ones(2)),tol=1e-14,max_iter=500)
dcomp=float(np.linalg.norm(delta+B@sol.x))
record('compensated_distance',abs(dcomp-.01),1e-7)

# Linear-Gaussian weak-coordinate completion: y=u+n, v=u+xi.
noise_var=.01;conditional_var=.04
vpost_u=noise_var/(1+noise_var)
vpost_v=conditional_var+vpost_u
record('unobservable_conditional_variance_floor',max(0,conditional_var-vpost_v),1e-14)

# A raw forward error controls log likelihood error on the same candidate.
worst_excess=0.
for _ in range(100):
    obs=rng.normal(size=11);ft=rng.normal(size=11);err=.03*rng.normal(size=11)
    f=ft+err;b=float(np.linalg.norm(err))
    exact=.5*float(np.sum((obs-f)**2));approx=.5*float(np.sum((obs-ft)**2))
    cert=b*np.linalg.norm(obs-ft)+.5*b*b
    worst_excess=max(worst_excess,abs(exact-approx)-cert)
record('likelihood_error_certificate',max(0,worst_excess),1e-12)

# A single value calibration retains a first-order slope defect.
dirh=h/np.linalg.norm(h)
true_slope=jvp(x,dirh)
wrong_slope=.9*true_slope
rems=[];wrong=[]
for t in [.002,.001,.0005]:
    yy=state(x+t*dirh)[3]
    rems.append(float(np.linalg.norm(yy-y-t*true_slope)))
    wrong.append(float(np.linalg.norm(yy-y-t*wrong_slope)))
quad_ratio=rems[-2]/rems[-1];linear_ratio=wrong[-2]/wrong[-1]
record('true_tangent_second_order_ratio',abs(quad_ratio-4),.03)
record('calibrated_wrong_slope_first_order_ratio',abs(linear_ratio-2),.03)

# Exact profiling of Gaussian nuisance is not the same as deleting it for free.
Bn=rng.normal(size=(8,2));rn=rng.normal(size=8);C=np.diag([.3,.7])
P=np.eye(8)-Bn@np.linalg.solve(Bn.T@Bn+np.linalg.inv(C),Bn.T)
u=np.linalg.solve(Bn.T@Bn+np.linalg.inv(C),Bn.T@rn)
profile=np.linalg.norm(rn-Bn@u)**2+u@np.linalg.inv(C)@u
record('penalized_nuisance_schur_profile',abs(profile-rn@P@rn),1e-11)

# Frozen-GN restriction: no nonlinear or unrestricted optimization claim.
summary=dict(status='PASS',checks=checks,
    validation=dict(physical_Maxwell_backend_evaluations=0,network_training_updates=0,
                    locked_payloads_read=0,generic_matrix_state_evaluations=algebraic_evaluations,
                    interpretation='Algebraic verification only; no A29 full-pool data available.'),
    examples=dict(raw_pair_distance=float(np.linalg.norm(delta)),compensated_distance=dcomp,
                  conditional_weak_prior_variance=1+conditional_var,
                  conditional_weak_posterior_variance=vpost_v,
                  conditional_irreducible_variance=conditional_var,
                  true_tangent_error_halving_ratio=quad_ratio,
                  value_calibrated_wrong_slope_error_halving_ratio=linear_ratio,
                  anchor_q=q,feedback_remainder_norm=float(np.linalg.norm(rem)),
                  feedback_remainder_upper_bound=bound,
                  generalized_information_eigenvalues=eig0.tolist()))
out=Path(__file__).with_name('A30_ALGEBRA_CHECKS.json')
out.write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps(dict(status=summary['status'],checks=len(checks),examples=summary['examples'],validation=summary['validation']),indent=2))
