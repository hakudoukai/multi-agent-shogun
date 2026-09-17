#!/usr/bin/env python3
"""CC-GOAL-HOOK (canon: claude-code-loop-stack.md 一・2026-08-30 総監督canary実装)
Stop hookとして走る。席のgoal file(queue/goals/<agent_id|session_id>.yaml)が生きている限り
exit 2で停止を差し戻し続行させる(公式仕様: exit2="Prevents Claude from stopping")。
安全: goal file無し=即exit0(非対象sessionへ影響ゼロ)/max_turns背止め/blocked:脱出/done・verify緑で解除。
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


def _load(path):
    d = {}
    try:
        for ln in open(path, encoding="utf-8"):
            if ":" in ln and not ln.lstrip().startswith("#"):
                k, v = ln.split(":", 1)
                d[k.strip()] = v.strip()
    except Exception:
        return None
    return d


# 2026-09-10 家老mac ESCALATE 299390: _load は値を悉く文字列にするため verify: false が真値となり
#   shell で `false` を走らせ rc=1 が永久（なし=127）。「検証無し」を表す値は verify 無しと解する（fail-loud に stderr へ1行）。
NO_VERIFY = ("", "false", "no", "none", "null", "nil", "off", "0", "~", "なし", "無し", "無", "検証なし", "検証無し")


def _verify_cmd(raw):
    v = (raw or "").strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in ("'", '"'):
        v = v[1:-1].strip()
    if v.lower() in NO_VERIFY:
        if raw is not None and (raw or "").strip():
            print("verify=%r は『検証無し』と解した（shell で実行しない）" % raw.strip(), file=sys.stderr)
        return ""
    return v


def _save(path, d):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        for k, v in d.items():
            f.write("%s: %s\n" % (k, v))
    os.replace(tmp, path)


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    sid = payload.get("session_id") or ""
    key = _agent_key() or sid
    if not key:
        sys.exit(0)
    path = os.path.join(GOALS, key + ".yaml")
    if not os.path.exists(path):
        sys.exit(0)
    g = _load(path)
    if g is None:
        sys.exit(0)  # 読めないgoalで艦隊を止めない(fail-open・註はlogへ)
    os.makedirs(os.path.join(GOALS, "done"), exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    # 脱出1: blocked宣言(stop_when=blocker4)
    if g.get("blocked"):
        os.replace(path, os.path.join(GOALS, "done", "%s.blocked-%s.yaml" % (key, stamp)))
        print("goal解除(blocked): %s ―― blocker4を上げた事を確認した" % g.get("blocked", "")[:80], file=sys.stderr)
        sys.exit(0)
    # 脱出2: done宣言
    if (g.get("done") or "").lower() in ("true", "yes", "1"):
        # quality gate: verifyが在れば緑を要求(赤ならdoneを差し戻す=公式goalsのgate思想)
        v = _verify_cmd(g.get("verify"))
        if v:
            try:
                r = subprocess.run(v, shell=True, cwd=REPO, capture_output=True, text=True, timeout=300)
            except Exception as e:
                r = None
            if r is None or r.returncode != 0:
                g["done"] = "false"
                g["turns_used"] = str(int(g.get("turns_used") or 0) + 1)
                _save(path, g)
                tail = (r.stdout + r.stderr)[-400:] if r else "(verify実行不能)"
                print("↻ goal継続: done宣言されたが★verifyが赤★ ―― 直してから done を立て直せ。verify末尾: %s" % tail, file=sys.stderr)
                sys.exit(2)
        os.replace(path, os.path.join(GOALS, "done", "%s.done-%s.yaml" % (key, stamp)))
        print("goal達成を確認(verify緑)。停止を許可する。", file=sys.stderr)
        sys.exit(0)
    # turn予算
    used = int(g.get("turns_used") or 0) + 1
    mx = int(g.get("max_turns") or 20)
    g["turns_used"] = str(used)
    if used > mx:
        os.replace(path, path + ".paused")
        print("⏸ goal一時停止(%d/%d turns)。検分の上 .paused を外して再開せよ。" % (used - 1, mx), file=sys.stderr)
        sys.exit(0)
    _save(path, g)
    print("↻ goal継続(%d/%d): %s ―― 次の一手を実行し成果物path+SHAを出せ。達成したらgoal fileへ done: true を書け(verifyが在れば緑必須)。詰まったらblocker4を上げ goal fileへ blocked: <理由> を書いてから停止してよい。" % (used, mx, g.get("outcome", "")[:200]), file=sys.stderr)
    sys.exit(2)


main()
