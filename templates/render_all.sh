#!/usr/bin/env bash
set -euo pipefail

if ! command -v vhs >/dev/null 2>&1; then
  echo "Error: vhs is not installed or not on PATH." >&2
  exit 1
fi

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT_DIR="${1:-$PROJECT_ROOT/recordings/generated}"

mkdir -p "$OUTPUT_DIR"

echo "Rendering templates to: $OUTPUT_DIR"

for template in "$PROJECT_ROOT"/templates/*.tape; do
  name="$(basename "$template")"
  base="${name%.tape}"
  tmp="$(mktemp)"
  sed \
    -e "s|{{PROJECT_ROOT}}|$PROJECT_ROOT|g" \
    "$template" > "$tmp"

  echo ":: Running $name"
  if ! vhs -o "$OUTPUT_DIR/${base}.gif" "$tmp"; then
    echo "!! Failed to render $name" >&2
  fi
  rm -f "$tmp"
done

echo "Done."
