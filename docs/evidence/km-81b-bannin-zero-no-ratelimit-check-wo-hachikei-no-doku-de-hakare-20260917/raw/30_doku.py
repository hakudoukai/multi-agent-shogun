# -*- coding: utf-8 -*-
"""30 ㋒(第77弾 km-81b)―― 的 scripts/ratelimit_check.sh から ★逐語で★(錨= 行の字面・一致 1 本を assert)數比較器の左項へ値を運ぶ六つの口の区画を切り出し、
束内の写し器(/bin/bash 3.2.57・的の set -euo pipefail を頭に置く)へ八形の毒を当てる。repo へ 0 字・稼働 process 不觸。
口: P1 ctx(L339+L396-406) / P2 CODEX_LIMIT_HITS(L417-427) / P3 CLAUDE_5H_UTIL・P4 CLAUDE_7D_UTIL(L458-475) / P5 CLAUDE_TODAY_TOTAL(L490-501) / P6 LANG_MODE(L435-439 字面) / P7 argv --lang(L13-25)。
毒八形= 未設定 / 空文字 / 空白のみ(半角・全角) / 20桁(2^63超) / 負数 / 域外の十進(2・01・+1) / 先頭改行付き(␊1) / 正常値(陰性対照)。★両対照★= 陽性(正しい別の値で枝が変はる= 器が生きて居る)/ 陰性(正常値で黙つて通る)。
補(八形の外・現實に python が刷り得る値)= abc / None / ? / 101 / 1e3。値は env で渡す(bash は env を其の名の変数として受ける・未設定= env に無し)。"""
import os, sys, re, time, subprocess
D = sys.argv[1]; sys.path.insert(0, D + '/raw'); import kaki as K; M = '/Users/momizimac/multi-agent-shogun'; T = 'scripts/ratelimit_check.sh'; BASH = '/bin/bash'
L = open(M + '/' + T, encoding='utf-8').read().split('\n')
def one(pred, what):
    h = [i for i, l in enumerate(L) if pred(l)]; assert len(h) == 1, f'{what}: {len(h)} 本'; return h[0]
def upto(i, endpred, what):
    j = i + 1
    while not endpred(L[j]): j += 1
    return j
