#!/usr/bin/env python3
"""板 a6c0f720 ⑷: hermes2 reverse watcher の陽性・陰性の両対照。

DB と pane には触らない。sb_curl・sudo・tmux は偽物に差し替へ、watcher を写した
一時 dir で H2_MAX_POLLS 回だけ回す。

  ⑴ 同じ組は再び起こさない / 増えた・状態が変はつた時は起こす / 減つただけなら起こさない
  ⑵ 照会に to_pc・target_agent・topic=cross_pc_inbox_hermes2 の三つが入る
  ⑶ 門に拒まれた ACK は帳へ id ごとに一度だけ書き、PATCH を繰り返さない。成功時は帳に書かない
"""
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
WATCHER = pathlib.Path(os.environ.get("H2_TEST_WATCHER", ROOT / "shim/hakudokai/hakudokai_hermes2_reverse_watcher.sh"))
GUARD = pathlib.Path(os.environ.get("H2_TEST_GUARD", ROOT / "shim/hakudokai/lib/hermes2_reverse_guard.sh"))

FAILS = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + (f"  [{detail}]" if detail and not ok else ""))
    if not ok:
        FAILS.append(name)


def row(i, seq, priority="normal", rr=True, mt="request", **extra):
    r = {"id": f"00000000-0000-4000-8000-{i:012d}", "seq": seq, "from_pc": "third_pc", "to_pc": "third_pc",
         "created_at": "2026-10-02T00:00:00Z", "requires_response": rr, "message_type": mt,
         "priority": priority, "topic": "cross_pc_inbox_hermes2", "context_data": {"target_agent": "hermes2"}}
    r.update(extra)
    return r


# ---------- 単体: guard lib ----------

def bash(script, env=None):
    e = dict(os.environ)
    e.update(env or {})
    return subprocess.run(["bash", "-c", f'source "{GUARD}"; {script}'], capture_output=True, text=True, env=e)


def wake_select(rows, state):
    out = bash("h2_wake_select", {"H2_ROWS_JSON": json.dumps(rows), "H2_WOKEN_STATE": str(state)}).stdout.splitlines()
    return out[0], (out[1].split() if len(out) > 1 else [])


def wake_record(rows, state, ids):
    return bash("h2_wake_record", {"H2_ROWS_JSON": json.dumps(rows), "H2_WOKEN_STATE": str(state),
                                   "H2_WAKE_IDS": " ".join(ids)}).returncode


