# -*- coding: utf-8 -*-
"""㋓ 害の広さ ―― 「素の空白名の行」が何行在るかを disk と樹の二欄で數へる(專任2 km-109)。

★定義(逐語・數へる前に此處へ書く)★
  臺帳らしき紙 = b"sha256=" を含む ★常体(S_ISREG)★ の file(名では判ぜぬ)
  甲(広い定義) = 其の紙の行の内、★則①が当たり・則②も当たり・剥ぎ後の出目が違ふ★ 行
                 (= 讀み手が ★切り落した★ 行。名に空白が在るとは限らぬ ―― bytes=/lines= が
                    path と sha256 の間に在る行も此處に落ちる)
  乙(狭い定義) = 甲の内、★①の出目と②の出目の差にある語が 悉く 「語=」形でない★ 行
                 (= 真に「名に空白が在る」と疑へる行)
  丙(對照)     = ★則②が当たり・則①が外れた★ 行(= 括つた空白名。正規の書き手が出す形)
  測れぬ       = 行が長過ぎて當席が上限を掛けた行 / 讀めなんだ file(★0 に混ぜぬ★)

★根と深さ★: 根 = repo 根(下に絶対 path を刷る)。深さ = ★限り無し★。`.git/` のみ除く。
★己の除外★: 當席の束 docs/evidence/ashigaru-mac-2_km-109-… は ★陽性対照★ ゆゑ別欄にする
             (器は己を數へてはならぬ ―― 然れど「歩いて居らぬ」ではなく「歩いた上で分けた」)。
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kaki  # noqa: E402

BUNDLE = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(os.path.dirname(BUNDLE)))
BUNDLE_REL = os.path.relpath(BUNDLE, REPO)

P1 = r'(?:^|\s)path=([^\s"\']+)'
P2 = r"(?:^|\s)path=(.+?)[ \t]+sha256="
GYOU_KAGIRI = 200_000          # 一行の上限(byte)。超えたら「測れぬ」へ

KAGO = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")   # 「語=」形


def _dequote(t):
    t = t.strip()
    if len(t) >= 2 and t[0] == t[-1] and t[0] in "\"'":
        t = t[1:-1]
    return t


def hanzu(line):
    """一行を 甲/乙/丙/― に分ける。"""
    line = line.replace("\r", "")
    m1 = re.search(P1, line)
    m2 = re.search(P2, line)
    if m1 is None and m2 is not None:
        return "丙"
    if m1 is None or m2 is None:
        return "―"
    a = _dequote(m1.group(1))
    b = _dequote(m2.group(1))
    if a == b:
        return "―"
    # 甲。差にある語を見る
    if b.startswith(a):
        nokori = b[len(a):].split()
    else:
        nokori = b.split()
    if nokori and all(not KAGO.match(w) for w in nokori):
        return "乙"
    return "甲"


def hashiru(gyou_iter):
    n = {"甲": 0, "乙": 0, "丙": 0, "測れぬ": 0}
    reibun = {"甲": [], "乙": [], "丙": []}
    for ln in gyou_iter:
        if len(ln) > GYOU_KAGIRI:
            n["測れぬ"] += 1
            continue
        s = ln.strip()
        if not s or s.startswith("#"):
            continue
        k = hanzu(s)
        if k in n:
            n[k] += 1
            if len(reibun[k]) < 5:
                reibun[k].append(s[:150])
    return n, reibun


# ―――― disk 欄 ――――
disk = {"file_aruita": 0, "file_daichou": 0, "file_yomenu": 0}
disk_n = {"甲": 0, "乙": 0, "丙": 0, "測れぬ": 0}
disk_jibun_n = {"甲": 0, "乙": 0, "丙": 0, "測れぬ": 0}
disk_rei = {"甲": [], "乙": [], "丙": []}
disk_daichou_paths = []
JIBUN = os.path.abspath(BUNDLE) + os.sep

for r, ds, fs in os.walk(REPO):
    if ".git" in ds:
        ds.remove(".git")
    for f in fs:
        p = os.path.join(r, f)
        try:
            st = os.lstat(p)
        except OSError:
            disk["file_yomenu"] += 1
            continue
        import stat as _s
        if not _s.S_ISREG(st.st_mode):
            continue
        disk["file_aruita"] += 1
        # 先づ b"sha256=" を持つかだけを見る(塊読み・長い行を素通りさせぬ)
        mochi = False
        try:
            with open(p, "rb") as fh:
                zan = b""
                while True:
                    buf = fh.read(1 << 22)
                    if not buf:
                        break
                    if b"sha256=" in (zan + buf):
                        mochi = True
                        break
                    zan = buf[-8:]
        except OSError:
            disk["file_yomenu"] += 1
            continue
        if not mochi:
            continue
        disk["file_daichou"] += 1
        jibun = p.startswith(JIBUN)
        if not jibun:
            disk_daichou_paths.append(os.path.relpath(p, REPO))
        try:
            with open(p, "r", encoding="utf-8", errors="replace") as fh:
                n, rei = hashiru(fh)
        except OSError:
            disk["file_yomenu"] += 1
            continue
        tgt = disk_jibun_n if jibun else disk_n
        for k in n:
            tgt[k] += n[k]
        if not jibun:
            for k in disk_rei:
                for x in rei[k]:
                    if len(disk_rei[k]) < 5:
                        disk_rei[k].append("%s :: %s" % (os.path.relpath(p, REPO), x))

# ―――― 樹 欄 ――――
def ki(ref):
    out = subprocess.run(["git", "ls-tree", "-r", "-z", "--format=%(objectname) %(path)", ref],
                         cwd=REPO, capture_output=True, text=True)
    if out.returncode != 0:
        return None, out.returncode, None
    n = {"甲": 0, "乙": 0, "丙": 0, "測れぬ": 0}
    rei = {"甲": [], "乙": [], "丙": []}
    nfile = ndai = 0
    for ent in out.stdout.split("\0"):
        if not ent.strip():
            continue
        obj, path = ent.split(" ", 1)
        nfile += 1
        blob = subprocess.run(["git", "cat-file", "blob", obj], cwd=REPO, capture_output=True)
        if blob.returncode != 0 or b"sha256=" not in blob.stdout:
            continue
        ndai += 1
        t = blob.stdout.decode("utf-8", "replace")
        nn, rr = hashiru(t.splitlines())
        for k in nn:
            n[k] += nn[k]
        for k in rei:
            for x in rr[k]:
                if len(rei[k]) < 5:
                    rei[k].append("%s :: %s" % (path, x))
    return (n, rei, nfile, ndai), 0, None


kekka = {}
for ref in ["origin/main", "HEAD"]:
    r_, rc_, _ = ki(ref)
    kekka[ref] = (r_, rc_)

# ―――― 陽性対照(己の器で、己の測る路に乗せて) ――――
YOUSEI = [
    "path=a b.txt sha256=%s bytes=6 lines=1" % ("0" * 64),       # 乙 に成るべし
    "path=x.txt bytes=6 sha256=%s" % ("0" * 64),                  # 甲 に成るべし
    'path="a b.txt" sha256=%s' % ("0" * 64),                      # 丙 に成るべし
    "path=kiyoi.txt sha256=%s" % ("0" * 64),                      # ― に成るべし
]
yousei_demé = [(y.replace("0" * 64, "<64>"), hanzu(y)) for y in YOUSEI]

ima = subprocess.run(["date", "+%Y-%m-%dT%H:%M:%S%z"], capture_output=True, text=True).stdout.strip()

out = []
out.append("# ㋓ 害の広さ ―― 素の空白名の行を disk と樹の二欄で數へる(專任2 km-109)")
out.append("")
out.append("刻(數へ了へた時) %s" % ima)
out.append("根              %s" % REPO)
out.append("深さ            限り無し(`.git/` のみ除く・常体 S_ISREG のみ)")
out.append("rc              此の器は最後まで走り rc=0 で終へた(下の『測れぬ』が 0 でない時は其れを讀め)")
out.append("")
out.append("## 定義(逐語・上の docstring と同一)")
out.append("  臺帳らしき紙 = b\"sha256=\" を含む常体 file(★名では判ぜぬ★)")
out.append("  甲(広) = 則①当たり・則②当たり・剥ぎ後の出目が ★違ふ★ 行")
out.append("  乙(狭) = 甲の内、①と②の差にある語が悉く「語=」形でない 行(★真に空白名と疑へる★)")
out.append("  丙(對照) = 則②当たり・則①外れ(= ★括つた★ 空白名。正規の書き手の形)")
out.append("  測れぬ = 一行が %d byte を超えた行 / 讀めなんだ file" % GYOU_KAGIRI)
out.append("  則①逐語 %r" % P1)
out.append("  則②逐語 %r" % P2)
out.append("")
out.append("## 陽性対照(★檢出子 其の物で・測る路に乗せて★)")
for y, k in yousei_demé:
    out.append("  %-46s → %s" % (y, k))
out.append("")
out.append("## disk 欄(己の束を除いた ―― ★歩いた上で分けた★)")
out.append("  歩いた常体 file      %d" % disk["file_aruita"])
out.append("  臺帳らしき紙         %d" % disk["file_daichou"])
out.append("  讀めなんだ file      %d" % disk["file_yomenu"])
out.append("  ★甲(広)★            %d 行" % disk_n["甲"])
out.append("  ★乙(狭・真の空白名)★ %d 行" % disk_n["乙"])
out.append("  丙(括つた空白名)     %d 行" % disk_n["丙"])
out.append("  測れぬ               %d 行" % disk_n["測れぬ"])
out.append("")
out.append("## disk 欄・★當席の束(陽性対照の實物)★")
out.append("  甲 %d / 乙 %d / 丙 %d / 測れぬ %d"
           % (disk_jibun_n["甲"], disk_jibun_n["乙"], disk_jibun_n["丙"], disk_jibun_n["測れぬ"]))
out.append("  ★之は本弾で當席が作つた試験臺帳である。現物の害に足すな。★")
out.append("")
for k in ["乙", "甲", "丙"]:
    out.append("### disk の例(%s・最大5)" % k)
    if disk_rei[k]:
        for x in disk_rei[k]:
            out.append("  %s" % x)
    else:
        out.append("  (一本も無し)")
out.append("")
out.append("## 樹 欄")
for ref in ["origin/main", "HEAD"]:
    r_, rc_ = kekka[ref]
    out.append("")
    out.append("### %s (= %s)" % (ref, subprocess.run(["git", "rev-parse", ref], cwd=REPO, capture_output=True, text=True).stdout.strip()))
    if r_ is None:
        out.append("  ★取れず rc=%d★" % rc_)
        continue
    n, rei, nfile, ndai = r_
    out.append("  樹に在る file        %d" % nfile)
    out.append("  臺帳らしき blob      %d" % ndai)
    out.append("  ★甲(広)★            %d 行" % n["甲"])
    out.append("  ★乙(狭・真の空白名)★ %d 行" % n["乙"])
    out.append("  丙(括つた空白名)     %d 行" % n["丙"])
    out.append("  測れぬ               %d 行" % n["測れぬ"])
    for k in ["乙", "甲", "丙"]:
        out.append("  例(%s): %s" % (k, "; ".join(rei[k]) if rei[k] else "(一本も無し)"))
kaki.kaku(os.path.join(HERE, "30_gai_no_hirosa.txt"), "\n".join(out))
kaki.kaku(os.path.join(HERE, "31_daichou_rashiki_kami.list"),
          "\n".join(sorted(disk_daichou_paths)))
print("disk: 甲%d 乙%d 丙%d 測れぬ%d / 紙%d / 歩%d"
      % (disk_n["甲"], disk_n["乙"], disk_n["丙"], disk_n["測れぬ"],
         disk["file_daichou"], disk["file_aruita"]))
print("己の束: 甲%d 乙%d 丙%d" % (disk_jibun_n["甲"], disk_jibun_n["乙"], disk_jibun_n["丙"]))
for ref in ["origin/main", "HEAD"]:
    r_, rc_ = kekka[ref]
    if r_:
        n, rei, nfile, ndai = r_
        print("%s: 甲%d 乙%d 丙%d 測れぬ%d / blob%d/%d" % (ref, n["甲"], n["乙"], n["丙"], n["測れぬ"], ndai, nfile))
print("陽性対照", yousei_demé)
