# 2026-08-06 CAP_ROTATED 箱の主通知 (足軽3号)

下命= karo-second msg_20260806_021657_0b74da3e (発注根拠= 将軍second が機構化候補として起票のみとした物を、
理事長令「止まるな」と当職が file の持ち主である事を以て karo-second の判断で発注。差止めあれば直ちに取り下げ)。

## 0. 断面

- 着手前 (pre-edit): `scripts/inbox_write.sh` 726行 / sha256=`a960383f8fff9cd2be7f36f29bb9bc5a78d3ca3397bf95088fa9c4e141e6034b` / base_commit=`f3501fd`
- 着手前 git status: `M shim/hakudokai/senmu_desktop_route_watcher.py` (本工区と無関係・他 lane の作業残) / `?? docs/incident_logs/2026-08-06_venv_collection_count_feasibility_a4.md` / `?? docs/incident_logs/2026-08-06_w205b_name_kill_enumeration_a1.md` (いずれも足軽4号・足軽1号の別工区成果物・不触)
- 着手後 (post-edit): `scripts/inbox_write.sh` 769行 / sha256=`fd90c6aa0dceb91b5aa80183a69791804aefa844c029df52e12df1de3582e09a`
- 差分: +43/-0 (既存行の削除・改変なし。既存契約への破壊的変更を避けるため純追記で実装)

## 1. 既存を探した結果 (欄①新様式・打った命令を貼る)

```
$ /usr/bin/grep -n "CAP_ROTATED\|cap_rotat" scripts/inbox_write.sh
187: (本件コメント自身)
213: print('[inbox_write] CAP_ROTATED: ...) file=sys.stderr)   ← 旧実装・呼び手stderrのみ
335: # 50件超で既読分を _archive/<agent>_pruned.yaml へ CAP_ROTATED 退避する (コメント)

$ /usr/bin/grep -rln "CAP_ROTATED" .
./scripts/inbox_write.sh (現行) / .bak-w67fix / .bak-w67 / .bak-realpath-20260803-225945 (いずれも旧版バックアップ・不触)
./scripts/read_pruned_archive.sh (退避archiveの読み手ツール・既存)
docs/incident_logs/*.md 3件・queue/orders/*.md 1件・queue/reports/*.md 2件 (いずれも言及のみ・機構実体なし)
queue/inbox/{ashigaru3,ashigaru4,ashigaru2,ashigaru7,karo-second}.yaml + queue/inbox/_archive/*_pruned.yaml
  → 全て「stderrを当職が偶々見て手で告げた」履歴便であり、機構としての箱の主通知は探索範囲内に0件

$ /usr/bin/grep -n "_notify_pc_dispatcher_of_unroutable\|cap_rotated_notice" scripts/inbox_write.sh
→ 既存の隣接機構 (_notify_pc_dispatcher_of_unroutable) は「FROM不明の墓場落ちをPC差配者へ」通知する物であり、
  宛先も事象も本件 (CAP_ROTATEDを箱の主target自身へ) とは別。二重実装ではない (対工区として §5 に記す)。
```

母集団宣言: 上記4正規表現 (`CAP_ROTATED\|cap_rotat` / `CAP_ROTATED` repo全体 / `_notify_pc_dispatcher_of_unroutable\|cap_rotated_notice`) を `scripts/inbox_write.sh` 単体および repo 全体へ適用。
結論: 箱の主(target)向けの CAP_ROTATED 通知機構は着手前に0件 (探した限りで無し)。

## 2. 設計・契約 (下命 ⒜⒝⒞⒟)

**核となる設計判断**: 別便を新規に `_write_message()` 経由で送るのではなく、CAP_ROTATED を起こしている
その同一 atomic write の中で、target 自身の未読メッセージとして `data['messages']` へ直接埋め込む。

