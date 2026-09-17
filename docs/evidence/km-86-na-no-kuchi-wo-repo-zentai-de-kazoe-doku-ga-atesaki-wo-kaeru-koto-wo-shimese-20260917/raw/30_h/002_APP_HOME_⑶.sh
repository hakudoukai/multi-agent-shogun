#!/bin/bash
# 写し器 2 ―― 口 android/gradlew:APP_HOME(合成) / 讀手 android/gradlew:101 類 ⑶
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
APP_HOME="${APP_HOME:-./}"
printf 'TARGET='; printf '%s' CLASSPATH=$APP_HOME/gradle/wrapper/gradle-wrapper.jar | od -An -v -tx1 | tr -d ' \n'; printf '\n'
