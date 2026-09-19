# -*- coding: utf-8 -*-
"""65 ―― ④依存は repository-local・lockfile 未測、代りに實際に呼んで在処と版を引く。
★注意★: 對象二器(switch_cli.sh/watcher_supervisor_third.sh)は `bash <script>` で
起動される ―― 即ち其の `grep` 解決は★此の對話 zsh session の函數(ugrep 経由)を
繼がぬ★(函數は shell 固有・子 bash process へは渡らぬ)。∴ 在処測定は
`bash -c '...'` を通して行ひ、對話 shell の別解決(ugrep)と混同せぬ事。
"""
import io
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BUNDLE = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(BUNDLE, "..", "..", ".."))
sys.path.insert(0, HERE)
import kaki as K  # noqa: E402

TAG = sys.argv[1] if len(sys.argv) > 1 else "65_izon_kyoukai"

def bash_c(cmd):
    p = subprocess.run(["bash", "-c", cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=ROOT)
    return p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")

lines = []
lines.append(u"★65 ―― ④依存境界(repository-local lockfile 未測・代替=實測)★")
lines.append(u"")
lines.append(u"■理由")
lines.append(u"  對象二器は shell script であり、当repoに shell 依存の lockfile は存在せぬ。")
lines.append(u"  代りに、對象二器が★実行時に實際呼ぶ経路★(=`bash <script>` の子process)で")
lines.append(u"  在処・rc・版を引いた。")
lines.append(u"")
lines.append(u"■對話shellとの相違(注意・自己検証)")
lines.append(u"  對話 zsh session の裸 `grep` は函數(ugrep 7.8.4 を claude 経由で呼ぶ)に")
lines.append(u"  解決される ―― だが此の函數は★zsh固有★であり、對象二器を起動する")
lines.append(u"  `bash <script>` の子processへは継がれぬ(函數はshell間を渡らぬ)。")
lines.append(u"  ∴ 下記は★`bash -c` を通した実測★(=對象二器と同じ解決経路)。")
lines.append(u"")

tools_cmds = [
    ("bash", "command -v bash", "bash --version"),
    ("tmux", "command -v tmux", "tmux -V"),
    ("grep", "command -v grep", "grep --version"),
]

rows = []
for name, loc_cmd, ver_cmd in tools_cmds:
    loc_rc, loc_out, loc_err = bash_c(loc_cmd)
    ver_rc, ver_out, ver_err = bash_c(ver_cmd)
    loc = loc_out.strip() if loc_rc == 0 else u"(rc=%d) %s" % (loc_rc, loc_err.strip())
    ver_line = (ver_out.splitlines() or [u""])[0].strip() if ver_out.strip() else ver_err.splitlines()[0].strip() if ver_err.strip() else u""
    rows.append((name, loc, loc_rc, ver_line, ver_rc))
    lines.append(u"  %s" % name)
    lines.append(u"    argv(在処)=bash -c %r  rc=%d  在処=%s" % (loc_cmd, loc_rc, loc))
    lines.append(u"    argv(版)=bash -c %r  rc=%d  版=%s" % (ver_cmd, ver_rc, ver_line))

lines.append(u"")
lines.append(u"■対象二器が literal に呼ぶ外部器(逐語grep済・raw/10_bosuu.txt系とは別に本弾で再確認)")
lines.append(u"  scripts/switch_cli.sh: tmux(list-panes/display-message/show-options/send-keys/capture-pane/set-option/select-pane)・grep(-v, -qE, -qiE)")
lines.append(u"  scripts/watcher_supervisor_third.sh: tmux(list-panes)・grep(-qx)・pgrep")
lines.append(u"")
lines.append(u"★此の数が意味せぬ事★:")
lines.append(u"  ・此は★系(Mac本体)の器★であって repository-local ではない ―― 之は本弾で直した事ではない。")
lines.append(u"  ・對話shellの `grep`(ugrep)とscript内`grep`(/usr/bin/grep BSD)は★別物★ ―― 混同禁(raw/10の`--include`後置罠と同根の注意)。")

K.kaku(os.path.join(BUNDLE, "raw", "%s.txt" % TAG), u"\n".join(lines) + u"\n")

for name, loc, loc_rc, ver_line, ver_rc in rows:
    print(u"%s 在処=%s(rc=%d) 版=%s(rc=%d)" % (name, loc, loc_rc, ver_line, ver_rc))