def unit_tests(tmp):
    st = tmp / "woken.state"
    a, b = row(1, 101), row(2, 102)
    v, ids = wake_select([a], st)
    check("unit⑴ 陽性: 初回は起こす", v == "wake" and ids == [a["id"]], f"{v} {ids}")
    wake_record([a], st, [a["id"]])
    v, ids = wake_select([a], st)
    check("unit⑴ 陰性: 同じ組は起こさない", v == "quiet" and ids == [], f"{v} {ids}")
    v, ids = wake_select([a, b], st)
    check("unit⑴ 陽性: 新しい seq が加はれば其の行だけ起こす", v == "wake" and ids == [b["id"]], f"{v} {ids}")
    v, ids = wake_select([dict(a, priority="high")], st)
    check("unit⑴ 陽性: 同じ seq でも状態(priority)が変はれば起こす", v == "wake" and ids == [a["id"]], f"{v} {ids}")
    v, ids = wake_select([dict(a, requires_response=False)], st)
    check("unit⑴ 陽性: requires_response が変はれば起こす", v == "wake", f"{v} {ids}")
    wake_record([a, b], st, [a["id"], b["id"]])
    v, ids = wake_select([b], st)
    check("unit⑴ 陰性: 減つただけなら起こさない", v == "quiet", f"{v} {ids}")
    v, ids = wake_select([], st)
    check("unit⑴ 陰性: 空なら起こさない", v == "quiet", f"{v} {ids}")
    wake_record([a, b], st, [a["id"], b["id"]])
    check("unit⑴ 記録は重ならない", st.read_text().count(a["id"]) == 1, st.read_text())
    st2 = tmp / "keep.state"
    rows = [row(10 + i, 200 + i) for i in range(5)]
    bash("h2_wake_record", {"H2_ROWS_JSON": json.dumps(rows), "H2_WOKEN_STATE": str(st2),
                            "H2_WAKE_IDS": " ".join(r["id"] for r in rows), "H2_WOKEN_KEEP": "3"})
    check("unit⑴ 記録は末尾 H2_WOKEN_KEEP 行に保つ", len(st2.read_text().splitlines()) == 3, st2.read_text())

    led = tmp / "rej.jsonl"
    gate = tmp / "gate.json"
    gate.write_text('{"code":"P0001","details":null,"hint":null,"message":"HUMAN_ACK_ONLY: acknowledged_by=system は機械名義ゆえ拒否"}')
    other = tmp / "other.json"
    other.write_text('{"code":"PGRST301","message":"JWT expired"}')

    def rec(i, http, body, kind="machine"):
        return bash(f'h2_ack_reject_record "{led}" "{i}" "7" "{http}" "{body}" "{kind}"').returncode

    check("unit⑶ 陽性: 門の拒否(400/P0001)は rc=0 で帳へ書く", rec("id-a", "400", gate) == 0)
    lines = led.read_text().splitlines()
    e = json.loads(lines[0]) if lines else {}
    check("unit⑶ 帳に id・seq・http・code・kind・本文の頭が在る",
          e.get("id") == "id-a" and e.get("seq") == "7" and e.get("http") == "400" and e.get("code") == "P0001"
          and e.get("kind") == "machine" and "HUMAN_ACK_ONLY" in e.get("message_head", ""), str(e))
    check("unit⑶ 陰性: 同じ id は二度書かない(rc=3)", rec("id-a", "400", gate) == 3 and len(led.read_text().splitlines()) == 1)
    check("unit⑶ 陰性: 門以外の失敗(401)は帳に書かない(rc=1)", rec("id-b", "401", other) == 1 and len(led.read_text().splitlines()) == 1)
    check("unit⑶ 陰性: 400 でも門の拒否でなければ帳に書かない", rec("id-c", "400", other) == 1)
    check("unit⑶ h2_ack_gate_rejected 陽性", bash(f'h2_ack_gate_rejected "{led}" id-a').returncode == 0)
    check("unit⑶ h2_ack_gate_rejected 陰性", bash(f'h2_ack_gate_rejected "{led}" id-b').returncode != 0)


# ---------- 結合: 偽の sb_curl・sudo・tmux で watcher を回す ----------

FAKE_SB = r'''
sb_curl() {
  local out="" patch=0 url=""
  while [ $# -gt 0 ]; do
    case "$1" in
      -o) out="$2"; shift 2 ;;
      -X) [ "$2" = PATCH ] && patch=1; shift 2 ;;
      -w|-H|-d) shift 2 ;;
      -*) shift ;;
      *) url="$1"; shift ;;
    esac
  done
  if [ "$patch" = 1 ]; then
    echo "$url" >>"$FAKE_DIR/patch.log"
    if [ "${FAKE_ACK:-reject}" = ok ]; then : >"$out"; printf 204
    else printf '%s' '{"code":"P0001","details":null,"hint":null,"message":"HUMAN_ACK_ONLY: acknowledged_by=system は機械名義ゆえ拒否"}' >"$out"; printf 400; fi
    return 0
  fi
  case "$url" in *parent_message_id=in.*) printf '[]\n200'; return 0 ;; esac
  echo "$url" >>"$FAKE_DIR/get.log"
  local n f
  n=$(cat "$FAKE_DIR/pollno" 2>/dev/null || echo 0); n=$((n+1)); echo "$n" >"$FAKE_DIR/pollno"
  f="$FAKE_DIR/rows-$n.json"; [ -f "$f" ] || f="$FAKE_DIR/rows.json"
  cat "$f"; printf '\n200'
}
'''

FAKE_SUDO = '''#!/usr/bin/env bash
while [ "$#" -gt 0 ]; do case "$1" in -n) shift ;; -u) shift 2 ;; *) break ;; esac; done
exec "$@"
'''

