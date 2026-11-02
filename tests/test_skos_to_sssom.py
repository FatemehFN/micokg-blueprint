"""The VERDANT SKOS -> SSSOM converter produces valid, unreviewed candidate files."""

from sssom.parsers import parse_sssom_table

from scripts.kg import ROOT
from scripts.skos_to_sssom import convert
from scripts.sssom_to_rdf import read_sssom


def test_convert_fake_verdant_output(tmp_path):
    out = tmp_path / "candidates.sssom.tsv"
    n = convert(ROOT / "tests" / "fixtures" / "verdant-sample.ttl", out,
                "https://w3id.org/micokg/mappings/verdant/test", "test")
    assert n == 3

    meta, rows = read_sssom(out)
    assert {"micokg", "UBERON", "ENVO", "skos", "semapv"} <= set(meta["curie_map"])
    by_subject = {r["subject_id"]: r for r in rows}

    stool = by_subject["micokg:term/sample/stool"]
    assert stool["predicate_id"] == "skos:exactMatch"
    assert stool["object_id"] == "UBERON:0001988"
    assert stool["confidence"] == "0.940"
    assert stool["subject_label"] == "stool"

    indoor = by_subject["micokg:term/habitat/indoor-air"]
    assert indoor["predicate_id"] == "skos:broadMatch"
    assert indoor["confidence"] == ""  # plain SKOS triple, no score

    assert all(r["mapping_justification"] == "semapv:SemanticSimilarityThresholdMatching" for r in rows)
    assert all(r["mapping_tool"] == "VERDANT" and r["reviewer_id"] == "" for r in rows)
    parse_sssom_table(out)
