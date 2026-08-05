# inbox_write.sh 呼び手 FROM引数 canon/和名 判定 台帳 (足軽2号)

- **下命**: karo-second (msg_20260805_140235_784252fc, 2026-08-05T14:02:35)。
  「repo 内で inbox_write.sh を呼ぶ箇所を列挙し、FROM 引数に何を渡しておるかを一件ずつ読め
  (canon id か 和名か)。零を述べるなら陽性対照を同梱せよ」。
- **縛り (遵守)**: 凍結 (工区新設禁・本書は新規 W 番号を採らず既存の下命名のみで綴じる) /
  commit・push・stage 禁 / bats 実行禁 (止血継続中・karo-second 令 msg_20260805_121348_364ebac2) /
  registry・inbox_write.sh・墓場 file は ★読むのみ★ (改変一切なし) / dd189・process 不触。
- **本書の性質**: measurement/discovery のみ。17箇所の「是正」(FROM を canon id へ書き換える実装) は
  本工区の範囲外 — 下命は「読め」であって「直せ」ではない。

---

## 0. 母集団の定義 (先行資産を再利用・Anti-Duplication 順守)

母集団Aの定義・抽出コマンド・除外基準は **足軽1号 `docs/incident_logs/2026-08-05_legC_17site_ledger_a1.md`**
(典拠= 足軽3号 legC survey 3書) を再利用する。当職はこれを写さず、独立に再実行して一致を確認した:

```
/usr/bin/grep -rn "inbox_write\.sh" --include="*.sh" --include="*.py" scripts/ shim/
```
(`scripts/archive/`・`.bak*`・test file・散文言及(comment/docstring/Usage文)・変数代入のみの行を除外)

**断面凍結時刻 (当職実測)**: 2026-08-05T14:1x (本書執筆時)。**再実行結果 = 17件、a1 の母集団と一致** (独立検証済)。

