# -*- coding: utf-8 -*-
"""㋔ v2 ―― v1(80_matome.py)を走らせて★己の規則の疵を二つ★見たゆゑ直した版。

v1 が出した疵(隠さず記す。v1 の出目は 81_matome_v1.json に残す):
  疵①: 枝の順が 乙 を 既読0 より先に見たゆゑ、
        karo(659 項・既読 0・本日 13:57 着信)を「残」と刷つた。
        ★今も便が落ち続け、一通も讀まれて居らぬ箱★ が最も害の大きい箱であるのに、
        最も安全な札が付いた ―― ★順序が判定を逆へ倒した★。
  疵②: 「既読>0 → 残」が ★裁★ を追ひ越した。
        ashigaru-mac-7 は裁 seq302248 で DEAD-INBOX と判じられて居るのに「残」と刷つた。
        ★過去に讀まれた事は、今讀む者が居る事ではない。★

v2 の規則(順に当てる ―― 上が勝つ):
  ⒈ 異名(読点・空白) → 外(白名簿へ入れぬ。門が無条件に拒む形)
  ⒉ 裁で死箱と判じられた名 → 宣(裁が先。既読の跡より裁が勝つ)
  ⒊ 既に宣済(_IW_DEAD_LIST に在る) → 宣済
  ⒋ 項>0 かつ 既読=0 → 宣(要裁)。★齢が浅い程 害が大きい★ゆゑ齢で序を付ける
  ⒌ 判が甲/乙、又は既読>0 → 残
  ⒍ 其の他 → 要裁(0 と書かず未分と書く)
"""
import json, sys

hantei = json.load(open(sys.argv[1], encoding="utf-8"))
kidoku = {r["name"]: r for r in json.load(open(sys.argv[2], encoding="utf-8"))["rows"]}
DEAD_DECLARED = {"gunshi-mac"}
SAI = {
 "ashigaru-mac-7": "裁 seq302248(2026-09-11T05:17:11+09:00)逐語=『queue/inbox/ashigaru-mac-7.yaml は★旧 足軽mac-7＝現ドクターM(dr-m)★の局所箱。…この箱を読む者は居ない(watcher 0本が正)。…箱は消さず DEAD-INBOX 扱い』",
 "dr-m": "裁 seq302248 逐語=『dr-m は 9/4 の独立後 DB便(to_pc=mac_pc・target_agent=dr-m)で受ける席』 ―― 局所箱ではなく DB が正路。",
}

rows = []
for r in hantei["rows"]:
    k = kidoku.get(r["file"], {})
    yomi, n = k.get("yomi", "測れぬ"), k.get("n", "測れぬ")
    age = None if r["age_sec"] is None else r["age_sec"] / 86400
    imei = ("," in r["name"]) or any(c.isspace() for c in r["name"])
    sai = SAI.get(r["name"])
    if imei:
        wake = "外"
        riyu = "異名(U+002C 読点)。門 L48 が読点/空白を無条件に落とす ―― 白名簿へ入る道が無い。★箱は消さず★迷ひ箱として残す(足軽mac4号の復命 1 通が 28.6 日 未讀の現物)。"
    elif sai:
        wake = "宣"
        riyu = "★裁が先★ ―― 既読 %s/%s 通の跡が在つても、今讀む者は居らぬ。%s" % (yomi, n, sai)
    elif r["name"] in DEAD_DECLARED:
        wake = "宣済"
        riyu = "既に宣 有(rc=68 で正路 pc_handshake を刷る)。★白名簿には残すのが正★ ―― 外すと rc=69『未知の宛名』と成り、箱が現に在るのに『無い』と刷る誤報に化ける。"
    elif isinstance(n, int) and isinstance(yomi, int) and n > 0 and yomi == 0:
        wake = "宣(要裁)"
        ito = "★齢 %.2f 日 ―― 今も便が落ちて居る。害は此の箱が最大★。" % age if (age is not None and age <= 1) else "齢 %.2f 日。" % (age or -1)
        riyu = "既読 0/%d 通(read:true が一通も無い)・判=%s。%s%s" % (
            n, r["han"], ito,
            "生 pane 有 ―― ★pane が在る事は箱を讀む事ではない★。" if r["han"] == "甲" else "")
    elif r["han"] in ("甲", "乙") or (isinstance(yomi, int) and yomi > 0):
        wake = "残"
        riyu = "既読 %s/%s 通・判=%s・齢 %s 日 ―― 讀み手の跡が在る。%s" % (
            yomi, n, r["han"], "%.2f" % age if age is not None else "測れぬ",
            "外せば復帰した席への令が rc=69 で止まる。" if r["han"] == "乙" else "静止は死ではない。")
    else:
        wake, riyu = "要裁", "此の器の規則で分けられぬ ―― 未分と書く(0 と書かぬ)。"
    rows.append(dict(name=r["name"], han=r["han"], n=n, yomi=yomi, mi=r["mikou"],
                     age_d=None if age is None else round(age, 2),
                     white="在" if r["in_white"] else "無", wake=wake, riyu=riyu,
                     dA_tag=r["dA_tag"]))

order = {"残": 0, "宣(要裁)": 1, "宣": 2, "宣済": 3, "外": 4, "要裁": 5}
rows.sort(key=lambda x: (order.get(x["wake"], 9), -(x["age_d"] is not None and -x["age_d"] or 0), x["name"]))
rows.sort(key=lambda x: (order.get(x["wake"], 9), x["age_d"] if x["age_d"] is not None else 1e9, x["name"]))
tally = {}
for r in rows:
    tally[r["wake"]] = tally.get(r["wake"], 0) + 1
print(json.dumps(dict(bogen=len(rows), tally=tally, rows=rows), ensure_ascii=False, indent=1))
