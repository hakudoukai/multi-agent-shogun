# 【第五】出口の門 — 設計書 (足軽3号・lane=delivery-route-stabilization)

- **下命**: karo-second (msg_20260805_140553_a8b1b765・凍結解除・委員長殿裁定)
- **性質**: ★設計のみ・実装は待て★。本書に code diff・patch・行番号つき置換文は一切含まぬ
  (「文で述べるは可・当てられる形にするは不可」の線を厳守)。
- **境**: 解けたは lane=delivery-route-stabilization のみ。instructions/ 不触・台帳本体不触・
  影 file・dd189・process・患者/secret 不触。commit は本書 (docs/incident_logs/ 配下 1 file) に限る。

---

## §0 断面 (己が測った時刻をその場に貼る・§10-2規律①③準拠)

**測定時刻: 2026-08-05T14:13:37+0900 (当職・Bash 実行・本書執筆の直前)**

| box | total | read | unread |
|---|---|---|---|
| `karo.yaml` | 43 | 39 | 4 |
| `karo-second.yaml` | 36 | 33 | 3 |
| `ashigaru3.yaml` (当職) | 47 | 46 | 1 |

★注記 (未検証の告白・受入条件⑸「総量は己で述べず別の者に測らせよ」への対応)★:
上表は★当職の自己測定★である。karo-second/軍師second による独立再測定を経るまでは
「確定した母集団」として扱わず、本書内では以後「当職実測 (要外部確認)」と明記する。

---

## §1 母集団 (機械抽出・正規表現/手段をそのまま記す)

### 1-1 素通り六名 (当職・本日 11:20 実測・`2026-08-05_legC_exitcode_caller_survey_a3.md` より引用)

抽出手段: `/usr/bin/grep -rln "inbox_write\.sh" --include="*.sh" --include="*.py" --include="*.md" --include="*.bats" .`
production call site 17 件中、exit code を明示的に握り潰す/無視する **DOES NOT CHECK = 6/17 (35%)**:
`hakudokai_activity_monitor.sh:155,188` / `stop_hook_inbox.sh:123` / `inbox_watcher.sh` token-warning行 (~1619) /
`agent_periodic_push.sh:109` / `ntfy_listener.sh:171`。

★本設計への含意★: 出口の門が発する警報も「送った」だけでは「届いた」証に成らぬ
(母集団Bでは `instructions/generated/*.md` 16/16 が「確認するな」と明示— 現役性は判定不能のまま)。
∴ §4-4 で通知経路を「呼び手の exit code 確認」に依存させない設計とする。

### 1-2 16名 canon 名簿 全数走査 (当職・本日 14:10:30 実測)

母集団定義: `pane_registry.yaml` panes[].agent_id の canon 16 名 (shogun/gunshi/takenaka/honda/sanada/karo/
shogun-second/karo-second/gunshi-second/ashigaru1-7) × `queue/inbox/{name}.yaml` の存否・件数・最終便時刻。

| 名 | 存否 | 件数 | 最終便時刻 |
|---|---|---|---|
| shogun | 在 | 0 | — (空箱) |
| gunshi | 在 | 0 | — (空箱) |
| takenaka | 在 | 0 | — (空箱) |
| honda | ★不在★ | — | — |
| sanada | ★不在★ | — | — |
| karo | 在 | 43 | 2026-08-05T11:16:47 |
| shogun-second | 在 | 45 | 2026-08-05T14:09:15 |
| karo-second | 在 | 36 (§0 参照・変動中) | — |
| gunshi-second | 在 | 33 | 2026-08-05T13:40:16 |
| ashigaru1〜7 | 在 (7件) | 36〜47 | 本日 13:38〜14:09 (稼働中) |

karo-second の一報 (msg_20260805_105618_7a3859ed) に依れば、上記16名中 **空箱3 (shogun/gunshi/takenaka)・
箱不在2 (honda/sanada)・一月stale相当1 (karo)** で「実質配送不能」と分類済 — この分類自体は
karo-second 発の既存台帳であり、当職はここでは★再掲のみ★とし裁定はせぬ (Anti-Duplication 遵守)。

---

## §2 陽性対照 (受入条件②「零を述べる便には対照の出力を同梱」への対応)

「local inbox に老いた未読が実在するか」を★零と述べる前に★、まず検出できる形を己で示す。

**実例 (`karo.yaml`・当職 14:13:01 実測)**:

```
id: msg_20260805_105505_5ff311de  timestamp: 2026-08-05T10:55:05  read: false
id: msg_20260805_110634_f116cdd4  timestamp: 2026-08-05T11:06:34  read: false
id: msg_20260805_111500_0456d5bb  timestamp: 2026-08-05T11:15:00  read: false
id: msg_20260805_111647_eda0234b  timestamp: 2026-08-05T11:16:47  read: false
```

