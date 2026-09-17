#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""km-117 納めの文を ★紙から数を抜いて★ 組む(打ち直さぬ)。送りはせぬ ―― 出目を raw/90_fumi.txt へ。
★臺帳凍結後に生れた器★ ∴ 己も出目も臺帳の外。
"""
import hashlib, os, re, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kaki as K

B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(B)
paper = open("00_shodan.md", encoding="utf-8").read()
shimai = open("raw/99_shimai.txt", encoding="utf-8").read()

def pick(src, pat, nm):
    m = re.search(pat, src)
    if not m:
        raise SystemExit("★紙から抜けぬ: %s★" % nm)
    return m.group(1)

# ★紙の逐語から抜く(打ち直さぬ)★
v5 = pick(paper, r"\| \*\*v5_PR23\*\* \| \*\*(\d+)\*\* \| \*\*(\d+)\*\* \| \*\*(\d+)\*\* \|", "v5 の三数") \
     if False else re.search(r"\| \*\*v5_PR23\*\* \| \*\*(\d+)\*\* \| \*\*(\d+)\*\* \| \*\*(\d+)\*\* \|", paper).groups()
kusari = re.search(r"\| 案甲鎖 \| (\d+) \| (\d+) \| (\d+) \|", paper).groups()
bo = re.search(r"\| 案戊\(断の外\) \| (\d+) \| (\d+) \| (\d+) \|", paper).groups()
sub = pick(paper, r"v5 ⊂ 鎖.*?\| \*\*(\d+)\*\* \|", "v5⊂鎖")
sub_r = pick(paper, r"鎖 ⊂ v5.*?\| \*\*(\d+)\*\* \|", "鎖⊂v5")
otori_v5 = pick(paper, r"\| \*\*v5_PR23\*\* \| 正 \| 正 \| ★偽の通★ \| \*\*(\d+)\*\* \|", "囮 v5")
daichou0 = pick(paper, r"★臺帳甲 11821 行で、v5 の第二の for が足した候補は (\d+) 本。★", "臺帳甲の寄与")
diff_sha = pick(paper, r"`raw/40_naoshi\.diff`\(sha256 `([0-9a-f]{64})`", "diff の sha")
sue_sha = pick(paper, r"出来た物の sha256 = `([0-9a-f]{64})`", "据ゑ試しの sha")
kadou = pick(paper, r"\| 今 `scripts/checks/karo_mac_manifest_verify\.py` に在る器 \| `([0-9a-f]{8})…` \| (?:\d+) \| \*\*盤の `v2_originmain` と同一\*\* \|", "稼働木の sha")
ingai = pick(shimai, r"== 員外\(★臺帳に載せたが門へ渡さなんだ物★・(\d+)本\) ==", "員外の数")
daichou_gyou = pick(shimai, r"path= の行\t(\d+)", "臺帳の行")
mon0 = pick(shimai, r"★臺帳の中の mon_ を含む行\(自数\)\t(\d+)★", "mon_ の自数")
futa = pick(shimai, r"★納めの二走\(受取条件⑷\)★ = (.+)", "納めの二走")

# 實(受取条件⑺) ―― ★端点を宣する★
T0 = time.mktime(time.strptime("2026-09-17 19:20:00", "%Y-%m-%d %H:%M:%S"))  # 下命の刻(task yaml issued)
now = time.time()
jitsu = int((now - T0) // 60)
paper_b = open("00_shodan.md", "rb").read()

body = (
 "km-117 納め ―― PR#23 v5 の可否、己の数で断じた。★断=⑶(第二の for だけ除く)★\n"
 "束=docs/evidence/ashigaru-mac-2_km-117-v5-wo-240-hashiri-ni-kakeyo-20260917/ 紙=00_shodan.md\n"
 "㋐型見30面(通/赤/正): v5=%s/%s/%s・案甲鎖=%s/%s/%s・六欄突合で v5≡案甲鎖 30/30。方言丙は★十二器悉く2通3赤★。\n"
 "㋑家老の読みに訂正二つ: ⑴③sha無の行は main() が paths_of の前で落とす∴差に成り得ぬ(㋐飛ばし585行)。"
 "⑵★向きが逆★―― v5⊂鎖=%s行 / 鎖⊂v5=%s行 ∴ v5 の方が厳しい(則②當りで return が第二のforをも飛ばす)。"
 "臺帳甲11821行で出目の変る行=★0★。差6行は悉く臺帳でないTSV。\n"
 "㋒第二の for は★v5 の新設に非ず★―― v1_127行から在り案甲鎖も持つ(grep=1 が十一器)。"
 "囮の区(臺帳の主張する path 不在・'/'語実在)で偽の通/6: 八器=3・v5=%s(方言丙のみ)・第二無/案戊=0。"
 "区癸は十二器 rc1 だが★理由が違ふ★(八器=相違:aru/mono.txt=囮を昇格／第二無=実体無:nai/mono.txt)。臺帳甲での寄与=%s本。\n"
 "㋓陽性対照 区庚(真に不在)=36面悉く rc1/正。負対照 区辛は★方言乙で v5/案甲鎖/案乙が偽の赤★(則②非貪欲が bytes= lines= を呑む)。"
 "v4 の得た丁二/戊二は方言甲で保つ。現物での乙の穴=11821行中 他の欄を呑む行★0★。\n"
 "㋔断=★⑶★。⑵却下(型見で得無し・囮1→3悪化・現物で緩い)。⑶は型見30面 六欄不動のまま囮1→0。"
 "diff=raw/40_naoshi.diff(sha %s…)・据ゑ試し rc0/rc0・出来た物 sha %s… で拙者の測つた版と一致。\n"
 "★残る穴(悉くは治らぬ)★=9面: 乙丁二/乙戊/乙戊二/乙辛=偽の赤・丙甲/丙己=偽の通・丙丁二/丙戊/丙戊二=偽の赤。方言丙は十二器誰も治さず。\n"
 "★⑶が閉ぢる物★=「sha256有・path無・'/'裸語」の行形(臺帳甲に今0行だが不可能ではない)。\n"
 "★要注意★ 稼働木の scripts/checks/karo_mac_manifest_verify.py は sha %s… = ★v2_originmain(198行・最悪段6/9/15)★。"
 "PR#23 の v5 は★据ゑて居らぬ★∴ 上の diff は PR#23 枝に当てる物で、稼働木へは素で当たらぬ(逐語錠の路を紙に書いた)。\n"
 "断の外=案戊(2/3/25・囮0/6)。宣する穴=末尾が ' a=b' の path を切る。据ゑ所を求められれば別便で測る。\n"
 "㋕門 rc=0 ★二度★(控名 %s)・臺帳 path=行 %s・★臺帳の中の mon_ 行=%s★・員外 %s本(理由は raw/99_shimai.txt)。"
 "門の疵を一つ拾つた: 條②は★空白/TABの直後にNULが来ると濡れ衣を着せる★(六対照で当てた・偽の赤の向き)。\n"
 "受取条件⑶ km-114 からの写し=写しの儘9/★写した後に書き換へた1(driver/10_menseki.py)★/己が書いた11(raw/42_utsushi.txt に出所sha)。\n"
 "禁: commit/push/枝/refs書込=零。scripts/ 配下=一指も触れず(v5 は git cat-file で取り出し束内で走らせた)。他席の束=不触。空白名=零。\n"
 "宣ETA 全納20:35 / ★實=下命19:20 から %d 分(此の文を組んだ刻 %s)★ ―― 端点=task yaml issued → 文の組み上がり。\n"
 "紙 00_shodan.md = %d行 / %dbyte / sha256 %s…\n"
 "★之が意味せぬ事★: 型見の数は己が建てた30区の話で現物の分布に非ず。現物の数は歩き根 docs/evidence・刻19:34〜19:36 の物。"
 "門 rc=0 は「中身が正しい」を言はず「出す前五條を満たす」の一事のみ。"
) % (v5[0], v5[1], v5[2], kusari[0], kusari[1], kusari[2], sub, sub_r, otori_v5, daichou0,
     diff_sha[:12], sue_sha[:12], kadou, futa, daichou_gyou, mon0, ingai,
     jitsu, time.strftime("%Y-%m-%dT%H:%M:%S%z"),
     paper_b.count(b"\n"), len(paper_b), hashlib.sha256(paper_b).hexdigest()[:12])

open("raw/90_fumi_hondou.txt", "w", encoding="utf-8", newline="\n").write(body)
L = ["# km-117 納めの文 ―― 刻 " + time.strftime("%Y-%m-%dT%H:%M:%S%z"),
     "胴の字数(python len)\t%d" % len(body),
     "胴の bytes(utf-8)\t%d" % len(body.encode("utf-8")),
     "胴の行(LF数)\t%d" % body.count("\n"),
     "胴 sha256\t" + hashlib.sha256(body.encode("utf-8")).hexdigest(),
     "★紙から抜いた数(打ち直して居らぬ)★",
     "\tv5 通/赤/正\t%s/%s/%s" % v5,
     "\t案甲鎖 通/赤/正\t%s/%s/%s" % kusari,
     "\t案戊 通/赤/正\t%s/%s/%s" % bo,
     "\tv5⊂鎖 / 鎖⊂v5\t%s / %s" % (sub, sub_r),
     "\t囮 v5 偽の通\t%s" % otori_v5,
     "\t臺帳甲 第二for の寄与\t%s" % daichou0,
     "\tdiff sha\t%s" % diff_sha,
     "\t据ゑ試しの出来物 sha\t%s" % sue_sha,
     "\t稼働木 sha(頭8)\t%s" % kadou,
     "\t臺帳 path=行 / mon_行 / 員外\t%s / %s / %s" % (daichou_gyou, mon0, ingai),
     "\t納めの二走\t%s" % futa,
     "★實★\t下命 2026-09-17T19:20:00 → 文の組み上がり = %d 分" % jitsu,
     "★之が意味せぬ事★",
     "・「字数 %d」は inbox の受ける上限を言はぬ ―― 送つた後に箱の尾を読んで検める。" % len(body),
     "・「實 %d 分」は手を動かした時間ではない ―― ★下命の刻から文を組むまでの壁時計★である。" % jitsu,
     "・此の器と此の出目は ★臺帳が凍つた後★ に生れた ∴ 臺帳にも門にも載らぬ。"]
K.kaku("raw/90_fumi.txt", "\n".join(L))
print("\n".join(L[:6]))
print("★胴を raw/90_fumi_hondou.txt へ書いた★")
