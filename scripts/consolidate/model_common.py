"""Local RDF input handling shared by the exporter and independent verifier."""

import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit

import rdflib
from rdflib import BNode, Graph, Literal, Namespace, OWL, RDF, RDFS, URIRef
from rdflib.compare import to_canonical_graph

SH = Namespace("http://www.w3.org/ns/shacl#")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")


class ModelError(ValueError):
    pass


def read_config(filename):
    path = Path(filename).resolve()
    if not path.exists() and path.parent == Path.cwd():
        path = Path("model", path.name).resolve()
    config = json.loads(path.read_text())
    root = (path.parent / config.get("root", "..")).resolve()
    return config, root


def parse_turtle(path, base, *, data=None):
    normalize = rdflib.NORMALIZE_LITERALS
    try:
        rdflib.NORMALIZE_LITERALS = False
        return Graph().parse(path, data=data, format="turtle", publicID=base)
    finally:
        rdflib.NORMALIZE_LITERALS = normalize


def parse_source(root, filename):
    # Stable base for files without @base, and disjoint blank-node scopes per file.
    graph = parse_turtle(
        root / filename, "https://data.hetarchief.be/source/" + filename
    )
    canonical = to_canonical_graph(graph)
    scope = hashlib.sha256(filename.encode()).hexdigest()[:12]
    result = Graph()
    for prefix, namespace in graph.namespaces():
        result.bind(prefix, namespace)
    for triple in canonical:
        result.add(
            tuple(
                BNode(scope + "_" + str(t)) if isinstance(t, BNode) else t
                for t in triple
            )
        )
    return result


def load_sources(config, root):
    core = list(config["core"]) + list(config.get("drafts", []))
    if any("draft" in Path(f).parts for f in config["core"]):
        raise ModelError("Drafts must be listed explicitly in drafts, not core")
    external = sorted(
        {
            str(p.relative_to(root))
            for pattern in config["external"]
            for p in root.glob(pattern)
        }
    ) + config.get("supplemental", [])
    local = sorted(
        {
            str(p.relative_to(root))
            for pattern in config["local_concepts"]
            for p in root.glob(pattern)
        }
    )
    fallback = {
        f for files in config.get("missing_definitions", {}).values() for f in files
    }
    sources = {
        f: parse_source(root, f)
        for f in sorted(set(core + external + local) | fallback)
    }
    return sources, core, set(core + external + local)


def external_documents(config, root, selected, core, mapping):
    files = {
        str(path.relative_to(root))
        for pattern in config["external"]
        for path in root.glob(pattern)
    }
    files.update(
        filename
        for filenames in config.get("missing_definitions", {}).values()
        for filename in filenames
    )
    documents = {}
    for filename in sorted((files & selected.keys()) - set(core)):
        for subject, _, _ in selected[filename]:
            if not isinstance(subject, URIRef):
                continue
            target = str(mapping.get(str(subject), {}).get("target", subject))
            if target.startswith(config["namespace"]):
                continue
            matches = [
                (namespace, prefix)
                for prefix, namespace in config["prefixes"].items()
                if target.startswith(namespace) and prefix
            ]
            if not matches:
                raise ModelError(
                    f"Configure a namespace prefix for external definition {target}"
                )
            namespace, prefix = min(
                matches, key=lambda item: (-len(item[0]), len(item[1]), item[1])
            )
            if Path(prefix).name != prefix or prefix in (".", "..") or "\\" in prefix:
                raise ModelError(
                    f"External ontology prefix is not a safe filename: {prefix}"
                )
            documents[namespace] = f"external/{prefix.lower()}.rdfs.ttl"
    if len(set(documents.values())) != len(documents):
        raise ModelError(
            "External ontology filenames collide; configure distinct prefixes"
        )
    return dict(sorted(documents.items()))


def definition_partition(config, subject, mapping, documents, shape_nodes):
    target = str(mapping.get(str(subject), {}).get("target", subject))
    core = "shacl" if subject in shape_nodes else "rdfs"
    if isinstance(subject, URIRef) and not target.startswith(config["namespace"]):
        for namespace in sorted(documents, key=len, reverse=True):
            if target.startswith(namespace):
                return documents[namespace]
    return core


