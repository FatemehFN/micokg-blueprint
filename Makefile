# MiCoKnowGraph build. Run inside the micokg environment, or pass a runner:
#   make all
#   make all RUN="mamba run -n micokg"
RUN ?=
SCHEMA := schema/micokg.yaml
VALID := $(wildcard examples/valid/*.yaml)
INVALID := $(wildcard examples/invalid/*.yaml)
CURATED := $(wildcard mappings/curated/*.sssom.tsv)

.PHONY: all lint validate gen rdf shacl mappings slims spex test terms docs-serve clean

all: lint gen rdf mappings spex test

lint:
	$(RUN) linkml-lint --config .linkmllint.yaml $(SCHEMA)

validate:
	@for f in $(VALID); do \
	  echo "validate $$f"; \
	  $(RUN) linkml-validate -s $(SCHEMA) -C Container $$f || exit 1; \
	done
	@for f in $(INVALID); do \
	  if $(RUN) linkml-validate -s $(SCHEMA) -C Container $$f >/dev/null 2>&1; then \
	    echo "ERROR: $$f should be invalid but passed"; exit 1; \
	  else echo "rejected (as expected) $$f"; fi; \
	done

gen:
	mkdir -p build/owl build/shacl build/jsonld docs/schema
	$(RUN) gen-owl $(SCHEMA) > build/owl/micokg.owl.ttl
	$(RUN) gen-shacl --non-closed $(SCHEMA) > build/shacl/micokg.shacl.ttl
	$(RUN) gen-jsonld-context $(SCHEMA) > build/jsonld/micokg.context.jsonld
	$(RUN) gen-doc -d docs/schema $(SCHEMA)

rdf:
	$(RUN) python scripts/yaml_to_rdf.py $(VALID) -o build/rdf

# SHACL shapes are generated from the schema inside the test (see test docstring).
shacl:
	$(RUN) pytest -q tests/test_rdf_shacl.py

mappings:
	mkdir -p build/mappings
	@for f in $(CURATED); do \
	  echo "sssom $$f"; \
	  $(RUN) sssom validate $$f || exit 1; \
	  $(RUN) sssom convert $$f -O ttl -o build/mappings/$$(basename $$f .sssom.tsv).sssom.ttl || exit 1; \
	done
	$(RUN) python scripts/sssom_to_rdf.py $(CURATED) -o build/mappings/curated-direct.ttl

slims:
	$(RUN) python scripts/build_slims.py

spex:
	$(RUN) python scripts/rq_to_spex.py

test:
	$(RUN) pytest -q

# Needs `pip install -e .[terms]` and downloads whole ontologies (NCBITaxon is several GB).
terms:
	@for f in $(VALID); do $(RUN) linkml-term-validator validate-data $$f -s $(SCHEMA) -t Container || exit 1; done

docs-serve: gen
	$(RUN) mkdocs serve

clean:
	rm -rf build docs/schema .pytest_cache
