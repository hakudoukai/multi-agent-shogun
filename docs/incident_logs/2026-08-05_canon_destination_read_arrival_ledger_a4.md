# W-新規 (工区番号未採番): 『届いたか』別帳 — canon 宛先の最終既読日/便数 台帳

- **発令**: karo-second `msg_20260805_115735_5c982ada` (2026-08-05T11:57:35)
- **執行**: 足軽4号 (SecondPC)
- **提出先**: karo-second
- **母集団凍結時刻 (断面)**: **2026-08-05T12:04:02+0900**
- **監査体制**: 二者制 (Codex leg 停止中・理事長 SAFETY 裁定 seq132707)
- **read: false / read: true → EXISTING_ASSET_CHECK 等 8 項目は本件が inbox 直読の read-only 調査ゆえ非該当。代わりに §0 に母集団導出根拠を明示する。**

---

## §0. 母集団宣言 (手で列挙せず、条件で導出)

**手順**: `ls queue/inbox/*.yaml` 全件 → `.lock` / `.tmp` / `.bak*` / `.historical*` / `_test_*` / `_archive`(dir) を除外 → 残 28 件。

**除外 (7件、理由つき)**: `ashigaru-second-1〜7.yaml`。
理由 = **本日進行中の別発令 `docs/incident_logs/2026-08-05_order_shadow_mailbox_failclosed.md` (委員長殿裁定、leg A/B/C = a5/a2/a3 担当) が明記**:
「`ashigaru-second-1〜7` という **canon 外の宛名**」。
∴ 当職の母集団 (canon 宛先) から除くのが正しい — **含めれば別工区と scope が混ざる** (発令書「三つの穴を混ぜぬ」に反する)。
除外した事実をここに明記し、隠して「全件」とは書かぬ。

**残 21 件 = 当職の canon 宛先母集団**:
`ashigaru1, ashigaru2, ashigaru3, ashigaru4, ashigaru5, ashigaru6, ashigaru7, ashigaru8, fukuincho, gunshi, gunshi-second, honbucho, karo, karo-second, maeda, senmu_codex_second, shogun, shogun-second, takenaka, third_pc, training`

karo-second 殿の当初実測「16名」との差 (21−16=5) は **当職の推定では** `ashigaru8` / `maeda` (persona 名 purge 済) / `karo`・`shogun`・`gunshi` (bare 名・後述 §4-A で shadow 疑い) の 5 件を除けば 16 に一致し得る。**然れど断定はせぬ** — 出所不明のまま「符合した」と書くのは陽性対照の悪用ゆえ、ここでは可能性の提示に留める。

**判定材料 (令の指示通り)**:
- ⒝ 既読判定 = `read: true` の **transition** のみ。`mtime` は不使用 (write で進み循環する為)。
- 「最終既読便」= `read: true` な message の中で **message 自身の `timestamp` (送信時刻)** の最大値。
  本 schema には別途 `read_at` field が **存在しない** (id/read/timestamp/from/type/content/expires_at/supersedes の8 field のみ、全 21 件で確認)。ゆえに「最終既読便の timestamp」は「既読扱いになっている最新の便の送信時刻」を意味する (= それ以降に届いた便は未読のまま、という読み方になる)。

---

## §1. 一覧表 (⒜便数/既読数/最終既読 ⒞watcher実在 ⒟状態判定)

凡例: **状態** = `活性`(本日 断面直近に既読進行) / `不明箱`(便0=判定不能=第四値) / `未読滞留`(便>0・既読0) / `既読あるが停止`(既読はあるが最終既読が古い=居たが止んだ) / `退役`(pane_registry 上撤回済 or persona purge 済で新着自体が止んでいる)。

