# -*- coding: utf-8 -*-
"""問一の器 20(第56弾)。argv = <第55弾の束の前置>。讀むのみ(己の出目は 10_run が書く)。
第55弾 raw/97_after_send_dated.txt が刷つた「門控の刻より後 22 本 / 36096 B」を、裁 seq310228⑵「門自身の台帳への一行は門の出力であり禁の外」に照らして
㋐ 門自身の産物 / ㋑ 其れ以外 に分ける。根拠 = ⑴ 何の器が書いたか(第55弾の器の逐語の行番号)⑵ 中身が門の口から出た物と一致するか(sha / 行の逐語)⑶ 門控の刻からの隔たり(ms・st_mtime_ns)。
㋐ は更に三段に割る: ㋐1 門(gate.sh)の stdout/stderr/rc を其の儘 kaki で置いた物 / ㋐2 門控(裁の言ふ「門自身の一行」の写し)/ ㋐3 門を走らせた器(60_gate_run.py)と其の駆動器(10_run.py)の産物 ―― ★㋐3 は「門自身」ではなく「門を走らせた器」の物 ∴ 厳しい讀みでは ㋑ に落ちる。両方の和を刷る。"""
import os, re, sys, hashlib, datetime as dt
B = sys.argv[1]; R = B + '_evidence'; RAW = R + '/raw'
sha16 = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]
t97 = open(RAW + '/97_after_send_dated.txt', encoding='utf-8').read()
rows = [(m.group(1), int(m.group(2))) for m in re.finditer(r'^  後 (\S+) (\d+)B ', t97, re.M)]
decl = re.search(r'より後\(mtime 秒 > 門控\)= (\d+) 本 / byte 和 (\d+)', t97)
gline = open(B + '_gate.txt', encoding='utf-8').read().split('\n')[1]; gt = dt.datetime.strptime(re.search(r'刻 (\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)', gline).group(1), '%Y-%m-%dT%H:%M:%S').timestamp()
# 中身の検め: 60_gate_all.err の行 = 門控「走り all」節の行(逐語)か / 60_gate_top.r55.txt = <束>_gate.txt(sha)か / 60_gate_rcs.txt の stderr sha16(生の byte)と 60_gate_all.err(kaki 正規化後)の sha16
top = open(B + '_gate.txt', encoding='utf-8').read().split('\n'); ia = top.index('## 走り all(stderr 逐語)'); im = top.index('## 走り main(stderr 逐語)')
sec_all = [l for l in top[ia + 1:im]]; err_all = open(RAW + '/60_gate_all.err', encoding='utf-8').read().rstrip('\n').split('\n')
rcs = open(RAW + '/60_gate_rcs.txt', encoding='utf-8').read(); m_all = re.search(r'^all \| .*stderr sha16 ([0-9a-f]{16})', rcs, re.M)
def cls(n):
    b = os.path.basename(n)
    if b in ('60_gate_all.err', '60_gate_all.out', '60_gate_all.rc'): return '㋐1', '門(gate.sh)の stderr/stdout/rc を 60_gate_run.py L88-89 が subprocess で受け kaki で置いた ―― 中身は門の口から出た物(下の逐語検め)'
    if b.startswith('60_gate_top.'): return '㋐2', '門控 = 門の stderr の写し + 二行の頭(60_gate_run.py L116-120)―― 裁 310228⑵ の「門自身の一行」の当弾の形(<束>_gate.txt と byte 同一・下の sha 検め)'
    if b == '60_gate_rcs.txt': return '㋐3', '門を走らせた器 60_gate_run.py L108 の要約(門の出目ではなく駆動の記録)'
    if b.startswith('60_gate_run.'): return '㋐3', '駆動器 10_run.py L11 が 60_gate_run.py の stdout/stderr/rc を置いた(門から二段 離れる)'
    if b.startswith('99_'): return '㋑', '門の後の歩き 30_kusari.py(99_after_gate の名)の出目 ―― 門でも門の駆動器でもない'
    if b.startswith('62_') or b == '63_sent.txt': return '㋑', '便の器 62_letters.py の出目(本文・id の列・駆動器の写し)―― 門と無縁'
    if b.startswith('96_'): return '㋑', '門の後の二段目の歩き 30_kusari.py(96_after_send の名)の出目'
    if b.startswith('97_'): return '㋑', '門の後に足した未宣の器 97 の .py(手で書いた・便 8 で申告済)'
    return '?', '型に無い名'
