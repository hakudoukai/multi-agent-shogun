# 停滞便の仕分け（群㈣）— queue/inbox/karo.yaml（家老）

下命=家老second msg_20260806_203150_543dc237（2026-08-06T20:31:50）。
読取のみ・票のみ。対象file自体は★一切変更していない★（`read`を立てず・移さず・消していない）。

測時=2026-08-06T20:35:09+09:00（`date -Iseconds`実行結果）。
git rev-parse HEAD=4e8ab81ea680163e8d18872ba3425c8505c12cc3。

## 対象fileの実測

```
$ ls -la queue/inbox/karo.yaml
-rw------- 1 hakudokai hakudokai 47316 Aug  5 11:16 queue/inbox/karo.yaml

$ stat -c 'mtime=%y epoch=%Y' queue/inbox/karo.yaml
mtime=2026-08-05 11:16:47.939853384 +0900 epoch=1785896207

$ wc -l queue/inbox/karo.yaml
782 queue/inbox/karo.yaml

$ sha256sum queue/inbox/karo.yaml
fbb09df7c5d0b496d2a2f91e47b45608ebf78ff7e9bfed614d836f67ffbd8e05  queue/inbox/karo.yaml

$ git check-ignore -q queue/inbox/karo.yaml; echo "check-ignore exit=$?"
check-ignore exit=0

$ git status --short queue/inbox/karo.yaml
（出力なし＝working tree に対する変更を当職は加えていない）
```

## 名簿確認（`karo`は名簿在り＝孤児箱ではない）

```
$ /usr/bin/grep -n "agent_id" queue/pane_registry.yaml
26:    agent_id: shogun
32:    agent_id: karo
38:    agent_id: ashigaru1
...(以下省略、全20件中 `karo` は line32 に実在)
```

`karo` は名簿に★実在する canon agent_id★。群㈥（`ashigaru-second-1`＝孤児箱）とは事情が異なる——
本file自体は正規の受信箱であり、問題は「箱の主が不在」ではなく「箱に着地した4通の性質」である。

## 母集団宣言（③ 数の扱い）

令＝「4通(33.6h・from=inbox_write)」。実行の刻（2026-08-06T20:35:09+09:00）に
`python3 + yaml.safe_load`（本文を読まぬ grep でなく、messages配列を parse）で数え直した結果：

```python
import yaml
with open('queue/inbox/karo.yaml') as f:
    data = yaml.safe_load(f)
msgs = data.get('messages', [])
print('total=', len(msgs))               # 43
print('unread=', sum(1 for m in msgs if not m.get('read')))         # 4
print('from_inbox_write=', sum(1 for m in msgs if m.get('from')=='inbox_write'))  # 4
```

- `messages` 全体＝**43通**（母集団の全体像として記す。仕分け対象はこの部分集合ではない）
- `from == 'inbox_write'`＝**4通**（令の「4通」と★一致・食い違い無し★）
- `read == false`（未読）＝**4通**（`from=inbox_write` の4通と完全に重なる＝この箱の未読は全てこの4通のみ）

測時＝2026-08-06T20:35:09+09:00／器＝`python3` + `yaml.safe_load`／範囲＝`queue/inbox/karo.yaml` の `messages[]` 全件。
以上。

## 対象4通の内容（全文・完全同一）

| id | timestamp(JST) | 測時との差 | type | read |
|---|---|---|---|---|
| `msg_20260805_105505_5ff311de` | 2026-08-05T10:55:05 | 33.67h | delivery_failed | false |
| `msg_20260805_110634_f116cdd4` | 2026-08-05T11:06:34 | 33.48h | delivery_failed | false |
| `msg_20260805_111500_0456d5bb` | 2026-08-05T11:15:00 | 33.34h | delivery_failed | false |
| `msg_20260805_111647_eda0234b` | 2026-08-05T11:16:47 | 33.31h | delivery_failed | false |

4通とも `content` は文字列完全一致：

```
宛先不明: test_agent ／ 名簿に在る有効な宛先の一例: ashigaru1 (registry=/home/hakudokai/projects/multi-agent-shogun/queue/pane_registry.yaml)
```

`expires_at`・`supersedes` は4通とも `null`。`from` は4通とも `inbox_write`（＝人ではなく★機構自身★が書いた通知）。

