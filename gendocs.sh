#!/bin/sh

# output dir
out=$1 
parent="Knowledge Graph"

# create individual docs
python $SHACL2MD_HOME/shacl2md.py organizations/organizations.rdfs.ttl organizations/organizations.shacl.ttl general/skos.rdfs.ttl  --name organization --out $out --parent "$parent" --nav_order 1 --language nl en --vdir --validate
python $SHACL2MD_HOME/shacl2md.py objects/objects.rdfs.ttl objects/objects.shacl.ttl general/skos.rdfs.ttl  --name object --out $out --parent "$parent" --nav_order 2 --language nl en --vdir --validate 
python $SHACL2MD_HOME/shacl2md.py description/description.shacl.ttl  description/description.rdfs.ttl objects/objects.rdfs.ttl organizations/organizations.rdfs.ttl general/skos.rdfs.ttl  --name descriptive --out $out --parent "$parent" --nav_order 3 --language nl en --vdir --validate
python $SHACL2MD_HOME/shacl2md.py events/events.shacl.ttl  events/events.rdfs.ttl objects/objects.rdfs.ttl organizations/organizations.rdfs.ttl general/skos.rdfs.ttl   --name events --out $out --parent "$parent" --nav_order 4 --language nl en --vdir --validate
python $SHACL2MD_HOME/shacl2md.py general/skos.shacl.ttl  general/skos.rdfs.ttl general/skos-xl.rdfs.ttl  --name thesauri --out $out/0.0.1 --parent "$parent" --nav_order 5 --language nl en --validate

# create diagram of all
python $SHACL2MD_HOME/shacl2md.py events/events.shacl.ttl description/description.shacl.ttl objects/objects.shacl.ttl organizations/organizations.shacl.ttl general/skos.shacl.ttl  events/events.rdfs.ttl objects/objects.rdfs.ttl organizations/organizations.rdfs.ttl description/description.rdfs.ttl general/skos.rdfs.ttl general/skos-xl.rdfs.ttl --name all --out $out --parent "$parent" --nav_order 4 --language nl en --vdir --validate --nodocs