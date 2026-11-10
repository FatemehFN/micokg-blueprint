#!/usr/bin/env python3
"""Class and property counts for the ontologies in the coordination sheet, from OLS and BioPortal.

Fills the two pairs of columns in the sheet's "Task 2 - Ontologies" tab:
"Nb of classes / concepts (OLS)", "Nb of properties (OLS)",
"Nb of classes / concepts (BioPortal)", "Nb of properties (BioPortal)".

OLS (https://www.ebi.ac.uk/ols4) needs no key. BioPortal (https://bioportal.bioontology.org)
needs a personal API key: log in, open your account page, copy the key, and pass it
through the environment, never on the command line or in a file:

    export BIOPORTAL_API_KEY='...'
    python3 scripts/ontology_counts.py                 # both sources, all ontologies below
    python3 scripts/ontology_counts.py --only GO ENVO  # a subset
    python3 scripts/ontology_counts.py --csv counts.csv

The two portals count differently, so the numbers are not expected to agree:
OLS counts every class and every property (annotation properties included) in the
file it loaded, imports included; BioPortal counts the ontology's own classes and its
object/data properties, and may hold an older release. State the source next to the
number, as the sheet now does.

The ontology list is the sheet's "Short name" column on 10 November 2026. Add a row
to SHEET_TO_PORTALS when the sheet gains one; None means the portal does not host it.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.request

OLS = "https://www.ebi.ac.uk/ols4/api/ontologies/"
BIOPORTAL = "https://data.bioontology.org/ontologies/"

# sheet short name -> (OLS ontology id, BioPortal acronym). None = not hosted there.
# Traps already checked: BioPortal's "RO" is the Radiomics Ontology (Relations Ontology is OBOREL);
# HPO is "hp"/"HP"; PROV is "prov"/"PROVO"; schema.org is "schemaorg_http"/"SCHEMA";
# the Plant Trait Ontology is "to" in OLS and "PTO" on BioPortal; SNOMED on BioPortal is the US edition.
SHEET_TO_PORTALS: dict[str, tuple[str | None, str | None]] = {
    "ARO": ("aro", "ARO"), "BERO": (None, "BERO"), "BFO": ("bfo", "BFO"), "CHEAR": (None, "CHEAR"),
    "CHEBI": ("chebi", "CHEBI"), "COB": ("cob", "COB"), "DC": ("dc", "DC"), "DCTERMS": ("dcterms", "DCTERMS"),
    "ECTO": ("ecto", "ECTO"), "EFO": ("efo", "EFO"), "ENVO": ("envo", "ENVO"), "FAO": ("fao", "FAO"),
    "FOODON": ("foodon", "FOODON"), "GENEPIO": ("genepio", "GENEPIO"), "GeoSPARQL": ("geo", "GEOSPARQL"),
    "GO": ("go", "GO"), "HHEAR": (None, "HHEAR"), "HPO": ("hp", "HP"), "IAO": ("iao", "IAO"),
    "JERM": (None, "JERM"), "MeSH": ("mesh", "MESH"), "MICRONT": (None, "MICRONT"), "MIxS": ("gscmixs", "MIXS"),
    "MONDO": ("mondo", "MONDO"), "NCBITAXON": ("ncbitaxon", "NCBITAXON"), "NCIT": ("ncit", "NCIT"),
    "OBI": ("obi", "OBI"), "OBOE": (None, "OBOE"), "OHMI": ("ohmi", "OHMI"), "OIO": ("oio", None),
    "OpenBiodiv-O": (None, None), "OMO": ("omo", "OMO"), "OWL": ("owl", None), "PATO": ("pato", "PATO"),
    "PCO": ("pco", "PCO"), "PO": ("po", "PO"), "PROV": ("prov", "PROVO"), "QUDT": (None, "QUDT"),
    "RDFS": ("rdfs", "RDFS"), "RDF-DataCube": (None, None), "RO": ("ro", "OBOREL"),
    "SCHEMAORG_HTTP": ("schemaorg_http", "SCHEMA"), "SFWO": (None, None), "SIO": ("sio", "SIO"),
    "SKOS": ("skos", None), "SNOMED-CT": ("snomed", "SNOMEDCT"), "SO": ("so", "SO"), "SOSA": (None, None),
    "SWEET": (None, "SWEET"), "TYPON": (None, "TYPON"), "UBERON": ("uberon", "UBERON"), "VARIO": ("vario", "VARIO"),
    "BioLink": ("biolink", "BIOLINK"), "OMP": ("omp", "OMP"), "GloSiS": (None, None), "OWL-Time": (None, "TIME"),
    "KEGG": (None, None), "WHOW": (None, None), "PTO": ("to", "PTO"), "ECOCORE": ("ecocore", "ECOCORE"),
    "AGRO": ("agro", "AGRO"), "PECO": ("peco", "PECO"), "DOID": ("doid", "DOID"), "EXO": ("exo", "EXO"),
    "NBO": ("nbo", "NBO"), "ECO": ("eco", "ECO"), "CL": ("cl", "CL"),
}

NOT_IN = "not in {}"


def get_json(url: str, headers: dict[str, str] | None = None, timeout: int = 60):
    req = urllib.request.Request(url, headers={"Accept": "application/json", **(headers or {})})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        return {"_http": e.code}
    except Exception as e:  # network, timeout, bad JSON
        return {"_error": type(e).__name__}


def ols_counts(ontology_id: str) -> dict:
    d = get_json(OLS + ontology_id)
    if "_http" in d or "_error" in d:
        return {"classes": None, "properties": None, "version": None, "note": d.get("_http") or d.get("_error")}
    return {
        "classes": d.get("numberOfTerms"),
        "properties": d.get("numberOfProperties"),
        "version": (d.get("config") or {}).get("version"),
        "note": "",
    }


def bioportal_counts(acronym: str, key: str) -> dict:
    headers = {"Authorization": f"apikey token={key}"}
    metrics = get_json(f"{BIOPORTAL}{acronym}/metrics", headers)
    sub = get_json(f"{BIOPORTAL}{acronym}/latest_submission?include=released,version", headers)
    if "_http" in metrics or "_error" in metrics:
        return {"classes": None, "properties": None, "released": None, "version": None,
                "note": metrics.get("_http") or metrics.get("_error")}
    return {
        "classes": metrics.get("classes"),
        "properties": metrics.get("properties"),
        "released": (sub.get("released") or "")[:10] if isinstance(sub, dict) else None,
        "version": sub.get("version") if isinstance(sub, dict) else None,
        "note": "",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--only", nargs="*", metavar="SHORT_NAME", help="sheet short names to fetch (default: all)")
    ap.add_argument("--no-ols", action="store_true", help="skip OLS")
    ap.add_argument("--no-bioportal", action="store_true", help="skip BioPortal (also skipped when no key is set)")
    ap.add_argument("--csv", metavar="FILE", help="also write the table to this CSV file")
    ap.add_argument("--pause", type=float, default=0.25, help="seconds between BioPortal calls (be polite)")
    args = ap.parse_args()

    key = os.environ.get("BIOPORTAL_API_KEY", "").strip()
    use_bp = not args.no_bioportal and bool(key)
    if not args.no_bioportal and not key:
        print("BIOPORTAL_API_KEY is not set; BioPortal columns will be empty.", file=sys.stderr)

    names = args.only or list(SHEET_TO_PORTALS)
    unknown = [n for n in names if n not in SHEET_TO_PORTALS]
    if unknown:
        print(f"not in the table: {', '.join(unknown)}", file=sys.stderr)
        return 2

    rows = []
    for name in names:
        ols_id, bp_acr = SHEET_TO_PORTALS[name]
        row = {"short_name": name, "ols_id": ols_id or "", "bioportal_acronym": bp_acr or ""}
        if not args.no_ols:
            if ols_id:
                o = ols_counts(ols_id)
                row.update(ols_classes=o["classes"], ols_properties=o["properties"], ols_version=o["version"], ols_note=o["note"])
            else:
                row.update(ols_classes=NOT_IN.format("OLS"), ols_properties=NOT_IN.format("OLS"), ols_version="", ols_note="")
        if use_bp:
            if bp_acr:
                b = bioportal_counts(bp_acr, key)
                row.update(bp_classes=b["classes"], bp_properties=b["properties"], bp_released=b["released"],
                           bp_version=b["version"], bp_note=b["note"])
                time.sleep(args.pause)
            else:
                row.update(bp_classes=NOT_IN.format("BioPortal"), bp_properties=NOT_IN.format("BioPortal"),
                           bp_released="", bp_version="", bp_note="")
        rows.append(row)
        print(f"{name:15} OLS {row.get('ols_classes', '-')!s:>9} / {row.get('ols_properties', '-')!s:>5}"
              f"   BioPortal {row.get('bp_classes', '-')!s:>9} / {row.get('bp_properties', '-')!s:>5}"
              f"   {row.get('bp_released', '') or ''}")

    if args.csv:
        fields = sorted({k for r in rows for k in r}, key=lambda k: (k != "short_name", k))
        with open(args.csv, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=fields)
            w.writeheader()
            w.writerows(rows)
        print(f"wrote {args.csv}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
