#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 30_an.py ―― ★三族の直し案を、生器の写しへ当てて 仮器を建てる。生器へは一字も書かぬ。★
#
#   本器が作る物は二つ:
#     ⑴ .nama/ki_<案>/… ―― 走らせて対照を取る為の ★仮器★
#     ⑵ an/<案>_<門>.diff ―― 紙に載せる ★逐語の diff★(据ゑぬ・回付用)
#
#   ★掟★ str.replace は ★当たつた数を数へて assert する★。
#          当たらぬ置換は黙つて素通りし「直つた様に見える」故。
#          (memory: str_replace patch must assert count)
import io, os, sys, subprocess, difflib

NAMA = '.nama'
AN   = 'an'
SEIKI = {
    'gate4':   '../../../scripts/checks/karo_mac_gate4.sh',
    'dasumae': '../../../scripts/checks/karo_mac_dasumae_gate.sh',
}

def okikae(s, furu, atarashii, kazu, fuda):
    u"""★当たつた数を数へてから置換する★"""
    n = s.count(furu)
    if n != kazu:
        sys.stderr.write(u'★倒す: %s ―― 当たり %d 本(宣 %d 本)★\n' % (fuda, n, kazu))
        sys.exit(3)
    return s.replace(furu, atarashii)

# ---- 生器の逐語(置換の的) ----
T_NUM   = 'num_same_op(){ [ "${1:-}" -ge 0 ] 2>/dev/null; [ $? -le 1 ]; }'
T_LOCAL = '  local name="$1" dflt="$2" out="$3" st raw'
T_IF    = '  if num_same_op "$raw"; then eval "$out=\\$raw"; return 0; fi'
T_SAY   = '  say "★閾 ${name} が比較器で扱へぬ(「${raw}」) ―― 既定 ${dflt} へ倒す(fail-closed)★"'

# ---- 案甲 ―― 番人の幅を閾ごとに絞る ----
KOU_NUM = T_NUM + u'''
# ★案甲(第50弾)★ 幅が広過ぎる ―― 上の num_same_op は「0以上か」でなく「數として讀めたか」
#   しか問うて居らぬ([ $? -le 1 ] が 偽(rc=1) をも可とする)。∴ 負値・零・天井無しが素通りする。
#   ★後段と同じ演算子の儘、床と天を課す。★ rc=2(讀めぬ)も || で 1 へ落ちる ―― fail-closed。
num_in_range(){ # $1=値 $2=床 $3=天
  [ "${1:-}" -ge "${2:-0}" ] 2>/dev/null || return 1
  [ "${1:-}" -le "${3:-9223372036854775806}" ] 2>/dev/null || return 1
}'''
KOU_LOCAL = '  local name="$1" dflt="$2" out="$3" lo="${4:-0}" hi="${5:-1048576}" st raw'
KOU_IF    = '  if num_in_range "$raw" "$lo" "$hi"; then eval "$out=\\$raw"; return 0; fi'
KOU_SAY   = '  say "★閾 ${name} が比較器で扱へぬ か 範囲外(「${raw}」・許 ${lo}..${hi}) ―― 既定 ${dflt} へ倒す(fail-closed)★"'

# ---- 案乙 ―― 後段の器そのもので検める ----
OTSU_TMO = T_NUM + u'''
# ★案乙(第50弾)★ 後段の語法が別 ―― DASUMAE_READ_TIMEOUT の後段は [ -ge ] に非ず ★timeout(1)★。
#   故に [ -ge ] で検めると ⑴timeout が受ける 10m を拒み ⑵timeout が拒む「 50 」を通す。
#   ★検め器を後段の器 其の物に替へる。★ 加へて 數として讀める時のみ 床1/天86400 を課す
#   (timeout 0 は ★時限を掛けぬ★ の意ゆゑ ―― 實測 .nama/20_moto.tsv)。
tmo_ok(){ # $1=値 ―― timeout(1) が受けるか
  if [ "${1:-}" -ge 0 ] 2>/dev/null; then
    [ "${1:-}" -ge 1 ] 2>/dev/null || return 1
    [ "${1:-}" -le 86400 ] 2>/dev/null || return 1
  fi
  [ -n "${TIMEOUT_BIN:-}" ] || return 0
  "$TIMEOUT_BIN" "${1:-}" true >/dev/null 2>&1
  [ $? -ne 125 ]
}'''
OTSU_LOCAL = '  local name="$1" dflt="$2" out="$3" chk="${4:-num_same_op}" st raw'
OTSU_IF    = '  if "$chk" "$raw"; then eval "$out=\\$raw"; return 0; fi'

