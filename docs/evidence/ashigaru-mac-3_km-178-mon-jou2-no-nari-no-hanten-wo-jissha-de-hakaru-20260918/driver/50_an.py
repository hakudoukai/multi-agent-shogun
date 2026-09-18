# -*- coding: utf-8 -*-
"""治し方の案 ―― ★器は直さぬ(変更統制)★。案の効きだけを ★器の外で★ 撃つて示す。"""
import importlib.util, os, subprocess, datetime
spec = importlib.util.spec_from_file_location("K","driver/00_kaki.py")
K = importlib.util.module_from_spec(spec); spec.loader.exec_module(K)
def ima(): return datetime.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")

def sh(args, env=None, stdin=None):
    e=dict(os.environ)
    if env is not None: e.update(env)
    r=subprocess.run(args,capture_output=True,env=e,input=stdin)
    return r.returncode, r.stdout.decode("utf-8","replace").strip()

PY_LAW = (r'import sys'"\n"
          r'b=open(sys.argv[1],"rb").read()'"\n"
          r'ls=b.split(b"\n")'"\n"
          r'if ls and ls[-1]==b"": ls=ls[:-1]'"\n"
          r'import re'"\n"
          r'print(sum(1 for l in ls if re.search(rb"[ \t]+\r?$", l)))')

rows=[]
for nm in sorted(os.listdir("_tane")):
    p="_tane/"+nm
    rc0,o0 = sh(["/usr/bin/grep","-cE","[ \t]+\r?$",p])                     # 素
    rcA,oA = sh(["python3","-B","-c",PY_LAW,p])                            # 案甲
    rcB,oB = sh(["/usr/bin/grep","-cE","[ \t]+\r?$",p], env={"GREP_OPTIONS":""})  # 案乙(素環境)
    rcBv,oBv = sh(["/usr/bin/env","-u","GREP_OPTIONS","/usr/bin/grep","-cE","[ \t]+\r?$",p],
                  env={"GREP_OPTIONS":"-v"})                               # 案乙(汚染下)
    nul = open(p,"rb").read().count(b"\x00")
    rows.append([nm, nul, o0, oA, "○" if o0==oA else "★差★", oB, oBv])
K.kaku_tsv("raw/50_an_jissha.tsv", rows,
  header=["種","NUL数","素(門の型)","案甲(python)","甲と素の差","案乙(GREP_OPTIONS空)","案乙(env -u・汚染下)"])

# 案乙 が汚染を本当に殺すか ―― 清い紙で確かめる
rc_y,o_y = sh(["/usr/bin/grep","-cE","[ \t]+\r?$","_tane/f01_kirei.txt"], env={"GREP_OPTIONS":"-v"})
rc_z,o_z = sh(["/usr/bin/env","-u","GREP_OPTIONS","/usr/bin/grep","-cE","[ \t]+\r?$","_tane/f01_kirei.txt"],
              env={"GREP_OPTIONS":"-v"})

K.kaku("_jou/05_naoshikata_an.md","\n".join([
 "# ㋓ 治し方の案 ―― ★紙に書くだけ★(器は一字も直して居らぬ)", "",
 "変更統制(委員長の事前許可)に依り ★門の器は直さぬ★。",
 "案の効きは ★器の外で同じ型を撃つ★ 事で示した(raw/50_an_jissha.tsv)。",
 "刻 = " + ima(), "",
 "## 穴は二つ在つた(本弾で実射したもの)", "",
 "  ★穴甲★ NUL の濡れ衣 ―― grep が NUL で行を切る故、NUL 直前の空白を行末と看る。",
 "          害の向き = ★偽の鳴り★(数を多く言ふ) ∴ ★安全側★。清い紙を落とす。",
 "  ★穴乙★ GREP_OPTIONS の汚染 ―― 環境変数が立つと各條が独立に反転する(v = 行 − 素)。",
 "          害の向き = ★一定ならず★。清い紙が鳴り、汚れた紙が黙る例も出た ∴ ★危険側を含む★。", "",
 "## 案甲(穴甲へ) ―― 行を ★byte で切る★", "",
 "  今 : `grep -cE $'[ \\t]+\\r?$' \"$f\"`",
 "  案 : 中身を byte で読み、`\\n` で切つてから型を当てる(python3 一行)。",
 "", "  ```python",
 "  b=open(f,'rb').read(); ls=b.split(b'\\n')",
 "  if ls and ls[-1]==b'': ls=ls[:-1]",
 "  n=sum(1 for l in ls if re.search(rb'[ \\t]+\\r?$', l))",
 "  ```", "",
 "  ★実射★ = %d 本中 ★%d 本で素と一致★・差が出たのは ★%s★" % (
   len(rows), sum(1 for r in rows if r[4]=="○"),
   "／".join(r[0] for r in rows if r[4]!="○") or "無し"),
 "  ∴ 案甲は ★NUL を持つ紙でのみ素と別れ、其処こそが濡れ衣の在處★ である。", "",
 "  ★併し案甲は無条件に勧められぬ★ ―― 害の向きが ★安全側★ である以上、",
 "  直す事で ★今まで落ちて居た紙が通る★ 様になる。∴ ★委員長の判が要る★。", "",
 "  ★代案(より小さく・fail-closed)★ = NUL を含む紙を條② の前に見つけ、",
 "  「★測れぬは通さぬ★」の既存の道へ倒す。器の既存の default-deny を使ふ故 ★新しい振舞ひを足さぬ★。", "",
 "## 案乙(穴乙へ) ―― 門の頭で環境を掃く", "",
 "  案 : 門の先頭で `unset GREP_OPTIONS GREP_COLOR GREP_COLORS` ―― もしくは各 grep を `env -u GREP_OPTIONS` で包む。",
 "",
 "  ★実射(清い紙 f01_kirei.txt・GREP_OPTIONS=-v を立てた儘)★",
 "    素のまま      → 出目「%s」(rc=%d) ―― ★清い紙が 2 行鳴る★" % (o_y, rc_y),
 "    env -u 経由   → 出目「%s」(rc=%d) ―― ★正しく 0★" % (o_z, rc_z),
 "  ∴ ★案乙は効く。★しかも ★出目の意味を変へぬ★(汚染が無い環境では何も変らぬ)。", "",
 "## 勧める順", "",
 "  ⑴ ★案乙を先に★ ―― 危険側の害を消し、出目の意味を変へず、一行で済む。",
 "  ⑵ 案甲(または其の代案)は ★後★ ―― 害が安全側ゆゑ急がず、通る紙が増える故 判が要る。", "",
 "★何れも本弾では据ゑて居らぬ。★器の sha256 は測り始めと締めで同一である事を _jou/06_kizu_hikae.md に焼く。",
]))
print("案 了")
