# -*- coding: utf-8 -*-
"""機構の直射 ―― 門を経ずに ★grep 其の物★ を撃ち、鳴りの因を名指す。
門を直さぬ ∴ 之は「門が何に乗つて居るか」を測るだけである。"""
import importlib.util, os, subprocess
spec = importlib.util.spec_from_file_location("K", "driver/00_kaki.py")
K = importlib.util.module_from_spec(spec); spec.loader.exec_module(K)

GREP = "/usr/bin/grep"
PAT2 = "[ \t]+\r?$"      # 門 條② の実型(逐語)
PAT3 = "\r"              # 門 條③ は grep -c $'\r' ―― 固定文字列ではなく ERE

def sh(args, env=None):
    e = dict(os.environ)
    if env: e.update(env)
    r = subprocess.run(args, capture_output=True, env=e)
    return r.returncode, r.stdout.decode("utf-8","replace").strip(), r.stderr.decode("utf-8","replace").strip()

rows = []
for nm in sorted(os.listdir("_tane")):
    p = "_tane/" + nm
    b = open(p,"rb").read()
    gyou = b.count(b"\n")
    # 素
    rc2, o2, _ = sh([GREP,"-cE",PAT2,p])
    rc3, o3, _ = sh([GREP,"-c","\r",p])
    # NUL を除いた同じ中身(機構の切り分け ―― 書き出さず stdin へ)
    r = subprocess.run([GREP,"-cE",PAT2], input=b.replace(b"\x00",b""), capture_output=True)
    onul = r.stdout.decode().strip()
    # -v
    rv2, v2, _ = sh([GREP,"-cE",PAT2,p], env={"GREP_OPTIONS":"-v"})
    rv3, v3, _ = sh([GREP,"-c","\r",p], env={"GREP_OPTIONS":"-v"})
    rows.append([nm, gyou, b.count(b"\x00"), o2, rc2, onul, o3, rc3, v2, rv2, v3, rv3])
K.kaku_tsv("raw/30_grep_chokusha.tsv", rows,
    header=["種","行(LF数)","NUL数","素②数","素②rc","NUL除去後②数","素③数","素③rc","v②数","v②rc","v③数","v③rc"])

# ―― GREP_OPTIONS が実際に効くのか(BSD grep 2.6.0-FreeBSD)――
rc, o, e = sh([GREP,"--version"])
K.kaku("raw/31_grep_mi.txt", "\n".join([
  "# 門が解く grep の身元",
  "",
  "path = %s" % GREP,
  "which(PATH 先頭) = %s" % sh(["bash","-lc","command -v grep"])[1],
  "",
  "--version:", o,
  "",
  "rc=%d" % rc,
]))
print("直射 了")
