import os
import yaml
from dataclasses import fields, MISSING

from hungerlib.addons import load_yaml, flatten_nested
from serverwatcher.configclasses.global_config import GlobalConfig
from serverwatcher.configclasses.messages import MessagesConfig
from serverwatcher.configclasses.watcher import WatcherConfig


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def load_yaml_default(schema, default_path):
    """
    Load the default YAML file located inside the schema's package.
    """
    module_file = schema.__module__.replace(".", "/")
    pkg_root = os.path.dirname(os.path.dirname(__import__(schema.__module__).__file__))
    abs_default = os.path.join(pkg_root, default_path.lstrip("/"))

    if os.path.exists(abs_default):
        return flatten_nested(load_yaml(abs_default))
    return {}


def get_schema_defaults(schema):
    """
    Extract default values from dataclass fields.
    """
    defaults = {}
    for f in fields(schema):
        if f.default is not MISSING:
            defaults[f.name] = f.default
        elif f.default_factory is not MISSING:  # type: ignore
            defaults[f.name] = f.default_factory()  # type: ignore
    return defaults


def repair_value(name, value, expected_type, schema_defaults, yaml_defaults, repairs):
    """
    Determine the correct value for a field using priority:
    1. User value (if valid)
    2. Schema default
    3. YAML default
    """
    # If value is correct type and valid, keep it
    if isinstance(value, expected_type):
        if expected_type in (int, float) and value < 0:
            repairs.append(f"{name}: negative → repaired to default")
        else:
            return value

    # Try schema default
    if name in schema_defaults:
        repairs.append(f"{name}: repaired using schema default")
        return schema_defaults[name]

    # Try YAML default
    if name in yaml_defaults:
        repairs.append(f"{name}: repaired using YAML default")
        return yaml_defaults[name]

    # Fallback: empty string or zero
    repairs.append(f"{name}: no defaults found → set to safe fallback")
    if expected_type is str:
        return ""
    if expected_type in (int, float):
        return 0
    return None


def repair_config(path, default_path, schema):
    """
    Load, repair, and rewrite a config file.
    """
    print(f"\n🔧 Repairing {path}...")

    # Load user config (raw YAML)
    if os.path.exists(path):
        raw = flatten_nested(load_yaml(path))
    else:
        raw = {}

    # Load defaults
    schema_defaults = get_schema_defaults(schema)
    yaml_defaults = load_yaml_default(schema, default_path)

    repaired = {}
    repairs = []

    # Validate each field in schema
    for f in fields(schema):
        name = f.name
        expected_type = f.type
        value = raw.get(name, None)

        repaired[name] = repair_value(
            name, value, expected_type, schema_defaults, yaml_defaults, repairs
        )

    # Write repaired YAML back to disk
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        yaml.dump(repaired, f, sort_keys=False)

    if repairs:
        print("  ✔ Repairs applied:")
        for r in repairs:
            print("    -", r)
    else:
        print("  ✔ No repairs needed")

    return repairs


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def autorepair_all():
    print("=== ServerWatcher Auto‑Repair ===")

    repairs = []
    repairs += repair_config("config/global.yaml", "/defaultconfigs/global.yaml", GlobalConfig)
    repairs += repair_config("config/messages.yaml", "/defaultconfigs/messages.yaml", MessagesConfig)
    repairs += repair_config("config/watcher.yaml", "/defaultconfigs/watcher.yaml", WatcherConfig)

    if repairs:
        print("\n✅ Auto‑repair completed with fixes.")
    else:
        print("\n✅ All configs already valid — no repairs needed.")


if __name__ == "__main__":
    autorepair_all()
