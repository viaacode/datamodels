#!/bin/sh

# output dir
out=$1 
parent="Knowledge Graph"

declare -a models
models[0]='organization=organizations/organizations.shacl.ttl,objects/objects.rdfs.ttl,organizations/organizations.rdfs.ttl,ontologies/dct.rdfs.ttl,ontologies/ebucore.rdfs.ttl,ontologies/edm.rdfs.ttl,ontologies/foaf.rdfs.ttl,ontologies/org.rdfs.ttl,ontologies/premis.rdfs.ttl,ontologies/prov.rdfs.ttl,ontologies/rdf.rdfs.ttl,ontologies/schema.rdfs.ttl,ontologies/seq.rdfs.ttl,ontologies/skos-xl.rdfs.ttl,ontologies/skos.rdfs.ttl'
models[1]='object=objects/objects.shacl.ttl,objects/objects.rdfs.ttl,organizations/organizations.rdfs.ttl,ontologies/dct.rdfs.ttl,ontologies/ebucore.rdfs.ttl,ontologies/edm.rdfs.ttl,ontologies/foaf.rdfs.ttl,ontologies/org.rdfs.ttl,ontologies/premis.rdfs.ttl,ontologies/prov.rdfs.ttl,ontologies/rdf.rdfs.ttl,ontologies/schema.rdfs.ttl,ontologies/seq.rdfs.ttl,ontologies/skos-xl.rdfs.ttl,ontologies/skos.rdfs.ttl'
models[2]='descriptive=description/description.shacl.ttl,objects/objects.rdfs.ttl,organizations/organizations.rdfs.ttl,ontologies/dct.rdfs.ttl,ontologies/ebucore.rdfs.ttl,ontologies/edm.rdfs.ttl,ontologies/foaf.rdfs.ttl,ontologies/org.rdfs.ttl,ontologies/premis.rdfs.ttl,ontologies/prov.rdfs.ttl,ontologies/rdf.rdfs.ttl,ontologies/schema.rdfs.ttl,ontologies/seq.rdfs.ttl,ontologies/skos-xl.rdfs.ttl,ontologies/skos.rdfs.ttl'
models[3]='events=events/events.shacl.ttl,objects/objects.rdfs.ttl,organizations/organizations.rdfs.ttl,ontologies/dct.rdfs.ttl,ontologies/ebucore.rdfs.ttl,ontologies/edm.rdfs.ttl,ontologies/foaf.rdfs.ttl,ontologies/org.rdfs.ttl,ontologies/premis.rdfs.ttl,ontologies/prov.rdfs.ttl,ontologies/rdf.rdfs.ttl,ontologies/schema.rdfs.ttl,ontologies/seq.rdfs.ttl,ontologies/skos-xl.rdfs.ttl,ontologies/skos.rdfs.ttl'
models[4]='terms=terms/terms.shacl.ttl,objects/objects.rdfs.ttl,organizations/organizations.rdfs.ttl,ontologies/dct.rdfs.ttl,ontologies/ebucore.rdfs.ttl,ontologies/edm.rdfs.ttl,ontologies/foaf.rdfs.ttl,ontologies/org.rdfs.ttl,ontologies/premis.rdfs.ttl,ontologies/prov.rdfs.ttl,ontologies/rdf.rdfs.ttl,ontologies/schema.rdfs.ttl,ontologies/seq.rdfs.ttl,ontologies/skos-xl.rdfs.ttl,ontologies/skos.rdfs.ttl'

for i in $(seq 0 1 $((${#models[@]}-1)))
do
    IFS='=' read -r -a model <<< "${models[$i]}"
    # select model files
    IFS=',' read -r -a model_files <<< "${model[@]:1}"
    # IFS=',' read -r -a model <<< "${models[$i]}"
    # select all models in models array except the 'i-th' one'
    crosslinks=$(IFS=' '; echo "${models[@]:0:${i}}" "${models[@]:$(($i+1))}")
    # echo $crosslinks
    python $SHACL2MD_HOME/shacl2md.py ${model_files[0]} --ontology ${model_files[@]:1} --name ${model[0]} --out $out --parent "$parent" --nav_order $i --language nl en fr --crosslinks $crosslinks  --vdir --validate 
done

# create diagram of all
python $SHACL2MD_HOME/shacl2md.py events/events.shacl.ttl description/description.shacl.ttl objects/objects.shacl.ttl organizations/organizations.shacl.ttl terms/terms.shacl.ttl --ontology  objects/objects.rdfs.ttl organizations/organizations.rdfs.ttl ontologies/dct.rdfs.ttl ontologies/ebucore.rdfs.ttl ontologies/edm.rdfs.ttl ontologies/foaf.rdfs.ttl ontologies/org.rdfs.ttl ontologies/premis.rdfs.ttl ontologies/prov.rdfs.ttl ontologies/rdf.rdfs.ttl ontologies/schema.rdfs.ttl ontologies/seq.rdfs.ttl ontologies/skos-xl.rdfs.ttl ontologies/skos.rdfs.ttl --name all --out $out --parent "$parent" --language nl en fr --vdir --validate --nodocs