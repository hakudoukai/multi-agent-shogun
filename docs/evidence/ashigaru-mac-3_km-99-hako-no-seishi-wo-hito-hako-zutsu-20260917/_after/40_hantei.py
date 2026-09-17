# -*- coding: utf-8 -*-
"""㋑⑶⑷食ひ違ひ・㋒生死の判・㋓白名簿との突合せ。

★宣(閾は使ふ前に宣する)★
  閾A(⑶⑷の食ひ違ひ) = 600 秒。
      根拠: 箱は「着信の刻を胴へ書く」→「file を閉ぢる」の順ゆゑ
            mtime は最終着信より ★数秒だけ後★ に成るのが正。
            600 秒を超える差は「便が着かぬのに file が動いた/其の逆」= 疵。
      向きも記す: mtime>last=後触(読印・回転・手直し) / mtime<last=未来印(刻の偽り)。
  閾B(㋒の「古い」)   = 86400 秒(24時間)。測定刻からの差。
      根拠: 當艦隊は 24 時間無停止で回る(CLAUDE.md 24時間ノンストップ稼働原則)。
            丸一日 一通も着かぬ箱は、現に文の往来が絶えて居る。
  ★閾は此処だけで定め、下の判定は悉く此の二つを使ふ。★

判(㋒):
  甲 = 生 pane に同名の @agent_id が在る
  乙 = pane 無し・併し最終着信が閾B 以内
  丙 = pane 無し・最終着信が閾B より古い(刻無しも丙)
"""
import json, sys, datetime

JST = datetime.timezone(datetime.timedelta(hours=9))
SHIKII_A = 600      # 秒
SHIKII_B = 86400    # 秒

census = json.load(open(sys.argv[1], encoding="utf-8"))
panes = []
with open(sys.argv[2], encoding="utf-8") as fh:
    for ln in fh:
        parts = ln.rstrip("\n").split("\t")
        if len(parts) >= 2 and parts[1].strip():
            panes.append(parts[1].strip())
pane_set = sorted(set(panes))
white = [l.strip() for l in open(sys.argv[3], encoding="utf-8") if l.strip()]
white_set = sorted(set(white))

now = datetime.datetime.fromisoformat(census["measured_at"])
box_names = [r["name"][:-len(".yaml")] for r in census["rows"]]

out = []
for r in census["rows"]:
    nm = r["name"][:-len(".yaml")]
    mt = datetime.datetime.fromisoformat(r["mtime"])
    if r["last"] in ("測れぬ", "刻無し"):
        last, dA, dA_tag = None, None, "測れぬ(最終着信の刻が無い)"
    else:
        last = datetime.datetime.fromisoformat(r["last"])
        dA = (mt - last).total_seconds()
        if abs(dA) <= SHIKII_A:
            dA_tag = "整合"
        elif dA > 0:
            dA_tag = "★食違・後触(mtime が %.0f 秒 後)★" % dA
        else:
            dA_tag = "★食違・未来印(mtime が %.0f 秒 前)★" % (-dA)
    if nm in pane_set:
        han = "甲"
    elif last is not None and (now - last).total_seconds() <= SHIKII_B:
        han = "乙"
    else:
        han = "丙"
    age = None if last is None else (now - last).total_seconds()
    out.append(dict(name=nm, file=r["name"], kou=r["kou"], mikou=r["mikou"],
                    last=r["last"], mtime=r["mtime"], dA=dA, dA_tag=dA_tag,
                    han=han, age_sec=age, in_white=(nm in white_set)))

# ㋓ 白名簿と判の突合せ
dead_list = ["gunshi-mac"]          # inbox_write.sh L109 既定 _IW_DEAD_LIST の逐語値
mismatch = []
for r in out:
    if r["name"] in dead_list and r["han"] == "甲":
        mismatch.append((r["name"], "死箱の宣 有・併し生 pane 有(甲) ―― 宣と判が正面から食ひ違ふ"))
    if r["name"] in dead_list and r["in_white"]:
        mismatch.append((r["name"], "死箱の宣 有・併し白名簿に居る ―― 門は通し dead-gate が rc=68 で落とす二段"))
    if r["han"] == "丙" and r["in_white"] and r["name"] not in dead_list:
        mismatch.append((r["name"], "丙(pane 無・着信古)・併し白名簿に居る ―― 宣 無き死箱の疑ひ"))

pane_only = [p for p in pane_set if p not in box_names]
box_only  = [b for b in box_names if b not in pane_set]

res = dict(shikii=dict(A_sec=SHIKII_A, B_sec=SHIKII_B), measured_at=census["measured_at"],
           pane_set=pane_set, white=white_set, white_n=len(white_set),
           bogen=len(out), rows=out, mismatch=mismatch,
           pane_only=pane_only, box_only=box_only,
           tally={k: sum(1 for r in out if r["han"] == k) for k in "甲乙丙"},
           kuichigai_n=sum(1 for r in out if r["dA_tag"].startswith("★")))
sys.stdout.write(json.dumps(res, ensure_ascii=False, indent=1) + "\n")
