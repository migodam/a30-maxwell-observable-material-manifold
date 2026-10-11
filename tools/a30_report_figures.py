#!/usr/bin/env python3
"""Generate saved-result A30 figures. Launch through tools/a30_job.py."""
from pathlib import Path
import argparse
import json
import sys


def main():
    parser = argparse.ArgumentParser(description="Render A30 scientific PNG/SVG figures and raw plot tables from saved results only.")
    parser.add_argument("--root", type=Path, required=True, help="A30 project root with saved results/a30 artifacts")
    parser.add_argument("--out", type=Path, default=None, help="Output directory inside --root; default results/a30/figures")
    parser.add_argument("--metadata-out", type=Path, default=None, help="Source-caption directory inside --root; default research/delegated/a30_plots")
    parser.add_argument("--include-saved-hull-details", action="store_true",
                        help="Also render saved hull-family, weight/ESS and structure figures; default is the three core outcome figures")
    args = parser.parse_args()
    root = args.root.resolve()
    sys.path.insert(0, str(root / "src"))
    from a30.plots import generate
    result = generate(root, output=args.out, metadata_output=args.metadata_out,
                      include_saved_hull_details=args.include_saved_hull_details)
    print(json.dumps(result, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
