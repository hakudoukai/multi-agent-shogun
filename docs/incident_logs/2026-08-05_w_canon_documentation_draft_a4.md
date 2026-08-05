# W (次任) 正本一本化 — 明文化2件 逐語案 + 条⑿自己適用 足軽4号

**測時**: 2026-08-05T17:12:25+0900 (`date` 実行、§0 欄①に貼付)
**下命**: karo-second msg_20260805_170909_3c22624b (「次ブロック=正本の一本化、実装は為さず合意の材料まで」)
**前便 (本便の直接土台)**: `docs/incident_logs/2026-08-05_w_canon_source_unification_design_a4_corrected.md` (訂正版・結論=実装変更不要・明文化2件のみ必達)
**境**: 設計/起草のみ・実装禁・commit禁・registry/pc_mapping/hakudokai_watchdog.sh/inbox_write.sh 不触 (読むのみ)。

---

## §0 欄① 命令貼付 (既存調査・散文禁・出力そのまま)

```
$ /usr/bin/grep -n "scope\|watcher.*対象\|正本" queue/pane_registry.yaml
109:  # ── SecondPC vessel 最終正本 map (FUKUINCHO 裁定 seq96053 / 改訂 R-series seq96064/96065) ──
116:  #   本 map は最終正本。live 位置は R2+ swap 完了まで移行表の『現況』を参照。
（→ registry.pc 自体を説明するコメントは0件。上記2行は別トピック=vessel map の正本表示）

$ /usr/bin/grep -n "routing\|scope\|正本" config/settings.yaml config/settings_local.yaml
config/settings.yaml:130:  #   commander/third_pc 配置の登録は別 task 起票要 (副医院長正本守護承認案件)。
config/settings.yaml:132:  #   は本 PR scope 外、副院長殿御差配仰ぐ正本守護承認案件として継続。
（→ pc_mapping と registry.pc の役割分離に言及するコメントは0件）

$ /usr/bin/grep -n "scope\|正本\|canon" shim/hakudokai/hakudokai_watchdog.sh
（→ 0件。scope 判定コード (L158-172) に説明コメント無し = 完全な空白地点）

$ /usr/bin/grep -n "正本\|canon\|scope" scripts/inbox_write.sh | head -20
11:# ★canon fail-closed gate (leg B, subtask_shadow_failclosed_legB_a2_20260805)★:
...(canon 関連コメント多数・既に濃い)
270:# INBOX_WRITE_DISPATCH_NOTICE_TARGET で上書き可・足軽4号 registry scope 欄実装後は
...

$ git status --short scripts/inbox_write.sh
 M scripts/inbox_write.sh
（→ ★現在進行形で未commit差分あり = a2/a5/a7 の作業対象と重なる衝突危険を実測で確認★）

$ date
Wed Aug  5 17:12:25 JST 2026
```

**結論 (母集団=既存調査)**: registry.pc / pc_mapping.agents[] の役割分離を説明するコメントは queue/pane_registry.yaml・config/settings*.yaml・shim/hakudokai/hakudokai_watchdog.sh の3ファイルいずれにも★0件★。scripts/inbox_write.sh 側は canon 関連コメントが既に濃く、かつ現在進行形で他工区が編集中 (`M`)。∴ 明文化は inbox_write.sh を避け、上記3ファイルへ置くのが安全 (§2 で確定)。

---

## §1 明文化2件 — 逐語案 (⑴ 何処へ・何と書くか)

### 1a. `queue/pane_registry.yaml` — 既存 `notes:` フィールド (L17-23) への追記案

現状 (L17-23、変更対象):
```yaml
  notes: 'ashigaru4 は欠番 (PC 境界の視覚的区切り、CLAUDE.md §18.1 番号体系の原則)。

    SecondPC entries は karo-second 主管領域。本 PC からの tmux 検証は不可ゆえ

    advisory のみ (= 4-way audit の対象は MainPC を主軸とし、SecondPC は記録参考)。

    '
```

