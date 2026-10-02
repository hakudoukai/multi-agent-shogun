#!/usr/bin/env python3
"""陰性対照: 写しを一箇所だけ壊し、試験が赤に成る事を確かめる。原本には触れない。"""
import os, pathlib, subprocess, sys, tempfile
WT = pathlib.Path("/home/hakudoukai/a2/wt-a6c0-h2watch")
W = WT / "shim/hakudokai/hakudokai_hermes2_reverse_watcher.sh"
G = WT / "shim/hakudokai/lib/hermes2_reverse_guard.sh"
T = WT / "tests/test_hermes2_reverse_wake_dedup.py"
MUT = [
  ("M1 wake_select が常に起こす(⑴)", "G", 'key(row) not in woken]', 'True]'),
  ("M2 照会を旧い to_pc 単独へ戻す(⑵)", "W", "?or=(to_pc.eq.hermes2,context_data-%3E%3Etarget_agent.eq.hermes2,topic.eq.cross_pc_inbox_hermes2)", "?to_pc=eq.hermes2"),
  ("M3 照会から topic だけ落とす(⑵)", "W", ",topic.eq.cross_pc_inbox_hermes2)", ")"),
  ("M4 起床の記録を外す(⑴)", "W", 'H2_WAKE_IDS="$NEW_IDS" h2_wake_record \\', 'H2_WAKE_IDS="$NEW_IDS" true \\'),
  ("M5 門の拒否を見ない＝黙る(⑶)", "G", 'gate = os.environ["H2_REJ_HTTP"] == "400" and', 'gate = False and'),
  ("M6 帳へ書かない(⑶)", "G", 'f.write(json.dumps(entry, ensure_ascii=False) + "\\n")', 'pass'),
  ("M7 帳の id を見ず PATCH を繰り返す(⑶)", "G", 'grep -Fq -- "\\"id\\": \\"$id\\"" "$ledger"', 'return 1'),
]
red = 0
for name, which, old, new in MUT:
    d = pathlib.Path(tempfile.mkdtemp(prefix="h2mut-"))
    w, g = d / "w.sh", d / "g.sh"
    ws, gs = W.read_text(), G.read_text()
    src = gs if which == "G" else ws
    n = src.count(old)
    if n != 1:
        print(f"ERROR {name}: 壊し所が {n} 箇所(1 であるべき)"); sys.exit(2)
    src = src.replace(old, new)
    if which == "G": gs = src
    else: ws = src
    w.write_text(ws); g.write_text(gs)
    env = dict(os.environ, H2_TEST_WATCHER=str(w), H2_TEST_GUARD=str(g))
    p = subprocess.run([sys.executable, str(T)], env=env, capture_output=True, text=True, timeout=900)
    fails = [l for l in p.stdout.splitlines() if l.startswith("FAIL")]
    ok = p.returncode != 0 and fails
    red += bool(ok)
    print(f"{'RED ' if ok else 'GREEN(穴)'} {name} rc={p.returncode} fails={len(fails)}")
    for l in fails: print("    " + l[:160])
print(f"MUTATION SUMMARY red={red}/{len(MUT)}")
sys.exit(0 if red == len(MUT) else 1)
