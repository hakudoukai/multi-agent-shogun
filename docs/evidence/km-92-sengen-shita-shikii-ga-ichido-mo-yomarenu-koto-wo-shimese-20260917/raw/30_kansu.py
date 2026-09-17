# -*- coding: utf-8 -*-
"""30 函数の出目(第81弾 km-92 ㋒)―― 写し raw/utsushi/scripts/lib/detect_stale.sh を /bin/bash 3.2 で source し detect_stale_evaluate_row を打つ。deadline_epoch が 非数／空／負／2^63 等の時、★何を返し(rc)・log に何と書き・auto-poke(CLI の enqueue 分岐= rc 0)が起きるか★ を刷る。
三つの姿: B= 当機の /bin/date(BSD)/ G= raw/stub_gnu(date→gdate・flock stub= Linux/third_pc の姿)/ S= raw/stub_inj(date -d が KM92_D_OUT を刷る= deadline_epoch へ字を注ぐ)。
両対照: 陰性(G: 正しい時刻で FRESH/STALE が宣どほり)・陽性(S: 非数で ANOMALY に成らぬ事)。加へて ★宣 DETECT_STALE_STALE_SEC=999999 を与へても出目が変はらぬ★(㋐ の振舞ひの証)。CLI の写しも同じ row で打ち enqueued= を讀む。"""
import os, sys, re, time, subprocess, shutil, datetime
D = sys.argv[1]; sys.path.insert(0, D + '/raw'); import kaki as K
LIB = D + '/raw/utsushi/scripts/lib/detect_stale.sh'; CLI = D + '/raw/utsushi/scripts/fukuincho_detect_stale_cli.sh'; ENV = D + '/raw/30_env'
if len(sys.argv) > 2: LIB, CLI, ENV, TAG = sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]
else: TAG = '30'
os.makedirs(ENV, exist_ok=True)
now = int(time.time()); iso = lambda t: datetime.datetime.fromtimestamp(t).astimezone().isoformat(timespec='seconds')
row = lambda cid, rbt: '{"from":"karo-third","recipient":"fukuincho","type":"auto_poke","status":"pending","correlation_id":"%s","response_by_time":"%s"}' % (cid, rbt)
# (名, 姿, response_by_time, stub の出目, stub rc, 宣(註 L218-224 が言ふ出目), 追加 env)
CASES = [
 ('G_past_2020',     'G', '2020-01-01T00:00:00Z', None, 0, 'STALE rc0', {}),
 ('G_future_2099',   'G', '2099-01-01T00:00:00Z', None, 0, 'FRESH rc1', {}),
 ('G_now-1s',        'G', iso(now - 1),  None, 0, 'STALE rc0(閾 120 が讀まれて居れば FRESH)', {}),
 ('G_now-119s',      'G', iso(now - 119), None, 0, 'STALE rc0(閾 120 が讀まれて居れば FRESH)', {}),
 ('G_now-121s',      'G', iso(now - 121), None, 0, 'STALE rc0', {}),
 ('G_now-1s_SEC999999', 'G', iso(now - 1), None, 0, '宣を 999999 にしても STALE rc0 なら閾は死', {'DETECT_STALE_STALE_SEC': '999999'}),
 ('G_now-1s_SECabc', 'G', iso(now - 1), None, 0, '宣を abc にしても出目不変なら閾は死', {'DETECT_STALE_STALE_SEC': 'abc'}),
 ('G_abc',           'G', 'abc', None, 0, 'ANOMALY rc2(gdate rc1 → 0)', {}),
 ('G_empty',         'G', '', None, 0, 'ANOMALY rc2(deadline_empty・date へ行かぬ)', {}),
 ('B_past_2020',     'B', '2020-01-01T00:00:00Z', None, 0, 'STALE rc0 の筈(当機は date -d rc1 → 0 → ANOMALY)', {}),
 ('B_future_2099',   'B', '2099-01-01T00:00:00Z', None, 0, 'FRESH rc1 の筈(当機は ANOMALY)', {}),
 ('S_abc',           'S', 'x', 'abc', 0, 'ANOMALY rc2(註: parse 不能 → ANOMALY)', {}),
 ('S_empty',         'S', 'x', '', 0, 'ANOMALY rc2', {}),
 ('S_neg5',          'S', 'x', '-5', 0, 'ANOMALY rc2', {}),
 ('S_2^63',          'S', 'x', '9223372036854775808', 0, 'ANOMALY rc2(家老の見立= 永久 FRESH)', {}),
 ('S_010',           'S', 'x', '010', 0, '過去(8 秒)→ STALE rc0', {}),
 ('S_1e3',           'S', 'x', '1e3', 0, 'ANOMALY rc2', {}),
 ('S_space7',        'S', 'x', ' 7', 0, '過去 → STALE rc0', {}),
 ('S_zero',          'S', 'x', '0', 0, 'ANOMALY rc2', {}),
 ('S_out+rc1',       'S', 'x', 'garbage', 1, 'ANOMALY rc2(date が刷つて且つ落ちる= $() が garbage␊0 を捕る)', {}),
 ('S_newline_inj',   'S', 'x', '5\n0', 0, 'ANOMALY rc2', {}),
]
def env_for(shape, extra, log, inflight, lock, stub_out=None, stub_rc=0):
    e = dict(os.environ); e.update({'DETECT_STALE_LOG': log, 'DETECT_STALE_INFLIGHT_DIR': inflight, 'DETECT_STALE_LOCK_FILE': lock, 'LC_ALL': 'C'})
    e.pop('DETECT_STALE_STALE_SEC', None); e.update(extra)
    if shape == 'G': e['PATH'] = D + '/raw/stub_gnu:' + e['PATH']
    if shape == 'S': e['PATH'] = D + '/raw/stub_inj:' + e['PATH']; e['KM92_D_OUT'] = stub_out; e['KM92_D_RC'] = str(stub_rc)
    return e