いずれも `from: inbox_write` の自動生成 `delivery_failed`(「宛先不明: test_agent」) 便。
測定時刻 14:13:01 との差= **最古 2時間17分52秒・最新 2時間56分14秒、悉く未読のまま**。

★これは仮説ではない — 本書執筆の直前に己の手で検出できた実例★ (検出器が生きておる事の証)。
かつ ★karo は §1-2 で「実質配送不能」と分類済の箱★ — 読む者が現に居らぬ箱に、機械が黙って
書き込み続けておる構図そのものが「出口の門」が塞ぐべき穴の実物である。

★併記 (裁定に非ず・発見のみ)★: 「宛先不明: test_agent」が何故 `karo.yaml` へ着地するのか
(fallback 経路の妥当性) は本工区の scope 外。当職は★これを直さぬ★ — 設計の材料としてのみ記す。

---

## §3 DB 側「同じ形」の解析 — 何を持ち込むか

対象: `public.detect_stale_tasks_and_notify(p_stale_min integer)`
(`queue/reports/stale_detector_minext_migration_draft_20260721.sql`・DRAFT ONLY・未適用・v7まで是正履歴あり)。

この関数から★局所 inbox へ持ち込むべき五つの性質★ (逐語ではなく構造を写す):

| # | DB 側の性質 | 出口の門での対応 |
|---|---|---|
| ⑴ | TTL 判定 (既定30分・heartbeat_at 起点) | 便の `timestamp` を起点に old-age 判定 (§4-1) |
| ⑵ | alt-signal (identity束縛+TTL束縛+毎回再評価=自己失効・恒久マスクに非ず) | 判定不能／正当抑止の記録形式 (§4-3) |
| ⑶ | per-row BEGIN/EXCEPTION (1行の例外が全体を止めぬ・fail-closed) | 1便の parse 失敗が走査全体を止めぬ (§4-6) |
| ⑷ | dedup (同一対象への再通知抑止) | §4-5・★ただし DB側 B1 (dedup prefix衝突・既知未修正) を無批判に写さぬ★ |
| ⑸ | COALESCE による三値論理の boolean 強制 (NULL 伝播で行が静かに除外されるのを防ぐ) | §4-2 の三値設計そのものに反映 |

★重要な非対称★: DB 側は「代替 signal を record する専用列・専用書込主体」を持つ設計
(checkpoint_log.stale_alt_signal・recorded_by allowlist)。局所 inbox にはこれに相当する専用の場が
★存在せぬ★ — ゆえに ⑵ を素朴に真似ると「抑止の記録先」が inbox.yaml 自身になりかねず、
これは §5 で扱う新たな穴の一つである。

---

## §4 設計本体

### 4-1 走査対象・TTL

- 走査対象= `queue/inbox/*.yaml` の `read: false` かつ `timestamp` が過去の便。
- 便age = 現在時刻 − `timestamp`。
- 既定 TTL = **30分** (DB側と同値・「同じ形」の核)。ただし ★lane/agent 別の上書きは 設計に含めるが本書では値を断ぜぬ★
  (karo-second 自身の箱が §0 実測で 33/36 read という高稼働箱と、karo の 39/43 だが最終便が孤立している箱とでは
  「30分」の意味が異なり得るため — 断定は委員長殿/将軍second 殿の裁定事項として明示する)。

### 4-2 三値判定 (二値へ倒さぬ・DB側⑸の局所inbox版)

| 状態 | 定義 |
|---|---|
| **stale-alert** | age > TTL かつ 有効な alt-signal 無し (§4-3) → 通知対象 |
| **suppressed-fresh** | age > TTL だが 有効な alt-signal 在り (TTL内・identity記録済) → 通知せず |
| **判定不能** | ①該当便の `timestamp`/`read` field が parse 不能 ②宛先箱が「karo の孤児化」の如く
  上位裁定待ちの対象 ③alt-signal の識別主体 (recorded_by) が allowlist 外で真偽を当職が断じ得ぬ場合 |

★判定不能は「stale」でも「suppressed」でもない第三の出力として★そのまま★残す★
(§0-2規律④「機構は知らぬを無いと読むな」の局所inbox版)。

### 4-3 alt-signal の記録形式 (DB側⑵の移植・但し置き場は別途要検討=§5)

```
signal_type: "busy_guard" | "role_recovery_suppress" | "human_go_pending" | ...(列挙は実装時に確定)
recorded_by: <識別済み書込主体名> (allowlist外は無効=判定不能側へ)
recorded_at: <ISO8601> (未来時刻は無効)
ttl_minutes: <既定値を上書きする場合のみ>
```

