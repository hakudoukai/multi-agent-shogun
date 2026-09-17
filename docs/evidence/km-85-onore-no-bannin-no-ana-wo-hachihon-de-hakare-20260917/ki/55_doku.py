# -*- coding: utf-8 -*-
"""55 ―― ㋒㋓ 毒十値を ★寫し器★ へ当てる。生器へは触れぬ(前後に sha16 を引いて證す)。
一つの値につき四欄を取る:
  ①rc ②枝(既定へ倒れたか・通つたか、下流の枝は何れか) ③報せ(刷つたか黙つたか)
  ④下流で何に成るか(何秒待つ・何 byte と比べる)
★器の報せ行と外の声(interpreter)は二欄に分ける★ ―― 分け方は下の RE_SOTO に宣す。"""
import os, sys, re, time, hashlib, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kaki as K
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
BUNDLE = os.path.abspath(os.path.join(HERE, ".."))
UTS = os.path.join(BUNDLE, "utsushi")
BASH = "/bin/bash"

# ★外の声(interpreter)の見分け(宣)★ bash 己の診断は argv0 を冠に付ける。
RE_SOTO = re.compile(r'^\S*utsushi/[A-Za-z0-9_]+\.sh:\s')

DOKU = [("0", u"0"), ("-0", u"-0"), ("-5", u"-5"),
        ("4294967295", u"4294967295"), ("4294967296", u"4294967296"),
        ("9223372036854775807", u"9223372036854775807"),
        ("9223372036854775808", u"9223372036854775808"),
        ("020", u"020"), ("", u"空文字"), ("+10", u"+10")]
TAISHOU = [("7", u"陽性対照 7"), ("abc", u"陰性対照 abc")]

UTSU = [
    dict(n="kou_health",   kata=u"甲", var="HEALTH_CHECK_COOLDOWN_SEC", kitei="300",
         rel="scripts/agent_health_check.sh",
         imi=lambda v: u"冷却 %s 秒として [ 0 -lt %s ] を引く" % (v, v)),
    dict(n="otsu_gate4",   kata=u"乙", var="GATE4_MAX_FILE_MB", kitei="50",
         rel="scripts/checks/karo_mac_gate4.sh",
         imi=lambda v: u"單 file の上限 %s MB として [ 1 -ge %s ] を引く" % (v, v)),
    dict(n="otsu_dasumae", kata=u"乙", var="DASUMAE_MAX_BYTES", kitei="10485760",
         rel="scripts/checks/karo_mac_dasumae_gate.sh",
         imi=lambda v: u"byte和の上限 %s byte として [ 6 -ge %s ] を引く" % (v, v)),
    dict(n="otsu_hook",    kata=u"乙", var="STOP_HOOK_STDIN_TIMEOUT", kitei="10",
         rel="scripts/stop_hook_inbox.sh",
         imi=lambda v: u"read -t %s 秒として stdin を待ち [ 経過 -ge %s ] を引く" % (v, v)),
]

