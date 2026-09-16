#!/bin/bash
# 33 の陰性対照 ―― pipefail 有・$? は pipe の無い行。此の file は鳴つてはならぬ。
set -o pipefail
out=$(ls /nonexistent)
rc=$?
echo "$out" | head -1
