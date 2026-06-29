#!/usr/bin/env python3
"""Convert the local description RDFS and SHACL Turtle files to LinkML YAML.

This is a small, dependency-free converter for the Turtle style used in this
repository. It is not a general RDF parser. It extracts:

* RDFS classes and haDes properties from description.rdfs.ttl
* SHACL node shapes, property shapes, cardinalities, ranges, and sh:in values
  from description.shacl.ttl
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import OrderedDict, defaultdict
from pathlib import Path


PREFIXES = OrderedDict(
    [
        ("linkml", "https://w3id.org/linkml/"),
        ("haDes", "https://data.hetarchief.be/ns/description/"),
        ("haObj", "https://data.hetarchief.be/ns/object/"),
        ("haOrg", "https://data.hetarchief.be/ns/organization/"),
        ("bf", "http://id.loc.gov/ontologies/bibframe/"),
        ("dct", "http://purl.org/dc/terms/"),
        ("dbo", "http://dbpedia.org/ontology/"),
        ("ebucore", "http://www.ebu.ch/metadata/ontologies/ebucore/ebucore#"),
        ("edtf", "http://id.loc.gov/datatypes/edtf/"),
        ("foaf", "http://xmlns.com/foaf/0.1/"),
        ("org", "http://www.w3.org/ns/org#"),
        ("owl", "http://www.w3.org/2002/07/owl#"),
        ("premis", "http://www.loc.gov/premis/rdf/v3/"),
        ("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#"),
        ("rdfs", "http://www.w3.org/2000/01/rdf-schema#"),
        ("rel", "http://id.loc.gov/vocabulary/preservation/relationshipSubType/"),
        ("schema", "https://schema.org/"),
        ("sh", "http://www.w3.org/ns/shacl#"),
        ("skos", "http://www.w3.org/2004/02/skos/core#"),
        ("xsd", "http://www.w3.org/2001/XMLSchema#"),
        ("haCt", "https://data.hetarchief.be/id/color-type/"),
        ("haEdTId", "https://data.hetarchief.be/id/edition-type/"),
        ("haPrmId", "https://data.hetarchief.be/id/production-method/"),
        ("haRot", "https://data.hetarchief.be/id/rotational-speed/"),
    ]
)

XSD_TO_LINKML = {
    "xsd:string": "string",
    "rdf:langString": "string",
    "rdfs:Literal": "string",
    "rdf:Literal": "string",
    "xsd:integer": "integer",
    "xsd:nonNegativeInteger": "integer",
    "xsd:boolean": "boolean",
    "xsd:float": "float",
    "xsd:decimal": "decimal",
    "xsd:dateTime": "datetime",
    "xsd:date": "date",
    "xsd:time": "time",
    "xsd:duration": "string",
}


def strip_comments(text: str) -> str:
    """Strip Turtle comments while preserving IRIs and quoted strings."""
    output = []
    for line in text.splitlines():
        in_string = False
        in_triple_string = False
        in_angle_iri = False
        escaped = False
        cleaned = ""
        i = 0
        while i < len(line):
            if line[i : i + 3] == '"""' and not escaped and not in_angle_iri:
                in_triple_string = not in_triple_string
                cleaned += line[i : i + 3]
                i += 3
                continue

            char = line[i]
            if not in_string and not in_triple_string:
                if char == "<":
                    in_angle_iri = True
                elif char == ">":
                    in_angle_iri = False

            if char == '"' and not escaped and not in_triple_string and not in_angle_iri:
                in_string = not in_string

            if char == "#" and not in_string and not in_triple_string and not in_angle_iri:
                break

            cleaned += char
            escaped = char == "\\" and not escaped
            if char != "\\":
                escaped = False
            i += 1
        output.append(cleaned)
    return "\n".join(output)


def qname_to_name(value: str) -> str:
    value = value.strip().rstrip(";,")
    if value.startswith("<") and value.endswith(">"):
        iri = value[1:-1]
        local = iri.split("/")[-1].split("#")[-1]
        return re.sub(r"[^A-Za-z0-9_]", "_", local).strip("_") or "IRI"
    if ":" in value:
        _, local = value.split(":", 1)
        return re.sub(r"[^A-Za-z0-9_]", "_", local).strip("_")
    return re.sub(r"[^A-Za-z0-9_]", "_", value).strip("_")


def clean_uri(value: str) -> str:
    value = value.strip().rstrip(";,")
    if value.startswith("<") and value.endswith(">"):
        return value[1:-1]
    return value


