# -*- coding: utf-8 -*-
"""㋐㋑ ―― queue/inbox の箱を一つづつ measure する器。

宣(此の器が何を母數とするか):
  母數 = 歩き根 直下の ★通常 file★ にして、名が '.yaml' で終はる物のみ。
         dir(_archive 等)・.lock・.bak-* は母數の外。
         ★非通常 file(FIFO/symlink 先無し等)は開かず「止」として別に数へる★
         (open() で止まる事故を避ける ―― 疵 walker-needs-S_ISREG)。
  歩き根 = argv[1](既定 queue/inbox)。★字面で固定せぬ★。

測る四つ:
  ⑴項数   = yaml.safe_load した後の messages 要素数。★字面 grep で数へぬ★。
  ⑵未読数 = 要素(dict)の ★鍵 read★ が False の物。胴(content)中の "read: false"
             は dict の値の中に在るゆゑ此の数へ方では拾はぬ(其れが此の測り方の理由)。
  ⑶最終着信 = 要素の timestamp の最大。刻無しの要素は別に数へる。
             naive な刻は ★JST(+09:00) と看做す★(宣)。
  ⑷file 刻 = st_mtime(JST 表示)。

解けぬ時は 0 と書かず '測れぬ' と書き、理由(例外の型と文)を併記する。
"""
import os, stat, sys, json, datetime
try:
    import yaml
except Exception as e:
    print("yaml import 不可: %r" % (e,), file=sys.stderr); raise

JST = datetime.timezone(datetime.timedelta(hours=9))

def as_aware(ts):
    """刻の字を aware datetime へ。naive は JST と看做す(宣)。解けねば None。"""
    if not isinstance(ts, str):
        if isinstance(ts, datetime.datetime):
            return ts if ts.tzinfo else ts.replace(tzinfo=JST)
        return None
    s = ts.strip()
    try:
        d = datetime.datetime.fromisoformat(s)
    except Exception:
        return None
    return d if d.tzinfo else d.replace(tzinfo=JST)

def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "queue/inbox"
    rows, tomari, skipped = [], [], []
    names = []
    with os.scandir(root) as it:
        for de in it:
            names.append(de.name)
    names.sort()
    for name in names:
        p = os.path.join(root, name)
        try:
            st = os.lstat(p)
        except OSError as e:
            tomari.append((name, "lstat 不可: %r" % (e,))); continue
        if stat.S_ISLNK(st.st_mode):
            skipped.append((name, "symlink")); continue
        if not stat.S_ISREG(st.st_mode):
            tomari.append((name, "非通常 file(mode=%o)" % (st.st_mode,))); continue
        if not name.endswith(".yaml"):
            skipped.append((name, "名が .yaml で終らぬ")); continue
        st = os.stat(p)
        mtime = datetime.datetime.fromtimestamp(st.st_mtime, JST)
        try:
            with open(p, encoding="utf-8") as fh:
                doc = yaml.safe_load(fh)
            err = ""
        except Exception as e:
            rows.append(dict(name=name, bytes=st.st_size, kou="測れぬ", mikou="測れぬ",
                             last="測れぬ", mtime=mtime.isoformat(), nots="測れぬ",
                             err="%s: %s" % (type(e).__name__, str(e).replace("\n", " ")[:120])))
            continue
        msgs = (doc or {}).get("messages")
        if msgs is None:
            rows.append(dict(name=name, bytes=st.st_size, kou="測れぬ", mikou="測れぬ",
                             last="測れぬ", mtime=mtime.isoformat(), nots="測れぬ",
                             err="頂に messages 鍵が無い(頂の鍵=%s)" % (sorted((doc or {}).keys()) if isinstance(doc, dict) else type(doc).__name__,)))
            continue
        if not isinstance(msgs, list):
            rows.append(dict(name=name, bytes=st.st_size, kou="測れぬ", mikou="測れぬ",
                             last="測れぬ", mtime=mtime.isoformat(), nots="測れぬ",
                             err="messages が列でない(%s)" % type(msgs).__name__))
            continue
        kou = len(msgs)
        mikou = sum(1 for m in msgs if isinstance(m, dict) and m.get("read") is False)
        stamps, nots = [], 0
        for m in msgs:
            if not isinstance(m, dict):
                nots += 1; continue
            d = as_aware(m.get("timestamp"))
            if d is None:
                nots += 1
            else:
                stamps.append(d)
        last = max(stamps).isoformat() if stamps else "刻無し"
        rows.append(dict(name=name, bytes=st.st_size, kou=kou, mikou=mikou,
                         last=last, mtime=mtime.isoformat(), nots=nots, err=""))
    out = dict(root=root, walked=len(names), bogen=len(rows),
               tomari=tomari, skipped=skipped, rows=rows,
               measured_at=datetime.datetime.now(JST).isoformat())
    sys.stdout.write(json.dumps(out, ensure_ascii=False, indent=1) + "\n")

main()
