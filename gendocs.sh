#!/bin/sh

# output dir
out=$1 
parent="Knowledge Graph"

declare -a models
models[0]='organization=organizations/organizations.ttl,ontologies/dct.rdfs.ttl,ontologies/ebucore.rdfs.ttl,ontologies/edm.rdfs.ttl,ontologies/foaf.rdfs.ttl,ontologies/org.rdfs.ttl,ontologies/premis.rdfs.ttl,ontologies/prov.rdfs.ttl,ontologies/rdf.rdfs.ttl,ontologies/schema.rdfs.ttl,ontologies/seq.rdfs.ttl,ontologies/skos-xl.rdfs.ttl,ontologies/skos.rdfs.ttl'
models[1]='object=objects/objects.ttl,ontologies/dct.rdfs.ttl,ontologies/ebucore.rdfs.ttl,ontologies/edm.rdfs.ttl,ontologies/foaf.rdfs.ttl,ontologies/org.rdfs.ttl,ontologies/premis.rdfs.ttl,ontologies/prov.rdfs.ttl,ontologies/rdf.rdfs.ttl,ontologies/schema.rdfs.ttl,ontologies/seq.rdfs.ttl,ontologies/skos-xl.rdfs.ttl,ontologies/skos.rdfs.ttl'
models[2]='descriptive=description/description.ttl,ontologies/dct.rdfs.ttl,ontologies/ebucore.rdfs.ttl,ontologies/edm.rdfs.ttl,ontologies/foaf.rdfs.ttl,ontologies/org.rdfs.ttl,ontologies/premis.rdfs.ttl,ontologies/prov.rdfs.ttl,ontologies/rdf.rdfs.ttl,ontologies/schema.rdfs.ttl,ontologies/seq.rdfs.ttl,ontologies/skos-xl.rdfs.ttl,ontologies/skos.rdfs.ttl'
models[3]='events=events/events.ttl,ontologies/dct.rdfs.ttl,ontologies/ebucore.rdfs.ttl,ontologies/edm.rdfs.ttl,ontologies/foaf.rdfs.ttl,ontologies/org.rdfs.ttl,ontologies/premis.rdfs.ttl,ontologies/prov.rdfs.ttl,ontologies/rdf.rdfs.ttl,ontologies/schema.rdfs.ttl,ontologies/seq.rdfs.ttl,ontologies/skos-xl.rdfs.ttl,ontologies/skos.rdfs.ttl'
models[4]='terms=terms/terms.ttl,ontologies/dct.rdfs.ttl,ontologies/ebucore.rdfs.ttl,ontologies/edm.rdfs.ttl,ontologies/foaf.rdfs.ttl,ontologies/org.rdfs.ttl,ontologies/premis.rdfs.ttl,ontologies/prov.rdfs.ttl,ontologies/rdf.rdfs.ttl,ontologies/schema.rdfs.ttl,ontologies/seq.rdfs.ttl,ontologies/skos-xl.rdfs.ttl,ontologies/skos.rdfs.ttl'

for i in $(seq 0 1 $((${#models[@]}-1)))
do
    IFS='=' read -r -a model <<< "${models[$i]}"
    # select model files
    IFS=',' read -r -a model_files <<< "${model[@]:1}"
    # IFS=',' read -r -a model <<< "${models[$i]}"
    # select all models in models array except the 'i-th' one'
    crosslinks=$(IFS=' '; echo "${models[@]:0:${i}}" "${models[@]:$(($i+1))}")
    # echo $crosslinks
    python $SHACL2MD_HOME/shacl2md.py ${model_files[0]} --ontology ${model_files[@]:1} --name ${model[0]} --out $out --parent "$parent" --nav_order $i --language nl en --crosslinks $crosslinks  --vdir --validate 
done

# create diagram of all
python $SHACL2MD_HOME/shacl2md.py events/events.ttl description/description.ttl objects/objects.ttl organizations/organizations.ttl terms/terms.ttl --ontology  ontologies/dct.rdfs.ttl ontologies/ebucore.rdfs.ttl ontologies/edm.rdfs.ttl ontologies/foaf.rdfs.ttl ontologies/org.rdfs.ttl ontologies/premis.rdfs.ttl ontologies/prov.rdfs.ttl ontologies/rdf.rdfs.ttl ontologies/schema.rdfs.ttl ontologies/seq.rdfs.ttl ontologies/skos-xl.rdfs.ttl ontologies/skos.rdfs.ttl --name all --out $out --parent "$parent" --language nl en --vdir --validate --nodocs