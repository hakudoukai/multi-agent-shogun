# W (次任) 正本一本化 方式案 — ★訂正版★ 足軽4号

**測時**: 2026-08-05T15:23:26+0900 (`date` 実行、本文冒頭に貼付済)
**下命 (本便の直接根拠)**: karo-second msg_20260805_152046_47d1783d (「貴殿の★訂正の方★が誤り・元の主張が正」)
**前便 (誤りを含む・保存のまま残す=消さぬ)**: `docs/incident_logs/2026-08-05_w_canon_source_unification_design_a4.md` (15:11-15:17)
**境**: 設計のみ・実装禁・commit禁・registry/inbox_write.sh/墓場file 不触(読むのみ)。

---

## §0 訂正の経緯 (何を誤り、何故誤ったか — 隠さず書く)

**誤った箇所**: 前便 §1 の scope 行=「`registry.pc` は型④死蔵 field (grep 0件)」。
**正しくは**: `registry.pc` は **`shim/hakudokai/hakudokai_watchdog.sh` L166 の embedded python が現に読んでおる生きた scope 判定源** である (karo-second 実測・本便で独立再確認済=§7)。

**何故誤ったか (真因)**: 前便 §7 の grep 母集団が `scripts/` 一本に狭まっており、`shim/` を含めておらなんだ。
```
前便 (誤):   grep -rn "..." scripts/                      → 0件
本便 (正):   grep -rn "..." scripts/ shim/                → shim/hakudokai/hakudokai_watchdog.sh:166 が hit
```
★★これが最も重い点★★= 当職は ★同日 14:52:45 の自分自身の先行調査★ (`docs/incident_logs/2026-08-05_registry_pcmapping_readsite_survey_a4.md` §1 表 #3・§1「⑴この調査が新たに開ける穴」節) で、**既に `hakudokai_watchdog.sh:158-174` を registry.pc の read site として明記し、かつ「pc_mapping を正本と早合点して registry.pc を廃止すれば watchdog の scope 判定が壊れる」と自分で警めておった**。
15:11 の後続設計 (方式案) を書く際、この14:52便の母集団 (`shim/` を含む) を引き継がず `scripts/` のみへ**無自覚に狭めて**しまい、自分の20分前の警めを自分で崩しかけた。

**教訓 (本工区限りでなく台帳へ)**: 関連工区の母集団は毎回 grep し直すのではなく、**先行便の母集団を明示的に引き継ぐ (または引き継がぬ理由を書く)** — 引き継がねば「同じ日の自分」同士でも矛盾し得る。

---

## §1 三問の「現状の正本」 実測 (訂正版)

| 問い | 委員長殿の逐語 | 実測した現状 |
|---|---|---|
| **identity** | registry | ✅ 一致 (前便から変更なし)。`_canon_lookup()` (`scripts/inbox_write.sh` L433-464) が `pane_registry.panes[].agent_id` のみを読む。 |
| **routing** | pc_mapping | ✅ 一致 (前便から変更なし)。`_cross_pc_bridge()` (`scripts/inbox_write.sh` L539-591) が `pc_mapping[<pc>].agents[]` を読む。 |
| **scope** | registry.pc | ✅ **一致 (訂正)**。`shim/hakudokai/hakudokai_watchdog.sh` L160-172 の embedded python が `pane_registry.yaml` の `panes[].pc` を `pc_role` (=起動時引数 `$PC_ROLE`) と突合し、一致する agent のみを「本 PC で watcher を張るべき対象」として抽出する (`if p.get('pc') != pc_role: continue`)。**唯一の scope read call site** (§7 で母集団=`scripts/`+`shim/` を再確認)。 |

**∴ 訂正の確定**: 委員長殿の逐語 (identity=registry / routing=pc_mapping / scope=registry.pc) は**三問とも実測と一致**しており、訂正すべきは前便の scope 行のみであった。「二正本が分裂しておる」という 14:52 便の§5結論も揺るがず — **配送 (pc_mapping) と 監視スコープ (registry.pc) は現に別々の file を読む、別々の生きた機構**である。

---

## §2 提案 (訂正) —— フォークは★解消★される (§48-b 順守はそのまま)

前便は「scope の正本をどちらにするか」でフォーク (案A/案B) を立てたが、**訂正後はフォークが不要になる**:

- **scope の正本は既に `registry.pc` である** (§1、生きた唯一の read site)。
- **routing の正本は既に `pc_mapping.agents[]` である** (前便から変更なし)。
- 両者は「PC帰属」という近縁の情報を扱ってはいるが、**異なる問い (誰に届けるか／誰をこの PC で監視するか) に、異なる機構が、異なる file から答えている**——これは §48-b が要求する「問い毎に正本を一つずつ」を**既に満たしている**状態であり、畳み込みでも重複実装でもない。

**∴ 実装変更は不要 (Anti-Duplication 順守)。必要なのは明文化のみ**:
1. `registry.pc` のコメント欄 (または隣接ドキュメント) に「本 field は `shim/hakudokai/hakudokai_watchdog.sh` の watcher scope 判定が読む scope の正本。**pc_mapping.agents[] とは別の問いに答える別の正本**であり、どちらかを『導出物』として廃止してはならぬ」と明記する (軽微追記・ロジック不変)。
2. `pc_mapping.agents[]` 側にも同様に「routing の正本。scope (watcher 対象範囲) の判定には使われぬ」と明記する。

**前便 案B (「pc_mapping を scope の事実上の正本と追認し registry.pc を非正本降格」) は★撤回★する**: 案B を実行すれば `hakudokai_watchdog.sh` の scope 判定が読む対象を失い、watcher 起動対象の決定が壊れる (14:52 便で当職自身が既に警めておった穴と同一)。

---

## §3 整合を保つ機構 (前便から変更なし・再掲のみ)

前便 §3 の `canon_source_drift.sh` (advisory・design only) 提案はそのまま有効。**むしろ訂正後の方が根拠が強まる**: scope=registry.pc / routing=pc_mapping.agents[] が「別々の生きた正本」と確定した以上、両者の**乖離検出**の必要性は前便より高い (前便は「片方が死蔵ゆえ乖離は意味を持たぬ」と誤解しかけていた)。検出項目3種・exit code・timeout・独立呼出契機の設計は前便のまま流用可 (再掲省略・前便 §3 参照)。

---

## §4 ⑼ 次に名簿が増えた時、また割れるのを止めるか (前便から変更なし)

★止めぬ★。前便 §4 の結論・案①②はそのまま有効 (再掲省略)。

---

## §5 この修正 (訂正) が新たに開ける穴は何か (条⑴・空欄不可)

1. **「フォーク解消」が思考停止に見えかねぬ**: §2 で「実装変更不要・明文化のみ」と結論したが、これは「何もしなくてよい」と読まれ得る。実際には**明文化そのものが未実装**であり、明文化を怠れば前便で当職が一度踏んだ誤り (母集団を狭めて型④と誤判定) を**次の担当者が再び踏む**。∴ 明文化 (§2 の2項目) を次任の必達事項として明記する。
2. **母集団継承の欠如という真因 (§0) が、本訂正便自身にも起こり得る**: 本便は `scripts/`+`shim/` を母集団としたが、**dashboard/fukuincho/third_pc 側の script は依然未検め** (前便 §0 の KNOWLEDGE_GAP をそのまま引き継ぐ — 訂正したのは scope 行のみで、未検め範囲は縮小しておらぬ)。
3. **「委員長殿の基準は3問とも実測と一致した」という訂正が、基準そのものへの再検証を止める理由にならぬ**: 一致したのは**現時点**の実装に対してのみであり、将来 `hakudokai_watchdog.sh` や `inbox_write.sh` が改修されれば再び乖離し得る。∴ §3 の drift script が「一度確認して終わり」ではなく継続監視である必要性を再強調する。

---

## §6 対になる他工区 (前便から変更なし・再掲)

前便 §6 参照。近縁: 足軽7号「`_archive/` 可読化案」、足軽3号「出口の門」。

---

## §7 己が実行した出力 (条⑾・本便の訂正根拠)

```
$ /usr/bin/grep -rln "pane_registry" --include="*.sh" --include="*.py" scripts/ shim/ tests/
scripts/agent_health_check.sh
scripts/alive_to_productive_monitor_v0_2_once.sh
scripts/inbox_write.sh
scripts/checks/pane_identity.sh
scripts/archive/message_delivery_v2_full_20260508/supervisor.sh
shim/hakudokai/hakudokai_watchdog.sh          ← ★前便で欠落しておった行★

$ /usr/bin/grep -rn "\.get('pc')\|\['pc'\]\|p\.get(\"pc\")\|panes\[.\]\.pc\b" scripts/ shim/
shim/hakudokai/hakudokai_watchdog.sh:166:        if p.get('pc') != pc_role:
(scripts/ 側は前便同様 0件のまま — 欠落は shim/ を含めておらなんだ事)

$ grep -n "pc_role\|p.get('pc')\|panes = \|for p in panes" shim/hakudokai/hakudokai_watchdog.sh
160:path, pc_role = sys.argv[1], sys.argv[2]
164:    panes = ((data or {}).get('pane_registry', {}) or {}).get('panes', []) or []
165:    for p in panes:
166:        if p.get('pc') != pc_role:

$ date
Wed Aug  5 15:23:26 JST 2026
```

---

## §9 条⑿ 自己適用 (★己の門を、己ならどう破るか★) — 本訂正版にも適用

前便 §9 の4件 (advisory は無視すれば通る／disable flag／既知例外リストへの紛れ込み／呼出契機未定のまま放置) はそのまま有効。**加えて本訂正固有の破り方**:

5. **★母集団を「都合よく」再度狭める★** — 本便は `shim/` を含めて訂正したが、次に別の担当者 (または当職自身) が同種の設計便を書く際、`shim/` を含め忘れれば**同じ誤りが再発**する。これを防ぐ機構は本便にも§3の drift script にも無い——**母集団の継承漏れそのものを検出する仕組みは未設計** (次任候補: 「関連工区の grep コマンド履歴を1箇所に集約し、新しい便は前便のコマンドを diff で確認してから母集団を確定する」運用ルール)。

---

## §8 完了規準 (self-check)

- [x] §0 訂正の経緯・真因 (母集団の欠落=shim/未検索) を明記
- [x] §1 三問とも実測一致 (訂正済み scope 行)
- [x] §2 フォーク解消・案B撤回を明記 (実装変更不要・明文化2件のみ必達)
- [x] §5 新たに開ける穴 3件 (空欄でない)
- [x] §7 己が実行した出力 (訂正の根拠となる grep 再実行・shim/ 含む)
- [x] §9 条⑿ 自己適用 (前便4件 + 本訂正固有1件)
- [x] 実装・commit・push・stage は行っておらぬ (設計文書のみ・git status で確認可)
- [x] 前便を削除・改変せず、独立ファイルとして保存 (系譜を消さぬ)

---
report path: docs/incident_logs/2026-08-05_w_canon_source_unification_design_a4_corrected.md
