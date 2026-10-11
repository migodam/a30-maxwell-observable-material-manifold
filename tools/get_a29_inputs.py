#!/usr/bin/env python3
"""Download public A29 inputs only. No checksum, physics, or locked data."""
from pathlib import Path,PurePosixPath
import argparse,shutil,subprocess,zipfile


def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path('.'));root=p.parse_args().root.resolve()
    downloads=root/'inputs/releases';destination=root/'inputs/a29_release'
    downloads.mkdir(parents=True,exist_ok=True);destination.mkdir(parents=True,exist_ok=True)
    for name in ('A29_RAW_EVIDENCE.zip','A29_REPRO_INPUTS.zip'):
        archive=downloads/name
        if not archive.exists():
            subprocess.run(['gh','release','download','a29-v0.1.0','--repo',
                'migodam/a29-material-hypothesis-coverage','--pattern',name,'--dir',str(downloads)],check=True)
        with zipfile.ZipFile(archive) as z:
            for info in z.infolist():
                path=PurePosixPath(info.filename)
                if path.is_absolute() or '..' in path.parts or any('locked' in s.lower() for s in path.parts):
                    raise ValueError('Unsafe/locked archive path')
                target=destination/path
                if info.is_dir():target.mkdir(parents=True,exist_ok=True);continue
                if target.exists():continue
                target.parent.mkdir(parents=True,exist_ok=True)
                with z.open(info) as source,target.open('wb') as output:shutil.copyfileobj(source,output)
    metrics=destination/'src/a26';metrics.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(root/'src/a30/frozen_a26_metrics.py',metrics/'metrics.py')
    (metrics/'__init__.py').touch()
    print('Public A29 inputs ready; zero new Maxwell calls.')


if __name__=='__main__':main()
