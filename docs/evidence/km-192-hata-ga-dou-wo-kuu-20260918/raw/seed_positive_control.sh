#!/usr/bin/env bash
~/bin/sb-ashigaru-mac-1 write letter "正しい胴" --to gunshi-mac --parent-seq 1
~/bin/sb-ashigaru-mac-1 write letter --to gunshi-mac "旗が前の胴" --parent-seq 1
sb read seq 123
bash scripts/inbox_write.sh karo-mac "胴" report ashigaru-mac-1
sb-karo-mac write letter --to iincho "胴" --parent-seq 333753
