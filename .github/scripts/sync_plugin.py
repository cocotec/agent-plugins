#!/usr/bin/env python3
"""Download a released plugin version and extract it over the right channel directory.

Prints the plugin directory name to stdout for the workflow.
"""

import argparse
import json
import shutil
import sys
import urllib.request
import zipfile
from pathlib import Path

from validate import AGENT_MANIFEST, validate_plugin

ARCHIVE = "popili-agent-plugin.zip"


def determine_channel(version: str) -> str:
  """Return the plugin directory name based on version string."""
  if "-beta." in version or "-rc." in version:
    return "popili-beta"
  return "popili"


def main() -> None:
  parser = argparse.ArgumentParser()
  parser.add_argument("--version", required=True)
  args = parser.parse_args()

  zip_path = Path(ARCHIVE)
  target = Path(determine_channel(args.version))

  url = f"https://dl.cocotec.io/popili/archive/{args.version}/{ARCHIVE}"
  print(f"Downloading {url}", file=sys.stderr)
  urllib.request.urlretrieve(url, zip_path)

  if target.exists():
    shutil.rmtree(target)
  target.mkdir()

  with zipfile.ZipFile(zip_path) as archive:
    archive.extractall(target)
  zip_path.unlink()

  if problems := validate_plugin(target):
    for problem in problems:
      print(f"ERROR: {problem}", file=sys.stderr)
    sys.exit(f"{ARCHIVE} for {args.version} is not loadable; refusing to open a pull request")

  version = json.loads((target / AGENT_MANIFEST).read_text())["version"]
  print(f"Plugin version: {version}", file=sys.stderr)
  print(target)


if __name__ == "__main__":
  main()
