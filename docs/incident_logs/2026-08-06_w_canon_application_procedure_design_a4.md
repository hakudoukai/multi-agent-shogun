# W (次任) 正本一本化 — 明文化2件 逐語案の「適用手順」設計 足軽4号

**測時**: 2026-08-06T00:29:00+0900 (`date` 実行、§0 欄①に貼付)
**下命**: karo-second msg_20260806_002057_adfcfce8 (「明文化2件 逐語案の ★適用★ の設計 = 実際に 4 file へ 当てる手順 (①順序 ②検め ③復旧) を書け。実編集は本工区に含めず (設計まで)」)
**前便 (本便の直接対象)**: `docs/incident_logs/2026-08-05_w_canon_documentation_draft_a4.md` (176行 sha256=f1826b336cda38d48c3bd8590c6b346f9abc85b4c1976e4a7450ad9b41f5bb82・軍師second PASS済・commit 749468b)
**境**: 設計のみ・実編集禁・commit禁 (本便自体も未commit — karo-second/軍師second の受理後、通常の保全commitフローに委ねる)。

---

## §0 欄① 命令貼付 + 現況実測 (既存調査・出力そのまま)

```
$ /usr/bin/grep -n "正本一本化設計 a4" queue/pane_registry.yaml shim/hakudokai/hakudokai_watchdog.sh config/settings.yaml config/settings_local.yaml
(4ファイル いずれも 0件 = ★前便の逐語案は まだ 1件も適用されておらぬ★。git status --short も4file とも空 = clean)

$ git status --short queue/pane_registry.yaml shim/hakudokai/hakudokai_watchdog.sh config/settings.yaml config/settings_local.yaml scripts/inbox_write.sh
 M scripts/inbox_write.sh
(→ 対象4fileは全てclean。inbox_write.shのみ他工区が編集中 = 前便の除外判断が本日も引き続き妥当)

$ wc -l queue/pane_registry.yaml shim/hakudokai/hakudokai_watchdog.sh config/settings.yaml config/settings_local.yaml
  210 queue/pane_registry.yaml
  743 shim/hakudokai/hakudokai_watchdog.sh
  149 config/settings.yaml
   38 config/settings_local.yaml
 1140 total
(★編集前の基準行数。適用後の検めに使う★)

$ python3 -c "import yaml; yaml.safe_load(open('queue/pane_registry.yaml')); print('OK')"   → OK
$ python3 -c "import yaml; yaml.safe_load(open('config/settings.yaml')); print('OK')"        → OK
$ python3 -c "import yaml; yaml.safe_load(open('config/settings_local.yaml')); print('OK')"  → OK
$ bash -n shim/hakudokai/hakudokai_watchdog.sh                                                → OK (無出力=構文健全)

$ date
Thu Aug  6 00:23:48 JST 2026
```

**★前便からの食い違い1件 (§6 に「己が直した誤り」として記載)★**: 前便 §1-2a は `config/settings.yaml` の挿入直前を「L108-109 = `#   fukuincho_pc を pc_mapping に新規追加...`」と逐語引用したが、実測では該当文言は L127-128 (`pc_mapping:` ブロック**内側**・`fukuincho_pc:` 直前のネストコメント) に在り、L108-109 の実際の内容は「注: ashigaru3 は非常時のみ起動...」であった。**ただし挿入先そのもの (`pc_mapping:` トップレベルキー直前) は一意に定まっており (下記 uniqueness 確認)、実害は無い** — 前便の「引用テキスト」が誤っていただけで、「挿入位置の構造的定義」(=トップレベル `pc_mapping:` の直前) は今回の実測でも変わらず有効。

```
$ /usr/bin/grep -n "^pc_mapping:" config/settings.yaml config/settings_local.yaml
config/settings.yaml:110:pc_mapping:
config/settings_local.yaml:5:pc_mapping:
$ /usr/bin/grep -n "^  notes:" queue/pane_registry.yaml
queue/pane_registry.yaml:17:  notes:
$ /usr/bin/grep -n "^import sys, yaml$" shim/hakudokai/hakudokai_watchdog.sh
shim/hakudokai/hakudokai_watchdog.sh:159:import sys, yaml
```
**∴ 4アンカー全て単一出現 (一意)。「引用文の一致」ではなく「構造キーの一意性」でアンカーを取れ、が本件の教訓 (§10-2 item 4 と同型 = 名で当てた物は実体で確かめよ)。**

---

## §1 適用順序 (①) — 危険度昇順・4段階

**原則**: 挿入は全4件とも「既存コメント/文字列への追記のみ・ロジック変更ゼロ」ゆえ相互依存は無い (どの順でも機能的には成立)。∴ 順序は **挿入点の構造的脆さ (壊した時に沈黙のまま壊れる度合い)** で決める。

