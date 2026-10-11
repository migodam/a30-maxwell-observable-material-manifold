#!/usr/bin/env python3
"""Publish this authorized A30 deliverable. No checksums or experiment calls."""
from pathlib import Path
import subprocess,json

root=Path(__file__).resolve().parents[1]
repo='migodam/a30-maxwell-observable-material-manifold'
def run(args,capture=False):
    return subprocess.run(args,cwd=root,check=True,text=True,
        stdout=subprocess.PIPE if capture else None).stdout

run(['git','add','.'])
run(['git','-c','commit.gpgsign=false','commit','-m',
     'Complete A30 E0 capacity and bounded Maxwell compensation diagnosis'])
run(['gh','repo','create',repo,'--public','--source',str(root),'--remote','origin',
     '--description','A30 cached material-capacity and bounded Maxwell compensation diagnostics; exposed 2D TM development.'])
run(['git','push','--set-upstream','origin','HEAD:main'])
notes=root/'publication/release_notes.md'
notes.write_text('''# A30 E0 / conditional E1

E0 offline capacity passes the original protocol: full hull13.12%complex improvement; fixed-support sparse64 achieves35.69%. These are offline capacity, not online recovery gains.

E1:29/32legitimate local pairs,3unavailable. No nominal>=3 to compensated<=1witness found; no global compensated minimum claimed. Total161full-wave invocations within192global cap, including60redundant first-pass calls; the32failure reserve was exceeded and the correction/limitedL endpoint audit are disclosed. NoE2,NN,newtruthlabels or locked data.

The raw asset contains all384fit trajectories and actual hull/compensation material arrays. Input data are the original public A29release. Scientific decisions and failures remain in the Chinese report and tables. Nohash/SHA256checks.
''')
run(['gh','release','create','a30-e0-e1-v0.1.0','--repo',repo,'--target','main',
     '--title','A30 E0 / E1 — capacity and compensation diagnosis',
     '--notes-file',str(notes),str(root/'publication/A30_E0_E1_RAW_RESULTS.zip')])
commit=run(['git','log','-1','--format=%H'],capture=True).strip()
receipt=dict(repository='https://github.com/'+repo,commit=commit,
    report='https://github.com/'+repo+'/blob/'+commit+'/A30_E0_E1_DECISION.md',
    raw='https://raw.githubusercontent.com/'+repo+'/'+commit+'/A30_E0_E1_DECISION.md',
    release='https://github.com/'+repo+'/releases/tag/a30-e0-e1-v0.1.0')
(root/'publication/RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt),flush=True)
