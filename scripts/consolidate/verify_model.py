#!/usr/bin/env python3
"""Independently reread sources and audit the URI map and exported RDF structures."""

import argparse
from collections import defaultdict
from hashlib import sha256
import json
from pathlib import Path
import sys

from rdflib import BNode, Graph, Literal, OWL, RDF, RDFS, URIRef
from rdflib.compare import graph_diff, isomorphic, to_isomorphic

from model_common import (
    EXECUTABLE,
    ModelError,
    SH,
    SKOS,
    annotation_predicate,
    consolidates,
    definition_partition,
    document_uri,
    executable_namespaces,
    executable_tokens,
    external_documents,
    external_reference,
    hierarchy_exclusions,
    kind,
    load_outputs,
    load_sources,
    naming,
    ontology_metadata,
    output_paths,
    protected,
    read_config,
    reference_exclusions,
    rewrite_executable,
    retained,
    source_label,
    syntax_check,
    term_data,
    term_from,
    union,
)


def independent_selection(config, sources, core, normal, excluded=()):
    """Fixed point over source triples, independent of the exporter's work queue."""
    selected = {f: set(g) if f in core else set() for f, g in sources.items()}
    metadata = {f: ontology_metadata(g, config) for f, g in sources.items()}
    while True:
        required = defaultdict(set)
        missing = set()
        for filename, triples in selected.items():
            for s, p, o in triples:
                if (filename, (s, p, o)) in excluded:
                    continue
                annotation = s in metadata[filename] or annotation_predicate(p, config)
                refs = [] if annotation else [p]
                if isinstance(o, BNode) or (
                    not annotation
                    and str(p) not in config["documentary_predicates"]
                    and not (
                        isinstance(o, URIRef)
                        and any(
                            str(o).startswith(ns)
                            for ns in config.get("documentary_namespaces", [])
                        )
                    )
                ):
                    refs.append(o)
                if not annotation and isinstance(o, Literal) and o.datatype:
                    refs.append(o.datatype)
                if not annotation and p in EXECUTABLE and isinstance(o, Literal):
                    refs.extend(
                        uri
                        for _, _, uri in executable_tokens(
                            str(o), executable_namespaces(sources[filename])
                        )
                    )
                for ref in refs:
                    if isinstance(ref, BNode):
                        required[filename].add(ref)
                    elif isinstance(ref, URIRef) and not protected(ref, config):
                        matches = [
                            f
                            for f in normal
                            if any(sources[f].triples((ref, None, None)))
                        ]
                        if not matches:
                            matches = [
                                f
                                for f in config.get("missing_definitions", {}).get(
                                    str(ref), []
                                )
                                if any(sources[f].triples((ref, None, None)))
                            ]
                        if not matches:
                            missing.add(f"{ref} at {filename}: {s} / {p}")
                        for match in matches:
                            required[match].add(ref)
        changed = False
        for filename, subjects in required.items():
            graph = sources[filename]
            for subject in list(subjects):
                if (
                    filename in normal
                    and filename not in core
                    and filename.endswith(".skos.ttl")
                ):
                    for relation in (SKOS.inScheme, SKOS.topConceptOf):
                        subjects.update(graph.subjects(relation, subject))
            for subject in subjects:
                triples = set(graph.triples((subject, None, None)))
                if not triples <= selected[filename]:
                    selected[filename].update(triples)
                    changed = True
        if not changed:
            if missing:
                raise ModelError(
                    "Unresolved definitions:\n" + "\n".join(sorted(missing))
                )
            return {f: triples for f, triples in selected.items() if triples}