out = [f'# 20 問一 裁き(裁 seq310228⑵)/ 的 = 第55弾 raw/97 が刷つた 後 {decl.group(1)} 本 / {decl.group(2)} B(母數 = 此の {len(rows)} 本)/ 門控の刻 {dt.datetime.fromtimestamp(gt)}(秒・<束>_gate.txt 二行目)']
out.append('類\t名\tbyte(97 の宣)\tbyte(今)\t門控の刻からの隔たり ms(st_mtime_ns)\t根拠')
tot = {}; cnt = {}; tot97 = 0
for n, b97 in rows:
    p = R + '/' + n; st = os.stat(p); ms = (st.st_mtime_ns / 1e9 - gt) * 1000; c, why = cls(n)
    tot[c] = tot.get(c, 0) + st.st_size; cnt[c] = cnt.get(c, 0) + 1; tot97 += b97
    out.append(f'{c}\t{n}\t{b97}\t{st.st_size}\t{ms:+.1f}\t{why}')
a1, a2, a3, b_ = (tot.get(k, 0) for k in ('㋐1', '㋐2', '㋐3', '㋑')); c1, c2, c3, cb = (cnt.get(k, 0) for k in ('㋐1', '㋐2', '㋐3', '㋑'))
out.append(f'## 和: ㋐1 {c1} 本 {a1} B / ㋐2 {c2} 本 {a2} B / ㋐3 {c3} 本 {a3} B / ㋑ {cb} 本 {b_} B → 計 {c1+c2+c3+cb} 本 {a1+a2+a3+b_} B ⇔ 97 の宣 {decl.group(1)} 本 {decl.group(2)} B(97 の行の和 {tot97})→ {"閉ぢる" if a1+a2+a3+b_ == int(decl.group(2)) and c1+c2+c3+cb == int(decl.group(1)) else "★閉ぢぬ★ 残 " + str(int(decl.group(2)) - (a1+a2+a3+b_)) + " B"}')
out.append(f'## 厳しい讀み(門自身 = ㋐1+㋐2 のみ): 禁の外 {c1+c2} 本 {a1+a2} B / ★禁に触れる {c3+cb} 本 {a3+b_} B★ ―― 緩い讀み(㋐3 も門の側): 禁の外 {c1+c2+c3} 本 {a1+a2+a3} B / ★禁に触れる {cb} 本 {b_} B★。★何れの讀みでも ㋑ {cb} 本 {b_} B は触れる。繕はぬ。★')
out.append(f'## 中身の検め: 60_gate_all.err の行 {len(err_all)} ⇔ 門控「走り all」節の行 {len(sec_all)} → 逐語一致 {err_all == sec_all} / raw/60_gate_top.r55.txt sha16 {sha16(RAW + "/60_gate_top.r55.txt")} ⇔ <束>_gate.txt {sha16(B + "_gate.txt")} → {"同一" if sha16(RAW + "/60_gate_top.r55.txt") == sha16(B + "_gate.txt") else "★別★"} / 60_gate_rcs.txt が刷つた門の生 stderr sha16 {m_all.group(1) if m_all else "−"} ⇔ 60_gate_all.err(kaki 正規化後)sha16 {sha16(RAW + "/60_gate_all.err")} → {"同一" if m_all and m_all.group(1) == sha16(RAW + "/60_gate_all.err") else "★別(kaki が末尾を整へた ∴ 生の byte とは違ふ ―― 行の逐語は上で一致)★"}')
same_sec = [n for n, _ in rows if int(os.stat(R + '/' + n).st_mtime) == int(gt)]
out.append(f'## 門控の刻と同じ秒に生れた物 {len(same_sec)} 本: {same_sec} ―― 門控の刻(60_gate_run.py L117 の strftime)は門控を書く★前★に採る ∴ 門控自身と門の出目が「刻より後」に落ちる(秒の下の差・上の ms 欄)。')
# 境の外(22 に入らなかつた門の産物): 60_gate_main/selftest/61_ の隔たり
pre = sorted(f for f in os.listdir(RAW) if f.startswith(('60_gate_main', '60_gate_selftest', '61_gate_argv')))
out.append('## 22 本に入らなかつた門の産物(門控の刻以前・門の走り main/selftest と argv の列): ' + ' / '.join(f'{f} {(os.stat(RAW + "/" + f).st_mtime_ns / 1e9 - gt) * 1000:+.0f}ms' for f in pre))
out.append('## ∴ 答: 22 本の内 門自身と言へるのは 厳しく 4 本(㋐1 3 + ㋐2 1)・緩く 8 本(+㋐3 4)。残り 14 本(99/62/63/96/97)は ★禁に触れる★ ―― 之は第55弾の紙 §3 の道 ㋑(門控と便の記録を根の外へ)を採らなかつた席の選びの結果であり、本弾は根の外 _after/ へ置く形で手を変へる(後段 31 で證す)。')
print('\n'.join(out))