| 順 | file | 挿入点の性質 | 危険度 | 理由 |
|---|---|---|---|---|
| 1 | `config/settings_local.yaml` | トップレベル `#` コメント (スカラー外) | 最低 | YAML構造に無関係・引用符不要・SecondPC限定读込 |
| 2 | `config/settings.yaml` | トップレベル `#` コメント (スカラー外) | 低 | 同上・ただしMainPC共有読込ゆえ僅かに広い |
| 3 | `queue/pane_registry.yaml` | 単一引用符 YAML ブロックスカラー (`notes:` フィールド内) | 中 | 引用符スカラー内追記ゆえ **単引用符の混入で構文破壊し得る** (下記§2-3で無混入を確認済) |
| 4 | `shim/hakudokai/hakudokai_watchdog.sh` | bash heredoc (`<<'PY'`) 内 python コメント | 最高 | (a) heredoc終端`PY`との衝突可能性 (b) python構文への波及可能性 (c) **本file は稼働中watcherが読むscope判定コードを含む** (D006条件⑤「shared watcher」に該当する隣接file) |

**∴ 低リスクから着手し、③④で問題が出れば①②の完了実績を汚さずに個別ロールバックできる形にする。④ (watchdog.sh) は最後に置き、①②③の検めが全てPASSした後にのみ着手する。**

---

## §2 各file の適用手順 + 検め (②)

### 2-1. `config/settings_local.yaml` (第1段)

1. アンカー確認: `grep -n "^pc_mapping:" config/settings_local.yaml` → 単一行 (L5) であることを確認 (既に§0で確認済・適用直前に再実行)。
2. 挿入: L3 (`# inbox_write.sh の cross-PC bridge が参照する pc_mapping を SecondPC視点に切替`) の直後・L5 (`pc_mapping:`) の直前に、前便§1-2b の逐語コメント3行を挿入。
3. **検め (直後)**:
   - `python3 -c "import yaml; yaml.safe_load(open('config/settings_local.yaml'))"` → 例外なしで完走すること。
   - `git diff config/settings_local.yaml` → **追加行のみ (削除行0)** であることを目視確認。
   - `wc -l config/settings_local.yaml` → 38+3=41行になっていること (基準行数との差分が挿入行数と一致)。
4. **もし失敗**: `git checkout -- config/settings_local.yaml` で即時復旧 (baseline がclean commitゆえ安全)。次のfileへ進まず、失敗内容をkaro-secondへ報告してから再開。

### 2-2. `config/settings.yaml` (第2段)

1. アンカー確認: `grep -n "^pc_mapping:" config/settings.yaml` → 単一行 (L110) であることを再確認。**★前便の「L108-109引用文」は使うな (§0の食い違い参照)。構造キー (`^pc_mapping:`) 一致で位置を取れ★**。
2. 挿入: `pc_mapping:` (L110) の直前 = 現行L109 (`#     ashigaru8 も同様の理由で second_pc.agents に保持。`) の直後に、前便§1-2a の逐語コメント4行を挿入。
3. **検め (直後)**:
   - `python3 -c "import yaml; yaml.safe_load(open('config/settings.yaml'))"` → 例外なし。
   - `git diff config/settings.yaml` → 追加行のみ。
   - `wc -l config/settings.yaml` → 149+4=153行。
   - **追加確認 (本file固有)**: 挿入がL126-132の既存 `fukuincho_pc` 隣接コメントと視覚的に混同されぬよう、挿入ブロックと既存ブロックの間に空行が保たれているか目視。
4. **もし失敗**: `git checkout -- config/settings.yaml` で復旧。

### 2-3. `queue/pane_registry.yaml` (第3段・★引用符ブロッカー実在★)

1. アンカー確認: `grep -n "^  notes:" queue/pane_registry.yaml` → 単一行 (L17) を再確認。
2. **★挿入前の必須チェック (本fileのみ)・実測で問題を検出★**: 挿入するテキスト (前便§1-1a の4段落目) の単引用符 `'` を実際に数えたところ **2件** 検出された (`python3` で `text.count("'")` を実行・下記)。
   ```
   >>> text.count("'")
   2
   ```
   出所= 前便が引用した埋込コード片 `` `if p.get('pc') != pc_role: continue` `` 内の `'pc'` の2文字。**前便執筆時 (本便草稿の当初版) は「丸め等の記号なし」を確認したのみで、単引用符の有無は確認しておらず、当初 本便に「0件確認済」と誤って書きかけた — 実行して初めて誤りに気付いた (§6 に追記)。**
   **∴ このまま逐語挿入すると、YAML単一引用符スカラー (`notes: '...'`) の途中で引用符が閉じてしまい構文破壊する。適用時は必ず `'pc'` → `''pc''` (YAML単引用符スカラー内のエスケープ規則=1文字の`'`は`''`で表現) へ置換した版を挿入すること。他の3段落 (config/settings*.yaml のコメント2件・watchdog.shのpythonコメント) は `#` コメント行または既にpython文字列外のためこの制約を受けない。**