def audit_map(config, selected, manifest):
    if manifest.get("namespace") != config["namespace"] or manifest.get("version") != 3:
        raise ModelError("Map namespace/version differs from config")
    if manifest.get("merges") != config.get("merges", []):
        raise ModelError("Map merges differ from config")
    if manifest.get("retain_namespaces", []) != config.get("retain_namespaces", []):
        raise ModelError("Map retained namespaces differ from config")
    if manifest.get("consolidate_collisions", False) != config.get(
        "consolidate_collisions", False
    ):
        raise ModelError("Map consolidation policy differs from config")
    if manifest.get("prune_unused_superclasses", False) != config.get(
        "prune_unused_superclasses", False
    ):
        raise ModelError("Map superclass policy differs from config")
    if manifest.get("selected") != {f: len(t) for f, t in selected.items()}:
        raise ModelError(
            "Selected source coverage differs from map; rebuild after source changes"
        )
    graph = Graph()
    locations = defaultdict(set)
    for f, triples in selected.items():
        for triple in triples:
            graph.add(triple)
            if isinstance(triple[0], URIRef) and not protected(triple[0], config):
                locations[str(triple[0])].add(f)
    entries = manifest["terms"]
    if set(entries) != set(locations):
        missing, extra = set(locations) - set(entries), set(entries) - set(locations)
        raise ModelError(
            f"Missing/unexplained mappings: missing={sorted(missing)}, extra={sorted(extra)}"
        )
    targets = defaultdict(set)
    for original, files in sorted(locations.items()):
        entry = entries[original]
        construct = kind(graph, URIRef(original))
        if retained(URIRef(original), config):
            target, label = original, source_label(graph, URIRef(original))
        else:
            name, label = naming(URIRef(original), construct, config)
            target = config["namespace"] + name
        if entry != {
            "target": target,
            "kind": construct,
            "english_label": label,
            "sources": sorted(files),
        }:
            raise ModelError(
                f"Incorrect mapping for {original} at {sorted(files)}: expected {target!r}"
            )
        targets[entry["target"]].add(original)
    allowed_merges = {
        frozenset(m["uris"]) for m in config.get("merges", []) if m.get("reason")
    }
    for target, originals in targets.items():
        automatic = consolidates(config, entries, originals)
        if (
            len(originals) > 1
            and not automatic
            and frozenset(originals) not in allowed_merges
        ):
            raise ModelError(
                f"URI collision / unexplained merge at {target}: {sorted(originals)}"
            )
        if len({entries[u]["kind"] for u in originals}) > 1:
            raise ModelError(f"Incompatible definitions merged at {target}")
        if len({entries[u]["english_label"] for u in originals}) > 1:
            raise ModelError(f"Incompatible English labels at {target}")
    consolidations = [
        {
            "target": target,
            "uris": sorted(originals),
            "kind": entries[next(iter(originals))]["kind"],
        }
        for target, originals in sorted(targets.items())
        if len(originals) > 1 and consolidates(config, entries, originals)
    ]
    if manifest.get("consolidations", []) != consolidations:
        raise ModelError(
            "Map consolidations differ from selected class/property collisions"
        )
    for pair in config["naming"].get("inverse_pairs", []):
        for key, name in [("direct", "direct_name"), ("reverse", "reverse_name")]:
            if (
                pair[key] in entries
                and not retained(URIRef(pair[key]), config)
                and entries[pair[key]]["target"] != config["namespace"] + pair[name]
            ):
                raise ModelError(
                    f"Incorrect inverse mapping: {pair[key]} must map to {pair[name]}"
                )
    return graph, locations


def rooted_view(graph, root):
    """Unfold sharing, coalescing only identical anonymous shapes, then compare RDF isomorphism."""
    result = Graph()

    def shape_signature(node):
        closure, pending, seen = Graph(), [node], set()
        while pending:
            current = pending.pop()
            if current in seen:
                continue
            seen.add(current)
            for triple in graph.triples((current, None, None)):
                closure.add(triple)
                if isinstance(triple[2], BNode):
                    pending.append(triple[2])
        closure.add((URIRef("urn:verify:root"), URIRef("urn:verify:shape"), node))
        return to_isomorphic(closure).graph_digest()

    def visit(source, target, ancestors):
        seen_shapes = set()
        for predicate, obj in graph.predicate_objects(source):
            if isinstance(obj, BNode):
                is_shape = any(graph.objects(obj, SH.path)) or bool(
                    set(graph.objects(obj, RDF.type)) & {SH.NodeShape, SH.PropertyShape}
                )
                if is_shape:
                    signature = (predicate, shape_signature(obj))
                    if signature in seen_shapes:
                        continue
                    seen_shapes.add(signature)
                if obj in ancestors:
                    clone = ancestors[obj]
                else:
                    clone = BNode()
                    visit(obj, clone, {**ancestors, obj: clone})
                result.add((target, predicate, clone))
            else:
                result.add((target, predicate, obj))

    visit(root, root, {root: root})
    return result


