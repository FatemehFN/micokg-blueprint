# Organising plan: BioHackathon Europe 2026, Project 16

> **Draft suggestion only.** Written by a participant before the event, not agreed with the co-leads. The official plan is the organisers' Google Doc and coordination sheet; this file is kept as a menu of ideas.

Dates assume the event runs **Mon 9 – Fri 13 November 2026**.

## Goals and deliverables

1. **Schema blueprint v0.2:** LinkML schema, OWL, SHACL, JSON-LD context and a docs site.
2. **Landscape:** inventory of existing microbiome KGs, plus an ontology evaluation matrix with decisions.
3. **Mappings:** curated SSSOM sets, including reviewed VERDANT candidates and rejected mappings.
4. **At least 12 competency questions** across the 4 use cases, with tested SPARQL templates exported in SIB format.
5. **Toy KG plus a real-data slice** (e.g. MGnify samples, CARD subset, gutMDisorder rows).
6. **VERDANT integration note** and a federated query demo.
7. **BioHackrXiv preprint**, with a tagged release and Zenodo DOI.
8. **Roadmap** of post-hackathon issues and a presentation to the ELIXIR Microbiome Community.

## Before the event

### By 28 Sep (weeks −8 to −6)
- [ ] Agree with co-leads: GitHub organisation, repository name, licences (MIT code / CC BY content)
- [ ] Register the `https://w3id.org/micokg/` redirect (PR to perma-id/w3id.org)
- [ ] Push this v0.1 blueprint; enable CI and GitHub Pages
- [ ] Decide which ADRs are ratified up front and which are left for Day 1

### By 12 Oct (weeks −6 to −4)
- [ ] Kick-off call with VERDANT leads: exchange contract (docs/verdant-integration.md), enrichment subset, endpoint
- [ ] Short syncs with Projects #19 (SSSOM reuse), #15 (SPARQL-examples format), #12 (MGnify sample metadata), #30 (tool identifiers)
- [ ] Recruit a domain champion per use case (Biodiversity → UC1, One Health/Health → UC2, Health → UC3, Food & Nutrition → UC4)

### By 26 Oct (weeks −4 to −2)
- [ ] Complete the `landscape/existing-kgs.tsv` TODO fields for the seeded resources
- [ ] Open 2–3 competency-question issues per use case; open 20–30 `good-first-issue` tickets
- [ ] Send a participant skills survey (ontologies, LinkML, SPARQL, domain)
- [ ] Record a 45-minute onboarding webinar (docs/kg-primer.md, association pattern, SSSOM)

### By 6 Nov (week −1)
- [ ] Tag `v0.1.0`
- [ ] One-page cheat sheet (prefixes, patterns, commands)
- [ ] Chat channel and a shared daily notes document
- [ ] Every participant has run `make all` successfully

## Subgroups

| Group | Owns | Suggested size |
|---|---|---|
| A: Core schema and ADRs | `schema/`, `docs/adr/` | 2–4 (one co-lead) |
| B: Landscape and ontology evaluation | `landscape/` | 2–4 |
| C: Mappings and VERDANT liaison | `mappings/`, `scripts/skos_to_sssom.py` | 2–3 + VERDANT delegate |
| D1–D4: Use-case squads | `queries/ucN-*/`, `examples/valid/*ucN*` | 2–4 each (champion + query writer) |
| E: Infrastructure, docs, paper | CI, docs site, `paper/` | 1–3 |

Daily: a 15-minute stand-up in the morning and a 15-minute demo of what merged at the end of the day.

## During the event

| Day | Focus | Exit criteria |
|---|---|---|
| **Mon 9 Nov** | Project intro; form subgroups. Ratify ADR-0001/0002/0003 (MONDO vs DO; NCBITaxon + GTDB). Squads finalise CQs. VERDANT sync. | ADRs merged; everyone has ≥1 assigned issue; CI green on everyone's machine |
| **Tue 10 Nov** | B fills the ontology matrix. A merges schema PRs from squads' gap reports. Squads extend toy data. C sets up curated SSSOM and runs the first VERDANT batch. | All toy data validates; ≥1 new CQ per use case passes |
| **Wed 11 Nov** | Queries for all CQs. Biolink/KG-Microbe crosswalk SSSOM. VERDANT curation session. Mid-week report. | ≥10 CQs green in CI |
| **Thu 12 Nov** | Real-data slice ingestion (MGnify / CARD / gutMDisorder). Federated query against VERDANT. Docs site live. Paper sections drafted per group. | Real slice loads; docs published; paper draft complete |
| **Fri 13 Nov** | Feature freeze; tag `v0.2.0` (Zenodo DOI). Final presentation. Finalise authors, ORCIDs, CRediT roles; submit to BioHackrXiv. Retrospective; create `post-hackathon` milestone. | Release, preprint and roadmap done |

## Risks

| Risk | Mitigation |
|---|---|
| Scope creep (imaging, clinical, exposome) | Future modules on the roadmap; core covers the 4 use cases only |
| Participants blocked by tooling | Pure-Python stack, onboarding doc, webinar, "make all works" check before the event |
| VERDANT output late | Fake fixture keeps the pipeline testable; integration is a Day 3–4 milestone, not a blocker |
| Ontology surprises (e.g. SO plasmid not an MGE) | Check hierarchies in OLS; slims make such issues visible in tests |
| Disagreement on disease ontology | Accept both, bridge via SSSOM, decide the preferred one on Day 1 |