SET = L[one(lambda l: l == 'set -euo pipefail', 'set')]
c0 = one(lambda l: l == 'CODEX_CONTEXT_WARN=20', 'const'); CONST = L[c0:c0 + 3]; assert CONST[2].startswith('CODEX_LIMIT_HITS_WARN='), CONST
ws, st = one(lambda l: l == 'CODEX_WARNINGS=""', 'W'), one(lambda l: l == 'CODEX_STATUS="OK"', 'S')
z = one(lambda l: l.strip() == '[[ -z "$ctx" ]] && ctx="?"', 'ctx guard')
p1s = [i for i, l in enumerate(L) if l.strip() == 'if [[ "$ctx" != "?" ]]; then'][0]  # 二本在る(L396/L527)・先の一本(CODEX_WARNINGS を持つ方)を取り次行で assert
assert L[p1s + 1].strip() == 'if [[ "$ctx" -lt "$CODEX_CONTEXT_CRIT" ]]; then'; p1e = upto(p1s, lambda l: l.rstrip() == '        fi', 'P1 end'); assert 'CODEX_STATUS="CRITICAL"' in '\n'.join(L[p1s:p1e + 1])
p2s = one(lambda l: l.strip() == 'CODEX_LIMIT_HITS="${CODEX_LIMIT_HITS:-0}"', 'P2'); p2e = upto(p2s, lambda l: l.rstrip() == '    fi', 'P2 end')
p3s = one(lambda l: l.strip() == 'if [[ -n "$CLAUDE_5H_UTIL" && "$CLAUDE_5H_UTIL" != "?" ]]; then', 'P3'); sd = one(lambda l: l.strip() == 'if [[ "$sd_int" -ge 80 ]]; then', 'sd'); p3e = upto(sd, lambda l: l.rstrip() == '        fi', 'P3 end')
p5s = one(lambda l: l.strip() == 'if [[ "$CLAUDE_TODAY_TOTAL" -gt 0 ]]; then', 'P5'); p5e = upto(p5s, lambda l: l.rstrip() == '    fi', 'P5 end')
p6s = [i for i, l in enumerate(L) if l.strip() == 'if [[ "$LANG_MODE" == "en" ]]; then'][0]; p6e = upto(p6s, lambda l: l.rstrip() == 'fi', 'P6 end')
p7s = one(lambda l: l == 'LANG_MODE="ja"', 'P7'); p7e = upto(p7s, lambda l: l == 'done', 'P7 end')
today = L[one(lambda l: l.startswith('TODAY=$(date '), 'TODAY')]; cs = one(lambda l: l == 'CLAUDE_STATUS="OK"', 'CS'); r5 = one(lambda l: l == 'CLAUDE_5H_RESET=""', 'r5'); r7 = one(lambda l: l == 'CLAUDE_7D_RESET=""', 'r7')
d0 = one(lambda l: l == 'CLAUDE_TODAY_DETAIL=""', 'd0'); dd = one(lambda l: l == 'CLAUDE_DATA_DATE=""', 'dd'); se_ = one(lambda l: l == 'CLAUDE_SESSIONS=""', 'se'); me_ = one(lambda l: l == 'CLAUDE_MESSAGES=""', 'me')
TAIL_C = 'printf "STATUS=%s WARN=[%s] VALUE=[%s]\\n" "$CODEX_STATUS" "$CODEX_WARNINGS" "${{VAR}-<unset>}"'  # {VAR} を replace で埋める(% 書式は printf の %s と衝突する ―― 初走の疵・.first)
KUCHI = {
 'P1 ctx(tmux 由来・L339 番人+L396-406)': dict(var='ctx', lines=f'L{z+1},L{p1s+1}-{p1e+1}', script='\n'.join([SET] + CONST + [L[ws], L[st], 'agent=ashigaru9', L[z].strip()] + L[p1s:p1e + 1] + [TAIL_C.replace('{VAR}', 'ctx')]), normal='50', pos=[('陽性対照 5(<CRIT 10)', '5'), ('陽性対照 15(<WARN 20)', '15')], dom=[('補 域外 101(百分率超)', '101')]),
 'P2 CODEX_LIMIT_HITS(grep -c 由来・L417-427)': dict(var='CODEX_LIMIT_HITS', lines=f'L{p2s+1}-{p2e+1}', script='\n'.join([SET] + CONST + [L[ws], L[st]] + L[p2s:p2e + 1] + [TAIL_C.replace('{VAR}', 'CODEX_LIMIT_HITS')]), normal='0', pos=[('陽性対照 3(=WARN 3)', '3')], dom=[]),
 'P3 CLAUDE_5H_UTIL(OAuth API 由来・L458-475)': dict(var='CLAUDE_5H_UTIL', lines=f'L{p3s+1}-{p3e+1}', script='\n'.join([SET, L[cs], L[r5], L[r7], 'CLAUDE_7D_UTIL=10.0'] + L[p3s:p3e + 1] + ['fi', 'printf "STATUS=%s VALUE=[%s]\\n" "$CLAUDE_STATUS" "${CLAUDE_5H_UTIL-<unset>}"']), normal='10.0', pos=[('陽性対照 85.5(>=80)', '85.5')], dom=[('補 域外 101', '101'), ('補 1e3', '1e3'), ('補 None(python の null)', 'None'), ('補 ?(python の既定)', '?')]),
 'P4 CLAUDE_7D_UTIL(OAuth API 由来・L468-475・番人無し)': dict(var='CLAUDE_7D_UTIL', lines=f'L{sd-1}-{p3e+1}', script='\n'.join([SET, L[cs], L[r5], L[r7], 'CLAUDE_5H_UTIL=10.0'] + L[p3s:p3e + 1] + ['fi', 'printf "STATUS=%s VALUE=[%s]\\n" "$CLAUDE_STATUS" "${CLAUDE_7D_UTIL-<unset>}"']), normal='10.0', pos=[('陽性対照 85.5(>=80)', '85.5')], dom=[('補 域外 101', '101'), ('補 1e3', '1e3'), ('補 None(python の null)', 'None'), ('補 ?(python の既定)', '?')]),
 'P5 CLAUDE_TODAY_TOTAL(python sum 由来・L490-501)': dict(var='CLAUDE_TODAY_TOTAL', lines=f'L{p5s+1}-{p5e+1}', script='\n'.join([SET, today, L[dd], L[d0], L[se_], L[me_]] + L[p5s:p5e + 1] + ['printf "VALUE=[%s]\\n" "${CLAUDE_TODAY_TOTAL-<unset>}"']), normal='0', pos=[('陽性対照 123456', '123456')], dom=[('補 abc', 'abc')]),
 'P6 LANG_MODE(argv 由来・L435-439・字面 ==)': dict(var='LANG_MODE', lines=f'L{p6s+1}-{p6e+1}', script='\n'.join([SET, today] + L[p6s:p6e + 1] + ['printf "VALUE=[%s]\\n" "${LANG_MODE-<unset>}"']), normal='ja', pos=[('陽性対照 en', 'en')], dom=[('補 域外 xx', 'xx'), ('補 EN(大文字)', 'EN')]),
}
POIS = [('未設定', None), ('空文字', ''), ('空白(半角)', ' '), ('空白(全角 U+3000)', '　'), ('20桁(2^63超)', '99999999999999999999'), ('負数 -5', '-5'), ('域外の十進 2', '2'), ('域外の十進 01', '01'), ('域外の十進 +1', '+1'), ('先頭改行付き ␊1', '\n1'), ('補 非数 abc', 'abc')]
vis = lambda s: '<unset>' if s is None else (s.replace('\n', '␊').replace('　', '<U+3000>').replace(' ', '<SP>') or '<empty>')
def branch(k, so):
    if k.startswith('P5'): return 'Tokens 刷る' if 'Tokens' in so else 'Tokens 刷らず'
    if k.startswith('P6'): return 'en 見出し' if 'Rate Limit Status' in so else ('ja 見出し' if 'レートリミット' in so else '見出し無し')
    m = re.search(r'STATUS=(\S+)', so); s = m.group(1) if m else '?'
    if k.startswith('P3') or k.startswith('P4'): return ('⚠️ ' if '⚠️' in so else '') + s
    return s
