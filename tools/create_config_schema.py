import json
import sys

from mashumaro.jsonschema import build_json_schema

sys.path.insert(0, "src")

from config_types import Config

json_schema = build_json_schema(Config, with_dialect_uri=True)


with open("config_schema.json", "w") as f:
    json.dump(json_schema.to_dict(), f, indent=2, ensure_ascii=False)
