# -*- coding: utf-8 -*-
"""紙の器 70(第71弾)―― 数は raw/20_bosu.txt・30_mon_santai.txt・40_katachi.txt から引き、㋔の逐語は source の行番号から引く(手写しでない)。紙は臺帳の前に生れる故 己の門の数は書けぬ(期待のみ)。"""
import os, sys, re, time, hashlib
B = sys.argv[1]; D = os.path.dirname(B); E = D + '/raw'; sys.path.insert(0, E); import kaki as K
M = '/Users/momizimac/multi-agent-shogun'; KM = os.path.basename(D); GATE = M + '/scripts/checks/karo_mac_dasumae_gate.sh'; VER = M + '/scripts/checks/karo_mac_manifest_verify.py'; K67 = M + '/docs/evidence/km-70-daichou-no-ne-wo-sokunai-soutai-e-tatenaosu-20260917/raw/67_git_add.py'
rd = lambda p: open(p, encoding='utf-8').read(); num = lambda pat, txt, alt='?': (re.search(pat, txt).group(1) if re.search(pat, txt) else alt); sha16 = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]
T20, T30, T40, T05 = rd(E + '/20_bosu.txt'), rd(E + '/30_mon_santai.txt'), rd(E + '/40_katachi.txt'), rd(E + '/05_chakushu.txt')
def lines_of(p, a, b): L = rd(p).split('\n'); return [f'L{i}: {L[i-1]}' for i in range(a, b + 1)]
N, Ms = num(r'★N\(器・現物\)= (\d+) 本★', T20), num(r'★M\(長さ0の文字列が判定に効き得る箇所・現物\)= (\d+) 箇所★', T20)
t20_tab = [l for l in T20.split('\n') if l.startswith('## ')]; t30_tab = [l for l in T30.split('\n') if l.startswith('|')]; t30_sum = [l for l in T30.split('\n') if l.startswith('## ') or l.startswith('  ')]; t40_tab = [l for l in T40.split('\n') if l.startswith('|')]; t40_pick = [l for l in T40.split('\n') if l.startswith('  ')]
gate_lines = lines_of(GATE, 193, 201); ver_lines = lines_of(VER, 97, 99); k67 = lines_of(K67, 8, 8)
lines = [
 f'# 第71弾 ―― ★空文字は値として振舞ふ ―― 己の器を悉皆せよ★(家老mac 発注 06:40:22・msg_20260917_064022_8608761c)―― 母數 N={N} 器 / M={Ms} 箇所(㋐)・門の基点 三態 24 走で "" は "." と同じ挙動・札だけ「明示」(㋑)・形六つを評価して示し檢出子自身の対照を同じ路に乗せた(㋒㋓)・塞ぎ方は紙のみ(㋔)―― 答を先に(★數の出處 = raw/20_bosu.{{txt,tsv}} / raw/30_mon_santai.{{txt,tsv}} + raw/30_*.{{out,err,rc}} / raw/40_katachi.txt / raw/fixture/{{pos,neg}}.py / raw/05_chakushu*.txt(起・宣)/ _after/60_gate_rcs.txt(門・紙の後に生れる故 紙は其の數を書けぬ)/ _after/63_sent.txt(端点・實)★)',
 '',
 f'★臺帳の基点(一行)★: 本束の臺帳 `ashigaru-mac-1_{KM}_manifest.txt` の path は ★束の根 `{D}/` からの相對(束内相対・裁 322699)★ ―― append.py を cwd = 束の根で呼ぶ故。照合は門に `KM_GATE_MANIFEST_BASE=<束の根の絶対 path>` を渡すか verify.py の第二引数に束の根を渡せ。既定基点(repo 根)で当てれば悉く実体無と出る(基点の違ひ)。★空文字 "" と "." は渡すな ―― 何れも cwd 相対に成る(本紙 §2)★。',
 '',
 '## 0. 断(先に)と親子の宣',
 f'1. **㋐ ★N = {N} 本 / M = {Ms} 箇所★**(現物。自身 1 本 {num(r"自身 (\d+) 箇所", T20)} 箇所・fixture 2 本は別札)。数へ方: 歩き根 = km-70 束・自主束・km-71 束(己)/ 深さ 無限(os.walk・__pycache__ は降りぬ)/ 規約 = S_ISREG かつ .py / 非通常 {num(r"非通常 (\d+)", T20)}・非 .py {num(r"非 \.py (\d+)", T20)} は母數外 / fixture/ は同じ路で歩き現物と分ける / 己は path 一致で「自身」。形別 {num(r"形別 M\(現物\): (.+?) / 内", T20)}・危=high {num(r"危=high\(形A の左が slice・形F\) (\d+)", T20)}(km-70 raw/67_git_add.py L8 `l[:1] in \'AM\'` ―― km-70 _after/66 で既に名指した物)。★M は「効き得る箇所」の上界であつて疵の数ではない★ ―― D/E の多くは欠(None)を扱ふ設計で、空文字が其處へ★来るか★は静的には判ぜぬ(器では決められぬ則は数へ器に堕ちる)。',
 f'2. **㋑ 門の基点 三態(据ゑず・24 走)**: {num(r"條① 通/落 の数\(態別・24 走中 各 8\)★: (.+)", T30)}。★cwd で條①が反転した組 = {num(r"反転した \(臺帳, 態\) = (\d+) 組", T30)}(= "" と "." の四臺帳全部・unset は 0 組)★。∴ ★"" は "." と寸分違はぬ挙動(cwd 相対)で、違ふのは札だけ★ ―― "." は呼ぶ側が字で書いた明示、"" は「何も書いて居らぬ」のに門は `條① 基点=★引数 明示★` を刷る。通/落の数が三態で同じ(各 通 4 落 4)のは ★数だけ見れば三態が同じに見える★ 事の實例 ―― 反転の組で初めて別れる。',
 '3. **㋒ 形六つ**(40 で評価): A 包含 in(`\'\' in \'AM\'` → True)/ B 等価 == \'\'(値の欠と空の値を同じ枝へ)/ C x or 定数(空は黙つて既定へ)/ D 裸の真偽(空は False = 無いと同じ枝)/ E 三項 else 定数(測れた空が『引けぬ』の顔)/ F startswith(\'\')(常に True)。発注の三つ(包含 in / 等価 == / 既定落ち or)を含み六つ。',
 f'4. **㋓ 対照は檢出子 20 自身の路に在る**: raw/fixture/pos.py(各形一つ)と neg.py(似て非なる形)を ★同じ os.walk★ で歩き現物と分けて数へた ―― 陽性 {num(r"形別 拾つた数 (\{[^}]+\})", T20)} → {"悉く拾つた" if "悉く拾つた" in T20 else "★落★"} / 陰性 {"0 → 一つも拾はず" if "一つも拾はず" in T20 else "★誤拾★"}。零の四つの札: 陽性対照 通 / 根と深さ 上記 / rc 0 / 刻 20 の頭。',
 '5. **㋔ 塞ぎ方は紙のみ(§5)** ―― 三つの案に 逐語 diff・戻し方一行・塞がぬ物。共有器へ 0 byte・四束(km-47/50/70・自主束)へ 0 byte(30 の印 前後同)。',
 '6. **親子の宣**: 自主束 `docs/evidence/a1-jishu-kuumoji-kiten-20260917/`(06:34〜06:41・空文字基点 16 走・門 通)は ★本弾の子★ である。動かして居らぬ(凍結済・staged 118)。本弾 30 は其の 16 走を四臺帳 24 走へ広げ、"." を加へて「"" は "." である」を示した。',
 '',
 '## 1. ㋐ 母數(20)―― 数へ方は頭に、数は後に', ] + t20_tab + [
 '',
 '## 2. ㋑ 門の基点 三態(30)―― 四臺帳 × 態 3 × cwd 2 = 24 走(argv = [臺帳, 臺帳]・條①で判ず)', ] + t30_tab + t30_sum + [
 '',
 '## 3. ㋒ 形と「空文字が通す判定」(40・評価して示す)', ] + t40_tab + ['- 現物の 形A・形B・危=high の行(逐語):'] + t40_pick + [
 '',
 '## 4. ㋓ 対照(20)―― 檢出子自身の物・測る路に乗せた',
 '- 陽性 raw/fixture/pos.py: 形 A〜F を一つづつ(D は `if s:` と三項の test の二つが拾はれ 2)。陰性 raw/fixture/neg.py: in の右が tuple / == の相手が非空 / or の右が非定数 / is None / else が非定数 / startswith(\'A\')。',
 f'- 出目: 陽性 {num(r"形別 拾つた数 (\{[^}]+\})", T20)} / 陰性 {num(r"陰性対照 fixture/neg.py★ 形別 (\{[^}]+\})", T20)}。★陽性が一つでも 0 なら其の形の M は「測れぬ」であつて 0 ではない★ ―― 本弾は六形とも ≥1 ゆゑ M は測れた数。',
 '',
 '## 5. ㋔ 塞ぎ方(★紙のみ・据ゑず・裁は家老と上の物★)',
 '### 案① 門の基点の口に乙(env_state)を当てる ―― 現行 逐語(scripts/checks/karo_mac_dasumae_gate.sh sha16 ' + sha16(GATE) + '):', '```'] + gate_lines + ['```',
 '- 改め(案・diff の形):', '```',
 '-    if [ -n "${KM_GATE_MANIFEST_BASE+set}" ]; then',
 '+    case "$(env_state KM_GATE_MANIFEST_BASE)" in',
 '+      empty|blank) say "★條① 基点 KM_GATE_MANIFEST_BASE が空/空白 ―― cwd 相対は許さぬ(明示するなら絶対 path か \\".\\" を書け)★"; fail=1; vrc=1 ;;',
 '+      value)',
 '       python3 "$(dirname "$0")/karo_mac_manifest_verify.py" "$man" "$KM_GATE_MANIFEST_BASE"',
 '       vrc=$?',
 '-      say "條① 基点=★引数 明示★(KM_GATE_MANIFEST_BASE)"',
 '+      say "條① 基点=★引数 明示★(KM_GATE_MANIFEST_BASE=${KM_GATE_MANIFEST_BASE})" ;;',
 '+      unset)',
 '       (既定の枝は其の儘) ;;',
 '+    esac', '```',
 '- 戻し方一行: `git checkout -- scripts/checks/karo_mac_dasumae_gate.sh`(据ゑる前に控 `…bak-<刻>` を取り `cp -p` で戻す)。',
 '- 塞がぬ物: ★"." の明示(正当な cwd 相対)は通る儘★ ―― 之は塞ぐ物ではない(呼ぶ側が字で書いた)。値の中の全角空白(env_state は ASCII の空白類のみ)。verify.py を直に呼ぶ路(案②)。',
 '### 案② verify.py の argv[2] の空を既定へ倒し、札に渡した値を刷る ―― 現行 逐語(sha16 ' + sha16(VER) + '):', '```'] + ver_lines + ['```',
 '- 改め(案):', '```',
 '-    if argv[2:]:',
 '-        bases = argv[2:]',
 '-        base_src = "引数(明示)"',
 '+    if any(b for b in argv[2:]):',
 '+        bases = [b for b in argv[2:] if b]',
 '+        base_src = "引数(明示) %r" % bases',
 '+    elif argv[2:]:',
 '+        print("★基点に空文字が渡された ―― cwd 相対は許さぬ★", file=sys.stderr); return 2', '```',
 '- 戻し方一行: `cp -p scripts/checks/karo_mac_manifest_verify.py.bak-<刻> scripts/checks/karo_mac_manifest_verify.py`。',
 '- 塞がぬ物: "." の明示・L146 `if b else p` の形其の物(空を弾いた後は死に枝)・門を経ずに verify を呼ぶ他席の器の期待(rc 2 が新たに出る)。',
 '### 案③ 己の器 ―― km-70 raw/67_git_add.py L8(逐語):', '```'] + k67 + ['```',
 "- 改め: `staged = [l for l in st if l and l[0] in 'AM']`(自主束・km-71 の 67 は既に此の形)。戻し方一行: km-70 の raw/ は凍結(0444)ゆゑ★改めぬ★ ―― 記録は km-70 _after/66。",
 "- 塞がぬ物: `l[0] in 'AM'` は一字目が 'A' か 'M' の行を数へる ―― porcelain の 'M ' と 'MM' 等を区別せぬ(本弾の的ではない)。形 C/D/E の 260 箇所(設計上の欠扱ひ)は案①〜③の外。",
 '',
 '## 6. 便と宣⇔實',
 f'- 起 = 着手便 05 の刻 {num(r"刻 (\S+) /", T05)}(字数 {num(r"字数 (\d+)", T05)}・rc {num(r"inbox_write rc (\d+)", T05)})。一走目は {num(r"字数 (\d+)", rd(E + "/05_chakushu.first.txt"))} 字で己の門に鳴つた → .first。宣 = 起 + 25 分(器 11 本 × 1.20 分/器(km-70 實)× 1.5 = 20 → 25)。端点 = 納め最終便 5/5 を inbox_write.sh へ渡す直前の date 刻(62 が 63_sent.txt に刷る)。實と符號は 63_sent.txt(紙の後に生れる)。',
 '',
 '## 7. 本紙が意味せぬ事',
 '1. M = 266 は疵の数ではない ―― 「長さ 0 の文字列が判定に効き得る箇所」の上界。空が其處へ来るかは来歴で決まり、器は来歴を見ぬ。',
 '2. N = 30 は「己の束(三つ)の .py」であつて「己が書いた器の全て」ではない ―― km-69 以前の束・~/bin・scripts/ は歩いて居らぬ(発注の母數は「己の束(km-70＋自主束)」)。',
 '3. 三態で通/落の数が同じ(各 通 4 落 4)事は「三態が同じ」を意味せぬ ―― 反転の組(0 / 8 / 8)で別れる。数の一致は同一の證ではない。',
 '4. "" が "." と同じ挙動なのは門 sha16 ' + sha16(GATE) + ' / 照合器 sha16 ' + sha16(VER) + ' の版に対して。版が変はれば数も変はる。',
 '5. 案①〜③は据ゑて居らぬ ―― 動くかは測つて居らぬ(紙の上の diff)。裁は家老と上の物。',
 '6. 陰性対照 0 は「檢出子が誤拾せぬ」を六つの似形についてのみ言ふ ―― 他の似形(例 `in` の右が Name で中身が str)は未測。',
 '7. 自主束を「子」と宣したが、其の紙の基点行は自主束の根を指した儘(凍結)―― 本弾へ写して居らぬ。',
 '8. 己の門の数(main/all/nobase)は紙の後に生れる故 本紙には無い ―― _after/60_gate_rcs.txt を見よ。',
]
K.kaku(B + '.md', '\n'.join(lines)); print('紙', os.path.getsize(B + '.md'), 'B', sum(1 for _ in open(B + '.md', encoding='utf-8')), '行')
