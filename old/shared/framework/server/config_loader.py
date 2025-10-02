import json, os
from jsonschema import validate

def load_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_validated(data_path: str, schema_path: str):
    data, schema = load_json(data_path), load_json(schema_path)
    validate(instance=data, schema=schema)
    return data

BASE = os.getenv("CONFIG_BASE", os.path.join(os.path.dirname(__file__), "..", "configs"))

def load_principles():
    return load_validated(os.path.join(BASE, "principles.example.json"),
                          os.path.join(BASE, "principles.schema.json"))

def load_decision_tree():
    return load_validated(os.path.join(BASE, "decision_tree.example.json"),
                          os.path.join(BASE, "decision_tree.schema.json"))

def load_adapters():
    return load_validated(os.path.join(BASE, "adapters.example.json"),
                          os.path.join(BASE, "adapters.schema.json"))
