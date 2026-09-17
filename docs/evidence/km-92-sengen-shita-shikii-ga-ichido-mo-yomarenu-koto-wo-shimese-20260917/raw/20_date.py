# -*- coding: utf-8 -*-
"""20 date の方言(第81弾 km-92 ㋑)―― 当機で `date -d "<時刻>" +%s` が何を返すかを ★GNU 形(-d)と BSD 形(-j -f)の両対照★ で刷り、verbatim 行 `deadline_epoch=$(date -d "$response_by_time" +%s 2>/dev/null || echo "0")` を /bin/bash 3.2 で其の儘走らせて `|| echo "0"` が現に何を作るかを measure する。
三つの date: ① /bin/date(BSD・当機の既定 PATH)② gdate(GNU coreutils・raw/stub_gnu/date → /opt/homebrew/bin/gdate を PATH 先頭に置き third_pc(Linux)の姿を写す)③ python3 datetime.fromisoformat(直しの候補)。入力= 正しい時刻 4 形 + 毒 6 形。"""
import os, sys, time, subprocess
D = sys.argv[1]; sys.path.insert(0, D + '/raw'); import kaki as K
INPUTS = [('past_Z', '2020-01-01T00:00:00Z'), ('past_+09:00', '2026-09-17T12:00:00+09:00'), ('past_+0900', '2026-09-17T12:00:00+0900'), ('naive_space', '2026-09-17 12:00:00'), ('future_Z', '2099-01-01T00:00:00Z'),
          ('abc', 'abc'), ('empty', ''), ('big_2^63', '9223372036854775808'), ('neg', '-5'), ('epoch_@', '@1757000000'), ('now_word', 'now'), ('injection', '$(echo INJ92)')]
def run(cmd, env=None, shell=False):
    p = subprocess.run(cmd, capture_output=True, text=True, env=env, shell=shell); return p.stdout.strip().replace('\n', '␊'), p.stderr.strip().replace('\n', '␊')[:90], p.returncode
GNU = dict(os.environ); GNU['PATH'] = D + '/raw/stub_gnu:' + os.environ['PATH']
koku = time.strftime('%Y-%m-%dT%H:%M:%S%z'); out = [f'# 20 date の方言 ㋑ / 刻 {koku} / /bin/bash 3.2 verbatim 行 / gdate= {os.path.realpath(D + "/raw/stub_gnu/date")}']
rows = [('形', '入力', '① /bin/date -d X +%s', '① BSD -j -f %Y-%m-%dT%H:%M:%S%z', '② gdate -d X +%s', '③ py fromisoformat', 'verbatim行 /bin/date', 'verbatim行 gdate')]
for name, s in INPUTS:
    a = run(['/bin/date', '-d', s, '+%s']); b = run(['/bin/date', '-j', '-f', '%Y-%m-%dT%H:%M:%S%z', s, '+%s']); c = run(['gdate', '-d', s, '+%s'], env=GNU)
    d = run(['python3', '-c', 'import sys;from datetime import datetime\ntry: print(int(datetime.fromisoformat(sys.argv[1]).timestamp()))\nexcept Exception as e: print("ERR", type(e).__name__, file=sys.stderr); sys.exit(1)', s])
    V = 'response_by_time="$1"; deadline_epoch=$(date -d "$response_by_time" +%s 2>/dev/null || echo "0"); printf "[%s]" "$deadline_epoch"'
    e = run(['/bin/bash', '-c', V, '_', s]); f = run(['/bin/bash', '-c', V, '_', s], env=GNU)
    fmt = lambda r: f'{r[0] or "(空)"} rc{r[2]}' + (f' ⟨{r[1]}⟩' if r[1] else '')
    rows.append((name, repr(s), fmt(a), fmt(b), fmt(c), fmt(d), f'{e[0]} rc{e[2]}', f'{f[0]} rc{f[2]}'))
K.kaku_tsv(D + '/raw/20_date.tsv', rows[1:], header=rows[0])
w = [max(len(str(r[i])) for r in rows) for i in range(len(rows[0]))]
out += [' | '.join(str(x).ljust(w[i]) for i, x in enumerate(r)) for r in rows]
# 当機で date が何者か
for c in ('command -v date', '/bin/date -d 2>&1 | head -1', 'gdate --version | head -1', 'python3 --version'):
    r = run(c, shell=True); out.append(f'{c} → {r[0] or r[1]} rc{r[2]}')
r = run('PATH="%s/raw/stub_gnu:$PATH" command -v date' % D, shell=True); out.append(f'GNU 写しの PATH で command -v date → {r[0]} rc{r[2]}')
out.append('意味せぬ事: ② は third_pc の gdate と同版とは限らぬ(coreutils 9.11・当機の Homebrew)。③ は Python 3.14 の fromisoformat(3.11 以降は Z を受ける・3.10 以前は Z を拒む)。① BSD -j -f は書式一本ゆゑ Z や naive を受けぬ(其れ自体が方言の疵)。')
K.kaku(D + '/raw/20_date.txt', '\n'.join(out)); print('\n'.join(out))