def fell(rc, sel, br, nb, label):
    if rc != 0: return ('★鳴つて止まる(rc≠0・stderr 有)★' if sel else '★黙つて止まる(rc≠0・stderr 0)★')
    if br == nb: return ('陰性対照・黙つて通る(宣どおり)' if label.startswith('正常値') else ('黙つて通る(正常と同じ枝)' + ('' if sel else ' ★毒が見えぬ★')))
    return ('陽性対照・枝が変はる(器は生きて居る)' if label.startswith('陽性') else ('★黙つて別枝★' if sel == 0 else '刷つて別枝'))
koku = time.strftime('%Y-%m-%dT%H:%M:%S%z'); bv = subprocess.run([BASH, '-c', 'echo $BASH_VERSION'], capture_output=True, text=True).stdout.strip()
out = [f'# 30 ㋒ / 刻 {koku} / 的 {T}(disk = HEAD・sha16 7f1e0311)/ 写し器= {BASH} {bv} / 頭= L8 `{SET}` + 閾 L{c0+1}-{c0+3} 逐語 / env LANG={os.environ.get("LANG","(無)")} LC_ALL={os.environ.get("LC_ALL","(無)")}']
tbl = ['口\t形\t値(写し)\trc\tstdout(頭 90 字)\tstderr 行数\tstderr 逐語(束 path を raw/ に縮め・頭 150 字・改行は␊)\t枝\t倒れ先']
for k, cfg in KUCHI.items():
    sp = D + f'/raw/30_{k[:2]}.sh'; K.kaku(sp, cfg['script']); out.append(f'{k}: 区画 {cfg["lines"]} → 写し器 raw/30_{k[:2]}.sh({cfg["script"].count(chr(10))+1} 行)')
    forms = [('正常値 ' + cfg['normal'], cfg['normal'])] + cfg['pos'] + POIS + cfg['dom']
    nb = None
    for label, val in forms:
        env = {kk: vv for kk, vv in os.environ.items() if kk != cfg['var']}
        if val is not None: env[cfg['var']] = val
        p = subprocess.run([BASH, sp], capture_output=True, env=env)
        so = p.stdout.decode('utf-8', 'replace'); se = p.stderr.decode('utf-8', 'replace').rstrip('\n').replace(D + '/raw/', 'raw/'); sel = se.count('\n') + 1 if se else 0
        br = branch(k, so)
        if nb is None: nb = br
        tbl.append('\t'.join([k[:2], label, vis(val), str(p.returncode), so.strip().replace('\n', '␊').replace('\t', '␉')[:90], str(sel), se.replace('\n', '␊').replace('\t', '␉')[:150], br, fell(p.returncode, sel, br, nb, label)]))
    if k.startswith('P2'):
        env = {kk: vv for kk, vv in os.environ.items() if kk != 'CODEX_LIMIT_HITS'}; env['CODEX_LIMIT_HITS'] = '　'; env['LC_ALL'] = 'C'
        p = subprocess.run([BASH, sp], capture_output=True, env=env); so = p.stdout.decode('utf-8', 'replace'); se = p.stderr.decode('utf-8', 'replace').rstrip('\n').replace(D + '/raw/', 'raw/'); sel = se.count('\n') + 1 if se else 0
        tbl.append('\t'.join(['P2', '補 空白(全角)を LC_ALL=C で(tr [:space:] の locale 差)', '<U+3000>', str(p.returncode), so.strip().replace('\n', '␊')[:90], str(sel), se.replace('\n', '␊')[:150], branch(k, so), fell(p.returncode, sel, branch(k, so), 'OK', '補')]))