理由: `_write_message()` は「今まさに target のinboxファイルをlock済で開いて書いている」関数そのものである。
その内部で target 自身への通知を組み立てて `data['messages']` に足すだけなら、新しい lock 取得や新しい
python subprocess 呼び出しを一切増やさない。∴ 通知そのものが新たな CAP_ROTATED を誘発する再帰は
**構造的に起き得ない** (下命の「注意」への直接の答え)。既存の `_notify_pc_dispatcher_of_unroutable` は
別ファイル(差配者の実箱)へ**別途** `_write_message()` を呼ぶ設計であり、これは「n件束ねて間引く」ことで
再帰を抑えているが、本件はそもそも別呼び出しを発生させないため束ねが不要。

- ⒜ 増分Nと累計Mを分けて書く: `len(dropped)` = 今回のevent増分N。累計Mは今回書込み後の archive file
  (`_apath`) を `yaml.safe_load_all()` で読み直し、各 document の `count` フィールドを合算して求める
  (今回分もすでに書込済のため自動的に含まれる)。読み直し失敗時は過大表示を避け、今回分Nを下限として代入。
- ⒝ 退避先path: 通知本文に `_apath` (絶対path) をそのまま含める。
- ⒞ multi-doc YAML: 通知本文に「`yaml.safe_load()` では読めず `yaml.safe_load_all()` を用いよ」と明記し、
  既存の読み手ツール `scripts/read_pruned_archive.sh` を参照させる。
- ⒟ git外: 通知本文に「git 外 (`queue/_archive` は追跡対象外)」と明記。

## 3. 実装

`scripts/inbox_write.sh` の `_write_message()` 内、overflow rotation ブロック (旧182-206行) に純追記。
既存の archive書込・stderr出力・永続log書込のロジックは一切変更していない (差分は追記のみ・既存契約非破壊)。

追記箇所の要旨: `dropped` が非空の場合、archive 書込直後に累計Mを算出し、`cap_rotated_notice` 型の
メッセージを組み立てて `unread` リストへ追加してから `data['messages'] = unread + read[-30:]` で確定する。

## 4. 負テスト四形 (実行可能な形・実測。bats framework は不使用 — 全隊 bats実行禁 [karo-second msg_20260805_161255_ce922f57・点検日2026-08-08]継続中のため、既存 `tests/test_inbox_write.bats` と同型の sandbox (SCRIPT_DIR書換コピー + `.venv` symlink) を python3/bash 直呼びで再現し、bats框組を経ずに実測)

sandbox 構築 (既存 `tests/test_inbox_write.bats` setup() と同型・非canonの `test_agent` を通すため sandbox専用
`queue/pane_registry.yaml` と `config/settings_local.yaml` (is_local) を用意 — 実 canon registry・実 pc_mapping は不触):
`/tmp/claude-1000/.../scratchpad/cap_rotate_sandbox/{scripts/inbox_write.sh(sed書換コピー), .venv(symlink), queue/pane_registry.yaml, config/settings_local.yaml}`

### ⒜ 51便到達で通知便が箱の主へ現に届く

```
(既読50件を事前投入 → 51件目書込)
$ bash sandbox/scripts/inbox_write.sh test_agent "the 51st message" test_type test_sender
[inbox_write] CAP_ROTATED: 20 read messages moved to .../_archive/test_agent_pruned.yaml
```
検証結果: `test_agent.yaml` 内に `type: cap_rotated_notice` のメッセージが1件・`read: False` で存在。
内容 = `[inbox_write→本人] 箱の容量上限(50件)超過につき既読便を退避いたし申した (増分N=20件・累計M=20件・退避先=…)。退避先はmulti-document YAMLゆえ yaml.safe_load() では読めず、yaml.safe_load_all() を用いよ (scripts/read_pruned_archive.sh 参照)。git 外 (queue/_archive は追跡対象外)。`
→ **PASS** (箱の主=target自身の実箱に、未読として、機械可読な形で到達)

### ⒝ 増分Nと累計Mが別々に書かれておる

