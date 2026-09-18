# -*- coding: utf-8 -*-
"""㋔ ―― 判(甲乙丙)・既読・白名簿・死箱の宣 を一枚へ束ね、
残すべき/外すべき を ★器が決める★(手で並べ替へぬ)。

宣(仕分けの規則 ―― 使ふ前に書く):
  残 = 白名簿に残す。判が甲/乙、又は既読が 1 通以上在る箱。
       (既読 1 通以上 = 過去に讀み手が居た證。席が戻れば讀む。)
  宣 = 白名簿には残し、★死箱の宣(_IW_DEAD_LIST)へ加へるべき★箱。
       既読 0 かつ 項 1 以上 かつ 判が丙、又は 既読 0 で裁が在る物。
       (白名簿から外すと rc=69「未知の宛名・箱を生ませぬ」と刷る ―― 箱は現に在るゆゑ★誤報★。
        死箱の宣なら rc=68 で★正路★を出す。∴ 外すのでなく宣へ加へる。)
  外 = 白名簿から外すべき箱。門が読点/空白で無条件に拒む異名のみ。
"""
import json, sys

hantei = json.load(open(sys.argv[1], encoding="utf-8"))
kidoku = {r["name"]: r for r in json.load(open(sys.argv[2], encoding="utf-8"))["rows"]}
DEAD_DECLARED = {"gunshi-mac"}          # inbox_write.sh L109 既定値(逐語)
SAI = {"ashigaru-mac-7": "裁 seq302248(2026-09-11 05:17)逐語=『queue/inbox/ashigaru-mac-7.yaml は…DEAD-INBOX 扱い』",
       "dr-m": "裁 seq302248 逐語=『dr-m は…DB便(to_pc=mac_pc・target_agent=dr-m)で受ける席』"}

rows = []
for r in hantei["rows"]:
    k = kidoku.get(r["file"], {})
    yomi = k.get("yomi", "測れぬ")
    n = k.get("n", "測れぬ")
    imei = ("," in r["name"]) or any(c.isspace() for c in r["name"])
    if imei:
        wake, riyu = "外", "異名(U+002C 読点)。門が無条件に拒む形ゆゑ白名簿へ入れてはならぬ。箱は消さず檢分済の迷ひ箱として残す。"
    elif r["name"] in DEAD_DECLARED:
        wake, riyu = "宣済", "既に死箱の宣 有 → rc=68 で正路(pc_handshake)を出す。白名簿には残すのが正(名の誤りと読手不在を別の札で分ける為)。"
    elif isinstance(yomi, int) and isinstance(n, int) and n > 0 and yomi == 0 and r["han"] == "丙":
        wake, riyu = "宣", "既読 0/%d 通・pane 無・最終着信 %.1f 日前 ―― 讀み手の跡が一つも無い。外すのでなく死箱の宣へ加へ正路を刷らせよ。" % (n, (r["age_sec"] or 0)/86400)
    elif isinstance(yomi, int) and isinstance(n, int) and n > 0 and yomi == 0 and r["han"] == "甲":
        wake, riyu = "宣(要裁)", "生 pane 有・併し既読 0/%d 通 ―― ★pane が在る事は箱を讀む事ではない★。%s" % (n, SAI.get(r["name"], "裁 未取得ゆゑ家老の檢分を請ふ。"))
    elif r["han"] == "乙":
        wake, riyu = "残", "pane 無・併し最終着信 %.2f 日前(閾B 以内)・既読 %s/%s ―― 席の落ちた隙であつて死ではない。外せば復帰時の令が止まる。" % ((r["age_sec"] or 0)/86400, yomi, n)
    elif isinstance(yomi, int) and yomi > 0:
        wake, riyu = "残", "既読 %s/%s 通 ―― 過去に讀み手が居た證。%s" % (yomi, n, ("生 pane 有。" if r["han"] == "甲" else "今は pane 無・静止 %.1f 日。" % ((r["age_sec"] or 0)/86400)))
    else:
        wake, riyu = "要裁", "此の器の規則で分けられぬ ―― 家老の檢分を請ふ(0 と書かず未分と書く)。"
    if r["name"] in SAI and wake.startswith("宣"):
        riyu = riyu if SAI[r["name"]] in riyu else riyu + " " + SAI[r["name"]]
    rows.append(dict(name=r["name"], han=r["han"], n=n, yomi=yomi, mi=r["mikou"],
                     age_d=None if r["age_sec"] is None else round(r["age_sec"]/86400, 2),
                     white="在" if r["in_white"] else "無", wake=wake, riyu=riyu,
                     dA_tag=r["dA_tag"]))

order = {"残": 0, "乙": 0, "宣(要裁)": 1, "宣": 2, "宣済": 3, "外": 4, "要裁": 5}
rows.sort(key=lambda x: (order.get(x["wake"], 9), x["name"]))
tally = {}
for r in rows:
    tally[r["wake"]] = tally.get(r["wake"], 0) + 1
print(json.dumps(dict(bogen=len(rows), tally=tally, rows=rows), ensure_ascii=False, indent=1))
