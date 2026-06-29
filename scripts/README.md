# Description LinkML conversion

Generate `description.linkml.yml` from the local RDFS and SHACL Turtle files:

```sh
python3 scripts/rdfs_shacl_to_linkml.py
```

By default, the script reads:

- `description/description.rdfs.ttl`
- `description/description.shacl.ttl`

and writes:

- `scripts/description.linkml.yml`

You can override the paths:

```sh
python3 scripts/rdfs_shacl_to_linkml.py \
  --rdfs description/description.rdfs.ttl \
  --shacl description/description.shacl.ttl \
  --output scripts/description.linkml.yml
```

Multiple RDFS or SHACL files can be supplied. They are concatenated in the order given:

```sh
python3 scripts/rdfs_shacl_to_linkml.py \
  --rdfs description/description.rdfs.ttl rights/rights.rdfs.ttl \
  --shacl description/description.shacl.ttl rights/rights.shacl.ttl
```

The converter is dependency-free and tailored to the Turtle style used in these files. It is not a general-purpose RDF or SHACL parser.
