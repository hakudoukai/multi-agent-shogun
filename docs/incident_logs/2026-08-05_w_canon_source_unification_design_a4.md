# W (次任) 正本一本化 方式案 (設計のみ) — 足軽4号

**測時**: 2026-08-05T15:11:39+0900 (`date` 実行、本文冒頭に貼付済)
**下命**: karo-second msg_20260805_150752_76ec3836 (§48-b 準拠・「一つに畳まぬ」前提)
**境**: 設計のみ・実装禁・commit禁・registry/inbox_write.sh/墓場file 不触(読むのみ)・凍結下(新規W起票禁だが本件は既存下命の応答ゆえ該当せず)。

---

## §0 母集団宣言・除外・KNOWLEDGE_GAP

**読んだ実物** (以下すべて本便執筆時に自分で開いた。要旨のみの伝聞は使わず):
- `scripts/inbox_write.sh` L420-690 (`_canon_lookup` / `_cross_pc_bridge` 全文)
- `queue/pane_registry.yaml` 全文 (panes[] 25件・reserved_gaps・persona_aliases)
- `config/settings_local.yaml` (SecondPC 版・pc_mapping 全 entries)
- `config/settings.yaml` L110-136 (pc_mapping フォールバック版)
- `scripts/checks/pane_identity.sh` L1-80 (4-way audit の既存実装)
- `scripts/checks/inbox_alias_integrity.sh` L1-25 (advisory check のもう一つの先例)
- `tests/checks/test_pane_identity.bats` L1-14 (既存 drift test の粒度)

**呼出箇所全数** (`/usr/bin/grep -rln` 実測・伝聞ではない):
- `pane_registry.yaml` を読む script: `scripts/agent_health_check.sh` / `scripts/alive_to_productive_monitor_v0_2_once.sh` / `scripts/inbox_write.sh` / `scripts/checks/pane_identity.sh` / `scripts/archive/message_delivery_v2_full_20260508/supervisor.sh` (archive は稼働外と見て以下では除外)
- `pc_mapping` / `settings_local.yaml` を読む script: **`scripts/inbox_write.sh` の一本のみ**

**除外**: `scripts/archive/` 配下は非稼働ゆえ「現に読む物」の母集団から除外 (稼働中の読者のみを正本候補の判定材料とする)。

**KNOWLEDGE_GAP_WARNINGS**: dashboard/ダッシュボード生成側・fukuincho/third_pc 側の script は本 PC から読めぬため未検め。`scripts/agent_health_check.sh` / `scripts/alive_to_productive_monitor_v0_2_once.sh` の registry 読取箇所は grep 一致のみ確認・中身の読取意味論 (identity 判定に使うか単なる一覧表示か) までは深掘りしておらぬ (本工区は「畳み込み方式」の設計が主眼ゆえ・深掘りは次任候補として§6に記す)。

---

## §1 三問の「現状の正本」 実測 (委員長殿の逐語 = identity/routing/scope への一次回答)

| 問い | 委員長殿の逐語 | 実測した現状 |
|---|---|---|
| **identity** (この agent_id は canon か) | registry | ✅ 一致。`_canon_lookup()` (L433-464) が `pane_registry.yaml` の `pane_registry.panes[].agent_id` 集合のみを読み、TARGET_OK/BAD を返す。**唯一の read call site**。 |
| **routing** (どう届けるか= local/bridge/unroutable) | pc_mapping | ✅ 一致。`_cross_pc_bridge()` (L539-591) が `pc_mapping` を読み LOCAL/BRIDGED/UNROUTABLE を返す。 |
| **scope** (この agent_id はどの PC に属するか) | registry.pc | ❌ **不一致 (要訂正)**。`panes[].pc` field は registry 内に実在する (例: `ashigaru4` → `pc: SecondPC`, L144)。**然れど `/usr/bin/grep -rn "\.get\('pc'\)\|\['pc'\]"  scripts/` = 0件**。読む script が一本も無い。 |