3. 挿入: L21 (`advisory のみ...`) と L23 (閉じ引用符 `'`) の間に、前便§1-1a の4段落目を **上記エスケープ済み版で** 追記 (既存の3段落構造= 空行区切りブロックの後に4段落目として)。
4. **検め (直後・最重要)**:
   - `python3 -c "import yaml; d=yaml.safe_load(open('queue/pane_registry.yaml')); print(len(d['pane_registry']['notes']))"` → 例外なく文字数が表示され、旧値より増加していること (スカラーが破壊されず伸びたことの直接証拠)。
   - `git diff queue/pane_registry.yaml` → 追加行のみ。
   - `wc -l` → 基準210行+追記行数。
   - **behavioral回帰確認 (本fileは稼働中の読込対象ゆえ必須)**: 編集後fileに対し `load_inbox_agents_from_registry` 相当のpython抽出 (§0で読んだ hakudokai_watchdog.sh L151-175 のロジックをそのまま単体実行) を **`PC_ROLE=MainPC` と `PC_ROLE=SecondPC` の両方**で実行し、編集前に同条件で取得したagent一覧 (baseline) と **完全一致**することを確認する。
5. **もし失敗**: `git checkout -- queue/pane_registry.yaml` で復旧。**この file は複数agentが常時読むため、失敗を検知したら他agentへの影響有無 (直近の read timestamp) も併せてkaro-secondへ報告する**。

### 2-4. `shim/hakudokai/hakudokai_watchdog.sh` (第4段・最終・最重要)

1. アンカー確認: `grep -n "^import sys, yaml$" shim/hakudokai/hakudokai_watchdog.sh` → 単一行 (L159) を再確認。
2. 挿入: L159 (`import sys, yaml`) の直後・L160 (`path, pc_role = sys.argv[1], sys.argv[2]`) の直前に、前便§1-1b の逐語 python コメント4行を挿入。
3. **検め (直後・二段階)**:
   - **静的**: `bash -n shim/hakudokai/hakudokai_watchdog.sh` → 無出力 (構文健全)。
   - **heredoc抽出構文検め**: heredoc本体 (L158-174付近、`cat <<'PY' ... PY`) を単体抽出し `python3 -c "compile(open('/tmp/extracted.py').read(), '<string>', 'exec')"` で python 構文エラーが無いことを確認 (bash -n はheredoc内部のpython構文までは検めぬため、**この段が本手順で唯一の「bash -n が見落とし得る」検めであり省略不可**)。
   - **動的 (最終確認)**: `load_inbox_agents_from_registry()` 相当を編集後のfileから抽出し、baseline (2-3で取得済のagent一覧) と再度突合し完全一致することを確認 — **ロジック不変を「読んで判断」ではなく「実行して確認」する**。
4. **★本file固有の境界★**: 本fileは**稼働中watcherの一部** (D006条件⑤「shared watcher」隣接)。★comment-onlyの変更ゆえ稼働中プロセスの再起動・kill は本設計の範囲外かつ本工区のstop boundary★ — 変更を稼働中プロセスへ反映させる必要があるか否かの判断・実行は別途karo-second/委員長の明示GOを要する (再起動が要る場合はD006条件⑤の理事長承認案件)。**適用手順自体は「fileを書き換える」までであり、「稼働へ反映させる」は含めない**。
5. **もし失敗**: `git checkout -- shim/hakudokai/hakudokai_watchdog.sh` で復旧。**稼働中watcherに影響し得るfileゆえ、失敗を検知したら他3fileの適用が既に完了していても連鎖して疑わず、本file単体の問題として報告する** (相互依存ゼロという前提に基づく切り分け)。

---

## §3 復旧手順の総括 (③)

| 段階 | 復旧コマンド | 前提として安全な理由 |
|---|---|---|
| 各段 個別失敗時 | `git checkout -- <対象1file>` | baselineが4file ともclean commit (§0実測)。他fileへの影響なし (相互依存ゼロ)。 |
| 全4段 完了後に問題発覚 | 逆順 (4→3→2→1) で個別 `git checkout` | 挿入は加算のみ・削除を伴わぬため、どの段まで戻しても残りは独立して健全 |
| watchdog.sh 適用後に稼働影響の疑いが生じた場合 | ★fileのgit checkoutのみ実施・プロセスの再起動/killは実施しない★ | プロセス操作はD006/Tier1境界であり本工区・本設計のscope外 (実行者=ashigaruの権限を超える) |