## ⒜ 誰宛・何・いつ

- **宛先＝`karo`（本file自体が家老の受信箱）**。ただしこれは「karo宛の指示」ではなく、
  `scripts/inbox_write.sh` の REJECT分岐（下記参照）が★送信元(FROM)へ自動で折り返した通知★。
- **本来の送信試行**＝何者か（未特定・下記参照）が `FROM=karo` として `target=test_agent` 宛に
  `inbox_write.sh` を4回呼び出した。`test_agent` は名簿（`queue/pane_registry.yaml`）に存在しない
  agent_id のため、4回とも `REJECTED` となり、機構が `FROM=karo` へ delivery_failed 通知を書き戻した。
- **何＝** type=`delivery_failed`、content=「宛先不明: test_agent／名簿に在る有効な宛先の一例: ashigaru1」
- **いつ＝** 上表の4件（2026-08-05 10:55〜11:16、22分の間に4回）
- **機構的根拠（己の手で確認）**＝ `scripts/inbox_write.sh` L560-568:
  ```
  if [ "$_FROM_STATUS" = "FROM_OK" ] && [ "$_FROM_RESOLVABLE_RC" -eq 0 ]; then
      _NOTICE="宛先不明: ${TARGET} ／ 名簿に在る有効な宛先の一例: ashigaru1 (registry=$CANON_REGISTRY)"
      _write_message "$FROM" "$_NOTICE" "delivery_failed" "inbox_write" "" ""
      echo "[inbox_write] REJECTED: target '$TARGET' is not a canon agent_id ... — delivery_failed notice returned to from='$FROM'" >&2
      exit 1
  ```
  ＝ `FROM` が canon 内で解決可能な場合、機構は拒否通知を **`$FROM`自身の箱**へ書く設計。
  `karo` は canon 内（名簿line32）ゆえ、本4通は「設計どおりの折り返し」であり、配送経路自体の不具合ではない。

## ⒝ なお要るか

- 本文に時限の指示は無い。内容は「test_agentという宛先は存在せず、正しい宛先の例はashigaru1」という
  ★診断情報の提供のみ★であり、対応を要求するアクション項目を含まない。
- 4通は完全同一内容（同じ試行を4回繰り返した結果）ゆえ、後発の3通は先発の1通に対して増分情報を持たない。
- ★他の既存記録による裏付け（新規探索ではなく、既に書かれた資産の確認）★:
  同じ「target=test_agent／FROM=karo」の delivery_failed 現象は、複数の既存 incident_logs で
  ★既知・既分析済み★として言及されている——
  - `docs/incident_logs/2026-08-05_stop_before_proceed_rules_a5.md` L14:
    「`test_agent` 宛実行が `karo.yaml` 等canon実boxへ誤配汚染する事故 (`delivery_failed` 4通が実例)」
    ＝★本4通そのものを指して「実例」と記載済み★。
  - `docs/incident_logs/2026-08-05_exit_gate_design_delivery_route_stabilization_a3.md` L77,84,254:
    「`from: inbox_write` の自動生成 `delivery_failed`（「宛先不明: test_agent」）便」を
    「発見のみ・直しておらぬ・scope外」と明記。
  - `dashboard.md` L471: 「実物の `scripts/inbox_write.sh` を直呼び（target=test_agent=canon外／
    FROM=karo=canon内）∴ canon gate が設計どおり発火し FROM の箱へ返送」
    ＝★canon gate の動作検証（意図的なテスト）であったと明言★。
  - 姉妹便（本4通とは別id・type=task_assigned・content=`compat-check`・escalated 08-05T11:31:26）は
    `queue/dead_letter/_unroutable/` 側に別途存在し、家老second が
    `docs/incident_logs/2026-08-06_unroutable_deadletter_triage_karo-second.md` にて
    ★既に「試験の残骸」と断じ「A 用済み」判定済み★（当職が新規に判定するのではなく、
    同一起源の事象について先行判定が既に存在する事を確認したのみ）。
- ∴ 本4通は★「対応を要する用件」ではなく、「機構の設計動作を裏付ける記録」として既に複数箇所へ
  引用済みの情報★——内容としては陳腐化しないが、★行動を要する意味では已に用済み★と見る。

