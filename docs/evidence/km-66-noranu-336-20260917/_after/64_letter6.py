# -*- coding: utf-8 -*-
"""追ひ便 6・7 の器 64(第66弾・根の外 _after/・50_sengen に名を宣した)。便 6 = 門の後の実測(96/33/67)を 96/33_onore_after/67 の出目から regex で運ぶ。便 7 = 監査提出の代送依頼 ―― gunshi-mac 局所箱は死箱(inbox_write rc=68・総監督裁 seq322250「足軽席は DB の sender を持たぬ・家老mac へ回せ・家老が代送する」)ゆゑ、監査提出の本文(短縮)を同封して karo-mac へ出す。字数を先に印字し 300 超は送らず落ちる。DRY=1 で測るのみ。"""
import sys, os, re, time, subprocess, yaml
B = sys.argv[1]; D = os.path.dirname(B); OUT = D + '/_after'; sys.path.insert(0, OUT); import kaki as K
M = '/Users/momizimac/multi-agent-shogun'; RN = '66弾'; DRY = bool(os.environ.get('DRY'))
rd = lambda p: open(p, encoding='utf-8').read()
t96 = rd(OUT + '/96_after_send.txt'); t33 = rd(OUT + '/33_onore_after.txt'); t67 = rd(OUT + '/67_git_add.txt'); t63 = rd(OUT + '/63_sent.txt')
dif = re.search(r'との差: 新 (\d+) / 変 (\d+) / 消 (\d+)', t96); a = re.search(r'秒 > 秒★\): (\d+) 本 / byte 和 (\d+)', t96); n = re.search(r'\(第55弾 97 の定義\): (\d+) 本 / byte 和 (\d+) ―― 差 = 門控と同じ秒に生れた (\d+) 本', t96)
ato = re.findall(r'^  後 (\S+) ', t96, re.M); j1 = re.search(r'一致 ★(\d+)★ / 相違 (\d+) / 実体無 (\d+) / 読めぬ行 (\d+)', t96)
s33 = re.search(r'★載らぬ (\d+)★', t33); k33 = re.search(r'甲計 (\d+) / 乙計 (\d+) / 丙計 (\d+) / 総和 (\d+) = 載らぬ (\d+) 差 (\d+)', t33); k1 = re.search(r'甲1 門の出目: (\d+) 本', t33); k2 = re.search(r'甲2 臺帳の器の出目: (\d+) 本', t33)
g = re.search(r'rc (\d+) / staged\(git diff --cached --name-only\) (\d+) 本 / 枝 (\S+) / HEAD (\S+)\(', t67)
seki = re.search(r'席基準.*= 實 ([\d.]+) 分 ⇔ 宣 ([\d.]+) 分 → 宣−實 ([+\-][\d.]+) 分', t63); karo = re.search(r'家老基準.*= 實 ([\d.]+) 分 ⇔ 宣 ([\d.]+) 分 → 宣−實 ([+\-][\d.]+) 分', t63)
l6 = f"[第{RN} 追ひ便 6] 門の後(96・根raw/): 99→96 新{dif.group(1)}/変{dif.group(2)}/消{dif.group(3)}・秒>秒 {a.group(1)}本{a.group(2)}B={'・'.join(ato)}(宣に在る名)・ns>秒{n.group(1)}本(門自身{n.group(3)})・條①{j1.group(1)}/{j1.group(2)}/{j1.group(3)}/{j1.group(4)}。㋔己の束へ同則(33):載らぬ{s33.group(1)}=甲{k33.group(1)}(門{k1.group(1)}+臺帳器{k2.group(1)})/乙{k33.group(2)}/丙{k33.group(3)}=乙3(門の後)0・再犯無し。git add -f rc{g.group(1)} staged{g.group(2)}本(枝{g.group(3)} HEAD {g.group(4)}・67/64は未staged)。宣⇔實:席{seki.group(1)}分({seki.group(3)})/家老{karo.group(1)}分({karo.group(3)})三たび過大。疵:64のDRY rcをpipe越しに取つた(送出0)"
audit = f"[監査提出(專任1 第{RN})] 束 docs/evidence/km-66-noranu-336-20260917(worktree)/ 紙 529059cc9624968e / 臺帳 d832288c49247002 / 門 rc0 / 題=載らぬ336を先に書いた則で三山へ / 答=甲285/乙49/丙2(同分4)差0・乙=届かぬ23/讀めぬ行3/門の後6/渡さず17・相違1=末尾LF一つ・一走目343=己の2MB閾。監査を乞ふ"
l7 = f"[第{RN} 追ひ便 7・監査提出の代送を乞ふ] gunshi-mac箱は死箱(inbox_write rc=68・裁322250「家老が代送」)ゆゑ同封→ {audit}"
lens = [len(l6), len(l7)]; print('字数', lens)
for i, nn in zip((6, 7), lens): assert nn <= 300, f'便{i} {nn} 字 > 300'
if DRY: print('DRY'); print(l6); print(l7); sys.exit(0)
now = time.strftime('%Y-%m-%dT%H:%M:%S%z'); rcs = []
for i, x in zip((6, 7), (l6, l7)):
    p = subprocess.run(['bash', M + '/scripts/inbox_write.sh', 'karo-mac', x, 'report', 'ashigaru-mac-1'], capture_output=True, text=True, cwd=M); rcs.append(f'便{i} inbox_write rc={p.returncode}' + (f' stderr={p.stderr.strip()[:140]}' if p.stderr.strip() else ''))
ms = yaml.safe_load(open(M + '/queue/inbox/karo-mac.yaml', encoding='utf-8')).get('messages') or []
g8 = []
for i, x in zip((6, 7), (l6, l7)):
    ids = [m['id'] for m in ms if m.get('from') == 'ashigaru-mac-1' and str(m.get('content', '')).startswith(f'[第{RN} 追ひ便 {i}')]
    c = next((str(m.get('content', '')).rstrip('\n') for m in ms if m['id'] == ids[-1]), '') if ids else ''
    g8.append(f'便{i} entry {len(ids)} 本 {ids} / 箱 {len(c)} / 64 {len(x)} / 逐語一致 {c == x}')
K.kaku(OUT + '/63b_sent.txt', f'{now}\n宛 karo-mac / type report / from ashigaru-mac-1 / 便 6({lens[0]} 字)+ 便 7({lens[1]} 字・監査提出の代送依頼・gunshi-mac へは出して居らぬ = 死箱の門 rc=68 に従つた)\n' + '\n'.join(rcs) + '\n第八の番人: ' + ' | '.join(g8) + f'\n本文6: {l6}\n本文7: {l7}')
print(open(OUT + '/63b_sent.txt', encoding='utf-8').read())