def linkml_range(value: str, custom_type_names: dict[str, str] | None = None) -> str:
    if custom_type_names and value in custom_type_names:
        return custom_type_names[value]
    return XSD_TO_LINKML.get(value, qname_to_name(value))


def custom_datatypes(shacl_text: str) -> OrderedDict[str, str]:
    custom_type_names: OrderedDict[str, str] = OrderedDict()
    class_names = {
        qname_to_name(value)
        for value in re.findall(r"sh:(?:class|targetClass)\s+([^\s;\]]+)", shacl_text)
    }
    for datatype in re.findall(r"sh:datatype\s+([^\s;\]]+)", shacl_text):
        if datatype not in XSD_TO_LINKML:
            type_name = qname_to_name(datatype)
            if type_name in class_names:
                print(
                    f"warning: {datatype} is used as both sh:datatype and sh:class; "
                    f"emitting datatype as {type_name}_datatype",
                    file=sys.stderr,
                )
                type_name = f"{type_name}_datatype"
            custom_type_names[datatype] = type_name
    return custom_type_names


def quote_yaml(value: object) -> str:
    text = str(value)
    text = text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    return f'"{text}"'


def enum_meaning(value: str) -> str | None:
    if value.startswith("<") and value.endswith(">"):
        return value[1:-1]
    if re.match(r"^[A-Za-z][A-Za-z0-9_-]*:", value):
        return value
    return None


def yaml_key(value: str) -> str:
    if re.match(r"^[A-Za-z0-9_. -]+$", value):
        return value
    return quote_yaml(value)


def english_literal(block: str, predicate: str) -> str | None:
    patterns = [
        re.escape(predicate) + r'\s+"""(.*?)"""@en',
        re.escape(predicate) + r'\s+"((?:[^"\\]|\\.)*)"@en',
        re.escape(predicate) + r'\s+"""(.*?)"""',
        re.escape(predicate) + r'\s+"((?:[^"\\]|\\.)*)"',
    ]
    for pattern in patterns:
        match = re.search(pattern, block, re.S)
        if match:
            return match.group(1).replace('\\"', '"').strip()
    return None


def extract_rdfs(rdfs_text: str) -> tuple[OrderedDict[str, dict], OrderedDict[str, dict]]:
    classes: OrderedDict[str, dict] = OrderedDict()
    slots: OrderedDict[str, dict] = OrderedDict()

    class_pattern = r"(?m)^((?:[A-Za-z][A-Za-z0-9_-]*:[^\s]+)|(?:<[^>]+>))\s+a\s+rdfs:Class\s*;(.*?)(?=\n\s*\n|\Z)"
    for match in re.finditer(class_pattern, rdfs_text, re.S):
        subject, block = match.group(1), match.group(2)
        name = qname_to_name(subject)
        classes[name] = {"class_uri": clean_uri(subject)}
        label = english_literal(block, "rdfs:label")
        description = english_literal(block, "skos:definition") or english_literal(block, "rdfs:comment")
        if label:
            classes[name]["title"] = label
        if description:
            classes[name]["description"] = description
        superclasses = re.findall(r"rdfs:subClassOf\s+([^;,.\s\]]+)", block)
        if superclasses:
            parent_name = qname_to_name(superclasses[0])
            classes[name]["is_a"] = parent_name
            classes.setdefault(parent_name, {"class_uri": clean_uri(superclasses[0])})

    property_pattern = r"(?m)^(haDes:[^\s]+)\s+a\s+rdf:Property\s*;(.*?)(?=\n\s*\n|\Z)"
    for match in re.finditer(property_pattern, rdfs_text, re.S):
        subject, block = match.group(1), match.group(2)
        name = qname_to_name(subject)
        slots[name] = {"slot_uri": subject}
        label = english_literal(block, "rdfs:label")
        description = english_literal(block, "skos:definition")
        if label:
            slots[name]["title"] = label
        if description:
            slots[name]["description"] = description
        range_match = re.search(r"rdfs:range\s+([^;,.\n]+)", block)
        if range_match:
            slots[name]["range_hint"] = range_match.group(1).strip()

    return classes, slots


