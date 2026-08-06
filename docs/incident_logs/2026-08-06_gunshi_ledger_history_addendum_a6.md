# queue/reports/gunshi_report.yaml 変遷復元への追補 — 用いた正規表現・走査file一覧 (足軽6号)

対象=`docs/incident_logs/2026-08-06_gunshi_ledger_history_a6.md`（282行
sha256=17e11a63c406be27bf75d2e1c89edafb4766d0869fcfc2505949c61bfa7f63a0）への追補。
家老second msg_20260806_141138_09d8f2eb（②の指摘）を受け、★数を直さず★、方法（正規表現＋走査file一覧）
のみを提示する。60対66/62/58の差の内訳は本追補でも★割らない★（家老second指示通り）。

測時=2026-08-06T14:14:07+09:00（`date -Iseconds`実行結果）。git rev-parse HEAD=7bbf1f9c67ba8e5254a7c75bde716a76defe523b。

## ① 用いた正規表現（Python re、そのまま）

```python
pattern = re.compile(
    r'gunshi_report\.yaml[^\n]{0,40}?(\d+)\s*行[^\n]{0,80}?sha256[=:]?\s*([0-9a-f]{8,64}|TO_FILL)'
)
```

★家老secondのgrep -coEとの構造差★（判定なし、事実のみ）：
- 家老second側＝`gunshi_report\.yaml[[:space:]]*[0-9]+[[:space:]]*行[[:space:]]*sha256=[0-9a-f]{16}`
  （空白のみを挟み、"sha256="固定、hex長16固定）
- 当職側＝`[^\n]{0,40}`（改行以外の任意文字を40字まで許容）／`sha256[=:]?`（"="と":"の両方を許容）／
  hex長8〜64文字またはplaceholder文字列`TO_FILL`も許容

## ② 用いた方法（grepは場所を探すのみ・数えるのに用いていない）

1. `/usr/bin/grep -rl "gunshi_report" queue/inbox/` で★該当file一覧の特定のみ★（本文の突合抽出には未使用）
2. 各fileを`yaml.safe_load_all()`でパースし、各messageの`content`欄（文字列）を取得
3. パース後の`content`文字列に対して①の正規表現を`re.finditer`で適用（★raw grep出力にではなく、パース済み
   文字列に対して適用★——家老second指摘の「YAML折返しをgrepが行単位で見落とす」欠陥は、当職の抽出経路
   では構造的に生じない。パース時にYAMLのfolded/foldedブロックscalarは`safe_load_all`が結合済みの
   一続き文字列として返すため）

## ③ 走査したfile一覧と、fileごとの一致件数（生の出力）

`/usr/bin/grep -rl "gunshi_report" queue/inbox/`の出力6件のうち、①の正規表現が実際に１件以上一致した
fileのみ内訳を示す（他4件＝`_archive/shogun-second_pruned.yaml`・`ashigaru5.yaml`・`ashigaru6.yaml`・
`gunshi-second.yaml`は0件、家老secondがledgerについて論じた便のみで自己citation無し、前報告済）：

```
queue/inbox/_archive/karo-second_pruned.yaml  total=56 (うちsha256=TO_FILL の物=6)
queue/inbox/karo-second.yaml                  total=11 (TO_FILL=0)
-----
合計=67（前報告時と同一。前報告の「今日分66」はこの67からTO_FILL要素を除かず2026-08-04分1件
        [172行、18:10:54]を除いた本日分の生citation数）
```

★参考（判定ではなく、家老second③の「網の広さ」観察に対応する一データ点）★：
`karo-second_pruned.yaml`単独でTO_FILLを除くと 56-6=50 件。家老secondが同fileをパースして得た値は49件
（家老second便本文より引用）。差=1件。この1件差の由来は当職側で未追跡（家老secondの指示通り、数の
是正・内訳の完全解明は本追補の範囲外とし、双方の方法を並べて提示するに留める）。

## ④ ㈣への一行追補（家老second指摘・「引用は下界を与え順序を与えぬ」原則との対応）

`queue/reports/gunshi_report.yaml`内容欄の`timestamp: "2026-08-06T14:04:20+09:00"`は、★その内容が
作られた刻の下界に過ぎず、fileが実際に書かれた刻（OS mtime＝13:52:52）そのものを保証しない★。
中身が名乗る刻と、fileが書かれた刻は別の述語である。

## 監査体制

暫定二者制（軍師second+Gemini）。Codex leg停止中（2026-07-21事案）。

以上、追補。新規探索・新規判定は行っていない（家老second④の一行と、①②③の方法提示のみ）。
