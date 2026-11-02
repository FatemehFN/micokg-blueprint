"""Curated SSSOM mapping files are well formed and internally consistent."""

from collections import defaultdict

import pytest
from sssom.parsers import parse_sssom_table

from scripts.kg import ROOT
from scripts.sssom_to_rdf import read_sssom

FILES = sorted((ROOT / "mappings").glob("**/*.sssom.tsv"))
REQUIRED_COLUMNS = {"subject_id", "predicate_id", "object_id", "mapping_justification"}
ALLOWED_PREDICATES = {
    "skos:exactMatch", "skos:closeMatch", "skos:broadMatch",
    "skos:narrowMatch", "skos:relatedMatch", "owl:equivalentClass",
}


@pytest.mark.parametrize("path", FILES, ids=[str(p.relative_to(ROOT)) for p in FILES])
def test_sssom_file(path):
    meta, rows = read_sssom(path)
    assert "mapping_set_id" in meta and "license" in meta
    assert rows, "no mappings"
    assert REQUIRED_COLUMNS <= set(rows[0]), f"missing columns: {REQUIRED_COLUMNS - set(rows[0])}"

    prefixes = set(meta.get("curie_map", {}))
    pairs = defaultdict(set)
    for row in rows:
        for col in ("subject_id", "predicate_id", "object_id", "mapping_justification"):
            prefix = row[col].split(":", 1)[0]
            assert prefix in prefixes, f"{row[col]}: prefix {prefix!r} not in curie_map"
        assert row["predicate_id"] in ALLOWED_PREDICATES, row["predicate_id"]
        assert row["mapping_justification"].startswith("semapv:")
        if row.get("confidence"):
            assert 0 <= float(row["confidence"]) <= 1
        modifier = (row.get("predicate_modifier") or "").strip()
        pairs[(row["subject_id"], row["object_id"])].add((row["predicate_id"], modifier))

    for pair, preds in pairs.items():
        assert not any((p, "Not") in preds and (p, "") in preds for p, _ in preds), f"{pair} asserted and negated"

    parse_sssom_table(path)  # must also load with sssom-py
