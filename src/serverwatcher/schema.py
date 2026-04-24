from typing import Dict, Any, List

from hungerlib.addons import validate_required_keys


def validate_config_schema(raw: Dict[str, Any]) -> list[str]:
    errors: List[str] = []

    # top-level sections
    errors += validate_required_keys(raw, ["panel", "origin", "server", "watcher"], "root")

    panel = raw.get("panel", {})
    origin = raw.get("origin", {})
    server = raw.get("server", {})
    watcher = raw.get("watcher", {})

    errors += validate_required_keys(panel, ["name", "url", "api_key"], "panel")
    errors += validate_required_keys(origin, ["server_id"], "origin")
    errors += validate_required_keys(
        server,
        ["name", "server_id", "domain", "port", "rcon_port", "rcon_password", "tps_command"],
        "server",
    )

    # simple sanity checks (optional but nice)
    if "port" in server and not isinstance(server["port"], int):
        errors.append("[server] 'port' must be an integer")
    if "rcon_port" in server and not isinstance(server["rcon_port"], int):
        errors.append("[server] 'rcon_port' must be an integer")

    # watcher numeric sanity
    if "ram_threshold" in watcher and watcher["ram_threshold"] <= 0:
        errors.append("[watcher] 'ram_threshold' must be > 0")
    if "cpu_threshold" in watcher and watcher["cpu_threshold"] <= 0:
        errors.append("[watcher] 'cpu_threshold' must be > 0")

    return errors


def validate_messages_schema(raw: Dict[str, Any]) -> list[str]:
    # you can make this as strict as you want; for now just ensure prefix exists
    errors: List[str] = []
    if "prefix" not in raw:
        errors.append("[messages] Missing required key: 'prefix'")
    return errors
