# -*- coding: utf-8 -*-
"""添状の器 62/63(第56弾・第55弾を写した ―― ★出目(62_report_body/63_sent)を根の外 <束>_after/ へ書く★・宣 40 分 ―― ★弾番は束の名から・起は 00_start から・assigned_at は札から讀む(手で打たぬ・八十二の席の同形を器の順で直す)★・門の前に DRY=1 で字数を検め ―― ★DRY 一走目 329/291/310/323/329・監査 336、二走目 便4 302・監査 310、三走目 便4 301 で assert に落ち(送らず・出目無し)縮めた★・門の後は此の file に触れぬ)。argv[1] = 束の前置。
便 5(各 300 字以内・字数を先に印字・超えれば assert)+ 監査提出 1 を karo-mac へ inbox_write.sh で出し、箱を content 鍵の startswith で讀み返して id を 63 に並べ、送つた本文を箱から讀み返して逐語一致を検める(第八の番人)。
送つた直後に己の札に印を書く(status→done・done_at = date・done_note)。DRY=1 なら送らず印も書かぬ・63 も書かぬ。便 7(96 の出目)は 64 が出す。★本弾は日付を跨ぐ ∴ 分は日付込み。★"""
import sys, os, re, time, subprocess, hashlib, yaml, datetime as dt
B = sys.argv[1]; E = B + '_evidence/raw'; OUT = B + '_after'; sys.path.insert(0, E); import kaki as K
RN = re.search(r'_km-(\d+)-', B).group(1)
sha16 = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]
DRY = bool(os.environ.get('DRY'))
def rd(p, alt): return open(p, encoding='utf-8').read() if os.path.isfile(p) else alt
def P(s): return dt.datetime.strptime(s[:19], '%Y-%m-%dT%H:%M:%S')
P_, M = sha16(B + '.md'), (sha16(B + '_manifest.txt') if os.path.isfile(B + '_manifest.txt') else 'x' * 16); G = sha16(B + '_gate.txt') if os.path.isfile(B + '_gate.txt') else 'x' * 16
gate_t = (re.search(r'刻 (\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)', rd(B + '_gate.txt', '刻 2026-09-16T17:00:00+0900').split('\n')[1] if os.path.isfile(B + '_gate.txt') else '刻 2026-09-16T17:00:00+0900')).group(1)
man = rd(B + '_manifest.txt', ''); items = sum(1 for l in man.split('\n') if l.startswith('path='))
rcs = rd(E + '/60_gate_rcs.txt', 'all | 渡した 00 | rc 0 | 札 0\nmain | 渡した 0 | rc 0 | 札 0'); ra = re.search(r'^all \| 渡した (\d+) \| rc (\d+) \| 札 (\d+)', rcs, re.M); rm = re.search(r'^main \| 渡した (\d+) \| rc (\d+) \| 札 (\d+)', rcs, re.M)
j1 = re.search(r'一致 ★(\d+)★ / 相違 (\d+) / 実体無 (\d+) / 読めぬ行 (\d+)', rd(OUT + '/99_after_gate.txt', '一致 ★00★ / 相違 0 / 実体無 0 / 読めぬ行 0'))
KI = re.search(r'起 (\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)', open(E + '/00_start.txt', encoding='utf-8').read()).group(1)
ASG = re.search(r'^assigned_at: "(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)"', open('queue/tasks/ashigaru-mac-1.yaml', encoding='utf-8').read(), re.M).group(1)
SEN_MIN = float(re.search(r'起 \+ (\d+) 分 = ', open(E + '/00_start.txt', encoding='utf-8').read()).group(1)); sen_clock = P(KI) + dt.timedelta(minutes=SEN_MIN)
j_seki = (P(gate_t) - P(KI)).total_seconds() / 60; d_seki = SEN_MIN - j_seki
PL = subprocess.run(['grep', '-c', '', B + '.md'], capture_output=True, text=True).stdout.strip()
ch = re.search(r"= 1 本: \['(msg_\S+?)'\]", rd(E + '/05_chakushu.txt', "= 1 本: ['msg_x']")).group(1)
a99 = re.search(r'より後の mtime\(★日付込み・秒 > 秒★\): (\d+) 本 / byte 和 (\d+)', rd(OUT + '/99_after_gate.txt', 'より後の mtime(★日付込み・秒 > 秒★): 0 本 / byte 和 0')); n99 = re.search(r'ns > 秒\.000 で比べると\(第55弾 97 の定義\): (\d+) 本 / byte 和 (\d+)', rd(OUT + '/99_after_gate.txt', 'ns > 秒.000 で比べると(第55弾 97 の定義): 0 本 / byte 和 0'))
letters = [
 f"[第{RN}弾 納め 1/5] 束 queue/reports/ashigaru-mac-1_km-{RN}-…-20260916 / 紙 sha16 {P_}({os.path.getsize(B + '.md')}B・{PL}行)/ 臺帳 {M}(項{items})/ 門控 {G}(名 60_gate_top.r{RN})/ 門 all rc{ra.group(2)} 札{ra.group(3)} 渡{ra.group(1)}・main rc{rm.group(2)} / 照合(99)一致{j1.group(1)}/相違{j1.group(2)}/実体無{j1.group(3)}/読めぬ{j1.group(4)} / ★門の後に根へ(99): 秒 {a99.group(1)}本{a99.group(2)}B・ns {n99.group(1)}本{n99.group(2)}B=門自身のみ★ / 着手便 出した({ch[-13:]}・297字・三走目)",
 f'[第{RN}弾 納め 2/5] 問一(raw/20) 22本/36096B=㋐1 門の口 3本618B(60_gate_all .err/.out/.rc・行の逐語一致 True)+㋐2 門控 1本1083B(_gate.txt と sha 同一)+㋐3 駆動器 4本4115B(60_gate_rcs・60_gate_run.*)+㋑ 14本30280B(99/62/63/96/97.py)→閉ぢる。★厳しく門自身 4本1701B・触れる 18本34395B／緩く 8本5816B・触れる 14本30280B。何れでも 14本は触れる=繕はぬ★。同じ秒 8本(門控の刻は書く前に採る)',
 f'[第{RN}弾 納め 3/5] 問一後半(raw/32・同根同刻) 30 HH:MM:SS 55本104101B ⇔ 31 日付込み 秒>秒 23本41310B / ns>秒.000 31本47126B ⇔ 97(其の刻) 22本36096B。30−31 = 偽32本62791B(97 の宣と一致)・31秒−30 = 0・31ns−97 = 後に生れた 9本11030B(63b/65×4/97 の出目×4)・消 0 → 閉ぢる。★秒の粒度は門自身 8本を隠す ∴ 31 は二定義を併記★',
 f'[第{RN}弾 納め 4/5] 問二 raw/70_sha_walk.py(据ゑず・--prefix は束の前置のみ・後置に依らぬ)。a1r55+a2r40 束=★母數234本★(家老の宣と一致)433359B・当たり 3/6: 紙1・臺帳1・★門控2本(同sha)★・札控76d4…0(三束に無し・seigo28/a1_prev_hikae.yaml に1本=母數617で4/6)・陰性 deadbeef/0123 各0・陽性 紙1。偽の場合: 同sha複数 21sha/101本(rc"0" 22本・空一行85B 21本・空0B 7本)・前置衝突0・束の外1・>64MB 0・symlink 0',
 f'[第{RN}弾 納め 5/5] 問三 数へ方=raw/80(語 直さず/知りながら/未だ直…)+81(N度目)を先に書いて走らせ、紙で裁いた。母數 file 439 行 6601(r52〜55)。80 候補21行 81 候補14行 → ★知つて居て直さなかつた 9 件★(r53 ⑵⑶⑷ 3・r54 見出し 1・r55 25_eta→30/64 1=陽性対照・21定数 1・起の刻 器の順 1・着手便 r51-53 1・便の字数 1)+権限の外 1(宣dir)+同族「知つて居て破つた」r52 7件+偽 12。★本弾の再犯: 起の刻 四度目・字数 二度★ ㊈ 席 {j_seki:.0f}分 宣{SEN_MIN:.0f} {d_seki:+.0f}',
]
audit = f"[監査提出(專任1 第{RN}弾)] 束 queue/reports/ashigaru-mac-1_km-{RN}-…-20260916 / 紙 sha16 {P_} / 臺帳 {M} / 門控 {G}(名 60_gate_top.r{RN})/ 門 all rc{ra.group(2)}・main rc{rm.group(2)} / 題=22本を裁く・shaで歩く器・知つて居て直さなかつた / 答=門自身 4(厳)8(緩)・触れる14は繕はず・母數234 再現・門控は同sha2本・9件(再犯2)。門の後の出目は根の外 _after/。監査を乞ふ(讀取のみ)"
lens = [len(x) for x in letters]; print('字数', lens, '監査提出', len(audit))
for i, (x, n) in enumerate(zip(letters, lens), 1): assert n <= 300, f'便{i} {n} 字 > 300'
assert len(audit) <= 300, f'監査提出 {len(audit)} 字'
if DRY: print('DRY ―― 送らず・印も 63 も書かぬ'); sys.exit(0)
now = time.strftime('%Y-%m-%dT%H:%M:%S%z')
os.makedirs(OUT, exist_ok=True); K.kaku(OUT + '/62_report_body.txt', f'# 62 便の本文(第{RN}弾・各 300 字以内・先に字数を印字 {lens}・監査提出 {len(audit)} 字)/ 刻 {now}\n' + '\n'.join(f'--- 便{i}/{len(letters)} ({n} 字)\n{x}' for i, (x, n) in enumerate(zip(letters, lens), 1)) + f'\n--- 監査提出 karo-mac ({len(audit)} 字)\n{audit}')
rcs_l = []
for i, x in enumerate(letters, 1):
    p = subprocess.run(['bash', 'scripts/inbox_write.sh', 'karo-mac', x, 'report', 'ashigaru-mac-1'], capture_output=True, text=True); rcs_l.append(f'便{i}/{len(letters)} inbox_write rc={p.returncode}' + (f' stderr={p.stderr.strip()[:140]}' if p.stderr.strip() else ''))
