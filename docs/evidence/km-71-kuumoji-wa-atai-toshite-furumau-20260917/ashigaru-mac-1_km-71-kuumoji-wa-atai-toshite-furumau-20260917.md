# 第71弾 ―― ★空文字は値として振舞ふ ―― 己の器を悉皆せよ★(家老mac 発注 06:40:22・msg_20260917_064022_8608761c)―― 母數 N=30 器 / M=266 箇所(㋐)・門の基点 三態 24 走で "" は "." と同じ挙動・札だけ「明示」(㋑)・形六つを評価して示し檢出子自身の対照を同じ路に乗せた(㋒㋓)・塞ぎ方は紙のみ(㋔)―― 答を先に(★數の出處 = raw/20_bosu.{txt,tsv} / raw/30_mon_santai.{txt,tsv} + raw/30_*.{out,err,rc} / raw/40_katachi.txt / raw/fixture/{pos,neg}.py / raw/05_chakushu*.txt(起・宣)/ _after/60_gate_rcs.txt(門・紙の後に生れる故 紙は其の數を書けぬ)/ _after/63_sent.txt(端点・實)★)

★臺帳の基点(一行)★: 本束の臺帳 `ashigaru-mac-1_km-71-kuumoji-wa-atai-toshite-furumau-20260917_manifest.txt` の path は ★束の根 `/Users/momizimac/multi-agent-shogun/docs/evidence/km-71-kuumoji-wa-atai-toshite-furumau-20260917/` からの相對(束内相対・裁 322699)★ ―― append.py を cwd = 束の根で呼ぶ故。照合は門に `KM_GATE_MANIFEST_BASE=<束の根の絶対 path>` を渡すか verify.py の第二引数に束の根を渡せ。既定基点(repo 根)で当てれば悉く実体無と出る(基点の違ひ)。★空文字 "" と "." は渡すな ―― 何れも cwd 相対に成る(本紙 §2)★。

## 0. 断(先に)と親子の宣
1. **㋐ ★N = 30 本 / M = 266 箇所★**(現物。自身 1 本 19 箇所・fixture 2 本は別札)。数へ方: 歩き根 = km-70 束・自主束・km-71 束(己)/ 深さ 無限(os.walk・__pycache__ は降りぬ)/ 規約 = S_ISREG かつ .py / 非通常 0・非 .py 291 は母數外 / fixture/ は同じ路で歩き現物と分ける / 己は path 一致で「自身」。形別 A 2 / B 4 / C 15 / D 156 / E 89 / F 0・危=high 1(km-70 raw/67_git_add.py L8 `l[:1] in 'AM'` ―― km-70 _after/66 で既に名指した物)。★M は「効き得る箇所」の上界であつて疵の数ではない★ ―― D/E の多くは欠(None)を扱ふ設計で、空文字が其處へ★来るか★は静的には判ぜぬ(器では決められぬ則は数へ器に堕ちる)。
2. **㋑ 門の基点 三態(据ゑず・24 走)**: unset: 通 4 落 4 不明 0 / kuu: 通 4 落 4 不明 0 / dot: 通 4 落 4 不明 0。★cwd で條①が反転した組 = 8(= "" と "." の四臺帳全部・unset は 0 組)★。∴ ★"" は "." と寸分違はぬ挙動(cwd 相対)で、違ふのは札だけ★ ―― "." は呼ぶ側が字で書いた明示、"" は「何も書いて居らぬ」のに門は `條① 基点=★引数 明示★` を刷る。通/落の数が三態で同じ(各 通 4 落 4)のは ★数だけ見れば三態が同じに見える★ 事の實例 ―― 反転の組で初めて別れる。
3. **㋒ 形六つ**(40 で評価): A 包含 in(`'' in 'AM'` → True)/ B 等価 == ''(値の欠と空の値を同じ枝へ)/ C x or 定数(空は黙つて既定へ)/ D 裸の真偽(空は False = 無いと同じ枝)/ E 三項 else 定数(測れた空が『引けぬ』の顔)/ F startswith('')(常に True)。発注の三つ(包含 in / 等価 == / 既定落ち or)を含み六つ。
4. **㋓ 対照は檢出子 20 自身の路に在る**: raw/fixture/pos.py(各形一つ)と neg.py(似て非なる形)を ★同じ os.walk★ で歩き現物と分けて数へた ―― 陽性 {'A': 1, 'B': 1, 'C': 1, 'D': 2, 'E': 1, 'F': 1} → 悉く拾つた / 陰性 0 → 一つも拾はず。零の四つの札: 陽性対照 通 / 根と深さ 上記 / rc 0 / 刻 20 の頭。
5. **㋔ 塞ぎ方は紙のみ(§5)** ―― 三つの案に 逐語 diff・戻し方一行・塞がぬ物。共有器へ 0 byte・四束(km-47/50/70・自主束)へ 0 byte(30 の印 前後同)。
6. **親子の宣**: 自主束 `docs/evidence/a1-jishu-kuumoji-kiten-20260917/`(06:34〜06:41・空文字基点 16 走・門 通)は ★本弾の子★ である。動かして居らぬ(凍結済・staged 118)。本弾 30 は其の 16 走を四臺帳 24 走へ広げ、"." を加へて「"" は "." である」を示した。

