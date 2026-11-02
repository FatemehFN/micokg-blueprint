"""Shared helpers: build an in-memory knowledge graph and run competency questions.

The store contains, in the default graph:
  * every examples/valid/*.yaml file converted to RDF with the LinkML schema
  * the ontology slims in examples/ontology-slims/*.ttl (subClassOf + labels)
  * direct skos mapping triples from mappings/curated/*.sssom.tsv
and, in the named graph <https://w3id.org/micokg/graph/shortcuts>, the direct
subject-predicate-object edges produced by scripts/materialise_shortcuts.rq.
"""

from __future__ import annotations

import functools
import sys
import types
from pathlib import Path

import yaml
from pyoxigraph import BlankNode, Literal, NamedNode, Quad, RdfFormat, Store

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schema" / "micokg.yaml"
SHORTCUTS_GRAPH = NamedNode("https://w3id.org/micokg/graph/shortcuts")


@functools.cache
def schemaview():
    from linkml_runtime import SchemaView

    return SchemaView(str(SCHEMA))


@functools.cache
def merged_schema():
    """Schema with all module imports merged in.

    linkml.validator.validate() resolves imports relative to the working
    directory, so it is given this self-contained SchemaDefinition instead.
    """
    from linkml_runtime import SchemaView

    sv = SchemaView(str(SCHEMA))
    sv.merge_imports()
    return sv.schema


@functools.cache
def python_model() -> types.ModuleType:
    """Python dataclasses generated from the schema (needed by the RDF dumper)."""
    from linkml.generators.pythongen import PythonGenerator

    code = PythonGenerator(str(SCHEMA)).serialize()
    module = types.ModuleType("micokg_model")
    sys.modules["micokg_model"] = module
    exec(compile(code, "micokg_model", "exec"), module.__dict__)  # noqa: S102
    return module


def yaml_to_turtle(path: Path) -> str:
    from linkml_runtime.dumpers import rdflib_dumper
    from linkml_runtime.loaders import yaml_loader

    obj = yaml_loader.load(str(path), target_class=python_model().Container)
    return rdflib_dumper.dumps(obj, schemaview())


def build_store(materialise: bool = True) -> Store:
    store = Store()
    for f in sorted((ROOT / "examples" / "valid").glob("*.yaml")):
        store.load(yaml_to_turtle(f).encode(), format=RdfFormat.TURTLE)
    for f in sorted((ROOT / "examples" / "ontology-slims").glob("*.ttl")):
        store.load(path=str(f), format=RdfFormat.TURTLE)

    mapping_files = sorted((ROOT / "mappings" / "curated").glob("*.sssom.tsv"))
    if mapping_files:
        from scripts.sssom_to_rdf import convert

        ttl = convert(mapping_files).serialize(format="turtle")
        store.load(ttl.encode(), format=RdfFormat.TURTLE)

    if materialise:
        construct = (ROOT / "scripts" / "materialise_shortcuts.rq").read_text()
        for t in list(store.query(construct)):
            store.add(Quad(t.subject, t.predicate, t.object, SHORTCUTS_GRAPH))
    return store


@functools.cache
def _prefixes() -> list[tuple[str, str]]:
    prefixes = yaml.safe_load(SCHEMA.read_text())["prefixes"]
    return sorted(prefixes.items(), key=lambda kv: -len(kv[1]))  # longest namespace first


def curie(iri: str) -> str:
    for prefix, ns in _prefixes():
        if iri.startswith(ns) and len(iri) > len(ns):
            return f"{prefix}:{iri[len(ns):]}"
    return iri


def term_to_str(term) -> str:
    """Render a result term for comparison: CURIEs for IRIs, sorted '|' lists."""
    if term is None:
        return ""
    if isinstance(term, NamedNode):
        return curie(term.value)
    if isinstance(term, BlankNode):
        return f"_:{term.value}"
    if isinstance(term, Literal):
        parts = [curie(p) if p.startswith(("http://", "https://")) else p for p in term.value.split("|")]
        return "|".join(sorted(parts)) if len(parts) > 1 else parts[0]
    return str(term)


def run_query(store: Store, query: str) -> tuple[list[str], list[dict[str, str]]]:
    results = store.query(query)
    variables = [v.value for v in results.variables]
    rows = [{v: term_to_str(sol[v]) for v in variables} for sol in results]
    return variables, rows


def load_cqs() -> list[dict]:
    """All competency questions from queries/*/cqs.yaml, with query text attached."""
    cqs = []
    for cqs_file in sorted((ROOT / "queries").glob("*/cqs.yaml")):
        spec = yaml.safe_load(cqs_file.read_text())
        for cq in spec.get("competency_questions", []):
            cq = dict(cq)
            cq["use_case"] = spec["use_case"]
            cq["query_path"] = cqs_file.parent / cq["query"]
            cq["query_text"] = cq["query_path"].read_text()
            cqs.append(cq)
    return cqs
