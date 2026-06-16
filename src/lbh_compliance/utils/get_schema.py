from __future__ import annotations
from lbh_compliance.utils.loggers import get_logger

from typing import (
    Optional,
    List,
    Dict,
    Set,
    TypeAlias,
    TypedDict,
    Literal,
    Union,
    TypeGuard,
    Tuple,
    Generator,
)

from pathlib import Path
from dataclasses import dataclass, field
import datetime as dt
import json, ijson
import re
import uuid
import warnings

Numeric: TypeAlias = Union[int, float]
ScalarValue: TypeAlias = Union[Numeric, str, dt.datetime, bool]
NullableScalar: TypeAlias = Optional[ScalarValue]
JSONValue: TypeAlias = Union[NullableScalar, Dict[str, "JSONValue"], List["JSONValue"]]
Pathlike: TypeAlias = Union[str, Path]

STRING_LIKE_TYPES: Set[str] = {
    "string",
    "str",
    "url",
    "email",
    "uuid",
    "empty_str",
    "numeric_str",
    "html",
    "date",
    "datetime",
    "slug",
    "datetime_str",
}


TYPE_MAP: Dict[str, str] = {
    "bool": "bool",
    "boolean": "bool",
    "int": "int",
    "integer": "int",
    "float": "float",
    "numeric": "int | float",
    "number": "int | float",
    "null": "None",
    "none": "None",
    "any": "None",
}


@dataclass
class TypedDictNode:
    name: str
    children: Dict[str, "TypedDictNode"] = field(default_factory=dict)
    fields: Dict[str, str] = field(default_factory=dict)
    list_fields: Dict[str, str] = field(default_factory=dict)


class OverlyGenericSchemaWarning(Warning):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class ScalarSchema(TypedDict):
    schema_type: Literal["scalar"]
    dtypes: List[str]
    examples: List[ScalarValue]


class ObjectSchema(TypedDict):
    schema_type: Literal["object"]
    properties: Dict[str, Schema]


class ArraySchema(TypedDict):
    schema_type: Literal["array"]
    items: Schema


class MixedSchema(TypedDict):
    schema_type: Literal["mixed"]
    options: List[Schema]


class NullSchema(TypedDict):
    schema_type: Literal["null"]


class EmptyListSchema(TypedDict):
    schema_type: Literal["empty_list"]


Schema: TypeAlias = Union[
    ScalarSchema,
    ObjectSchema,
    ArraySchema,
    MixedSchema,
    NullSchema,
    EmptyListSchema,
]


def is_scalar_schema(schema: Schema) -> TypeGuard[ScalarSchema]:
    return schema.get("schema_type") == "scalar"


def is_object_schema(schema: Schema) -> TypeGuard[ObjectSchema]:
    return schema.get("schema_type") == "object"


def is_array_schema(schema: Schema) -> TypeGuard[ArraySchema]:
    return schema.get("schema_type") == "array"


def is_mixed_schema(schema: Schema) -> TypeGuard[MixedSchema]:
    return schema.get("schema_type") == "mixed"


def is_null_schema(schema: Schema) -> TypeGuard[NullSchema]:
    return schema.get("schema_type") == "null"


def is_empty_list_schema(schema: Schema) -> TypeGuard[EmptyListSchema]:
    return schema.get("schema_type") == "empty_list"