**∴ 訂正一件**: 「scope=registry.pc」は**未確認の前提**であった。実測結果=「scope に相当する動作」を現に強制しておるのは `registry.pc` ではなく **`pc_mapping[<pc_name>].agents[]` の 集合分割そのもの** (`_cross_pc_bridge` L574 `if '$target' in local_agents: print('LOCAL')`)。→ **routing と scope は、現状 同じ file の同じ構造 (`pc_mapping`) に同居しており申す**。`registry.pc` は書かれてはおるが**型④ (在るが誰も使わぬ)** に該当する死蔵 field。

**判定不能ではなく訂正**: これは「判定不能」ではなく grep 0件という陽性対照つきの反証ゆえ、そのまま覆す (条=判定不能は何が出れば動くかを併記、の裏返し=**出た**ケース)。

---

## §2 提案 —— 三つの正本 (畳まぬ・§48-b 順守)

§48-b「一file への畳み込みは不可」は**厳守**する。以下、問い毎に正本を **1つずつ** 定める (routing/scope を同一 file に置くこと自体は「畳み込み」ではなく「同じ構造で扱うべき隣接した問い」と整理する — 理由は下記フォーク参照)。

### 2-1. identity の正本 = `queue/pane_registry.yaml` (`panes[].agent_id`)
現状維持。変更不要 (既に単一・唯一の read call site)。

### 2-2. routing の正本 = `pc_mapping` (`settings_local.yaml` 優先・`settings.yaml` fallback)
現状維持。**ただし副次的な二層構造を明記**: `_cross_pc_bridge` (L556-567) は `settings_local.yaml` が存在すればそれを採り、無ければ `settings.yaml` にフォールバックする。これは **git-ignored (PC 固有の override) + git-tracked (共有 default)** の意図的な二層であり (`git check-ignore -q config/settings_local.yaml` → exit 0 = ignored, 実測済)、routing 正本を「一本」と呼ぶ時は**この二層を一体として指す**ことを明文化する必要がある。二層の食い違い自体は本工区の範囲外 (§6 へ送る)。

### 2-3. scope の正本 —— **フォーク (裁定要)**、当職の推奨を添える

現状 2 案:

**案A (registry.pc を正式に scope 正本へ昇格・実装は別途)**
`_cross_pc_bridge` の `local_agents` 判定 (L574) を、`pc_mapping.agents[]` を直に読む代わりに `pane_registry.yaml` の `panes[].pc == 自PC` から**生成**する形へ変える。scope の書く場所は registry 一本になり、`pc_mapping.agents[]` は生成物 (導出物) に格下げ。
- 利点: scope の一次情報が「新しい agent を増やす時に人間が一度書く場所」に一本化される。
- 難点: **実装が要る** (本工区の境=設計のみ、を超える)。かつ `pc_mapping` には `is_local` / `supabase_bridge` / `pc_id` 等 routing 固有の属性も同居しており、「scope だけ抜き出して registry から生成」は routing の正本定義にも手を入れることになる (2-2 との結合)。

**案B (pc_mapping.agents[] を scope の事実上の正本と正式に追認・registry.pc は非正本明記に降格)** ★当職の推奨★
`registry.pc` を「参考表示 (advisory な人間可読ラベル)」と明文化し、**scope の正本は routing と同じ `pc_mapping[<pc>].agents[]`** と正式に定める。
- 利点: **実装変更ゼロ**。現に動いておる挙動をそのまま正本と呼ぶだけ (Anti-Duplication 順守=二重実装を増やさぬ)。案Aで懸念した「scope と routing が同じ file に同居」を、§48-b 違反ではなく「**一つの file が二つの問いに同時に答える設計** (file 単位ではなく **key 単位** で正本を分ける = `agents[]` が scope の正本・`is_local`/`supabase_bridge` が routing の正本、と読めば§48-bの『問い毎に定めよ』は破っておらぬ)」と整理し直す。
- 難点: `registry.pc` が生きた情報に見えて実は誰も読まぬ、という**型④の罠を放置**する (人間が誤って「ここを直せば伝わる」と思い込む余地が残る)。∴ 単なる「そのまま」ではなく、**registry.pc のコメント欄に「本 field は現在いかなる script からも読まれておらぬ (2026-08-05 grep実測)。scope の実効正本は config/settings_local.yaml pc_mapping[pc].agents[] を見よ」を明記**する軽微な追記 (ドキュメント変更のみ・ロジック不変) を条件とする。

