#!/usr/bin/env python3
"""Check the marketplace catalogue and that each plugin directory is complete.

Run with no arguments to check every plugin the marketplace lists. Import `validate_plugin` to check
a single directory.

Deliberately thin: manifest contents are validated before release, so this is a smoke test, not a
second implementation of the Agent Plugins spec.
"""

import json
from pathlib import Path
import sys
from typing import Any

Json = dict[str, Any]

PLUGIN_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
MCP_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json"

MARKETPLACE = Path(".claude-plugin") / "marketplace.json"

# Claude Code reads the first, every other client the second.
CLAUDE_MANIFEST = Path(".claude-plugin") / "plugin.json"
AGENT_MANIFEST = Path("plugin.json")

# Checked for presence only; a partial extraction or a stray deletion is what this catches.
EXPECTED_FILES = (
  Path(".mcp.json"),
  Path(".lsp.json"),
  Path("com.github.copilot") / "lsp.json",
)


def read_json(path: Path, problems: list[str]) -> Json | None:
  if not path.exists():
    problems.append(f"{path}: missing")
    return None
  try:
    parsed = json.loads(path.read_text())
  except json.JSONDecodeError as error:
    problems.append(f"{path}: invalid JSON: {error}")
    return None
  if not isinstance(parsed, dict):
    problems.append(f"{path}: must contain a JSON object, found {type(parsed).__name__}")
    return None
  return parsed


def validate_plugin(root: Path) -> list[str]:
  """Return every problem found in the plugin directory at `root`; empty means it looks installable."""
  problems: list[str] = []

  for relative in EXPECTED_FILES:
    if not (root / relative).is_file():
      problems.append(f"{root / relative}: missing")

  agent_manifest = read_json(root / AGENT_MANIFEST, problems)
  claude_manifest = read_json(root / CLAUDE_MANIFEST, problems)

  if agent_manifest is not None and claude_manifest is not None:
    version = agent_manifest.get("version")
    if not isinstance(version, str):
      problems.append(f"{root / AGENT_MANIFEST}: no version string")
    elif "{" in version:
      problems.append(f"{root / AGENT_MANIFEST}: unsubstituted template variable {version!r}")
    if version != claude_manifest.get("version"):
      problems.append(
        f"{root}: manifests disagree on version: {AGENT_MANIFEST} has {version!r}, "
        f"{CLAUDE_MANIFEST} has {claude_manifest.get('version')!r}"
      )

  # The field that decides whether a client outside Claude Code loads this at all.
  if agent_manifest is not None and agent_manifest.get("$schema") != PLUGIN_SCHEMA:
    problems.append(
      f"{root / AGENT_MANIFEST}: $schema is {agent_manifest.get('$schema')!r}, must be exactly "
      f"{PLUGIN_SCHEMA!r}"
    )

  portable_mcp = read_json(root / "mcp.json", problems)
  if portable_mcp is not None and portable_mcp.get("$schema") != MCP_SCHEMA:
    problems.append(f"{root}/mcp.json: $schema is {portable_mcp.get('$schema')!r}, must be exactly {MCP_SCHEMA!r}")

  return problems


def validate_marketplace() -> tuple[list[str], list[Path]]:
  """A bad entry installs nothing while every plugin directory looks fine."""
  problems: list[str] = []
  marketplace = read_json(MARKETPLACE, problems)
  if marketplace is None:
    return problems, []

  entries = marketplace.get("plugins")
  if not isinstance(entries, list):
    problems.append(f"{MARKETPLACE}: plugins must be a list")
    return problems, []

  roots: list[Path] = []
  seen: set[str] = set()
  for entry in entries:
    if not isinstance(entry, dict):
      problems.append(f"{MARKETPLACE}: every plugins entry must be an object")
      continue
    name = entry.get("name")
    if not isinstance(name, str) or not name:
      problems.append(f"{MARKETPLACE}: an entry has no name")
      continue
    if name in seen:
      problems.append(f"{MARKETPLACE}: duplicate plugin name {name!r}")
    seen.add(name)
    if not entry.get("description"):
      problems.append(f"{MARKETPLACE}: {name} has no description")

    source = entry.get("source")
    if not isinstance(source, str):
      problems.append(f"{MARKETPLACE}: {name} has no source path")
      continue
    root = Path(source)
    if not root.is_dir():
      problems.append(f"{MARKETPLACE}: {name} points at {source}, which is not a directory")
    else:
      roots.append(root)

  return problems, roots


def main() -> None:
  problems, roots = validate_marketplace()
  for root in roots:
    problems += validate_plugin(root)

  if problems:
    for problem in problems:
      print(f"FAIL: {problem}", file=sys.stderr)
    sys.exit(1)

  print(f"{len(roots)} plugin(s) validated: {', '.join(str(root) for root in roots)}")


if __name__ == "__main__":
  main()
