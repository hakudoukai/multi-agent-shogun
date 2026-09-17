#!/usr/bin/env python3
"""CC-STOPFAILURE-RESUME (canon: claude-code-loop-stack.md 二)
StopFailure(=turnがAPIエラーで終了)で発火。goal fileが生きている席は
⑴stallマーカーを必ず書き(外部見張りの拾い先) ⑵exit2で自己再駆動を試みる(版が許せば即復旧)。
goal無き席はマーカーのみ(exit0)——非対象への注入をしない。
"""
import json, os, subprocess, sys, time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GOALS = os.path.join(REPO, "queue", "goals")


def _agent_key():
    pane = os.environ.get("TMUX_PANE")
    if pane:
        try:
            r = subprocess.run(["tmux", "display-message", "-p", "-t", pane, "#{@agent_id}"],
                               capture_output=True, text=True, timeout=5)
            aid = (r.stdout or "").strip()
            if aid:
                return aid
        except Exception:
            pass
    return None


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    key = _agent_key() or payload.get("session_id") or "unknown"
    os.makedirs(GOALS, exist_ok=True)
    marker = os.path.join(GOALS, "stall-%s.marker" % key)
    with open(marker, "a", encoding="utf-8") as f:
        f.write("%s api-error-turn-end\n" % time.strftime("%Y-%m-%dT%H:%M:%S"))
    if os.path.exists(os.path.join(GOALS, key + ".yaml")):
        time.sleep(20)  # backoff(即再試行の暴走を作らない・非2xx即時拒否は1回で上申のcanonと整合)
        print("API断でturnが落ちた。★中断箇所から再開せよ★——何をしていたかを1行書いてから続けよ(goal継続中)。同じ壁が続くならblocker4。", file=sys.stderr)
        sys.exit(2)
    sys.exit(0)


main()