1回目event: N=20, M=20 (archive doc 1件目、`sum(count)=20`)
2回目event (別途50件到達を再現): N=20, M=**40** (archive doc 2件目追加、`sum(count)=20+20=40`)
→ N (今回分) と M (累計) が数値として分岐することを実測で確認。archive内 `yaml.safe_load_all()` で
読み直した `sum(count for doc)` が通知本文のMと一致 (40=40)。→ **PASS**

### ⒞ 通知便それ自体が回転を誘発して無限にならぬ

- 静的根拠: 通知は `_write_message()` の**呼び出し追加なし**で同一atomic write内に埋め込む設計 (§2) ゆえ、
  再帰呼び出し経路がコード上に存在しない (`grep -n '_write_message "' scripts/inbox_write.sh` → 呼び出し箇所
  3箇所のみ、いずれも本件追記コードの外)。
- 動的根拠: 150回の連続書込 (各書込後に全既読化して繰り返しrotationを誘発する最悪系ケース) を
  60s/90sのhard timeout付きで実行し、ハング無く完走 (実測 27秒・rc=0)。CAP_ROTATED は6回発火・
  archive累計=120件・最終メッセージ数は cap 近傍 (36件) に収束し、無限増殖なし。
→ **PASS**

### ⒟ 回転が起きぬ時は通知も出ぬ (過剰に鳴らすな)

既読40件+未読5件 (計45件、cap未満) の状態で1件追記 → `CAP_ROTATED` 行 0件・`cap_rotated_notice` 型メッセージ
0件。さらに120回の連続書込 (全て未読のまま=read化しない系列。`dropped=read[:-30]=[]`ゆえ `if dropped:` が
falseで通知ブロック自体に入らない) でも `cap_rotated_notice` 0件のまま完走。→ **PASS**

## 5. この工区と対に成る他工区

`_notify_pc_dispatcher_of_unroutable()` (同ファイル内、2026-08-05 lane=delivery-route-stabilization)。
あちらは「FROM不明で墓場(dead_letter)へ落ちた便」をPC差配者(既定=shogun-second)の実箱へ束ねて通知する。
本件は「CAP_ROTATEDで既読便が退避された」ことをその**箱の主自身**(target)へ通知する。
宛先(差配者 vs 箱の主本人)も事象(dead-letter vs 既読cap超過)も異なるため二重実装ではないが、
「機構化されていない通知の穴を塞ぐ」という同種の作業であり、束ね/間引きの設計判断 (あちらはcap=5/interval=300s
で束ねる・本件は同一writeへの埋め込みで束ね自体が不要) を対比すると設計選択の理由が読み取りやすい。

## 6. 本工区で己が直した誤り

無し (探索範囲=本ファイルの overflow rotation ブロック182-206行・隣接する `_notify_pc_dispatcher_of_unroutable`
関数・repo全体の `CAP_ROTATED` grep。既存ロジックの削除・改変は行っておらず、純追記のみ)。

## 7. 実行した負テストの限界 (確度)

- sandbox の cross-PC bridge は `config/settings_local.yaml` の `is_local: true` で LOCAL 経路に固定しており、
  実運用の Supabase bridge 経路 (BRIDGED/UNROUTABLE 分岐) は本件の対象外 (target=box owner の実箱書込という
  ローカル分岐のみを検証対象とした・意図的にscope外・cross-PC配送の可否は本工区の主張に含まない)。
- 累計M算出はarchiveファイルの読み直しに依存する。archive file自体が外部から破損/削除された場合の
  fallback (今回分Nを下限として返す) は実装したがテストでは未実測 (再現に破損注入が要る・未検証は未検証と明記)。

## 8. 三者監査の体制

二者制 (Codex leg は SAFETY 裁定 seq132707 で停止中)。本工区は軍師second へ直提出。

---

## §9 追補 —— 契約追加⑴⑵ の反映 (提出後に着信・drift 自己申告)

