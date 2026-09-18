# -*- coding: utf-8 -*-
"""㋐の異名検出 と ㋒の裏付け(既読の有無)。

異名 = 名(拡張子を除く)に ★読点(,)・空白(半角/全角/TAB)・改行★ を含む物。
      門(inbox_write.sh L40/L48)が白名簿から落とす形と同じ字集合を使ふ。
既読 = 要素の鍵 read が True の物。鍵そのものが無い要素は別に数へる。
      ★項>0 にして既読 0 の箱は「一度も讀まれて居らぬ」★ ―― 読み手不在の裏付け。
      (pane が在つても既読が 0 なら、其の席は此の箱を讀んで居らぬ。)
"""
import os, sys, json, re, unicodedata, datetime
import yaml
JST = datetime.timezone(datetime.timedelta(hours=9))

root = sys.argv[1]
SPACEY = re.compile(r'[,\s　]')
rows, imei = [], []
for name in sorted(os.listdir(root)):
    if not name.endswith(".yaml"):
        continue
    p = os.path.join(root, name)
    if not os.path.isfile(p):
        continue
    base = name[:-5]
    if SPACEY.search(base):
        imei.append(dict(name=name, base=base,
                         codepoints=[("U+%04X" % ord(c)) for c in base if SPACEY.match(c)],
                         chars=[unicodedata.name(c, "?") for c in base if SPACEY.match(c)]))
    try:
        doc = yaml.safe_load(open(p, encoding="utf-8"))
        msgs = (doc or {}).get("messages") or []
    except Exception as e:
        rows.append(dict(name=name, n="測れぬ", yomi="測れぬ", mi="測れぬ", nokey="測れぬ",
                         err="%s" % type(e).__name__))
        continue
    yomi = sum(1 for m in msgs if isinstance(m, dict) and m.get("read") is True)
    mi   = sum(1 for m in msgs if isinstance(m, dict) and m.get("read") is False)
    nokey= sum(1 for m in msgs if isinstance(m, dict) and "read" not in m)
    rows.append(dict(name=name, n=len(msgs), yomi=yomi, mi=mi, nokey=nokey, err=""))

never = [r["name"] for r in rows if r["err"] == "" and r["n"] > 0 and r["yomi"] == 0]
print(json.dumps(dict(root=root, measured_at=datetime.datetime.now(JST).isoformat(), rows=rows, imei=imei, imei_n=len(imei),
                      never_read=never, never_read_n=len(never)),
                 ensure_ascii=False, indent=1))
