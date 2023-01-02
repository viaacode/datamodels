#!/bin/sh

# output dir
out=$1 
parent="Knowledge Graph"

declare -a models
models[0]='organization=organizations/organizations.shacl.ttl,organizations/organizations.rdfs.ttl'
models[1]='object=objects/objects.shacl.ttl,objects/objects.rdfs.ttl'
models[2]='descriptive=description/description.shacl.ttl,description/description.rdfs.ttl'
models[3]='events=events/events.shacl.ttl,events/events.rdfs.ttl'
models[4]='thesauri=general/skos.shacl.ttl,general/skos.rdfs.ttl,general/skos-xl.rdfs.ttl'

for i in $(seq 0 1 $((${#models[@]}-1)))
do
    IFS='=' read -r -a model <<< "${models[$i]}"
    # select model files
    IFS=',' read -r -a model_files <<< "${model[@]:1}"
    # IFS=',' read -r -a model <<< "${models[$i]}"
    # select all models in models array except the 'i-th' one'
    crosslinks=$(IFS=' '; echo "${models[@]:0:${i}}" "${models[@]:$(($i+1))}")
    # echo $crosslinks
    python $SHACL2MD_HOME/shacl2md.py ${model_files[@]} --name ${model[0]} --out $out --parent "$parent" --nav_order $i --language nl en --crosslinks $crosslinks  --vdir --validate 
done

# Temp. workaround for missing version
mv $out/None/thesauri $out/0.0.1
rm -rf $out/None

# create diagram of all
python $SHACL2MD_HOME/shacl2md.py events/events.shacl.ttl description/description.shacl.ttl objects/objects.shacl.ttl organizations/organizations.shacl.ttl general/skos.shacl.ttl  events/events.rdfs.ttl objects/objects.rdfs.ttl organizations/organizations.rdfs.ttl description/description.rdfs.ttl general/skos.rdfs.ttl general/skos-xl.rdfs.ttl --name all --out $out --parent "$parent" --language nl en --vdir --validate --nodocs