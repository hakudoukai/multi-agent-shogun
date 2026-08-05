# registry vs pc_mapping — 現に読む物の呼出箇所全数調査 (足軽4号)

- 発令元: karo-second msg_20260805_144838_bffebc8c (14:48:38)
- 実施: 足軽4号 (ashigaru4)
- 測時: 2026-08-05 14:52:45+0900
- lane: delivery-route-stabilization (schema合意は karo-second 経由・実装は禁・設計のみ)

## §0 母集団宣言

```
/usr/bin/grep -rn "pane_registry" --include="*.sh" --include="*.py" --include="*.bats" .
/usr/bin/grep -rn "pc_mapping\|settings_local" --include="*.sh" --include="*.py" --include="*.bats" .
```
上記2コマンドの生出力を母集団とし、`queue/reports/**`(旧版アーカイブ)と`scripts/archive/**`(旧実装)を「非稼働系」として分離。以下は**現行稼働系のみ**を掲げる。手で列挙せず。

## §1 呼出箇所 一覧表 (現行稼働系のみ)

| # | file:line | 読む物 | 何を答えるか | 実行契機 |
|---|---|---|---|---|
| 1 | `scripts/inbox_write.sh:433-464` (`_canon_lookup`) | `queue/pane_registry.yaml` → `pane_registry.panes[].agent_id` | 「この agent_id は canon 識別子として在るか」(TARGET_OK/BAD) | **inbox_write.sh 全呼出で毎回** (第一段・fail-closed) |
| 2 | `scripts/inbox_write.sh:539-591` (`_cross_pc_bridge`) | `config/settings_local.yaml`(優先) → 無ければ `config/settings.yaml` の `pc_mapping.<pc>.agents[]` | 「この agent_id はどの PC が給仕するか」(LOCAL/BRIDGED/UNROUTABLE) | **canon gate 通過後 毎回** (第二段) |
| 3 | `shim/hakudokai/hakudokai_watchdog.sh:158-174` (`load_inbox_agents_from_registry`) | `queue/pane_registry.yaml` → `panes[]` の `pc:` フィールドで `$PC_ROLE` 一致filter | 「この PC 上で watcher を張るべき agent_id 一覧」 | watcher 起動時・registry 変更検知時 |
| 4 | `scripts/checks/pane_identity.sh:205-260` (source B) | `queue/pane_registry.yaml` → `panes[].{tmux_target,agent_id/persona,pc}` (`pc=="MainPC"` のみ抽出) | 4-source (tmux実態/registry/…) 突合の一枝 | `pane_identity.sh` 実行時 (定期監査) |
| 5 | `scripts/alive_to_productive_monitor_v0_2_once.sh:381` | `queue/pane_registry.yaml` (path のみ保持、後続で読込) | alive→productive 判定の入力の一つ | monitor 実行時 |
| 6 | `lib/cli_adapter.sh:1203-1212` (`get_mainpc_ashigaru_ids`) | `config/settings.yaml` → `pc_mapping.main_pc.agents[]` | 「MainPC 配置の ashigaru ID 一覧」(ホワイトリストfilter) | `shutsujin_departure.sh:71` 起動時 (呼出確認済) |

非稼働系 (参考・母集団に数えるが判定に含めず): `scripts/archive/message_delivery_v2_full_20260508/supervisor.sh` (将来対応の未実装コメント)、`queue/reports/**` (旧版 before-snapshot)、`shutsujin_departure_secondpc.sh:129/132` (persona召喚 prompt 文字列内の言及のみ・コードパース対象外)、`tests/**` (fixture/期待値であり本番読出しではない)。

## §2 二正本の重なりは「全面」ではなく「一点」

`queue/pane_registry.yaml` の `panes[]` は `agent_id` に加え **`pc:` フィールドを持つ** (実測: `pc: MainPC` 9件・`pc: SecondPC` 11件、`/usr/bin/grep -n "pc: MainPC\|pc: SecondPC" queue/pane_registry.yaml | wc -l` = 20)。これは意味論として `config/settings_local.yaml` / `config/settings.yaml` の `pc_mapping.<pc>.agents[]` と**同じ問い (この agent_id はどの PC か) に答えうる**——ここが唯一の重なり点である。