**当職の裁定 (推奨のみ・執行は上位)**: **案B**。理由=①実装ゼロで今日の凍結・commit禁の境と両立する ②案Aは routing 正本 (2-2) の定義に踏み込み、フォークが二重に増える ③案Bの難点 (型④放置) は軽微追記で消せる。

---

## §3 整合を保つ機構 (三つが互いに矛盾したら誰が気付くか)

**現状**: 気付く機構は**存在せぬ**。 `_canon_lookup` は identity 単体、`_cross_pc_bridge` は routing/scope 単体を見るのみで、両者の**突合**はどこにも実装されておらぬ。既知の乖離実例 (takenaka/honda/sanada = registry にのみ在り pc_mapping のどの `agents[]` にも無い) は、**メッセージ送信が現に発生して UNROUTABLE を踏むまで誰にも見えぬ** (受動検出)。

### 提案: 新規 advisory script `scripts/checks/canon_source_drift.sh` (design only・未作成)

既存の 2 先例 (`pane_identity.sh` の 4-way audit、`inbox_alias_integrity.sh` の alias↔canonical 整合) と**同型のアーキテクチャパターン**を踏襲する (Anti-Duplication: 新しい枠組みを発明せず、既存パターンを追加適用):

| 項目 | 値 | 根拠 |
|---|---|---|
| 実行方式 | 単体 script、advisory (stderr 警告 + 非0 exit のみ、**絶対 block せぬ**) | CLAUDE.md §19.3 mandate / 両先例が同じ規約 |
| exit code | 0=整合 / 2=drift検出 / 1=予約 | `pane_identity.sh` と同じ体系を踏襲 (呼出側の分岐コストを増やさぬ) |
| 手動停止flag | `~/.openclaw/disable_canon_source_drift_hook` | 両先例が同じ命名慣習 |
| timeout | 5秒上限 (YAML 読取のみ・tmux 呼出なし) | `inbox_alias_integrity.sh` が「小さい想定」で 5秒としており、本 check も tmux 不要ゆえ同等以下で足りる |
| 検出項目 (3種) | ⑴ registry にのみ在り pc_mapping の**どの** `agents[]` にも無い名 (=UNROUTABLE 予備軍) / ⑵ pc_mapping の `agents[]` にのみ在り registry に無い名 (=`_canon_lookup` が TARGET_BAD で弾く死んだ routing entry) / ⑶ **既知の例外リスト** (takenaka/honda/sanada 等) に載っておらぬ新規乖離のみを警告 (=許容済み乖離を毎回re-警告してノイズにせぬ) | ⑴⑵は L455 (`canon = {p.get('agent_id') ...}`) と L570-591 (`local_agents`/`agents` 集合) を突合するのみ、両方とも YAML 読取済のデータ構造の集合演算で実装可能 |
| 呼出タイミング (提案) | `pane_identity.sh` と**同一 hook には載せぬ** (下記理由) | — |

**同一hookに載せぬ理由**: `pane_identity.sh` は「tmux 操作前の事前チェック」= pane の**生死・実態**を見る (5秒予算の大半が tmux subprocess 呼出に割かれる設計、L34-37)。一方 `canon_source_drift.sh` は **静的 YAML の集合演算のみ**で tmux 呼出が要らぬ。両者を同居させると、tmux が重い時に軽い static check まで巻き込まれて誤って skip され得るし、逆に static drift の警告が tmux liveness の警告に埋もれて見落とされ得る。∴ **独立 script として新設し、独立の呼出契機 (registry / settings_local.yaml への書込後、または定期実行) を持たせる**ことを提案する (呼出契機の具体案=commit前hookか定期実行かは実装フェーズで裁定要・本設計では両論併記のみに留める=判定不能)。

**誰が止めれば止まるか (条⑹)**: 本 script は**止める機構ではない (advisory)**。止める権限は人間 (karo-second/委員長殿) にあり、本 script は「止めるべきか判断する材料 (drift 検出結果)」を出すのみ。停止できる唯一の主体=**手動 disable flag を置いた人間**。