## ⒞ 判ずる権は誰に在るか

「用済み」と最終的に断ずる権は★受け取るはずだった者★＝`karo`本人に属する（下命の原則通り）。
当職（足軽4号）が断じ得るのは「試験の残骸」と「已に閉じられた物」の2種のみ。

本4通は★「試験の残骸」に該当すると当職は判ずる★——理由：
1. `target=test_agent` は名簿に一件も存在しない架空名であり、本番運用の宛先として使われた形跡が無い
2. 22分間に同一内容が4回連続で試行されている＝偶発的な誤入力ではなく、機構（canon gate）の
   動作確認のために繰り返し実行されたパターンと整合する
3. 複数の独立した先行調査（a5・a3・dashboard.md・karo-second）が★同一起源の事象★を
   「canon gate の意図的なテスト」「試験の残骸」と既に性格付けしている（上記⒝参照）
4. 内容自体に本番運用上の実害・後続アクションの必要性を示す情報が無い（純粋な診断メッセージ）

★而して★、「誰が `FROM=karo` で `target=test_agent` の送信を4回試みたか」という★行為者の特定★は、
本票の読取範囲（`queue/inbox/karo.yaml` 単体）からは不能——コマンド実行履歴・shell history・
当時の pane transcript を辿らねば判らない。この一点のみ、権者を特定できないため
「試験の残骸」という★性質判定★は当職が示すが、★最終の廃棄・既読化の実行権は `karo`（本人）★に残す。

## ⒟ 己の手で為した事

- `date -Iseconds` を実行し測時を記録（2026-08-06T20:35:09+09:00）
- `git rev-parse HEAD` を実行（4e8ab81ea680163e8d18872ba3425c8505c12cc3）
- `ls -la queue/inbox/karo.yaml` を実行
- `stat -c 'mtime=%y epoch=%Y' queue/inbox/karo.yaml` を実行
- `wc -l queue/inbox/karo.yaml` を実行
- `sha256sum queue/inbox/karo.yaml` を実行
- `git check-ignore -q queue/inbox/karo.yaml` を実行、exit code=0 確認
- `git status --short queue/inbox/karo.yaml` を実行（出力なし＝未変更を確認）
- `python3 + yaml.safe_load` で `queue/inbox/karo.yaml` の `messages[]` を全件parse
  → total=43／`from=='inbox_write'`=4／`read==false`=4 を実測（filterで抽出、手で数えず）
- 4件それぞれの `id`/`timestamp`/`content`/`type`/`read`/`expires_at`/`supersedes` を個別出力・目視比較
  → content が4件とも文字列完全一致である事を確認
- `/usr/bin/grep -n "agent_id" queue/pane_registry.yaml` を実行（全20件列挙）→ `karo` が
  line32に実在する事を確認（孤児箱ではない事の裏付け）
- `grep -n "delivery_failed\|宛先不明\|test_agent" scripts/inbox_write.sh` を実行
  → L560-568 の REJECT分岐（`_write_message "$FROM" ...`）を特定し、本4通が
  「送信元(karo)への機構自動折返し」である機構的根拠を確認
- `/usr/bin/grep -rn "test_agent" --include="*.sh" --include="*.py" --include="*.md" .`
  （`queue/inbox` 自体は除外）を実行し、他の incident_logs/dashboard.md における
  同一事象の既存記載を収集（上記⒝⒞で引用した4箇所を特定）
- `docs/incident_logs/2026-08-06_unroutable_deadletter_triage_karo-second.md` を読了し、
  姉妹便（別id・別type）が既に「A 用済み」判定済みである事を確認（新規判定と誤読しないため）
- Python (`datetime`) で各便のtimestamp（JST）と測時（2026-08-06T20:35:09+09:00）の差分を計算
  （33.67h／33.48h／33.34h／33.31h、上記表に転記）

## 監査体制

暫定二者制（軍師second+Gemini）。Codex leg停止中（2026-07-21事案）。

以上、本群㈣（対象=`queue/inbox/karo.yaml`・`from=inbox_write`の4通）の仕分け票。
新規探索・新規判定（試験の残骸という性質判定を除く）・新規工区の拡張は行っていない。
対象fileへの書込・`read`立て・移動・削除は一切行っていない（`git status --short` で確認済）。