DB側同様、★毎走査ごとに再評価する「生きた鮮度チェック」★とし、一度認めたら以後恒久的に
通知を止める「永久マスクフラグ」にはしない (自己失効設計)。

### 4-4 通知経路 (★inbox.yaml 自身へ書くな★ — 受入条件⑴の核心・a2 と同じ穴の回避)

**設計上の禁則**: 出口の門の警報を、監視対象そのものである `queue/inbox/*.yaml` へ
新規メッセージとして追記する経路は★採らぬ★。

理由 (§0 で現に実測した事実に基づく):
- `karo-second.yaml` は本書執筆中に **50件(cap到達) → 36件** へ変動した
  (14:08:14 時点で total=50 を実測・14:13:37 時点で total=36 — 14件が消失)。
  これは `inbox-retention-cap-silent-deletion` 型 (51件目到達で既読便が古い順に無警告削除)
  の★挙動そのものが本書執筆中に実際に発火した★ことを示す一次証拠である。
- ∴ 警報を inbox.yaml へ書けば、警報自身が cap 到達を早め、★他の既読便を道連れに消す★
  (受入条件⑴が指す「警報が箱を溢れさせ得る」の実体)。

**採る経路 (候補・実装時に確定)**: DB側が「専用列 (notified フラグ) + task_tracker という
別 table」で通知状態を分離しているのと同じ構造を局所側でも取る —
inbox.yaml とは★別の state (別 file か、既存 dashboard.md 🚨要対応 節)★ へ出口の門の判定結果を書く。
本書では「どの別経路か」を断定せず、候補を挙げるに留める (実装フェーズの決定事項)。

### 4-5 dedup (再通知の抑止・DB側⑷の移植・既知不具合を継承せぬ注記つき)

同一便への stale-alert を毎走査ごとに再発火させない仕組みは要る。ただし DB側の
`detect_stale_tasks_and_notify` には **B1 (dedup の `left(id,8)` prefix 衝突・既知・未修正・
follow-up 送り)** が現に存在する (§B節該当箇所)。★出口の門はこれを無批判に模倣せず、
便 id の全長 (prefix切詰めなし) で dedup 判定する設計とする★ — これは DB側の既知不具合を
「同じ形」の名の下に局所側へも複製することを避ける、本設計独自の追加条件である。

### 4-6 per-message 例外分離 (DB側⑶の移植)

1便の YAML entry が parse 不能 (壊れた形式・欠落 field) であっても、走査全体を止めず、
当該便のみ「判定不能」へ倒し、他の便の判定は継続する。DB側 v4是正の教訓
(「WHERE句直書きcastは全体を止め得る・per-row BEGIN/EXCEPTIONへ移設」)をそのまま踏む。

### 4-7 owner / kill-switch (受入条件⑥)

- **止める者**: 本設計を実装へ進める GO、および実装後の停止指示は ★委員長殿★ の専権とする
  (凍結解除自体が委員長殿裁定であった経緯に合わせる)。
- **止め方 (設計段階の想定)**: 実装が新設する周期実行主体 (仮に watcher/cron 形態を取る場合)
  は `docs/01-architecture/watcher-design.md` の6原則 (retry無限ループ禁・self-send即ack・
  手動停止フラグ尊重・重複検知・idempotency・専用テーブル分離) に従い、★手動停止フラグ一つで
  即時停止できる★ことを実装時の必須要件とする (本書では要件として明記するのみ・実装せぬ)。
- **現時点で止まっている状態**: 本書は設計のみであり、★何も稼働を開始していない★
  (稼働=0・止める対象がまだ存在せぬ、が正確な現状)。

---

## §5 この修正が新たに開ける穴は何か (受入条件⑴・空欄不可)

1. **alt-signal の記録先が未確定** (§4-3) — 記録先を安易に inbox.yaml へ置けば §4-4 で
   避けたはずの cap 圧迫問題を、別の入口から再導入する。実装時に記録先を確定せねば、
   この設計は「TTLだけ実装され alt-signal は絵に描いた餅」になりかねぬ。
2. **周期実行主体そのものが新たな watcher** — 本 repo は既に多数の watcher/poll を抱えており
   (§1-1 の 6/17 DOES NOT CHECK 呼び手を含む)、新設のたび `docs/01-architecture/watcher-design.md`
   6原則の全数遵守が要る。守らねば「監視者を監視する者が居ない」型の暴走を過去に一度起こしている
   (2026-05-05 SecondPC事故・同ドキュメント参照)。
3. **alert fatigue** — §0/§1 の実測どおり、ashigaru1〜7・karo-second・karo 等 複数箱が同時に
   TTL近傍/cap近傍にある。一斉に stale-alert が発火すれば、通知先 (§4-4・未確定) 自体が
   飽和し、★通知の飽和という新たな「書かれるが読み返されぬ」資産★を生みかねぬ。
