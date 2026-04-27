import os

def load_or_default(path: str, default_path: str, schema):

    abs_path = os.path.join(BASE_DIR, path)
    abs_default = os.path.join(PACKAGE_DIR, default_path)

    if not os.path.exists(abs_path):
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        with open(abs_default, "r") as src, open(abs_path, "w") as dst:
            dst.write(src.read())

    raw = load_yaml(abs_path)
    raw = flatten_nested(raw)
    return map_to_dataclass(raw, schema)