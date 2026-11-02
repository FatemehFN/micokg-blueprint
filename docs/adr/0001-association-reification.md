# ADR-0001: Represent associations as nodes (reification), with derived shortcut edges

- **Status:** Proposed. To be ratified on hackathon Day 1.
- **Date:** 2026-09-15

## Context

Microbiome findings depend on context. The same taxon can be reported as increased in colorectal-cancer stool and decreased in tumour tissue. It can also be associated in one cohort and not in another, or depend on the sequencing method. Downstream users (curators, meta-analysts, graph-ML pipelines) need to know **direction, body site, environment, host, evidence type and source** for every claim. They also need to see **disagreement** instead of having it hidden.

A direct edge such as `NCBITaxon:817 RO:0002610 MONDO:0005575` can hold none of this. Two contradictory findings collapse into one triple.

Options considered:

1. **Direct edges only.** Simple queries and a small graph, but context and provenance are lost.
2. **Named graph per source.** Provenance only at dataset level; still no per-claim direction or body site.
3. **RDF-star / RDF 1.2 triple terms.** Elegant, but support across triple stores (and federation with VERDANT's endpoint) is still uneven.
4. **Association nodes** (the n-ary relation pattern used by Biolink, SIO and KG-Microbe). Each claim is a resource with `rdf:subject`, `rdf:predicate`, `rdf:object` and context slots.

## Decision

Use **option 4** as the source of truth, and add a **derived layer of direct edges**:

- Every claim is an instance of a subclass of `Association` (`schema/associations.yaml`).
- `scripts/materialise_shortcuts.rq` builds `?s ?p ?o` edges into the named graph `<https://w3id.org/micokg/graph/shortcuts>`. It leaves out negated associations and those with confidence below 0.5.
- Raw per-sample measurements are SOSA `Observation`s. Associations can point back to them with `prov:wasDerivedFrom`.

## Consequences

- ✅ Conflicting and context-dependent findings coexist and can be queried (`uc3-cq02`).
- ✅ It aligns with Biolink / KG-Microbe / MicrobiomeKG, so crosswalks are cheap.
- ✅ Graph-ML users can take the shortcut graph, and use association attributes as edge features.
- ⚠️ Queries are longer: 3 triple patterns per hop instead of 1.
- ⚠️ More triples. This is acceptable at the expected scale; revisit if needed.
- ⚠️ Shortcut thresholds (confidence ≥ 0.5, not negated) are a policy that needs community agreement.
