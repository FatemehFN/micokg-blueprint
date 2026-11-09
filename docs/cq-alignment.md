# Competency questions from the coordination sheet

The team's use cases and competency questions (CQs) live in the project's coordination sheet. This page checks the nine CQs written there (as of 8 November 2026) against the schema in this repository: what each one needs, what the schema already holds, and what would have to be added. It ends with the additions in priority order and a suggestion for which CQs to translate into SPARQL first.

The CQs are quoted in short form; the full text, entities and relationships are in the sheet ("Task 1 - Competency Questions").

## Use cases: sheet versus this repository

| Sheet | Owner | Repository | Fit |
|---|---|---|---|
| Use case 1, Photosynthetic biodiversity and activity in clouds | Bérénice | UC1 Aeromicrobiome | Same domain (air samples, taxa, gene functions). The sheet's version is about one site (Puy de Dôme), photosynthetic organisms, and many physical measurements. |
| Use case 2, Plasmids in the microbiome of diseases, especially cancer | Niko | UC2 AMR transmission and UC3 Host–microbiome in cancer | Covers both: taxa associated with tumours (UC3) and AMR genes on mobile elements (UC2). Plasmids as objects in their own right are new. |
| Use case 3, Sociability and gut bacteria in a macaque population | Caprice | none | New. Needs host-level behaviour and health attributes; see the end of this page. |
| Use case 4 | not started | | |
| Use case 5, SynCom traits in crop biocontrol | Pedro | none | New. Needs field-trial design, treatments and synthetic communities; see the end of this page. |
| none | | UC4 Nutrition | Not in the sheet. Kept as it exercises diet, taxon, metabolite and disease chains, which CQ 9 also needs. |

## How to read the verdicts

- **Answerable now**: the schema holds the data and the query can be written against the toy data.
- **Small addition**: a slot, enum or class is missing; the addition is listed and is a few lines of LinkML.
- **Not a schema question**: the relationship in the sheet is a comparison or statistic that a query computes (`comparedTo`, `differsFrom`, `hasSimilarity`), or a mechanistic claim that would only ever be a literature statement with free text behind it. These are noted and not modelled.

## Use case 1: clouds

### CQ 1. Taxa, diversity indices and abundances of photosynthetic versus non-photosynthetic organisms in cloud samples at Puy de Dôme

| Needs | Status |
|---|---|
| Samples at a named site, with date, coordinates, altitude, sampling method and weather | `Sample` has `geo_location`, `geo_loc_name`, `latitude`, `longitude`, `collection_date`, `env_*` (ENVO). Altitude and weather are not slots; they can be sample-level observations (addition 1) or MIxS air-package slots. |
| Relative or absolute abundance of a taxon in a sample (`hasAbundance`) | Answerable now: `Observation` with `observed_property` relative_abundance, `is_about` the taxon, `simple_result`, `unit` (cells/m³, gene copies). |
| Diversity indices per sample (`hasDiversityMetric`) | Small addition 1: a Shannon index is about the sample, not a taxon, but `is_about` is required. |
| Grouping taxa as photosynthetic or not (`belongsToGroup`) | Small addition 4: a taxon-level trait, e.g. taxon *capable of* photosynthesis (GO:0015979). Cyanobacteria can also be found by taxonomy alone. |
| `comparedTo` | Not a schema question: the query groups by trait and compares. |

Verdict: **small additions 1 and 4**. The taxon-and-abundance half is answerable now.

### CQ 2. Physiological state of photosynthetic organisms and the effect of stressors on photosynthetic efficiency

| Needs | Status |
|---|---|
| Measurements per sample or per organism: PSII yield, chlorophyll fluorescence, pigments, carbon fixation rate, gene expression (psbA, rbcL) | Addition 1 for sample-level values; gene expression is an `Observation` `is_about` a `FunctionalGene` with a new observed property (expression) and unit. |
| Stressor levels (UV index, temperature, pH, nutrients) | Addition 1: sample-level observations, or MIxS slots. |
| Physiological state as a category (active, dormant, stressed, damaged) | Small addition 2: `simple_result` is numeric only; categorical results need an ontology-term result. |
| `influencedBy`: stressor changes efficiency | Not a schema question in this round; it is a finding, not a measurement. Could later be an association between an exposure and a process. |

