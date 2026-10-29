#!/usr/bin/env bash
set -euo pipefail
source_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
output=${1:-/tmp/cursor-redraw-fix.so}
c++ -std=c++26 -O2 -shared -fPIC -fno-gnu-unique \
  "$source_dir/cursor-redraw-fix.cpp" -o "$output" \
  $(pkg-config --cflags --libs hyprland lua)
