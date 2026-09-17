# -*- coding: utf-8 -*-
"""㋐ 再現 10 ―― 專任2 の 48 走(四器×三案×四形)を ★己の台・己の切り方★ で走らせ、彼の raw/40_an_otsu.tsv(讀むのみ)と行毎に突き合せる。"""
import os, sys, subprocess, hashlib, time, csv, glob
D = sys.argv[1]; E = D + '/raw'; sys.path.insert(0, E); import kaki as K, dai73 as T
M = T.M; HIS = M + '/docs/evidence/km-53b-gyou-chunyu-no-naoshi-wo-sueru-20260917/raw/40_an_otsu.tsv'
KATA = [('甲 行注入(★陽性★)', '1' + chr(10) + T.FAKE), ('乙 ★負1★ 清い非数', 'abc'), ('丙 ★負2★ 正しい数', '777'), ('丁 ★負3★ 空文字', '')]
ANMAP = {'現行': '現行', '紙(甲)': '甲', '乙(當席案)': '乙'}
rows = []; mine = {}
for key, rel in T.TGT:
    for his_an, an in ANMAP.items():
        p = T.dai_path(E + '/dai', key, an); bn = subprocess.run(['/bin/bash', '-n', p], capture_output=True).returncode
        for nm, v in KATA:
            rc, so, se = T.hashi(p, v); n = T.yomite(se)['LF']
            mine[(rel, his_an, nm)] = (str(n), T.out_of(so), '★正★' if T.u8(se) == '正' else T.u8(se).replace('不正', '不正'), str(bn), str(rc))
            rows.append((rel, an, nm, n, T.out_of(so), T.u8(se), bn, rc, T.esc(se)[:160]))
K.kaku_tsv(E + '/10_saigen.tsv', rows, ['生器', '案', '形', '鳴り行数(LF讀手)', 'OUT', '札のUTF-8', 'bash -n rc', '走 rc', 'stderr(esc・160字迄)'])
# 彼の表(讀むのみ)
his = [l.rstrip('\n').split('\t') for l in open(HIS, encoding='utf-8') if l.startswith('scripts/')]
bo = len(his); icchi = 0; chigai = []
for r in his:
    rel, an, nm, n, out, u, bn, rc = r[:8]; me = mine.get((rel, an, nm))
    if me is None: chigai.append(f'{rel}/{an}/{nm}: 當席に無し'); continue
    theirs = (n, out, u, bn, rc); m2 = (me[0], me[1], me[2], me[3], me[4])
    if theirs == m2: icchi += 1
    else: chigai.append(f'{rel}/{an}/{nm}: 彼 {theirs} ⇔ 己 {m2}')
# 台の sha ―― 彼の束外の写し(~/km53b-utsushi-20260917/)が今も在れば sha16 を並べる(讀むのみ)
his_dai = sorted(glob.glob(os.path.expanduser('~/km53b-utsushi-20260917/an_*.sh')))
pair = []
for hp in his_dai:
    b = os.path.basename(hp)
    key = next((k for k, rel in T.TGT if rel.replace('/', '__') in b), None); an = next((a for h, a in ANMAP.items() if b.endswith('__%s.sh' % h)), None)
    if key and an:
        mp = E + '/dai/dai_%s__%s.sh' % (key, an); pair.append(f'{b}: 彼 {T.sha16(open(hp,"rb").read())} ⇔ 己 {T.sha16(open(mp,"rb").read())} {"同" if open(hp,"rb").read()==open(mp,"rb").read() else "異"}')
head = [f'# 10 再現 / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 己の走 {len(rows)} / 彼の表 {HIS} sha16 {T.sha16(open(HIS,"rb").read())}',
        f'★母數 {bo}(彼の表の行)/ 一致 {icchi} / 食ひ違ひ {len(chigai)}★(欄 = 鳴り行数・OUT・札のUTF-8・bash -n rc・走 rc の五つ)',
        '食ひ違ひ: ' + (' ／ '.join(chigai) if chigai else '無し(五欄とも 48/48)'),
        f'彼の束外の台 {len(his_dai)} 本(~/km53b-utsushi-20260917/)⇔ 己の台(raw/dai/): ' + (' / '.join(pair) if pair else '彼の台は disk に無い(比べられぬ)'),
        '★共有した前提(一致しても此処は二人で同じ石を踏んで居る)★:',
        '  ⑴ 台 = 生器から助器四本(_th_say/num_same_op/env_state/fix_threshold)を抜き 駆動一行を足した物 ―― 生器本体は一度も走らせて居らぬ(preflight の向う側)',
        '  ⑵ 鳴り行数 = stderr の非空行を \\n で割つた数(LF 讀手)―― 他の讀手(splitlines 等)は 20 が別に数へる',
        '  ⑶ LC_ALL=C・/bin/bash 3.2.57 で走らせた(sh/dash/zsh は 30 が別に)',
        '  ⑷ 形は彼の四つ(改行一つ・abc・777・空)―― 他の制御字は 20 が別に',
        '  ⑸ 置換の逐語は彼の ki/40 から一字も変へず写した(彼の逐語に疵が在れば二人とも同じ疵を踏む)',
        '★違へた前提★: 台の切り方(彼=一塊・己=関数毎)/ 駆動の変数名(KM53B→KM73・札の語が変る故 stderr の逐語は比べず 五欄で比べた)']
K.kaku(E + '/10_saigen.txt', '\n'.join(head)); print('\n'.join(head))