## 1. ㋐ 母數(20)―― 数へ方は頭に、数は後に
## 数へ方: 歩き根 = docs/evidence/km-70-daichou-no-ne-wo-sokunai-soutai-e-tatenaosu-20260917 / docs/evidence/a1-jishu-kuumoji-kiten-20260917 / docs/evidence/km-71-kuumoji-wa-atai-toshite-furumau-20260917 / 深さ 無限(os.walk・__pycache__ は降りぬ)/ 規約 = S_ISREG かつ名が .py で終はる / 非通常(symlink 等)と非 .py は別に数へ母數に入れぬ / fixture/ 配下は同じ路で歩き現物と分ける / 己(20_bosu.py)は path 一致で「自身」と札し現物から外す
## ★N(器・現物)= 30 本★(自身 1 本・fixture 2 本は別) / 非通常 0 / 非 .py 291 / parse 失敗 0 []
## ★M(長さ0の文字列が判定に効き得る箇所・現物)= 266 箇所★(自身 19 箇所は別)
## 束別 N / M(現物): km-70-daichou-no-ne-wo-sokunai-soutai-e-tatenaosu-20260917 N 18 M 180 / a1-jishu-kuumoji-kiten-20260917 N 10 M 79 / km-71-kuumoji-wa-atai-toshite-furumau-20260917 N 2 M 7
## 形別 M(現物): A 2 / B 4 / C 15 / D 156 / E 89 / F 0 / 内 危=high(形A の左が slice・形F) 1
## 形の名: A 包含 in(右が str 定数)/ B 等価 ==,!= と '' / C 既定落ち x or 定数 / D 真偽 if x, if not x(裸)/ E 三項 … if m else 定数 / F startswith|endswith('')
## ★陽性対照 fixture/pos.py★ 形別 拾つた数 {'A': 1, 'B': 1, 'C': 1, 'D': 2, 'E': 1, 'F': 1} → ★悉く拾つた★ / ★陰性対照 fixture/neg.py★ 形別 {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0, 'F': 0} → ★一つも拾はず★
## 零の札: 陽性対照 通 / 根と深さ 上記 / rc 0 / 刻 上記
## file 別(束 / 種 / file / 箇所):