| 宛先 | 便数 | 既読数 | 最終既読 (送信時刻) | watcher (SecondPC 実プロセス確認) | 状態 |
|---|---|---|---|---|---|
| ashigaru1 | 41 | 40 | 2026-08-05T11:26:43 | **在り** (pid 3181670, multiagent-second:0.1) | 活性 |
| ashigaru2 | 50 | 50 | 2026-08-05T11:51:34 | **在り** (pid 3181840, 0.2) | 活性 |
| ashigaru3 | 40 | 40 | 2026-08-05T11:50:28 | **在り** (pid 3182121, 0.3) | 活性 |
| ashigaru4 (当職) | 41 | 41 | 2026-08-05T11:57:35 | **在り** (pid 3182244, 0.4) | 活性 |
| ashigaru5 | 36 | 36 | 2026-08-05T11:57:35 | **在り** (pid 3182353, 0.5) | 活性 |
| ashigaru6 | 46 | 46 | 2026-08-05T12:02:50 | **在り** (pid 3182462, 0.6) | 活性 |
| ashigaru7 | 42 | 42 | 2026-08-05T11:59:03 | **在り** (pid 3182634, 0.7) | 活性 |
| karo-second | 40 | 35 | 2026-08-05T12:00:34 | **在り** (pid 1990805, 0.0) | 活性 (未読5残るが本日進行中) |
| shogun-second | 33 | 32 | 2026-08-05T11:59:56 | **在り** (pid 2001531) | 活性 |
| gunshi-second | 33 | 33 | 2026-08-05T11:58:39 | **在り** (pid 2001735) | 活性 |
| honbucho | 24 | 24 | 2026-08-05T10:27:19 | **在り** (pid 2006022, hermes-honbucho:0.0) | 活性 |
| ashigaru8 | 49 | 49 | **2026-05-07T16:57:09** | **無し** (プロセス列挙で不在確認) | **退役** — pane_registry「a8 旧standby登録は撤回 (FUKUINCHO裁定 seq96053)」と整合。新着自体が5/7で止まっており「読まれぬ」のではなく「もう誰も宛てておらぬ」。 |
| karo | 43 | 39 | **2026-07-01T21:25:39** | **無し** (SecondPC に「karo」宛 watcher プロセス不在。実在するのは「karo-second」のみ) | **既読あるが停止 + shadow 疑い** — 詳細 §4-A |
| maeda | 43 | 40 | **2026-07-02T02:01:57** | **無し** | **既読あるが停止 + 退役疑い** — persona 名 purge 済 (commit 55ff787 「persona名purge残党一掃」)。未読3件は 2026-07-20/21 (ashigaru5 発、旧 persona 名宛の status_update)。宛先自体が既に存在しない名という別種の停止。 |
| senmu_codex_second | 7 | 5 | 2026-08-03T20:06:59 | **無し** (プロセスにも `scripts/` 参照にも不在) | **既読あるが停止 (2日)** — watcher **infrastructure が最初から無い**。過去の既読5件がどう処理されたか不明 (手動/別経路の可能性、当職では確認不能=第四値として明記)。 |
| third_pc | 1 | 0 | (既読無し) | **無し** | **未読滞留 (最重度)** — 唯一便 (2026-07-16T06:16、shogun-second 発、gunshi-second /clear 未着火の escalation) が **20日間 read:false のまま**。宛先が生存しているか自体、当職からは検証不能。 |
| training | 6 | 0 | (既読無し) | **無し** | **未読滞留 だが訂正済** — 6便中 最後の2便 (2026-08-04T18:08:28) が **本文で「宛先訂正・撤回」を明記** (「研修部長ではなくSecondPCの本部長」)。∴ 未読のままなのは **設計通り** の可能性が高い (宛先自体が誤りと自己申告済)。**咎めに非ず** — 訂正先である honbucho は同日活性 (既読24/24) で着弾を裏付ける。 |
| fukuincho | 0 | 0 | — | 未確認 (プロセスなし) | **不明箱** — 便0件。「探索失敗」ではなく「対象無し」と「未使用」の区別が付かぬ第四値として記す。 |
| gunshi | 0 | 0 | — | 未確認 | **不明箱** (同上。SecondPC には無く MainPC 側 bare 名の可能性、当職から検証不能) |
| shogun | 0 | 0 | — | 未確認 | **不明箱** (同上) |
| takenaka | 0 | 0 | — | 未確認 | **不明箱** (同上。MainPC registry 上 `持ち場準備中` ゆえ空箱は整合的だが断定はせぬ) |

---

## §2. 陽性対照 (令の例示を自手法で再現できたか)

karo-second 殿の例示: 「karo は 40便39既読なれど 最終既読 07-01」。
当職の実測 (§1): **karo = 43便39既読、最終既読 2026-07-01T21:25:39**。
→ **既読数 (39) と 停止日 (07-01) は完全一致。便数 (40 vs 43) のみ差** — これは「約」「概ね」の丸めの範囲内と判断する (令の④「丸めた数と誤った数を分けよ」に従い、誤りではなく概数として扱う)。
∴ **read:true 遷移ベースの自手法は、令が示した陽性対照を独立に再現できた**。

---

## §3. 【本工区で己が直した誤り】(空欄不可)