追記する段落 (L21 と L23 の間、既存3段落構造を崩さず4段落目として挿入):
```
    panes[].pc field は shim/hakudokai/hakudokai_watchdog.sh の watcher scope 判定

    (embedded python `if p.get('pc') != pc_role: continue`) が読む scope 正本である。

    config/settings*.yaml の pc_mapping.agents[] (配送先 routing 正本) とは別の問いに

    答える別正本であり、どちらかを『導出物』として廃止・統合してはならない

    (2026-08-05 正本一本化設計 a4/karo-second 参照)。

    '
```

### 1b. `shim/hakudokai/hakudokai_watchdog.sh` — L158-159 直前へのコメント案

現状 (L157-160、python heredoc 内):
```python
import sys, yaml
path, pc_role = sys.argv[1], sys.argv[2]
```

挿入するコメント (`import sys, yaml` の直後・`path, pc_role = ...` の直前、Python `#`):
```python
# scope 正本 read site (2026-08-05 正本一本化設計 a4): 本関数が読む
# queue/pane_registry.yaml panes[].pc は「本 PC で watcher を張るべき対象か」を
# 判定する scope 正本。config/settings*.yaml の pc_mapping.agents[]
# (配送 routing 正本) とは別の問いに答える別正本 — 統合・代替禁。
```

### 2a. `config/settings.yaml` — `pc_mapping:` 直前コメントブロック (L100-109) への追記案

現状末尾 (L108-109、追記対象直前):
```yaml
#   fukuincho_pc を pc_mapping に新規追加。これで inbox_write.sh の cross-PC bridge
#   resolve が target=fukuincho を解決可能化、cross-PC INSERT skip 防止 (phantom 恒久根治)。
```
(この直後、`pc_mapping:` の直前に追記)

追記するコメント:
```yaml
# routing 正本 (2026-08-05 正本一本化設計 a4): 本 pc_mapping.agents[] は
# 配送先 PC 判定 (routing) の正本。watcher が「どの pane を監視すべきか」
# (scope) の判定には使われぬ — scope 正本は queue/pane_registry.yaml の
# panes[].pc (shim/hakudokai/hakudokai_watchdog.sh が読む)。両者は別正本、統合禁。
```

### 2b. `config/settings_local.yaml` — L3 直後への追記案

現状 (L3、追記対象直後):
```yaml
# inbox_write.sh の cross-PC bridge が参照する pc_mapping を SecondPC視点に切替
```

追記するコメント (L3 の直後・L5 `pc_mapping:` の直前):
```yaml
# 同上の役割分離 (2026-08-05 正本一本化設計 a4): 本 pc_mapping は routing 正本。
# scope 正本は queue/pane_registry.yaml panes[].pc (hakudokai_watchdog.sh 読)。
# 別正本、統合禁。
```

---

## §2 欄⑤ 触る path (本便が「もし実装されたら」触る対象・今回は不触=草案のみ)

| path | 変更種別 | 衝突リスク |
|---|---|---|
| `queue/pane_registry.yaml` | 追記のみ (notes: 1段落・ロジック不変) | 低 (git status clean 実測§0) |
| `shim/hakudokai/hakudokai_watchdog.sh` | 追記のみ (heredoc 内コメント4行・ロジック不変) | 低 (git status clean・§0 grep で説明コメント0件を確認済) |
| `config/settings.yaml` | 追記のみ (コメント4行・ロジック不変) | 低 (git status clean) |
| `config/settings_local.yaml` | 追記のみ (コメント3行・ロジック不変) | 低 (git status clean) |

**★明示的に不触★ = `scripts/inbox_write.sh`**: §0 実測で `M` (未commit差分あり) を確認済。a2 (canon fail-closed gate leg B)・a5 (intake_validator)・a7 (archive 読み手) が現に触っている対象と同一ファイルであり、本便の明文化はここへは置かない (前便§2で「隣接ドキュメント」の候補に挙げたが、衝突回避のため本便で確定除外)。将来 inbox_write.sh 側にも同旨コメントを置く場合は、a2/a5/a7 の patch 収束後・別工区として起票すべき。

---

## §3 条⑿ 己ならどう骨抜きにするか (⑵の回答・2種)

### (a) 書いてあるが読まれぬ 型