FAKE_TMUX = '''#!/usr/bin/env bash
[ "$1" = -S ] && shift 2
cmd="$1"; shift
case "$cmd" in
  has-session) exit 0 ;;
  set-buffer) [ "$1" = -- ] && shift; printf '%s' "$1" >"$FAKE_DIR/buffer" ;;
  paste-buffer) cp "$FAKE_DIR/buffer" "$FAKE_DIR/composer" ;;
  send-keys)
    if [ -s "$FAKE_DIR/composer" ]; then
      cat "$FAKE_DIR/composer" >>"$FAKE_DIR/history"; echo >>"$FAKE_DIR/history"
      cat "$FAKE_DIR/composer" >>"$FAKE_DIR/pokes"; echo >>"$FAKE_DIR/pokes"
      : >"$FAKE_DIR/composer"
    fi ;;
  capture-pane)
    tail -n 5 "$FAKE_DIR/history" 2>/dev/null
    echo "──────────────"
    printf '❯ %s\\n' "$(cat "$FAKE_DIR/composer" 2>/dev/null)" ;;
esac
exit 0
'''


def run_watcher(tmp, polls, rows_by_poll=None, rows=None, ack="reject", watcher=WATCHER, guard=GUARD):
    tmp.mkdir(parents=True, exist_ok=True)
    shim = tmp / "shim"
    (shim / "lib").mkdir(parents=True)
    shutil.copy(watcher, shim / "watcher.sh")
    shutil.copy(guard, shim / "lib/hermes2_reverse_guard.sh")
    (shim / "lib/sb_auth.sh").write_text(FAKE_SB)
    fake = tmp / "fake"
    fake.mkdir()
    bindir = tmp / "bin"
    bindir.mkdir()
    for name, body in (("sudo", FAKE_SUDO), ("tmux", FAKE_TMUX)):
        p = bindir / name
        p.write_text(body)
        p.chmod(0o755)
    if rows is not None:
        (fake / "rows.json").write_text(json.dumps(rows))
    for i, rs in enumerate(rows_by_poll or [], 1):
        (fake / f"rows-{i}.json").write_text(json.dumps(rs))
    home = tmp / "home"
    home.mkdir()
    env = {
        "PATH": f"{bindir}:{os.environ['PATH']}", "HOME": str(home), "FAKE_DIR": str(fake), "FAKE_ACK": ack,
        "SUPABASE_URL": "http://fake.invalid", "SUPABASE_SERVICE_ROLE_KEY": "fake-not-a-secret",
        "H2_MAX_POLLS": str(polls), "H2_POKE_RATE_LIMIT_SEC": "0", "H2_TMP_DIR": str(tmp),
        "H2_PROCESSED_FILE": str(tmp / "processed.txt"), "H2_HEALTH_FILE": str(tmp / "health.json"),
        "H2_WATCHER_LOG": str(tmp / "watcher.log"), "H2_LAST_POKE_FILE": str(tmp / "lastpoke.ts"),
        "H2_DEFER_FILE": str(tmp / "defer.count"), "H2_DEFER_ALERT_FILE": str(tmp / "defer.alert"),
        "H2_LOCK_FILE": str(tmp / "watcher.lock"), "H2_WOKEN_STATE": str(tmp / "woken.state"),
        "H2_ACK_REJECT_LEDGER": str(tmp / "ack_rejected.jsonl"),
    }
    p = subprocess.run(["bash", str(shim / "watcher.sh"), "--interval", "0"], env=env,
                       capture_output=True, text=True, timeout=300)

    def lines(name):
        f = fake / name
        return [ln for ln in f.read_text().splitlines() if ln] if f.exists() else []

    led = tmp / "ack_rejected.jsonl"
    return {
        "rc": p.returncode, "pokes": lines("pokes"), "patch": lines("patch.log"), "get": lines("get.log"),
        "ledger": [json.loads(ln) for ln in led.read_text().splitlines()] if led.exists() else [],
        "health": json.loads((tmp / "health.json").read_text()) if (tmp / "health.json").exists() else {},
        "log": (tmp / "watcher.log").read_text() if (tmp / "watcher.log").exists() else "",
    }


