# MiCoKnowGraph draft blueprint

A draft data model for a microbiome knowledge graph, written for [BioHackathon Europe 2026, Project 16 (MiCoKnowGraph)](https://github.com/elixir-europe/biohackathon-projects-2026/blob/main/16.md).

I put this together before the event as something concrete to discuss. It is a starting point, not a proposal. I drafted it with help from Claude and reviewed it myself. The toy data is invented, including the studies, people and papers in it. The ontology terms are real.

Docs: <https://fatemehfn.github.io/micokg-blueprint/>

## What is in it

| Part | What it does | Where |
|---|---|---|
| Schema | A [LinkML](https://linkml.io) model in three layers. Entities: taxa, genes, metabolites, diseases and foods, identified by ontology terms. Samples and observations: MIxS context plus SOSA measurements. Associations: claims such as "taxon X is increased in disease Y", stored as nodes so that direction, body site, evidence and source stay attached and conflicting findings can coexist | `schema/` |
| Toy data | One small dataset per use case, validated against the schema | `examples/valid/` |
| Competency questions | 12 questions as SPARQL queries. Each runs as a test against the toy data | `queries/`, `tests/` |
| Mappings | SSSOM tables linking equivalent identifiers, for example DOID to MONDO | `mappings/` |
| Docs | A primer on RDF, ontologies and SPARQL, a modelling guide, and three design notes | `docs/` |

## Use cases

The four use cases below come from the project proposal. They do not yet match the use cases in the organisers' coordination sheet; realigning them is the next step.

| Use case | Example question |
|---|---|
| [UC1 Aeromicrobiome](queries/uc1-aeromicrobiome/cqs.yaml) | Which taxa in air carry stress-survival functions? |
| [UC2 AMR transmission](queries/uc2-amr-transmission/cqs.yaml) | Which resistance genes seen in waste water show up later in human stool from the same city? |
| [UC3 Host–microbiome in cancer](queries/uc3-host-microbiome-cancer/cqs.yaml) | Which taxa are associated with colorectal cancer, and where do studies disagree? |
| [UC4 Nutrition](queries/uc4-nutrition-metabolism/cqs.yaml) | Which diets increase butyrate-producing taxa, and what outcomes follow? |

UC3 is the most complete one. The full list is in [docs/use-cases.md](docs/use-cases.md).

## Run it

Needs Python 3.12 or 3.13.

```bash
mamba env create -f environment.yml     # or conda
mamba activate micokg
make all                                 # lint, validate, generate OWL/SHACL, build RDF, run tests
python scripts/run_cq.py                 # list competency questions
python scripts/run_cq.py uc3-cq02        # run one against the toy data
```

Step by step instructions are in [docs/onboarding.md](docs/onboarding.md). If RDF and ontologies are new to you, start with [docs/kg-primer.md](docs/kg-primer.md).

## Layout

```
schema/            LinkML schema, one file per module
examples/          toy data (valid and deliberately invalid), ontology slims for offline tests
queries/           competency questions, one .rq file each
tests/             pytest suite with expected query results
mappings/          SSSOM mapping tables
docs/              guides and design notes
scripts/           build and conversion tools
```

The inventory of existing knowledge graphs, data sources and ontologies is kept in the project's coordination sheet, not here.

## Related

Project 11 ([VERDANT](https://github.com/elixir-europe/biohackathon-projects-2026/blob/main/11.md)) generates ontology mappings; [docs/verdant-integration.md](docs/verdant-integration.md) sketches how its output could feed the mapping tables here.

## License

Code: [MIT](LICENSE). Schema, mappings, queries, data and documentation: [CC BY 4.0](LICENSE-CONTENT).