def split_top_level_shapes(shacl_text: str) -> tuple[dict[str, str], list[tuple[str, str]]]:
    starts = [
        match.start()
        for match in re.finditer(
            r"(?m)^<#([^>]+)>\s+a\s+sh:(?:NodeShape|Nodeshape|PropertyShape)\b",
            shacl_text,
        )
    ]
    starts.append(len(shacl_text))

    named_property_shapes: dict[str, str] = {}
    node_shapes: list[tuple[str, str]] = []
    for index in range(len(starts) - 1):
        block = shacl_text[starts[index] : starts[index + 1]]
        header = re.match(r"<#([^>]+)>\s+a\s+sh:([^\s;]+)", block.strip())
        if not header:
            continue
        identifier, kind = header.group(1), header.group(2).lower()
        if kind == "propertyshape":
            named_property_shapes[identifier] = block
        elif kind == "nodeshape":
            node_shapes.append((identifier, block))
    return named_property_shapes, node_shapes


def extract_inline_property_shapes(block: str) -> list[str]:
    shapes = []
    index = 0
    while True:
        start = block.find("[", index)
        if start < 0:
            break

        depth = 0
        in_string = False
        in_triple_string = False
        escaped = False
        cursor = start

        while cursor < len(block):
            if block[cursor : cursor + 3] == '"""' and not escaped:
                in_triple_string = not in_triple_string
                cursor += 3
                continue

            char = block[cursor]
            if not in_triple_string and char == '"' and not escaped:
                in_string = not in_string

            if not in_string and not in_triple_string:
                if char == "[":
                    depth += 1
                elif char == "]":
                    depth -= 1
                    if depth == 0:
                        fragment = block[start : cursor + 1]
                        if "sh:PropertyShape" in fragment:
                            shapes.append(fragment)
                        index = cursor + 1
                        break

            escaped = char == "\\" and not escaped
            if char != "\\":
                escaped = False
            cursor += 1
        else:
            break

    return shapes


def parse_shacl_in_values(block: str) -> list[str]:
    match = re.search(r"sh:in\s*\((.*?)\)\s*;", block, re.S)
    if not match:
        return []

    inner = match.group(1)
    values = re.findall(r'"((?:[^"\\]|\\.)*)"(?:\^\^\S+)?', inner)
    without_strings = re.sub(r'"(?:[^"\\]|\\.)*"(?:\^\^\S+)?', " ", inner)
    values.extend(
        token.rstrip(";,")
        for token in re.findall(r"<[^>]+>|[A-Za-z][A-Za-z0-9_-]*:[^\s()]+", without_strings)
    )
    return values


def parse_shacl_or_ranges(block: str) -> list[tuple[str, str]]:
    match = re.search(r"sh:or\s*\((.*?)\)\s*;", block, re.S)
    if not match:
        return []
    return re.findall(r"sh:(class|datatype)\s+([^\s;\]]+)", match.group(1))


def parse_property_shape(block: str, custom_type_names: dict[str, str]) -> tuple[str, dict] | None:
    path_match = re.search(r"sh:path\s+([^\s;]+)\s*;", block)
    if not path_match:
        return None

    path = path_match.group(1)
    slot_name = qname_to_name(path)
    slot = {"slot_uri": path}

    label = english_literal(block, "sh:name")
    description = english_literal(block, "sh:description") or english_literal(block, "skos:definition")
    if label:
        slot["title"] = label
    if description:
        slot["description"] = description

    min_count = re.search(r"sh:minCount\s+(\d+)\s*;", block)
    max_count = re.search(r"sh:maxCount\s+(\d+)\s*;", block)
    if min_count and int(min_count.group(1)) > 0:
        slot["required"] = True
    slot["multivalued"] = False if max_count and int(max_count.group(1)) == 1 else True

    datatype = re.search(r"sh:datatype\s+([^\s;\]]+)\s*;", block)
    class_ = re.search(r"sh:class\s+([^\s;\]]+)\s*;", block)
    or_ranges = parse_shacl_or_ranges(block)
    if datatype:
        slot["range"] = linkml_range(datatype.group(1), custom_type_names)
    elif class_:
        slot["range"] = linkml_range(class_.group(1))
    elif or_ranges:
        slot["range"] = "Any"
        slot["any_of"] = [
            linkml_range(value, custom_type_names if kind == "datatype" else None)
            for kind, value in or_ranges
        ]
    else:
        node_kind = re.search(r"sh:nodeKind\s+sh:([^\s;]+)\s*;", block)
        slot["range"] = "uriorcurie" if node_kind and "IRI" in node_kind.group(1) else "string"

    enum_values = parse_shacl_in_values(block)
    if enum_values:
        slot["range"] = f"{slot_name}_enum"
        slot["enum_values"] = enum_values

    if "sh:uniqueLang true" in block:
        slot["annotations"] = {"unique_lang": True}

    return slot_name, slot


