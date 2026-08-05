# W-新規 (工区番号未採番): registry 全数棚卸し + 一括登録

- **発令**: karo-second `msg_20260805_123521_c513df51` (2026-08-05T12:35:21)、出所=委員長殿裁可 `msg_20260805_123141_5de6198b`
- **執行**: 足軽4号 (SecondPC)・提出先: karo-second
- **母集団凍結時刻 (断面)**: **2026-08-05T12:42:00+0900** (以下の実測は全てこの断面)
- **監査体制**: 二者制 (Codex leg 停止中・理事長 SAFETY 裁定 seq132707)
- 前提資産 (再掲禁・参照のみ): `docs/incident_logs/2026-08-05_canon_destination_read_arrival_ledger_a4.md` (queue/inbox/*.yaml 21件の母集団を既に確定済)

---

## §0. 母集団宣言 (手で列挙せず、条件で導出。★何処まで探したかを明記★)

一度で足す (令⒜「1つずつ足すと母集団の欠けを再演する」) ため、以下 **4 系統を同時に**棚卸しした。

1. **受信側 (宛先)**: `docs/incident_logs/2026-08-05_canon_destination_read_arrival_ledger_a4.md` §0/§1 の既確定 21 件母集団を再利用 (再測せず引用)。
2. **送り手 (_unroutable の from/target)**: `queue/dead_letter/_unroutable/unroutable_20260805_*.yaml` を `ls` で**全件**列挙 (grep 内容検索ではなく directory listing。理由は §3-1 参照)。
3. **実 process の watcher 名**: `ps -ef | grep -i watcher` (SecondPC ローカルのみ・全件)。
4. **tmux pane の @agent_id**: `tmux list-panes -a -F '#{session_name}:... @agent_id=...'` (本ホストの全 tmux server・全 session・全 pane)。

**★探しておらぬ所 (明記)★**:
- **pc_handshake の送り手名 (third_pc 等)**: DB/API 経由の情報であり、SecondPC の当職の権限・視界では secret を用いずに引けぬ。令の禁則「secret 値を出力するな・探して回るな」に従い、**探索を行わなかった** (探して0件だったのではなく、探していない=検証不能の第四値)。
- **MainPC 側 の watcher process / tmux pane**: SecondPC からは一切確認不能 (前工区 §5 と同じ制約、再確認せず引用)。

---

## §1. 一覧表 (発見名 × 既存registry在否 × 実在証拠 × 判定)

凡例: **判定** = `追加`(実在証拠3点以上・登録実施) / `見送り`(実在証拠不足=名は加えず) / `既存`(登録済で変更なし) / `棚上げ・裁定せず`(実在するが registry の"agent pane"概念に該当するか要判断、当職からは断定せず報告のみ)。

| 発見名 | 発見経路 | registry 既存? | 実在証拠 (2026-08-05T12:4x 実測) | 判定 |
|---|---|---|---|---|
| **honbucho** | 受信側21件中 / watcher / tmux | **無し (欠落確認)** | ①watcher pid 2006022 (`scripts/inbox_watcher.sh honbucho hermes-honbucho:0.0 codex`) ②tmux pane `hermes-honbucho:0.0` @agent_id=honbucho ③`queue/inbox/honbucho.yaml` 24便24既読・最終既読2026-08-05T10:27:19 | **追加 (実施済・§2)** |
| shogun-second 〜 gunshi-second (SecondPC 12名) | 受信側21件中 / tmux / watcher | 既存 | 前工区 §1 で個別実測済 (活性 or 既読あるが停止) | 既存・変更なし |
| shogun / karo / gunshi / takenaka / honda / sanada (MainPC 6名) | 受信側21件中 | 既存 | MainPC 側は当職の視界では未検証 (§0 の限界どおり) | 既存・変更なし (再検証せず) |
| **karo** (bare 名、宛先0.0既読あるが最終既読07-01) | 受信側21件中 / _unroutable from | SecondPC には無し (karo-second のみ) | queue/inbox/karo.yaml に実体あるが SecondPC watcher process 不在 (前工区 §4-A 既報)。本日11:31 `from=karo target=test_agent` 便が dead-letter | **見送り** — 実体は"読まれぬ受信箱"であって"実 watcher を持つ agent pane"ではない。前工区 §4-A の shadow 疑いを再掲するに留め、pane 追加はせず |
| **test_agent** | _unroutable target (1件、11:31:26) | 無し | reason=`target_non_canon_from_canon_but_inbox_stale`。宛先自体が canon 外と明記 | **見送り** — 実在証拠は「dead-letter に現れた」のみで、agent としての実体 (watcher/pane/inbox) 皆無 |
| **third_pc** | _unroutable from (5件、いずれも target=honbucho) | 既存 (persona_aliases には無いが概念として ALL-SSH-NO-NEW-ENDPOINT-01 で既定の接続先) | SecondPC 上に third_pc 宛 watcher/pane は無し。実在は「third_pc という PC 自体」の話であり pane_registry の tmux pane 概念とは別次元 | **見送り** — 既に CLAUDE.md ALL-SSH-NO-NEW-ENDPOINT-01 で正本管理されており、pane_registry への重複登録は不要と判断 (二重正本回避)。断定は避け報告に留める |
| **hermes** (bare 名) | _unroutable target (3件、from=将軍second) | 無し | SecondPC 上に `hermes` 単体宛の watcher/pane は無し (`hermes-honbucho`/`hermes-gunshi-second` という**複合名**の pane はあるが `hermes` 単体ではない) | **見送り** — 実在証拠なし。`hermes-*` 複合名との混同が unroutable の原因である可能性を示唆するに留める (裁定せず) |
| **将軍second** (漢字表記) | _unroutable from (3件) | 無し (shogun-second は既存) | shogun-second 自身が「from」欄で自称に用いた形跡はあるが、当職はこれが shogun-second の別名なのか別経路なのかを**実体で確かめておらぬ** | **棚上げ・裁定せず** — persona_alias 追加は routing 挙動に影響する判断ゆえ、当職の権限を超えると判じ、karo-second への報告のみとする |
| honbucho_downlink_watcher.py (pid 405/530) | ps -ef | — (pane 概念に非ず) | 実在 (hermes-departments 配下の別プロセス。honbucho の agent inbox_watcher とは別物) | **棚上げ・裁定せず** — pane_registry は「tmux pane + agent_id」の概念であり、本 process は下位の配送インフラ。登録対象の型が異なると判断し追加せず、存在のみ報告 |
| senmu_desktop_route_watcher (inbound/outbound、pid 853230台/3759956台) | ps -ef | — | 実在 (専務ルート watcher、bridge インフラ) | **棚上げ・裁定せず** — 同上理由 (pane を持たぬインフラ watcher) |

---

## §2. 実施した登録 (1件・実施根拠)

`queue/pane_registry.yaml` の `panes:` 末尾 (gunshi-second entry の直後、`# a8 (旧 registered standby...)` コメント行の直後) に **honbucho を1件追加**した。

- **編集前**: sha256=`1c807cb4ae8603da9d32c4a70730be5ae06bebb3953ab4cfff51702c7cf3c874` / 196行
- **編集後**: sha256=`20886275f98efffb85c5492dabcc781e10be2ac80c4884fa8463c05ba52f184d` / 210行 (+14行)
- **YAML 構文検証**: `python3 -c "import yaml; yaml.safe_load(open('queue/pane_registry.yaml'))"` → 例外無し・`panes` 件数 19→20 に増加確認済 (己で読み返して確認)
- **git diff**: `docs/incident_logs/` 配下の新規追加のみを想定していた前工区と異なり、本工区は**唯一 `queue/pane_registry.yaml` を意図的に変更** (令の主旨)。`git status --short` は `M queue/pane_registry.yaml` のみ (他 file 不変を確認)。**commit/push/stage は行っていない** (working tree 変更のみ)。
- **自己改変防止機構**: 本編集では発火せず (令が警告した壁には当たらなんだ)。当たった場合の手順 (即止まり・迂回せず karo-second へ報告) は今回は不要だった。

---

## §3. 【本工区で己が直した誤り】(空欄不可)

1. **_unroutable の母集団を grep 内容検索で取り違えかけた**: 当初 `grep -rl "_unroutable"` で 9 件と数えたが、`queue/dead_letter/_unroutable/` を `ls` で直接列挙し直すと **10 件**存在した (`unroutable_20260805_113126_ed7db710.yaml` は本文中に文字列 `_unroutable` を含まぬため grep 内容検索から漏れていた)。**道具の出力を判定と読むな (既知の失敗型) の再発を自ら検知し、directory listing に切り替えて是正した** (§0 に反映済)。
2. **honbucho の実在証拠を1系統 (watcher pid) のみで確定させかけた**: pid 発見のみで即登録判断せず、tmux pane と inbox 履歴の計3系統が揃うまで判定を保留し、揃ってから §2 の追加を実施した (令⒝「実在証拠1行」だが当職は安全側で3点を揃えた)。

## §4. 【この工区と対に成る他工区】(空欄不可)

- **A. `docs/incident_logs/2026-08-05_canon_destination_read_arrival_ledger_a4.md`** (当職・同日) — 本工区の受信側母集団 (§0-1) の直接の土台。両者は「誰が実在するか (本工区)」と「実在する宛先が読まれておるか (前工区)」で相補。
- **B. `docs/incident_logs/2026-08-05_order_shadow_mailbox_failclosed.md`** (leg A=a5/B=a2/C=a3) — `ashigaru-second-1〜7` という canon 外の宛名を扱う工区。本工区は同名を母集団に含めず (前工区 §0 の除外を踏襲)、互いに補完 (canon 内/外)。
- **C. 家老second下命が言う「三つの穴」の残り一つ ((c)=失敗が消えぬ事)**: 本工区が扱ったのは「宛先が生きておる事」のみ。dead-letter 自体が消えるか否か ((c)) は本工区の scope 外であり、別工区が要る。

---

## §5. 検証不能事項 (第四値として明記・「無し」と書かぬ)

- **pc_handshake の送り手名**: secret 不使用の制約下で探索不能。0件ではなく「探索未実施」。
- **MainPC 側の実 watcher process / tmux pane**: SecondPC からは一切確認不能 (registry 既存6件は前回同様「記録参考」扱いのまま、当職は変更していない)。
- **将軍second (漢字) が shogun-second の別名か否か**: 当職の権限・視界では断定不能。§1 参照。

---

## §6. Not done (scope 外・禁則順守の確認)

- **影 file** (`queue/inbox/ashigaru-second-*` 等) = 不触。
- **dd189** script = 不触。
- **process** = 一切起動/停止せず (`ps -ef` は読取のみ)。
- **commit・push・stage** = せず (working tree 変更のみ、§2 参照)。
- **`_unroutable` の file** = 一件も削除・改変せず (読取のみ)。
- **bats 実行** = せず (止血命令 `msg_20260805_121349_28b3f51c` 継続中を順守)。
- **裁定** = `karo` bare 名 shadow 疑い・`将軍second` alias 疑い・third_pc/hermes の扱いは全て「棚上げ・裁定せず」とし、karo-second の判断に委ねた。

---

## §7. 報告メタデータ

- report path (絶対 path): `/home/hakudokai/projects/multi-agent-shogun/docs/incident_logs/2026-08-05_pane_registry_full_inventory_bulk_register_a4.md`
- 本 file の sha256/行数は書込み後に別途実測し追而報告 (自己追記でなく別便、前工区と同じ作法)。
- 変更した canon file: `queue/pane_registry.yaml` (sha256 変化 = §2 参照。git 上は working tree 変更のみで未 commit)。
