#!/usr/bin/env python3
"""Package experimental arrays/fit trajectories, not source inputs or backups."""
from pathlib import Path
import json,zipfile

root=Path(__file__).resolve().parents[1]
destination=root/'publication/A30_E0_E1_RAW_RESULTS.zip'
destination.parent.mkdir(exist_ok=True)
paths=sorted((root/'results/a30/capacity/fits').glob('*.json'))
paths+=sorted((root/'results/a30').glob('*/*.npz'))
with zipfile.ZipFile(destination,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for path in paths:z.write(path,path.relative_to(root))
    z.writestr('RAW_RESULTS_README.txt',
        'A30 actual E0 fits, hull materials and E1 local endpoints. Offline truth-bearing capacity evidence; not deployable algorithm output.\n'
        'Scalar2DTM, exposed development, no locked data or new labels. First compensation directory is invalid; corrected directory contains the scientific witnesses.\n'
        'Public metrics and protocol are in the GitHub repository. Input arrays are the original A29 Release. No hash/SHA256 checks.\n')
print(json.dumps(dict(asset=destination.name,bytes=destination.stat().st_size,files=len(paths))))