def apply_shacl(
    shacl_text: str,
    classes: OrderedDict[str, dict],
    slots: OrderedDict[str, dict],
) -> tuple[
    OrderedDict[str, dict],
    OrderedDict[str, dict],
    OrderedDict[str, OrderedDict[str, str]],
    OrderedDict[str, str],
]:
    named_property_shapes, node_shapes = split_top_level_shapes(shacl_text)
    enums: OrderedDict[str, OrderedDict[str, str]] = OrderedDict()
    custom_type_names = custom_datatypes(shacl_text)
    class_uris = {
        qname_to_name(value): clean_uri(value)
        for value in re.findall(r"sh:(?:class|targetClass)\s+([^\s;\]]+)", shacl_text)
    }
    class_slot_usage: defaultdict[str, OrderedDict[str, dict]] = defaultdict(OrderedDict)

    for identifier, block in node_shapes:
        target_match = re.search(r"sh:targetClass\s+([^\s;]+)", block)
        if not target_match:
            continue

        class_name = qname_to_name(target_match.group(1))
        classes.setdefault(class_name, {"class_uri": clean_uri(target_match.group(1))})

        property_blocks = []
        for ref in re.findall(r"<#([^>]+)>", block):
            if ref != identifier and ref in named_property_shapes:
                property_blocks.append(named_property_shapes[ref])
        property_blocks.extend(extract_inline_property_shapes(block))

        for property_block in property_blocks:
            parsed = parse_property_shape(property_block, custom_type_names)
            if not parsed:
                continue

            slot_name, slot_data = parsed
            enum_values = slot_data.pop("enum_values", None)
            slots[slot_name] = {**slots.get(slot_name, {}), **slot_data}

            if enum_values:
                enum_name = slots[slot_name]["range"]
                enums.setdefault(enum_name, OrderedDict())
                for value in enum_values:
                    enums[enum_name][qname_to_name(value)] = value

            class_slot_usage[class_name][slot_name] = {
                key: slot_data[key]
                for key in ("required", "multivalued", "range", "any_of")
                if key in slot_data
            }

    for class_name, usage in class_slot_usage.items():
        classes.setdefault(class_name, {"class_uri": class_uris.get(class_name, class_name)})
        classes[class_name]["slots"] = list(usage.keys())
        classes[class_name]["slot_usage"] = usage

    add_external_range_stubs(classes, slots, custom_type_names, class_uris)
    return classes, slots, enums, custom_type_names


def add_external_range_stubs(
    classes: OrderedDict[str, dict],
    slots: OrderedDict[str, dict],
    custom_type_names: OrderedDict[str, str],
    class_uris: dict[str, str],
) -> None:
    scalar_ranges = {
        "string",
        "integer",
        "boolean",
        "float",
        "decimal",
        "datetime",
        "date",
        "time",
        "uriorcurie",
        "Any",
        *custom_type_names.values(),
    }
    for slot in slots.values():
        ranges = []
        if "range" in slot:
            ranges.append(slot["range"])
        ranges.extend(slot.get("any_of", []))
        for range_name in ranges:
            if range_name not in scalar_ranges and not range_name.endswith("_enum"):
                classes.setdefault(range_name, {"class_uri": class_uris.get(range_name, range_name)})


