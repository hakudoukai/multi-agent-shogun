# -*- coding: utf-8 -*-
# km-199 再測 ―― raw/20_calls の出目を数へる（読むのみ）。
# 胴の字数は ★行頭錨★ の regex で取る（`(?=\n[a-z_]+:)` 形は context_data まで食ふ・既知の疵）。
import os, re, glob, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
C = os.path.join(HERE, "20_calls")
REPO = "/Users/momizimac/multi-agent-shogun"

# 宣された字数（F1〜F6 = 家老の宣 9/18・378724/378725 = 送出器の stderr「胴=N字」raw/05）
DECL = {334180: 230, 334181: 258, 334182: 122, 334183: 240, 334184: 237, 334185: 132,
        378724: 283, 378725: 248}
RX = re.compile(r"^\s*content:\s*(.*?)(?=^\s*[a-z_]+:\s|^\s*-{60}|\Z)", re.S | re.M)


def rd(n):
    return open(os.path.join(C, n), encoding="utf-8").read()


def rows(text):
    """show の出目を行 dict の列へ（区切り = 空白2+'-'60）。content は複数行を持ち得る。"""
    out = []
    for blk in re.split(r"^  -{60}\n", text, flags=re.M):
        if "  seq: " not in blk:
            continue
        d = {}
        m = re.search(r"^  seq: (\d+)", blk, re.M); d["seq"] = int(m.group(1))
        m = RX.search(blk); d["content"] = m.group(1).rstrip("\n") if m else None
        for k in ("content_len", "sender_agent", "target_agent", "context_data", "created_at"):
            m = re.search(rf"^  {k}: (.*)$", blk, re.M)
            if m: d[k] = m.group(1)
        out.append(d)
    return out


print("# 刻", datetime.datetime.now().astimezone().isoformat(timespec="seconds"))
print("## ⒝ 胴の字数（宣 → 各路の返り）")
print("seq | 宣 | ⑴seq | ⑵seqs(刷字/content_len) | ⑶sent 在否 | ⑷inbox200 在否(字) | ⑦pcid(刷字/content_len)")
s2 = rows(rd("r2_seqs_334180-334185.out")) + rows(rd("r2_seqs_378724,378725.out"))
s2 = {r["seq"]: r for r in s2}
sent = {}
for t in ("karo-mac", "gunshi-mac", "iincho"):
    for r in rows(rd(f"r3_sent_{t}.out")):
        sent[r["seq"]] = (t, r)
inbox = {r["seq"]: r for r in rows(rd("r4_inbox_200.out"))}
pc = {}
for f in glob.glob(os.path.join(C, "r7_pcid_*.out")):
    for r in rows(open(f, encoding="utf-8").read()):
        pc[r["seq"]] = r
diff_n = 0
for q, n in DECL.items():
    r1 = rows(rd(f"r1_seq_{q}.out"))
    a = len(r1[0]["content"]) if r1 and r1[0]["content"] is not None else None
    b = s2.get(q); bs = f"{len(b['content'])}/{b.get('content_len')}" if b else "無"
    c = sent.get(q); cs = f"在({c[0]}・{len(c[1]['content'])}字)" if c else "無"
    d = inbox.get(q); ds = f"在({len(d['content'])})" if d else "無"
    e = pc.get(q); es = f"{len(e['content'])}/{e.get('content_len')}" if e else "未測"
    if a != n: diff_n += 1
    print(f"{q} | {n} | {a}{'' if a == n else ' ★差★'} | {bs} | {cs} | {ds} | {es}")
print(f"⑴ seq 路の 宣≠返り = {diff_n}/{len(DECL)}")

print("## ⒞ context_data の出方")
for q in (334180, 378724):
    t = rd(f"r1_seq_{q}.out")
    m = re.search(r"^  context_data: (.*)$", t, re.M)
    print(f"⑴ seq {q}: {m.group(1) if m else '無'}")
for name in ("r2_seqs_378724,378725.out", "r3_sent_karo-mac.out", "r4_inbox_20.out", "r7_pcid_8986a8e8.out"):
    t = rd(name)
    keys = sorted(set(re.findall(r"^  ([a-z_]+): ", t, re.M)))
    print(f"{name}: 刷る欄 = {keys}")

print("## ⒟ 並びと窓")
for name in ("r2_seqs_334180-334185.out", "r3_sent_karo-mac.out", "r3_sent_gunshi-mac.out", "r3_sent_iincho.out",
             "r4_inbox_20.out", "r4_inbox_200.out", "r7_pcid_8986a8e8.out"):
    t = rd(name); rs = rows(t)
    sq = [r["seq"] for r in rs]
    order = "asc" if sq == sorted(sq) else ("desc" if sq == sorted(sq, reverse=True) else "混")
    print(f"{name}: {t.splitlines()[0]} | 行={len(sq)} 頭={sq[0] if sq else None} 尾={sq[-1] if sq else None} 並び={order}")

print("## ⒠ 截り（刷られた胴が '…' で終る行の数 / 行数）")
for name in ("r3_sent_karo-mac.out", "r3_sent_gunshi-mac.out", "r3_sent_iincho.out", "r7_pcid_8986a8e8.out",
             "r7_pcid_5c88b950.out", "r4_inbox_200.out"):
    rs = rows(rd(name))
    cut = [r for r in rs if r["content"] and r["content"].endswith("…")]
    lens = sorted({len(r["content"]) for r in cut})
    print(f"{name}: 截り {len(cut)}/{len(rs)} ・截った行の刷字 = {lens[:5]}")

print("## 今日の己の便（378724/378725・km_send.sh 経由）を sent 路は返すか")
for q in (378724, 378725):
    t = rd(f"r1_seq_{q}.out")
    res = re.search(r"^  resolved_at: (.*)$", t, re.M)
    cd = re.search(r"^  context_data: (.*)$", t, re.M).group(1)
    print(f"{q}: resolved_at={'有 ' + res.group(1) if res else '無(未返答)'} ・ context_data={cd} ・ sent 路={'在' if q in sent else '無'}")

print("## ⑹ 箱 file の尾（DB の seq を持つか・今日の便の胴が在るか）")
body378724 = rows(rd("r1_seq_378724.out"))[0]["content"]
for box in ("karo-mac", "gunshi-mac", "ashigaru-mac-1"):
    p = os.path.join(REPO, "queue", "inbox", f"{box}.yaml")
    t = open(p, encoding="utf-8").read()
    print(f"{box}.yaml: 字={len(t)} ・ 'seq: ' 欄={len(re.findall(r'^ *seq: ', t, re.M))} ・ "
          f"'378724' の字面={t.count('378724')} ・ 378724 の胴の頭40字={t.count(body378724[:40])}")
print("# 了", datetime.datetime.now().astimezone().isoformat(timespec="seconds"))
