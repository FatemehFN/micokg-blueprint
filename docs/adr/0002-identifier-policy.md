# ADR-0002: Identifiers, IRIs and ontology-valued slots

- **Status:** Proposed. To be ratified on hackathon Day 1.
- **Date:** 2026-09-15

## Context

Integration only works if the same thing has the same identifier everywhere. The blueprint also has to produce RDF that SPARQL can traverse, including ontology hierarchies. Early prototyping showed two technical pitfalls:

- LinkML serialises **enum** values as string literals in RDF, so they can't be linked to ontology hierarchies.
- **Class-typed** ranges make the generated SHACL require every referenced ontology term to be typed in the data, which contributors would find tedious.

## Decision

1. **Reuse ontology identifiers** for biological, chemical, environmental and disease entities. Mint `micokg:<type>/<local-id>` only for instance data (samples, observations, associations, studies, hosts, gene records).
2. **Namespace:** `https://w3id.org/micokg/`. The w3id redirect is to be registered once the GitHub organisation is agreed.
3. **Ontology-valued slots** use `range: uriorcurie` plus a prefix `pattern`, and optionally `bindings` to a dynamic enum for branch checks. They are serialised as IRIs, and a test enforces this.
4. **Expand prefixes to OBO PURLs** (`http://purl.obolibrary.org/obo/ENVO_`), matching the ontologies' own IRIs. The `canonical_prefixes` lint rule (identifiers.org) is disabled.
5. **Preferred prefixes per entity:**

   | Entity | Prefixes |
   |---|---|
   | Taxon | NCBITaxon; GTDB accepted for MAG-derived taxa |
   | Disease | MONDO preferred; DOID, NCIT and EFO accepted and bridged by SSSOM (**to be decided**: the proposal names DO) |
   | Metabolite | CHEBI (HMDB accepted) |
   | Habitat / environment | ENVO |
   | Anatomy | UBERON |
   | Function | GO; KEGG orthology and EC as gene families |
   | AMR | ARO |
   | Food | FOODON (CHEBI for defined compounds) |
   | Evidence | ECO |

## Consequences

- ✅ Data from different resources joins on identifiers, not labels.
- ✅ Queries can use `rdfs:subClassOf*` over ontology slims or full ontologies.
- ⚠️ YAML patterns check the prefix only, not whether the term exists or sits in the right branch. The nightly `linkml-term-validator` job covers that.
- ⚠️ SHACL `sh:pattern` constraints written for CURIEs don't apply to expanded IRIs, so they are dropped when validating RDF (see `tests/test_rdf_shacl.py`).