def verify_graphs(config, root, manifest, outputs):
    sources, core, normal = load_sources(config, root)
    excluded = hierarchy_exclusions(config, sources, core, normal)
    reference_omissions = reference_exclusions(config, sources)
    selected = independent_selection(
        config, sources, core, normal, excluded | reference_omissions
    )
    metadata = {f: ontology_metadata(g, config) for f, g in sources.items()}
    if "source_sha256" in manifest:
        hashes = {
            f: sha256((root / f).read_bytes()).hexdigest() for f in sorted(selected)
        }
        if manifest["source_sha256"] != hashes:
            raise ModelError(
                "Source file hashes differ from map; inputs changed since this run"
            )
    if manifest.get("core") != sorted(core):
        raise ModelError("Core input coverage differs from map")
    original_graph, locations = audit_map(config, selected, manifest)
    entries = manifest["terms"]
    documents = external_documents(config, root, selected, core, entries)
    if manifest.get("external_documents", {}) != documents:
        raise ModelError("External document provenance differs from selected sources")
    if manifest.get("outputs") != output_paths(config, documents):
        raise ModelError("Output paths differ from selected external documents")
    partitions = {"rdfs", "shacl", *documents.values()}
    if set(outputs) != partitions:
        raise ModelError("Missing/unexpected output documents")
    for partition in documents.values():
        if any(
            isinstance(subject, URIRef) and str(subject).startswith(config["namespace"])
            for subject in outputs[partition].subjects()
        ):
            raise ModelError(
                f"{partition}: consolidated namespace definition in external output"
            )

    def mapped(term):
        if isinstance(term, URIRef) and str(term) in entries:
            return URIRef(entries[str(term)]["target"])
        if (
            isinstance(term, Literal)
            and term.datatype
            and str(term.datatype) in entries
        ):
            return Literal(
                str(term),
                datatype=entries[str(term.datatype)]["target"],
                normalize=False,
            )
        return term

    # Establish shape ownership from the original graph, without using the merger.
    shape_nodes = {s for s, p, _ in original_graph if str(p).startswith(str(SH))}
    shape_nodes.update(original_graph.subjects(RDF.type, OWL.Ontology))
    while True:
        linked = {
            o
            for s in shape_nodes
            for o in original_graph.objects(s)
            if isinstance(o, BNode)
        }
        if linked <= shape_nodes:
            break
        shape_nodes.update(linked)
    # Recompute anonymous ownership by fixed point, independently of the exporter.
    owners = defaultdict(set)
    for filename, triples in selected.items():
        for subject, _, _ in triples:
            if isinstance(subject, URIRef):
                owners[filename, subject].add(
                    definition_partition(
                        config, subject, entries, documents, shape_nodes
                    )
                )
        while True:
            changed = False
            for subject, predicate, obj in triples:
                if (
                    isinstance(obj, BNode)
                    and (filename, (subject, predicate, obj)) not in excluded
                    and (filename, (subject, predicate, obj)) not in reference_omissions
                ):
                    additions = owners[filename, subject] - owners[filename, obj]
                    if additions:
                        owners[filename, obj].update(additions)
                        changed = True
            if not changed:
                break
        for subject, _, _ in triples:
            if not owners[filename, subject]:
                owners[filename, subject].add(
                    definition_partition(
                        config, subject, entries, documents, shape_nodes
                    )
                )
    changes, additions = {}, []
    for change in manifest["changes"]:
        before = (
            tuple(term_from(t) for t in change["before"]) if change["before"] else None
        )
        after = (
            tuple(term_from(t) for t in change["after"]) if change["after"] else None
        )
        filename = change["source"]
        if before is None:
            additions.append((filename, after, change["reason"]))
            continue
        if filename not in selected or before not in selected[filename]:
            raise ModelError(
                f"Change references absent source triple at {filename}: {before}"
            )
        key = (filename, before)
        if key in changes:
            raise ModelError(f"Duplicate change record at {filename}: {before}")
        s, p, o = before
        partition = min(
            owners[filename, s], key=lambda p: (p not in ("rdfs", "shacl"), p)
        )
        permitted, reason = None, None
        if (filename, before) in reference_omissions:
            reason = (
                "omit non-external reference"
                if p == RDFS.seeAlso
                else "omit non-external reference subtree"
            )
        elif (filename, before) in excluded:
            reason = "omit unused superclass axiom"
        elif p == RDFS.seeAlso and isinstance(o, URIRef):
            permitted = (mapped(s), mapped(p), o)
            reason = "preserve original reference"
        elif p == OWL.imports and not (retained(s, config) or retained(o, config)):
            reason = "replace remote imports with local dependency link"
        elif p == RDFS.isDefinedBy and not (retained(s, config) or retained(o, config)):
            permitted = (mapped(s), p, document_uri(config, partition))
            reason = "local definition document"
        elif (
            p in (RDFS.label, SH.name)
            and isinstance(o, Literal)
            and o.language == "en"
            and str(s) in entries
            and not retained(s, config)
        ):
            permitted = (
                mapped(s),
                mapped(p),
                Literal(entries[str(s)]["english_label"], lang="en"),
            )
            reason = "configured English name"
        elif p in EXECUTABLE and isinstance(o, Literal):
            permitted = (
                mapped(s),
                mapped(p),
                rewrite_executable(
                    o, executable_namespaces(sources[filename]), entries
                ),
            )
            reason = "mapped executable URI references"
        elif (
            str(p) in config.get("header_values", {})
            and (s, RDF.type, OWL.Ontology) in original_graph
            and not retained(s, config)
        ):
            permitted = (mapped(s), mapped(p), Literal(config["header_values"][str(p)]))
            reason = "consolidated namespace header"
        elif s in metadata[filename] or annotation_predicate(p, config):
            permitted = (mapped(s), p, o)
            reason = "preserve ontology metadata vocabulary"
        if reason is None or reason != change["reason"] or permitted != after:
            raise ModelError(f"Unapproved change at {filename}: {before} -> {after}")
        changes[key] = after

    expected = {key: Graph() for key in ("rdfs", "shacl", *documents.values())}
    for filename, triples in selected.items():
        for triple in triples:
            after = changes.get((filename, triple), tuple(mapped(t) for t in triple))
            if after:
                for partition in owners[filename, triple[0]]:
                    expected[partition].add(after)
    for filename, after, reason in additions:
        matches = [
            u
            for u, e in entries.items()
            if not retained(URIRef(u), config)
            and filename in e["sources"]
            and (
                after
                == (
                    URIRef(e["target"]),
                    RDFS.label,
                    Literal(e["english_label"], lang="en"),
                )
                or (
                    external_reference(URIRef(e["target"]), URIRef(u))
                    and after == (URIRef(e["target"]), RDFS.seeAlso, URIRef(u))
                )
            )
        ]
        expected_reason = (
            "original term reference"
            if after and after[1] == RDFS.seeAlso
            else "configured English label"
        )
        if not matches or reason != expected_reason:
            raise ModelError(f"Unapproved annotation addition at {filename}: {after}")
        partition = definition_partition(
            config, URIRef(matches[0]), entries, documents, shape_nodes
        )
        expected[partition].add(after)
    for partition in expected:
        doc = document_uri(config, partition)
        if partition in ("rdfs", "shacl"):
            expected[partition].add((doc, RDF.type, OWL.Ontology))
        if partition == "shacl":
            expected[partition].add((doc, OWL.imports, document_uri(config, "rdfs")))
        elif partition == "rdfs":
            for external in documents.values():
                expected[partition].add(
                    (doc, OWL.imports, document_uri(config, external))
                )
        generated = [
            [term_data(t) for t in triple]
            for triple in sorted(
                expected[partition].triples((doc, None, None)),
                key=lambda t: tuple(x.n3() for x in t),
            )
        ]
        if manifest.get("generated", {}).get(partition) != generated:
            raise ModelError(f"{partition}: generated ontology header differs from map")

    mapped_locations = defaultdict(set)
    for original, files in locations.items():
        mapped_locations[URIRef(entries[original]["target"])].update(files)
    for partition, wanted in expected.items():
        actual = outputs[partition]
        wanted_roots = {s for s in wanted.subjects() if isinstance(s, URIRef)}
        actual_roots = {s for s in actual.subjects() if isinstance(s, URIRef)}
        if wanted_roots != actual_roots:
            missing = wanted_roots - actual_roots
            raise ModelError(
                f"{partition}: missing definitions {sorted(map(str, missing))}, "
                f"unexplained definitions {sorted(map(str, actual_roots - wanted_roots))}; "
                f"sources: {[sorted(mapped_locations[s]) for s in missing]}"
            )
        reached = set()
        for subject in sorted(wanted_roots, key=str):
            # Track original blank nodes too, to reject unrooted/lost source components.
            pending = [subject]
            while pending:
                node = pending.pop()
                if node in reached:
                    continue
                reached.add(node)
                pending.extend(o for o in wanted.objects(node) if isinstance(o, BNode))
            before, after = rooted_view(wanted, subject), rooted_view(actual, subject)
            if not isomorphic(before, after):
                _, lost, added = graph_diff(to_isomorphic(before), to_isomorphic(after))
                raise ModelError(
                    f"{partition}: lost/changed triples for {subject} at "
                    f"{sorted(mapped_locations[subject])}; "
                    f"missing={list(lost)[:5]}, extra={list(added)[:5]}"
                )
        unrooted = set(wanted.subjects()) - reached
        if unrooted:
            raise ModelError(
                f"{partition}: unrooted source blank-node component cannot be dropped: "
                f"{sorted(map(str, unrooted))[:3]}"
            )
        actual_reached, pending = set(), list(actual_roots)
        while pending:
            node = pending.pop()
            if node not in actual_reached:
                actual_reached.add(node)
                pending.extend(o for o in actual.objects(node) if isinstance(o, BNode))
        if set(actual.subjects()) - actual_reached:
            raise ModelError(
                f"{partition}: unexplained anonymous definitions in output"
            )
    combined = union(outputs)
    for subject, obj in combined.subject_objects(RDFS.seeAlso):
        if not external_reference(subject, obj):
            raise ModelError(f"Non-external rdfs:seeAlso reference: {subject} -> {obj}")
    documentary_predicates = {
        mapped(URIRef(p)) for p in config["documentary_predicates"]
    }
    local_documents = {document_uri(config, key) for key in outputs}
    for s, p, o in combined:
        for term in [p] + ([] if p in documentary_predicates else [o]):
            if (
                isinstance(term, URIRef)
                and str(term).startswith(config["namespace"])
                and term not in local_documents
                and not any(combined.triples((term, None, None)))
            ):
                raise ModelError(f"Dangling domain reference {term} at {s} / {p}")
    for original, entry in entries.items():
        if retained(URIRef(original), config):
            continue
        if (
            external_reference(URIRef(entry["target"]), URIRef(original))
            and (URIRef(entry["target"]), RDFS.seeAlso, URIRef(original))
            not in combined
        ):
            raise ModelError(
                f"Missing original term reference for {original} at {entry['sources']}"
            )
        if (
            URIRef(entry["target"]),
            RDFS.label,
            Literal(entry["english_label"], lang="en"),
        ) not in combined:
            raise ModelError(
                f"Missing configured English label for {original} at {entry['sources']}"
            )
    for filename, before in excluded:
        if (
            filename in selected
            and before in selected[filename]
            and changes.get((filename, before), ()) is not None
        ):
            raise ModelError(
                f"Missing superclass omission record at {filename}: {before}"
            )
    for filename, before in reference_omissions:
        if (
            filename in selected
            and before in selected[filename]
            and changes.get((filename, before), ()) is not None
        ):
            raise ModelError(
                f"Missing non-external reference omission record at {filename}: {before}"
            )
    syntax_check(combined)
    return {
        "constructs": len(entries),
        "core_files": len(core),
        "source_triples": sum(map(len, selected.values())),
    }


def verify_run(config, root, map_path=None):
    map_path = Path(map_path) if map_path else root / config["outputs"]["map"]
    if not map_path.exists() and map_path.parent == Path("."):
        map_path = root / "model" / map_path
    manifest = json.loads(map_path.read_text())
    outputs = load_outputs(config, root)
    return verify_graphs(config, root, manifest, outputs)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="scripts/consolidate/model-config.json")
    parser.add_argument("--map", default=None)
    args = parser.parse_args(argv)
    try:
        config, root = read_config(args.config)
        report = verify_run(config, root, args.map)
        print(
            f"100% coverage: {report['constructs']} constructs, {report['core_files']} core files, "
            f"{report['source_triples']} source triples; zero unresolved conflicts; SHACL syntax valid."
        )
    except (ModelError, OSError, ValueError) as exc:
        print(f"Model verification failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
