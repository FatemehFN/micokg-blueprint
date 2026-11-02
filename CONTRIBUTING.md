# Contributing to MiCoKnowGraph

Thank you for helping build a shared microbiome knowledge graph! Contributions of every kind count: competency questions from domain experts, ontology evaluation, mappings, toy or real data, schema design, queries, documentation, and infrastructure.

By participating you agree to follow the [Code of Conduct](CODE_OF_CONDUCT.md).

## Ways to contribute

| I want to… | Start here |
|---|---|
| Suggest a question the KG should answer | Open a **Competency question** issue |
| Propose a class, slot or modelling change | Open a **Schema change** issue |
| Propose or review a mapping | Open a **Mapping proposal** issue, or review a PR in `mappings/verdant/candidates/` |
| Add an existing KG or resource to the landscape | Open a **KG / resource** issue |
| Report something broken | Open a **Bug** issue |

New here? Look for issues labelled `good-first-issue`, and read [docs/onboarding.md](docs/onboarding.md).

## Workflow

1. Comment on, or assign yourself to, an issue so others know you're on it.
2. Create a branch: `git checkout -b uc3/add-cq04-butyrate-crc`.
3. Make your change and run `make all` (or at least `make validate test`).
4. Open a pull request and fill in the checklist.
5. One reviewer from the owning group approves (see `.github/CODEOWNERS`). **Schema changes also need a reviewer from Group A (core schema).**
6. PRs are squash-merged.

## Conventions

- **Identifiers:** CURIEs for ontology terms; `micokg:<type>/<local-id>` for instances. See [docs/modelling-guide.md](docs/modelling-guide.md).
- **Dates:** quoted ISO strings in YAML (`"2024-02-10"`).
- **Every schema element** has a `description`; every slot has a `slot_uri`.
- **Every competency question** has toy data that answers it and an expected-results CSV that you checked by hand.
- **Design decisions** get an ADR in `docs/adr/`, numbered sequentially.
- **Mappings** follow SSSOM and include `mapping_justification`, and `author_id` / `reviewer_id` as ORCIDs.

## Labels

`schema` · `mappings` · `landscape` · `uc1-aero` · `uc2-amr` · `uc3-cancer` · `uc4-nutrition` · `verdant` · `docs` · `infra` · `good-first-issue` · `needs-decision`

## Credit

- Add yourself to `CITATION.cff` in your first PR, with your ORCID.
- Contributors are listed as authors of the BioHackrXiv preprint (`paper/paper.md`), with [CRediT](https://credit.niso.org/) roles.
