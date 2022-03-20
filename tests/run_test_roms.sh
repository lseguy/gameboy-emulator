#!/usr/bin/env bash

TESTS_DIR=$(dirname $0)
ROMS_DIR="$TESTS_DIR/../roms/blargg"
MAIN_DIR="$TESTS_DIR/.."

function run_test() {
  echo "Running $(basename $1)..."

  PYTHONUNBUFFERED=1 python3 "$MAIN_DIR/main.py" "$1" | {
    while IFS= read -r line; do
      echo $line

      if [[ $line =~ Passed ]]; then
        pkill -P $$
        return 0
      elif [[ $line =~ Failed ]]; then
        pkill -P $$
        return 1
      fi
    done
  }
}

for rom_file in "$ROMS_DIR"/*; do
  run_test "$rom_file" || exit $?
done