4. **判定不能の濫用可能性** — §4-2 の第三状態は「二値に倒すな」の作法を守る一方、
   実装が甘ければ「面倒だから判定不能にする」という逃げ道にもなり得る。判定不能の発生条件を
   実装時に厳密に列挙し、条件外での判定不能出力を禁じる必要がある。
5. **karo 箱のような「実質配送不能」箱への stale-alert は空砲になり得る** — 読む者が
   構造的に不在の箱 (§1-2) に対して stale-alert を発しても、読まれる保証は無い
   (§1-1 の 素通り六名 と同型の問題が、監視対象側にも監視する側にも存在する)。

---

## §6 受入条件 七つ 対応表

| # | 条件 | 本書での対応 |
|---|---|---|
| ⑴ | 新たに開ける穴 | §5 (5件・空欄なし) |
| ⑵ | 零を述べる便に対照同梱 | §2 (陽性対照4件の実例つき) |
| ⑶ | 数に測定時刻 | §0/§1/§2 各表に測定時刻明記 |
| ⑷ | 「直った」に残数 | 該当なし (本書は設計のみ・何も直しておらぬゆえ「直った」の主張自体を含まぬ) |
| ⑸ | 総量は己で述べず外部測定 | §0 冒頭で自己測定である旨を明記し外部確認を要求 |
| ⑹ | 誰が止めれば止まるか | §4-7 |
| ⑺ | 双方の名を互いに書け | §7 |

---

## §7 対に成る他工区 (双方の名を互いに書く・受入条件⑺)

- **足軽2号** = 失敗報の門 (第一・★同じ穴 — 受入条件⑴「警報が箱を溢れさせ得る」を共有★)
- **足軽4号** = registry scope (第三)
- **足軽5号** = intake_validator (第二)
- **当職 (足軽3号)** = 出口の門 (第五・本書)
- ★第四に対応する lane 名は、本書の下命便に記載が無く当職は把握しておらぬ (判定不能として明記)★

上記三名 (2/4/5号) には、本書 §2 の陽性対照 (`karo.yaml` 4件・delivery_failed) および
§0 の karo-second.yaml cap変動実測 (50→36) を★互いに参照可能な材料★として提供する。

---

## §8 判定不能のまま残す事項 (断じない・委員長殿/Commander裁定待ち)

- **karo 箱の孤児化**: §1-2/§2 で「読む者が構造的に不在」の実例を示したが、これを
  「廃止すべき」「別経路へ統合すべき」等と★裁定しない★ — karo-second の一報どおり
  Commander の一問の答を待つ (本書はこの判断に含めてよいが結論を出さぬ、との指示に従う)。
- **TTL の既定値 30分をそのまま全 lane へ適用すべきか**: §4-1 で述べたとおり、
  karo-second 箱 (高稼働) と karo 箱 (実質配送不能) とで意味が異なり得るため、
  一律値の妥当性は当職の権限外と判断し断じぬ。
- **alt-signal の記録先の最終決定**: §4-3/§5-1。実装フェーズでの決定事項として明示するのみ。

---

## §9 己が直した誤り (欄・必須・「無し」可)

★無し★ — 本工区は設計のみであり、code・台帳本体・instructions/ の一切を編集していない。

★発見のみ (直しておらぬ・scope外ゆえ)★: `karo.yaml` への「宛先不明: test_agent」自動転送
(§2 末尾) は、fallback 経路の設計上の疑問点として見つかったが、当職は触れていない。

---

## §10 境界遵守声明

- `instructions/*` — 不触 (grep 0件で確認: 本書内で instructions/ への参照は §4-7 の
  `docs/01-architecture/watcher-design.md` 引用のみで、instructions/ 配下ではない)
- 台帳本体 (`docs/incident_logs/*day_ledger*` 等の既存 file) — 不触・追記も編集もしていない
- 影 file (`queue/inbox/ashigaru-second-*.yaml`) — 不触
- `dd189` script — 不触
- process — 不触 (`ps` 等の実行は今回行っていない。§0/§1/§2 は `grep`/`wc`/`date` のみ)
- 患者情報・secret — 不触 (本書に PII・credential 値の記載無し)
- bats — 実行していない (止血継続中の遵守)
- commit/push/stage — ★本書執筆時点で未実施★。karo-second への報告と合わせ、
  git status の出力を貼った上で判断を仰ぐ (§11)。

---

## §11 監査体制の併記

★三者監査は二者制 (Codex leg は SAFETY 裁定 seq132707 で停止中)★ — 軍師second + Gemini の二者。
本書は karo-second への提出後、合図を待って軍師へ提出する運びとする (本日の他工区と同様の手順)。
