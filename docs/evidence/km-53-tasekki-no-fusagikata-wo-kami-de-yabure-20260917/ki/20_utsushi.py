# -*- coding: utf-8 -*-
"""usage: 20_utsushi.py <outdir>
★生器へ一字も書かぬ★ ―― 門と照合器の写しを束内 utsushi/ へ建て、写しへ二案を当てる。
置換は ★必ず count を assert★ する(無一致の置換は「直つた顔」をする ―― 己の memory)。
"""
import sys, os, shutil, hashlib
outdir = sys.argv[1]
root = os.getcwd()
UT = os.path.join(os.path.dirname(outdir), 'utsushi')
os.makedirs(UT, exist_ok=True)
SRC_G = os.path.join(root, 'scripts/checks/karo_mac_dasumae_gate.sh')
SRC_V = os.path.join(root, 'scripts/checks/karo_mac_manifest_verify.py')

def sha16(p):
    return hashlib.sha256(open(p,'rb').read()).hexdigest()[:16]

log=[]
log.append('=== 写しの素(生器・讀取のみ) ===')
for p in (SRC_G, SRC_V):
    log.append('%s\tsha16=%s\tbytes=%d' % (os.path.relpath(p,root), sha16(p), os.path.getsize(p)))
assert sha16(SRC_G)=='e11f0d0142549086', '門の版が紙の刻と違ふ: '+sha16(SRC_G)
assert sha16(SRC_V)=='a507c998c7bd6485', '照合器の版が紙の刻と違ふ: '+sha16(SRC_V)
log.append('★紙(742972a4f88885db)が対象とした版と一致 ―― 二案の diff は当たる。★')

shutil.copy2(SRC_V, os.path.join(UT,'karo_mac_manifest_verify.py'))
shutil.copy2(SRC_G, os.path.join(UT,'gate_base.sh'))

OLD = '''    local vrc
    if [ -n "${KM_GATE_MANIFEST_BASE+set}" ]; then
      python3 "$(dirname "$0")/karo_mac_manifest_verify.py" "$man" "$KM_GATE_MANIFEST_BASE"
      vrc=$?
      say "條① 基点=★引数 明示★(KM_GATE_MANIFEST_BASE)"
    else
      python3 "$(dirname "$0")/karo_mac_manifest_verify.py" "$man"
      vrc=$?
      say "條① 基点=既定(器の在處から導いた repo 根・cwd に依らぬ) ―― ★倒した事を刷る(裁322952 乙)★"
    fi
'''

NEW_I = '''    local vrc
    case "$(env_state KM_GATE_MANIFEST_BASE)" in
      empty|blank)
        say "★條① 基点 KM_GATE_MANIFEST_BASE が空/空白($(env_state KM_GATE_MANIFEST_BASE)) ―― cwd 相対は許さぬ。絶対 path を渡すか unset にせよ★"
        vrc=2 ;;
      value)
      python3 "$(dirname "$0")/karo_mac_manifest_verify.py" "$man" "$KM_GATE_MANIFEST_BASE"
      vrc=$?
      say "條① 基点=★引数 明示★(KM_GATE_MANIFEST_BASE=${KM_GATE_MANIFEST_BASE})" ;;
      unset)
      python3 "$(dirname "$0")/karo_mac_manifest_verify.py" "$man"
      vrc=$?
      say "條① 基点=既定(器の在處から導いた repo 根・cwd に依らぬ) ―― ★倒した事を刷る(裁322952 乙)★" ;;
    esac
'''

NEW_RO = '''    local vrc
    case "$(env_state KM_GATE_MANIFEST_BASE)" in
      value)
      python3 "$(dirname "$0")/karo_mac_manifest_verify.py" "$man" "$KM_GATE_MANIFEST_BASE"
      vrc=$?
      say "條① 基点=★引数 明示★(KM_GATE_MANIFEST_BASE=${KM_GATE_MANIFEST_BASE})" ;;
      empty|blank)
        say "★條① 基点 KM_GATE_MANIFEST_BASE が空/空白($(env_state KM_GATE_MANIFEST_BASE)) ―― 既定(repo 根)へ倒す(★倒した事を刷る★・cwd 相対には★せぬ★)★"
        python3 "$(dirname "$0")/karo_mac_manifest_verify.py" "$man"
        vrc=$? ;;
      unset)
      python3 "$(dirname "$0")/karo_mac_manifest_verify.py" "$man"
      vrc=$?
      say "條① 基点=既定(器の在處から導いた repo 根・cwd に依らぬ) ―― ★倒した事を刷る(裁322952 乙)★" ;;
    esac
'''

src = open(SRC_G, encoding='utf-8').read()
n = src.count(OLD)
log.append('')
log.append('=== 置換 ―― ★count を assert★ ===')
log.append('OLD 塊の出現数 = %d (1 でなければ止める)' % n)
assert n == 1, '置換の的が %d 箇所 ―― 止める' % n

for nm, new in (('an_i', NEW_I), ('an_ro', NEW_RO)):
    dst = os.path.join(UT, 'gate_%s.sh' % nm)
    out = src.replace(OLD, new)
    assert out != src
    assert out.count(new) == 1
    open(dst, 'w', encoding='utf-8').write(out)
    os.chmod(dst, 0o755)
    log.append('%s\tsha16=%s\tbytes=%d\t行差=%+d' % (os.path.basename(dst), sha16(dst), os.path.getsize(dst),
               out.count('\n') - src.count('\n')))

log.append('')
log.append('=== 生器 不触の検め(前後で sha が動かぬ事) ===')
for p in (SRC_G, SRC_V):
    log.append('%s\tsha16=%s' % (os.path.relpath(p,root), sha16(p)))
open(os.path.join(outdir,'20_utsushi.txt'),'w',encoding='utf-8').write('\n'.join(log)+'\n')
print('\n'.join(log))