def document_name(partition):
    return f"model.{partition}.ttl" if partition in ("rdfs", "shacl") else partition


def document_uri(config, partition):
    return URIRef(config["namespace"] + document_name(partition))


def output_paths(config, documents):
    outputs = {key: config["outputs"][key] for key in ("rdfs", "shacl", "map")}
    directory = Path(outputs["rdfs"]).parent
    outputs.update({name: str(directory / name) for name in documents.values()})
    return outputs


def load_outputs(config, root):
    return {
        key: parse_turtle(root / filename, str(document_uri(config, key)))
        for key, filename in config["outputs"].items()
        if key != "map"
    }


def protected(uri, config):
    return str(uri) in config.get("preserve_uris", []) or any(
        str(uri).startswith(ns) for ns in config["preserve_namespaces"]
    )


def retained(uri, config):
    namespaces = config.get("retain_namespaces", [])
    if not isinstance(namespaces, list) or any(
        not isinstance(ns, str) or not ns for ns in namespaces
    ):
        raise ModelError(
            "retain_namespaces must be a list of nonempty namespace strings"
        )
    return isinstance(uri, URIRef) and any(str(uri).startswith(ns) for ns in namespaces)


def consolidates(config, entries, originals):
    enabled = config.get("consolidate_collisions", False)
    if not isinstance(enabled, bool):
        raise ModelError("consolidate_collisions must be a boolean")
    kinds = {entries[uri]["kind"] for uri in originals}
    return (
        enabled
        and kinds in ({"class"}, {"property"})
        and all(not retained(URIRef(uri), config) for uri in originals)
    )


def source_label(graph, subject):
    for predicate in (RDFS.label, SH.name):
        labels = sorted(
            str(label)
            for label in graph.objects(subject, predicate)
            if isinstance(label, Literal) and label.language == "en"
        )
        if labels:
            return labels[0]
    return local_name(subject)


def documentary(predicate, config):
    return str(predicate) in config["documentary_predicates"]


def annotation_predicate(predicate, config):
    return documentary(predicate, config) or any(
        str(predicate).startswith(ns) for ns in config.get("annotation_namespaces", [])
    )


def ontology_metadata(graph, config):
    nodes = set(graph.subjects(RDF.type, OWL.Ontology))
    nodes.update(
        o
        for _, p, o in graph
        if isinstance(o, BNode)
        and p != RDFS.seeAlso
        and annotation_predicate(p, config)
    )
    pending = list(nodes)
    while pending:
        for obj in graph.objects(pending.pop()):
            if isinstance(obj, BNode) and obj not in nodes:
                nodes.add(obj)
                pending.append(obj)
    return nodes


def external_reference(subject, obj):
    if not isinstance(subject, URIRef) or not isinstance(obj, URIRef):
        return False
    source_host, target_host = (
        urlsplit(str(subject)).hostname,
        urlsplit(str(obj)).hostname,
    )
    return bool(source_host and target_host and source_host != target_host)


def reference_exclusions(config, sources):
    excluded = set()
    for filename, graph in sources.items():
        removed = set()
        for subject, obj in graph.subject_objects(RDFS.seeAlso):
            target = (
                subject
                if protected(subject, config) or retained(subject, config)
                else URIRef(config["namespace"])
            )
            if isinstance(subject, BNode) or not external_reference(target, obj):
                removed.add((subject, RDFS.seeAlso, obj))
        # Remove only anonymous subgraphs detached by a discarded reference.
        affected, pending = set(), [o for _, _, o in removed if isinstance(o, BNode)]
        while pending:
            node = pending.pop()
            if node not in affected:
                affected.add(node)
                pending.extend(o for o in graph.objects(node) if isinstance(o, BNode))
        if affected:
            reachable, pending = (
                set(),
                [s for s in set(graph.subjects()) if isinstance(s, URIRef)],
            )
            while pending:
                node = pending.pop()
                if node not in reachable:
                    reachable.add(node)
                    pending.extend(
                        o
                        for _, p, o in graph.triples((node, None, None))
                        if isinstance(o, BNode) and (node, p, o) not in removed
                    )
            removed.update(
                t
                for node in affected - reachable
                for t in graph.triples((node, None, None))
            )
        excluded.update((filename, t) for t in removed)
    return excluded


