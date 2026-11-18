# Consolidated model

Each new build saves its artifacts in `model/runs/<UTC timestamp>/`.
`model.rdfs.ttl` contains the consolidated `ha:` vocabulary, including terms
remapped from external sources, local SKOS resources and supplemental declarations.
Definitions retaining external identifiers are grouped by ontology namespace in
`external/<prefix>.rdfs.ttl`, combining selected definitions from all source files. `model.rdfs.ttl` imports those files
locally. `model.shacl.ttl` contains the consolidated shapes and their metadata,
and uses `owl:imports <model.rdfs.ttl>` to link to the local vocabulary. Neither command
changes the original model files, downloads imports, or migrates instance data.

RDFS anonymous expressions stay inline with their owning properties, including
typed class expressions under `rdfs:domain` and `rdfs:range`, nested restrictions,
and lists. Mapping rewrites their named IRIs while retaining the nested blank
nodes. Shared or cyclic blank nodes keep labels when needed to preserve identity.

## Run the complete workflow

With Python 3.10+ installed, install dependencies into your chosen environment,
then run from the repository root:

```sh
python3 -m pip install -r scripts/consolidate/requirements.txt
python3 scripts/consolidate/run_model.py
```

The [script](run_model.py) uses the current interpreter to run the test suite,
build the model and HTML report, and verify the saved run through direct Python
calls. It then builds again from the saved configuration
and checks reproducibility: recursive file sets must match, every Turtle/HTML file
must match byte for byte, and JSON must match after excluding output paths. Any failure stops the script with a nonzero exit.

Both runs are retained under `model/runs/`: `<UTC timestamp>/` and
`<UTC timestamp>-repeat/`. The script prints the report path when finished.
Edit source definitions or `scripts/consolidate/model-config.json` before rerunning, then
review the report for the intended changes. No plan document is needed.

To use another configuration, including a saved run:

```sh
python3 scripts/consolidate/run_model.py model/runs/<run>/model-config.json
```

The script works from any directory; relative config paths use the calling
directory. Activate your chosen Python environment before running it.
PREMIS/ODRL/PROV namespace retention is enabled in the default config and applies
automatically to both builds.

## Build or verify a single run

After setup, use the merger directly to skip the repeated build:

```sh
python3 scripts/consolidate/merge_model.py --config scripts/consolidate/model-config.json
```

It prints the run path; use that path to verify it:

```sh
run_dir="model/runs/<run>"
python3 scripts/consolidate/verify_model.py --config "$run_dir/model-config.json"
```

Use `--run-dir` on the merger to choose an explicit path. Existing directories
are rejected.
Each run contains an effective `model-config.json`, both core Turtle files,
the selected external ontology files, `model-map.json`, and `model-map.html`:

```text
model/runs/<run>/
  model-config.json
  model.rdfs.ttl
  model.shacl.ttl
  model-map.json
  model-map.html
  external/
    odrl.rdfs.ttl
    premis.rdfs.ttl
    prov.rdfs.ttl
```

Only selected definitions are exported. Placement follows the final namespace:
all `ha:` definitions belong in the main vocabulary or shapes file, regardless of
their original source. For example, `ha:Organization` belongs in `model.rdfs.ttl`
even when its definition originated in Schema.org. Retained PREMIS, ODRL and PROV
definitions are grouped into one file per namespace. For example, selected ODRL
terms from `ontologies/odrl.rdfs.ttl` and `external_ontologies_complete/odrl.ttl`
are combined in `external/odrl.rdfs.ttl`. A mixed source can contribute to multiple
ontology files. Output names use the namespace's configured nonempty `prefixes`
entry; missing prefixes and filename collisions stop the build. Empty external
files are omitted.
External files may reference `ha:` terms but never define `ha:` subjects or receive
synthetic `ha:` ontology headers.

Attached blank nodes, ordered lists and metadata move with their owning definitions;
shared anonymous structures are copied into each ontology file that needs them.
Separate source-file blank-node scopes remain distinct when their definitions
are combined. Document references are relative to each Turtle file; rewritten
`rdfs:isDefinedBy` links identify the owning document. The version 3 manifest's
`external_documents` maps ontology namespace URIs to output document names.
Original source files and hashes remain recorded independently of output grouping.
`outputs` in both the manifest and saved config lists every Turtle file.
Regenerate older runs with the current configuration to use this layout.

Validation and report generation finish
before publication; failed runs leave no artifacts. Earlier runs and top-level
outputs are unchanged.

Verify a run using its saved configuration. Pass that configuration to the
merger to rebuild into a fresh run. Relative input paths resolve against `root`;
run snapshots save the absolute repository root and absolute output paths.
Selected source hashes in `source_sha256` detect input changes during later
verification. Replaying an older run requires the corresponding source versions.

## HTML map explorer

New runs include the standalone report automatically. To regenerate it:

```sh
python3 scripts/consolidate/visualize_model_map.py "$run_dir/model-map.json"
```

Open the run's `model-map.html` in a browser. The report includes summary charts,
source contributions, a searchable URI mapping table with kind/source filters,
and the source change log, including superclass omissions. It works offline without a web server.
The map contains migration metadata rather than class/property relationships.

Pass a run's manifest explicitly. To use another output path:

```sh
python3 scripts/consolidate/visualize_model_map.py path/to/model-map.json -o /tmp/model-map.html
python3 -m unittest discover -s scripts/consolidate/tests -p 'test_visualize_model_map.py' -v
```

## Inputs and dependencies

`core` lists the twelve top-level RDFS and SHACL inputs in description, events,
objects, organizations, rights and terms. Drafts are excluded unless listed in
`drafts`. Files in `scripts/` and `external_ontologies_complete/` are excluded
from the normal definition pool. Local SKOS files supply referenced concepts
and schemes; a selected local scheme also brings its members.

The exporter follows references recursively through predicates, classes,
ranges, inverse axioms, shapes, blank nodes and ordered lists.

The default `prune_unused_superclasses: true` policy omits named superclass
links unless the superclass is used by the shapes. Nested constraints, linked
shapes, implicit class targets, and executable constraint references count as
uses. Domains, equivalences, and disjointness axioms to unused ancestor classes
are also omitted to avoid reimporting them. Direct range dependencies still
bring their class definitions: `ha:MediaResource` is sufficient without its
unused `EbuCoreAsset` ancestry. Anonymous restrictions and protected language
identifiers remain intact. This policy also limits retained vocabulary
hierarchies without renaming retained identifiers. Every omitted source triple
is recorded in the manifest with its location and reason. Set the option to
`false` to restore recursive hierarchy expansion. Undefined unused superclass
references do not need fallback definitions.

Documentary
references such as imports, vocabulary version links and SKOS
mapping links retain their URLs without fetching those documents. Qualifying
external `rdfs:seeAlso` targets retain their URLs; same-host and non-URI links
are omitted and recorded. When a
referenced URI also has an included definition, its identifier is rewritten,
except for annotation vocabulary and qualifying `rdfs:seeAlso` targets.
`documentary_namespaces` also preserves documentation URLs such as Schema.org
collaborator pages. Missing definitions may use only the exact URI/file pairs in
`missing_definitions`; adding a file there does not include its unused terms.
Unknown references stop the build and identify their source file and subject.

`@base` is honored. Files without a base use a stable
`https://data.hetarchief.be/source/<repository-path>` base. Blank nodes are scoped
per source file. Literal lexical forms, list order, Dutch and French text,
contextual constraints and existing inverse axioms are preserved.

`supplemental.rdfs.ttl` contains
explicit minimal declarations authorized for otherwise undefined source terms.
These assert a term's kind and English label, without guessing a domain, range,
equivalence or inverse. Source spelling variants and typos remain distinct.
The map identifies every selected term originating in this file. Extend these
declarations when authoritative definitions become available. RDFLib may print
warnings about two whitespace-padded date-time literals in the original ODRL
fallback file; those unused literals are not exported.

## Naming and identity

The proposed namespace is configurable through `namespace`. Update the `ha`
prefix and namespace header values with it. Ontology-description vocabulary
remains unchanged: RDF, RDFS, OWL, SHACL, XSD, SKOS/SKOS-XL, VANN, DCAM, and
vocabulary-status namespaces are protected through `preserve_namespaces`.
For example, definitions use `skos:definition`, not `ha:hasSkosDefinition`.
Configured Schema.org modeling predicates and three EDTF datatypes are also
protected through `preserve_uris`.

`annotation_namespaces` preserves Dublin Core and PAV predicates when used to
annotate source definitions. Ontology-header predicates and connected anonymous
author/contact metadata retain their vocabulary too: `dct:title`,
`dct:creator`, `schema:name`, `schema:email`, and `pav:version` stay unchanged.
Configured namespace-header values still change to the consolidated namespace.
These annotation uses do not import their domain-property definitions. A term
used separately in a shape path can still map to `ha:` as a domain property;
the manifest records contextual vocabulary-preservation changes when needed.

`retain_namespaces` keeps selected terms in their original namespace. The
default config enables PREMIS, ODRL, and PROV:

```json
{
  "retain_namespaces": [
    "http://www.loc.gov/premis/rdf/v3/",
    "http://www.w3.org/ns/odrl/2/",
    "http://www.w3.org/ns/prov#"
  ]
}
```

Remove an entry to consolidate that namespace into `ha:`; use `[]` to disable
retention entirely. Configurations without this setting retain the previous
behavior. Retention takes priority over naming overrides for those terms.