# ---- 案丙 ―― 刷る前に濾す ----
HEI_SHOW = T_NUM + u'''
# ★案丙(第50弾)★ 門票への行注入 ―― 拒んだ値を ★逐語で★ 刷る故、値が門票を一行 書く。
#   ★形だけ刷り、生は刷らぬ。★ LC_ALL=C の [:print:] は 改行も和字も印字可に非ず
#   ∴ 「門 通。出してよい。」の語も潰れる(實測 .nama/20_moto.tsv koshi_C_locale)。
#   生の byte 数を併記する ―― 截つた事を黙らぬ為。
safe_show(){
  local s="${1:-}" n
  n=$(printf '%s' "$s" | wc -c | tr -d ' ')
  printf '%s' "$s" | LC_ALL=C tr -c '[:print:]' '?' | cut -c1-40
  printf '(生 %s byte)' "$n"
}'''
HEI_SAY = '  say "★閾 ${name} が比較器で扱へぬ(「$(safe_show "$raw")」) ―― 既定 ${dflt} へ倒す(fail-closed)★"'

def kou(s, mon):
    s = okikae(s, T_NUM,   KOU_NUM,   1, u'甲/num')
    s = okikae(s, T_LOCAL, KOU_LOCAL, 1, u'甲/local')
    s = okikae(s, T_IF,    KOU_IF,    1, u'甲/if')
    s = okikae(s, T_SAY,   KOU_SAY,   1, u'甲/say')
    if mon == 'gate4':
        s = okikae(s, 'fix_threshold GATE4_MAX_FILE_MB 50 MAXF',
                      'fix_threshold GATE4_MAX_FILE_MB 50 MAXF 0 1048576', 1, u'甲/呼 MAXF')
        s = okikae(s, 'fix_threshold GATE4_MAX_TOTAL_MB 100 MAXT',
                      'fix_threshold GATE4_MAX_TOTAL_MB 100 MAXT 0 1048576', 1, u'甲/呼 MAXT')
    else:
        s = okikae(s, 'fix_threshold DASUMAE_READ_TIMEOUT 10 SAFE_SIZE_TMO',
                      'fix_threshold DASUMAE_READ_TIMEOUT 10 SAFE_SIZE_TMO 1 86400', 1, u'甲/呼 TMO')
        s = okikae(s, 'fix_threshold DASUMAE_MAX_BYTES 10485760 MAXB',
                      'fix_threshold DASUMAE_MAX_BYTES 10485760 MAXB 0 1099511627776', 1, u'甲/呼 MAXB')
    return s

def otsu(s, mon):
    if mon != 'dasumae':
        return None   # ★時限閾は dasumae にしか無い ―― gate4 へは当てぬ(当てる物が無い)★
    s = okikae(s, T_NUM,   OTSU_TMO,   1, u'乙/tmo')
    s = okikae(s, T_LOCAL, OTSU_LOCAL, 1, u'乙/local')
    s = okikae(s, T_IF,    OTSU_IF,    1, u'乙/if')
    s = okikae(s, 'fix_threshold DASUMAE_READ_TIMEOUT 10 SAFE_SIZE_TMO',
                  'fix_threshold DASUMAE_READ_TIMEOUT 10 SAFE_SIZE_TMO tmo_ok', 1, u'乙/呼 TMO')
    return s

def hei(s, mon):
    s = okikae(s, T_NUM, HEI_SHOW, 1, u'丙/show')
    s = okikae(s, T_SAY, HEI_SAY,  1, u'丙/say')
    return s