def references(triple, config):
    s, p, o = triple
    if annotation_predicate(p, config):
        return
    if isinstance(p, URIRef) and not protected(p, config):
        yield p
    if (
        isinstance(o, URIRef)
        and not protected(o, config)
        and not documentary(p, config)
        and not any(
            str(o).startswith(ns) for ns in config.get("documentary_namespaces", [])
        )
    ):
        yield o
    if isinstance(o, Literal) and o.datatype and not protected(o.datatype, config):
        yield o.datatype


def hierarchy_exclusions(config, sources, core, normal):
    enabled = config.get("prune_unused_superclasses", False)
    if not isinstance(enabled, bool):
        raise ModelError("prune_unused_superclasses must be a boolean")
    if not enabled:
        return set()
    shape_nodes = {
        (f, s)
        for f, graph in sources.items()
        for s, p, o in graph
        if str(p).startswith(str(SH))
        or p in (RDF.first, RDF.rest)
        or (p == RDF.type and o in (SH.NodeShape, SH.PropertyShape))
    }
    pending = [(f, s) for f, s in shape_nodes if f in core]
    visited, used = set(), set()
    while pending:
        filename, subject = pending.pop()
        if (filename, subject) in visited:
            continue
        visited.add((filename, subject))
        graph = sources[filename]
        if (subject, RDF.type, RDFS.Class) in graph or (
            subject,
            RDF.type,
            OWL.Class,
        ) in graph:
            used.add(subject)
        for _, predicate, obj in graph.triples((subject, None, None)):
            if predicate in (SH["class"], SH.targetClass):
                used.add(obj)
            if predicate in EXECUTABLE and isinstance(obj, Literal):
                used.update(
                    uri
                    for _, _, uri in executable_tokens(
                        str(obj), executable_namespaces(graph)
                    )
                )
            if isinstance(obj, BNode):
                pending.append((filename, obj))
            elif isinstance(obj, URIRef) and (
                str(predicate).startswith(str(SH)) or predicate in (RDF.first, RDF.rest)
            ):
                files = [f for f in normal if (f, obj) in shape_nodes]
                if not files:
                    files = [
                        f
                        for f in config.get("missing_definitions", {}).get(str(obj), [])
                        if (f, obj) in shape_nodes
                    ]
                pending.extend((f, obj) for f in files)
    ancestors = {
        obj
        for graph in sources.values()
        for obj in graph.objects(None, RDFS.subClassOf)
        if isinstance(obj, URIRef)
    }
    # Domains and class axioms can otherwise reimport ancestors excluded from the hierarchy.
    return {
        (f, (s, p, o))
        for f, graph in sources.items()
        for s, p, o in graph
        if isinstance(o, URIRef)
        and o not in used
        and not protected(o, config)
        and (
            p == RDFS.subClassOf
            or (
                o in ancestors
                and p in (RDFS.domain, OWL.equivalentClass, OWL.disjointWith)
            )
        )
    }


