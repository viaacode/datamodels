#!/usr/bin/env python3
"""Consolidate configured local RDF definitions without changing the originals."""

import argparse
from collections import defaultdict
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
from io import BytesIO
from pathlib import Path
from posixpath import dirname, relpath
import sys
from tempfile import TemporaryDirectory

from rdflib import BNode, Graph, Literal, OWL, RDF, RDFS, URIRef, XSD
from rdflib.compare import to_canonical_graph, to_isomorphic
from rdflib.plugins.serializers.longturtle import LongTurtleSerializer

from model_common import (
    EXECUTABLE,
    ModelError,
    SH,
    annotation_predicate,
    consolidates,
    executable_namespaces,
    definition_partition,
    document_name,
    document_uri,
    external_documents,
    external_reference,
    hierarchy_exclusions,
    json_write,
    kind,
    load_sources,
    naming,
    ontology_metadata,
    output_paths,
    parse_turtle,
    protected,
    read_config,
    reference_exclusions,
    rewrite_executable,
    retained,
    select_sources,
    source_label,
    term_data,
    union,
)
from visualize_model_map import render


def make_mapping(config, selected):
    graph = union(selected)
    entries, targets = {}, defaultdict(list)
    for subject in sorted(set(graph.subjects()), key=str):
        if not isinstance(subject, URIRef) or protected(subject, config):
            continue
        construct = kind(graph, subject)
        if retained(subject, config):
            target, label = str(subject), source_label(graph, subject)
        else:
            name, label = naming(subject, construct, config)
            target = config["namespace"] + name
        entries[str(subject)] = {
            "target": target,
            "kind": construct,
            "english_label": label,
            "sources": sorted(
                f
                for f, triples in selected.items()
                if any(t[0] == subject for t in triples)
            ),
        }
        targets[target].append(str(subject))
    merges = {frozenset(m["uris"]): m["reason"] for m in config.get("merges", [])}
    for target, originals in targets.items():
        automatic = consolidates(config, entries, originals)
        if (
            len(originals) > 1
            and not automatic
            and not merges.get(frozenset(originals))
        ):
            raise ModelError(
                f"Naming collision at {target}: {originals}; enable class/property consolidation, "
                "configure distinct overrides or an explicit merge"
            )
        kinds = {entries[u]["kind"] for u in originals}
        if len(kinds) > 1:
            raise ModelError(f"Incompatible definitions merged at {target}: {kinds}")
        if len(originals) > 1:
            labels = {entries[u]["english_label"] for u in originals}
            if len(labels) > 1:
                raise ModelError(f"Incompatible English labels at {target}: {labels}")
    for direct, inverse in graph.subject_objects(OWL.inverseOf):
        if (direct, RDF.type, OWL.SymmetricProperty) in graph or (
            retained(direct, config) and retained(inverse, config)
        ):
            continue
        configured = config["naming"].get("inverse_pairs", [])
        if not any(
            {str(direct), str(inverse)} == {p["direct"], p["reverse"]}
            for p in configured
        ):
            raise ModelError(f"Inverse pair needs explicit naming: {direct}, {inverse}")
    for pair in config["naming"].get("inverse_pairs", []):
        for key, name_key in [("direct", "direct_name"), ("reverse", "reverse_name")]:
            if (
                pair[key] in entries
                and not retained(URIRef(pair[key]), config)
                and entries[pair[key]]["target"] != config["namespace"] + pair[name_key]
            ):
                raise ModelError(
                    f"Incorrect inverse mapping: {pair[key]} must be {pair[name_key]}"
                )
    return entries


