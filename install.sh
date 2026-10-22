#!/bin/sh
# Link every skill in ./skills into ~/.claude/skills.
set -e
root=$(cd "$(dirname "$0")" && pwd)
dest="$HOME/.claude/skills"
mkdir -p "$dest"
for d in "$root"/skills/*/; do
  name=$(basename "$d")
  if [ -e "$dest/$name" ]; then
    echo "skipped  $name (already in $dest)"
  else
    ln -s "${d%/}" "$dest/$name"
    echo "linked   $name -> ${d%/}"
  fi
done
