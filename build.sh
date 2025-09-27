#!/usr/bin/env bash
DIR="$(dirname "$0")"
cd "$DIR"
uvx hatch clean;
fd -e py -x autoflake {};
fd -e py -x pyupgrade --py311-plus {};
fd -e py -x ruff check --output-format=github --fix --unsafe-fixes {};
fd -e py -x ruff format --respect-gitignore --target-version py311 {};
uvx hatch fmt;

EXCLUDE="*.svg,.specstory,ref,testdata,*.lock,llms.txt"
if [[ -n "$1" ]]; then
  EXCLUDE="$EXCLUDE,$1"
fi

uvx codetoprompt --compress --output "./llms.txt" --respect-gitignore --cxml --exclude "$EXCLUDE" "."

gitnextver .;
uvx hatch build;
uv publish;
uv pip install --system --upgrade -e .