class SchemaGetter:
    def __init__(
        self,
        logging_level: Literal["debug", "info", "warn", "error", "critical"] = "info",
    ) -> None:
        self.logger = get_logger(__name__, logging_level)

        self.original_data: Optional[JSONValue] = None
        self.schema: Optional[Schema] = None
        self.paths: Optional[Dict[str, List[str]]] = None
        self.root: Optional[TypedDictNode] = None

    def read_data_from_filepath(
        self, filepath: Pathlike, sample_size: Optional[int] = None, lines: bool = True
    ) -> None:
        # JSON NewLine seperated
        self.logger.info(f"Starting getting data from {filepath}")
        if lines:
            self._read_newline_json(filepath, sample_size)

        # This is for a normal JSON file
        else:
            self._read_normal_json(filepath, sample_size)
        self.logger.info(f"Data gotten from {filepath}")

    def read_data_from_variable(
        self,
        var: Union[List[JSONValue], Dict[str, JSONValue]],
        sample_size: Optional[int] = None,
    ) -> None:
        self.logger.info("Starting getting data from variable.")

        # Usually just one record, if not, it will be recursively unpacked anyhow
        if isinstance(var, dict):
            self.original_data = var
            self.schema = self._infer_schema(var, is_root=True)
            self._validate_schema(self.schema)

        # Array of records
        elif isinstance(var, list):
            schemas: List[Schema] = []
            for i, record in enumerate(var):
                schemas.append(self._infer_schema(record, is_root=True))
                if (sample_size is not None) and (i + 1 >= sample_size):
                    break

            self.original_data = var
            self.schema = self._merge_schemas(schemas)
            self._validate_schema(self.schema)

        else:
            msg = f'Expected `from_dict` to be either List or Dict, got "{type(var)} instead.'
            self.logger.error(msg)
            raise TypeError(msg)

        self.logger.info("Data gotten from variable.")

    def collect_paths(self, schema: Schema, path: str = "$") -> Dict[str, List[str]]:
        raw = self._collect_paths_with_dtypes(schema, path)
        paths = {k: sorted(v) for k, v in raw.items()}
        self.paths = paths
        return paths

    def get_schema(self) -> Schema:
        if self.schema is not None:
            return self.schema

        msg = 'Schema is still empty, run either "read_data_from_filepath()" or "read_data_from_variable()".'
        self.logger.error(msg)
        raise AttributeError(msg)

    def generate_typed_dicts(
        self, paths: Dict[str, List[str]], root_name: str = "Vacancy"
    ) -> str:
        self.root = TypedDictNode(name=root_name)

        for path, inferred_types in paths.items():
            parts = self._parse_json_path(path)
            self._insert_path(parts, inferred_types)

        self._assign_child_names(self._get_root())
        self._refresh_child_field_types(self._get_root())

        definitions: List[str] = [
            "from __future__ import annotations",
            "",
            "from typing import TypedDict",
            "",
            "" "",
        ]

        nodes = self._collect_nodes_leaf_first(self._get_root())

        for node in nodes:
            definitions.append(self._render_typed_dict(node))
            definitions.append("")

        return "\n".join(definitions).rstrip() + "\n"

    # ---------------------
    # READ JSON FILES
    # ---------------------
    def _read_newline_json(
        self, filepath: Pathlike, sample_size: Optional[int]
    ) -> None:
        data: List[JSONValue] = []
        schemas: List[Schema] = []

        with open(filepath, "r", encoding="utf-8") as file:
            for i, line in enumerate(file):
                if line.strip() == "":
                    continue

                record: Dict[str, JSONValue] = json.loads(line)
                data.append(record)
                schemas.append(self._infer_schema(record, is_root=True))

                if (sample_size is not None) and (i + 1 >= sample_size):
                    break

        if data == []:
            msg = f"No valid JSON records founs in {filepath}"
            self.logger.error(msg)
            raise ValueError(msg)

        self.original_data = data
        self.schema = self._merge_schemas(schemas)
        self._validate_schema(self.schema)

    def _read_normal_json(self, filepath: Pathlike, sample_size: Optional[int]) -> None:
        """
        Reads a JSON file, lo

        Args:
            filepath (Pathlike): _description_
            sample_size (Optional[int]): _description_

        Raises:
            ValueError: If the JSON is empty.
            TypeError: If the JSON is invalid by not having a "{" or "[" as first character.
        """
        with open(filepath, "r", encoding="utf-8") as file:
            # Check first character
            char = file.read(1)

        # We have to reset the file, since .read() actually removes the first character
        with open(filepath, "r", encoding="utf-8") as file:
            if char == "":
                msg = f'File "{filepath}" is empty.'
                self.logger.error(msg)
                raise ValueError(msg)

            # If an object, we fully load
            elif char == "{":
                data: JSONValue = json.load(file)
                self.original_data = data
                self.schema = self._infer_schema(data, is_root=True)
                self._validate_schema(self.schema)

            # If an array of objects, we load it record by record
            elif char == "[":
                if sample_size is None:
                    records = json.load(file)

                    self.original_data = records
                    self.schema = self._infer_schema(records, is_root=True)

                else:
                    records: List[JSONValue] = []
                    schemas: List[Schema] = []
                    for i, item in enumerate(ijson.items(file, "item")):
                        records.append(item)
                        schemas.append(self._infer_schema(item, is_root=True))

                        if (sample_size is not None) and (i + 1 >= sample_size):
                            break

                    self.original_data = records
                    self.schema = self._merge_schemas(schemas)
                self._validate_schema(self.schema)

            else:
                msg = f'Expected either "[" or "{"{"}", got {char} instead.'
                self.logger.error(msg)
                raise ValueError(msg)

    # ---------------------
    # INFER AND VALIDATE SCHEMA
    # ---------------------
    def _infer_schema(self, data: JSONValue, is_root: bool = False) -> Schema:
        if data is None:
            return self._get_null_schema()

        # Unpack objects
        if isinstance(data, dict):
            return self._get_object_schema(data)

        # Unpack arrays (in a separate method)
        if isinstance(data, list):
            return self._get_list_schema(data, is_root=is_root)

        # If the data is not null, object, or array it must be a scalar
        return self._get_scalar_schema(data)

    def _validate_schema(self, schema: Schema) -> None:
        if not isinstance(schema, dict):
            msg = f"Schema is the wrong type, expected Dict, got {type(schema)} instead"
            self.logger.error(msg)
            raise ValueError(msg)

        if is_scalar_schema(schema) and len(schema.get("dtypes", [])) > 3:
            msg = f"Overly generic scalar schema: {schema}"
            self.logger.warning(msg)
            warnings.warn(OverlyGenericSchemaWarning(msg))

        elif is_object_schema(schema):
            for prop in schema["properties"].values():
                self._validate_schema(prop)

        elif is_array_schema(schema):
            self._validate_schema(schema["items"])

        elif is_mixed_schema(schema):
            for option in schema["options"]:
                self._validate_schema(option)

        elif (
            is_null_schema(schema)
            or is_empty_list_schema(schema)
            or is_scalar_schema(schema)
            or schema is None
        ):
            return None

        else:
            msg = f"Unknown schema: {schema.get('schema_type')}, {schema}"
            self.logger.error(msg)
            raise ValueError(msg)

    def _collect_paths_with_dtypes(
        self, schema: Schema, path: str = "$"
    ) -> Dict[str, Set[str]]:
        paths: Dict[str, Set[str]] = {}

        def merge(merge_path: str, merge_dtypes: Set[str]) -> None:
            nonlocal paths
            if merge_path not in paths:
                paths[merge_path] = set()
            paths[merge_path].update(merge_dtypes)
            return

        # The path can go deeper into objects
        if is_object_schema(schema):
            for key, value in schema["properties"].items():
                child_path = f"{path}.{key}"
                nested = self._collect_paths_with_dtypes(value, child_path)
                for p, dtype in nested.items():
                    merge(p, dtype)

        # Or the path goes deeper into arrays
        elif is_array_schema(schema):
            child_path = f"{path}[]"
            nested = self._collect_paths_with_dtypes(schema["items"], child_path)
            for p, dtype in nested.items():
                merge(p, dtype)

        # The path can also reach the scalars
        elif is_scalar_schema(schema):
            merge(path, set(schema["dtypes"]))

        # If the scalars are mixed we need to iterate through the options
        elif is_mixed_schema(schema):
            for option in schema["options"]:
                nested = self._collect_paths_with_dtypes(option, path)
                for p, dtype in nested.items():
                    merge(p, dtype)

        # If there is a null value, we ought to add it to the current path
        elif is_null_schema(schema):
            merge(path, {"null"})

        # The empty lists are similar to null in that their contents are near meaningless
        elif is_empty_list_schema(schema):
            merge(path, {"empty_list"})

        # Once we have reached the bottom / end, we return our paths, sorted alphabetically
        return dict(sorted(paths.items()))

    # ---------------------
    # DEFINE ALL SCHEMAS
    # ---------------------
    def _get_scalar_schema(self, scalar: ScalarValue) -> ScalarSchema:
        return {
            "schema_type": "scalar",
            "dtypes": [self._get_type_name(scalar)],
            "examples": [scalar],
        }

    def _get_object_schema(self, json_object: Dict[str, JSONValue]) -> ObjectSchema:
        return {
            "schema_type": "object",
            "properties": {
                key: self._infer_schema(value) for key, value in json_object.items()
            },
        }

    def _get_null_schema(self) -> NullSchema:
        return {"schema_type": "null"}

    def _get_empty_list_schema(self) -> EmptyListSchema:
        return {"schema_type": "empty_list"}

    def _get_list_schema(
        self, data: List[JSONValue], is_root: bool = False
    ) -> Union[ArraySchema, EmptyListSchema, Schema]:
        # If this is the root array (E.G. an array of records), we unpack the records recursively
        if is_root and all(isinstance(item, dict) for item in data):
            item_schemas = [self._infer_schema(item) for item in data]
            return self._merge_schemas(item_schemas)

        # Some data might consist only of empty lists
        if data == []:
            return self._get_empty_list_schema()

        if all(isinstance(item, list) and len(item) == 0 for item in data):
            return self._get_empty_list_schema()

        # Check if array consists of objects
        if all(isinstance(item, dict) for item in data):
            all_keys: Set[str] = set()
            item_schemas: List[Schema] = []

            # Find the schema and keys of all objects in the list
            for item in data:
                schema = self._infer_schema(item)
                item_schemas.append(schema)
                if is_object_schema(schema):
                    all_keys.update(schema["properties"].keys())
                else:
                    msg = f"Unknown SchemaType, expected Object, got '{schema['schema_type']}' instead."
                    self.logger.error(msg)
                    raise TypeError(msg)

            # Merge the properties (keys)
            unified_props = dict()
            for key in all_keys:
                key_schemas: List[Schema] = []
                for schema in item_schemas:
                    if is_object_schema(schema):
                        key_schemas.append(
                            schema["properties"].get(key, self._get_null_schema())
                        )
                    else:
                        msg = f"Unknown SchemaType, expected Object, got '{schema['schema_type']}' instead."
                        self.logger.error(msg)
                        raise TypeError(msg)
                merged = key_schemas[0]
                for ks in key_schemas[1:]:
                    merged = self._merge_two_schemas(merged, ks)
                unified_props[key] = merged
            return {
                "schema_type": "array",
                "items": {"schema_type": "object", "properties": unified_props},
            }

        # The other possibility is a mixed or scalar typing
        # We collect the types and examples, but don't recurse further
        types: Set[str] = set()
        examples: List[ScalarValue] = []

        for item in data:
            if isinstance(item, dict) or isinstance(item, list):
                types.add("mixed")
            elif item is not None:
                types.add(self._get_type_name(item))
                examples.append(item)
            else:
                types.add("null")

        items_schema: ScalarSchema = {
            "schema_type": "scalar",
            "dtypes": list(types),
            "examples": examples[:5],
        }
        result: ArraySchema = {"schema_type": "array", "items": items_schema}
        return result

    # ---------------------
    # DEFINE SCALAR TYPES
    # ---------------------
    def _get_type_name(self, value: Union[ScalarValue, None]) -> str:
        if isinstance(value, bool):
            return "bool"
        elif isinstance(value, int) or isinstance(value, float):
            return "numeric"
        elif isinstance(value, str):
            return self._classify_str(value)
        elif isinstance(value, dt.datetime):
            return "datetime"
        elif value is None:
            return "null"
        else:
            self.logger.warn(
                f'Type of {value} ({type(value)}) is unknown. Stored as "unknown" in schema.'
            )
            return "unknown"

    def _classify_str(self, value: str) -> str:
        try:
            uuid.UUID(value)
            return "uuid"
        except ValueError:
            pass

        try:
            dt.datetime.strptime(value, "%Y-%m-%d %H:%M:%S.%f UTC")
            return "datetime_str"
        except ValueError:
            pass

        try:
            dt.datetime.strptime(value, "%Y-%m-%d %H:%M:%S UTC")
            return "datetime_str"
        except ValueError:
            pass

        try:
            dt.datetime.fromisoformat(value)
            return "datetime_str"
        except ValueError:
            pass

        if value.isdigit():
            return "numeric_str"

        # Regex Source - https://stackoverflow.com/a/719543
        # Posted by Good Person, modified by community. See post 'Timeline' for change history
        # Retrieved 2026-04-08, License - CC BY-SA 3.0
        elif re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", value):
            return "email"

        elif re.match(r"^https?://[^\s/$.?#].[^\s]*$", value):
            return "url"

        elif re.match(r"^(true|false|yes|no|0|1|y|n)$", value, re.IGNORECASE):
            return "bool_str"

        elif "" == value:
            return "empty_str"

        else:
            return "string"

    # ---------------------
    # MERGE SCHEMAS TO ONE
    # ---------------------
    def _merge_schemas(self, schemas: List[Schema]) -> Schema:
        merged = schemas[0]
        for schema in schemas[1:]:
            merged = self._merge_two_schemas(merged, schema)
        return merged

    def _merge_two_schemas(self, s1: Schema, s2: Schema) -> Schema:
        # Handle empty arrays
        if is_empty_list_schema(s1) or is_empty_list_schema(s2):
            if is_empty_list_schema(s1) and is_empty_list_schema(s2):
                return self._get_empty_list_schema()
            else:
                if is_empty_list_schema(s1):
                    return s2
                else:
                    return s1

        # Merge scalar types
        if is_scalar_schema(s1) and is_scalar_schema(s2):
            combined_dtypes = set(s1.get("dtypes", [])).union(set(s2.get("dtypes", [])))
            combined_examples = (s1.get("examples", []) + (s2.get("examples", [])))[:5]
            combined_scalar_schema: ScalarSchema = {
                "schema_type": "scalar",
                "dtypes": list(combined_dtypes),
                "examples": combined_examples,
            }
            return combined_scalar_schema

        # Merge objects
        if is_object_schema(s1) and is_object_schema(s2):
            all_keys = set(s1["properties"].keys()).union(set(s2["properties"].keys()))
            merged_props = {}
            for key in all_keys:
                prop1 = s1["properties"].get(key, self._get_null_schema())
                prop2 = s2["properties"].get(key, self._get_null_schema())
                merged_props[key] = self._merge_two_schemas(prop1, prop2)
            obj_schema: ObjectSchema = {
                "schema_type": "object",
                "properties": merged_props,
            }
            return obj_schema

        # Merge arrays
        if is_array_schema(s1) and is_array_schema(s2):
            arr_schema: ArraySchema = {
                "schema_type": "array",
                "items": self._merge_two_schemas(s1["items"], s2["items"]),
            }
            return arr_schema

        # Different types
        options: List[Schema] = self._deduplicate_options([s1, s2])

        # Merge scalar schemas with identical types
        merged_options: List[Schema] = []
        seen_types: Set[Tuple] = set()

        for opt in options:
            if is_scalar_schema(opt):
                type_tuple = tuple(sorted(opt.get("dtypes", [])))

                if type_tuple in seen_types:
                    # Find the existing merged option
                    for mo in merged_options:
                        if (
                            is_scalar_schema(mo)
                            and tuple(sorted(mo.get("dtypes", []))) == type_tuple
                        ):
                            # Add maximum 5 examples
                            mo["examples"].extend(opt.get("examples", []))
                            mo["examples"] = mo["examples"][:5]
                            break
                else:
                    seen_types.add(type_tuple)
                    merged_options.append(opt)
            else:
                merged_options.append(opt)

        mixed_schema: MixedSchema = {"schema_type": "mixed", "options": merged_options}
        return mixed_schema

    def _deduplicate_options(self, options: List[Schema]) -> List[Schema]:
        seen: Set[str] = set()
        unique: List[Schema] = []

        def flatten_mixed(option: Schema) -> Generator[Schema]:
            if is_mixed_schema(option):
                nested_options = option.get("options", [])
                for nested_option in nested_options:
                    for flattened_option in flatten_mixed(nested_option):
                        yield flattened_option
            else:
                yield option

        flattened: List[Schema] = []
        for opt in options:
            flattened.extend(list(flatten_mixed(opt)))

        # Group by type
        value_groups: Dict[Tuple, List[Schema]] = {}
        object_group: List[Schema] = []
        other: List[Schema] = []

        for opt in flattened:
            t = opt.get("schema_type")

            if t == "scalar":
                key = tuple(sorted(opt.get("dtypes", [])))
                value_groups.setdefault(key, []).append(opt)

            elif t == "object":
                object_group.append(opt)

            else:
                other.append(opt)

        # Merge scalar schemas
        for key, group in value_groups.items():
            merged: ScalarSchema = {
                "schema_type": "scalar",
                "dtypes": list(key),
                "examples": [],
            }
            for g in group:
                merged["examples"].extend(g.get("examples", []))
            merged["examples"] = merged["examples"][:5]
            unique.append(merged)

        # Merge object schemas
        if object_group != []:
            merged_object = object_group[0]
            for obj in object_group[1:]:
                merged_object = self._merge_two_schemas(merged_object, obj)
            unique.append(merged_object)

        # Keep the other types as is
        for opt in other:
            key = json.dumps(opt, sort_keys=True)
            if key not in seen:
                seen.add(key)
                unique.append(opt)
        return unique[:5]

    # ---------------------
    # GENERATE TYPED DICTS
    # ---------------------
    def _get_root(self) -> TypedDictNode:
        if self.root is not None:
            return self.root

        msg = 'Root is still empty, this helper function is only used in "generate_typed_dict()".'
        self.logger.error(msg)
        raise AttributeError(msg)

    def _parse_json_path(self, path: str) -> List[Tuple[str, bool]]:
        path = path.removeprefix("$.")
        raw_parts = path.split(".")

        parts: List[Tuple[str, bool]] = []

        for raw_part in raw_parts:
            is_list = raw_part.endswith("[]")
            key = raw_part.removesuffix("[]")
            parts.append((key, is_list))

        return parts

    def _insert_path(
        self, parts: List[Tuple[str, bool]], inferred_types: List[str]
    ) -> None:
        current = self._get_root()

        for index, (key, is_list) in enumerate(parts):
            is_leaf: bool = index == len(parts) - 1

            if is_leaf:
                value_type = self._to_python_type(inferred_types)

                if is_list:
                    current.fields[key] = f"List[{value_type}]"
                else:
                    current.fields[key] = value_type

                return None

            if is_list:
                child_key = f"{key}[]"
                if child_key not in current.children:
                    current.children[child_key] = TypedDictNode(name="")
                current.fields[key] = (
                    f"List[{current.children[child_key].name or 'PLACEHOLDER'}]"
                )
                current = current.children[child_key]
            else:
                if key not in current.children:
                    current.children[key] = TypedDictNode(name="")
                current.fields[key] = current.children[key].name or "PLACEHOLDER"
                current = current.children[key]

    def _assign_child_names(self, node: TypedDictNode) -> None:
        for child_key, child in node.children.items():
            clean_key = child_key.removesuffix("[]")
            suffix = "Item" if child_key.endswith("[]") else ""
            child.name = f"{node.name}{self._to_pascal_case(clean_key)}{suffix}"
            self._assign_child_names(child)

    def _refresh_child_field_types(self, node: TypedDictNode) -> None:
        for child_key, child in node.children.items():
            field_name = child_key.removesuffix("[]")

            if child_key.endswith("[]"):
                node.fields[field_name] = f"List[{child.name}]"
            else:
                node.fields[field_name] = child.name

            self._refresh_child_field_types(child)

    def _collect_nodes_leaf_first(self, node: TypedDictNode) -> List[TypedDictNode]:
        nodes: List[TypedDictNode] = []

        for child in node.children.values():
            nodes.extend(self._collect_nodes_leaf_first(child))

        nodes.append(node)
        return nodes

    def _render_typed_dict(self, node: TypedDictNode) -> str:
        lines: List[str] = [f"{node.name} = TypedDict(", f"    {node.name!r},", "    {"]

        if not node.fields:
            lines.extend(["    },", "    total=False,", ")"])
            return "\n".join(lines)

        for field_name, field_type in sorted(node.fields.items()):
            resolved_type = self._resolve_placeholders(node, field_type)
            lines.append(f"        {field_name!r}: {resolved_type},")

        lines.extend(["    },", "    total=False,", ")"])
        return "\n".join(lines)

    def _resolve_placeholders(self, node: TypedDictNode, field_type: str) -> str:
        if "PLACEHOLDER" not in field_type:
            return field_type

        for child_key, child in node.children.items():
            if child_key.endswith("[]"):
                field_type = field_type.replace(
                    "List[PLACEHOLDER]", f"List[{child.name}]"
                )
            else:
                field_type = field_type.replace("PLACEHOLDER", child.name, 1)

        return field_type

    def _to_python_type(self, inferred_types: List[str]) -> str:
        python_types: Set[str] = set()

        for inferred_type in inferred_types:
            normalised = inferred_type.strip().lower()

            if normalised in STRING_LIKE_TYPES:
                python_types.add("str")
            elif normalised in TYPE_MAP.keys():
                python_types.add(TYPE_MAP[normalised])
            else:
                python_types.add("str")

        if not python_types:
            return "None"

        if "None" in python_types:
            return "None"

        return " | ".join(sorted(python_types, key=self._type_sort_key))

    def _type_sort_key(self, type_name: str) -> Tuple[int, str]:
        order = {
            "None": 99,
            "bool": 1,
            "int": 2,
            "float": 3,
            "int | float": 4,
            "str": 5,
        }
        return order.get(type_name, 50), type_name

    def _to_pascal_case(self, value: str) -> str:
        return "".join(
            part.capitalize() for part in re.split(r"[_\-\s]+", value) if part
        )