def integration_tests(tmp):
    a, b = row(1, 101), row(2, 102)

    r = run_watcher(tmp / "A_same", 3, rows=[a, b])
    check("int⑴ 陰性: 同じ組を3回照会しても起こすのは1回", r["rc"] == 0 and len(r["pokes"]) == 1, f"pokes={len(r['pokes'])} rc={r['rc']}")
    check("int⑴ 初回の起床に両 seq が載る", r["pokes"] and "seqs=101,102" in r["pokes"][0], str(r["pokes"]))
    check("int⑶ 陽性: 門に拒まれた2行が帳へ1件づつ", sorted(e["seq"] for e in r["ledger"]) == ["101", "102"], str(r["ledger"]))
    check("int⑶ 陰性: 拒まれた id へ PATCH を繰り返さない(各1回)", len(r["patch"]) == 2, f"patch={len(r['patch'])}")
    check("int⑶ health に ack_gate_rejected=2", r["health"].get("ack_gate_rejected") == 2, str(r["health"]))
    check("int⑶ log に GATE-REJECTED が出る(黙らない)", r["log"].count("ACK GATE-REJECTED machine") == 2, r["log"][-600:])
    check("int⑵ 照会に to_pc.eq.hermes2 が在る", bool(r["get"]) and all("to_pc.eq.hermes2" in u for u in r["get"]), r["get"][:1])
    check("int⑵ 照会に context_data->>target_agent.eq.hermes2 が在る",
          bool(r["get"]) and all("context_data-%3E%3Etarget_agent.eq.hermes2" in u for u in r["get"]), r["get"][:1])
    check("int⑵ 照会に topic.eq.cross_pc_inbox_hermes2 が在る",
          bool(r["get"]) and all("topic.eq.cross_pc_inbox_hermes2" in u for u in r["get"]), r["get"][:1])
    check("int⑵ 三つは or=(...) で結ぶ(AND で狭めない)", bool(r["get"]) and all("?or=(" in u for u in r["get"]), r["get"][:1])
    check("int⑵ 陰性: 旧い to_pc=eq.hermes2 単独の照会は残つてゐない", not any("to_pc=eq.hermes2" in u for u in r["get"]), r["get"][:1])

    r = run_watcher(tmp / "B_grow", 3, rows_by_poll=[[a], [a, b], [a, b]])
    check("int⑴ 陽性: 新しい seq が加はれば再び起こす(計2回)", len(r["pokes"]) == 2, f"pokes={len(r['pokes'])}")
    check("int⑴ 2回目の起床は新しい seq だけ", len(r["pokes"]) == 2 and r["pokes"][1].endswith("seqs=102"), str(r["pokes"]))

    r = run_watcher(tmp / "C_change", 3, rows_by_poll=[[a], [dict(a, priority="high")], [dict(a, priority="high")]])
    check("int⑴ 陽性: 状態が変はれば同じ seq でも起こす(計2回)", len(r["pokes"]) == 2, f"pokes={len(r['pokes'])}")

    r = run_watcher(tmp / "D_shrink", 3, rows_by_poll=[[a, b], [a], [a]])
    check("int⑴ 陰性: 減つただけなら起こさない(計1回)", len(r["pokes"]) == 1, f"pokes={len(r['pokes'])}")

    t = row(3, 103, topic="telemetry_inbox", context_data={"telemetry": True, "target_agent": "hermes2"})
    r = run_watcher(tmp / "E_telemetry", 3, rows=[t])
    check("int⑶ 陽性: telemetry の拒否も帳へ1件", [e["kind"] for e in r["ledger"]] == ["telemetry"], str(r["ledger"]))
    check("int⑶ 陰性: telemetry へ PATCH を繰り返さない(1回)", len(r["patch"]) == 1, f"patch={len(r['patch'])}")
    check("int telemetry は pane を起こさない", len(r["pokes"]) == 0, f"pokes={len(r['pokes'])}")

    r = run_watcher(tmp / "F_ack_ok", 3, rows=[a], ack="ok")
    check("int⑶ 陰性: ACK が通れば帳に書かない", r["ledger"] == [] and r["health"].get("ack_gate_rejected") == 0, str(r["ledger"]))
    check("int ACK が通れば起こすのは1回", len(r["pokes"]) == 1, f"pokes={len(r['pokes'])}")


def main():
    for p in (WATCHER, GUARD):
        if not p.is_file():
            print(f"FAIL missing {p}")
            return 1
    with tempfile.TemporaryDirectory(prefix="h2wake-") as d:
        tmp = pathlib.Path(d)
        (tmp / "unit").mkdir()
        unit_tests(tmp / "unit")
        integration_tests(tmp / "int")
    print(f"SUMMARY pass={len(FAILS) == 0} fails={len(FAILS)}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
