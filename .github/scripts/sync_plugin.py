#!/usr/bin/env python3
"""Download and extract the Popili Claude Code plugin from dl.cocotec.io.

Determines the target plugin directory (popili or popili-beta) based on the
version string, downloads the plugin zip, extracts it, and validates that
the plugin.json version was stamped correctly.

Prints the plugin directory name to stdout for use by the workflow.
"""

import argparse
import json
import shutil
import sys
import urllib.request
import zipfile
from pathlib import Path


def determine_channel(version: str) -> str:
  """Return the plugin directory name based on version string."""
  if "-beta." in version or "-rc." in version:
    return "popili-beta"
  return "popili"


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("--version", required=True)
  args = parser.parse_args()

  zip_path = Path("claude-code-plugin.zip")
  target = Path(determine_channel(args.version))

  url = f"https://dl.cocotec.io/popili/archive/{args.version}/claude-code-plugin.zip"
  print(f"Downloading {url}", file=sys.stderr)
  urllib.request.urlretrieve(url, zip_path)

  if target.exists():
    shutil.rmtree(target)
  target.mkdir()

  with zipfile.ZipFile(zip_path) as zf:
    zf.extractall(target)
  zip_path.unlink()

  plugin_json = target / ".claude-plugin" / "plugin.json"
  if not plugin_json.exists():
    sys.exit("ERROR: plugin.json not found in extracted zip")

  with open(plugin_json) as f:
    version = json.load(f)["version"]

  if version == "{STABLE_BUILD_SEMANTIC_VERSION}":
    sys.exit("ERROR: plugin.json still contains template variable")

  print(f"Plugin version: {version}", file=sys.stderr)
  print(target)


if __name__ == "__main__":
  main()