# ---- 合(三族を併せた形) ----
GOU_NUM = T_NUM + KOU_NUM[len(T_NUM):] + OTSU_TMO[len(T_NUM):] + HEI_SHOW[len(T_NUM):]
GOU_LOCAL = ('  local name="$1" dflt="$2" out="$3" chk="${4:-num_in_range}"'
             ' lo="${5:-0}" hi="${6:-1048576}" st raw')
GOU_IF  = '  if "$chk" "$raw" "$lo" "$hi"; then eval "$out=\\$raw"; return 0; fi'
GOU_SAY = ('  say "★閾 ${name} が比較器で扱へぬ か 範囲外(「$(safe_show "$raw")」・許 ${lo}..${hi})'
           ' ―― 既定 ${dflt} へ倒す(fail-closed)★"')

def gou(s, mon):
    s = okikae(s, T_NUM,   GOU_NUM,   1, u'合/num')
    s = okikae(s, T_LOCAL, GOU_LOCAL, 1, u'合/local')
    s = okikae(s, T_IF,    GOU_IF,    1, u'合/if')
    s = okikae(s, T_SAY,   GOU_SAY,   1, u'合/say')
    if mon == 'gate4':
        s = okikae(s, 'fix_threshold GATE4_MAX_FILE_MB 50 MAXF',
                      'fix_threshold GATE4_MAX_FILE_MB 50 MAXF num_in_range 0 1048576', 1, u'合/MAXF')
        s = okikae(s, 'fix_threshold GATE4_MAX_TOTAL_MB 100 MAXT',
                      'fix_threshold GATE4_MAX_TOTAL_MB 100 MAXT num_in_range 0 1048576', 1, u'合/MAXT')
    else:
        s = okikae(s, 'fix_threshold DASUMAE_READ_TIMEOUT 10 SAFE_SIZE_TMO',
                      'fix_threshold DASUMAE_READ_TIMEOUT 10 SAFE_SIZE_TMO tmo_ok 1 86400', 1, u'合/TMO')
        s = okikae(s, 'fix_threshold DASUMAE_MAX_BYTES 10485760 MAXB',
                      'fix_threshold DASUMAE_MAX_BYTES 10485760 MAXB num_in_range 0 1099511627776',
                      1, u'合/MAXB')
    return s

AN_TACHI = [(u'kou', kou), (u'otsu', otsu), (u'hei', hei), (u'gou', gou)]

def main():
    tsv = [u'\t'.join([u'案', u'門', u'仮器', u'生 byte', u'仮 byte', u'diff 行', u'刷つた diff'])]
    for an, fn in AN_TACHI:
        d = os.path.join(NAMA, 'ki_' + an)
        if not os.path.isdir(d):
            os.makedirs(d)
        for mon, path in sorted(SEIKI.items()):
            sei = io.open(path, encoding='utf-8').read()
            kari = fn(sei, mon)
            if kari is None:
                tsv.append(u'\t'.join([an, mon, u'(当てず)', u'%d' % len(sei.encode()),
                                       u'―', u'0', u'★此の族は此の門に的が無い★']))
                continue
            dest = os.path.join(d, os.path.basename(path))
            with io.open(dest, 'w', encoding='utf-8', newline='') as fh:
                fh.write(kari)
            os.chmod(dest, 0o755)
            dl = list(difflib.unified_diff(sei.split('\n'), kari.split('\n'),
                                           fromfile=u'a/' + os.path.basename(path),
                                           tofile=u'b/' + os.path.basename(path),
                                           lineterm=u'', n=3))
            dp = os.path.join(AN, u'%s_%s.diff' % (an, mon))
            with io.open(dp, 'w', encoding='utf-8', newline='') as fh:
                fh.write(u'\n'.join(dl) + u'\n')
            tsv.append(u'\t'.join([an, mon, dest, u'%d' % len(sei.encode()),
                                   u'%d' % len(kari.encode()), u'%d' % len(dl), dp]))
    sys.stdout.write(u'\n'.join(tsv) + u'\n')
    return 0

if __name__ == '__main__':
    sys.exit(main())