1. **`notes:` フィールドの埋没**: pane_registry.yaml の `notes:` は既に3段落 (欠番/SecondPC主管/advisory) あり、4段落目として追記すると「先頭だけ読んで離脱する」読み手には届かぬ。実測 (§0) で本フィールドは階層化されておらず単一文字列 — 読み手が「自分に関係する段落」を検索する動機を持たねば末尾は読み飛ばされる。
2. **heredoc 内コメントの見落とし**: hakudokai_watchdog.sh のコメントは bash script 内の python heredoc に置かれる。「shell 側だけ diff を見る」担当者 (grep で `.sh` 拡張子のみ検索、python 構文を意識せず読み飛ばす等) はここへ到達しない可能性がある。

### (b) 書いてあるが従われぬ 型

1. **緊急是正圧力下での特例扱い**: watcher 暴走等の是正時、「今だけ両方を1つに統合すれば早い」という判断が、明文化コメントの存在を知りつつも「今回は特例」として押し通される型。24時間ノンストップ稼働原則下では「立ち止まってコメントを読み従う」より「動かす」が優先されがちである。
2. **コメント自体の陳腐化 (comment rot)**: 将来 `hakudokai_watchdog.sh` や `inbox_write.sh` が改修され、`pc_mapping.agents[]` が scope 判定にも使われるよう変更された場合、コメントは「routing 正本」のまま古びて残る。読んだ者が「コメント通りだから統合しても安全」と誤信する — CLAUDE.md Index が指す docs/* 正本の大半が実在しなかった先例 ([[claudemd-index-phantom-canon-paths]] 型) と同型の欠陥。本便のコメントも「一度書いて終わり」ではなく、§3 (前便) の `canon_source_drift.sh` による継続検証と対で運用しない限り同じ穴に落ちる。

**∴ この2種は、明文化2件を実装する際にも消えぬ残存穴である。明文化それ自体は前便§5で述べた通り「次任が同じ誤りを踏む」ことへの緩和策に過ぎず、根治ではない。**

---

## §4 欄 六つ まとめ

| 欄 | 内容 |
|---|---|
| ①命令貼付 | §0 参照 (grep 4種+git status+date、出力そのまま貼付済) |
| ②解き方 | 前便訂正版の結論 (実装変更不要・明文化2件) を受け、対象file実物を読んで挿入位置を1行単位で確定 (§1)。inbox_write.shは§0実測(`M`)により意図的に除外 (§2)。 |
| ③約の検め | 本便に「約」「概ね」「〜台」等の丸め数値表現なし (該当ゼロにつき対照省略・条⑵準拠=丸め値を主張しておらぬため対照不要) |
| ④諾・手・時 | 諾=未 (karo-second/委員長の明示GO待ち・本便は合意材料の提出のみ)。手=実装者は下記§5参照。時=ETA=本便提出をもって完了 (起草作業自体は即時完了、実ファイル編集は別途GO後)。 |
| ⑤触る path | §2 表 参照 |
| ⑥誰が為すべきか | `queue/pane_registry.yaml`・`config/settings*.yaml` はコメントのみ・ロジック不変ゆえ家老(second)承認後は担当足軽(当職)が実行可。`shim/hakudokai/hakudokai_watchdog.sh` は watcher 起動に直結する shim/ 配下ゆえ、コメントのみとはいえ実行前に家老の明示GOを得るべき (実装権限の慎重側)。`scripts/inbox_write.sh` は§2の通り今回対象外、別工区として a2/a5/a7 収束後に起票。 |

---

## §5 完了規準 (self-check)

- [x] ⑴ 明文化2件の具体の文 (逐語案) — §1 に file/節/挿入位置つきで記載
- [x] ⑵ 条⑿ 自己適用 — §3 に2種 (読まれぬ/従われぬ) を記載
- [x] ⑶ 欄① — §0 に命令+出力のみで記載 (散文の範囲説明なし)
- [x] 縛り = 実装・commit 不履行 (git status で確認可・本便は起草のみ)
- [x] 触るpath欄 (⑤) — §2 に明記、inbox_write.sh を明示的に除外し理由を記載
- [x] 欄 六つ (①-⑥) — §4 表に集約
- [x] ETA を添えた (§4 ④)

---
report path: docs/incident_logs/2026-08-05_w_canon_documentation_draft_a4.md
