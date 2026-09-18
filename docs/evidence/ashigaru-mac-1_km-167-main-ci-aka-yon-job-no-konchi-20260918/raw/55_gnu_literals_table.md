| 類 | file | 行 | 字面 | CI での扱ひ |
|---|---|---|---|---|
| md5sum | tests/unit/test_build_system.bats | 281 | `checksums_first=$(find "$OUTPUT_DIR" -name "*.md" -type f -exec md5sum` | ★直した★ shasum -a 256(BSD/GNU 両方) |
| md5sum | tests/unit/test_build_system.bats | 286 | `checksums_second=$(find "$OUTPUT_DIR" -name "*.md" -type f -exec md5su` | ★直した★ shasum -a 256(BSD/GNU 両方) |
| other | tests/test_karo_second_send_iincho.bats | 216 | `for _ in $(seq 1 20); do` | seq は BSD にも在る(依存なし) |
| other | tests/unit/test_safe_nudge.bats | 103 | `for _ in $(seq 1 30); do` | seq は BSD にも在る(依存なし) |
| timeout | tests/agent_selfwatch.bats | 62 | `timeout() { shift; "$@"; }` | stub 定義(GNU 依存なし) |
| timeout | tests/agent_selfwatch.bats | 65 | `export -f tmux timeout sleep pgrep` | stub 定義(GNU 依存なし) |
| timeout | tests/agent_selfwatch.bats | 82 | `@test "TC-FR-002: inotify + timeout fallback is configured" {` | GNU timeout 要・CI は ubuntu 既設/macOS coreutils(test.yml L33-37) |
| timeout | tests/test_karo_second_send_iincho.bats | 139 | `timeout 10 bash "$HELPER_SCRIPT" --live -- "T-207 content"` | GNU timeout 要・CI は ubuntu 既設/macOS coreutils(test.yml L33-37) |
| timeout | tests/test_karo_second_send_iincho.bats | 232 | `timeout 10 bash "$HELPER_SCRIPT" --live -- "T-209 content"` | GNU timeout 要・CI は ubuntu 既設/macOS coreutils(test.yml L33-37) |
| timeout | tests/unit/test_idle_flag.bats | 91 | `timeout() { shift; "\$@"; }` | stub 定義(GNU 依存なし) |
| timeout | tests/unit/test_idle_flag.bats | 94 | `export -f tmux timeout pgrep sleep` | stub 定義(GNU 依存なし) |
| timeout | tests/unit/test_ntfy_ack.bats | 107 | `timeout 3 bash "$MOCK_PROJECT/ntfy_listener_test.sh" 2>/dev/null \|\| ` | GNU timeout 要・CI は ubuntu 既設/macOS coreutils(test.yml L33-37) |
| timeout | tests/unit/test_send_wakeup.bats | 138 | `timeout() { shift; "\$@"; }` | stub 定義(GNU 依存なし) |
| timeout | tests/unit/test_send_wakeup.bats | 141 | `export -f tmux timeout pgrep sleep` | stub 定義(GNU 依存なし) |
| timeout | tests/unit/test_send_wakeup.bats | 502 | `timeout 2 tmux send-keys -t "$PANE_TARGET" C-u 2>/dev/null` | GNU timeout 要・CI は ubuntu 既設/macOS coreutils(test.yml L33-37) |
| timeout | tests/unit/test_send_wakeup.bats | 525 | `timeout 2 tmux send-keys -t "$PANE_TARGET" C-u 2>/dev/null` | GNU timeout 要・CI は ubuntu 既設/macOS coreutils(test.yml L33-37) |
| timeout | tests/unit/test_watcher_rc6_integration.bats | 11 | `#   ∴ watcher は initial sweep (1 巡) + inotify 2 回 (2,3 巡) を回つて自然終了する。t` | GNU timeout 要・CI は ubuntu 既設/macOS coreutils(test.yml L33-37) |
| timeout | tests/unit/test_watcher_rc6_integration.bats | 74 | `timeout 30 bash "$SB/scripts/message_delivery_v2/watcher.sh" test_agen` | GNU timeout 要・CI は ubuntu 既設/macOS coreutils(test.yml L33-37) |