Verdict: **small additions 1 and 2** for the measurements; the mechanistic half is not modelled.

### CQ 3. Enriched carbon-fixation pathways and genes, compared with non-photosynthetic organisms

| Needs | Status |
|---|---|
| Genes (cbbL, ccmK, prk, ppc) with function and host taxon (`exhibitsGene`) | Answerable now: `FunctionalGene` with `gene_symbol`, `has_function` (GO), `gene_family` (KO, EC), `in_taxon`. |
| Pathways (`hasMetabolicPathway`) | GO biological processes cover them (e.g. GO:0015977 carbon fixation, GO:0019253 reductive pentose-phosphate cycle). A KEGG pathway identifier can go in `gene_family` today; a `Pathway` class is optional. |
| Gene presence or abundance per sample | Answerable now (`gene_presence`; add an abundance or expression property). |
| Enzyme activity, carbon flux, measured under conditions (`measuredUnder`) | Addition 1: sample-level observations; conditions are other observations on the same sample, joined by sample. |
| `comparesTo` | Not a schema question. |

Verdict: **answerable now for genes and pathways; addition 1 for the rates**.

### CQ 4. Metabolic by-products and their effect on cloud chemistry

| Needs | Status |
|---|---|
| Organism produces by-product (`producesByproduct`) | Answerable now: `TaxonMetaboliteAssociation` with RO:0002234 *has output* and a ChEBI object (oxalic acid, hydrogen peroxide, isoprene). |
| Cloud chemistry parameters (pH, ROS, ions) per sample | Addition 1. |
| By-product changes a parameter (`influencesChemistry`, `hasMechanism`) | Not a schema question in this round: chemistry and mechanism belong to the literature, not the KG's measurements. |

Verdict: **answerable now for production; addition 1 for chemistry; mechanisms not modelled**.

### CQ 5. Biogeographical differences between Puy de Dôme and other sites

| Needs | Status |
|---|---|
| Sites and their community composition (`hasComposition`) | Answerable now: aggregate observations by `geo_location`. |
| Atmospheric conditions per site | Addition 1. |
| Functional traits of taxa (`hasTrait`, `adaptsTo`) | Addition 4 (taxon trait association). |
| Ecological interactions (`interactsWith`) | Answerable now: `TaxonHostAssociation` with RO:0002437 *biotically interacts with*; competition and mutualism are RO sub-relations and could be allowed in the predicate pattern. |
| `differsFrom`, `hasSimilarity` | Not a schema question: beta diversity is computed. |

Verdict: **small additions 1 and 4**.

### CQ 6. Diurnal, cloud-lifecycle and seasonal variation of photosynthetic activity

| Needs | Status |
|---|---|
| Time of day of sampling | Small addition 3: `collection_date` is a date; a datetime, or a separate time slot, is needed for day/night. |
| Cloud lifecycle stage and season as sample attributes | Addition 3: a categorical sampling-context slot (or a categorical observation, addition 2). |
| Activity metrics and gene expression over time | Addition 1 plus `result_time`, which exists. |
| `variesWith`, `drivenBy`, `correlatesWith`, `hasAmplitude` | Not a schema question: computed over the time series. |

Verdict: **small additions 1, 2 and 3**.

## Use case 2: plasmids in cancer

### CQ 7. Taxa, plasmid replicons, diversity and abundance in tumour versus adjacent normal tissue and healthy controls

| Needs | Status |
|---|---|
| Specimen from a body site, with pathology status (`sampledFrom`) | `host_body_site` (UBERON) exists. Tumour versus adjacent normal versus healthy is a small addition 3: a sample condition slot (NCIT or MONDO term). Specimen type (FFPE, fresh-frozen, stool, cell-free DNA) is a second slot in the same addition. |
| Patient's cancer type | Answerable now: `Host.has_disease` (MONDO). |
| Taxon abundance per sample | Answerable now. |
| Plasmids with replicon type, mobility class, copy number, host taxon (`harboursPlasmid`, `hasMobilityClass`, `hasCopyNumber`) | Small addition 5: a `Plasmid` (mobile genetic element) class. Today only genes know they sit on a plasmid (`genomic_context` SO:0000155). |
| Diversity indices | Addition 1. |
| Fold change, p-values, LDA scores, tumour versus normal (`comparedTo`) | Answerable now as claims: `TaxonDiseaseAssociation` with `direction`, `effect_size`, `p_value`, `anatomical_context`, `has_evidence`, `source_study`. The existing query `uc3-cq01` (taxa associated with colorectal cancer, with direction and evidence) is a working subset of this CQ. |