def select_sources(config, sources, core, normal, excluded=()):
    """Compute subject closure; fallback definitions are allowed only by exact URI."""
    index = {}
    for filename, graph in sources.items():
        for subject in set(graph.subjects()):
            index.setdefault(subject, []).append(filename)
    selected = {f: set(g) if f in core else set() for f, g in sources.items()}
    metadata = {f: ontology_metadata(g, config) for f, g in sources.items()}
    pending = [(f, t) for f in core for t in sources[f]]
    seen, unresolved = set(), set()
    while pending:
        filename, triple = pending.pop()
        if (filename, triple) in excluded:
            continue
        candidates = (
            [] if triple[0] in metadata[filename] else list(references(triple, config))
        )
        if (
            triple[0] not in metadata[filename]
            and triple[1] in EXECUTABLE
            and isinstance(triple[2], Literal)
        ):
            candidates.extend(
                uri
                for _, _, uri in executable_tokens(
                    str(triple[2]), executable_namespaces(sources[filename])
                )
                if not protected(uri, config)
            )
        if isinstance(triple[2], BNode):
            candidates.append(triple[2])
        for node in candidates:
            key = (filename, node) if isinstance(node, BNode) else node
            if key in seen:
                continue
            seen.add(key)
            if isinstance(node, BNode):
                files = [filename]
            else:
                files = [f for f in index.get(node, []) if f in normal]
                if not files:
                    files = [
                        f
                        for f in config.get("missing_definitions", {}).get(
                            str(node), []
                        )
                        if node in index and f in index[node]
                    ]
                if not files:
                    unresolved.add(
                        (str(node), filename, str(triple[0]), str(triple[1]))
                    )
                    continue
            for source in files:
                additions = set(sources[source].triples((node, None, None)))
                # A referenced local scheme brings its concepts, not unrelated schemes.
                if (
                    source in normal
                    and source not in core
                    and source.endswith(".skos.ttl")
                ):
                    for relation in (SKOS.inScheme, SKOS.topConceptOf):
                        for member in sources[source].subjects(relation, node):
                            additions.update(
                                sources[source].triples((member, None, None))
                            )
                for item in additions - selected[source]:
                    selected[source].add(item)
                    pending.append((source, item))
    if unresolved:
        raise ModelError(
            "Unresolved definitions (configure exact missing_definitions):\n"
            + "\n".join(
                f"  {uri} at {f}: {s} / {p}" for uri, f, s, p in sorted(unresolved)
            )
        )
    return {f: triples for f, triples in selected.items() if triples}


def union(selected):
    graph = Graph()
    for triples in selected.values():
        for triple in triples:
            graph.add(triple)
    return graph


def kind(graph, subject):
    types = set(graph.objects(subject, RDF.type))
    if types & {SH.NodeShape, SH.PropertyShape} or any(
        str(p).startswith(str(SH)) for p in graph.predicates(subject)
    ):
        return "shape"
    if types & {RDFS.Class, OWL.Class} or any(graph.objects(subject, RDFS.subClassOf)):
        return "class"
    if types & {
        RDF.Property,
        OWL.ObjectProperty,
        OWL.DatatypeProperty,
        OWL.AnnotationProperty,
        OWL.SymmetricProperty,
        OWL.TransitiveProperty,
        OWL.FunctionalProperty,
    }:
        return "property"
    if OWL.Ontology in types:
        return "ontology"
    if SKOS.ConceptScheme in types or SKOS.Collection in types:
        return "scheme"
    return "concept"


def json_write(path, value):
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    )


def words(value):
    import re

    return re.findall(r"[A-Z]+(?=[A-Z][a-z]|[0-9]|$)|[A-Z]?[a-z]+|[0-9]+", value)


def local_name(uri):
    return str(uri).rsplit("#", 1)[-1].rsplit("/", 1)[-1]


def naming(uri, construct, config):
    """Pure config policy, also checked by the verifier against the recorded map."""
    naming_config = config["naming"]
    override = naming_config.get("overrides", {}).get(str(uri), {})
    tokens = words(local_name(uri))
    acronyms = naming_config.get("acronyms", [])
    pascal = "".join(
        t.upper() if t.upper() in acronyms else t.capitalize() for t in tokens
    )
    if construct == "property":
        name = naming_config.get("property_names", {}).get(str(uri))
        if name is None:
            # Noun properties express possession. Verbs/inverses require explicit names.
            name = "has" + pascal
    elif construct == "shape":
        name = pascal.replace("NodeShape", "Shape")
        if not name.endswith("Shape"):
            name += "Shape"
    else:
        name = pascal
    style = naming_config.get(
        f"{construct}_case",
        "PascalCase" if construct in ("class", "shape") else "lowerCamelCase",
    )
    if style not in ("PascalCase", "lowerCamelCase"):
        raise ModelError(f"Unsupported case rule: {style}")
    if name:
        name = (
            name[0].lower() if style == "lowerCamelCase" else name[0].upper()
        ) + name[1:]
    name = override.get("name", name)
    import re

    pattern = (
        r"[a-z][A-Za-z0-9]*" if style == "lowerCamelCase" else r"[A-Z][A-Za-z0-9]*"
    )
    if not re.fullmatch(pattern, name):
        raise ModelError(
            f"Invalid {construct} name {name!r} for {uri}; configure an override"
        )
    label = override.get(
        "label", " ".join(t if t in acronyms else t.lower() for t in words(name))
    )
    return name, label