1. **中間集計の取り違えを自己検知・訂正した**: 最初の実測 (12:00頃) で `ashigaru6`=45既読・`gunshi-second`=31既読と出たが、grep による横断チェックで grep 側は 46/33 を示し不一致が生じた。再調査の結果、**両者とも稼働中 watcher が調査中にも既読を進めていた** (状態がライブに動いていた) ためであり、道具のバグではなかった。∴ **一度目の数値を破棄し、断面を 2026-08-05T12:04:02+0900 に凍結して取り直した** (本報告の数値は全てこの断面のもの)。
2. **母集団の scope 侵犯を自己是正した**: 当初 `queue/inbox/` 全 28 件をそのまま母集団にしかけたが、`ashigaru-second-1〜7` が本日進行中の別発令 (shadow_mailbox_failclosed, leg A/B/C) の対象であり「canon 外の宛名」と明記されているのを見つけ、**母集団から除外**した (§0)。除外せねば §4 で二重に穴を掘るところであった。

## §4. 【この工区と対に成る他工区】(空欄不可)

- **A. `docs/incident_logs/2026-08-05_order_shadow_mailbox_failclosed.md`** (leg A=a5 / B=a2 / C=a3) — `ashigaru-second-1〜7` の影 file 根治。本工区は **その対象を意図的に除外**しており、互いに補完 (母集団の内と外)。
- **B. registry 掃除 (宛先が生きておる事の確認)** — karo-second 殿の令が「三つの穴」として並置した項目。本工区は「届いたか」のみを扱い、registry の生死判定そのものには踏み込んでいない。
- **C. 当職 W208 (`2026-08-04_w208_uplink_number_audit_a4.md`)** — 数の出所突合という同型の「己の実測を検めよ」作業。本工区の §2 陽性対照・§3 自己是正は W208 と同じ作法の継続。

### §4-A. 追加所見 (裁定はせぬ・報告のみ) — `karo` bare 名の shadow 疑い

`queue/inbox/karo.yaml` が **SecondPC ローカルに存在し**、本日 2026-08-05T10:55〜11:16 の間に **4件の `inbox_write` 発 `delivery_failed` 通知が read:false のまま滞留**している。
pane_registry.yaml は SecondPC の役職名を明示的に `karo-second`/`shogun-second`/`gunshi-second` (bare 名と別) と定めており、SecondPC 上に bare 名 `karo` 宛の実 watcher は **存在しない** (プロセス列挙で確認)。
∴ **これは memory 記録済パターン `inbox-write-crosspc-bridge-shadow` (cross-PC 宛が local yaml へ落ちる) の新事例の可能性がある**。断定は避けるが、**誰も読まぬ理由が「怠り」ではなく「そもそも読む者が local に存在しない構造的欠陥」である疑いが強い**点を明記する。同種の `shogun.yaml`(0件)/`gunshi.yaml`(0件) は現状火を噴いていないが、同じ経路の余地として併記する。**本工区の scope 外ゆえ是正はせぬ・報告のみ。**

---

## §5. 検証不能事項 (第四値として明記・「無し」と書かぬ)

- MainPC 側 (`karo`/`shogun`/`gunshi`/`takenaka`/`ashigaru1`〜`2`/`gunshi` 本来の MainPC pane) の **watcher プロセス生死は、SecondPC からは一切確認不能**。§1 の「watcher 無し」欄は「**SecondPC 上には無い**」の意であり「**世界のどこにも無い**」の意ではない。
- `senmu_codex_second` の過去の既読5件がどの経路 (watcher/手動) で処理されたかは、ログ的証跡が見つからず不明。

---

## §6. Not done (scope 外・禁則順守の確認)

- repo 内 file 編集・commit・push・stage・pull・checkout・merge = **せず** (git status --short は本作業前後で `docs/incident_logs/` への新規 `??` 追加のみの想定、他 file 不変)。
- `ashigaru-second-*` 影 file・`dd189` script・agent process = **一切不触**。
- secret 値 = 出力せず (変数名のみ扱った)。
- 裁定・是正の実施 = せず (§4-A も報告に留めた)。

---

## §7. 報告メタデータ

- report path: `docs/incident_logs/2026-08-05_canon_destination_read_arrival_ledger_a4.md` (絶対 path: `/home/hakudokai/projects/multi-agent-shogun/docs/incident_logs/2026-08-05_canon_destination_read_arrival_ledger_a4.md`)
- sha256/行数: 本 file 書込み後に別途 `sha256sum` を実測し追而報告 (自己追記でなく別便で提出)。