def check_conflicts(graph):
    for subject in set(graph.subjects()):
        types = set(graph.objects(subject, RDF.type))
        if types & {OWL.Class, RDFS.Class} and types & {
            RDF.Property,
            OWL.ObjectProperty,
            OWL.DatatypeProperty,
        }:
            raise ModelError(f"Incompatible class/property definitions: {subject}")
        for predicate in [SH.path, SH.datatype, SH.nodeKind, SH.minCount, SH.maxCount]:
            if len(set(graph.objects(subject, predicate))) > 1:
                raise ModelError(f"Incompatible {predicate} definitions on {subject}")
        minima, maxima = (
            list(graph.objects(subject, SH.minCount)),
            list(graph.objects(subject, SH.maxCount)),
        )
        if minima and maxima and int(minima[0]) > int(maxima[0]):
            raise ModelError(f"Incompatible min/max counts on {subject}")
        if (subject, OWL.disjointWith, subject) in graph:
            raise ModelError(f"Merge makes {subject} disjoint with itself")


def deduplicate_shapes(graph):
    """Coalesce only structurally identical anonymous shapes; retain contextual variants."""
    signatures, replacements = {}, {}
    candidates = {
        s
        for s in graph.subjects()
        if isinstance(s, BNode)
        and (
            (s, RDF.type, SH.PropertyShape) in graph
            or (s, RDF.type, SH.NodeShape) in graph
            or any(graph.objects(s, SH.path))
        )
    }
    for subject in sorted(candidates, key=str):
        subgraph, pending, seen = Graph(), [subject], set()
        while pending:
            node = pending.pop()
            if node in seen:
                continue
            seen.add(node)
            for triple in graph.triples((node, None, None)):
                subgraph.add(triple)
                if isinstance(triple[2], BNode):
                    pending.append(triple[2])
        subgraph.add((URIRef("urn:model:root"), URIRef("urn:model:shape"), subject))
        digest = to_isomorphic(subgraph).graph_digest()
        if digest in signatures:
            replacements[subject] = signatures[digest]
        else:
            signatures[digest] = subject
    result = Graph()
    for triple in graph:
        if triple[0] in replacements:
            continue
        # Descendant lists are retained if still reachable; orphan copies are pruned below.
        result.add(tuple(replacements.get(t, t) for t in triple))
    reachable = set(s for s in result.subjects() if isinstance(s, URIRef))
    pending = list(reachable)
    while pending:
        for obj in result.objects(pending.pop()):
            if isinstance(obj, BNode) and obj not in reachable:
                reachable.add(obj)
                pending.append(obj)
    pruned = Graph()
    for triple in result:
        if triple[0] in reachable:
            pruned.add(triple)
    return pruned


