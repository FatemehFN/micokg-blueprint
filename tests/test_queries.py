"""Every competency question in queries/*/cqs.yaml runs against the toy KG.

Results are compared as an order-insensitive set of rows against
tests/expected/<file>.csv (every question must have one) (IRIs shown as CURIEs, '|' lists sorted).
Generate or refresh an expected file with:
    python scripts/run_cq.py <cq-id> --write-expected
and check the output by hand before committing it.
"""

import csv

import pytest

from scripts.kg import ROOT, load_cqs, run_query

CQS = load_cqs()


@pytest.mark.parametrize("cq", CQS, ids=[cq["id"] for cq in CQS])
def test_competency_question(kg, cq):
    variables, rows = run_query(kg, cq["query_text"])
    with (ROOT / "tests" / "expected" / cq["expected"]).open(newline="") as fh:
        reader = csv.DictReader(fh)
        assert reader.fieldnames == variables, "expected CSV header must match query variables"
        expected = [tuple(row[v] for v in variables) for row in reader]
    got = [tuple(row[v] for v in variables) for row in rows]
    assert sorted(got) == sorted(expected)


def test_every_cq_has_a_query_file():
    for cq in CQS:
        assert cq["query_path"].is_file(), cq["id"]


def test_shortcut_edges_are_materialised(kg):
    ask = """
    ASK { GRAPH <https://w3id.org/micokg/graph/shortcuts> {
      <http://purl.obolibrary.org/obo/NCBITaxon_851>
        <http://purl.obolibrary.org/obo/RO_0002610>
        <http://purl.obolibrary.org/obo/MONDO_0005575> } }
    """
    assert kg.query(ask)