a1 の台帳は「exit code を検めるか」の軸で17件を判定した。**本書はそれとは別の軸 — FROM 引数の canon 性**
を同じ母集団に対して判定する。file:line 番号は a1 の通し番号 (#1〜#17) をそのまま引き継ぎ、突合を容易にする。

---

## 1. 判定基準

| 区分 | 定義 |
|---|---|
| **canon** | 渡された FROM の値が `queue/pane_registry.yaml` の `pane_registry.panes[].agent_id` 集合に文字列一致する。 |
| **canon外 (和名/系統名)** | 上記集合に無い固定文字列 (persona名・PC名・process名等)。 |
| **canon外 (PC名/和名・動的)** | 実行時に外部データ (msg の `from_pc` フィールド等) から取り込む値で、取り得る値の集合自体が非canon (`second_pc`/`third_pc`/`main_pc` 等)。 |
| **判定不能 (二値に倒さず残す)** | 値が実行時の自由文字列 (message content 由来の正規表現抽出等) に依存し、canon にも和名にも両方成り得る、または当該コード経路が現に一度も呼ばれていない (dead code) ため判定材料自体が存在しない。 |

**canon id 集合 (当職が `queue/pane_registry.yaml` から実測抽出、`agent_id:` 行を全 grep)**:
`shogun, karo, ashigaru1, ashigaru2, ashigaru3, ashigaru4, ashigaru5, ashigaru6, ashigaru7, gunshi,
gunshi-second, karo-second, shogun-second, takenaka, honda, sanada, honbucho` (17 種、`ashigaru1-3` は
MainPC/SecondPC 両方に同名で存在するが集合としては同一文字列)。

---

## 2. 全17件 判定 (a1 の通し番号を継承)

| # | file:line | FROM の実体 (読んだコード) | 判定 |
|---|---|---|---|
| 1 | `shim/hakudokai/hakudokai_secondpc_watcher_poll.py:274-282` | `sender = "second_pc"` (既定) → `re.search(r'\[(\w+)→', content)` が一致すれば `sender = m.group(1)` (message 本文の自由文字列を **無検証で** 採用) | **判定不能 (二値に倒さず)** — 既定値自体は canon外 (`second_pc`)。正規表現一致時は本文次第で canon id にも和名にもなり得、canon 照合が一切無い。§4-2 に実例 (`将軍second` が実際にここを通った証拠)。 |
| 2 | `shim/hakudokai/hakudokai_fukuincho_reverse_poll.py:151-152` | `from_pc = msg.get("from_pc", "unknown")` (pc_handshake message の PC 名フィールドをそのまま転用) | **canon外 (PC名/和名・動的)** — 取り得る値は `second_pc`/`third_pc`/`main_pc` 等の PC 名であり、いずれも registry の agent_id 集合に無い。 |
| 3 | `shim/hakudokai/hakudokai_activity_monitor.sh:155` | 固定文字列 `activity_monitor` | **canon外 (系統名)** |
| 4 | `shim/hakudokai/hakudokai_activity_monitor.sh:188` | 固定文字列 `activity_monitor` | **canon外 (系統名)** (#3 と同一起動経路・同一値) |
| 5 | `shim/hakudokai/hakudokai_secondpc_receiver_poll.py:353` | `from_pc = msg.get("from_pc", "unknown")` | **canon外 (PC名/和名・動的)** (#2 と同型) |
| 6 | `shim/hakudokai/hakudokai_fukuincho_poll.py:125` | 固定文字列 `fukuincho` | **canon外** — ★`fukuincho` 自体が registry `agent_id` 集合に無い★ (§4-1 で実測確認、`queue/pane_registry.yaml` に `fukuincho` の行は0件)。 |
| 7 | `shim/hakudokai/hakudokai_fukuincho_poll.py:136` | 固定文字列 `fukuincho` | **canon外** (#6 と同一理由) |
| 8 | `scripts/agent_health_check.sh:159` | 固定文字列 `health_check` | **canon外 (系統名)** |
| 9 | `scripts/redundancy/shogun_report_watcher.sh:234,237` (`notify_shogun()`) | 固定文字列 `shogun_report_watcher` | **canon外 (系統名)** |
| 10 | `scripts/karo_overload_monitor.sh:350` | 固定文字列 `nobunaga` | **canon外 (persona 別名)** — ★これは canon id `shogun` の persona alias (`persona_aliases.shogun: nobunaga`, registry 199-203行) であり、まさに下命が名指す「和名で名乗る」型の実例。コード内コメント (343-344行) には「from = nobunaga (信長補完 watcher)」と ★意図して persona 名を使う設計★ である旨が明記されている。 |
| 11 | `scripts/fukuincho_report_poke_bundle.py` `report_insert_via_inbox_write()` (呼出元 `report_and_poke()`) | `from_agent` は呼出元が渡す必須引数 | **判定不能 (該当なし)** — `report_and_poke()` の呼び手を repo 全域で検索したが ★0件★ (`/usr/bin/grep -rn "report_and_poke(" --include="*.py" .` が自身の定義とテストのみに一致)。`hakudokai_fukuincho_reverse_poll.py` が同ファイルから import するのは別関数 `fire_poke_local` (これは inbox_write.sh を呼ばず、Windows python.exe 経由で poke を発火するのみ)。∴ この呼び出し自体が **現在 dead code** であり、FROM に実際に渡される値が存在しない。 |
| 12 | `scripts/stop_hook_inbox.sh:123` | `"$AGENT_ID"` = `tmux display-message ... '#{@agent_id}'` (自 pane の tmux user option) | **名目上 canon (但し条件付き)** — 値そのものは「起動時に自分の canon id を名乗る」設計だが、pane への `@agent_id` 焼き込みが正しい前提に依存する。過去に非canon命名で焼かれた実例が既知 (respawn 経路の欠陥、本書執筆時点で当職が直接再現検証はしていない・伝聞に基づく留保)。 |
| 13 | `scripts/inbox_watcher.sh:594` (`return_message_to_sender()`) | `"$AGENT_ID"` (自 watcher 自身の canon id・delivery_failed 通知の FROM として使用) | **名目上 canon (#12 と同じ留保)** — ★この関数自体が「FROM が canon なら通知を返す」canon fail-closed gate の中核だが、この関数の呼出コンテキストにおける FROM は「配送に失敗した watcher 自身」であり、本survey の対象である「他の呼び手が渡す FROM」とは層が異なる (メタ的な自己参照)。 |
| 14 | `scripts/inbox_watcher.sh:1619` (token-warning) | 固定文字列 `shogun` | **canon (陽性対照①)** — registry agent_id 集合に実在。当職の判定法が「canon」を正しく検出できる証跡。 |
| 15 | `scripts/shogun_self_check.sh:31` | 固定文字列 `systemd_self_check` | **canon外 (系統名)** |
| 16 | `scripts/agent_periodic_push.sh:109` | 固定文字列 `shogun` | **canon (陽性対照②)** — #14 と同一値、独立した呼び手での再現。 |
| 17 | `scripts/ntfy_listener.sh:171` | 固定文字列 `ntfy_listener` | **canon外 (系統名)** |

## 3. 集計 (記憶でなく本表から数えた)

- **17件中訳**: canon外(固定文字列・系統名/persona別名) = 8件 (#3,4,6,7,8,9,10,15,17 → 実数9件、内訳下記)。
  再集計 (誤数え防止のため表から直接数え直し):
  - **canon (陽性対照)**: #14, #16 = **2件**
  - **canon外 (固定文字列)**: #3, #4, #6, #7, #8, #9, #10, #15, #17 = **9件**
  - **canon外 (PC名/和名・動的 `from_pc`)**: #2, #5 = **2件**
  - **名目上canon・条件付き (`$AGENT_ID`)**: #12, #13 = **2件**
  - **判定不能 (二値に倒さず)**: #1, #11 = **2件**
  - 合計 2+9+2+2+2 = **17件** (§0 母集団と一致)。
- **∴ 明確に「canon id」を渡しているのは 17件中 2件のみ (#14, #16、いずれも固定文字列 `shogun`)**。
  残り15件は「canon外」「動的PC名」「条件付きcanon」「判定不能」のいずれかであり、
  下命が名指した「和名で名乗る」型 (#1既定値・#2・#5・#10) を含め、**canon 前提が薄い状態が例外ではなく多数派**。

---

## 4. 陽性対照 (下命必達・零を述べる前に検出器が生きている事を示す)

### 4-1. `fukuincho` が canon外である事の実測根拠

```
$ /usr/bin/grep -n "fukuincho" queue/pane_registry.yaml
(0件)
$ ls -la queue/inbox/fukuincho.yaml
-rw------- 1 hakudokai hakudokai 336 Jul  2 13:13 queue/inbox/fukuincho.yaml
```
★file の mtime が 7/2 のまま (本日 8/5 時点で33日間更新なし)★。**但し正直に記す**: canon fail-closed gate
自体は本日 (`subtask_shadow_failclosed_legB_a2_20260805`、当職が今朝実装) 新設されたものであり、
この gate が33日間の無更新の**原因であるとは断定できない** (gate 新設は今日、無更新は gate 以前から)。
∴ 「`fukuincho` 宛が33日間 canon gate で弾かれ続けていた」という因果は主張しない — **相関のみを記し、
原因は判定不能として残す**。今後 (gate 稼働後) は #6,#7 の target=`fukuincho` は TARGET_BAD として
現に弾かれる状態にある事は、上記 grep 結果 (0件) から機械的に導かれる。

### 4-2. `queue/dead_letter/_unroutable/` の実データ (10件全件・読むのみ)

下命の名指す2例 (`third_pc` / `将軍second`) が、**理論上の懸念ではなく現に本日発生した実データ**である事を
生の出力で示す:

```
$ for f in queue/dead_letter/_unroutable/*.yaml; do
    /usr/bin/grep -E "^from:|^target:|^closed_at:" "$f"; echo; done

from: karo            target: test_agent        (closed_at 無し)
from: third_pc         target: honbucho          closed_at: '2026-08-05T12:36:25'
from: 将軍second        target: hermes            (closed_at 無し)
from: 将軍second        target: hermes            (closed_at 無し)
from: 将軍second        target: hermes            (closed_at 無し)
from: third_pc         target: honbucho          closed_at: '2026-08-05T12:36:25'
from: third_pc         target: honbucho          closed_at: '2026-08-05T12:36:25'
from: third_pc         target: honbucho          (closed_at 無し)
from: third_pc         target: honbucho          (closed_at 無し)
from: third_pc         target: honbucho          (closed_at 無し)
```

**内訳 (10件全件)**: `from=karo` (canon) 1件 / `from=third_pc` (和名/PC名) 6件 (3件closed・3件openのまま) /
`from=将軍second` (和名/persona) 3件 (**全件 open のまま、closed_at 無し**)。

**★対照実験 (canon FROM は実際に通知が届く事の確認)★**: `from=karo` の1件は `reason:
target_non_canon_from_canon_but_inbox_stale` であり、gate の別経路 (FROM_OK だが inbox 再解決性が
stale 判定) を通ったが、それでも FROM が canon であったため karo 本人の実箱に通知が着地している:
```
$ /usr/bin/grep -c "宛先不明: test_agent" queue/inbox/karo.yaml
4
```
(この4件は今朝 karo-second が「止血命令」で名指した delivery_failed 4通と同一群と見られる —
別工区の話題だが本書執筆中に遭遇したため、混同を避けるため脚注として明記のみ行い、深入りしない。)

**★これに対し `from=third_pc` / `from=将軍second` の9件は、reason 欄がいずれも
`unroutable_target_and_unresolvable_from` — FROM 自体が canon 外ゆえ、どの実箱にも通知が
書かれず dead_letter へ直行している。★** `third_pc→honbucho` の3件が closed_at を持つのは、
自動配送経路が機能したからではなく、**委員長殿が pane へ直打ちする別経路で気付いて手動救済した**
結果 (該当 file `closed_reason: '既達(別経路・委員長pane直打ち)・再送不要・2026-08-05委員長裁定'`)
—— ★これはまさに下命の一句「和名で名乗る者は不達を永久に知り得ない」の実例で、
救済されたのは自動機構ではなく人手による偶然の気付きだった事を示す★。
残る `将軍second→hermes` の3件と `third_pc→honbucho` の3件、計6件は本書執筆時点で ★未だ open のまま★。

**∴ 本書は「零」を主張していない (canon外の実例は現に9件・open未解決6件が実在) が、
上記 karo の1件を陽性対照として併記し、当職の判定法が「canon なら通知が届く」ことを
正しく検出できる事を示した。**

---

## 5. 【本工区で己が直した誤り】

**無し。** 本工区は read-only の調査・分類のみであり、`inbox_write.sh`・`pane_registry.yaml`・
`queue/dead_letter/`・呼び手 file のいずれも1文字も編集していない。

---

## 6. 【どこまで検めたか】(疑義の広さと検めの広さは別)

- **検めた**: `scripts/` `shim/` 配下の production call site 17件全件を file:line 単位で実読し、
  FROM に渡る値の出所 (固定文字列 / 変数 / 呼出元引数) を追跡した。`queue/pane_registry.yaml` の
  agent_id 集合を実 grep で抽出し照合した。`queue/dead_letter/_unroutable/` 全10件を実読した。
- **検めていない (自己申告)**:
  - `tests/*.bats` `tests/*.py` `scripts/tests/*.py` 内の inbox_write.sh 呼出 (a1 の母集団定義に倣い
    「振る舞い検証であり本番呼び手ではない」として除外・件数は数えていない)。
  - #1 (`hakudokai_secondpc_watcher_poll.py`) の正規表現 `\[(\w+)→` が **実際に運用中どのような
    sender 値を生成してきたか** の全数調査 — §4-2 で `将軍second` が1件この経路で dead-letter 化した
    「証拠」を示したが、それが本当にこのファイルのこの行を経由したかまでは trace log を突き合わせて
    いない (経路として整合するが、当職は個々のメッセージのログ trace までは追っていない・
    ★判定材料は状況証拠であり確定証拠ではない★)。
  - #12/#13 の `$AGENT_ID` が実際に非canon値で焼かれた事例が現存するか — 伝聞 (memory の既知事故)
    に基づく留保のみで、本SecondPC上での再現検証は行っていない。
  - `fukuincho.yaml` が33日間更新されていない**真の原因** — gate 新設前からの無更新であり、
    poll script の非稼働・fukuincho 側の非読出しなど他の原因候補を排除できていない (判定不能のまま残す)。

---

## 7. 【この工区と対に成る他工区】

- **足軽1号 `2026-08-05_legC_17site_ledger_a1.md`** — 同一母集団17件を「exit code を検めるか」の軸で
  判定済。本書はこれの FROM-canon 軸での対。母集団定義を継承・独立再実行で一致確認済。
- **足軽3号 legC exitcode survey 3書** — a1 の典拠。本書は間接的にこれも継承。
- **足軽6号 `2026-08-05_unroutable_triage_a6.md`** — `queue/dead_letter/_unroutable/` 10件を
  「第一者の証で判じ得るか」の軸で分類済 (target側の honbucho 追加タイミングに着目)。
  本書は同じ10件を FROM 側 (canon/和名) の軸で読んでおり、§4-2 で直接引用・突合した。
- **軍師second (監査)** — 本書は未提出・両者未実施 (下記§9)。
- **人手 dispatch 層 (17箇所の是正実装)** — 本書の範囲外。是正 (FROM を canon id へ書き換える、
  または #1 の正規表現抽出に canon 照合を追加する等) は別途下命が要る。

---

## 8. 判定不能の明記 (二値に倒さず残す・下命必達)

- **#1**: 既定値は canon外だが、正規表現抽出時は本文次第で canon にも和名にもなり得る。二値化せず
  「入力に無検証で依存」という性質そのものを判定として残す。
- **#11**: dead code (呼び手0件) ゆえ FROM 値そのものが存在しない。「和名である」とも「canon である」
  とも言えない ★該当なし★ という第四の値として残す。

---

## 9. 二者制の併記 (下命必達)

★本書の監査は 二者制 (軍師second + Gemini)。Codex leg は SAFETY 裁定 seq132707 で停止中・
監査モデル gpt-5.4 暫定★。「三者PASS」とは書かない。本書は提出前・両者とも未実施。

---

## 10. 禁則の遵守 (再掲・確認)

測定・台帳化のみ (read-only)。影 file 不触・dd189 不触・process 不触・commit/push/stage 禁・
scope 拡大なし (工区新設せず・是正実装は範囲外)・凍結下で新規に増やしたのは「己を厳しくする事」
(独立再検証・二正本読了) のみ。
