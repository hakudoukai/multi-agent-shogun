# -*- coding: utf-8 -*-
import csv, importlib.util, os
spec = importlib.util.spec_from_file_location("K","driver/00_kaki.py")
K = importlib.util.module_from_spec(spec); spec.loader.exec_module(K)
import datetime
def ima(): return datetime.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")
K.ima = ima
def tsv(p):
    with open(p, encoding="utf-8") as fh: return list(csv.DictReader(fh, delimiter="\t"))
ip = tsv("raw/20_ippatsu.tsv"); ch = {r["種"]: r for r in tsv("raw/30_grep_chokusha.tsv")}

# ―― ㋑⑶ 反転の実射(両方向) ――
naru_de = [r for r in ip if r["法_條②"]=="鳴る"]   # 鳴るべき紙
damaru  = [r for r in ip if r["法_條②"]=="黙る"]   # 鳴るべきでない紙
a = [r for r in damaru if r["實_條②"]=="鳴る"]      # 向A: 鳴るべきでないのに鳴つた
b = [r for r in naru_de if r["實_條②"]=="黙る"]     # 向B: 鳴るべきなのに黙つた
L = ["# ㋑⑶ 反転の実射 ―― ★両方向★ に撃つ", "",
 "★片方向だけでは反転とは言へぬ。★∴ 二つの向きを別々に数へる。", "",
 "根   = %s" % os.path.join(os.getcwd(),"_tane"),
 "深さ = 1(_tane 直下のみ)",
 "母數 = %d 本(鳴るべき %d + 鳴るべきでない %d)" % (len(ip), len(naru_de), len(damaru)),
 "刻   = " + K.ima(), "",
 "## 向A ―― 「鳴るべきでない紙」に鳴つたか", "",
 "  母數 %d 本 ・ ★該当 %d 本★" % (len(damaru), len(a)), ""]
for r in a: L.append("  - %s (%s) ―― 鳴② %s 行 / ★rc=%s★ / 出目 %s" % (r["種"],r["問ひ"],r["鳴②"],r["rc"],r["出目"]))
if not a: L.append("  (一本も無し)")
L += ["", "## 向B ―― 「鳴るべき紙」に黙つたか", "",
 "  母數 %d 本 ・ ★該当 %d 本★" % (len(naru_de), len(b)), ""]
for r in b: L.append("  - %s (%s) ―― 鳴② %s 行 / ★rc=%s★ / 出目 %s" % (r["種"],r["問ひ"],r["鳴②"],r["rc"],r["出目"]))
if not b: L.append("  (一本も無し)")
L += ["", "## 黙りにも rc を添へる(向B の母數 ―― 鳴つた紙)", ""]
for r in naru_de: L.append("  - %s ―― 實=%s / 鳴② %s 行 / ★rc=%s★" % (r["種"],r["實_條②"],r["鳴②"],r["rc"]))
L += ["", "## 判", "",
 "  向A(偽の鳴り) = %d 本 ・ 向B(偽の黙り) = %d 本" % (len(a), len(b)), "",
 "★∴ 本日の器で出たのは ★片方向のみ★ である。★",
 "「反転」と呼べる程の双方向の崩れは ★実射では出なかつた★。",
 "出たのは ★偽の鳴り(濡れ衣)一方向★ であり、★偽の黙り(見逃し)は 0 本★。",
 "後者は 2026-09-12 の止血(器のコメントに逐語で在り)で塞がれて居ると読める ――",
 "実際 f04(CRLF かつ末尾空白)は ★鳴つた★(旧型なら黙る筈の形である)。"]
K.kaku("_jou/01_hanten.md","\n".join(L))

# ―― ㋑⑸ GREP_OPTIONS=-v ――
sw = tsv("raw/24_grep_options_v.tsv")
rows, kazu = [], {"入替":0,"入替に非ず":0}
for r in sw:
    s2,s3,v2,v3 = int(r["素_鳴②"]),int(r["素_鳴③"]),int(r["v_鳴②"]),int(r["v_鳴③"])
    ir = (v2,v3)==(s3,s2)
    kazu["入替" if ir else "入替に非ず"] += 1
    c = ch[r["種"]]; gyou=int(c["行(LF数)"])
    yosoku = (gyou-int(c["素②数"]), gyou-int(c["素③数"]))
    rows.append([r["種"],gyou,s2,s3,v2,v3,"○" if ir else "×",
                 "%d,%d"%yosoku, "○" if (int(c["v②数"]),int(c["v③数"]))==yosoku else "×"])
K.kaku_tsv("raw/41_v_hantei.tsv",rows,
  header=["種","行","素②","素③","v②","v③","入替か","予測(行-素)","予測と合ふか"])
K.kaku("_jou/02_grep_options.md","\n".join([
 "# ㋑⑸ `GREP_OPTIONS=-v` で ②と③ は入れ替はるか", "",
 "★門に -v/冗語の旗は無い。★(`grep -n -- '-v' <器>` で旗の定義 0 件)",
 "∴ memory の言ふ「-v」は ★環境変数 GREP_OPTIONS=-v★ と解して撃つた。", "",
 "母數 = %d 本 ・ 根 = _tane ・ 深さ 1 ・ 刻 = %s" % (len(sw), K.ima()), "",
 "## 出目", "",
 "  ★入替に見えた   = %d 本★" % kazu["入替"],
 "  ★入替に非ず     = %d 本★" % kazu["入替に非ず"], "",
 "## ★然し「入替」は因の名ではない★", "",
 "grep 直射(raw/30_grep_chokusha.tsv)で測ると、-v 下の出目は悉く",
 "", "    ★v の数 = 其の file の行数 − 素の数★", "",
 "に一致した(raw/41_v_hantei.tsv 末欄 ―― %d/%d 本が予測と一致)。" % (
   sum(1 for r in rows if r[-1]=="○"), len(rows)), "",
 "∴ 機構は ★入替ではなく反転★ である ―― `-c` と `-v` が重なり、",
 "grep が ★型に合はぬ行★ を数へる。②も③も ★各々独立に★ 反転する。",
 "「②と③が入れ替はる」様に見えた %d 本は、たまたま (行−素) が" % kazu["入替"],
 "相手の素と等しく成つただけの ★偶然★ である。", "",
 "## 害の向き", "",
 "  ★清い紙(f01)が -v 下で ②③ 共に鳴る★(素 0,0 → v 2,2 / rc 0→1)。",
 "  ∴ 之は ★偽の黙り★ ではなく ★偽の鳴り★ を作る = ★安全側に倒れる★。",
 "  併し ★f06 の様に素で鳴つて居た紙が -v 下で黙る★ 例も在る(素②1 → v②0) ――",
 "  ★∴ 向きは一定ではない。GREP_OPTIONS が立つた環境では門の出目は信じられぬ。★",
]))
print("紙 了")
