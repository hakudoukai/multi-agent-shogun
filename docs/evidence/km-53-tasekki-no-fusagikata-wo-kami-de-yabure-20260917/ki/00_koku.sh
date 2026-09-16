#!/bin/bash
# usage: 00_koku.sh <out>  ―― 刻を一行で刷る(起点の記録)
set -u
out="${1:?usage: 00_koku.sh <out>}"
{ date '+%Y-%m-%dT%H:%M:%S%z'; echo "pwd=$(pwd)"; echo "branch=$(git branch --show-current)"; echo "head=$(git rev-parse --short HEAD)"; } > "$out"
echo "rc=0"
