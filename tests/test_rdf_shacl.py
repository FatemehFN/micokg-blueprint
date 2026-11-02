"""RDF produced from valid examples conforms to the schema's SHACL shapes,
and ontology-valued slots are serialised as IRIs.

Shapes come from `gen-shacl --non-closed`. LinkML `pattern`s are written for
CURIEs (e.g. ^NCBITaxon:\\d+$); SHACL would test them against the expanded IRI
and always fail, so sh:pattern is dropped for IRI-valued properties here. Those
patterns are already enforced on the YAML by tests/test_examples.py.
"""

import functools

import pytest
from linkml.generators.shaclgen import ShaclGenerator
from pyshacl import validate as shacl_validate
from rdflib import Graph
from rdflib.namespace import SH

from scripts.kg import ROOT, SCHEMA, schemaview, yaml_to_turtle

VALID = sorted((ROOT / "examples" / "valid").glob("*.yaml"))

def iri_predicates() -> list[str]:
    """Every slot whose values are identifiers (range uriorcurie), except the id slot itself."""
    sv = schemaview()
    return [sv.get_uri(name, expand=True) for name, slot in sv.all_slots().items()
            if slot.range == "uriorcurie" and name != "id"]


@functools.cache
def shapes() -> Graph:
    g = Graph()
    g.parse(data=ShaclGenerator(str(SCHEMA), closed=False).serialize(), format="turtle")
    for prop in list(g.subjects(SH.nodeKind, SH.IRI)):
        g.remove((prop, SH.pattern, None))
    return g


@pytest.mark.parametrize("path", VALID, ids=[p.name for p in VALID])
def test_shacl_conforms(path):
    data = Graph().parse(data=yaml_to_turtle(path), format="turtle")
    conforms, _, report = shacl_validate(data, shacl_graph=shapes())
    assert conforms, report


@pytest.mark.parametrize("path", VALID, ids=[p.name for p in VALID])
def test_ontology_slots_are_iris(path):
    data = Graph().parse(data=yaml_to_turtle(path), format="turtle")
    values = ", ".join(f"<{p}>" for p in iri_predicates())
    literals = list(data.query(f"SELECT ?s ?p ?o WHERE {{ ?s ?p ?o FILTER(?p IN ({values}) && isLiteral(?o)) }}"))
    assert literals == [], f"literal values where IRIs are required: {literals[:5]}"