def sha16f(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()[:16]

def mie(s):
    return s.replace("\n", u"␊").replace("\r", u"␍").replace("\t", u"␉")

def hashiru(name, var, val, stdin_data, cap):
    env = dict(os.environ)
    if val is None:
        env.pop(var, None)
    else:
        env[var] = val
    env["LC_ALL"] = "C.UTF-8" if sys.platform != "darwin" else "en_US.UTF-8"
    t0 = time.time()
    kiri = 0
    rfd = wfd = None
    kw = {}
    if stdin_data is None:
        # ★開いた儘の口★ ―― 何も書かず、閉ぢもせぬ。此れでしか「待つか否か」は測れぬ
        rfd, wfd = os.pipe()
        kw["stdin"] = rfd
    else:
        kw["input"] = stdin_data
    try:
        pr = subprocess.run([BASH, os.path.join(UTS, name + ".sh")], env=env,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            timeout=cap, **kw)
        rc, out, err = pr.returncode, pr.stdout, pr.stderr
    except subprocess.TimeoutExpired as e:
        rc, out, err, kiri = None, (e.stdout or b""), (e.stderr or b""), 1
    finally:
        for fd in (rfd, wfd):
            if fd is not None:
                os.close(fd)
    el = time.time() - t0
    out = out.decode("utf-8", "replace"); err = err.decode("utf-8", "replace")
    uke, eda, krc = u"(RESULT 無)", u"(RESULT 無)", u"―"
    for ln in out.split("\n"):
        if ln.startswith("RESULT\t"):
            c = ln.split("\t")
            uke = c[1]
            eda = c[2] if len(c) > 2 else u""
            krc = c[3] if len(c) > 3 else u"―"
    shirase, soto = [], []
    for ln in err.split("\n"):
        if not ln.strip():
            continue
        (soto if RE_SOTO.match(ln) else shirase).append(mie(ln))
    return dict(rc=rc, uke=uke, eda=eda, krc=krc, shirase=shirase, soto=soto, el=el, kiri=kiri)

t0 = time.time(); kiz = time.strftime("%Y-%m-%dT%H:%M:%S%z")
mae = dict((u["rel"], sha16f(os.path.join(ROOT, u["rel"]))) for u in UTSU)

ARI = b"x\0"      # stdin に物が在る路
NASHI = b""       # stdin が即 EOF の路

rows = []
def hitotsu(u, hyouji, val, michi, stdin_data, cap):
    r = hashiru(u["n"], u["var"], val, stdin_data, cap)
    taoreta = (r["uke"] == u["kitei"] and val != u["kitei"])
    rows.append([
        u["n"], u["kata"], hyouji, michi,
        ((u"打切(%.1fs)" % r["el"]) if r["rc"] is None else r["rc"]),
        r["krc"],
        r["uke"],
        (u"★既定へ倒れた★" if taoreta else u"通した") + u" / 下流の枝=" + r["eda"],
        (u"%d 行: " % len(r["shirase"])) + (u" ▫ ".join(r["shirase"]) if r["shirase"] else u"★黙つた★"),
        (u"%d 行: " % len(r["soto"])) + (u" ▫ ".join(r["soto"]) if r["soto"] else u"―"),
        (u["imi"](r["uke"]) if not r["kiri"]
         else u"閾=%s を受理し、物の来ぬ口で★待ち続けた★(受け皿は打切ゆゑ printf へ到達せず)"
              % (u"未設定" if val is None else (u"空文字" if val == "" else val)))
        + (u" ／ 経過 %.2f 秒%s" % (r["el"], u"(★3秒で打ち切り=待つ★)" if r["kiri"] else u"")),
    ])
    return r

for u in UTSU:
    for val, hyouji in DOKU + TAISHOU:
        hitotsu(u, hyouji, val, u"在り(stdin に物)", ARI, 20)
    # 未設定 も一つ取る(母數の端)
    hitotsu(u, u"未設定", None, u"在り(stdin に物)", ARI, 20)

# hook だけは「物の無い口」を別路で引く ―― 何秒待つかは此の路でしか見えぬ
for val, hyouji in DOKU + TAISHOU:
    hitotsu(UTSU[3], hyouji, val, u"無し(stdin 開いた儘・何も書かず・3秒で打切)", None, 3)

ato = dict((u["rel"], sha16f(os.path.join(ROOT, u["rel"]))) for u in UTSU)

K.kaku_tsv(os.path.join(BUNDLE, "nama", "55_doku.tsv"), rows,
           ["#寫し器", "型", "毒値", "路", "①rc(器)", "①rc(read)", "受け皿の値", "②枝",
            "③器の報せ(己の声)", "③外の声(interpreter)", "④下流で何に成るか"])

L = []
L.append(u"= 55 ―― ㋒ 毒十値 × 呼び方 / ㋓ 両対照 =")
L.append(u"刻=%s  経過=%.1f 秒  行=%d" % (kiz, time.time() - t0, len(rows)))
L.append(u"走らせた器 = /bin/bash %s" % subprocess.run([BASH, "--version"], stdout=subprocess.PIPE)
         .stdout.decode().split("\n")[0])
L.append(u"")
L.append(u"-- ★生器の不動の證★(毒を当てたのは寫しのみ) --")
warui = [k for k in mae if mae[k] != ato[k]]
for k in sorted(mae):
    L.append(u"  %s  前=%s  後=%s  %s" % (k, mae[k], ato[k], u"○不動" if mae[k] == ato[k] else u"★動いた★"))
L.append(u"  ★動いた生器 = %d 本★" % len(warui))
L.append(u"")
L.append(u"-- 二欄の分け方(宣) --")
L.append(u"  外の声(interpreter) = stderr の行で %s に当たる物(bash は己の診断に argv0 を冠す)" % RE_SOTO.pattern)
L.append(u"  器の報せ            = 其れ以外の stderr 行(_th_say / say / echo >&2 の出目)")
L.append(u"  改行・復帰・字送りは ␊␍␉ へ写して一行に畳む")
L.append(u"")
for u in UTSU:
    L.append(u"━━ %s(型=%s ・ 生器 %s ・ 閾 %s ・ 既定 %s) ━━"
             % (u["n"], u["kata"], u["rel"], u["var"], u["kitei"]))
    for r in rows:
        if r[0] != u["n"]:
            continue
        L.append(u"  [%s] 路=%s" % (r[2], r[3]))
        L.append(u"    ①rc(器)=%s  rc(read)=%s  受け皿=%s" % (r[4], r[5], r[6]))
        L.append(u"    ②枝  =%s" % r[7])
        L.append(u"    ③報せ=%s" % r[8])
        L.append(u"    ③外声=%s" % r[9])
        L.append(u"    ④下流=%s" % r[10])
    L.append(u"")
L.append(u"-- ★小結 ―― 表から機械で引いた要点★ --")

def yomu(n, michi):
    return [r for r in rows if r[0] == n and r[3].startswith(michi)]

matsu = [r[2] for r in yomu("otsu_hook", u"無し") if u"打切" in str(r[4])]
otosu = [r[2] for r in yomu("otsu_hook", u"無し")
         if u"字数=0" in r[7] and u"★黙つた★" in r[8]]
naku  = [r[2] for r in yomu("otsu_hook", u"無し")
         if u"字数=0" in r[7] and u"時限切れ" in r[8]]
L.append(u"  ⑴ otsu_hook・物の来ぬ口で★閾を受理し待ち續けた★(3秒で打切) = %d 値 : %s"
         % (len(matsu), u" / ".join(matsu)))
L.append(u"     内 4294967295 は ★甲も乙も通す★ ―― 是が 專任2 第56弾 km-78 の「136年待つ」の再現である")
L.append(u"  ⑵ otsu_hook・read に★拒まれ 0 字で先へ進み、而も器が黙つた★ = %d 値 : %s"
         % (len(otosu), u" / ".join(otosu)))
L.append(u"     ★此れが本弾最大の穴★ ―― hook 入力 JSON を丸ごと落とし、落とした事を報せぬ")
L.append(u"  ⑶ otsu_hook・0 字なのに★時限切れの報せを刷つた(偽報)★ = %d 値 : %s"
         % (len(naku), u" / ".join(naku)))
L.append(u"")
taore, toosu = [], []
for val, h in DOKU + TAISHOU:
    ku = [r for r in rows if r[2] == h and r[3].startswith(u"在り")]
    n = len([r for r in ku if u"既定へ倒れた" in r[7]])
    (taore if n == len(ku) else toosu).append(u"%s(%d/%d 本が倒した)" % (h, n, len(ku)))
L.append(u"  ⑷ 四本★悉く★既定へ倒した毒値 = %s" % (u" / ".join(taore) if taore else u"無し"))
L.append(u"  ⑸ 一本でも★通した★毒値 = %s" % (u" / ".join(toosu) if toosu else u"無し"))
L.append(u"")
L.append(u"  ⑹ ㋓ 両対照(同じ路・同じ駆動部で引いた) ―― 両の出目を共に書く")
for nm in [u"陽性対照 7", u"陰性対照 abc"]:
    for r in [x for x in rows if x[2] == nm and x[3].startswith(u"在り")]:
        L.append(u"     %-12s %-14s rc=%s 受け皿=%s ／ %s ／ %s"
                 % (nm, r[0], r[4], r[6], r[7], (r[8][:46] + u"…") if len(r[8]) > 46 else r[8]))
K.kaku(os.path.join(BUNDLE, "nama", "55_doku.txt"), u"\n".join(L))
sys.exit(6 if warui else 0)
