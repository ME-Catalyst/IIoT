"""Utility script to validate Node-RED flows against a lightweight schema.

The script intentionally avoids third-party dependencies so it can run in
CI environments without additional setup.  The validation rules mirror the
"tests/schemas/node_red_flow.schema.json" definition by enforcing that
flow exports are arrays of objects with "id" and "type" fields.  Additional
checks ensure the presence of at least one workspace ("tab") and that node
references target known tabs.
"""
from __future__ import annotations

import json
import pathlib
import sys
from typing import Iterable, List, Set

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC_FLOW_DIR = ROOT / "src" / "flows"
SCHEMA_PATH = ROOT / "tests" / "schemas" / "node_red_flow.schema.json"


class ValidationError(RuntimeError):
    """Raised when a flow export violates the validation contract."""


def _load_flow(path: pathlib.Path) -> List[dict]:
    data = json.loads(path.read_text())
    if not isinstance(data, list):
        raise ValidationError(f"{path} is not a list of nodes")
    for idx, node in enumerate(data):
        if not isinstance(node, dict):
            raise ValidationError(f"{path} entry {idx} is not an object")
        for field in ("id", "type"):
            if field not in node or not isinstance(node[field], str) or not node[field]:
                raise ValidationError(f"{path} entry {idx} missing string field '{field}'")
    return data


def _validate_tabs(flow: Iterable[dict], path: pathlib.Path) -> None:
    tabs: Set[str] = {node["id"] for node in flow if node["type"] == "tab"}
    if not tabs:
        raise ValidationError(f"{path} does not define a workspace tab")

    containers: Set[str] = tabs | {
        node["id"] for node in flow if node.get("type") == "subflow"
    }

    for node in flow:
        tab_id = node.get("z")
        if tab_id and tab_id not in containers:
            raise ValidationError(
                f"{path} node '{node['id']}' targets unknown tab '{tab_id}'"
            )


def _flow_files() -> Iterable[pathlib.Path]:
    if not SRC_FLOW_DIR.exists():
        return []
    return SRC_FLOW_DIR.rglob("*.json")


def main(argv: List[str]) -> int:
    flow_paths = sorted(_flow_files())
    if not flow_paths:
        print("No flow exports found under src/flows; nothing to validate.")
        return 0

    failures = []
    for path in flow_paths:
        try:
            flow = _load_flow(path)
            _validate_tabs(flow, path)
        except ValidationError as exc:
            failures.append(str(exc))

    if failures:
        print("Flow validation failed:")
        for failure in failures:
            print(f" - {failure}")
        return 1

    print(f"Validated {len(flow_paths)} flow export(s) against {SCHEMA_PATH.name}.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
