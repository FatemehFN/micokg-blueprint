"""Exported SIB-style SPARQL examples are well formed and their queries parse."""

from pyoxigraph import Store
from rdflib import RDF, RDFS, Graph, Namespace

from scripts.rq_to_spex import FORMS, export

SH = Namespace("http://www.w3.org/ns/shacl#")
SCHEMA = Namespace("https://schema.org/")


def test_spex_export(tmp_path):
    files = export(tmp_path)
    assert files, "no competency questions found"
    empty = Store()
    query_predicates = {pred for _, pred in FORMS.values()}

    for path in files:
        g = Graph().parse(path, format="turtle")
        nodes = list(g.subjects(RDF.type, SH.SPARQLExecutable))
        assert len(nodes) == 1, path
        node = nodes[0]
        assert g.value(node, RDFS.comment), f"{path}: missing rdfs:comment"
        assert g.value(node, SCHEMA.target), f"{path}: missing schema:target"
        queries = [o for p in query_predicates for o in g.objects(node, p)]
        assert len(queries) == 1, f"{path}: expected exactly one query"
        empty.query(str(queries[0]))  # raises SyntaxError if the query does not parse
