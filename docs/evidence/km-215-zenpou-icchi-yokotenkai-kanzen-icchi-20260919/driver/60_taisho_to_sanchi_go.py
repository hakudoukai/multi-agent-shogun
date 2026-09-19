# -*- coding: utf-8 -*-
"""60 ―― 同一runで(甲)兩對照(has-session 陽性/陰性)と(乙)据ゑ後の三値を併せ測る。
甲: tmux has-session -t multiagent (前方一致・陽性=誤つて掴む證) と
    tmux has-session -t =multiagent (完全一致・陰性=正しく掴まぬ證) の rc を別々に取る。
乙: 二器の據ゑ後 sha256/bytes/行 ―― 受入条件⑵。
丙: bash -n の rc ―― 受入条件⑶(再掲・同一runで採る)。
"""
import hashlib
import io
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BUNDLE = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(BUNDLE, "..", "..", ".."))
sys.path.insert(0, HERE)
import kaki as K  # noqa: E402

TMUX = "/opt/homebrew/bin/tmux"
if not os.path.exists(TMUX):
    TMUX = "tmux"

def has_session(target):
    p = subprocess.run([TMUX, "has-session", "-t", target],
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=ROOT)
    return p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")

rc_pos, out_pos, err_pos = has_session("multiagent")
rc_neg, out_neg, err_neg = has_session("=multiagent")

targets = ["scripts/switch_cli.sh", "scripts/watcher_supervisor_third.sh"]
rows = []
for rel in targets:
    p = os.path.join(ROOT, rel)
    data = io.open(p, "rb").read()
    sha = hashlib.sha256(data).hexdigest()
    n_bytes = len(data)
    n_lines = data.count(b"\n")
    bn = subprocess.run(["bash", "-n", p], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=ROOT)
    rows.append((rel, sha, n_bytes, n_lines, bn.returncode,
                 bn.stdout.decode("utf-8", "replace"), bn.stderr.decode("utf-8", "replace")))

lines = []
lines.append(u"★60 ―― 同一run: 兩對照 + 據ゑ後三値 + bash -n★")
lines.append(u"")
lines.append(u"■甲 兩對照(read-only ―― has-session のみ・send-keys 皆無)")
lines.append(u"  cwd=%s" % ROOT)
lines.append(u"  argv(陽性)=%s has-session -t multiagent" % TMUX)
lines.append(u"  rc(陽性)=%d  stdout=%r  stderr=%r" % (rc_pos, out_pos, err_pos))
lines.append(u"  argv(陰性)=%s has-session -t =multiagent" % TMUX)
lines.append(u"  rc(陰性)=%d  stdout=%r  stderr=%r" % (rc_neg, out_neg, err_neg))
lines.append(u"  ★判定★: rc(陽性)=0 かつ rc(陰性)≠0 ならば「前方一致は現に掴み、完全一致は現に掴まぬ」の證が立つ。")
ok_control = (rc_pos == 0 and rc_neg != 0)
lines.append(u"  ★對照成立=%s★" % (u"真" if ok_control else u"★偽(要再検)★"))
lines.append(u"")
lines.append(u"■乙 據ゑ後 三値(受入条件⑵)")
for rel, sha, nb, nl, bnrc, bnout, bnerr in rows:
    lines.append(u"  %s" % rel)
    lines.append(u"    sha256=%s bytes=%d 行=%d" % (sha, nb, nl))
    lines.append(u"    bash -n rc=%d out=%r err=%r" % (bnrc, bnout.strip(), bnerr.strip()))
lines.append(u"")
lines.append(u"★此の数が意味せぬ事★:")
lines.append(u"  ・對照は★此のrunの此の刻★の状態(當機に session multiagent-mac が生きて居る間のみ陽性が成立する)。")
lines.append(u"    session が落ちれば陽性対照も落ちる ―― 恒常の證ではない。")
lines.append(u"  ・乙の sha256 は★編集後★の値であり、編集が正しい事の證ではない(別途 15_shiwake/50/55 の實行結果と併せ読め)。")

K.kaku(os.path.join(BUNDLE, "raw", "60_taisho_to_sanchi_go.txt"), u"\n".join(lines) + u"\n")

print(u"rc_pos=%d rc_neg=%d control_ok=%s" % (rc_pos, rc_neg, ok_control))
for rel, sha, nb, nl, bnrc, _, _ in rows:
    print(u"%s sha256=%s bytes=%d 行=%d bash-n_rc=%d" % (rel, sha, nb, nl, bnrc))

assert ok_control, u"★對照不成立★"
for rel, sha, nb, nl, bnrc, _, _ in rows:
    assert bnrc == 0, u"★%s bash -n rc=%d★" % (rel, bnrc)