def emit_linkml(
    classes: OrderedDict[str, dict],
    slots: OrderedDict[str, dict],
    enums: OrderedDict[str, OrderedDict[str, str]],
    custom_type_names: OrderedDict[str, str],
) -> str:
    lines = [
        "id: https://data.hetarchief.be/ns/description",
        "name: description",
        "title: Data model Description",
        "description: Data model to describe the content of objects.",
        "version: 1.1.0",
        "license: https://creativecommons.org/publicdomain/zero/1.0/",
        "default_prefix: haDes",
        "default_range: string",
        "imports:",
        "  - linkml:types",
        "prefixes:",
    ]
    for prefix, uri in PREFIXES.items():
        lines.append(f"  {prefix}: {quote_yaml(uri)}")

    lines.extend(
        [
            "",
            "types:",
            "  Any:",
            "    typeof: string",
            "    description: Unconstrained value from SHACL union or node-kind constraints.",
        ]
    )
    for type_uri, type_name in custom_type_names.items():
        lines.extend([f"  {type_name}:", "    typeof: string", f"    uri: {type_uri}"])

    lines.extend(["", "classes:"])

    for class_name, class_data in classes.items():
        lines.append(f"  {class_name}:")
        if "class_uri" in class_data:
            lines.append(f"    class_uri: {class_data['class_uri']}")
        if "title" in class_data:
            lines.append(f"    title: {quote_yaml(class_data['title'])}")
        if "description" in class_data:
            lines.append(f"    description: {quote_yaml(class_data['description'])}")
        if "is_a" in class_data:
            lines.append(f"    is_a: {class_data['is_a']}")
        if class_data.get("slots"):
            lines.append("    slots:")
            for slot_name in class_data["slots"]:
                lines.append(f"      - {slot_name}")
            lines.append("    slot_usage:")
            for slot_name, usage in class_data["slot_usage"].items():
                if not usage:
                    continue
                lines.append(f"      {slot_name}:")
                emit_mapping(lines, usage, indent="        ")

    lines.extend(["", "slots:"])
    for slot_name, slot_data in slots.items():
        lines.append(f"  {slot_name}:")
        if "slot_uri" in slot_data:
            lines.append(f"    slot_uri: {slot_data['slot_uri']}")
        if "title" in slot_data:
            lines.append(f"    title: {quote_yaml(slot_data['title'])}")
        if "description" in slot_data:
            lines.append(f"    description: {quote_yaml(slot_data['description'])}")
        if "range" in slot_data:
            lines.append(f"    range: {slot_data['range']}")
        elif "range_hint" in slot_data:
            lines.append(f"    range: {linkml_range(slot_data['range_hint'])}")
        for key in ("required", "multivalued"):
            if key in slot_data:
                lines.append(f"    {key}: {str(slot_data[key]).lower()}")
        if "any_of" in slot_data:
            lines.append("    any_of:")
            for range_name in slot_data["any_of"]:
                lines.append(f"      - range: {range_name}")
        if "annotations" in slot_data:
            lines.append("    annotations:")
            emit_mapping(lines, slot_data["annotations"], indent="      ")

    if enums:
        lines.extend(["", "enums:"])
        for enum_name, values in enums.items():
            lines.append(f"  {enum_name}:")
            lines.append("    permissible_values:")
            for key, value in values.items():
                meaning = enum_meaning(value)
                lines.append(f"      {yaml_key(value if meaning is None else key)}:")
                if meaning is not None:
                    lines.append(f"        meaning: {meaning}")

    return "\n".join(lines) + "\n"


def emit_mapping(lines: list[str], mapping: dict, indent: str) -> None:
    for key, value in mapping.items():
        if key == "any_of":
            lines.append(f"{indent}any_of:")
            for range_name in value:
                lines.append(f"{indent}  - range: {range_name}")
        elif isinstance(value, bool):
            lines.append(f"{indent}{key}: {str(value).lower()}")
        else:
            lines.append(f"{indent}{key}: {value}")


def read_all(paths: list[Path]) -> str:
    return "\n\n".join(path.read_text() for path in paths)


def convert(rdfs_paths: list[Path], shacl_paths: list[Path], output_path: Path) -> None:
    rdfs_text = strip_comments(read_all(rdfs_paths))
    shacl_text = strip_comments(read_all(shacl_paths))
    classes, slots = extract_rdfs(rdfs_text)
    classes, slots, enums, custom_type_names = apply_shacl(shacl_text, classes, slots)
    output_path.write_text(emit_linkml(classes, slots, enums, custom_type_names))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert description.rdfs.ttl and description.shacl.ttl to description.linkml.yml."
    )
    base_dir = Path(__file__).resolve().parent
    parser.add_argument(
        "--rdfs",
        type=Path,
        nargs="+",
        default=[base_dir.parent / "description" / "description.rdfs.ttl"],
        help="RDFS Turtle file(s), concatenated in the order supplied.",
    )
    parser.add_argument(
        "--shacl",
        type=Path,
        nargs="+",
        default=[base_dir.parent / "description" / "description.shacl.ttl"],
        help="SHACL Turtle file(s), concatenated in the order supplied.",
    )
    parser.add_argument("--output", type=Path, default=base_dir / "description.linkml.yml")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    convert(args.rdfs, args.shacl, args.output)


if __name__ == "__main__":
    main()