p = subprocess.run(['bash', 'scripts/inbox_write.sh', 'karo-mac', audit, 'report', 'ashigaru-mac-1'], capture_output=True, text=True); rcs_l.append(f'監査提出 karo-mac inbox_write rc={p.returncode}' + (f' stderr={p.stderr.strip()[:140]}' if p.stderr.strip() else ''))
done_at = time.strftime('%Y-%m-%dT%H:%M:%S')
card = open('queue/tasks/ashigaru-mac-1.yaml', encoding='utf-8').read(); assert card.count('\nstatus: assigned\n') == 1
j_k = (P(done_at) - P(ASG)).total_seconds() / 60; sen_k = (sen_clock - P(ASG)).total_seconds() / 60; d_k = sen_k - j_k
note = f'門 {gate_t}(起 {KI}・宣 起+{SEN_MIN:.0f}分={sen_clock.strftime("%m-%d %H:%M:%S")})/ 紙 {P_} {os.path.getsize(B + ".md")}B {PL}行(grep) / 臺帳 {M} 項{items} / 門控 60_gate_top.r{RN} / 着手便 1(05・三走目で出した)+ 便 5 + 監査提出 1 + 追ひ便 7(96 の出目・64 が出す・根の外 _after/) / ★両基準: 席 {j_seki:.1f}分 宣−實 {d_seki:+.1f}({"＋過大" if d_seki > 0 else "−過少"})・家老 assigned_at {ASG}→done_at {done_at} = {j_k:.1f}分 宣−實 {d_k:+.1f}({"＋過大" if d_k > 0 else "−過少"})★ / 答=問一 22本=門自身 4(厳)/8(緩)・触れる 14 は繕はず・30/31/97 閉ぢる / 問二 70_sha_walk 母數234 再現・門控 同sha 2本・札控は束の外 / 問三 9件(本弾の再犯 2)'
card = card.replace('\nstatus: assigned\n', f'\nstatus: done\ndone_at: "{done_at}"\ndone_note: "{note}"\n', 1)
open('queue/tasks/ashigaru-mac-1.yaml', 'w', encoding='utf-8', newline='\n').write(card)
back = open('queue/tasks/ashigaru-mac-1.yaml', encoding='utf-8').read(); da = re.search(r'^done_at: "(\S+)"', back, re.M).group(1)
t8 = time.strftime('%Y-%m-%dT%H:%M:%S%z'); ms = yaml.safe_load(open('queue/inbox/karo-mac.yaml', encoding='utf-8')).get('messages') or []
ids = [m['id'] for m in ms if m.get('from') == 'ashigaru-mac-1' and str(m.get('content', '')).startswith(f'[第{RN}弾 納め')]
ida = [m['id'] for m in ms if m.get('from') == 'ashigaru-mac-1' and str(m.get('content', '')).startswith(f'[監査提出(專任1 第{RN}弾)]')]
byid = {m['id']: str(m.get('content', '')) for m in ms}; g8 = []
for x, i in zip(letters + [audit], ids + ida):
    c = byid.get(i, '').rstrip('\n'); g8.append(f'{i} 箱 {len(c)} / 62 {len(x)} / 差 {len(c) - len(x)} / 逐語一致 {c == x}')