def transform(
    config,
    sources,
    selected,
    mapping,
    excluded=(),
    reference_omissions=(),
    documents=None,
):
    documents = documents or {}
    outputs = {key: Graph() for key in ("rdfs", "shacl", *documents.values())}
    changes = []
    source_union = union(selected)
    metadata = {f: ontology_metadata(g, config) for f, g in sources.items()}
    shape_subjects = {
        s
        for s in source_union.subjects()
        if kind(source_union, s) in {"shape", "ontology"}
    }
    pending = list(shape_subjects)
    while pending:
        for obj in source_union.objects(pending.pop()):
            if isinstance(obj, BNode) and obj not in shape_subjects:
                shape_subjects.add(obj)
                pending.append(obj)

    # Copy shared anonymous expressions when their owners land in different files.
    owners = defaultdict(set)
    for filename, triples in selected.items():
        children = defaultdict(list)
        for triple in triples:
            if (
                isinstance(triple[2], BNode)
                and (filename, triple) not in excluded
                and (filename, triple) not in reference_omissions
            ):
                children[triple[0]].append(triple[2])
        pending = [
            (s, definition_partition(config, s, mapping, documents, shape_subjects))
            for s, _, _ in triples
            if isinstance(s, URIRef)
        ]
        while pending:
            subject, partition = pending.pop()
            if partition in owners[filename, subject]:
                continue
            owners[filename, subject].add(partition)
            pending.extend((obj, partition) for obj in children[subject])
        for subject, _, _ in triples:
            if not owners[filename, subject]:
                owners[filename, subject].add(
                    definition_partition(
                        config, subject, mapping, documents, shape_subjects
                    )
                )

    def mapped(term):
        if isinstance(term, URIRef):
            return (
                URIRef(mapping[str(term)]["target"]) if str(term) in mapping else term
            )
        if (
            isinstance(term, Literal)
            and term.datatype
            and str(term.datatype) in mapping
        ):
            return Literal(
                str(term),
                datatype=mapping[str(term.datatype)]["target"],
                normalize=False,
            )
        return term

    for filename, triples in selected.items():
        for subject, predicate, obj in sorted(
            triples, key=lambda t: tuple(ti.n3() for ti in t)
        ):
            partitions = owners[filename, subject]
            partition = min(partitions, key=lambda p: (p not in ("rdfs", "shacl"), p))
            before, after = (
                (subject, predicate, obj),
                (mapped(subject), mapped(predicate), mapped(obj)),
            )
            reason = None
            if (filename, before) in reference_omissions:
                after = None
                reason = (
                    "omit non-external reference"
                    if predicate == RDFS.seeAlso
                    else "omit non-external reference subtree"
                )
            elif (filename, before) in excluded:
                after, reason = None, "omit unused superclass axiom"
            elif predicate == RDFS.seeAlso and isinstance(obj, URIRef):
                after = (mapped(subject), mapped(predicate), obj)
                reason = "preserve original reference"
            elif predicate == OWL.imports and not (
                retained(subject, config) or retained(obj, config)
            ):
                after, reason = (
                    None,
                    "replace remote imports with local dependency link",
                )
            elif predicate == RDFS.isDefinedBy and not (
                retained(subject, config) or retained(obj, config)
            ):
                after = (mapped(subject), predicate, document_uri(config, partition))
                reason = "local definition document"
            elif (
                predicate in (RDFS.label, SH.name)
                and isinstance(obj, Literal)
                and obj.language == "en"
                and str(subject) in mapping
                and not retained(subject, config)
            ):
                after = (
                    mapped(subject),
                    mapped(predicate),
                    Literal(mapping[str(subject)]["english_label"], lang="en"),
                )
                reason = "configured English name"
            elif predicate in EXECUTABLE and isinstance(obj, Literal):
                after = (
                    mapped(subject),
                    mapped(predicate),
                    rewrite_executable(
                        obj, executable_namespaces(sources[filename]), mapping
                    ),
                )
                if after[2] != obj:
                    reason = "mapped executable URI references"
            elif (
                str(predicate) in config.get("header_values", {})
                and (subject, RDF.type, OWL.Ontology) in source_union
                and not retained(subject, config)
            ):
                after = (
                    mapped(subject),
                    mapped(predicate),
                    Literal(config["header_values"][str(predicate)]),
                )
                reason = "consolidated namespace header"
            elif subject in metadata[filename] or annotation_predicate(
                predicate, config
            ):
                after = (mapped(subject), predicate, obj)
                reason = "preserve ontology metadata vocabulary"
            if reason and (after is None or after != tuple(mapped(t) for t in before)):
                changes.append(
                    {
                        "source": filename,
                        "before": [term_data(t) for t in before],
                        "after": [term_data(t) for t in after] if after else None,
                        "reason": reason,
                    }
                )
            if after:
                for owner in partitions:
                    outputs[owner].add(after)
    for original, entry in mapping.items():
        subject = URIRef(original)
        if retained(subject, config):
            continue
        for filename in entry["sources"]:
            partition = definition_partition(
                config, subject, mapping, documents, shape_subjects
            )
            if external_reference(URIRef(entry["target"]), subject):
                triple = (URIRef(entry["target"]), RDFS.seeAlso, subject)
                if triple not in outputs[partition]:
                    outputs[partition].add(triple)
                    changes.append(
                        {
                            "source": filename,
                            "before": None,
                            "after": [term_data(t) for t in triple],
                            "reason": "original term reference",
                        }
                    )
            triple = (
                URIRef(entry["target"]),
                RDFS.label,
                Literal(entry["english_label"], lang="en"),
            )
            if triple not in outputs[partition]:
                outputs[partition].add(triple)
                changes.append(
                    {
                        "source": filename,
                        "before": None,
                        "after": [term_data(t) for t in triple],
                        "reason": "configured English label",
                    }
                )
    for partition in ("rdfs", "shacl"):
        graph = outputs[partition]
        document = document_uri(config, partition)
        graph.add((document, RDF.type, OWL.Ontology))
        if partition == "shacl":
            graph.add((document, OWL.imports, document_uri(config, "rdfs")))
        elif partition == "rdfs":
            for external in documents.values():
                graph.add((document, OWL.imports, document_uri(config, external)))
    return outputs, sorted(changes, key=lambda c: str(c))


