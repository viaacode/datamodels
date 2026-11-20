# Data models for meemoo

This repository contains all SHACL, RDFS and SKOS definitions used in the meemoo Knowledge Graph. 
See generated documentation pages here: https://developer.meemoo.be/docs/metadata/knowledge-graph

## Generate a LinkML schema

```sh
python -m pip install -r scripts/requirements-linkml.txt
python scripts/rdfs_shacl_to_linkml.py hetarchief -o hetarchief/model.linkml.yaml
```

The directory argument defaults to `hetarchief`. It must contain `model.rdfs.ttl`
and `model.shacl.ttl`; all Turtle files under its `external` directory are included.
Omit `-o` to write YAML to stdout. Imports are read from these local files only.

The converter includes RDFS/OWL classes, property hierarchies, domains, ranges,
labels and descriptions, plus class-specific SHACL cardinalities, alternative
ranges and controlled-value enums. It preserves RDF URIs and distinguishes terms
with identical local names. `ha:` terms use unprefixed names (`ha:Agent` becomes
`Agent`); other namespaces keep their prefix (`prov:Agent` becomes `prov_Agent`).
Built-in datatypes use their LinkML names, such as `integer`.
See the [LinkML schema documentation](https://linkml.io/linkml/schemas/).

This is a structural conversion, not an OWL reasoner or a replacement for SHACL
validation. Warnings on stderr identify approximations: complex paths,
`sh:uniqueLang`, `sh:disjoint`, and referenced node shapes retain metadata but
lose their full validation behavior. URI enums preserve their original values
and meanings; additional class/datatype restrictions on enums remain annotations.
Custom datatypes retain their URIs with a string or integer base; language tags
and full datatype lexical rules are not enforced. Unsupported SHACL predicates
also produce warnings.

Run the converter tests with:

```sh
python -m unittest discover -s scripts -p 'test_rdfs_shacl_to_linkml.py'
```

## Generate docs

You can use [shacl2md](https://github.com/viaacode/shacl2md) to generate the datamodel docs. 

```
export SHACL2MD_HOME=../shacl2md; bash gendocs.sh <path to output documentation>
```
