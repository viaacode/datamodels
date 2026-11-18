# Model consolidation execution plan

Produce verified, reproducible model artifacts under `model/runs/` without changing original sources. Use Python 3.10+ and run commands from the repository root.

1. **Configure execution.** Set `root` to `../..` in [model-config.json](model-config.json). Use the current Python environment to run tests, build, verify, and render HTML through direct function calls in [run_model.py](run_model.py). Discover tests in `scripts/consolidate/tests`, save runs under `model/runs/`, and use the commands in [README.md](README.md).

2. **Configure inputs.** Select core RDFS/SHACL files from `description/`, `events/`, `objects/`, `organizations/`, `rights/`, and `terms/`; external definitions from `ontologies/*.ttl`; referenced local SKOS resources; and [supplemental declarations](../../model/supplemental.rdfs.ttl). Require explicit inclusion of non-core sources. Use `external_ontologies_complete/` only through exact `missing_definitions` entries. Stop on unresolved required terms; never download imports or copy unused vocabularies.

3. **Resolve dependencies.** Recursively collect referenced definitions, shapes, blank nodes, ordered lists, inverses, and selected SKOS scheme members. Respect base URIs, per-file blank-node scope, literal forms, annotations, and contextual constraints. Enable `prune_unused_superclasses`: retain named ancestors only when used by shapes, including linked/nested shapes, implicit targets, and executable constraints. Omit domains, equivalences, and disjointness links that reintroduce unused ancestors; record each omitted axiom and its location. Keep direct ranges, anonymous restrictions, and protected language terms.

4. **Map and name terms.** Rewrite domain identifiers and structural/executable references into `ha: <https://data.hetarchief.be/ns/>` using configured English names, acronyms, inverse pairs, and per-URI overrides.

   | Term | Naming rule | Example |
   |---|---|---|
   | Class | Singular PascalCase | `DigitalRepresentation` |
   | Shape | PascalCase | `PersonHasNameShape` |
   | Property | Active/possession lowerCamelCase | `creates`, `hasPart`, `isPartOf` |
   | Concept, scheme, ontology | lowerCamelCase | `contentRange`, `descriptionModel` |

   Align English `rdfs:label` and `sh:name`; preserve French/Dutch text and contextual shape names. Configure irregular verbs and inverses explicitly; never invent inverse properties. Preserve RDF/RDFS/OWL/SHACL/XSD, SKOS/SKOS-XL, VANN, DCAM, vocabulary-status terms, configured Schema.org modeling predicates, and EDTF identifiers. Keep Dublin Core/PAV annotation predicates and ontology-header vocabulary, including nested author/contact metadata; apply configured `header_values`. Annotation uses must not prevent independent mapping of domain uses.

   Retain PREMIS, ODRL, and PROV through `retain_namespaces`, including definitions, dependencies, identifiers, labels, namespace headers, and documentary imports. Record identity mappings; apply naming only to remapped terms. Keep language terms excluded from selection/mapping through `preserve_namespaces`.

5. **Consolidate and export.** Enable `consolidate_collisions` to union non-retained classes or predicates sharing configured names and English labels; rewrite all uses. Keep contextual shapes and other resource kinds separate unless explicitly merged. Reject mixed kinds, mismatched labels, self-disjoint classes, and incompatible constraints. Preserve selected axioms except recorded omissions; deduplicate triples and structurally equivalent anonymous shapes without losing context or list order.

   Add or retain `rdfs:seeAlso` only between URI resources with different nonempty hostnames; preserve qualifying targets verbatim. Omit same-host and non-URI links and record omissions. Record every original-to-target mapping and source, selected triple counts, consolidation/merge groups, policies, annotation/header adjustments, the `source_sha256` hashes, and namespace-to-document paths in the version 3 `model-map.json`.

   Route definitions by their final URI: keep every `ha:` definition in `model.rdfs.ttl` or `model.shacl.ttl`, including terms remapped from external sources. Keep source provenance in the manifest. Group definitions retaining non-`ha:` identifiers by ontology namespace in one `external/<prefix>.rdfs.ttl` file per namespace. Use the configured `prefixes` for filenames; combine selected curated and exact-fallback definitions, preserve their source provenance, reject filename collisions, and omit empty files. ODRL must produce one `external/odrl.rdfs.ttl`, regardless of which source files supply its definitions. Move attached blank nodes, lists, and metadata with their owners; copy shared anonymous structures into each document that needs them. External files may reference `ha:` terms but must never define `ha:` subjects or receive synthetic `ha:` headers. Import external files locally from `model.rdfs.ttl`, retain `owl:imports <model.rdfs.ttl>` in the shapes file, and write local document references relative to each file.

   Export readable, deterministically ordered Turtle with meaningful prefixes, consistent indentation, and separated definitions. Keep single-use anonymous RDFS expressions inline, including typed domain/range classes, restrictions, and lists; label shared or cyclic blank nodes only when identity requires it. Deduplicate within documents and check conflicts across their union.

6. **Verify and publish.** Use [verify_model.py](verify_model.py) to independently reread sources and compare complete mapped structures in each output file up to graph isomorphism. Reject `ha:` definitions in external files. Check ontology grouping, final-namespace ownership, local imports, mappings, retained vocabulary, consolidation groups, required external links, and recorded adjustments/omissions. Reject missing files and misplaced, lost, or unexpected triples, dangling references, unexplained merges, forged omissions, and changed source hashes. Run SHACL meta-validation over all local output graphs without downloading imports. Run regression fixtures covering remapped external classes/shapes, mixed-namespace sources, shared anonymous structures, one file per ontology, combined curated/fallback sources, filename collisions, nested constraints, ordered lists, inverse mappings, executable references, shared blank nodes, namespace retention, hierarchy pruning, and run isolation.

   Validate all serialized Turtle and generate `model-map.html` before publishing a fresh UTC timestamp directory. Reject existing destinations and leave no failed-run artifacts. Save the effective config with absolute repository paths and every output path, all Turtle files, manifest, and report. Keep earlier runs untouched; regenerate them to use the new layout.

7. **Run and review.** Execute the workflow after path alignment:

   ```sh
   python3 scripts/consolidate/run_model.py
   ```

   Pass a saved config as the optional argument to replay a run. Verify using that saved config and matching source versions. Rebuild into a separate directory; require identical recursive file sets, compare every Turtle/HTML file byte for byte, and compare JSON after excluding run-specific output paths. Review the map/report against the previous run. Make semantic or policy adjustments in sources/config, then regenerate.

Accept when source-to-output coverage is 100%, conflicts are zero, SHACL syntax and fixtures pass, changes are reviewed, and repeat builds match. Verification establishes migration fidelity and SHACL syntax; it does not establish full OWL consistency or validate production data.