## 2. ㋑ 門の基点 三態(30)―― 四臺帳 × 態 3 × cwd 2 = 24 走(argv = [臺帳, 臺帳]・條①で判ず)
| 臺帳 | 形 | 基点 | cwd | 門rc | 條① | 母數 | 一致 | 相違 | 実体無 | 読めぬ | 基点の札 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| km-47 | 舊形(repo根相対) | unset | repo | 0 | 通 | 22 | 22 | 0 | 0 | 0 | 既定(器の在處から導いた repo 根・cwd に依 |
| km-47 | 舊形(repo根相対) | unset | taba | 0 | 通 | 22 | 22 | 0 | 0 | 0 | 既定(器の在處から導いた repo 根・cwd に依 |
| km-47 | 舊形(repo根相対) | kuu | repo | 0 | 通 | 22 | 22 | 0 | 0 | 0 | ★引数 明示★(KM_GATE_MANIFEST_B |
| km-47 | 舊形(repo根相対) | kuu | taba | 1 | 落 | 22 | 0 | 0 | 22 | 0 | ★引数 明示★(KM_GATE_MANIFEST_B |
| km-47 | 舊形(repo根相対) | dot | repo | 0 | 通 | 22 | 22 | 0 | 0 | 0 | ★引数 明示★(KM_GATE_MANIFEST_B |
| km-47 | 舊形(repo根相対) | dot | taba | 1 | 落 | 22 | 0 | 0 | 22 | 0 | ★引数 明示★(KM_GATE_MANIFEST_B |
| km-50 | 舊形(repo根相対) | unset | repo | 0 | 通 | 39 | 39 | 0 | 0 | 0 | 既定(器の在處から導いた repo 根・cwd に依 |
| km-50 | 舊形(repo根相対) | unset | taba | 0 | 通 | 39 | 39 | 0 | 0 | 0 | 既定(器の在處から導いた repo 根・cwd に依 |
| km-50 | 舊形(repo根相対) | kuu | repo | 0 | 通 | 39 | 39 | 0 | 0 | 0 | ★引数 明示★(KM_GATE_MANIFEST_B |
| km-50 | 舊形(repo根相対) | kuu | taba | 1 | 落 | 39 | 0 | 0 | 39 | 0 | ★引数 明示★(KM_GATE_MANIFEST_B |
| km-50 | 舊形(repo根相対) | dot | repo | 0 | 通 | 39 | 39 | 0 | 0 | 0 | ★引数 明示★(KM_GATE_MANIFEST_B |
| km-50 | 舊形(repo根相対) | dot | taba | 1 | 落 | 39 | 0 | 0 | 39 | 0 | ★引数 明示★(KM_GATE_MANIFEST_B |
| km-70 | 束内相対 | unset | repo | 1 | 落 | 139 | 0 | 0 | 139 | 0 | 既定(器の在處から導いた repo 根・cwd に依 |
| km-70 | 束内相対 | unset | taba | 1 | 落 | 139 | 0 | 0 | 139 | 0 | 既定(器の在處から導いた repo 根・cwd に依 |
| km-70 | 束内相対 | kuu | repo | 1 | 落 | 139 | 0 | 0 | 139 | 0 | ★引数 明示★(KM_GATE_MANIFEST_B |
| km-70 | 束内相対 | kuu | taba | 0 | 通 | 139 | 139 | 0 | 0 | 0 | ★引数 明示★(KM_GATE_MANIFEST_B |
| km-70 | 束内相対 | dot | repo | 1 | 落 | 139 | 0 | 0 | 139 | 0 | ★引数 明示★(KM_GATE_MANIFEST_B |
| km-70 | 束内相対 | dot | taba | 0 | 通 | 139 | 139 | 0 | 0 | 0 | ★引数 明示★(KM_GATE_MANIFEST_B |
| a1-jishu | 束内相対 | unset | repo | 1 | 落 | 86 | 0 | 0 | 86 | 0 | 既定(器の在處から導いた repo 根・cwd に依 |
| a1-jishu | 束内相対 | unset | taba | 1 | 落 | 86 | 0 | 0 | 86 | 0 | 既定(器の在處から導いた repo 根・cwd に依 |
| a1-jishu | 束内相対 | kuu | repo | 1 | 落 | 86 | 0 | 0 | 86 | 0 | ★引数 明示★(KM_GATE_MANIFEST_B |
| a1-jishu | 束内相対 | kuu | taba | 0 | 通 | 86 | 86 | 0 | 0 | 0 | ★引数 明示★(KM_GATE_MANIFEST_B |
| a1-jishu | 束内相対 | dot | repo | 1 | 落 | 86 | 0 | 0 | 86 | 0 | ★引数 明示★(KM_GATE_MANIFEST_B |
| a1-jishu | 束内相対 | dot | taba | 0 | 通 | 86 | 86 | 0 | 0 | 0 | ★引数 明示★(KM_GATE_MANIFEST_B |
## ★條① 通/落 の数(態別・24 走中 各 8)★: unset: 通 4 落 4 不明 0 / kuu: 通 4 落 4 不明 0 / dot: 通 4 落 4 不明 0
  unset × 舊形(repo根相対) × cwd=repo: 通 2 / 落 0 (母數 2)
  unset × 舊形(repo根相対) × cwd=taba: 通 2 / 落 0 (母數 2)
  unset × 束内相対 × cwd=repo: 通 0 / 落 2 (母數 2)
  unset × 束内相対 × cwd=taba: 通 0 / 落 2 (母數 2)
  kuu × 舊形(repo根相対) × cwd=repo: 通 2 / 落 0 (母數 2)
  kuu × 舊形(repo根相対) × cwd=taba: 通 0 / 落 2 (母數 2)
  kuu × 束内相対 × cwd=repo: 通 0 / 落 2 (母數 2)
  kuu × 束内相対 × cwd=taba: 通 2 / 落 0 (母數 2)
  dot × 舊形(repo根相対) × cwd=repo: 通 2 / 落 0 (母數 2)
  dot × 舊形(repo根相対) × cwd=taba: 通 0 / 落 2 (母數 2)
  dot × 束内相対 × cwd=repo: 通 0 / 落 2 (母數 2)
  dot × 束内相対 × cwd=taba: 通 2 / 落 0 (母數 2)
## cwd で條①が反転した (臺帳, 態) = 8 組 [('km-47', 'kuu'), ('km-47', 'dot'), ('km-50', 'kuu'), ('km-50', 'dot'), ('km-70', 'kuu'), ('km-70', 'dot'), ('a1-jishu', 'kuu'), ('a1-jishu', 'dot')] ―― unset は 0 組が期待(cwd に依らぬ既定)
## 禁域と四束 前⇔後: 門 e11f0d0142549086→e11f0d0142549086 / 照合器 a507c998c7bd6485→a507c998c7bd6485 / 束の印 km-47 cf7365ab4ceb8235(30)→cf7365ab4ceb8235(30) 同 / km-50 3f6ec2665646f716(47)→3f6ec2665646f716(47) 同 / km-70 c063d827d172f2ad(197)→c063d827d172f2ad(197) 同 / a1-jishu b1496aa6613d47ac(118)→b1496aa6613d47ac(118) 同 / 共有器 同

## 3. ㋒ 形と「空文字が通す判定」(40・評価して示す)
| 形 | 名 | 式 | 空文字 '' の出目 | 'A' の出目 | 空文字が通す判定(一行) |
|---|---|---|---|---|---|
| A | 包含 in(右が str 定数) | `s[:1] in 'AM'` | `True` | `True` | 空文字は如何なる文字列にも含まれる('' in x は常に True)∴ 空要素が『A か M』として通る |
| B | 等価 == と '' | `s == ''` | `True` | `False` | 空文字を番兵に使ふ判定は、値の欠と『空といふ値』を見分けぬ(None と '' が別の意味でも同じ枝へ) |
| C | 既定落ち x or 定数 | `s or 'default'` | `'default'` | `'A'` | 空文字は falsy ゆゑ既定へ黙つて落ちる ―― 『空と測れた』が『既定と同じ』に化ける |
| D | 真偽 if x / if not x(裸) | `bool(s)` | `False` | `True` | 空文字は False ―― 『無い』と『空である』が同じ枝へ(0byte と「空である旨の一行」の別が消える) |
| E | 三項 … if m else 定数 | `s if s else '?'` | `'?'` | `'A'` | 空文字は else へ落ち定数(例 '?')に化ける ―― 測れた空が『引けぬ』の顔を着る |
| F | startswith('') / endswith('') | `s.startswith('')` | `True` | `True` | 空文字の接頭辞は全てに合ふ(常に True)∴ 篩が篩でなくなる |
- 現物の 形A・形B・危=high の行(逐語):
  km-70-da / _after/kaki.py / L10 / B / low / lines[-1] == ""
  km-70-da / raw/67_git_add.py / L8 / A / high / l[:1] in 'AM'
  km-70-da / raw/kaki.py / L10 / B / low / lines[-1] == ""
  a1-jishu / raw/67_git_add.py / L9 / A / low / l[0] in 'AM'
  a1-jishu / raw/kaki.py / L10 / B / low / lines[-1] == ""
  km-71-ku / raw/kaki.py / L10 / B / low / lines[-1] == ""

## 4. ㋓ 対照(20)―― 檢出子自身の物・測る路に乗せた
- 陽性 raw/fixture/pos.py: 形 A〜F を一つづつ(D は `if s:` と三項の test の二つが拾はれ 2)。陰性 raw/fixture/neg.py: in の右が tuple / == の相手が非空 / or の右が非定数 / is None / else が非定数 / startswith('A')。
- 出目: 陽性 {'A': 1, 'B': 1, 'C': 1, 'D': 2, 'E': 1, 'F': 1} / 陰性 {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0, 'F': 0}。★陽性が一つでも 0 なら其の形の M は「測れぬ」であつて 0 ではない★ ―― 本弾は六形とも ≥1 ゆゑ M は測れた数。

## 5. ㋔ 塞ぎ方(★紙のみ・据ゑず・裁は家老と上の物★)
### 案① 門の基点の口に乙(env_state)を当てる ―― 現行 逐語(scripts/checks/karo_mac_dasumae_gate.sh sha16 e11f0d0142549086):
```
L193:     #   環境変数 KM_GATE_MANIFEST_BASE が ★set されて居る時のみ★ 渡す
L194:     #   (空文字も「cwd 相対」の明示として通る ―― ${x+set} は空でも set を返す故)。
L195:     #   可逆: 下の if/else を `python3 ... "$man"` の一行へ戻せば旧挙動。
L196:     local vrc
L197:     if [ -n "${KM_GATE_MANIFEST_BASE+set}" ]; then
L198:       python3 "$(dirname "$0")/karo_mac_manifest_verify.py" "$man" "$KM_GATE_MANIFEST_BASE"
L199:       vrc=$?
L200:       say "條① 基点=★引数 明示★(KM_GATE_MANIFEST_BASE)"
L201:     else
```
- 改め(案・diff の形):
```
-    if [ -n "${KM_GATE_MANIFEST_BASE+set}" ]; then
+    case "$(env_state KM_GATE_MANIFEST_BASE)" in
+      empty|blank) say "★條① 基点 KM_GATE_MANIFEST_BASE が空/空白 ―― cwd 相対は許さぬ(明示するなら絶対 path か \".\" を書け)★"; fail=1; vrc=1 ;;
+      value)
       python3 "$(dirname "$0")/karo_mac_manifest_verify.py" "$man" "$KM_GATE_MANIFEST_BASE"
       vrc=$?
-      say "條① 基点=★引数 明示★(KM_GATE_MANIFEST_BASE)"
+      say "條① 基点=★引数 明示★(KM_GATE_MANIFEST_BASE=${KM_GATE_MANIFEST_BASE})" ;;
+      unset)
       (既定の枝は其の儘) ;;
+    esac
```
- 戻し方一行: `git checkout -- scripts/checks/karo_mac_dasumae_gate.sh`(据ゑる前に控 `…bak-<刻>` を取り `cp -p` で戻す)。
- 塞がぬ物: ★"." の明示(正当な cwd 相対)は通る儘★ ―― 之は塞ぐ物ではない(呼ぶ側が字で書いた)。値の中の全角空白(env_state は ASCII の空白類のみ)。verify.py を直に呼ぶ路(案②)。
### 案② verify.py の argv[2] の空を既定へ倒し、札に渡した値を刷る ―― 現行 逐語(sha16 a507c998c7bd6485):
```
L97:     if argv[2:]:
L98:         bases = argv[2:]
L99:         base_src = "引数(明示)"
```
- 改め(案):
```
-    if argv[2:]:
-        bases = argv[2:]
-        base_src = "引数(明示)"
+    if any(b for b in argv[2:]):
+        bases = [b for b in argv[2:] if b]
+        base_src = "引数(明示) %r" % bases
+    elif argv[2:]:
+        print("★基点に空文字が渡された ―― cwd 相対は許さぬ★", file=sys.stderr); return 2
```
- 戻し方一行: `cp -p scripts/checks/karo_mac_manifest_verify.py.bak-<刻> scripts/checks/karo_mac_manifest_verify.py`。
- 塞がぬ物: "." の明示・L146 `if b else p` の形其の物(空を弾いた後は死に枝)・門を経ずに verify を呼ぶ他席の器の期待(rc 2 が新たに出る)。
### 案③ 己の器 ―― km-70 raw/67_git_add.py L8(逐語):
```
L8: staged = [l for l in st if l[:1] in 'AM']; un = [l for l in st if l[:2] in ('??', ' M', 'AM')]
```
- 改め: `staged = [l for l in st if l and l[0] in 'AM']`(自主束・km-71 の 67 は既に此の形)。戻し方一行: km-70 の raw/ は凍結(0444)ゆゑ★改めぬ★ ―― 記録は km-70 _after/66。
- 塞がぬ物: `l[0] in 'AM'` は一字目が 'A' か 'M' の行を数へる ―― porcelain の 'M ' と 'MM' 等を区別せぬ(本弾の的ではない)。形 C/D/E の 260 箇所(設計上の欠扱ひ)は案①〜③の外。

## 6. 便と宣⇔實
- 起 = 着手便 05 の刻 2026-09-17T06:43:34+0900(字数 297・rc 0)。一走目は 315 字で己の門に鳴つた → .first。宣 = 起 + 25 分(器 11 本 × 1.20 分/器(km-70 實)× 1.5 = 20 → 25)。端点 = 納め最終便 5/5 を inbox_write.sh へ渡す直前の date 刻(62 が 63_sent.txt に刷る)。實と符號は 63_sent.txt(紙の後に生れる)。

## 7. 本紙が意味せぬ事
1. M = 266 は疵の数ではない ―― 「長さ 0 の文字列が判定に効き得る箇所」の上界。空が其處へ来るかは来歴で決まり、器は来歴を見ぬ。
2. N = 30 は「己の束(三つ)の .py」であつて「己が書いた器の全て」ではない ―― km-69 以前の束・~/bin・scripts/ は歩いて居らぬ(発注の母數は「己の束(km-70＋自主束)」)。
3. 三態で通/落の数が同じ(各 通 4 落 4)事は「三態が同じ」を意味せぬ ―― 反転の組(0 / 8 / 8)で別れる。数の一致は同一の證ではない。
4. "" が "." と同じ挙動なのは門 sha16 e11f0d0142549086 / 照合器 sha16 a507c998c7bd6485 の版に対して。版が変はれば数も変はる。
5. 案①〜③は据ゑて居らぬ ―― 動くかは測つて居らぬ(紙の上の diff)。裁は家老と上の物。
6. 陰性対照 0 は「檢出子が誤拾せぬ」を六つの似形についてのみ言ふ ―― 他の似形(例 `in` の右が Name で中身が str)は未測。
7. 自主束を「子」と宣したが、其の紙の基点行は自主束の根を指した儘(凍結)―― 本弾へ写して居らぬ。
8. 己の門の数(main/all/nobase)は紙の後に生れる故 本紙には無い ―― _after/60_gate_rcs.txt を見よ。
