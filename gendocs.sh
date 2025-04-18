#!/bin/sh

# output dir
out=${1:-./output}
parent="Knowledge Graph"
#pip install shacl2md --extra-index-url http://do-prd-mvn-01.do.viaa.be:8081/repository/pypi-all/simple --trusted-host do-prd-mvn-01.do.viaa.be
shacl2md generate \
    all:organizations/organizations.shacl.ttl,objects/objects.shacl.ttl,description/description.shacl.ttl,description/film.shacl.ttl,description/audiovisual.shacl.ttl,description/bibliographic.shacl.ttl,events/events.shacl.ttl,terms/terms.shacl.ttl \
    organization:organizations/organizations.shacl.ttl \
    object:objects/objects.shacl.ttl \
    descriptive:description/description.shacl.ttl \
    events:events/events.shacl.ttl \
    terms:terms/terms.shacl.ttl \
    --languages en --languages nl --languages fr \
    --output_dir $out \
    --ontology_file objects/objects.rdfs.ttl --ontology_file organizations/organizations.rdfs.ttl --ontology_file description/description.rdfs.ttl --ontology_file ontologies/dct.rdfs.ttl --ontology_file ontologies/ebucore.rdfs.ttl --ontology_file ontologies/edm.rdfs.ttl --ontology_file ontologies/foaf.rdfs.ttl --ontology_file ontologies/org.rdfs.ttl --ontology_file ontologies/premis.rdfs.ttl --ontology_file ontologies/prov.rdfs.ttl --ontology_file ontologies/rdf.rdfs.ttl --ontology_file ontologies/schema.rdfs.ttl --ontology_file ontologies/seq.rdfs.ttl --ontology_file ontologies/skos-xl.rdfs.ttl --ontology_file ontologies/skos.rdfs.ttl \
    --crosslink --version_directory --shacl_shacl_validation \
    --jekyll_parent_page "$parent" 