# P7 argv
sp = D + '/raw/30_P7.sh'; K.kaku(sp, '\n'.join([SET] + L[p7s:p7e + 1] + ['printf "VALUE=[%s]\\n" "$LANG_MODE"'])); out.append(f'P7 argv --lang(L{p7s+1}-{p7e+1}・case 字面): 写し器 raw/30_P7.sh')
for label, args in [('正常値 (引数無し)', []), ('陽性対照 --lang en', ['--lang', 'en']), ('--lang のみ(値が無い)', ['--lang']), ('--lang 空文字', ['--lang', '']), ('--lang 空白', ['--lang', ' ']), ('--lang 域外 xx', ['--lang', 'xx']), ('--lang 先頭改行 ␊en', ['--lang', '\nen']), ('未知の旗 --bogus', ['--bogus'])]:
    p = subprocess.run([BASH, sp] + args, capture_output=True); so = p.stdout.decode('utf-8', 'replace'); se = p.stderr.decode('utf-8', 'replace').rstrip('\n').replace(D + '/raw/', 'raw/'); sel = se.count('\n') + 1 if se else 0
    m = re.search(r'VALUE=\[(.*)\]', so, re.S); br = ('VALUE=' + vis(m.group(1))) if m else ('止(VALUE 無し)' + ('・stdout: ' + so.strip().replace('\n', '␊')[:40] if so.strip() else ''))
    tbl.append('\t'.join(['P7', label, ' '.join(vis(a) for a in args) or '(無)', str(p.returncode), so.strip().replace('\n', '␊')[:90], str(sel), se.replace('\n', '␊')[:150], br, fell(p.returncode, sel, br, 'VALUE=ja', label)]))
out.append('枝の讀み方: P1/P2= CODEX_STATUS(OK/WARNING/CRITICAL)/ P3/P4= ⚠️ の有無+CLAUDE_STATUS / P5= Tokens 段の有無 / P6= 見出しの言語 / P7= LANG_MODE の値。')
out.append('倒れ先の語: 「黙つて通る ★毒が見えぬ★」= 毒が正常と同じ枝を踏み rc0・stderr 0 / 「黙つて別枝」= 毒が別の枝を踏み rc0・stderr 0(偽の警報 or 警報の抜け)/ 「鳴つて止まる」= rc≠0 で stderr に理由(set -u 等)/ 「黙つて止まる」= rc≠0 で stderr 0。')
out.append('此の器が意味せぬ事: 写し器は bash 3.2.57(此の PC の唯一の bash)。的が走る筈の Linux(bash 5.x)での [[ ]] 算術評価の差は測つて居らぬ。P1-P5 は「値が口まで届いた後」の挙動であり、此の checkout では L28 で止まるゆゑ届かぬ(45)。')
out.append('疵(初走 .first): stderr 欄が束の path(110 字超)に食はれ本文が見えなんだ ―― path を raw/ に縮めて再走。數(rc・行数・枝)は初走と一つも動いて居らぬ(diff で検む)。')
K.kaku(D + '/raw/30_doku.txt', '\n'.join(out)); K.kaku(D + '/raw/30_doku.tsv', '\n'.join(tbl)); print('\n'.join(out)); print('\n'.join(tbl))
