"""Export competency-question queries in the SIB SPARQL-examples format.

Each queries/<use-case>/cqs.yaml entry becomes one Turtle file:

    ex:uc3-cq01 a sh:SPARQLExecutable, sh:SPARQLSelectExecutable ;
        rdfs:comment "<question>"@en ;
        sh:select "<query>" ;
        schema:target <endpoint> ;
        schema:keywords "..." .

This is the convention used by https://github.com/sib-swiss/sparql-examples, so
the same files can be loaded into a SPARQL endpoint (and shared with Project 15
and VERDANT). Queries containing SERVICE <...> get spex:federatesWith.

Usage: python scripts/rq_to_spex.py [-o build/sparql-examples]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from rdflib import RDF, RDFS, Graph, Literal, Namespace, URIRef

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.kg import load_cqs  # noqa: E402

SH = Namespace("http://www.w3.org/ns/shacl#")
SCHEMA = Namespace("https://schema.org/")
SPEX = Namespace("https://purl.expasy.org/sparql-examples/ontology#")
EX = Namespace("https://w3id.org/micokg/sparql-examples/")

FORMS = {
    "SELECT": (SH.SPARQLSelectExecutable, SH.select),
    "ASK": (SH.SPARQLAskExecutable, SH.ask),
    "CONSTRUCT": (SH.SPARQLConstructExecutable, SH.construct),
    "DESCRIBE": (SPEX.SPARQLDescribeExecutable, SPEX.describe),
}


def query_form(query: str) -> str:
    body = re.sub(r"#[^\n]*", "", query)  # strip comments
    body = re.sub(r"(?im)^\s*(PREFIX|BASE)\b[^\n]*", "", body)
    match = re.search(r"\b(SELECT|ASK|CONSTRUCT|DESCRIBE)\b", body, re.IGNORECASE)
    if not match:
        raise ValueError("cannot determine query form")
    return match.group(1).upper()


def cq_graph(cq: dict, target: str) -> Graph:
    g = Graph()
    for prefix, ns in (("sh", SH), ("schema", SCHEMA), ("spex", SPEX), ("ex", EX)):
        g.bind(prefix, ns)
    node = EX[cq["id"]]
    executable_type, query_predicate = FORMS[query_form(cq["query_text"])]
    g.add((node, RDF.type, SH.SPARQLExecutable))
    g.add((node, RDF.type, executable_type))
    g.add((node, RDFS.comment, Literal(" ".join(cq["question"].split()), lang="en")))
    g.add((node, query_predicate, Literal(cq["query_text"])))
    g.add((node, SCHEMA.target, URIRef(target)))
    for keyword in cq.get("keywords", []):
        g.add((node, SCHEMA.keywords, Literal(keyword)))
    for service in re.findall(r"SERVICE\s+<([^>]+)>", cq["query_text"], re.IGNORECASE):
        g.add((node, SPEX.federatesWith, URIRef(service)))
    return g


def export(outdir: Path) -> list[Path]:
    import yaml

    written = []
    targets = {}
    for cq in load_cqs():
        if cq["use_case"] not in targets:
            spec = yaml.safe_load((cq["query_path"].parent / "cqs.yaml").read_text())
            targets[cq["use_case"]] = spec.get("target", "https://w3id.org/micokg/sparql")
        out = outdir / cq["use_case"] / f"{cq['id']}.ttl"
        out.parent.mkdir(parents=True, exist_ok=True)
        cq_graph(cq, targets[cq["use_case"]]).serialize(out, format="turtle")
        written.append(out)
    return written


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-o", "--outdir", type=Path, default=Path("build/sparql-examples"))
    args = ap.parse_args()
    written = export(args.outdir)
    print(f"wrote {len(written)} SPARQL examples to {args.outdir}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