---

## §4 ⑼ 次に名簿が増えた時、また割れるのを止めるか

**★止めぬ★。正直に書く。**

本設計 (§2 の三正本明文化 + §3 の advisory drift script) は、**乖離を「静かに」から「見える」に変えるのみ**であり、**乖離が生まれること自体は防がぬ**。新しい agent_id を registry にだけ足して pc_mapping を更新し忘れる、という操作は今後も物理的に可能なまま残る。advisory script は**書いた後に気付ける**が、**書く前に止める**機構ではない。

止めるには (実装は別途・本設計の範囲外として明記):
- 案①: registry への新規 pane 追加を単一の helper script 経由に強制し、その helper が pc_mapping への追記を同時に強制する (write-time 強制)。
- 案②: commit 前 hook で `canon_source_drift.sh` を **advisory ではなく gate** として使う (但し CLAUDE.md §19.3 mandate「絶対 block 禁止」の advisory 原則と衝突するため、gate 化には別途 policy 裁定が要る)。

**∴ 本工区の成果は「止血 (見える化)」であって「根治 (発生防止)」ではない。** 根治は次任候補 (§6)。

---

## §5 この修正が新たに開ける穴は何か (条⑴・空欄不可)

1. **既知例外リストが 第四の正本 になり得る**: §3 の検出項目⑶ (takenaka/honda/sanada を許容済みとして黙らせるリスト) を script 内にハードコードすれば、それ自体が「registry でも pc_mapping でもない、乖離の正本」という**新種の型①/②複合**を生む。∴ 実装時は**この例外リストの件数を毎回 stderr に出力し、増加したら (減少ではなく増加を) 別途警告する**ことを設計要件に加える (増加=新しい乖離が『許容』の名で隠されてゆく兆候)。
2. **§2案B の「registry.pc は非正本」明記が、逆に registry.pc を書く動機を失わせる**: 人間可読ラベルとしての価値 (「このagent_idはどのPCの物か一目でわかる」) は残るため、コメントで明確に位置づけないと**放置され陳腐化した嘘の情報**に転じ得る (型①へ退化)。∴ 明記コメントには「最終更新は手動・実効性なし・drift script の対象外」の三点を必須で含める。
3. **本設計自体が「三問」以外の第四の問いを見落としている可能性**: 本便は committee chief の逐語 (identity/routing/scope) をそのまま母集団としたが、`pc_mapping` には `is_local` / `supabase_bridge` という**routing 内のサブ区分**が別途あり、これを「routing」に一括りにした判断自体、次に細分化を要求される火種になり得る (§6 送り)。

---

## §6 対になる他工区

**探した範囲**: 本便執筆時点 (2026-08-05T15:1x) の `queue/inbox/ashigaru4.yaml` 既読分。直接の対になる新規下命は見当たらず。

**近縁 (性質が同型)**:
- 足軽7号「`_archive/` を読める形にする案 (設計のみ)」— 「保存されておるのに読めぬ (型③)」を「②へ引き上げる」工区であり、本工区「気付く機構が無い (型①/④混合) を advisory 検出 (型②寄り) へ引き上げる」と**同じ梯子の段の話**。
- 足軽3号「出口の門 設計」— 本工区の drift script も一種の「門 (通す/通さぬ)」だが**advisory ゆえ何も遮らぬ**点が異なる。境界線が要る際は突合を推奨。

**無し領域**: registry.pc の実装変更 (§2案A の実装フェーズ) / drift script の実コード化 — いずれも本便では未着手・次任候補。

---

## §7 己が実行した出力 (条⑾・抜粋)

```
$ /usr/bin/grep -rln "pane_registry" --include="*.sh" --include="*.py" scripts/ tests/
scripts/agent_health_check.sh
scripts/alive_to_productive_monitor_v0_2_once.sh
scripts/inbox_write.sh
scripts/checks/pane_identity.sh
scripts/archive/message_delivery_v2_full_20260508/supervisor.sh

$ /usr/bin/grep -rln "pc_mapping\|settings_local.yaml" --include="*.sh" --include="*.py" scripts/
scripts/inbox_write.sh

$ /usr/bin/grep -rn "\.get('pc')\|\['pc'\]\|p\.get(\"pc\")\|panes\[.\]\.pc\b" scripts/
(0件・出力なし)

$ git check-ignore -q config/settings_local.yaml; echo "exit=$?"
exit=0

$ git show HEAD:scripts/inbox_write.sh | grep -c "BRIDGED\|UNROUTABLE"
9
```