Retained terms still bring their definitions and dependencies into the outputs.
Their URIs remain unchanged in triples, datatypes, and executable references;
the map records identity mappings with provenance. Source labels, names,
namespace header values, and documentary import links are retained; imports
are never fetched. The map's display label uses an original English label/name or
the URI's local name when none exists; no label is added to the graph.
Other domain dependencies still map to `ha:`.

This differs from `preserve_namespaces`, which excludes language terms from
dependency selection and mapping. Turtle output uses `premis:` and `odrl:`
prefixes configured in `prefixes`.

`naming` configures case rules (`PascalCase` or `lowerCamelCase`), acronyms,
explicit property names, preferred English labels in per-URI `overrides`, and
inverse pairs with both names specified. Classes use singular PascalCase;
shapes also use PascalCase (`PersonShape`). All other remapped terms start with
lowercase: properties, concepts, schemes, and ontology resources (`descriptionModel`)
use lowerCamelCase.
Retained and protected identifiers stay unchanged. Properties use active
third-person names or possession expressions. Irregular
verbs and inverse names are configured explicitly. No inverse properties are
created. Named shapes receive English labels; existing contextual English names
on anonymous shapes remain intact.

For example, an override can rename a term and its English label:

```json
{
  "https://schema.org/Person": {
    "name": "Person",
    "label": "person"
  }
}
```

The default `consolidate_collisions: true` policy unions classes with the same
configured target name into one `ha:` class, and does the same for predicates.
EBUCore, FOAF, and Dublin Core `Agent` become `ha:Agent`; their selected definitions
and annotations are combined, and all structural and executable references use
the consolidated term. New collisions join automatically. The config removes
class/property overrides that previously added vocabulary names to avoid collisions.
Retained namespaces are excluded: PREMIS and PROV `Agent` stay at their original URIs.

Remapped terms receive `rdfs:seeAlso` links to original URIs only when their
hostnames differ. Existing references follow the same rule, and qualifying
targets stay unchanged even if that term is also consolidated. Same-host
links are omitted even if scheme, port, path, or fragment differs. Non-URI
references are also omitted, along with anonymous details attached only through
those removed links; shared anonymous content remains. All omitted source
triples are recorded. Local migrations within `data.hetarchief.be` remain in
the map without `rdfs:seeAlso` links. Retained terms receive no generated self-links.

Per-URI overrides can still assign distinct names when terms must stay separate.
Shapes and other resource kinds remain distinct on collision. With the policy
disabled or absent, collisions also remain errors unless explicitly approved.
To authorize a merge outside the automatic policy, give the terms the same name
and English label and add an entry to `merges`, such as
`{"uris": ["https://example.org/one", "https://example.org/two"], "reason": "Reviewed identity"}`.
Mixed kinds, differing configured labels, self-disjoint classes, and conflicting
shape constraints stop the build. Equivalent
anonymous shapes are deduplicated structurally, including their complete nested
constraints. Distinct contextual shapes and named shapes remain separate.

## Verification

`model-map.json` records each original URI, target URI, kind, English label and
source files, the selected triple counts, automatic `consolidations`, explicit
merges, annotation/header changes, superclass and reference omissions, the consolidation,
superclass and retention policies, generated document headers, and selected
source hashes. It is a migration manifest, not a replacement for the original sources.

The verifier imports no merger logic. It independently computes the source
closure, checks the map against the configuration, applies only documented
annotation/header adjustments, configured superclass omissions, and non-external
reference omissions, and compares
each named definition and its full blank-node structure up to RDF graph
isomorphism. It checks lists and paths,
rejects missing triples, unexpected triples, mappings, dangling domain
references and unexplained merges. It checks the recorded consolidation groups
and requires every external original-URI link. Non-external `rdfs:seeAlso` links,
altered metadata vocabulary, and missing or forged omission records fail
verification. The verifier checks definitions in their owning files, rejects
`ha:` definitions in external files, misplaced triples and missing local imports, and runs pySHACL's SHACL
meta-validation over the union of all output graphs. It reads the files listed
in the saved config directly and does not download imports.
Shared anonymous shapes are compared by structure, so deduplication does not
hide a removed nested constraint. The builder verifies the serialized Turtle
before replacing any artifact.

The small fixture suite proves that deleting a constraint, changing list order,
swapping inverse mappings, colliding URIs, forging a change record or omitting a
mapping fails. It also checks dependency selection, separate blank-node scopes,
literal preservation, executable SPARQL URI rewriting, contextual constraints,
anonymous-shape deduplication and deterministic repeated builds.

Verification proves migration fidelity and SHACL syntax. It does not assert full
OWL consistency or correct pre-existing modeling choices, and does not validate
production instance data. To check reproducibility, build twice into separate
runs. Compare recursive file sets and every Turtle/HTML file byte for byte; compare
the manifests and saved configs after excluding run-specific output paths. Regenerate older runs to
apply the new consolidation and required original-URI links.