**壊れる試験の件数 = 0件見込み**: 4件とも既存ロジック・既存試験対象コードパスに変更を加えぬ (コメント/文字列追記のみ) ため、既存のtest suiteへの影響は無いと見込む。★ただし実測ではない (実際にtestを走らせて確認したのは本設計の範囲外)★ — 実適用の際は、適用直後に既存test (TC-FR-003b/LB-07b 等、W201関連) を実行し件数0件であることを実測で確認するステップを追加することを推奨する。

---

## §4 全体完了後の総合検め

1. `git status --short` で対象4fileのみが `M` として現れ、他fileに意図せぬ変更が波及していないことを確認。
2. `git diff --stat` の4fileそれぞれの `+` 行数が、前便§1で提示した逐語案の行数と一致することを確認 (例: pane_registry.yamlなら4段落分の行数)。
3. 4fileの `-` (削除) 行数が **全て0** であることを確認 (追記のみの原則が守られたことの直接証拠)。
4. 実commitはこの設計の範囲外 — karo-second/委員長の明示GOの後、通常の保全commitフロー (本件の前例=commit 749468b) に委ねる。

---

## §5 境界 (stop boundaries・本工区共通)

- 実編集そのものを本工区に含めない (設計のみ・§0の検めコマンドは「読み取り専用」のみ実行済、書込は一切実施せず)。
- `scripts/inbox_write.sh` は引き続き不触 (他工区が現在進行形で編集中・前便§2の判断を本日も再確認し妥当と確定)。
- watchdog.sh の稼働プロセスへの反映 (再起動等) は本設計・本工区のscope外。
- registry/pc_mapping/hakudokai_watchdog.sh/inbox_write.sh への**実際の書込**は本工区でも実施していない (git status確認済・全てclean)。

---

## §6 己が直した誤り (欄・空欄不可)

**誤り1 (本便執筆中に自ら検出・最重要)**: 本便は当初 §2-3 で「前便の pane_registry.yaml 挿入文に単引用符は含まれない」と書きかけたが、これは**確認せず思い込みで書いた**ものであった。実際に `python3` で `text.count("'")` を実行したところ **2件** (埋込コード片 `p.get('pc')` 由来) が検出され、当初の記述は誤りと判明した。★これを確認せず「確認済」と書いたまま提出していれば、次任が本設計に従って逐語挿入した瞬間に `queue/pane_registry.yaml` のYAML構文を破壊していた★ (本fileは複数agentが常時読む稼働中file)。§2-3 を実測に基づき訂正し、エスケープ (`'pc'`→`''pc''`) を適用手順の必須ステップとして明記した。

**誤り2**: 前便 (`2026-08-05_w_canon_documentation_draft_a4.md` §1-2a) が `config/settings.yaml` の挿入直前の引用文を「L108-109」として逐語引用したが、実測では該当文言 (`#   fukuincho_pc を pc_mapping に新規追加...`) は L127-128 (pc_mapping ブロック内側のネストコメント) にあり、L108-109 の実際の内容とは異なっていた。本便§0-§2-2 でこれを実測により発見・訂正し、挿入手順を「引用文一致」ではなく「構造キー (`^pc_mapping:`) 一意性」でアンカーする方式に改めた。実害 (誤った位置への挿入) は本便が実編集を伴わぬため未発生。

**共通の型**: 両誤りとも「読んで大丈夫そうに見えた」箇所を**実行して検めずに済ませかけた**点で同型 (CLAUDE.md Critical Thinking Rule / 2026-08-04 規律「名で当てた物は実体で確かめよ」)。誤り1は特に、**実行確認を省いていれば PASS 済の前便を土台に構文破壊を次任へ手渡すところであった**という点で重い。

---

## §7 完了規準 (self-check)

- [x] ①適用順序 + 理由 — §1 表
- [x] ②各段の検め (静的+動的、可能な箇所は実行確認) — §2 各節
- [x] ③壊れた時の復旧 (全段・個別) — §3 表
- [x] 全体検め (④相当) — §4
- [x] 境界の明記 (プロセス反映は別GO要) — §5
- [x] 己が直した誤り欄 (空欄不可) — §6 (前便のsettings.yamlアンカー引用誤り)
- [x] 壊れる試験件数欄 — §3 末尾 (0件見込み・未実測と明記)
- [x] 実編集ゼロ (git status clean を§0で確認・本便執筆中も書込なし)
- [x] ETA = 本便提出をもって完了 (設計作業自体は即時完了)

---
report path: docs/incident_logs/2026-08-06_w_canon_application_procedure_design_a4.md