**時系列 (隠さず記す)**: 当職の初回提出 (§0-§8) は 2026-08-06T02:2x台に送達済であった所、
karo-second の契約追加二件 (msg_20260806_022008_8725d1eb / msg_20260806_022200_2e7aa326) は
その ★数分前に着信しており、当職が読んだのは提出後★ であった (「交差」— 本日隊が幾度も記録した型)。
karo-second 便は「再提出は不要=貴殿は未着手ゆえ」としていたが、その前提 (未着手) は
★当職の実態 (提出済) と食い違っていた★ ため、当職の判断で本追補を追加し、drift を自己申告する。

### 追加⑴: 累計Mの出所訂正

karo-second 明示=「mtimeは最後の1回しか示さぬゆえ累計の出所に使えぬ ∴ archiveの★doc数★
(safe_load_allで数える)とせよ」。

**初回提出時の実装は これに反していた**=archive内各documentの `count` フィールド (退避
メッセージ総数) を合算しており、「doc数(rotation event回数)」ではなく「メッセージ累計数」を
Mとして報じていた。★これは当職が直した誤りである★ (§6 を訂正=「無し」ではなく本件1件)。

訂正実装=`_cum` を「documentの個数」として数え直し (`_cum += 1` per document、フィールド値の
合算はせず)、数え得ぬ場合は数値0で埋めず文字列 `'未測'` を代入 (0と未測を混ぜぬ)。

**実測 (2箇所での経験的検証・読取のみ・実 repo の既存 archive に対して)**:
```
$ (yaml.safe_load_all で全12箱の queue/inbox/_archive/*_pruned.yaml を doc数/count合算の両方で集計)
_test_cap_rotation: docs=1 sum_count=21 (2026-08-03 由来の他工区の遺物・不触)
honbucho: docs=1 sum_count=20
ashigaru1〜7 + gunshi-second + karo-second + shogun-second (計10箱、canon):
  docs合計=186 / sum_count合計=3178
```
将軍second が引用した「全箱通算166 doc・10箱」とは一致せず (186 と 166)。★これは当職の実装の
誤りではなく、対象数が動く母集団を異なる断面で測った結果と判断する★ (karo-second・当職とも
今日一日で幾度も記録した「実測値は断面である」の当てはまり — karo-second の166は当職の実測より
前の断面である公算が高いが、当職はそれを検証する権限のログを持たぬため★断定はせず併記に留める★)。

サンドボックスでの再検証: 訂正後の実装で event1=M「1」件・event2=M「2」件と正しく
rotation event回数として増分することを実測 (§4 ⒜⒝ と同型の sandbox で再実行)。

### 追加⑵: 負テスト⒠ (通知便を51件目に置いた時の挙動)

karo-second の第二便 (msg_20260806_022200_2e7aa326) が自ら補正=「別便を送らぬ設計では
この境界は★そもそも起こり得ぬ★ ∴ 『該当せず・理由は設計上別便が無いゆえ』と明記せよ。
0件と該当せずを分けよ」。

**⒠ 判定 = 該当せず (0件ではない)**。理由: 本実装は CAP_ROTATED 通知を独立した便として
`_write_message()` で送信しないため、通知が「51件目のメッセージ」としてinboxに積まれ次の
overflowを引き起こす、という事象の入力条件 (独立送信) 自体が存在しない。通知は既存の
`data['messages']` 再構成 (`unread + read[-30:]`) の直後に1件差し込まれるのみであり、この
差し込みが新たな `len(data['messages']) > 50` 判定を誘発することはない (次回 `_write_message()`
呼び出し時まで判定自体が走らない)。

### 断面

- 訂正後: `scripts/inbox_write.sh` 773行 / sha256=`6060e9c1e8d358255e4809f25b6ac65f7455bf05d684f88d83ffc0d430df280d`
- 初回提出時 (訂正前・§0-§8時点): 769行 / sha256=`fd90c6aa0dceb91b5aa80183a69791804aefa844c029df52e12df1de3582e09a` (現物は既に訂正後版に置換済・この sha は来歴記録のみ)
