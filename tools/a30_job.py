#!/usr/bin/env python3
"""Account all CPU subprocess work; reservation precedes real physical actions.

No backend is imported. A failed or killed job remains paid. A second launch
cannot ignore an unfinished job. CPU jobs use max(wall, native process CPU).
"""
from __future__ import annotations
import argparse, json, os, resource, subprocess, sys, time
from pathlib import Path


def write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as f:
        json.dump(obj, f, indent=2, allow_nan=False)
        f.write('\n')


def history(root):
    cpu = gpu = 0.
    unresolved = []
    for p in sorted((root/'results/a30/jobs').glob('*/manifest.json')):
        receipt=p.parent/'receipt.json'
        if not receipt.exists():
            unresolved.append(p.parent.name); continue
        r=json.loads(receipt.read_text())
        cpu+=float(r['charged_cpu_seconds']); gpu+=float(r.get('gpu_occupied_seconds',0))
    external=root/'results/a30/EXTERNAL_COSTS.jsonl'
    if external.exists():
        for line in external.read_text().splitlines():
            r=json.loads(line);cpu+=float(r['charged_cpu_seconds']);gpu+=float(r.get('gpu_occupied_seconds',0))
    return dict(cpu_seconds=cpu,gpu_seconds=gpu,unresolved=unresolved)


def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True)
    p.add_argument('--job',required=True);p.add_argument('--stage',required=True)
    p.add_argument('--seconds',type=float,required=True);p.add_argument('command',nargs=argparse.REMAINDER)
    a=p.parse_args();root=a.root.resolve()
    if Path(a.job).name!=a.job or not a.command:raise ValueError('SIMPLE_JOB_AND_COMMAND_REQUIRED')
    cfg=json.loads((root/'a30_config.json').read_text());h=history(root)
    if h['unresolved']:raise RuntimeError('UNRESOLVED_JOBS:'+','.join(h['unresolved']))
    if h['cpu_seconds']+a.seconds>cfg['budgets']['cpu_seconds']-30:raise RuntimeError('CPU_RESERVATION_REFUSED')
    if a.stage=='e1':
        g=json.loads((root/'results/a30/E0_GATE.json').read_text())
        if g['status']!='PASS':raise RuntimeError('E0_PASS_REQUIRED')
    if a.stage=='e2':raise RuntimeError('E2_PROHIBITED')
    directory=root/'results/a30/jobs'/a.job
    if directory.exists():raise FileExistsError(directory)
    directory.mkdir(parents=True)
    command=a.command[1:] if a.command[0]=='--' else a.command
    write(directory/'manifest.json',dict(job=a.job,stage=a.stage,command=command,prior=h,
          cpu_reserved_seconds=a.seconds,started_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())))
    start=time.perf_counter();own=time.process_time();child0=resource.getrusage(resource.RUSAGE_CHILDREN)
    env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',VECLIB_MAXIMUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONPATH=str(root/'src'))
    status='FAILED';error=None;returncode=None
    try:
        with (directory/'stdout.log').open('w') as out,(directory/'stderr.log').open('w') as err:
            process=subprocess.Popen(command,cwd=root,env=env,stdout=out,stderr=err)
            while process.poll() is None:
                if time.perf_counter()-start>a.seconds:
                    process.terminate()
                    try:process.wait(timeout=3)
                    except subprocess.TimeoutExpired:process.kill();process.wait()
                    status='BUDGET_STOP';break
                time.sleep(.05)
            returncode=process.returncode
            if status!='BUDGET_STOP':status='COMPLETE' if returncode==0 else 'FAILED'
    except BaseException as exc:error=type(exc).__name__+': '+str(exc)
    finally:
        usage=resource.getrusage(resource.RUSAGE_CHILDREN)
        wall=time.perf_counter()-start
        cpu=time.process_time()-own+usage.ru_utime+usage.ru_stime-child0.ru_utime-child0.ru_stime
        receipt=dict(job=a.job,stage=a.stage,status=status,error=error,returncode=returncode,
           wall_seconds=wall,process_cpu_seconds=cpu,charged_cpu_seconds=max(wall,cpu),gpu_occupied_seconds=0,
           native_process_cpu=True,ended_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()))
        write(directory/'receipt.json',receipt)
        with (root/'results/a30/COST_LEDGER.jsonl').open('a') as f:f.write(json.dumps(receipt)+'\n')
        if status!='COMPLETE':
            with (root/'results/a30/FAILURE_LEDGER.jsonl').open('a') as f:f.write(json.dumps(receipt)+'\n')
    print(json.dumps(receipt));return 0 if status=='COMPLETE' else 3


if __name__=='__main__':raise SystemExit(main())
