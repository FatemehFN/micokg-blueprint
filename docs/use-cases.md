# Use cases and competency questions

Competency questions (CQs) are the questions the knowledge graph must be able to answer. Each has a SPARQL query, toy data designed to exercise it, and an expected result checked in CI.

| Use case | Queries | Toy data |
|---|---|---|
| UC1 Aeromicrobiome functional characterisation | `queries/uc1-aeromicrobiome/` | `examples/valid/Container-uc1-aeromicrobiome.yaml` |
| UC2 Antimicrobial resistance transmission | `queries/uc2-amr-transmission/` | `examples/valid/Container-uc2-amr.yaml` |
| UC3 Host–microbiome interactions in cancer ⭐ | `queries/uc3-host-microbiome-cancer/` | `examples/valid/Container-uc3-cancer.yaml` |
| UC4 Metabolic impact of nutrition | `queries/uc4-nutrition-metabolism/` | `examples/valid/Container-uc4-nutrition.yaml` |

⭐ UC3 is the reference use case; copy its structure.

## UC1: Aeromicrobiome

| ID | Question | Tests the model on… |
|---|---|---|
| uc1-cq01 | Which GO processes are detected in air samples, per local setting? | ENVO sample context, gene function, subclass closure |
| uc1-cq02 | Which air taxa carry stress-survival genes (sporulation, UV, desiccation)? | gene → taxon, GO hierarchy |
| uc1-cq03 | Which air taxa have humans as a host? | bridging observations to taxon–host interactions |

## UC2: AMR transmission

| ID | Question | Tests the model on… |
|---|---|---|
| uc2-cq01 | Which determinants found in waste water appear later in human stool from the same place? | place and time joins, host taxon via `host/in_taxon` |
| uc2-cq02 | Which determinants on mobile elements are carried by more than one taxon? | SO genomic context, aggregation |
| uc2-cq03 | Which drug classes are affected by determinants in all three One Health compartments? | compartment enum, ARO drug classes |

## UC3: Host–microbiome in cancer

| ID | Question | Tests the model on… |
|---|---|---|
| uc3-cq01 | Which taxa are associated with colorectal cancer (subtypes and DOID/NCIT equivalents included)? | disease hierarchy, SSSOM expansion, evidence |
| uc3-cq02 | Are findings consistent, conflicting, or from a single study? | reified associations keeping contradictory claims |
| uc3-cq03 | Which genotoxic or carcinogenic metabolites are produced by CRC-associated taxa? | chaining association types, ChEBI roles |

## UC4: Nutrition

| ID | Question | Tests the model on… |
|---|---|---|
| uc4-cq01 | Which diets increase butyrate-producing taxa? | diet → taxon → metabolite |
| uc4-cq02 | Food → taxon → metabolite → disease: which outcomes, in which direction? | 3-hop chains |
| uc4-cq03 | Which diet-induced metabolite changes have no known producer? | gap analysis with `FILTER NOT EXISTS` |

## Proposing a new competency question

Open a **Competency question** issue. A good question:

- names the **entities** involved (taxon, habitat, disease…) and the **context** that matters (body site, time, place);
- includes a **concrete example answer** from your domain, so toy data can be written;
- says which **existing resource** could supply real data (e.g. MGnify, CARD, gutMDisorder).

Squads then add the query, toy data and expected result (see [Onboarding](onboarding.md#4-typical-contributions)).
