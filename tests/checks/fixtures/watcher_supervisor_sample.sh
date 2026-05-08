#!/usr/bin/env bash
# bats fixture: watcher_supervisor のうち pane_identity.sh source C parser が抽出する行のみ
# pane_identity.sh の grep -E '^\s*start_watcher_if_missing\s+"[^"]+"\s+"multiagent:agents\.[0-9]+"' 対象

start_watcher_if_missing "hideyoshi" "multiagent:agents.0"
start_watcher_if_missing "ashigaru1" "multiagent:agents.1"
start_watcher_if_missing "ashigaru2" "multiagent:agents.2"
start_watcher_if_missing "ieyasu"    "multiagent:agents.3"
