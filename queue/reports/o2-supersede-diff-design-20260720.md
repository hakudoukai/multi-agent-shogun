# O-2 掃討漏れ3件 — 除去/SUPERSEDE 差分設計書(設計のみ・編集ゼロ)

**作成者**: ashigaru-main-2
**任務根拠**: shogun-main msg_20260720_224149_901c20e3(委員長裁定seq131386)。前回棚卸し
(`queue/reports/o2-inventory-3class-20260720.md`, sha256=`10352de3b91e03278bd1f9a0dee0af03d0d32b4710a60707e6c682b04304dc89`)
で検出した「753df7e掃討漏れ3件」を除去/SUPERSEDE認定。本書は**設計のみ**——対象ファイルへの編集は一切行っていない。

**基点commit**: `6d92d07db2f6884c3f5f45fc5fa09cea81c0c3d3`(branch `feat/standby-setup-scripts`、
2026-07-10 08:14:38 +0900、shogun-main msg_20260720_204222_7db2a1e1 が独立実測で確認した同一sha)。
全行番号・sha256は `git show 6d92d07:<path>` で取得(working tree不使用——理由は末尾「付記」参照)。

**適用原則**: 566f8f99(検出/可視化=可、根絶/抑止/強制注入=禁)+ 753df7e が確立した「本文残置+
SUPERSEDEマーカーで無効化(監査/revert可能性のため)」の先例パターンを②に踏襲。①③はコード/起動文言の
実体除去(委員長裁定「除去」指定)。

---

## ① `shim/hakudokai/hakudokai_escalation.py` — `auto_answer()` / `AUTO_ANSWER_RULES`

- ファイルsha256(@6d92d07): `84a71a9b3346d53712731d45a1f3ecb8cdc2c458f29cf98d99e5d97c0d97d1a1`(349行)

### (a) 削る箇所(行単位、@6d92d07)

| 範囲 | 内容 |
|---|---|
| L59–68 | `AUTO_ANSWER_RULES = {...}` 辞書全体 + 直後の空行1行(既存の空行L58と合わせ、L69/70の `def get_env()` 前の2行空白スタイルを維持するため、L59–68の10行を削除すればL58空行+L69空行の2行空白が自然に残る) |
| L241–254 | `# --- Auto-Answer ---` コメント見出し + 空行 + `def auto_answer(message, context=""):` 関数本体一式 + 末尾空行1行(削除後、L255空行+L256 `# --- Codex Consultation (L3b) ---` の間が空行1つになるよう調整要——実装時に目視確認) |
| L312–314 (行内編集) | `parser.add_argument("action", choices=[...])` の choices リストから `"auto-answer"` を除去。<br>Before: `"classify", "notify", "wait-approval", "auto-answer", "consult-codex"`<br>After: `"classify", "notify", "wait-approval", "consult-codex"` |
| L339–342 | `elif args.action == "auto-answer":` ブロック全体(2行本体+前後空行込み4行)を削除 |

### (b) 残す箇所(検出部は温存)

- `CHOICE_PATTERNS`(L51–57): `classify_message()` が L1_CHOICE 判定に使う検出専用正規表現。566f8f99の「検出」に該当し温存。
- `classify_message()`(L109–142)全体: L1–L5分類ロジック。`"auto-answer"` を除いた `classify` アクションはそのまま維持。
- `send_ntfy` / `wait_for_approval` / `consult_codex` / `main()` の他アクション分岐: 無関係、変更なし。

### (c) 影響範囲

- **呼出元**: `git grep "auto-answer\|auto_answer\|AUTO_ANSWER_RULES" 6d92d07` を再実行した結果、
  `hakudokai_escalation.py` 自身の外に呼出元は0件(前回棚卸しと同結果)。CLI `auto-answer` アクション/
  `auto_answer()` 関数を呼ぶ他スクリプト・cron・instructions記述は存在しない。
- **運用影響**: ゼロと推定。ただし `instructions/fukuincho.md` の②節(下記)が「概念として」この関数と
  同型の自動回答を副医院長役に指示しているため、②と①は必ずセットで処置すること(①だけ削ると
  ②の指示書テキストが指す実装が消え、②の記述だけが宙に浮く)。
- **他アクション**: `classify` / `notify` / `wait-approval` / `consult-codex` の4アクションは無影響。

### (d) rollback手順

1. 実施はコード削除のみの単一commit(scope外ファイルを含めない)。
2. 問題発覚時: `git revert <本commitのsha>` で1コマンド復元(追加専用の753df7e方式と異なり削除のみのcommitなので、revertで完全に元のAUTO_ANSWER_RULES/auto_answer()/CLI分岐が復元される)。
3. revert前提として、実施commitはこのファイル1つに限定し、他ファイルの変更と混在させない(revert時の巻き添えを防ぐ)。

