# Knowledge-graph primer

This page is for people who work comfortably with dataframes, pipelines or ML, but haven't worked with RDF, ontologies or SPARQL. Each idea links to where it shows up in this repository.

## 1. Triples: a graph as a three-column table

A knowledge graph is a set of **triples**: *subject – predicate – object*.

| subject | predicate | object |
|---|---|---|
| `NCBITaxon:851` | `rdfs:label` | `"Fusobacterium nucleatum"` |
| `micokg:sample/UC3-S01` | `mixs:0000014` (env_medium) | `UBERON:0001988` (feces) |
| `micokg:obs/UC3-O01` | `sosa:hasSimpleResult` | `0.042` |

If you know PyTorch Geometric: subjects and objects are nodes, and each predicate is an **edge type**. The graph is heterogeneous by nature. The difference from an `edge_index` is that every node and edge type has a globally unique name, so graphs from different groups can simply be merged.

This format is called **RDF**, and `.ttl` (Turtle) files are one way to write it. Run `make rdf` and open `build/rdf/Container-uc3-cancer.ttl` to see our toy data as triples.

## 2. IRIs and CURIEs: global names

Every node and predicate is named by an **IRI**, a web address such as `http://purl.obolibrary.org/obo/NCBITaxon_851`. Writing that in full is tedious, so we use **CURIEs** (`NCBITaxon:851`) plus a prefix map that expands them. The prefix map is in [`schema/micokg.yaml`](https://github.com/FatemehFN/micokg-blueprint/blob/main/schema/micokg.yaml).

The golden rule: **if an ontology already has an identifier for the thing, use it.** Two resources that both say `NCBITaxon:851` are automatically about the same organism, with no joining on fuzzy names.

## 3. Ontologies: controlled vocabularies with a hierarchy

An ontology is a curated set of terms with definitions and relations, most importantly **is_a** (`rdfs:subClassOf`):

```
colorectal adenocarcinoma (MONDO:0005008)
  is_a colorectal carcinoma
    is_a colorectal cancer (MONDO:0005575)
```

So a question about *colorectal cancer* should also find records coded as *colorectal adenocarcinoma*. The ontologies used here, by entity:

| Entity | Ontology |
|---|---|
| Taxa | NCBITaxon |
| Environments | ENVO |
| Anatomy | UBERON |
| Diseases | MONDO / DOID / NCIT / EFO |
| Chemicals and metabolites | ChEBI |
| Functions | GO |
| Sequence features | SO |
| Antimicrobial resistance | ARO |
| Foods | FoodOn |
| Evidence types | ECO |

Browse any of them in [OLS](https://www.ebi.ac.uk/ols4/). For offline tests we keep **slims**: the is_a ancestors of only the terms we use, in `examples/ontology-slims/`.

## 4. LinkML: the schema you edit

Hand-writing RDF is error-prone, so we describe the data model in **LinkML**, a YAML schema language similar in spirit to pydantic models or JSON Schema. From one schema we get:

- **validation** of YAML/JSON data (`make validate`);
- **RDF** conversion, where every slot has a `slot_uri` that becomes the predicate;
- **OWL**, **SHACL**, a JSON-LD context and documentation (`make gen`).

A slot definition looks like this:

```yaml
env_medium:
  slot_uri: mixs:0000014        # the RDF predicate (reused from the MIxS standard)
  range: uriorcurie             # the value is an identifier, so it becomes an IRI in RDF
  pattern: "^(ENVO:\\d{8}|UBERON:\\d{7})$"
```

Contributors mostly write **YAML data** that follows the schema (see `examples/valid/`). They rarely write RDF directly.

## 5. Observations vs associations

Two kinds of statement are easily confused:

- **Observation** (SOSA standard): *in sample S01, the relative abundance of F. nucleatum was 0.042.* This is a raw measurement.
- **Association**: *F. nucleatum is increased in colorectal cancer (stool, study A, experimental evidence).* This is a claim made from observations or from a paper.

A plain edge `F.nucleatum → correlated_with → CRC` has nowhere to store *increased*, *stool*, *which study* or *how confident*. And when another study finds the opposite, the two findings collapse into one edge. So each association is a **node of its own** (in RDF terms, a *reified statement*):

```
micokg:assoc/UC3-A03  rdf:subject    NCBITaxon:817
                      rdf:predicate  RO:0002610       # correlated with
                      rdf:object     MONDO:0005575
                      micokg:direction "increased"
                      micokg:anatomical_context UBERON:0001988
                      dct:source     micokg:study/UC3-A
```

In graph-ML terms, the edge now has attributes, or you can think of it as a hyperedge. For tools that want plain edges, `scripts/materialise_shortcuts.rq` derives them. See [ADR-0001](adr/0001-association-reification.md).

## 6. SPARQL: querying the graph

SPARQL matches **patterns of triples**. Variables start with `?`:

```sparql
SELECT ?taxon ?direction WHERE {
  ?a a micokg:TaxonDiseaseAssociation ;      # ?a is a taxon–disease association
     rdf:subject ?taxon ;                    # about some taxon
     rdf:object  ?disease ;                  # and some disease
     micokg:direction ?direction .
  ?disease rdfs:subClassOf* obo:MONDO_0005575 .   # the disease is CRC or any subtype
}
```

- `;` repeats the same subject.
- `rdfs:subClassOf*` is a **property path** meaning "zero or more is_a steps".
- `skos:exactMatch|^skos:exactMatch` means "a mapping in either direction".

All our questions are in `queries/`, with comments explaining each part. Run them with `python scripts/run_cq.py`.

## 7. SSSOM: mappings between ontologies

Different resources code the same concept differently, e.g. DOID:9256 and MONDO:0005575 for colorectal cancer. **SSSOM** is a TSV format for such mappings. Each row records the match type (`skos:exactMatch`, `closeMatch`…), **how** it was made (manual curation, lexical match, or an AI model such as VERDANT) and **who** made or reviewed it. See `mappings/` and [VERDANT integration](verdant-integration.md).

## 8. SHACL: shape checks on RDF

**SHACL** describes what well-formed RDF looks like ("every association has exactly one `rdf:subject`, and it is an IRI"). We generate it from the LinkML schema and check the converted examples (`make shacl`).

## Further reading

- LinkML tutorial: <https://linkml.io/linkml/intro/tutorial.html>
- SPARQL by example: <https://www.w3.org/2009/Talks/0615-qbe/>
- SSSOM: <https://mapping-commons.github.io/sssom/>
- SOSA/SSN (observations): <https://www.w3.org/TR/vocab-ssn/>
- Biolink Model, the association pattern in biomedical KGs: <https://biolink.github.io/biolink-model/>
