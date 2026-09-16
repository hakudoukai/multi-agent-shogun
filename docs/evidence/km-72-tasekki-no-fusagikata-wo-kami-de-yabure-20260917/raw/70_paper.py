# -*- coding: utf-8 -*-
"""紙の器 70(第72弾)―― 数は悉く raw/ の出目 file から regex/TSV で引く(手写し 0)。他席の紙を破る: 專任3 第50弾の diff 7 本を写しへ当て、彼が名指さなんだ穴を 形/rc/裁/注入行/欺き/対照 で並べる。"""
import os, sys, re, csv, time, hashlib, collections
B = sys.argv[1]; D = os.path.dirname(B); E = D + '/raw'; sys.path.insert(0, E); import kaki as K
M = '/Users/momizimac/multi-agent-shogun'; KM = os.path.basename(D)
rd = lambda n: open(f'{E}/{n}', encoding='utf-8').read(); sha16 = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]
def num(pat, txt): m = re.search(pat, txt); assert m, pat; return m.group(1)
T00, T05, T10, T20, T25, T30, T40, T45, T46, T48 = (rd(n) for n in ('00_start.txt', '05_chakushu.txt', '10_utsushi.txt', '20_matrix.txt', '25_timeout.txt', '30_junjo.txt', '40_matome.txt', '45_cut.txt', '46_test.txt', '48_lead_nl.txt'))
rows = list(csv.DictReader(open(E + '/20_matrix.tsv', encoding='utf-8'), delimiter='\t')); r47 = list(csv.DictReader(open(E + '/47_kegare.tsv', encoding='utf-8'), delimiter='\t')); r48 = list(csv.DictReader(open(E + '/48_lead_nl.tsv', encoding='utf-8'), delimiter='\t')); r46 = list(csv.DictReader(open(E + '/46_test.tsv', encoding='utf-8'), delimiter='\t')); r25 = list(csv.DictReader(open(E + '/25_timeout.tsv', encoding='utf-8'), delimiter='\t'))
K20 = int(num(r'路 K = (\d+) 本', T20)); K25 = len(r25) * 2; K30 = 6 * 3 + 2 * 2; K45 = 5 * 2 + 1; K46 = len(r46) * 2; K47 = len(r47); K48 = len(r48) * 2; KT = K20 + K25 + K30 + K45 + K46 + K47 + K48
gate_sha, g4_sha, ver_sha = num(r'門 sha16 ([0-9a-f]{16})', T00), num(r'gate4 sha16 ([0-9a-f]{16})', T00), num(r'照合器 sha16 ([0-9a-f]{16})', T00)
# 40 から
sec = lambda h: T40[T40.index(h):].split('\n## ')[0]
line40 = lambda pat: num(pat, T40)
n_orig = sum(1 for d_, ds_, fs_ in os.walk(E + '/junjo') for f_ in fs_ if f_.endswith('.orig') and not f_.endswith('.rej.orig')); n_rejorig = sum(1 for d_, ds_, fs_ in os.walk(E + '/junjo') for f_ in fs_ if f_.endswith('.rej.orig')); n_rej = sum(1 for d_, ds_, fs_ in os.walk(E + '/junjo') for f_ in fs_ if f_.endswith('.rej'))
bc = {v: sum(1 for r in r47 if r['var'] == v and 'B≠C' in r['判']) for v in ('nama', 'hei', 'gou')}; den = {v: sum(1 for r in r47 if r['var'] == v) for v in ('nama', 'hei', 'gou')}; A = {v: sum(1 for r in r47 if r['var'] == v and r['讀手A_rc≠0∧通句'] == '1') for v in ('nama', 'hei', 'gou')}
n48_tw = sum(1 for r in r48 if int(r['行末空白の行']) > 0); n48_rc1 = sum(1 for r in r48 if r['門票を門に掛けた rc'] == '1'); n48_g4_rc0 = sum(1 for r in r48 if r['gate'] == 'gate4' and r['rc'] == '0' and int(r['行末空白の行']) > 0)
def cellv(gate, var, thr, vid):
    r = next(x for x in rows if (x['gate'], x['var'], x['thr'], x['vid']) == (gate, var, thr, vid)); return r
six = ['v01', 'v02', 'v03', 'v04', 'v05', 'v06']; LAB = {r['vid']: r['label'] for r in rows}
def sai_of(gate, var, thr, vid):
    r = cellv(gate, var, thr, vid); t = r['stderr_esc'].replace('\\n', '\n'); st = [l for l in t.split('\n') if f'閾 {thr}' in l]
    if not st: return f"{r['rc']}/受"
    return f"{r['rc']}/" + ('既定' if '未設定' in st[0] else ('倒:' + ('空文字' if '空文字' in st[0] else '空白のみ' if '空白のみ' in st[0] else '扱へぬ')))
