"""Convert curated SSSOM TSV files to plain RDF triples for querying.

`sssom convert -O ttl` writes each mapping as an owl:Axiom (reified), which is
right for publishing but awkward in SPARQL. For the query layer we also want
the direct triple, e.g. DOID:9256 skos:exactMatch MONDO:0005575, so templates
can expand identifiers with `skos:exactMatch|^skos:exactMatch`.

Rows with predicate_modifier "Not" (rejected mappings) are skipped.

Usage: python scripts/sssom_to_rdf.py mappings/curated/*.sssom.tsv -o build/mappings/curated-direct.ttl
"""

from __future__ import annotations

import argparse
import csv
import io
import sys
from pathlib import Path

import yaml
from rdflib import Graph, URIRef


def read_sssom(path: Path) -> tuple[dict, list[dict]]:
    meta_lines, body_lines = [], []
    for line in path.read_text().splitlines():
        (meta_lines if line.startswith("#") else body_lines).append(line)
    meta = yaml.safe_load("\n".join(l[1:] for l in meta_lines)) or {}
    rows = list(csv.DictReader(io.StringIO("\n".join(body_lines)), delimiter="\t"))
    return meta, rows


def expand(curie: str, prefixes: dict[str, str]) -> URIRef:
    if curie.startswith(("http://", "https://")):
        return URIRef(curie)
    prefix, sep, local = curie.partition(":")
    if not sep or prefix not in prefixes:
        raise ValueError(f"unknown prefix in {curie!r}")
    return URIRef(prefixes[prefix] + local)


def convert(paths: list[Path]) -> Graph:
    g = Graph()
    for path in paths:
        meta, rows = read_sssom(path)
        prefixes = meta.get("curie_map", {})
        for row in rows:
            if (row.get("predicate_modifier") or "").strip() == "Not":
                continue
            g.add((
                expand(row["subject_id"], prefixes),
                expand(row["predicate_id"], prefixes),
                expand(row["object_id"], prefixes),
            ))
    return g


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("inputs", nargs="+", type=Path)
    ap.add_argument("-o", "--output", type=Path, required=True)
    args = ap.parse_args()
    g = convert(args.inputs)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    g.serialize(args.output, format="turtle")
    print(f"{len(g)} mapping triples -> {args.output}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
