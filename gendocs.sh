#!/bin/sh

# output dir
out=$1 
parent="Knowledge Graph"

shacl2md \
    organization:organizations/organizations.shacl.ttl \
    object:objects/objects.shacl.ttl \
    descriptive:description/description.shacl.ttl \
    events:events/events.shacl.ttl \
    terms:terms/terms.shacl.ttl \
    --languages en --languages nl --languages fr \
    --output_dir $out \
    --ontology_file objects/objects.rdfs.ttl --ontology_file organizations/organizations.rdfs.ttl --ontology_file ontologies/dct.rdfs.ttl --ontology_file ontologies/ebucore.rdfs.ttl --ontology_file ontologies/edm.rdfs.ttl --ontology_file ontologies/foaf.rdfs.ttl --ontology_file ontologies/org.rdfs.ttl --ontology_file ontologies/premis.rdfs.ttl --ontology_file ontologies/prov.rdfs.ttl --ontology_file ontologies/rdf.rdfs.ttl --ontology_file ontologies/schema.rdfs.ttl --ontology_file ontologies/seq.rdfs.ttl --ontology_file ontologies/skos-xl.rdfs.ttl --ontology_file ontologies/skos.rdfs.ttl \
    --crosslink --version_directory --shacl_shacl_validation \
    --jekyll_parent_page "$parent" 