rows = []; out = [f'# {TAG} 函数の出目 ㋒ / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / now(器) {now} / lib {os.path.relpath(LIB, D)} sha16 {__import__("hashlib").sha256(open(LIB, "rb").read()).hexdigest()[:16]} / shell /bin/bash 3.2 / 姿 B=/bin/date G=stub_gnu(gdate+flock stub) S=stub_inj(date -d → KM92_D_OUT)']
for name, shape, rbt, so, src, sen, extra in CASES:
    log = f'{ENV}/{name}.log'; inflight = f'{ENV}/inflight_{name}'; lock = f'{ENV}/lock_{name}'
    K.kaku(log, f'# log {name}(器が先に置いた一行・以下が lib の追記)'); r = row('km92_' + re.sub(r'[^A-Za-z0-9_]', '_', name), rbt)
    e = env_for(shape, extra, log, inflight, lock, so, src)
    p = subprocess.run(['/bin/bash', '-c', 'source "$1"; detect_stale_evaluate_row "$2"; echo "rc=$?"', '_', LIB, r], capture_output=True, text=True, env=e)
    rc = re.search(r'rc=(\d+)', p.stdout).group(1); err = p.stderr.strip().replace('\n', '␊')[:160]
    lines = [l for l in open(log, encoding='utf-8').read().split('\n') if l and not l.startswith('#')]; tag = re.search(r'\[(\w+)\]', lines[-1]).group(1) if lines else '(log 無し)'
    # 同じ row を CLI の写しへ(enqueue 分岐が走るか)
    K.kaku(log, open(log, encoding='utf-8').read() + '# --- CLI の写し ---')
    c = subprocess.run(['/bin/bash', CLI, '--detect-stale-handshake'], input=r + '\n', capture_output=True, text=True, env=e)
    L = open(log, encoding='utf-8').read(); done = re.search(r'done processed=(\d+) enqueued=(\d+) skipped=(\d+) anomalies=(\d+)', L); nenq = L.count('[ENQUEUE]')
    cli = f'enq{done.group(2)} skip{done.group(3)} anom{done.group(4)} ENQUEUE行{nenq} rc{c.returncode}' if done else f'(done 行無し) rc{c.returncode}'
    for q in (lock,):
        if os.path.exists(q): os.remove(q)
    if os.path.isdir(inflight): shutil.rmtree(inflight)
    poke = '★auto-poke★' if rc == '0' else ('anomaly' if rc == '2' else 'skip')
    rows.append((name, shape, repr(rbt if shape != 'S' else so), rc, tag, poke, cli, err or '-', sen, lines[-1][:150] if lines else '-'))
    out.append(f'{name:22s} 姿{shape} 入力 {rows[-1][2]:26s} → rc {rc} log[{tag}] {poke:12s} CLI {cli} | stderr {err or "-"} | 宣: {sen}')
    out.append(f'    log 逐語: ' + (' ␊ '.join(lines) if lines else '(無し)'))
K.kaku_tsv(D + f'/raw/{TAG}_kansu.tsv', rows, header=['name', 'shape', 'input', 'rc', 'log_tag', 'poke', 'cli', 'stderr', 'sengen', 'last_log_line'])
out.append('意味: rc 0 = CLI の case 0 → detect_stale_enqueue(= auto-poke の経路・Linux では flock 在り → ENQUEUE)。stderr は bash の `[: integer expression expected`(cron では mail/黙・log には残らぬ)。姿 S は date -d の出目だけを差し替へ、+%s と -Iseconds は /bin/date へ渡る。scratch(inflight dir・lock)は讀んだ後に消す(0byte・門 條④)。log は残す(先頭一行は器の印)。')
K.kaku(D + f'/raw/{TAG}_kansu.txt', '\n'.join(out)); print('\n'.join(out))
