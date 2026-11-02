"""Run competency questions against the toy KG and print the results.

Examples:
    python scripts/run_cq.py                      # list all competency questions
    python scripts/run_cq.py uc3-cq01             # run one and print a table
    python scripts/run_cq.py uc3-cq01 --write-expected   # write tests/expected/<file>.csv
    python scripts/run_cq.py --query my-draft.rq  # run an ad-hoc query file
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.kg import ROOT, build_store, load_cqs, run_query  # noqa: E402


def print_table(variables: list[str], rows: list[dict[str, str]]) -> None:
    widths = {v: max([len(v)] + [len(r[v]) for r in rows]) for v in variables}
    print("  ".join(v.ljust(widths[v]) for v in variables))
    print("  ".join("-" * widths[v] for v in variables))
    for r in rows:
        print("  ".join(r[v].ljust(widths[v]) for v in variables))
    print(f"({len(rows)} rows)")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cq_id", nargs="?")
    ap.add_argument("--query", type=Path, help="run an ad-hoc .rq file instead")
    ap.add_argument("--write-expected", action="store_true")
    args = ap.parse_args()

    cqs = {cq["id"]: cq for cq in load_cqs()}
    if not args.cq_id and not args.query:
        for cq in cqs.values():
            print(f"{cq['id']:<10} [{cq.get('status', '?')}] {' '.join(cq['question'].split())}")
        return 0

    store = build_store()
    query = args.query.read_text() if args.query else cqs[args.cq_id]["query_text"]
    variables, rows = run_query(store, query)
    print_table(variables, rows)

    if args.write_expected:
        if not args.cq_id or "expected" not in cqs[args.cq_id]:
            print("--write-expected needs a CQ id with an 'expected' entry", file=sys.stderr)
            return 1
        out = ROOT / "tests" / "expected" / cqs[args.cq_id]["expected"]
        with out.open("w", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=variables, lineterminator="\n")
            writer.writeheader()
            writer.writerows(sorted(rows, key=lambda r: tuple(r[v] for v in variables)))
        print(f"wrote {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
