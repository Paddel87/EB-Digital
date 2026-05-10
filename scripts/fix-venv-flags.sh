#!/usr/bin/env bash
# Removes the macOS BSD UF_HIDDEN file flag from the project venv tree.
#
# Background: when the project lives inside a hidden parent directory
# (e.g. a Claude Code worktree under .claude/worktrees/), the very first
# `uv sync` produces a .venv whose files inherit the UF_HIDDEN flag.
# Python 3.13's site.py explicitly skips .pth files that carry this flag
# ("Skipping hidden .pth file:"), which breaks editable installs and shows
# up as `ModuleNotFoundError: No module named 'eb_digital'`. Subsequent
# sync runs into the same venv write non-hidden files, so this script
# only needs to run once per fresh venv.
#
# See: docs/blockers.md → Blocker #001 (resolved 2026-05-10).

set -euo pipefail

VENV_DIR="${1:-.venv}"

if [[ "$(uname)" != "Darwin" ]]; then
  echo "fix-venv-flags: not macOS, nothing to do."
  exit 0
fi

if [[ ! -d "$VENV_DIR" ]]; then
  echo "fix-venv-flags: '$VENV_DIR' not found. Run 'uv sync' first." >&2
  exit 1
fi

chflags -R nohidden "$VENV_DIR"
echo "fix-venv-flags: cleared UF_HIDDEN on '$VENV_DIR' (recursive)."
