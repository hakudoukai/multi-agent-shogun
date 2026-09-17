# -*- coding: utf-8 -*-
"""55 ★「未だ待つて居る」と「自ら返つた」を分つ★(54 形9 の測り直し)
54 は perl の alarm で砂時計を掛けたが ―― ★bash の `read -t` は alarm() で出来て居る★。
∴ read が己の alarm を掛け直し、當席の砂時計を ★上書きして消した★。
  形9 が丁度 12 秒で返つたのは「砂時計が切つた」のか「偶さか」なのか ★判らぬ★。
★分つ法★: 砂時計の丈を 5 秒と 12 秒の二度に変へて走らす。
  wall が砂時計に ★追随すれば★ ―― 其の時まで ★未だ待つて居た★(=時限が効いて居らぬ)。
  wall が砂時計に ★依らず一定なら★ ―― 自ら返つて居る。
砂時計は python の subprocess timeout(外から断つ)ゆゑ bash の alarm に消せぬ。
★陽性対照★: TMO=1 は何れの砂時計でも wall≒1 に成らねばならぬ。"""
import subprocess, sys, time, os
D = sys.argv[1]; sys.path.insert(0, D + '/raw'); import kaki as K
H = D + '/utsushi/kou_new_harness.sh'
CASES = [('5正常値1(陽性対照)', '1'), ('9二の32乗引1', '4294967295'),
         ('9b十億', '1000000000'), ('10二の32乗', '4294967296'), ('1既定10', '10')]
out = []
for cap in (5, 12):
    for lab, val in CASES:
        env = dict(os.environ, STOP_HOOK_STDIN_TIMEOUT=val)
        # ★stdin は開いた儘でなければならぬ★(初走の疵):
        #   subprocess.PIPE + communicate() は親側を ★直ちに閉ぢる★ ゆゑ read は EOF で
        #   即返る。初走は陽性対照(TMO=1)まで 0.0 秒に成り、其れが器の壊れの徴であつた。
        #   ∴ 自前の pipe を作り、書き手側を ★親が握つた儘★ 子へ讀み手側を渡す。
        rfd, wfd = os.pipe()
        r = subprocess.Popen(['/bin/bash', H], stdin=rfd,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
        os.close(rfd)
        t0 = time.time()
        try:
            so, se = r.communicate(timeout=cap); cut = '自ら返つた'
        except subprocess.TimeoutExpired:
            r.terminate(); so, se = r.communicate(); cut = '★砂時計が断つた★'
        os.close(wfd)
        el = round(time.time() - t0, 1)
        say = '有' if '時限切れ' in se.decode('utf-8', 'replace') else '無'
        out.append([str(cap), lab, val, str(el), cut, say])
K.kaku_tsv(D + '/raw/55_yomi_kagiri.tsv', out,
           header=['砂時計_s', '形', 'TMO', 'wall_s', '出方', '時限切れの報せ'])
by = {}
for cap, lab, val, el, cut, say in out: by.setdefault(lab, {})[cap] = (el, cut, say)
sm = ['# 55 砂時計 5s / 12s の二度走り ―― 追随すれば「未だ待つて居た」']
for lab in [c[0] for c in CASES]:
    a, b = by[lab]['5'], by[lab]['12']
    tsui = float(b[0]) - float(a[0]) > 3
    sm.append('  %-18s 5s→%-5s(%s)  12s→%-5s(%s)  ∴ %s' %
              (lab, a[0], a[1], b[0], b[1], '★追随=未だ待つて居た★' if tsui else '一定=自ら返つた'))
sm.append('')
sm.append('★∴ `read -t` が受ける上限は 2^32-1 = 4294967295 秒(=136.1 年)。')
sm.append('  其れ以下の巨値は ★正しく時計を組み、其の儘 待ち続ける★。')
sm.append('  num_same_op は 2^63 未満を悉く「數」と呼ぶ ∴ ★此の穴を塞がぬ★。')
K.kaku(D + '/raw/55_yomi_kagiri_summary.txt', '\n'.join(sm))
print('\n'.join(sm))