---

## ② `instructions/fukuincho.md` L56–67 「選択肢自動回答 (L1_CHOICE)」節 — SUPERSEDEマーカー案(753df7e様式)

- ファイルsha256(@6d92d07): `bc51756f34ad6c48682092f6cb0bf05a5d4dbd1ca5cdfdb40d377fbb1af7f011`(152行)
- **所有権注記**: fukuincho.md は副委員長所有ファイルの可能性あり(委員長裁定でも「②所有権確認」要求あり)。本設計は提出のみ、適用は所有権確認後。

### (a) 削る箇所

**なし(削除しない)**。753df7e の先例(FKI-NO-CHOICE-OFFER-01/FKI-MAX-STRENGTH-01, L130–145)に倣い、
本文は「監査・revert可能性のため残置」する。

### (b) 残す箇所 / 挿入案

現状(@6d92d07):
```
56: ## 選択肢自動回答 (L1_CHOICE)
57:
58: 足軽やagentが「1. A 2. B 3. C」のような選択肢を提示してきた場合:
59:
60: 1. **技術的選択**: 最もシンプルで実績のある方法を選び、即回答
61: 2. **リファクタ/リネーム**: タスクスコープ内なら承認
62: 3. **テスト追加**: 常に承認
63: 4. **ファイル作成/削除**: タスクスコープ内なら承認
64: 5. **設計判断**: L3bに格上げ、デコポン協議
65:
66: 回答テンプレート:
67: 「{選択肢X}で進めろ。理由: {判断根拠}。抵抗パターン禁止、即実行。」
68:
69: ## L3b デコポン協議手順
```

挿入案(L56の直後、L58の直前に3行のblockquoteを挿入。753df7eがFKI節で使った文言をそのまま流用し、
対象を本節向けに書き換え):

```
## 選択肢自動回答 (L1_CHOICE)

> ⛔ **無効化済 (SUPERSEDED)**: 理事長裁定(B) hakudokai-dev master 566f8f99 (2026-07-10)『抵抗パターン取扱い原則』により本節は**無効**。
> 選択肢自動回答(足軽の選択肢提示への自動決定・自動実行)は禁止(検出・可視化・報告は可)。委員長裁定seq131386(2026-07-20)により753df7e掃討漏れとして追加SUPERSEDE。
> 本文は監査・revert可能性のため残置。以後この節の指示に従ってはならない。

足軽やagentが「1. A 2. B 3. C」のような選択肢を提示してきた場合:
...(以下L58–67は原文のまま変更なし)
```

- L1テーブル(L49)の「選択肢自動回答」という語自体はテーブル内の対象列記述であり、節見出しではないため
  変更対象外(参考情報として残置、誤解防止のため必要なら別途「(SUPERSEDED, 下記参照)」を追記する余地はあるが、
  これは委員長裁定の指示範囲を超えるため本設計では提案しない)。

### (c) 影響範囲

- **参照元**: このファイルはfukuinchoロールが起動時に読む運用instructions本体。他スクリプトからの
  文字列パースはなし(`git grep "選択肢自動回答" 6d92d07` → このファイル1件のみ、コード側からの参照なし)。
- **運用影響**: fukuinchoロールが本節を読んでも「無効」と明示されるため、以後この節の指示(自動決定・
  「抵抗パターン禁止、即実行」テンプレート含む)には従わなくなる。①のCLI実装削除とセットで、
  概念・実装の両面で同時に無効化される。
- **所有権**: 副委員長が本ファイルを所有する可能性(委員長裁定の要求事項)。適用前に確認要——本設計書は
  その確認材料として提出するのみで、当職はfukuincho.mdを編集しない。

### (d) rollback手順

