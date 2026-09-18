#!/bin/bash
# 陽性対照=家老が今日踏んだ形: 刻を刷らず ref を名で二度引いて「一致」と出す
a=$(git rev-parse ashigaru-mac-1/km-196-tesoto-main-29-no-census-20260918)
b=$(git rev-parse origin/main)
[ "$(git rev-parse ashigaru-mac-1/km-196-tesoto-main-29-no-census-20260918)" = "$a" ] && echo "tip 一致= yes ($a)"