Verdict: **small additions 1, 3 and 5**. The differential-abundance half is answerable now.

### CQ 8. Longitudinal resistome and plasmid evolution across clinical milestones

| Needs | Status |
|---|---|
| AMR genes with ARO class, drug class, mechanism, on plasmids | Answerable now: `AMRDeterminant` with `aro_class`, `confers_resistance_to`, `resistance_mechanism`, `genomic_context`. |
| Repeated samples from one patient over time | Answerable now: `Sample.has_host` plus `collection_date`. |
| Clinical milestones and treatments with dates (`variesAcrossTimepoint`, `drivenBySelectivePressure`, `hasBaseline`) | Small addition 6: host-level events (antibiotic given, chemotherapy, surgery, relapse) with a type and a date, so observations can be placed before or after them. |
| Genes co-located on one plasmid (`coSelectedWith`) | Addition 5: a plasmid record that lists the genes it carries. |
| `exhibitsEvolutionaryShift` (IS26 amplification, co-integrates, SNPs) | Not a schema question in this round: genome-structure findings per strain are better kept in the source data and cited. |
| `precedesClinicalEvent` | Derivable from dates once addition 6 exists; the causal reading stays with the literature. |

Verdict: **small additions 5 and 6**; the AMR gene layer is answerable now.

### CQ 9. Antibiotics before immunotherapy: depletion of commensals, resistome expansion, metabolites and treatment response

| Needs | Status |
|---|---|
| Antibiotic decreases a taxon (`depletesTaxon`) | Nearly now: `DietTaxonAssociation` accepts a CHEBI subject and `direction` decreased, but its name says diet. Small addition 7: rename it to an exposure-to-taxon association that covers foods and drugs. |
| Taxon produces metabolite, metabolite linked to outcome (`reducesMetabolite`, `impairsImmunePriming`) | Taxon to metabolite answerable now. Metabolite to outcome exists for diseases (`MetaboliteDiseaseAssociation`); immune processes would need GO or HP objects allowed in its pattern. |
| Resistome load and plasmid richness per sample (`enrichesPlasmidome`) | Answerable now for genes (observations about `AMRDeterminant` records, aggregated); plasmids need addition 5. |
| Therapy, exposure window and response (`attenuatesEfficacyOf`, `stratifiesPatientBy`) | Addition 6: events with dates, plus a response outcome on the host or the event. Stratification is then a query. |

Verdict: **small additions 5, 6 and 7**; the immunology chain is partly literature-only.

## Additions, in priority order

Each serves several CQs. None changes the three-layer design; they are slots, one enum and two classes.

