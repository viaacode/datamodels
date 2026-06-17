# Description LinkML conversion

Generate `description.linkml.yml` from the local RDFS and SHACL Turtle files:

```sh
python3 description/rdfs_shacl_to_linkml.py
```

By default, the script reads:

- `description/description.rdfs.ttl`
- `description/description.shacl.ttl`

and writes:

- `description/description.linkml.yml`

You can override the paths:

```sh
python3 description/rdfs_shacl_to_linkml.py \
  --rdfs description/description.rdfs.ttl \
  --shacl description/description.shacl.ttl \
  --output description/description.linkml.yml
```

The converter is dependency-free and tailored to the Turtle style used in these files. It is not a general-purpose RDF or SHACL parser.