uke = [r for r in rows if r['test_ge0_rc'] == '2' and r['var'] == 'otsu' and r['thr'] == 'DASUMAE_READ_TIMEOUT' and f"閾 DASUMAE_READ_TIMEOUT" not in r['stderr_esc'].replace('\\n', '\n')]
uke_lab = sorted({r['label'] for r in uke})
ge = {r['label']: r['rc_[v -ge 0]'] for r in r46}
ku2 = collections.Counter(r['var'] for r in rows if int(r['ku_n']) >= 2); after = sum(1 for r in rows if int(r['after_ku_lines']) > 0)
L = [
 f'# 第72弾 ―― 他席の塞ぎ方を、紙の上で破れ ―― 專任3 第50弾(枝 a9bb89a)の逐語 diff 7 本を写しへ当て、★彼が名指さなんだ穴★を 形/rc/裁/注入行/讀手の欺き/対照 で数へる ―― ★据ゑず・生器へ 0 字★(門 sha16 {gate_sha} / gate4 sha16 {g4_sha} / 照合器 sha16 {ver_sha} の版)',
 '',
 f'★臺帳の基点(一行)★: 本束の臺帳 `ashigaru-mac-1_{KM}_manifest.txt` の path は ★束の根 `{D}/` からの相對(束内相対・裁 322699)★。照合は門に `KM_GATE_MANIFEST_BASE=<束の根の絶対 path>` を渡せ。"" と "." は渡すな(cwd 相対に成る)。',
 '',
 '## 0. 断(先に)',
 '1. **★丙(safe_show)は、己が塞いだ筈の「札の行割れ」を 41 byte 以上の値で★自ら起こす★。** 因は `cut -c1-40` ―― BSD cut は入力が 40 byte 以上の時 出目の末尾に改行を足す(raw/45: 3/39 byte は足さず・40/41/60 byte は足す)。∴ 札「★閾 X が扱へぬ(「xxxx…」の後で行が切れ、「(生 60 byte)」) ―― 既定へ倒す」が★次の行★へ落ちる。生器では起きなんだ値(x×60)で起きる(raw/47: nama B=C / hei・gou B≠C)。★塞ぎが、塞いだ物と同じ形の疵を、別の値で作つた。★',
 f'2. **乙(tmo_ok)は timeout(1) に値を第一引数で渡す故、★option の語を「受ける」★。** `--help` `--version` は `timeout --help true` が rc 0 で「受」、後段 safe_size で `timeout --help stat …` が help 2783 byte を stdout へ吐き、條⑤が「測れぬ」で落ちる ―― rc 1 だが★門票は file を咎め、閾を咎めぬ★(raw/25・raw/20 v28/v29・raw/47 gou v28 = 11 行)。',
 f'3. **乙の床 1・天 86400 は★整数の綴りにしか効かぬ★。** `0m` `0.0` は timeout 0(時限を掛けぬ)と同じ綴り違ひで受かる(彼の ㋐08「0 を塞いだ」は綴りを変へれば戻る)。`99999d` `1e9` は天を越えて受かる。★`2^63-1` は拒み `2^63` は受ける★(`[` が rc2 で範囲を跳び、timeout が float で受ける)。受けた讀めぬ値(乙・TIMEOUT・[ ] rc2 なのに 受)= {len(uke)} 形: {", ".join(uke_lab)}(raw/40「受けた讀めぬ値」)。',
 f'4. **「\\n5」は 生・甲・丙・合の★悉くが受け★、受ける路(條⑤の行)で生の儘 刷られ、★門票が門自身の條②に落ちる★。** bash 3.2 の `[` は前の改行を許し後の改行を拒む(raw/46: 「\\n5」rc {ge["前 改行"]} / 「5\\n」rc {ge["後 改行"]})。raw/48: 40 走の内 行末空白を持つ門票 {n48_tw} / 其の門票を nama の門に掛けて rc1 {n48_rc1} / gate4 は rc 0 の儘 門票だけが壊れる {n48_g4_rc0}。丙は拒む路の札しか守らぬ(彼の ㋓⑶「別の道で刷る器」の★数へ★= dasumae 2 箇所 L244/L247・gate4 3 箇所 L104/L108/L113・悉く 受ける路)。',
 f'5. **合は三案を順に当てた物ではない ―― 手で織つた別物。** patch で 甲乙丙 を 3! = 6 順に重ねると★二本目から悉く rej★、合と同じ sha に成る順 0/6(gate4 2 順 0/2・raw/30)。∴「合 = 甲∧乙∧丙」は成らず、TIMEOUT では乙が甲を★上書き★し(甲の天 86400 は消え)、札だけ甲の語「範囲外(許 1..86400)」が残る(raw/40 ㋑: 合に一致する単 = otsu のみの組 が 10m/0m/0.0/0.5/1e9/99999d/--help/--version/2^63/0x10)。',
 f'6. **合の呼び口は二つの番人を持つ。** 合x(呼び口の床天を 5..60 に替へた写し)で 1 と 86400 は受かり、拒んだ札は「許 5..60」と刷る(raw/40 合x)。合y(chk を無い名 tmo_okk に替へた写し)は★全値が既定へ倒れ、札は値を咎め、bash の command not found が門票に一行入り、rc 0★。',
 f'7. **甲の札「扱へぬ か 範囲外」は 讀めぬ(rc2)と 範囲外(rc0/1)を分けぬ** ―― 彼自身が拠つた裁 seq322952 乙「分けて名指し」に反する(raw/40 札の語: {line40(r"kou ge0=0: (\d+)")}+{line40(r"kou ge0=1: (\d+)")} 範囲外 ⇔ {line40(r"kou ge0=2: (\d+)")} 讀めぬ が同じ札)。',
 '',
 '## 1. 母數(㋐)',
 f'- {num(r"(★母數★ diff 7 本[^\n]*)", T10)}',
 f'- ★当たる路 K = {KT} 本(実際に走らせた数)★ = 20 行列 {K20}(dasumae 7 形 × 2 閾 × 46 値 + gate4 4 形 × 2 閾 × 46 値)+ 25 timeout {K25}(17 値 × true/sleep)+ 30 順序 {K30}(patch 呼出)+ 45 cut {K45} + 46 `[` {K46}(22 値 × 2 式)+ 47 汚れ {K47} + 48 前の改行 {K48}(40 走 + 門票の検め 40)。',
 f'- 写し七形(nama/甲/乙/丙/合/合x/合y): 甲乙丙合の写しは專任3 の仮器 `.nama/ki_*/` と sha16 が★悉く同★(raw/10・patch offset/fuzz 無)。乙は gate4 に diff 無し(nama の写し)。',
 '- 觀る欄(㋓): rc / 裁(札から: 既定(未設定)・倒・受)/ 注入行(未設定走の行頭 2 字に無い行 = odd・結語の後の行 = after_ku・通句の行数 = ku_n)/ 讀手の欺き(A: rc≠0 なのに通句(專任3 の定義)・B: 閾の★行★に「既定」・C: 門票★全文★に「既定」―― B≠C が「札の割れが行讀みを欺く」)。',
 '',
 '## 2. 彼が名指した三つ(再び言はぬ)と、彼が「未測」と書いた三つの出目',
 '- 名指し済 ―― ⑴ -0 を甲は塞がぬ ⑵ 乙は timeout の無い箱では番人に成らぬ ⑶ 丙は表示を潰すのみ。本紙は之を★数へ直さぬ★(行列には載る: v17/-0 は生・甲・合 とも 鳴1/受 = 彼の表と同)。',
 f'- 彼の ㋕⑶ 未測の三つ: `+0` = 甲 {sai_of("dasumae","kou","DASUMAE_MAX_BYTES","v16")} / 合 {sai_of("dasumae","gou","DASUMAE_MAX_BYTES","v16")}(MAX_BYTES・受けて 0 と讀む → 條⑤ 超 = -0 と同じ穴)/ `全角０` = 甲 {sai_of("dasumae","kou","DASUMAE_MAX_BYTES","v20")} / 合 {sai_of("dasumae","gou","DASUMAE_MAX_BYTES","v20")} / `0x10` = 甲 {sai_of("dasumae","kou","DASUMAE_MAX_BYTES","v14")} 但し ★乙・合の TIMEOUT は 0x10 を受ける★({sai_of("dasumae","gou","DASUMAE_READ_TIMEOUT","v14")}・timeout が 16 と讀む・raw/25 未載 ∴ 秒数は言はぬ)。',
 '',
 '## 3. 新たに破れた形(彼が名指さなんだ穴)―― 形 / rc / 裁 / 注入行 / 欺き / 対照',
 '| # | 形 | 族 | 値 | rc | 裁 | 注入行 | 讀手の欺き | 陽性対照 | 陰性対照 | 根 |',
 '|---|---|---|---|---|---|---|---|---|---|---|',
 f'| 3-1 | ★丙の cut が札を割る★ | 丙 | x×60(60 byte)・v42/v43(43+ byte) | 0(清)/1(汚) | 倒(札割れ+1行) | 1(札の残りが次の行) | B≠C: hei {bc["hei"]}/{den["hei"]}・gou {bc["gou"]}/{den["gou"]}(nama {bc["nama"]}/{den["nama"]}・x×60 は B=C) | raw/45 40/41/60 byte で LF 足す | raw/45 3/39 byte は足さず | 45・47 |',
 f'| 3-2 | ★option 語を番人が受ける★ | 乙 | --help / --version | 1 | 受(札 無) | +2〜5(help 本文が條⑤の「出目」へ) | 門票は file を咎める(「測れぬ」)・閾を咎めぬ | raw/25 true_rc 0・stdout 2783/307 byte・sleep 2 が 0.0 秒 | -v は timeout が拒む(rc125) | 25・20・47 |',
 f'| 3-3 | ★綴りで床天を跳ぶ★ | 乙 | 0m / 0.0 / 99999d / 1e9 / 2^63 | 0 | 受 | 0 | 天 86400 が在ると讀む者を欺く(86401 は拒み 2^63 は受ける) | raw/25 0m・0.0 = sleep 2 走り切り | 86401 は倒・1 は受 | 25・20 |',
 f'| 3-4 | ★前の改行 → 受ける路 → 門票が門に落ちる★ | 甲(と生・丙・合) | \\n5 / \\n\\n\\n5 / \\x20\\n5 | 1(dasumae)/0(gate4) | 受 | 空行 1〜3 + 行末空白 1 | rc 0 の門票が條②に落ちる(gate4) | raw/48 {n48_rc1}/40 が門に落ちた | \\t1000 は行を切らず(門 rc 0) | 46・48 |',
 f'| 3-5 | ★合は順に当てた物でない★ | 合 | patch の順 6+2 | ― | ― | ― | 「三案一度に」は「三案を重ねた」ではない | raw/30 二本目から rej・同 sha 0/8 | 一本目は悉く rc0 | 30 |',
 f'| 3-6 | ★二つの番人・呼び口の誤字★ | 合 | 合x: 1 / 86400 ・ 合y: 全値 | 0 | 合x 受 ・ 合y 倒 | 合y: bash error 1 行 | 合x 札「許 5..60」⇔ 受けた 1・86400 / 合y 札は値を咎める | raw/40 合x 5 値受 / 合y 全値 倒 | 合(誤字無)は 5 を受 | 40 |',
 f'| 3-7 | ★札が因を分けぬ★ | 甲 | abc / -1 / 2^63-1 | 0 | 倒 | 0 | 同じ語「扱へぬ か 範囲外」 | raw/40 讀めぬ {line40(r"kou ge0=2: (\d+)")} ⇔ 範囲外 {int(line40(r"kou ge0=0: (\d+)")) + int(line40(r"kou ge0=1: (\d+)"))} | 生器の札は「扱へぬ」のみで嘘は無い | 40 |',
 '',
 '### 3-1 の逐語(raw/45)',
 '```', *[l for l in T45.split('\n') if l and not l.startswith('##')][:7], '```',
 '### 3-2 の逐語(raw/25・--help)', '```', *[l for l in T25.split('\n') if l.startswith("'--help'") or l.startswith("'--version'") or l.startswith("'0m'") or l.startswith("'99999d'") or l.startswith("'-v'")], '```',
 '### 3-4 の逐語(raw/48・dasumae nama \\n5 と gate4 gou \\n\\n\\n5)', '```', *[l for l in T48.split('\n') if l.startswith('dasumae\tnama\tn1\t') or l.startswith('gate4\tgou\tn3\t')], '```',
 '',
 '## 4. ㋑ 合 vs 単',
 '```', *[l for l in T30.split('\n') if l.startswith('★')], *[l.strip() for l in sec('## ㋑ 単 vs 合').split('\n') if l.strip().startswith(('DASUMAE', 'GATE4')) and ': 値 46 の内' in l], '```',
 '- ★順序★: どの順でも二本目の patch が rej(同じ行 `local name=…` を三案が別々に書き換へる故)。合は手で織つた物であり、合の振舞ひは単の和ではない。',
 '- ★上書き★: TIMEOUT で合と一致する単が乙のみの組 = 乙が甲を消した組(10m/0m/0.0/0.5/1e9/99999d/--help/--version/2^63/0x10)。甲の床天は乙の `if [ -ge 0 ]` の中でしか効かず、讀めぬ綴りは範囲を跳ぶ。',
 '- ★同じ値が二つの番人に当たる形★: 合の呼び口 `tmo_ok 1 86400` は tmo_ok が $2 $3 を讀まぬ故 二重に書かれた床天であり、片方を変へれば札が嘘を刷る(合x)。',
 '',
 '## 5. ㋒ 第71弾の六形を甲乙丙の閾へ(rc/裁・dasumae MAX_BYTES / TIMEOUT・gate4 FILE_MB)',
 '| 形 | 生 MAX_BYTES | 甲 | 丙 | 合 | 生 TIMEOUT | 乙 | 合 | gate4 生 | 甲 | 合 |', '|---|---|---|---|---|---|---|---|---|---|---|',
 *[f"| {LAB[v]} | {sai_of('dasumae','nama','DASUMAE_MAX_BYTES',v)} | {sai_of('dasumae','kou','DASUMAE_MAX_BYTES',v)} | {sai_of('dasumae','hei','DASUMAE_MAX_BYTES',v)} | {sai_of('dasumae','gou','DASUMAE_MAX_BYTES',v)} | {sai_of('dasumae','nama','DASUMAE_READ_TIMEOUT',v)} | {sai_of('dasumae','otsu','DASUMAE_READ_TIMEOUT',v)} | {sai_of('dasumae','gou','DASUMAE_READ_TIMEOUT',v)} | {sai_of('gate4','nama','GATE4_MAX_FILE_MB',v)} | {sai_of('gate4','kou','GATE4_MAX_FILE_MB',v)} | {sai_of('gate4','gou','GATE4_MAX_FILE_MB',v)} |" for v in six],
 '- 空文字・空白・tab・改行のみ = env_state が「欠」と讀み既定へ(甲乙丙は此處に触れぬ・生と同)。★全角空白・NBSP = 「値」と讀まれ、甲/生/丙/合は「扱へぬ」で倒し、乙も倒す(當箱は timeout 在り)★ ―― 71 の知見「全角空白は値として振舞ふ」は三案の後も変らぬ。丙の札は「???(生 3 byte)」で全角空白と全角０を分てぬ(raw/20 v05/v20 の札が同字)。',
 '',
 '## 6. ㋔ 対照と不動',
 f'- 生器 sha16 前(raw/00)⇔後(_after/60): 60 が刷る(門・gate4・照合器・append)。讀んだ四束(專任3 km-50 二束・km-71・km-71b)の印も 60 が前後で刷る。写しは束内 raw/ki/ のみ。',
 f'- 通句の行数 ≥2(偽の結語が門票に載つた走)= {" / ".join(f"{k} {n}" for k, n in sorted(ku2.items())) or "0"}(v42/v43 × 2 閾・丙と合は 0)。結語の後の行 > 0 = {after}/{K20}(彼の ㋕⑷ の穴は本弾の {K20} 路では現れなんだ ―― 「現れなんだ」は「起き得ぬ」ではない)。',
 '',
 '## 7. 破れなんだ物(六・試した形で数へる)',
 '1. **後ろに改行を付けた数(5\\n・5\\n\\n・\\n5\\n\\n)で受ける路へ改行を入れる** ―― `[` が rc2 で拒む(raw/46)故 破れず(v09/v10 は悉く倒)。前の改行のみが通る(3-4)。',
 '2. **結語の後への注入** ―― 1012 路で 0(§6)。',
 '3. **gate4 の受ける路で rc を動かす** ―― 「\\n5」で門票は壊れたが rc は 0 の儘(3-4)。rc を動かす形は見つけず。',
 '4. **丙の safe_show に 40 byte 未満で改行を足させる** ―― 3/39 byte では足さぬ(raw/45)。',
 '5. **乙で `-v` `-k` の如き短 option を受けさせる** ―― timeout が rc125 で拒む(raw/25 -v)。受かるのは rc 0 で終る `--help` `--version` のみ。',
 '6. **甲(num_in_range)そのものを整数の綴りで跳ぶ** ―― +5/010/-0 は受ける(彼の名指し・讀み違ひは無い)、0x10/全角/2^63 は拒む。甲を「通す」誤りは前の改行(3-4)と符号の外に見つけず。',
 '',
 '## 8. 便と宣⇔實',
 f'- 起 = 着手便 05 の刻 {num(r"刻 (\S+) /", T05)}(字数 {num(r"字数 (\d+)", T05)})。宣 = 4 分(家老指定の式: 新規 6 器 × 0.5 + 写し 9 器 × 0.1 = 3.9 → 4・讀みの刻を含まぬ)。端点 = 納め最終便を inbox_write.sh へ渡す直前の date 刻(62 が 63_sent.txt に刷る)。實・宣−實・器数は 63_sent.txt。★新規の器は 6 でなく 11(07/10/20/25/30/40/45/46/47/48/70)、写しは 9 で建つた ―― 宣の式の「新規 6」が先づ外れた(器の数は焼き込まず数へよ・家老三)。★',
 '',
 '## 9. 本紙が意味せぬ事(限り 六)',
 '1. **「三案が誤り」とは言へぬ。** 甲は -1 を、乙は 「 50 」 を、丙は改行の逐語刷りを、彼の表の通り塞いで居る(本弾の行列でも同じ出目)。本紙が数へたのは★塞ぎが作つた新しい形★と★塞ぎが届かぬ形★である。',
 '2. **「門が直る/壊れる」とは言へぬ。** 据ゑて居らぬ。生器の sha16 は始めから終りまで同(§6)。',
 '3. **3-2/3-3 は当箱の timeout(GNU coreutils 9.11)の振舞ひ。** 他の timeout(BusyBox 等)で同じ數が出るとは言へぬ。3-1 は BSD cut(macOS)の振舞ひ ―― GNU cut では測つて居らぬ。',
 '4. **「\\n5」が env に入る経路が現に在るとは言へぬ。** 本弾は値を其の儘 env に置いた。呼び手が YAML/heredoc から閾を組む時に前の改行が入るかは測つて居らぬ。',
 f'5. **K = {KT} 路は「悉く」ではない。** 値 46 形は席が選んだ物であり、選ばなんだ綴り(例: `1,000` `1_000` `0b101` `٥`)は測つて居らぬ。「測つて居らぬ物を無いと書かぬ」。',
 '6. **B≠C は「行讀みの讀手」を仮定した欺きである。** 門票全文を讀む讀手(C)は欺かれぬ。誰が行で讀むかは本紙の外(己の器 40 は行で讀んで三度誤つた ―― §10)。',
 '',
 '## 10. 疵の申告(己)',
 '1. **bytes 字面に和字を書いて SyntaxError を★二度★(20 と 47)** ―― 己の memory「rb\'第…\' は非ASCIIを拒む」を踏んだ。二度目は一度目の直しを見た後である。直し: fixture の頭は ASCII か .encode()。',
 '2. **40 の裁の讀みを三度直した(.first/.second/.third)** ―― ⑴ eff を札の行から拾つた ⑵ 最初の閾行を裁とした(受けた時に隣の閾の既定札を拾ふ) ⑶ 行で讀んだ故 割れた札を 受 と誤つた。∴ 己の器が §3-1 の欺きに現に掛かつた。裁は門票全文で引く形へ。',
 '3. **25 の一走目は「時限 無し(2 秒 走り切つた)」と書いた** ―― 2 秒の走りでは「無し」と「2 秒より長い」を分てぬ。.first に残し語を直した。',
 '4. **宣 4 分は讀みの刻を含まぬ式** ―― 家老の指定通りに建てたが、他席の紙 378 行と diff 335 行を讀む刻が式に無い。實は 63_sent.txt。',
 f'5. **raw/junjo に patch の副産物が残る: .orig {n_orig} 本(nama の写し・行末空白 無)/ .rej {n_rej} 本と .rej.orig {n_rejorig} 本(diff 断片・★行末空白 有★)** ―― 消さず臺帳に載せ、行末空白を持つ物は門の all 走で 條② に鳴るのが正として宣し、除いた all_kiyoi を併せ置く(_after/60)。專任3 の diff 写し raw/ki/an/*.diff は鳴らぬ(彼が ㋖ で行末空白を削つた diff)。',
 '6. **70 自身が行末空白を一つ持ち 59 で鳴つた**(死んだ行 `kizu = …; ` の後ろ)―― 消して臺帳を建て直した(_manifest.first.txt)。',
]
K.kaku(B + '.md', '\n'.join(L)); print('紙', os.path.getsize(B + '.md'), 'B', sum(1 for _ in open(B + '.md', encoding='utf-8')), '行')