- **identity の問い** (「この agent_id は canon か」) — 答えるのは **registry のみ** (#1)。pc_mapping は一度も使われぬ。
- **routing の問い** (「どの PC へ届けるか、届けられるか」) — `_cross_pc_bridge` (#2) は **registry の `pc:` を一度も読まず**、別ファイル (`pc_mapping.agents[]`) を読む。
- **scope の問い** (「この PC で watcher を張るべき agent_id は」) — `hakudokai_watchdog.sh` (#3) は **registry の `pc:` を読む** (pc_mapping は読まぬ)。

∴ 「どちらが PC 帰属の正本か」という一点において、**現に読む機構は2つに割れている**: 配送 (#2) は pc_mapping を読み、監視スコープ (#3) は registry.pc を読む。これは委員長殿の基準 (「機構が現に読む物を正本とし、もう一方は導出物にするか廃止する」) の前提——単一の機構が単一の物を読む——が**この一点に限り成立しておらぬ**ことを意味する。

## §3 実測 (陽性対照 — 委員長殿裁定 msg_20260805_142223_c14c10d5 で既出の三名を独立再現)

```
$ .venv/bin/python3 -c "... registry agent_id vs settings_local.yaml pc_mapping 全agents 差集合 ..."
registry agent_id count: 20
settings_local.yaml pc_mapping total agents: 20
IN REGISTRY, NOT IN pc_mapping (settings_local): ['honda', 'sanada', 'takenaka']
IN pc_mapping (settings_local), NOT IN REGISTRY: ['commander', 'fukuincho', 'hideyoshi', 'ieyasu', 'kuro_desktop', 'nobunaga']
```
- `honda`/`sanada`/`takenaka` = registry にのみ在り pc_mapping に無い → `_cross_pc_bridge` は UNROUTABLE (dead_letter 行き、既知の欠陥)。
- `commander`/`fukuincho`/`kuro_desktop` = pc_mapping にのみ在る他PC/他役職の bridge 先登録 (registry の対象外・本PC pane ではない実体ゆえ一致せず正常)。
- `hideyoshi`/`ieyasu`/`nobunaga` = 旧 persona 名 (DD-157/162 で purge 対象・registry は新名 karo/gunshi/shogun のみ) → pc_mapping 側に旧名が残存している。

∴ 前段便が挙げた「六名」は本調査で **`registry-only 3 + pc_mapping-only 6 = 9名`** に実測される (前段の「⒝他PC三名」との数の異同は本調査からは判定不能・前段の内訳定義が不明ゆえ——第四値のまま残す。何が出れば動くか: 前段発話者 (家老second) の「⒝他PC三名」の具体名列挙)。

## §4 委員長殿の基準を code で当てた結論

基準: 「機構が現に読む物を正本とし、もう一方は導出物にするか廃止する」

1. **identity (agent_id の存在)** — 現に読む物 = **registry** (`pane_registry.panes[].agent_id`)。pc_mapping はこの問いに使われず。∴ registry が正本。
2. **routing (cross-PC 配送先)** — 現に読む物 = **pc_mapping** (`settings_local.yaml` 優先→`settings.yaml`)。registry の `pc:` は `_cross_pc_bridge` から一度も参照されず。∴ **配送に限れば pc_mapping が正本**。
3. **scope (自PC監視対象)** — 現に読む物 = **registry.pc**。pc_mapping はこの問いに使われず。∴ **監視スコープに限れば registry が正本**。

∴ 「どちらが正本か」を単一の答えに畳むことはできぬ——**問いごとに現に読む機構が違う**。一本化するなら「PC帰属」という一つのデータを2つの経路 (registry.pc / pc_mapping.agents[]) で保持している事実こそが二正本であり、委員長殿の基準を杓子定規に適用するなら:
- 配送 (#2) と監視スコープ (#3) の双方が「PC帰属」を読んでいる以上、**どちらか一方に統一** (例: `hakudokai_watchdog.sh` を pc_mapping 読みに変える、または `_cross_pc_bridge` を registry.pc 読みに変える) すべきだが、**現状はどちらも生きた稼働系** ∴ 廃止側を誤れば #2 か #3 のどちらかが機能停止する。

## §5 貴殿への回答 (直接の問いに対して)

> 「二正本の実測が六名に育ち申した」の該当箇所への直接回答:
> - **手続き上の正本 (agent_id 存在)** = registry — 揺るがず。
> - **内容完全性 (PC帰属)** = 分裂中。配送は pc_mapping、監視は registry.pc。**どちらか片方を「導出物」にする決定は本調査の範囲外** (設計のみが許可された lane ゆえ、実装/裁定はせぬ)。

## ⑴ この調査が新たに開ける穴は何か

本調査自体はコード変更を伴わぬため直接の新穴は無い。ただし**この報告を根拠に「pc_mapping が正本」と早合点して registry.pc を廃止すれば `hakudokai_watchdog.sh` の scope 判定 (#3) が壊れる** (pc_mapping は「どの PC が agent を給仕するか」の粒度であり、`hakudokai_watchdog.sh` が要求する「この PC の pane 一覧 + tmux_target」の情報は pc_mapping に存在せぬ — `tmux_target` は registry にしかない)。∴ 一本化するなら pc_mapping 側に tmux_target を足すか、registry を正本のまま残し pc_mapping を「registry から導出する集合演算のキャッシュ」に格下げるかの二択になる。

## ⑸ 総量 (己で述べず数えた)

- 稼働系呼出箇所: registry 5件 (#1,3,4,5 + `pc:`直接参照は#3,4の2件)、pc_mapping 2件 (#2,6)。
- 非稼働系 (参考除外): 4件。

## ⑹ 誰が止めれば止まるか

本調査 (設計のみ・read-only) は karo-second が次任を出さねば自然停止する。commit/実装判断は karo-second 経由 (schema合意は横で結ばず縦を通す、との前段指示に従う)。

## ⑼ 判定不能は判定不能のまま (何が出れば動くか)

§3 の「六名 vs 九名」の異同は、前段発話者の「⒝他PC三名」の内訳が本便に引用されておらぬため判定不能。動く条件 = 前段の具体名列挙。

---
report path: docs/incident_logs/2026-08-05_registry_pcmapping_readsite_survey_a4.md
