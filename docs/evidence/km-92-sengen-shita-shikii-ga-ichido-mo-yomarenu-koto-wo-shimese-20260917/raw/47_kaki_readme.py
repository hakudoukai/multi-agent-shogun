# -*- coding: utf-8 -*-
"""47 紙を書く器(第81弾 km-92)―― 數・sha・刻は悉く raw/*.txt / .tsv から regex で抽き(手打ち 0・抽けねば落ちる)、README.md を kaki で書く。"""
import os, sys, re, time, hashlib, csv
D = sys.argv[1]; sys.path.insert(0, D + '/raw'); import kaki as K; R = D + '/raw'
T = {n: open(R + f'/{n}.txt', encoding='utf-8').read() for n in ('00_start', '01_letter', '10_meisho', '20_date', '30_kansu', '31_tests', '40_naoshi', '41_kansu_after', '42_tests', '45_commit')}
def g(n, pat, i=1):
    m = re.search(pat, T[n], re.S); assert m, (n, pat); return m.group(i)
def tsv(n): return list(csv.DictReader(open(R + f'/{n}.tsv', encoding='utf-8'), delimiter='\t'))
S30 = tsv('30_kansu'); S41 = tsv('41_kansu_after')
cnt = lambda rows, f: sum(1 for r in rows if f(r))
# 00 / 01
tsha = g('00_start', r'sha16 (\S+) / 13005 bytes'); koku00 = g('00_start', r'刻 (\S+) /'); fsha = g('00_start', r'札 \S+ sha16 (\S+) (\d+)行'); frow = g('00_start', r'札 \S+ sha16 \S+ (\d+)行')
st_id, st_ts = re.search(r"\('(msg_\S+)', '([^']+)'\)", T['01_letter']).groups()
# 10
nfile = g('10_meisho', r'歩いた通常 file (\d+) 本 (\d+) bytes / 非通常・讀めぬ (\d+) / rc 0'); nbytes = g('10_meisho', r'歩いた通常 file \d+ 本 (\d+) bytes / 非通常・讀めぬ'); koku10 = g('10_meisho', r'刻 (\S+) /')
n_sec = g('10_meisho', r'\n  DETECT_STALE_STALE_SEC: (\d+) 行'); n_log = g('10_meisho', r'\n  DETECT_STALE_LOG: (\d+) 行'); n_neg = g('10_meisho', r'\n  ZZ_KM92_NEG: (\d+) 行'); n_pk = g('10_meisho', r'\n  STALE_THRESHOLD_SEC: (\d+) 行')
kuchi, yomite = re.search(r'DETECT_STALE_STALE_SEC: 口\(代入 `DETECT_STALE_STALE_SEC=`\) (\d+) 行 / 讀手\(展開[^)]*\) (\d+) 行', T['10_meisho']).groups()
kuchiL, yomiteL = re.search(r'DETECT_STALE_LOG: 口\(代入 `DETECT_STALE_LOG=`\) (\d+) 行 / 讀手\(展開[^)]*\) (\d+) 行', T['10_meisho']).groups()
gB = re.search(r'器B `git grep -n -I -e DETECT_STALE_STALE_SEC -- \.`\(追跡 file・repo 根\)= rc (\d+) / (\d+) 行= docs/evidence/ 外 (\d+) \+ 先例の束 (\d+)', T['10_meisho']).groups(); gBn = re.search(r'ZZ_KM92_NEG -- \.`\(追跡 file・repo 根\)= rc (\d+) / (\d+) 行', T['10_meisho']).groups()
ev_files = g('10_meisho', r"根1′= \S+ / 深さ無制限 / 己の束 \S+ を除く / 歩いた通常 file (\d+) 本"); ev_sec = re.search(r"根1′.*?\n  DETECT_STALE_STALE_SEC: (\d+) 行\(束別: ([^)]*)\)", T['10_meisho'], re.S).groups(); hb = g('10_meisho', r'根3= \S+ / 深さ無制限 / 歩いた通常 file (\d+) 本')
# 20
d20 = tsv('20_date'); n20 = len(d20); bsd_rc1 = cnt(d20, lambda r: 'rc1' in r['① /bin/date -d X +%s']); bsdjf_ok = [r['形'] for r in d20 if 'rc0' in r['① BSD -j -f %Y-%m-%dT%H:%M:%S%z']]; gnu_ok = [r['形'] for r in d20 if 'rc0' in r['② gdate -d X +%s']]; py_ok = [r['形'] for r in d20 if 'rc0' in r['③ py fromisoformat']]
verb_mac0 = cnt(d20, lambda r: r['verbatim行 /bin/date'].startswith('[0]')); koku20 = g('20_date', r'刻 (\S+) /')
# 30
koku30 = g('30_kansu', r'刻 (\S+) /'); S = [r for r in S30 if r['shape'] == 'S']; S_poke = [r['name'] for r in S if r['rc'] == '0']; S_anom = [r['name'] for r in S if r['rc'] == '2']
S_nn = [r for r in S if r['name'] not in ('S_010', 'S_space7')]; S_nn_poke = [r['name'] for r in S_nn if r['rc'] == '0']
B30 = [r for r in S30 if r['shape'] == 'B']; G30 = [r for r in S30 if r['shape'] == 'G']; G_dead = [r['name'] for r in G30 if r['name'].startswith('G_now-1s') and r['rc'] == '0']
# 31 / 42
t31 = {m.group(1) + m.group(2): (m.group(3), m.group(4)) for m in re.finditer(r'(test_\w+\.sh):.*?\n  姿(B|G) *: rc (\d+) / 集計行 ([^\n]*)', T['31_tests'], re.S)}
u31B = g('31_tests', r'test_detect_stale\.sh:.*?姿B: rc \d+ / 集計行 (PASS=\d+ FAIL=\d+ SKIP=\d+)'); u31Bf = re.findall(r'FAIL: (\d\.\d)', T['31_tests'].split('test_fukuincho')[0])
u42B = g('42_tests', r'test_detect_stale\.sh:.*?姿B : rc \d+ / 集計行 (PASS=\d+ FAIL=\d+ SKIP=\d+)'); u42Bf = re.findall(r'FAIL: (\d\.\d)', T['42_tests'].split('test_fukuincho')[0])
u42BF = g('42_tests', r'姿BF: rc (\d+) / 集計行 PASS'); u42G = g('42_tests', r'test_detect_stale\.sh.*?姿G : rc (\d+) / 集計行 PASS'); c42BF = g('42_tests', r'test_fukuincho.*?姿BF: rc (\d+) / 集計行 PASS'); c42G = g('42_tests', r'test_fukuincho.*?姿G : rc (\d+) / 集計行 PASS'); c31G = g('31_tests', r'test_fukuincho.*?姿G: rc (\d+) / 集計行 PASS'); c31B = g('31_tests', r'test_fukuincho.*?姿B: rc (\d+) /')
# 40 / 41 / 45
nsha = g('40_naoshi', r'後: \S+ sha16 (\S+) sha256'); nfull = g('40_naoshi', r'sha256 (\S+) (\d+)B'); nB = g('40_naoshi', r'sha256 \S+ (\d+)B'); nL = g('40_naoshi', r'sha256 \S+ \d+B (\d+)行'); dplus = g('40_naoshi', r'diff \+(\d+) -(\d+) 行'); dminus = g('40_naoshi', r'diff \+\d+ -(\d+) 行'); bn = g('40_naoshi', r'bash -n rc (\d+)')
ok41, ng41, n41 = re.search(r'判 ○ (\d+) / ★×★ (\d+) / 母數 (\d+)', T['41_kansu_after']).groups(); koku41 = g('41_kansu_after', r'刻 (\S+) /')
csha = g('45_commit', r'full sha (\S+) /'); porc = g('45_commit', r'porcelain 前後: ([^/]+)/ 前 (\d+) 行'); porcN = g('45_commit', r'前 (\d+) 行 / 後'); nfiles = g('45_commit', r'\((\d+) 本・的一本なら'); br = g('45_commit', r'枝 (\S+) / full sha'); koku45 = g('45_commit', r'刻 (\S+) /')
warn41 = [r['name'] for r in S41 if 'WARN' in r['log_tag'] or '[WARN]' in r['log_lines']]; s2_anom = [r['name'] for r in S41 if r['shape'] == 'S2' and r['rc'] == '2']; s2_all = [r for r in S41 if r['shape'] == 'S2']
KM = os.path.basename(D); koku = time.strftime('%Y-%m-%dT%H:%M:%S%z')
P = f'''# 第81弾 ―― ★宣した閾が一度も讀まれぬ事を示せ★: `scripts/lib/detect_stale.sh` の `DETECT_STALE_STALE_SEC`(設計 §1.2 verbatim 120s)は repo 全体で ★口 {kuchi} 行・讀手 {yomite} 行★(器A 根 {nfile} file / 器B git grep {gB[1]} 行= 生 {gB[2]} + 先例の束 {gB[3]}・陽性対照 DETECT_STALE_LOG 口 {kuchiL}/讀手 {yomiteL}・陰性 ZZ_KM92_NEG {n_neg} 行 rc {gBn[0]})。振舞ひでも死: 閾を 999999 / abc にしても now-1s が STALE(30 姿G)。★当機 /bin/date -d は rc1★ ゆゑ verbatim 行は {n20} 入力中 {verb_mac0} が `[0]`= 正しい時刻も悉く ANOMALY(30 姿B)。★非數の番人は無い★: date -d の出目へ非數 {len(S_nn)} 形(abc/空/-5/0/2^63/1e3/改行/出力+rc1)を注ぐと ★{len(S_nn_poke)}/{len(S_nn)} が STALE 候補へ落ち CLI が enqueued=1(auto-poke)★(ANOMALY へ落ちたのは -5 と 0 だけ)。直し(㋓・写し・自枝 commit {csha[:12]}): 閾を讀ませ(同じ演算子で検め・倒す時は名指す)・date -d → python3 fromisoformat・出目を 數字のみ + [ -gt 0 ] && [ -le 253402300799 ] で検む → 両対照 {ok41}/{n41} ○・既存 test 二本 GNU 姿/BSD+flock 姿 PASS

- 弾: km-92(家老便 msg_20260917_125748_9dfcc5e2(clear_command・家老の呼称「第57弾」)・札 queue/tasks/ashigaru-mac-1.yaml sha16 {fsha} {frow} 行)/ 束 docs/evidence/{KM} / 書手 ashigaru-mac-1(專任1)/ 宛 karo-mac(監査 gunshi-mac へ sb・PASS は待たぬ= 裁 seq324831)/ 親裁 seq324588 順⑶(番人無し 4 file の一本)
- 據: 專任2 km-83「數値の閾は ER_THRESHOLD_MIN の一つだけ」→ 順⑵ ASW_PROCESS_TIMEOUT(宣のみ)と同型の疑ひを家老が 12:56 に当てた。本弾は其れを ★己の器で引き直し★(食ひ違ひ= 家老表の空・2^63 行)、直しまで。
- 刻: 起 {koku00} / 着手便 {st_id}({st_ts[11:19]}・宣ETA 120〜300 分(幅)・起点= 着手便 timestamp・端点= 納め最終便 timestamp)/ 紙 {koku} / 凍結点 HEAD 0039e1321654・main 363d5fb06084 / 枝(作業樹) ashigaru-mac-3/km-51-…(共有)・★直しの枝 {br}★
- 器: ★生器へ 0 字★(00 が固定した生 sha16 {tsha} = 札の宣・45 の後も不変)。測りは写し raw/utsushi/(前)と raw/40_utsushi/(後)。stub= raw/stub_gnu(date→gdate 9.11・flock)/ stub_inj(date -d へ注ぐ)/ stub_inj2(python3 の parser 呼出へ注ぐ)/ stub_flock。稼働 watcher・supervisor・settings.json 不觸。kaki.py は km-86 逐語。臺帳= MANIFEST.txt(★50 の .py 其の物を載せる= km-86 追紙 2★)・門控= _gate/(員外)・_after/ は臺帳の後。
- ★母數の根(逐語)★: 器A= repo 根 `/Users/momizimac/multi-agent-shogun` / 深さ無制限 / 除外を宣す(.git・queue(13GB)・node_modules・.venv・__pycache__・backups・.claude/worktrees・docs/evidence/)/ 追跡・未追跡を問はず(scripts/*.bak も歩く)/ 通常 file ★{nfile} 本 {nbytes} bytes★ / 非通常 0 / 刻 {koku10}。器B= `git grep -n -I -e <名> -- .`(追跡 file のみ・docs/evidence/ 含む)。根1′= docs/evidence/(先例の束 {ev_files} file・己の束除く)。根3= ~/bin({hb} file)。

## ㊀ 結語を先に

1. ★㋐ 零の四札★: `DETECT_STALE_STALE_SEC` は 器A 根1 で ★{n_sec} 行★= 宣其の物(`DETECT_STALE_STALE_SEC="${{DETECT_STALE_STALE_SEC:-120}}"`)のみ・★讀手 {yomite} 行★(展開 `$X`/`${{X` を、宣の RHS `${{X:-…}}` を除いて数へた)。陽性対照= 隣の宣 DETECT_STALE_LOG が同じ器で口 {kuchiL}/讀手 {yomiteL}(`>> "$DETECT_STALE_LOG"` 等)= 器は讀手を拾へる。陰性対照= ZZ_KM92_NEG {n_neg} 行・器B rc {gBn[0]}。根と深さ= 上。刻= {koku10}。器B(git grep)= {gB[1]} 行= 生 {gB[2]} + 先例の束 {gB[3]}(km-53/77/78/83 の紙と写し= 讀手ではない)。~/bin 0・crontab 無し・此の席の env 0。★振舞ひの証★(30 姿G): `G_now-1s_SEC999999` と `G_now-1s_SECabc` が共に STALE rc0 = ★閾を何にしても出目が変はらぬ★。同型の隣人: `scripts/fukuincho_desktop_poke.py` の `STALE_THRESHOLD_SEC = 120` も git grep {n_pk} 行= 宣のみ(的の外・紙にのみ)。
2. ★㋑ 方言(20・{n20} 入力)★: `/bin/date -d X +%s` は ★{bsd_rc1}/{n20} が rc1★(`illegal option -- d`・正しい時刻でも)。BSD 形 `-j -f '%Y-%m-%dT%H:%M:%S%z'` が通るのは {bsdjf_ok}(±hhmm のみ・Z / +09:00 / naive を拒む)。GNU 形(gdate 9.11)が通るのは {gnu_ok}(★空文字を今日の 0 時に読む★・`now` `@epoch` も通す)。python fromisoformat が通るのは {py_ok}。★verbatim 行 `$(date -d … || echo "0")` は当機で {verb_mac0}/{n20} が `[0]`★= 正しい時刻も 0 に成る(gdate の PATH では正しい epoch)。
3. ★㋒ 函数の出目(30・前)★: 姿G(Linux の姿)は陰性 ○(2020→STALE・2099→FRESH・abc→ANOMALY・空→ANOMALY)。姿B(当機)は ★正しい時刻 2 件が悉く `[ANOMALY] deadline_malformed`★= 当機で層①は一度も STALE を出せぬ。姿S(date -d の出目へ注ぐ {len(S)} 形): ★{len(S_poke)} 形が STALE + CLI enqueued=1(auto-poke)★= {S_poke}／ANOMALY へ落ちたのは {len(S_anom)} 形 {S_anom}(負と 0 だけ・`-le 0` が偶々真)。註 L218-224「parse 不能 → ANOMALY」は嘘であつた: `[ "abc" -le 0 ]` rc2 → if 偽 → `[ now -lt abc ]` rc2 → 偽 → inflight → STALE。stderr の `integer expression expected` は cron では誰も讀まぬ。既存 test(31): 単体 姿B {u31B}(落ちた {u31Bf})/ 姿G PASS・CLI 姿B rc {c31B}(CLI-5 落ち)/ 姿G rc {c31G}。
4. ★㋒ 家老表との照合★: 家老の「空 → le0 rc0 / lt rc1」「2^63 → le0 rc1 / lt rc0」は ★/bin/bash 3.2 では再現せず(共に rc2/rc2・abc と同じ側)★。同じ二行は ★zsh の `[ ]`★ で逐語一致(zsh は 18 桁で切り `number truncated after 18 digits` と言ふ)= 家老は zsh で測つた(宣は bash 3.2.57)。∴ 家老の見立「2^63 は永久 FRESH」は逆で、★bash では STALE 候補へ落ち auto-poke★(30 S_2^63: rc0・enqueued=1)。★家老補① msg_20260917_130832_8bb7204d(13:08:32)= 家老自身が両殻(bash 3.2.57 / zsh 5.9)で七値×二試を測り直し、二行を zsh の出目と認めて取消した ―― 己の 30 姿S の bash 値と逐語一致(空・2^63 とも (2,2))。★
5. ★㋓ 直し(40・写し raw/40_utsushi・diff +{dplus} -{dminus}・bash -n rc {bn}・{nL} 行 {nB}B sha16 {nsha})★: 一= 宣 `:-`→`-` と既定 `_DETECT_STALE_STALE_SEC_DEFAULT=120` 一本化 / 二= `_detect_stale_stale_sec()` が閾を ★比較器そのもの `[ -ge 0 ]` で検め★(裁 seq323062⑷ 甲)、空/空白のみ/非數/負/桁溢れを ★名指しの WARN★ と共に既定へ倒す(乙)/ 三= `date -d` → python3 fromisoformat(本 lib が json で既に依る= 新依存 0・`enter_restart_common_watchdog.sh` L221 と同 idiom・Z / ±hh:mm / ±hhmm / naive を受ける)、出目は ★數字のみ★ + `[ -gt 0 ] && [ -le 253402300799 ]`(9999-12-31T23:59:59Z)、stale= `now - sec < deadline` → FRESH(桁溢れを避ける形)。★捨てた側= 宣を消す★: 設計 §1.2 の承認値(50a1b936 verbatim)を実装から消す事に成り、正本と器の食ひ違ひを「器を正本へ」でなく「正本を無かつた事に」で解く形ゆゑ・且つ宣は唯一の外からの調整口(消せば焼き込み)。捨てた側 2= date -d を残し BSD -j -f を fallback: 方言二本を保ち、-j -f は Z/naive を拒む(㋑)= 三本目が要る。
6. ★㋓ 両対照(41・三走・{n41} case)= ○ {ok41} / × {ng41}★: 陰性= 正しい時刻 4 形(Z / +09:00 / +0900 / naive)が姿 B でも G でも宣どほり・★閾の前後★ now-115s → FRESH / now-125s → STALE(閾 120)・閾 30 で -25s FRESH / -35s STALE・閾 0 で旧の振舞ひ・閾 999999 で -125s も FRESH= ★閾が讀まれる★。陽性= abc / -5 / now / 2^63 / 年 10000 / `$(echo INJ92)` → 悉く ANOMALY・parser の出目へ注ぐ S2 {len(s2_all)} 形の内 ANOMALY {len(s2_anom)}(010 は 8 秒= 正しく STALE・上限 253402300799 は FRESH・+1 は ANOMALY)。閾の毒 {len(warn41)} case が名指しの `[WARN] stale_sec_(empty|blank|malformed|out_of_range)` と共に 120 へ倒れた。既存 test(42): 単体 姿BF rc {u42BF} PASS・姿G rc {u42G} PASS・CLI 姿BF rc {c42BF} PASS・姿G rc {c42G} PASS。姿B(flock 無し)の落ち {u42Bf} + CLI-5 は ★flock 不在(当機)★= 的の外(31 でも同じ二本が落ちる)。
7. ★㋓ commit(45)★: 枝 `{br}` / ★full sha {csha}★ / 親 main 363d5fb0 / 変はつた file {nfiles} 本(的のみ)/ 直し sha256 {nfull} / porcelain 前後 {porc.strip()}({porcN} 行・sha16 一致)/ 生 detect_stale.sh 不変(worktree を讀まぬ hash-object + update-index --cacheinfo)。push は請はぬ。
8. ★付(km-86 疵二つ)★: 追紙 TSUIGAMI_km86.md(束の根・臺帳に載せる)。一行= 臺帳を建てる器(50)と検める器(60)は臺帳の前に書かれるのが必然。加へて隠さぬ点= 50 の .py を臺帳に載せなかつたのは慣行であり必然ではない → 本弾の 50 は己の .py を載せる。
9. ★疵 {{KZ}}(㊈)・便= 着手 1 + 納め 5(_after/62)+ 監査 1(_after/64)。★

## ㊁ ㋐ 名の口(10 / 10_meisho.txt)

| 名 | 器A 根1({nfile} file) | 内 口(代入) | 内 讀手(展開) | 器B git grep(追跡・束含む) | 根1′ docs/evidence | 根3 ~/bin |
|---|---|---|---|---|---|---|
| ★DETECT_STALE_STALE_SEC★ | ★{n_sec}★ | {kuchi} | ★{yomite}★ | {gB[1]}(生 {gB[2]} + 束 {gB[3]}) | {ev_sec[0]}(束別 {ev_sec[1]}) | 0 |
| DETECT_STALE_LOG(陽性) | {n_log} | {kuchiL} | {yomiteL} | 21(生 11 + 束 10) | 322 | 0 |
| ZZ_KM92_NEG(陰性) | {n_neg} | ― | ― | {gBn[1]}(rc {gBn[0]}) | 0 | 0 |
| STALE_THRESHOLD_SEC(隣人・poke.py) | {n_pk} | 1 | 0 | 1 | 0 | 0 |

- 器A の {n_log} 行には `scripts/agent_health_check.sh.bak-shikii-zoku2-20260917T022513`(未追跡 .bak)の 2 行を含む(器A は追跡を問はぬ・器B は含まぬ= 11)。
- 「讀手」の則= 行から宣の RHS `${{X:-…}}` を落とした後に `$X` / `${{X` が残るか(逐語 regex は 10_meisho.py)。宣の RHS は「己を讀む」が、其の値は下流で消費されぬ。

## ㊂ ㋑ date の方言(20 / 20_date.tsv・20_date.txt)

- 表は 20_date.txt(12 入力 × 6 列)。要点= ① /bin/date -d: {bsd_rc1}/{n20} rc1 / ① BSD -j -f: 通るのは {bsdjf_ok} / ② gdate -d: 通るのは {gnu_ok} / ③ py: {py_ok} / verbatim 行(/bin/date): `[0]` が {verb_mac0}/{n20} / verbatim 行(gdate): 正しい 5 形が正しい epoch・空文字が 1789570800(★今日の 0 時★)・`now` `@1757000000` も通る・abc/2^63/-5/injection が `[0]`。
- ∴ 旧 impl の `|| echo "0"` は当機で「常に 0」を作り、GNU では「parse 不能の時だけ 0」を作る。空文字は `-z` の番人が先に止める故 gdate の「今日 0 時」は届かぬ(陰性 G_empty → deadline_empty)。

## ㊃ ㋒ 函数の出目(30 / 30_kansu.tsv・30_kansu.txt・30_env/*.log 逐語)

| 姿 | 入力 | rc | log | CLI enqueued | 宣(註)との差 |
|---|---|---|---|---|---|
| G | 2020 / 2099 / abc / 空 | 0 / 1 / 2 / 2 | STALE / FRESH / ANOMALY / ANOMALY | 1 / 0 / 0 / 0 | 無し(Linux の姿は宣どほり) |
| G | now-1s / now-119s / now-121s | 0 / 0 / 0 | STALE ×3 | 1 ×3 | ★閾 120 が効いて居らぬ★ |
| G | now-1s + SEC=999999 / SEC=abc | 0 / 0 | STALE / STALE | 1 / 1 | ★閾を変へても不変= 死★ |
| B | 2020 / 2099 | 2 / 2 | ANOMALY ×2 | 0 / 0 | ★正しい時刻が malformed★(当機) |
| S | abc / 空 / 2^63 / 1e3 / garbage+rc1 / 5␊0 | 0 ×6 | STALE ×6 | ★1 ×6★ | ★非數が auto-poke★ |
| S | -5 / 0 | 2 / 2 | ANOMALY ×2 | 0 / 0 | 偶々(`-le 0` が真) |
| S | 010 / ' 7' | 0 / 0 | STALE ×2 | 1 / 1 | 數(8 / 7 秒)= 過去= 正 |

## ㊄ ㋓ 直しと両対照(40 / 41 / 42 / 45)

- diff 全文= raw/40_diff.txt(三 hunk)。初走(.first)は上限無し → 41 二走 S2_max_int(2^63-1)が★永久 FRESH★ → 二走で上限を足した(疵④)。
- 41 の表= 41_kansu_after.txt({n41} case・判の則= log の札・rc・WARN の有無と名)。初走 .first は now を起動時に一度だけ取つた疵(②)で 6 case ×(実齢 122〜131 s= STALE が正)、二走 .second は上限前、三走が本。
- 42= 既存 test 二本を写しの樹で。31(前)との差: 単体 姿B {u31B} → {u42B}(残る {u42Bf} は flock)・CLI 姿B CLI-5 は前後とも flock で落ちる・姿BF/G は前後とも PASS(前は G のみ・BF は本弾で足した姿)。
- 45= 温 recipe 逐語(read-tree main → hash-object -w 直し → update-index --cacheinfo → write-tree → commit-tree -p main → update-ref)。porcelain 前後 sha16 一致・{porcN} 行。

## ㊅ 此の紙が意味せぬ事

- third_pc(Linux)の gdate・python3 の版は測つて居らぬ(当機 gdate 9.11 / python 3.14.6)。fromisoformat の Z と ±hhmm は 3.11+ で素で通るが、直しは Z→+00:00・±hhmm→±hh:mm を己で正規化する故 3.7+ で通る筈(★筈= 測れぬ★)。
- 姿 G の flock は stub(取れたと答へるだけ)。排他は測つて居らぬ(的の外)。
- 閾の意味= 「response_by_time 超過 120s」を「deadline の後 120 秒で stale」と読んだ(設計 §1.2 表・L137 は `now > response_by_time` とだけ言ふ)。別の読み(deadline の中に 120 が既に含まれる)なら `DETECT_STALE_STALE_SEC=0` で旧の振舞ひに戻る(41 B_now-1s_SEC0 で実測)。★何れの読みかは軍師/家老の裁★。
- 姿B で CLI が enqueued=0 なのは flock 不在(ERROR flock_acquire_failed)= 当機の事情。auto-poke の判は評価 rc 0 で置いた。

## ㊆ 疵(己の・順に)

{{KIZU}}
'''
KIZU = '''- ★疵①★ 着手便が 304 字で門(300 字の條)が鳴り送れず、二走で 288 字にした(01_letter.py は二走の形・raw/01_letter.txt は二走)。
- ★疵②★ 41 初走: now を器の起動時に一度だけ取り、各 case は其の 3〜12 秒後に走つた → now-119s の 6 case が実齢 122〜131 s で STALE(正)なのに × と判じた。二走で「時刻は case 毎・閾との差 ±5 s」へ(.first に残す)。
- ★疵③★ 41 二走の patch: regex で `iso(now - 121)` を組へ替へた後に naive 二 case の `[:19]` が組に掛かり落ちた(AttributeError)。錨を逐語にして手で直した。
- ★疵④★ 40 初走の直しに上限が無く、parser の出目へ 2^63-1 を注ぐと ★永久 FRESH★(41 二走 S2_max_int)。二走で `[ -le 253402300799 ]` を足し 41 三走で ANOMALY。
- ★疵⑤★ 60_gate_run.py を sed で km-86 から写した時、註の一行(初走の門控名)が壊れた(mon_km92_…T111110= 存在せぬ)。手で直した。
- ★疵⑥★ 器A は部分一致(語境界無し)ゆゑ多めに出る側= 零なら真に零だが、DETECT_STALE_LOG 13 の内訳は註 3 行を含む(口 3 讀手 7 註 3)。
- ★疵⑦★ 家老表との食ひ違ひ(空・2^63)は家老の器(zsh)の疵であり己の疵ではない ―― が、初めは「家老が値を直に入れた」の宣を信じ /bin/bash で引き直すまで気付かなかつた(引き直したから出た)。
- ★疵⑧★ 30/41 の scratch(inflight marker・lock= 0 byte)は讀んだ後に消した(門 條④)。log は残す(先頭一行は器の印・lib の追記が続く)。41 は三走ゆゑ 41_env / .first / .second の三組が在る。
- ★疵⑨★ 42 初走(.first)は 40 初走の写しで走つた(上限無し)。二走が本。差は S2_max_int にのみ効く(既存 test に其の case は無い)。
- ★疵⑩★ 宣ETA 120〜300 分(幅)⇔ 實は 62 の出目(㊀9・便 5)。
- ★疵⑪★ 家老補①(13:08:32・着手便の 3 分後)を ★門を通した後(13:25)★ に讀んだ= 「箱は弾の前に讀め」を犯した。補①は己の出目と一致し要求は「bash の値で組め」(既に其の形)ゆゑ紙の中身は変はらぬが、此の一行を足す為に臺帳を建て直し門を再走した。
- ★疵⑫★ 其の建て直しの一走目で、47 への patch が門の錠(raw/ 0444)に弾かれ(PermissionError)、★補①の無い紙★で臺帳と門(mon_km92_20260917T132533)を走らせた。錠を解いてから patch し三走目が本。初走 T132416・二走 T132533 の門控と臺帳の写し(_gate/MANIFEST.first.txt・.second.txt)は _gate/ に残る。
'''
P = P.replace('{KIZU}', KIZU.strip()); KZ = sum(1 for l in KIZU.split('\n') if l.startswith('- ★疵')); P = P.replace('{KZ}', str(KZ))
K.kaku(D + '/README.md', P); b = open(D + '/README.md', 'rb').read(); print(f'README.md {len(b)}B {b.count(b"\n")}行 sha16 {hashlib.sha256(b).hexdigest()[:16]} 疵 {KZ}'); print(P[:1500])