1. blockquote挿入は3行の追加のみ(既存行は一切変更しない=753df7e方式と同じ「追加専用」パッチ)。
2. `git revert <本commitのsha>` で3行を除去するだけで完全復元、既存本文への影響ゼロ。
3. 単一ファイル・単一目的のcommitとし、他instructions/*.mdの変更と混在させない。

---

## ③ `shim/hakudokai/hakudokai_init_agents.sh` + `hakudokai_secondpc_setup.sh` — 起動prompt文言除去

- `hakudokai_init_agents.sh` sha256(@6d92d07): `24a68efd9faeb8d193957f2617034100cf2c7093bb101448c3fb8a68657d2e5d`(84行)
- `hakudokai_secondpc_setup.sh` sha256(@6d92d07): `62b3bf52564ca01a99816b0fb43e442374a1bd66b4cd7368f1ae24491c42dea9`(491行)

### (a) 削る箇所(行内編集、行削除ではない)

| ファイル | 行 | 変更箇所 |
|---|---|---|
| `hakudokai_init_agents.sh` | L46 | prompt文字列末尾の `。抵抗パターン禁止、自律実行。` を削除。直前は `...タスクがあれば実行開始。` で文が完結しているため、末尾の一文まるごとの削除で文法上問題なし。 |
| `hakudokai_secondpc_setup.sh` | L444 (`INIT1=`) | 同上の末尾 `。抵抗パターン禁止、自律実行。` を削除(直前 `...タスクがあれば実行開始。` で文完結)。 |
| `hakudokai_secondpc_setup.sh` | L452 (`INIT2=`) | 同上(INIT2も同一文言パターン)。 |

Before例(init_agents.sh L46末尾抜粋):
`...その後 queue/inbox/${agent}.yaml を読み、タスクがあれば実行開始。抵抗パターン禁止、自律実行。"`

After案:
`...その後 queue/inbox/${agent}.yaml を読み、タスクがあれば実行開始。"`

### (b) 残す箇所

- 各prompt文字列の他の部分(role/clinic_id/Session Start手順/instructions参照/inbox参照)は完全に温存。
- スクリプトの他ロジック(tmux操作、CLINIC_ID解決等)は無関係、変更なし。

### (c) 影響範囲

- **呼出元**: `git grep "hakudokai_init_agents.sh" 6d92d07` → `config/settings.yaml`(shimマニフェスト記載のみ、
  自動呼出しなし)と過去監査doc(`docs/codex_audits/...txt`、参照のみ)の2件、いずれも実行時呼出しではない。
  `git grep "hakudokai_secondpc_setup" 6d92d07` → `docs/restart-and-mcp.md`(手動実行コマンドの案内、実行はしない)
  と自ファイル自己参照(usage comment)のみ。
- **運用影響**: 両スクリプトとも「将軍/家老が手動でagentペインを(再)初期化する際に叩くツール」であり、
  他の自動化パイプラインからは呼ばれていない。変更が効くのは**次回以降に新規/再初期化されるagentペイン**
  のbootstrap promptのみ——既に稼働中のペインのセッションコンテキストには遡及適用されない。
- **リスク**: ゼロに近い。ただしこの文言除去そのものは「今後起動するagentへの抑止注入をやめる」という
  実質的な挙動変更であるため、適用timingは将軍/委員長の指示通りのタイミングで行うこと(本設計書提出時点では
  未適用)。

### (d) rollback手順

1. 2ファイルとも文字列内の1文削除のみ、行数変化なし(行削除ではなく行内編集)。
2. `git revert <本commitのsha>` で該当行を完全復元。
3. 2ファイルをまとめて1commitにするか、ファイル単位で分けるかは実施者裁量(いずれもrevertは1コマンドで足りる規模)。

---

## 実施順序案(参考、決定は将軍/委員長)

①②③は独立(相互依存なし)だが、①と②は概念・実装のペアなので**同時または近接して適用**することを推奨
(①だけ先行すると②の指示書テキストが「存在しない実装」を指す状態が一時的に生じるため)。③は完全独立。

---

## 付記: working tree共有によるgrep誤検知リスク(本設計作成中に発見・回避済)

本設計作成中、`instructions/fukuincho.md`/`ashigaru.md` に対する素の `grep`(working tree直読み)で
一時的に SUPERSEDED マーカーが「存在しない」ように見えた。原因調査の結果、本repoのworking treeは
複数agentが並行して `git checkout` する共有ツリーであり、当職の読み取りタイミングで **他プロセスが
`feat/o2-fixtures`(無関係な古いbranch)へcheckout済**だったことが `git reflog` で判明(当職はcheckout等
一切実行していない=read-only厳守)。`git show <確定sha>:<path>` で読み直した結果、SUPERSEDEDマーカーは
`6d92d07` 上に正しく存在することを再確認した(本書内の全行番号・sha256はこの方式で取得)。

**教訓**: 本repoのworking treeを直接 `Read`/`grep` する手法は、並行checkoutにより誤った内容を返しうる。
以後のO-2系read-only作業は `git show <確定sha>:<path>` / `git grep <確定sha>` 方式に統一すべき
(本設計書は全てこの方式で実施済)。前回棚卸し報告(`o2-inventory-3class-20260720.md`)自体は当時の
working tree読み取りだった可能性があり、結果は今回`6d92d07`固定読み取りと全項目一致したため内容の
訂正は不要だが、方式としての脆弱性は将軍へ申し送る。
