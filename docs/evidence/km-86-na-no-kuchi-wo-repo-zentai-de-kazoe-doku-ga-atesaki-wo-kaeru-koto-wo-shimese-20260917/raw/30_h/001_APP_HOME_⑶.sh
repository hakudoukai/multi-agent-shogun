#!/bin/bash
# 写し器 1 ―― 口 android/gradlew:APP_HOME(合成) / 讀手 android/gradlew:67 類 ⑶
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
APP_HOME="${APP_HOME:-./}"
printf 'TARGET='; printf '%s' "${APP_HOME:-./}" | od -An -v -tx1 | tr -d ' \n'; printf '\n'