| # | Addition | Serves | Sketch |
|---|---|---|---|
| 1 | **Sample-level observations.** Make `Observation.is_about` optional, so a measurement can be about the sample as a whole; publish a controlled list of observed properties (relative abundance, gene presence, gene expression, Shannon index, Simpson index, richness, pH, temperature, UV index, cell count, ...) with the ontology term where one exists (PATO, STATO, UO for units). | CQ 1–7 | `is_about: required: false`; `observed_property` bound to a `micokg:property/...` list documented in the modelling guide. |
| 2 | **Categorical results.** Add `result_term` (`sosa:hasResult`, range uriorcurie) beside `simple_result`, for states such as dormant or stressed. | CQ 2, 6 | one slot |
| 3 | **Sample condition and context.** Add `sample_condition` (NCIT/MONDO/PATO term: malignant tumour, adjacent normal, healthy control), `specimen_type` (OBI/NCIT: FFPE, fresh-frozen, stool, cfDNA), and either make `collection_date` a datetime or add `collection_time`; optionally a `sampling_context` note for cloud stage or season. | CQ 6, 7 | three slots on `Sample` |
| 4 | **Taxon trait association.** `TaxonTraitAssociation`: subject taxon, predicate RO:0002215 *capable of* (or RO:0000053 *has characteristic*), object GO process or PATO/OMP trait (photosynthesis, UV resistance, desiccation tolerance). | CQ 1, 3, 5 | one association class, same slots as the others |
| 5 | **Plasmid class.** `MobileGeneticElement` (or `Plasmid`): identifier (PLSDB accession or minted), `replicon_type` (text: IncF, IncI1, ColRNAI), `mobility_class` enum (conjugative, mobilisable, non-mobilisable), `in_taxon` (host), `carries_gene` (multivalued, to `FunctionalGene`/`AMRDeterminant`). Observations may be about it (abundance, copy number). | CQ 7, 8, 9 | one class, one enum, four slots |
| 6 | **Host events.** `HostEvent`: `host`, `event_type` (NCIT or CHEBI: antibiotic administration with the drug, chemotherapy, surgery, immune checkpoint blockade, relapse), `start_date`, `end_date`, optional `outcome` (responder, non-responder). | CQ 8, 9; also UC3 macaques and UC5 field trials | one class |
| 7 | **Exposure association.** Rename `DietTaxonAssociation` and `DietMetaboliteAssociation` to `ExposureTaxonAssociation` and `ExposureMetaboliteAssociation`, subject FOODON, CHEBI or NCIT (foods, drugs, antibiotics). | CQ 9, UC4 | rename plus pattern |

Not planned: storing comparisons (`comparedTo`, `differsFrom`, `hasSimilarity`), and mechanistic statements (`influencesChemistry`, `hasMechanism`, `exhibitsEvolutionaryShift`, `impairsImmunePriming`). The first group is computed by queries; the second would need free-text claims, which the sheet's own ontology column cannot ground either.

## Ontologies named in the sheet

The nine CQs name ENVO, PROV, NCBITAXON, GO, CHEBI, UBERON, MONDO, ARO, SO, OBI and RO. All are prefixes in the schema and used by at least one slot. Two are not: **PO** (Plant Ontology, named for CQ 2; it would only matter if plant hosts enter, as in Use case 5) and **BERO** (named for Use case 2 in the sheet; it is in the Ontologies tab but not in any CQ). The sheet's "Classes / concepts" column currently lists only PROV terms (Entity, Collection, Location, atLocation); the schema places those on `Study` (PROV/DCTerms) and `Sample` (`geo_location`).

## The two new use cases

**Use case 3, macaques (Caprice).** Hosts are *Macaca mulatta* (`Host.in_taxon`), samples are faeces (`env_medium` UBERON:0001988), taxa and diversity come from observations (addition 1). What is missing is host-level data: sociability score, grooming rate, social rank, immune status, sampling period. The cleanest route is to let an `Observation` have a `Host` as its feature of interest (today only `Sample`), so behaviour and health scores are observations on the animal with a date; the CQ then joins host observations to sample observations. That is addition 1 plus a one-line range change.

**Use case 5, SynCom in crop biocontrol (Pedro).** Soil and plant-tissue samples fit `Sample` (ENVO soil terms; plant tissue as `env_medium` with PO terms, which would bring PO in). New: a `SyntheticCommunity` entity (member strains, delivery formulation), a field trial with blocks and treatments (addition 6 generalised to events on plots, not hosts), pathogen pressure and yield as outcomes. This is the furthest from the current schema and should wait for the CQs to be written.

## Suggested order of work

1. **CQ 7, differential-abundance half.** Runs today on `uc3-cq01`; retarget the question text and toy data to tumour versus adjacent normal tissue with `anatomical_context`, and paste the query into the sheet's translation column.
2. **CQ 1, taxa-and-abundance half.** Needs toy cloud samples (ENVO cloud terms, Puy de Dôme coordinates) and relative-abundance observations; one query, answerable today. Diversity indices follow once addition 1 is in.
3. **Additions 1 and 5**, which unlock the rest of CQ 1 and CQ 7 and most of CQ 8.
4. Then CQ 3 (genes and pathways, mostly answerable now) and CQ 8.
