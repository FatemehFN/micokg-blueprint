# MiCoKnowGraph

**A collaborative, interoperable knowledge-graph blueprint for microbiome research.**

This is a **personal draft blueprint** prepared by Fatemeh Nasrollah (EMBL-EBI) as a starting point for [BioHackathon Europe 2026, Project 16](https://github.com/elixir-europe/biohackathon-projects-2026/blob/main/16.md), led by the ELIXIR Microbiome Community and partnered with [Project 11, VERDANT](https://github.com/elixir-europe/biohackathon-projects-2026/blob/main/11.md). It is not the project's official repository: the co-leads decide what, if anything, is adopted.

Microbiome knowledge graphs today (microbe–disease, microbe–host, AMR, diet) are fragmented and don't link up. This project designs **one shared schema** with the community, and tests it with real **competency questions** from four use cases.

> **Status: v0.1 starter blueprint.** The toy data is invented, but every ontology identifier is real. Expect the model to change during the hackathon (9–13 Nov 2026).
>
> **Provenance:** drafted before the event with substantial help from Claude (Anthropic's AI assistant) and reviewed by a human. Treat it as a strawman to argue with, not a decision. The use cases here were drafted from the project proposal and will be realigned to the use cases and competency questions in the organisers' coordination sheet.

## What is in the blueprint

| Layer | What | Where |
|---|---|---|
| **Entities** | Taxa, genes, AMR determinants, metabolites, diseases, foods, all identified by existing ontology IRIs (NCBITaxon, GO, ARO, ChEBI, MONDO, FoodOn, ENVO, UBERON) | [`schema/entities.yaml`](schema/entities.yaml) |
| **Samples and observations** | MIxS environmental context; SOSA observations (what was measured, in which sample, and how) | [`schema/samples_observations.yaml`](schema/samples_observations.yaml) |
| **Associations** | Claims stored as nodes (taxon–disease, diet–taxon, and so on), each carrying direction, body site, evidence (ECO) and source study, so that conflicting findings can coexist | [`schema/associations.yaml`](schema/associations.yaml) |
| **Mappings** | SSSOM tables linking equivalent identifiers (e.g. DOID→MONDO), including VERDANT candidates | [`mappings/`](mappings/) |
| **Competency questions** | SPARQL queries per use case, run as tests against the toy KG and exported in SIB SPARQL-examples format | [`queries/`](queries/) |

### Use cases

| Use case | Example question |
|---|---|
| [UC1 Aeromicrobiome](queries/uc1-aeromicrobiome/cqs.yaml) | Which taxa in air carry stress-survival functions? |
| [UC2 AMR transmission](queries/uc2-amr-transmission/cqs.yaml) | Which resistance genes seen in waste water show up later in human stool from the same city? |
| [UC3 Host–microbiome in cancer](queries/uc3-host-microbiome-cancer/cqs.yaml) ⭐ | Which taxa are associated with colorectal cancer, and where do studies disagree? |
| [UC4 Nutrition](queries/uc4-nutrition-metabolism/cqs.yaml) | Which diets increase butyrate-producing taxa, and what outcomes follow? |

⭐ UC3 is the fully documented reference; copy its pattern.

## Quick start

```bash
mamba env create -f environment.yml     # or: conda env create -f environment.yml
mamba activate micokg
make all                                 # lint, validate, generate OWL/SHACL/docs, build RDF, run tests
python scripts/run_cq.py                 # list competency questions
python scripts/run_cq.py uc3-cq02        # run one against the toy KG
```

Python 3.12 or 3.13 is required (LinkML does not support 3.14 yet). The full walkthrough is in [docs/onboarding.md](docs/onboarding.md). If RDF and ontologies are new to you, start with [docs/kg-primer.md](docs/kg-primer.md).

## Repository map

```
schema/            LinkML schema (modules)        examples/valid|invalid/  toy data (YAML)
mappings/          SSSOM mapping sets             examples/ontology-slims/ ontology extracts for offline tests
queries/ucN-*/     competency questions (.rq)     tests/                   pytest suite (+ expected results)
landscape/         existing KGs and ontologies    scripts/                 build and conversion tools
docs/              guides and ADRs                paper/                   BioHackrXiv preprint
```

## Contributing

Everyone is welcome, whatever your background: domain experts, ontologists, data engineers. See [CONTRIBUTING.md](CONTRIBUTING.md), and pick an issue labelled `good-first-issue` or one tied to your use case. The hackathon plan is in [ORGANISING.md](ORGANISING.md).

## Related BioHackathon 2026 projects

- **#11 VERDANT:** AI-generated ontology mappings and a federated SPARQL endpoint. See [docs/verdant-integration.md](docs/verdant-integration.md).
- **#19 Exposome ontology cross-mapping:** shared SSSOM mappings for ENVO, ChEBI and FoodOn.
- **#15 Training KG:** SIB SPARQL-examples conventions.
- **#12 SampleSift:** spatial querying of MGnify/ENA samples.
- **#30 BiCoReCa:** tool and workflow identifiers.

## License

Code: [MIT](LICENSE). Schema, mappings, queries, data and documentation: [CC BY 4.0](LICENSE-CONTENT).

Project co-leads (per the project proposal): Nikolaos Strepis, Bérénice Batut, Brieuc Quemeneur.
