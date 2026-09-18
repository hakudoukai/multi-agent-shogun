#!/bin/bash
# 陰性対照=動かぬ物だけ測る(引数の file の中身を grep するのみ・git/date/stat/wc 無し)
grep -c "★" "$1"
