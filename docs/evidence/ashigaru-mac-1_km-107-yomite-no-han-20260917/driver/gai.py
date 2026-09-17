# -*- coding: utf-8 -*-
"""gai.py ―― 臺帳の一行を 甲/乙/丙/平/讀めぬ に分ける ★檢出子★(km-107)。
20(disk)・25(樹)・30(対照) の三器が ★同じ此の函數★ を使ふ(対照は檢出子自身の物で)。

宣(逐語):
  行     = b"\\n" で切つた一片(str.splitlines は U+2028 等も行末と見做す故 使はぬ)。
           末尾の \\r は剥ぐ(讀み手 直つた版と同じ)。
  註     = 左詰めして '#' で始まる行 / 空行 ―― 數へぬ(讀み手も數へぬ)。
  path行 = 註でなく、sha256=[0-9a-f]{64} を含む行。之が「臺帳の行」の母數。
  讀めぬ = 註でなく、sha256=<64hex> を含まぬ行。害の母數に入れぬ(別欄で報せる)。
  名の切り出し(seg):
    'path=' が在れば、最初の 'path=' の直後から、其の後に現れる最初の ' sha256=' / ' bytes=' / ' lines=' の手前まで。無ければ行末まで。
    'path=' が無ければ、最初の 'sha256=' の手前まで。其の中に ' = ' が在れば最後の ' = ' の右(label = <p> 形)。
    seg の両端の空白(' ' '\\t')は剥ぐ ―― 端の空白は「名の空白」と數へぬ。
  括り  = len(seg)>=2 かつ seg[0]==seg[-1] かつ其れが '"' か "'"。inner = 括りを剥いだ物。
  空白  = inner に ' ' か '\\t' が在る(書き手 append.py の KUUHAKU と同じ二字)。其の他の unicode 空白(U+3000 等)は 丁 として別欄。
  甲 = 括り ∧ 空白 / 乙 = ¬括り ∧ 空白 / 丙 = 括り ∧ ¬空白(旧形) / 平 = ¬括り ∧ ¬空白
"""
import re

SHA = re.compile(rb"sha256=[0-9a-f]{64}")
KUU = " \t"

def gyou_wake(data: bytes):
    """bytes → (行の總數[b'\\n' 實測], 行の列)。最後の改行無しの塊も一行(grep -c '' と同じ)。"""
    parts = data.split(b"\n")
    if parts and parts[-1] == b"":
        parts.pop()
    return len(parts), parts

def seg_of(line: str):
    i = line.find("path=")
    if i >= 0:
        rest = line[i + 5:]
        ends = [rest.find(k) for k in (" sha256=", " bytes=", " lines=")]
        ends = [e for e in ends if e >= 0]
        seg = rest[:min(ends)] if ends else rest
    else:
        j = line.find("sha256=")
        seg = line[:j] if j >= 0 else line
        k = seg.rfind(" = ")
        if k >= 0:
            seg = seg[k + 3:]
    return seg.strip(KUU)

def wake(raw: bytes):
    """一行(bytes) → (種, seg, inner)。種 ∈ 註/讀めぬ/甲/乙/丙/平"""
    line = raw.decode("utf-8", "surrogateescape").rstrip("\r")
    if line.strip() == "" or line.lstrip().startswith("#"):
        return "註", "", ""
    if not SHA.search(raw):
        return "讀めぬ", "", ""
    seg = seg_of(line)
    kukuri = len(seg) >= 2 and seg[0] == seg[-1] and seg[0] in "\"'"
    inner = seg[1:-1] if kukuri else seg
    kuu = any(c in inner for c in KUU)
    if kukuri and kuu:
        return "甲", seg, inner
    if kuu:
        return "乙", seg, inner
    if kukuri:
        return "丙", seg, inner
    return "平", seg, inner

def hoka_kuuhaku(inner: str):
    """丁: ' ' '\\t' 以外の unicode 空白を含むか"""
    return any(c.isspace() and c not in KUU for c in inner)

def file_wake(data: bytes):
    """一枚 → 集計 dict と 害行の列 [(行番, 種, seg, 行)]"""
    n, parts = gyou_wake(data)
    c = {"行總": n, "註": 0, "讀めぬ": 0, "path行": 0, "甲": 0, "乙": 0, "丙": 0, "平": 0, "丁": 0}
    kizu = []
    for no, raw in enumerate(parts, 1):
        sh, seg, inner = wake(raw)
        c[sh] += 1
        if sh in ("甲", "乙", "丙", "平"):
            c["path行"] += 1
            if hoka_kuuhaku(inner):
                c["丁"] += 1
        if sh in ("甲", "乙"):
            kizu.append((no, sh, seg, raw.decode("utf-8", "surrogateescape").rstrip("\r")))
    return c, kizu
