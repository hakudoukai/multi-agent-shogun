# -*- coding: utf-8 -*-
"""20_shikii.py — 18閾の正本。四器の fix_threshold 呼出を ★逐語で★ 持つ。
   欄: 器key, 生器path, env名, 既定, 受け皿(out), 呼出行, th_say の吐き先
"""
SHIKII = [
    # ── scripts/inbox_watcher.sh (10) : L164-167 の for ループ経由 out==名 ──
    ("watcher", "ESCALATE_PHASE1",          "120",     "ESCALATE_PHASE1",          165),
    ("watcher", "ESCALATE_PHASE2",          "240",     "ESCALATE_PHASE2",          165),
    ("watcher", "ESCALATE_COOLDOWN",        "300",     "ESCALATE_COOLDOWN",        165),
    ("watcher", "NUDGE_COOLDOWN_SEC",       "60",      "NUDGE_COOLDOWN_SEC",       165),
    ("watcher", "NUDGE_COOLDOWN_SEC_CODEX", "300",     "NUDGE_COOLDOWN_SEC_CODEX", 165),
    ("watcher", "NUDGE_COOLDOWN_SEC_CLAUDE","60",      "NUDGE_COOLDOWN_SEC_CLAUDE",165),
    ("watcher", "ASW_PHASE",                "2",       "ASW_PHASE",                165),
    ("watcher", "APPROVAL_ALERT_COOLDOWN",  "300",     "APPROVAL_ALERT_COOLDOWN",  165),
    ("watcher", "MAX_TYPING_SKIP",          "5",       "MAX_TYPING_SKIP",          165),
    ("watcher", "INOTIFY_TIMEOUT",          "30",      "INOTIFY_TIMEOUT",          165),
    # ── scripts/watchdogs/enter_restart_common_watchdog.sh (3) ──
    ("enter",   "ER_THRESHOLD_MIN",         "10",      "THRESHOLD_MIN",            108),
    ("enter",   "ER_FIRE_CAP_COUNT",        "3",       "FIRE_CAP_COUNT",           109),
    ("enter",   "ER_FIRE_CAP_WINDOW_MIN",   "15",      "FIRE_CAP_WINDOW_MIN",      110),
    # ── scripts/agent_health_check.sh (3) ──
    ("health",  "HEALTH_CHECK_COOLDOWN_SEC","300",     "ALERT_COOLDOWN_SEC",       117),
    ("health",  "HEALTH_CHECK_TOKEN_WARN",  "200000",  "TOKEN_WARN_THRESHOLD",     342),
    ("health",  "HEALTH_CHECK_TOKEN_CRIT",  "240000",  "TOKEN_CRIT_THRESHOLD",     343),
    # ── scripts/checks/context_usage_warn.sh (2) ──
    ("context", "CONTEXT_WARN_BYTES",       "1600000", "WARN_BYTES",               64),
    ("context", "CONTEXT_DANGER_BYTES",     "2000000", "DANGER_BYTES",             65),
]
KI = {
    "watcher": dict(path="scripts/inbox_watcher.sh",
                    guard="guard_inbox_watcher.sh",
                    th_say=r"""_th_say(){ printf '%s\n' "[watcher] $*" >&2; }""",
                    sink="stderr", setflags=""),
    "enter":   dict(path="scripts/watchdogs/enter_restart_common_watchdog.sh",
                    guard="guard_enter_restart_common_watchdog.sh",
                    th_say=r"""log() { printf '[%s] %s\n' "$(date -Is)" "$*" | tee -a "$LOG"; }
_th_say(){ log "$*"; }""",
                    sink="log(tee -a $LOG)", setflags="set -uo pipefail"),
    "health":  dict(path="scripts/agent_health_check.sh",
                    guard="guard_agent_health_check.sh",
                    th_say=r"""_th_say(){ printf '%s\n' "[health_check] $*" >&2; }""",
                    sink="stderr", setflags="set -uo pipefail"),
    "context": dict(path="scripts/checks/context_usage_warn.sh",
                    guard="guard_context_usage_warn.sh",
                    th_say=r"""_th_say(){ echo "[context_warn] $*" >&2; }""",
                    sink="stderr", setflags="set -u"),
}
assert len(SHIKII) == 18, len(SHIKII)
from collections import Counter
_c = Counter(s[0] for s in SHIKII)
assert _c == {"watcher":10, "enter":3, "health":3, "context":2}, _c
assert len({s[1] for s in SHIKII}) == 18, "env名に重複"
