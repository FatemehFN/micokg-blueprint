# Onboarding

Goal: go from a fresh clone to a green `make all` and your first query in about 15 minutes.

## 1. Set up the environment

You need Python **3.12 or 3.13**. LinkML does not support 3.14 yet. Java and Docker are not needed.

```bash
git clone https://github.com/FatemehFN/micokg-blueprint.git && cd micokg-blueprint
mamba env create -f environment.yml      # conda works too
mamba activate micokg
```

!!! tip "If `conda activate` / `mamba activate` does not work in your shell"
    Run commands through the environment instead: `mamba run -n micokg make all`.
    Or put it on your PATH for the session: `export PATH="$HOME/miniforge3/envs/micokg/bin:$PATH"`.

Without conda:

```bash
python3.12 -m venv .venv && source .venv/bin/activate && pip install -e ".[dev]"
```

## 2. Build and test everything

```bash
make all
```

This runs, in order:

| Target | What it does |
|---|---|
| `lint` | `linkml-lint` style and consistency checks on `schema/` |
| `validate` | every `examples/valid/*.yaml` must pass and every `examples/invalid/*.yaml` must fail |
| `gen` | OWL, SHACL, JSON-LD context and Markdown docs into `build/` and `docs/schema/` |
| `rdf` | converts the YAML examples to Turtle in `build/rdf/` |
| `shacl` | checks that RDF conforms to the generated SHACL shapes |
| `mappings` | validates SSSOM files and converts them to RDF |
| `spex` | exports queries as SIB SPARQL examples into `build/sparql-examples/` |
| `test` | the full pytest suite, including every competency question |

## 3. Run a competency question

```bash
python scripts/run_cq.py              # list all questions
python scripts/run_cq.py uc3-cq02     # run one
```

```
taxon          taxonLabel                    nStudies  directions           status
NCBITaxon:817  Bacteroides fragilis          2         decreased|increased  conflicting
NCBITaxon:562  Escherichia coli              1         increased            single study
...
```

Try an ad-hoc query: copy a `.rq` file, edit it, then run `python scripts/run_cq.py --query my.rq`.

## 4. Typical contributions

**Add data for a use case**

1. Edit `examples/valid/Container-ucN-*.yaml`.
2. Look up identifiers in [OLS](https://www.ebi.ac.uk/ols4/) and paste the CURIE, e.g. `ENVO:00002005`.
3. Quote dates: `"2024-02-10"`.
4. Run `make validate`.
5. Run `make slims` when you use new ontology terms. It needs internet access and updates `examples/ontology-slims/`, which you commit.

**Add a competency question**

1. Add a `.rq` file and an entry in `queries/ucN-*/cqs.yaml`.
2. Add toy data that should produce an answer.
3. Run `python scripts/run_cq.py <id>`. Check the output **by hand**, then write it with `--write-expected`.
4. Run `make test`.

**Change the schema**

1. Edit the relevant `schema/*.yaml` module.
2. Run `make lint validate test`.
3. If the change is a design decision, add a note in `docs/adr/`.

**Add or review mappings.** See [VERDANT integration](verdant-integration.md).

## 5. Where things live

```
schema/micokg.yaml          root schema: prefixes, imports, Container
schema/*.yaml               modules: core, enums, entities, samples_observations, provenance, associations
examples/valid/             toy data per use case (one Container per file)
examples/invalid/           examples that must be rejected (documents the rules)
examples/ontology-slims/    is_a hierarchy + labels for terms used (built from OLS)
mappings/curated/           reviewed SSSOM mappings
mappings/verdant/           VERDANT candidates and rejections
queries/ucN-*/              cqs.yaml + one .rq per competency question
tests/expected/             expected query results (CSV)
scripts/kg.py               builds the in-memory KG used by tests and run_cq.py
```

## Troubleshooting

| Symptom | Fix |
|---|---|
| `datetime.date(...) is not of type 'string'` | Quote the date in YAML |
| `does not match '^ENVO:\d{8}$'` | Use the CURIE, not the label or full IRI |
| A query returns nothing after you add a new term | Run `make slims`; subclass queries need the term's hierarchy |
| `FileNotFoundError: .../associations.yaml` | Run LinkML CLIs from the repo root via `make`; the scripts handle import paths |
| `No module named linkml` in your editor | Select the `micokg` environment as the Python interpreter |
