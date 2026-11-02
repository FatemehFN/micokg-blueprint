# ADR-0003: Ontology reuse and the use of slims

- **Status:** Proposed. To be ratified on hackathon Day 1.
- **Date:** 2026-09-15

## Context

The proposal names GO, ENVO, DO, SOSA, SIO, NCIT, UBERON, EFO and DCT, and the use cases add NCBITaxon, ChEBI, ARO, SO, FoodOn, ECO, OBI and MIxS.

- Importing whole ontologies into the schema is heavy (NCBITaxon alone is several GB) and makes CI slow.
- Queries still need hierarchy information, e.g. "colorectal adenocarcinoma is a colorectal cancer".
- Java/ROBOT tooling is not available to all contributors.

## Decision

1. **Reference ontologies by identifier; don't import them into the LinkML schema.**
2. **Standard vocabularies for properties:**

   | Vocabulary | Used for |
   |---|---|
   | MIxS | Sample environment slots |
   | SOSA | Observations |
   | RO | Biological relations |
   | DCTERMS / PROV | Provenance |
   | SKOS | Mappings |
   | SIO | `is about`; association class mapping |

3. **Slims for tests.** `scripts/build_slims.py` collects the is_a ancestors and labels of every term used in examples and curated mappings from the EBI OLS API, into `examples/ontology-slims/*.ttl`. The slims are committed, so tests run offline in seconds.
4. **Production** deployments should load full ontologies, or federate with a service that holds them (e.g. Ubergraph), instead of relying on slims.
5. **Branch checks.** Dynamic enums in `schema/enums.yaml` (`reachable_from`) describe the allowed branch for each slot. They are checked in the weekly `nightly-terms.yml` workflow, not in PR CI.

## Consequences

- ✅ Pure-Python tooling with fast, offline CI.
- ✅ The ontology evaluation matrix (`landscape/ontologies.tsv`) can change without schema churn.
- ⚠️ Slims have to be rebuilt (`make slims`) when new terms are used. The nightly job warns about drift.
- ⚠️ Ontology structure can surprise. For example, in SO, *plasmid* is not a subclass of *mobile_genetic_element*, so query authors must check hierarchies in OLS.