class PreservingTurtleSerializer(LongTurtleSerializer):
    def orderSubjects(self):
        # Emit owners before single-use anonymous expressions, including typed classes.
        return sorted(
            super().orderSubjects(),
            key=lambda node: (
                isinstance(node, BNode),
                isinstance(node, BNode) and self._references[node] == 1,
            ),
        )

    def isValidList(self, node):
        # Inlining a shared tail can leave later list members without their definitions.
        seen = set()
        while node != RDF.nil:
            if node in seen or node in self._serialized or self._references[node] > 1:
                return False
            seen.add(node)
            if (
                len(list(self.store.predicate_objects(node))) != 2
                or self.store.value(node, RDF.first) is None
            ):
                return False
            node = self.store.value(node, RDF.rest)
            if node is None:
                return False
        return bool(seen)

    def label(self, node, position):
        if isinstance(node, Literal) and node.datatype:
            # Numeric shorthand can lose leading zeroes, decimal scale or float precision.
            canonical_integer = (
                node.datatype == XSD.integer
                and node.value is not None
                and str(node) == str(int(node))
            )
            canonical_boolean = node.datatype == XSD.boolean and str(node) in (
                "true",
                "false",
            )
            if not (canonical_integer or canonical_boolean):
                return node._literal_n3(
                    use_plain=False, qname_callback=lambda dt: self.getQName(dt, False)
                )
        return super().label(node, position)


def readable_turtle(graph, config, partition="rdfs"):
    local_documents = {
        document_uri(config, key): URIRef(
            relpath(document_name(key), dirname(document_name(partition)) or ".")
        )
        for key in config["outputs"]
        if key != "map"
    }
    relative = Graph()
    for triple in graph:
        relative.add(tuple(local_documents.get(t, t) for t in triple))
    canonical = Graph(bind_namespaces="none")
    for triple in to_canonical_graph(relative):
        canonical.add(triple)
    for prefix, uri in config["prefixes"].items():
        canonical.bind(prefix, uri)
    stream = BytesIO()
    PreservingTurtleSerializer(canonical).serialize(stream, encoding="utf-8")
    return stream.getvalue().decode("utf-8")


