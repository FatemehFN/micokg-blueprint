# Modelling guide

These are the conventions used in `schema/` and `examples/`. The reasons behind them are in the design notes in `docs/adr/`.

## Principles

1. **Competency questions drive the model.** Every class or slot should serve at least one question in `queries/`. If no question needs it, it waits.
2. **Reuse before you invent.**
   - Use an existing ontology identifier for things: NCBITaxon, ENVO, MONDO, ChEBI and so on.
   - Use an existing standard property for relations: MIxS, SOSA, RO, DCTERMS, PROV.
   - Mint `micokg:` terms only when nothing fits, and write down why.
3. **Keep measurements separate from claims.** Per-sample measurements are `Observation`s. Generalised or literature-derived statements are `Association`s.
4. **Keep context with the claim.** Direction, body site, environment, host, evidence and source live on the association node ([ADR-0001](adr/0001-association-reification.md)).

## Identifiers

| Kind of thing | Identifier | Example |
|---|---|---|
| Organism, habitat, anatomy, disease, chemical, function, AMR gene family | Ontology CURIE | `NCBITaxon:851`, `ENVO:00002005`, `ARO:3000186` |
| Sample, observation, association, study, host, gene record | Minted `micokg:<type>/<local-id>` | `micokg:sample/UC3-S01` |
| Person | ORCID | `ORCID:0000-0002-...` |
| Publication | `doi:` or `PMID:` | `doi:10.1234/abcd` |
| Source resource | infores CURIE | `infores:gutmdisorder` |

Type segments currently in use: `study`, `sample`, `host`, `obs`, `assoc`, `gene`, `property`.

## Slots with ontology values

Ontology-valued slots have `range: uriorcurie` and a `pattern` restricting the prefix, and they may declare `bindings` to a dynamic enum (the allowed ontology branch):

```yaml
env_medium:
  slot_uri: mixs:0000014
  range: uriorcurie
  pattern: "^(ENVO:\\d{8}|UBERON:\\d{7})$"
  bindings:
    - range: EnvironmentalMaterialEnum
      obligation_level: RECOMMENDED
```

**Why not an enum?** LinkML writes enum values to RDF as string literals, but queries need IRIs so that they can follow `rdfs:subClassOf`. `tests/test_rdf_shacl.py::test_ontology_slots_are_iris` guards this. Static enums are fine for small internal code lists such as `direction` and `compartment`.

## Naming

- Classes are `UpperCamelCase`; slots and enum values are `snake_case`.
- Association classes are named `<Subject><Object>Association`, or `...Interaction` for organism–organism.
- Every slot has a `slot_uri`. Choose, in order:
  1. an established standard (MIxS, SOSA, DCTERMS, PROV, SKOS, RDFS);
  2. an OBO Relation Ontology property (RO);
  3. `micokg:<slot_name>`.

## Adding a new association type (worked recipe)

Example: *taxon produces a quorum-sensing molecule that affects host inflammation*.

1. **Write the competency question first.**
2. **Check whether an existing class fits.** Here `TaxonMetaboliteAssociation` plus `MetaboliteDiseaseAssociation` already chain.
3. If a new class is needed, add it to `schema/associations.yaml`:

    ```yaml
    TaxonPhenotypeAssociation:
      is_a: Association
      class_uri: micokg:TaxonPhenotypeAssociation
      description: A taxon is associated with a host phenotype.
      slot_usage:
        subject:
          pattern: "^(NCBITaxon:\\d+|GTDB:.+)$"
        predicate:
          pattern: "^RO:(0002610|0003302)$"
        object:
          pattern: "^(HP|MP|NCIT):[A-Za-z0-9_]+$"
    ```

4. Add a list slot to `Container` in `schema/micokg.yaml` (`taxon_phenotype_associations`), and any new prefixes.
5. Add toy data to `examples/valid/`, plus an `examples/invalid/` file showing a common mistake.
6. Add the `.rq` query and the `cqs.yaml` entry, then run `make slims` (for the new terms) and `make test`.

## Observations

- `observed_property` is a `micokg:property/...` IRI for now (`relative_abundance`, `gene_presence`). *Open question:* adopt a published property vocabulary (e.g. from OBA, STATO or the MIxS measurement terms).
- `simple_result` is a number. Use `0` for "tested and not detected", and simply leave out things that weren't tested.
- `used_procedure` should point to an OBI assay or a bio.tools/WorkflowHub identifier.

## Open questions

| # | Question | Current choice |
|---|---|---|
| 1 | MONDO or DO as the preferred disease ontology? | MONDO first; DO/NCIT/EFO accepted, bridged by SSSOM |
| 2 | NCBITaxon vs GTDB for MAG-derived taxa | Both accepted; mapping file needed |
| 3 | Plasmid is not under `mobile_genetic_element` in SO. How should "mobile context" be modelled? | Queries list both roots |
| 4 | How to represent negative findings (no association found)? | `negated: true`; excluded from shortcuts |
| 5 | Meaning and calibration of `confidence` across sources | Free float 0–1; needs a definition |
| 6 | Units and normalisation for abundance | `unit` slot; no vocabulary chosen yet (QUDT/UO?) |
| 7 | Imaging and clinical data | Future modules (`imaging.yaml`, `clinical.yaml`) |
| 8 | Individual-level host data and privacy | Hosts are pseudonymous toy records; real data only aggregated? |
| 9 | Reification in RDF 1.2 (triple terms) vs association nodes | Association nodes (see ADR-0001) |