j_karo = (P(da) - P(ASG)).total_seconds() / 60; d_karo = sen_k - j_karo
K.kaku(OUT + '/63_sent.txt', f'{now}\n宛 karo-mac / type report / from ashigaru-mac-1 / 便 {len(letters)}(各 300 字以内・先に字数を印字 {lens})+ karo-mac 宛 監査提出 1({len(audit)} 字)\n' + '\n'.join(rcs_l)
  + f'\n箱 queue/inbox/karo-mac.yaml で本弾の冠 [第{RN}弾 納め を持つ from=ashigaru-mac-1 の entry(content 鍵・startswith・刻で推さぬ) = {len(ids)} 本: {ids}\n監査提出の entry = {len(ida)} 本: {ida}\n札に印を書いた: status done / done_at {da}(讀み返し) / done_note 有'
  + f'\n★㊈ 宣⇔實 両基準(宣 = 起 {KI} + {SEN_MIN:.0f} 分 = {sen_clock} の刻・家老の宣も 起+{SEN_MIN:.0f})★\n席基準  起 {KI} → 門 {gate_t} = 實 {j_seki:.2f} 分 ⇔ 宣 {SEN_MIN:.1f} 分 → 宣−實 {d_seki:+.2f} 分 = {"＋過大(宣が長い)" if d_seki > 0 else "−過少(宣が短い)"}'
  + f'\n家老基準 assigned_at {ASG} → done_at {da} = 實 {j_karo:.2f} 分 ⇔ 宣 {sen_k:.2f} 分 → 宣−實 {d_karo:+.2f} 分 = {"＋過大" if d_karo > 0 else "−過少"}'
  + f'\n★符號は {"同じ" if (d_seki > 0) == (d_karo > 0) else "★分かれた★"}(第55弾 −4064/−4065・第54弾 +11.97/+11.65・第51弾は分かれた)★'
  + f'\n★第八の番人(送出後に箱から本文を讀み返す・刻 {t8})★: ' + ' | '.join(g8)
  + f'\n★此の 63 と 62 の .stdout/.err/.rc(根の外 _after/)と札の印は、此の後の 96_after_send が 99 との差で測る。96 の己の出目と 63b と便 7 は ★家老★ が測る。根(_evidence)には門の後 0 byte(門自身を除く)―― 96 が證す。★')
print(open(OUT + '/63_sent.txt', encoding='utf-8').read())