def build(config, root, *, destination=None):
    config = deepcopy(config)
    sources, core, normal = load_sources(config, root)
    excluded = hierarchy_exclusions(config, sources, core, normal)
    reference_omissions = reference_exclusions(config, sources)
    selected = select_sources(
        config, sources, core, normal, excluded | reference_omissions
    )
    mapping = make_mapping(config, selected)
    documents = external_documents(config, root, selected, core, mapping)
    config["outputs"] = output_paths(config, documents)
    outputs, changes = transform(
        config, sources, selected, mapping, excluded, reference_omissions, documents
    )
    for partition in outputs:
        outputs[partition] = deduplicate_shapes(outputs[partition])
    check_conflicts(union(outputs))
    manifest = {
        "version": 3,
        "external_documents": documents,
        "namespace": config["namespace"],
        "terms": mapping,
        "merges": config.get("merges", []),
        "changes": changes,
        "selected": {f: len(t) for f, t in selected.items()},
        "core": sorted(core),
        "outputs": config["outputs"],
        "source_sha256": {
            f: sha256((root / f).read_bytes()).hexdigest() for f in sorted(selected)
        },
        "retain_namespaces": config.get("retain_namespaces", []),
        "consolidate_collisions": config.get("consolidate_collisions", False),
        "prune_unused_superclasses": config.get("prune_unused_superclasses", False),
    }
    grouped = defaultdict(list)
    for original, entry in mapping.items():
        grouped[entry["target"]].append(original)
    manifest["consolidations"] = [
        {
            "target": target,
            "uris": sorted(originals),
            "kind": mapping[originals[0]]["kind"],
        }
        for target, originals in sorted(grouped.items())
        if len(originals) > 1 and consolidates(config, mapping, originals)
    ]
    manifest["generated"] = {
        p: [
            [term_data(t) for t in triple]
            for triple in sorted(
                outputs[p].triples((document_uri(config, p), None, None)),
                key=lambda t: tuple(x.n3() for x in t),
            )
        ]
        for p in outputs
    }
    # Verify before writing, so a rejected build never replaces good artifacts.
    from verify_model import verify_graphs

    serialized = {p: readable_turtle(g, config, p) for p, g in outputs.items()}
    reparsed = {
        p: parse_turtle(None, str(document_uri(config, p)), data=text)
        for p, text in serialized.items()
    }
    verify_graphs(config, root, manifest, reparsed)
    for partition, text in serialized.items():
        path = (
            destination / document_name(partition)
            if destination is not None
            else root / config["outputs"][partition]
        )
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    map_path = (
        destination / Path(config["outputs"]["map"]).name
        if destination is not None
        else root / config["outputs"]["map"]
    )
    json_write(map_path, manifest)
    return manifest


def build_run(config, root, run_dir=None):
    root = root.resolve()
    run_dir = (
        Path(run_dir)
        if run_dir is not None
        else root
        / "model/runs"
        / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    ).resolve()
    config = deepcopy(config)
    config["root"] = str(root)
    config["outputs"] = {
        key: str(run_dir / name)
        for key, name in {
            "rdfs": "model.rdfs.ttl",
            "shacl": "model.shacl.ttl",
            "map": "model-map.json",
        }.items()
    }
    # Reserve the name first; publish the completed directory only after all checks pass.
    run_dir.mkdir(parents=True, exist_ok=False)
    completed = False
    try:
        with TemporaryDirectory(
            prefix=f".{run_dir.name}-", dir=run_dir.parent
        ) as temporary:
            staging = Path(temporary)
            manifest = build(config, root, destination=staging)
            config["outputs"] = manifest["outputs"]
            json_write(staging / "model-config.json", config)
            try:
                (staging / "model-map.html").write_text(
                    render(manifest), encoding="utf-8"
                )
            except (OSError, ValueError, KeyError, TypeError) as exc:
                raise ModelError(f"HTML report failed: {exc}") from exc
            staging.replace(run_dir)
            completed = True
    finally:
        if not completed:
            run_dir.rmdir()
    return run_dir, manifest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="scripts/consolidate/model-config.json")
    parser.add_argument(
        "--run-dir",
        type=Path,
        help="New output folder (default: model/runs/<UTC timestamp>)",
    )
    args = parser.parse_args(argv)
    try:
        config, root = read_config(args.config)
        run_dir, manifest = build_run(config, root, args.run_dir)
        print(
            f"Built {len(manifest['terms'])} URI mappings; zero unresolved conflicts."
        )
        print(f"Run directory: {run_dir}")
    except (ModelError, OSError, ValueError) as exc:
        print(f"Model build failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
