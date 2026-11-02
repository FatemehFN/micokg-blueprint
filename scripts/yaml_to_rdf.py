"""Convert Container YAML files to Turtle using the LinkML schema.

Usage: python scripts/yaml_to_rdf.py examples/valid/*.yaml -o build/rdf

(Uses the LinkML Python API rather than `linkml-convert`, which resolves the
schema's module imports relative to the current working directory.)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.kg import yaml_to_turtle  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("inputs", nargs="+", type=Path)
    ap.add_argument("-o", "--outdir", type=Path, default=Path("build/rdf"))
    args = ap.parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)
    for path in args.inputs:
        out = args.outdir / f"{path.stem}.ttl"
        out.write_text(yaml_to_turtle(path))
        print(f"{path} -> {out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