---

## §9 追補 —— 条⑿ 自己適用 (★己の門を、己ならどう破るか★)

**出所**: karo-second msg_20260805_151539_ecd91458 (条⑿ 発行・全員宛)。
**時刻の並び (条=差し戻し先行則の準用)**: 条⑿ 発行 = 15:15:39。本設計の inbox 提出 = 15:15:48 (9秒後)。
∴ **交差ではなく、当職が未読のまま先に提出した単純な後追い**と認める (交差=双方が同時に書いていた場合の語ゆえ、9秒の差は「読めば防げた」に近い)。∴ 本節は §3 の提案 (`canon_source_drift.sh`) に対する**追記**であり、当初稿からの訂正ではなく後出しの補完として扱う。

**§3 の門 (`canon_source_drift.sh`・design only) を、当職ならどう破るか**:

1. **★advisory ゆえ、警告を無視すれば通る★** — 本 script は non-zero exit を返すのみで何も block せぬ (§3 で自ら明記済)。∴ 最も単純な破り方=**「警告を読んで、そのまま commit する」**。技術的迂回ですらない。§4 の「止めぬ」はこの①の言い換えでもある。
2. **★disable flag を立てて忘れる★** — `~/.openclaw/disable_canon_source_drift_hook` を一度置けば、以後の全 drift が恒久的に沈黙する。`pane_identity.sh`/`inbox_alias_integrity.sh` も同じ flag 機構ゆえ**同じ弱点を継承**しておる (先例と同型にした事の副作用)。
3. **★既知例外リストへ 新しい乖離を紛れ込ませる★** — §5-1 で既に指摘した「例外リストが第四の正本になり得る」と同一の穴。当職が悪意を持てば、新しい未承認の乖離を「既知」として先に登録しておけば、drift script は**それを健全と報告する**。
4. **★最も危うい破り方 = どこからも呼ばれぬまま放置する★** — 本設計は script の**存在**を提案したのみで、呼出契機 (commit前hook/定期実行) は「両論併記のみ・裁定要」と§3で明記済。∴ 実装されても**一度も呼ばれねば** `pane_registry.yaml`/`_archive/`/`document_hash` と同じ**型④ (在るが誰も使わぬ)** に落ちる。★これが本日一日 隊が繰り返し数えた病そのものであり、当職の提案が同じ轍を踏む危険が最も高い★。

**★何日経てば健全と言えるか (足軽3号の追加条・自己適用)★**: 「設計した」「実装した」だけでは健全と呼ばぬ。健全と呼べる最小条件を先に書く=
① script が実在する ② **少なくとも1箇所の実呼出元 (hook/cron/手動運用手順書) が存在する** ③ **実行ログに最低1回の実測結果 (mismatch=0 または >0) が残っておる**。①のみで「健全」と書けば、それは型④の再生産に他ならぬ。②③が揃うまでは「未健全・呼出未定」と明記し続ける義務を、実装を担う次任へ申し送る。

---

## §8 完了規準 (self-check)

- [x] §0 除外宣言・母集団宣言 (find/grep条件そのまま)
- [x] identity/routing/scope 各1正本の明示 (scope はフォーク明示+推奨案)
- [x] 整合を保つ機構の設計 (新規 advisory script・既存2先例と同型・block せぬ)
- [x] ⑼ 将来また割れるかに正直に回答 (止めぬ、と明記)
- [x] §5 新たに開ける穴 3件 (空欄でない)
- [x] §6 対になる他工区 (該当なしの理由つき)
- [x] §7 己が実行した出力
- [x] §9 条⑿ 自己適用 (己の提案した門の破り方4件・最も危うい物を明示・健全の最小条件3点)
- [x] 実装・commit・push・stage は行っておらぬ (設計文書のみ・git status で確認可)
