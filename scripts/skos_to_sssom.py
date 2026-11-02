"""Convert VERDANT (Project 11) SKOS mapping output to SSSOM candidate files.

Accepted input (Turtle), either or both of:
  1. plain SKOS triples:            <s> skos:exactMatch <o> .
  2. reified mappings with a score:
        [] a owl:Axiom ;
           owl:annotatedSource <s> ; owl:annotatedProperty skos:closeMatch ;
           owl:annotatedTarget <o> ; sssom:confidence 0.83 .

Output rows are marked as machine-generated and unreviewed
(mapping_justification semapv:SemanticSimilarityThresholdMatching,
mapping_tool VERDANT, no reviewer_id). Curators then move rows to
mappings/curated/ (adding reviewer_id) or to mappings/verdant/rejected/
(with predicate_modifier Not). See docs/verdant-integration.md.

Usage:
  python scripts/skos_to_sssom.py verdant-output.ttl -o mappings/verdant/candidates/habitat.sssom.tsv \\
      --mapping-set-id https://w3id.org/micokg/mappings/verdant/habitat --tool-version 0.3.0
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import sys
from pathlib import Path

import yaml
from rdflib import OWL, RDF, RDFS, Graph, Literal, Namespace, URIRef

SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
SSSOM = Namespace("https://w3id.org/sssom/")
SKOS_PREDICATES = [SKOS.exactMatch, SKOS.closeMatch, SKOS.broadMatch, SKOS.narrowMatch, SKOS.relatedMatch]
COLUMNS = [
    "subject_id", "subject_label", "predicate_id", "object_id", "object_label",
    "mapping_justification", "confidence", "mapping_tool", "mapping_tool_version",
    "reviewer_id", "comment",
]

ROOT = Path(__file__).resolve().parents[1]


def prefix_map() -> dict[str, str]:
    prefixes = yaml.safe_load((ROOT / "schema" / "micokg.yaml").read_text())["prefixes"]
    prefixes["semapv"] = "https://w3id.org/semapv/vocab/"
    return prefixes


def to_curie(iri: URIRef, prefixes: dict[str, str], used: dict[str, str]) -> str:
    best = max(((p, ns) for p, ns in prefixes.items() if str(iri).startswith(ns)),
               key=lambda kv: len(kv[1]), default=None)
    if best is None:
        raise ValueError(f"no prefix for {iri}; add it to schema/micokg.yaml prefixes")
    used[best[0]] = best[1]
    return f"{best[0]}:{str(iri)[len(best[1]):]}"


def extract(g: Graph) -> dict[tuple, float | None]:
    mappings: dict[tuple, float | None] = {}
    for axiom in g.subjects(RDF.type, OWL.Axiom):
        s = g.value(axiom, OWL.annotatedSource)
        p = g.value(axiom, OWL.annotatedProperty)
        o = g.value(axiom, OWL.annotatedTarget)
        if p in SKOS_PREDICATES and s is not None and o is not None:
            conf = g.value(axiom, SSSOM.confidence)
            mappings[(s, p, o)] = float(conf) if isinstance(conf, Literal) else None
    for p in SKOS_PREDICATES:
        for s, o in g.subject_objects(p):
            mappings.setdefault((s, p, o), None)
    return mappings


def convert(inp: Path, out: Path, mapping_set_id: str, tool_version: str) -> int:
    g = Graph().parse(inp, format="turtle")
    prefixes, used = prefix_map(), {}
    rows = []
    def label(node) -> str:
        return str(g.value(node, SKOS.prefLabel) or g.value(node, RDFS.label) or "")

    for (s, p, o), conf in sorted(extract(g).items()):
        rows.append({
            "subject_id": to_curie(s, prefixes, used),
            "subject_label": label(s),
            "predicate_id": to_curie(p, prefixes, used),
            "object_id": to_curie(o, prefixes, used),
            "object_label": label(o),
            "mapping_justification": "semapv:SemanticSimilarityThresholdMatching",
            "confidence": "" if conf is None else f"{conf:.3f}",
            "mapping_tool": "VERDANT",
            "mapping_tool_version": tool_version,
            "reviewer_id": "",
            "comment": "",
        })
    used["semapv"] = prefixes["semapv"]
    header = {
        "curie_map": dict(sorted(used.items())),
        "mapping_set_id": mapping_set_id,
        "mapping_set_description": f"Unreviewed VERDANT mapping candidates converted from {inp.name}.",
        "license": "https://creativecommons.org/licenses/by/4.0/",
        "mapping_date": dt.date.today().isoformat(),
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="") as fh:
        for line in yaml.safe_dump(header, sort_keys=False).splitlines():
            fh.write(f"# {line}\n")
        writer = csv.DictWriter(fh, fieldnames=COLUMNS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", type=Path)
    ap.add_argument("-o", "--output", type=Path, required=True)
    ap.add_argument("--mapping-set-id", required=True)
    ap.add_argument("--tool-version", default="unknown")
    args = ap.parse_args()
    n = convert(args.input, args.output, args.mapping_set_id, args.tool_version)
    print(f"{n} candidate mappings -> {args.output}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