def term_data(term):
    if isinstance(term, Literal):
        return {
            "literal": str(term),
            "language": term.language,
            "datatype": str(term.datatype) if term.datatype else None,
        }
    return {"bnode": str(term)} if isinstance(term, BNode) else {"uri": str(term)}


def term_from(data):
    if "literal" in data:
        return Literal(
            data["literal"],
            lang=data["language"],
            datatype=data["datatype"],
            normalize=False,
        )
    return BNode(data["bnode"]) if "bnode" in data else URIRef(data["uri"])


def syntax_check(shapes):
    from pyshacl import validate
    from pyshacl.errors import ReportableRuntimeError

    try:
        # Imports are deliberately disabled: the dependency closure is already local.
        conforms, _, report = validate(
            Graph(),
            shacl_graph=shapes + Graph(),
            meta_shacl=True,
            do_owl_imports=False,
            advanced=True,
        )
    except ReportableRuntimeError as exc:
        raise ModelError(f"SHACL syntax validation failed: {exc}") from exc
    if not conforms:
        raise ModelError(f"SHACL syntax validation failed:\n{report}")


EXECUTABLE = {SH.select, SH.ask, SH.construct, SH.update}


def executable_namespaces(graph):
    namespaces = dict(graph.namespaces())
    declared = {}
    for node, prefix in graph.subject_objects(SH.prefix):
        namespace = graph.value(node, SH.namespace)
        if namespace is None:
            raise ModelError(f"Missing sh:namespace on prefix declaration {node}")
        if str(prefix) in declared and declared[str(prefix)] != str(namespace):
            raise ModelError(f"Conflicting executable prefix declarations for {prefix}")
        declared[str(prefix)] = str(namespace)
    namespaces.update(declared)
    return namespaces.items()


def executable_tokens(text, namespaces):
    """Yield replaceable SPARQL IRI tokens, skipping strings and comments."""
    import re

    pattern = re.compile(
        r'''\#[^\n]*|"""[\s\S]*?"""|\x27\x27\x27[\s\S]*?\x27\x27\x27|"(?:\\.|[^"\\])*"|\x27(?:\\.|[^\x27\\])*\x27|<[^<>\s]*>|(?:[A-Za-z_][\w-]*)?:[\w.-]+'''
    )
    prefixes = dict(namespaces)
    prefixes.update(re.findall(r"(?i)\bPREFIX\s+([\w-]*):\s*<([^>]+)>", text))
    declarations = list(re.finditer(r"(?i)\b(?:PREFIX\s+[\w-]*:|BASE)\s*<[^>]+>", text))
    for match in pattern.finditer(text):
        if any(d.start() <= match.start() < d.end() for d in declarations):
            continue
        token = match.group()
        if token.startswith("<"):
            yield match.start(), match.end(), URIRef(token[1:-1])
        elif not token.startswith(('"', "'", "#")) and ":" in token:
            prefix, local = token.split(":", 1)
            if prefix in prefixes:
                yield match.start(), match.end(), URIRef(str(prefixes[prefix]) + local)


def rewrite_executable(value, namespaces, mapping):
    text = str(value)
    for start, end, uri in reversed(list(executable_tokens(text, namespaces))):
        if str(uri) in mapping and mapping[str(uri)]["target"] != str(uri):
            text = text[:start] + "<" + mapping[str(uri)]["target"] + ">" + text[end:]
    return Literal(text, lang=value.language, datatype=value.datatype, normalize=False)
