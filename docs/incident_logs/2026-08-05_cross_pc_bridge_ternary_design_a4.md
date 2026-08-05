# `_cross_pc_bridge` 戻り値 三値化 — 設計案 (実装前・足軽4号)

下命: 家老second msg_20260805_142223_c14c10d5 (14:22:23)。【次任】として指示された三値化の
★設計のみ★ (実装は schema 合意の後)。前段 (第0段=六名分類、第一段=`scope_gate_design`) を
受けて、下記の残置事項に答える:
①事態A/Bを名指す戻り値と呼び手(caller)の分岐 ②受入条件⑴・⑼ ③registry と pc_mapping の
どちらが正本か ④対に成る他工区。

★本 file は設計案のみ。`scripts/inbox_write.sh` / `queue/pane_registry.yaml` は★未変更(読むのみ)★。★

## §0 検めた範囲・断面

- `scripts/inbox_write.sh` 全文 (672行)。特に `_canon_lookup` (L419-462)・`_cross_pc_bridge`
  (L528-642)・呼び手 (L576-641 は関数内、L643-657 は呼出site)。
- `queue/pane_registry.yaml` 全文 (`panes[]` 20件 + `reserved_gaps[]` 1件を分離実測)。
- `config/settings_local.yaml` 全文 (`pc_mapping` 5エントリ)。
- 前段成果物 `docs/incident_logs/2026-08-05_scope_gate_design_karo_scope_field_a4.md`
  (§4 で三値化の初提案を既に行っており、本 file はその続篇・詳細化)。
- ★断面 (己で実測・2026-08-05T読了時)★:
  `base_commit=502cbfeed4ef0e6bd7f99b97838152f8a5e9c0c2`(HEAD)、
  ★作業樹は未commit変更あり★ (`git status --short` = `M scripts/inbox_write.sh` / `M queue/pane_registry.yaml`)。
  ∴ 本設計は★working tree の現物★を典拠とする (HEAD ではない — 差分は末尾の再測手順で己の目で確認されたし)。
  `sha256sum`: `scripts/inbox_write.sh`=`ad5738a4…7ff98` (672行) /
  `queue/pane_registry.yaml`=`20886275…52f184d` / `config/settings_local.yaml`=`2043516e…d028185…9ed25efb3bd7e069`
  (再測は読む者が己で `sha256sum <path>` を打つこと — 渡された値は読了の証にならぬ)。
- ★credential 探索・Supabase 実配送検証は本工区の縛り外★ (前段と同じ理由・権限分類機が正当に拒否)。

## §1 三値化の名前と戻り値の形

現状 (`_cross_pc_bridge` 内の埋込 python、L536-574) は 3つの出口が★2種類の記号★しか使わぬ:

| 出口 | 行 | 現在の出力 | 事態 |
|---|---|---|---|
| target が本PC `local_agents` に在り | L561-563 | `''` (空文字) | **A: 真にローカル (正当)** |
| target が或る remote pc の `agents[]` に在り、かつ `supabase_bridge: true` | L564-570 | `'local_pc\|target_pc'` | **C: bridge 成立 (正当・現状動作を維持)** |
| target がどの pc の `agents[]` にも見当たらぬ、または見当たっても `supabase_bridge` が真でない | L571 | `''` (空文字) | **B: canon だが bridge 先が無い (欠陥)** |
| `pc_mapping` 読込自体が例外 (壊れた YAML 等) | L572-573 (`except`) | `''` (空文字) | **(付随) 設定読込不能** |

★事態A と 事態B が 同じ `''` に潰れておる★ (前段 §2 で確定済)。加えて例外分岐も同じ `''` に潰れる
(前段では未言及だった残り — 本工区で追加確認)。

### 提案する三値 (要求どおり LOCAL / BRIDGED / UNROUTABLE の名を用いる)

| 値 | 出す事態 | 意味 |
|---|---|---|
| `LOCAL` | A | 本当にローカル。現状通りローカル書込へ委ねる。 |
| `BRIDGED\|<local_pc>\|<target_pc>` | C | 現状の `'local_pc\|target_pc'` に `BRIDGED\|` を前置。将来 pc_id が偶然 `LOCAL`/`UNROUTABLE`
  と衝突する事故を型で防ぐ (防御的タグ付け — 今日そのpc_id衝突は無いが、タグ無しの素の文字列比較は
  「名で索く」危うさを持つ、と前段以前に何度も出た型)。 |
| `UNROUTABLE` | B ★かつ★ 例外分岐 | ローカル書込を★止める★。理由は §3 (⑼への回答) で述べる — 例外もBに合流させたのは
  意図的な設計判断であり、異論を残す (§4-補)。 |

## §2 呼び手 (caller) の分岐 — 現状 (L576-657) と 提案差分

### 現状

```bash
# L576-578
    if [ -z "$bridge_info" ]; then
        return 0  # Local agent, no bridge needed
    fi
# L581-582
    local_pc="${bridge_info%%|*}"
    target_pc="${bridge_info##*|}"
    ...(payload生成→curl POST、L603-641)...
        return 70   # L638: 成功
    ...
    return 71       # L641: bridge INSERT失敗

# 呼出 site L646-657
    _cross_pc_bridge "$TARGET" "$CONTENT" "$TYPE" "$FROM"
    _BRIDGE_RC=$?
    if [ "$_BRIDGE_RC" -eq 70 ]; then exit 0; fi   # 送達済、local dead-letter を作らぬ
    if [ "$_BRIDGE_RC" -eq 71 ]; then exit 71; fi  # fail-closed、local へ落とさぬ
```

★問題の核心★: `bridge_info` が `''` である限り、事態A(正当)も事態B(欠陥)も同じ「何もせず
`return 0` (関数の暗黙終端)」を通り、呼出元は `_BRIDGE_RC` が 70/71 いずれでもないため
そのまま `_write_message` (ローカル書込) へ進む。事態Bの便は★誰にも読まれぬローカル file★
に落ちる (前段実測=takenaka/honda/sanada 宛がこの経路)。

### 提案

```bash
# 関数内、L576-582 相当を置換
    case "$bridge_info" in
      LOCAL)
        return 0                 # 事態A: 現状と同じ、正しい経路
        ;;
      UNROUTABLE)
        # 事態B (+ 設定読込不能): ローカル書込を止める。
        # _canon_lookup の TARGET_BAD 経路 (L467-505) と★同型★に揃える=
        # dead_letter 記録 + _notify_pc_dispatcher_of_unroutable 呼出し。
        set +e
        _DL_PATH="$(_write_dead_letter "$target" "$content" "$msg_type" "$from" "cross_pc_bridge_unroutable")"
        _notify_pc_dispatcher_of_unroutable "$_DL_PATH" "$target" "$from" "cross_pc_bridge_unroutable"
        set -e
        echo "[inbox_write] UNROUTABLE: target=$target is canon but has no configured bridge destination (pc_mapping) — not silently written to local inbox" >&2
        return 71                # 既存の 71 (fail-closed) を再利用。新規 exit code を増やさぬ。
        ;;
      BRIDGED\|*)
        local_pc="$(echo "$bridge_info" | cut -d'|' -f2)"
        target_pc="$(echo "$bridge_info" | cut -d'|' -f3)"
        ...(既存の payload生成→curl POST は無変更)...
        ;;
      *)
        # 想わなんだ第四の文字列 (契約違反=埋込pythonの出力形がここで想定する
        # 3値のどれとも一致せぬ)。「無視してローカル書込」より安全な側=
        # UNROUTABLE と同じ扱いへ倒す (fail-closed)。
        echo "[inbox_write] WARN: _cross_pc_bridge produced unexpected value '$bridge_info' — treated as UNROUTABLE (fail-closed)" >&2
        return 71
        ;;
    esac
```

呼出 site (L646-657) 自体は★無変更でよい★ — 70/71 の意味契約は保たれる。ただし L643-645 の
コメント「If insert fails, fail closed instead of silently creating an unread local queue」を
「If insert fails **or the target is UNROUTABLE**, fail closed …」へ拡張要 (戻り値の意味範囲を
拡げた本人が、同じ turn でその意味を検める者向けの注釈も書き換える — 本日の規律
「様式を改めた者は検める機構の持ち主へ同じ turn で告げよ」の自己適用)。

## §3 受入条件への回答

### ⑴ 横に開く穴 (この修正が新たに開ける穴)

1. ★canon gate との射程の食い違いが残る★: `_cross_pc_bridge` は `_canon_lookup` (fail-closed
   canon gate, L419-462) を★通過した TARGET にしか到達せぬ★。今回 `queue/pane_registry.yaml`
   (`panes[]`) を実測した所、`commander` / `fukuincho` / `kuro_desktop` は `pc_mapping` には
   bridge 設定が★実在する★ (config/settings_local.yaml L20-38) にも関わらず、
   `pane_registry.panes[].agent_id` には★一件も存在せぬ★ (実測=20件中0件)。∴ これらの宛先は
   本三値化が効く前の `_canon_lookup` で `TARGET_BAD` として先に落ち、UNROUTABLE 分岐には
   ★到達し得ぬ★。「三値化で欠陥が直った」と誤って一般化すれば、この★別の門で落ちておる便★を
   見落とす穴になる。∴ 本設計は★『pane_registry に在る名の bridge 欠落』にのみ効く★と
   射程を明記する。commander/fukuincho/kuro_desktop 側の扱いは §4 の一本化に委ねる。
2. ★exit code の情報量低下★: 「bridge先が構造的に無い (設定に登場せぬ)」場合と、
   「bridge先はあるが curl 通信が失敗した (一時的障害)」場合を★どちらも 71★ に統合する。
   前者は再送しても直らぬ (設定を直すまで恒久)、後者は再送で直る可能性がある (一時的)。
   同じ exit code に潰すと、呼出元やログ解析でこの区別が付かなくなる★新しい穴★。
   → 緩和策: stderr メッセージの prefix を分ける (`UNROUTABLE:` vs 既存の
   `WARN: cross-PC bridge INSERT failed` のまま) — exit code は共有するが、ログ上の文字列で
   切り分け可能にする (上記コード案は既にこの形で書いた)。
3. ★bash `case` 文パターンの実装ミス危険★: `BRIDGED\|*)` のような `case` パターンでの
   `|` (OR区切り文字) と、値そのものに含む `|` (BRIDGED の区切り文字) の衝突は、
   実装時にエスケープを誤ると★静かに全マッチしない/意図せぬパターンに誤マッチする★
   危険がある。実装段階で★負テスト必須★(例: `bridge_info="BRIDGED|main_pc|second_pc"` を
   与えて `BRIDGED\|*)` 枝が正しく拾うか、`bridge_info="UNROUTABLEX"` のような近似文字列を
   与えて誤って BRIDGED/LOCAL 枝に落ちぬか)。
4. ★例外分岐の合流そのものが新しい穴★ (§3⑼で詳述)。

### ⑼ 時を経てまた開く穴 (同じ穴が再発するか)

★直接の穴 (事態A/Bを同じ空文字で潰す) は型として塞がる★ — 呼出元が文字列を `case` で
明示的に分岐する限り、新しい `pc_mapping` エントリを追加するだけでは事態A/Bの混同は再発しない
(戻り値そのものが自己記述的になるため)。

★然れど『同じ穴』を広く「二つの異なる意味を一つの記号に潰す」型と捉えれば、再発経路が
最低二つ残る★:

1. ★例外分岐の合流★ (本設計の§1で `UNROUTABLE` に含めた `except Exception` 分岐)=
   「pc_mapping 設定が構造的に無い (B)」と「pc_mapping 設定ファイルが壊れて読めぬ (例外)」を
   ★また同じ記号 (UNROUTABLE) に潰しており申す★ — これは本設計が★自ら開けた、同型の穴★に
   御座る。このファイル自身に前例がある = `_canon_lookup` の registry 読込不能は
   `DETECTOR_UNAVAILABLE` として★別ラベルで fail-closed★ (L459-462)。同じ流儀を
   `_cross_pc_bridge` にも適用するなら、例外分岐は `UNROUTABLE` ではなく
   `BRIDGE_DETECTOR_UNAVAILABLE` 等の★第四の値★にすべき、という異論が立つ。
   ★本設計は安全側 (どちらもローカル書込を止める) を優先して敢えて合流させたが、
   原因切り分けの観点では分けるべきという反論を明記し、次段の合意事項として残す★。
2. ★二正本 (pane_registry / pc_mapping) の追加漏れそのものは、三値化では止まらぬ★=
   本工区が三値化で直すのは「`_cross_pc_bridge` 内部で情報が潰れる」経路のみであり、
   「新しい agent を pane_registry と pc_mapping の★片方にだけ★追加する」事故
   (今回実測した takenaka/honda/sanada 〈registry のみ〉、commander/fukuincho/kuro_desktop
   〈pc_mapping のみ〉が現に六件とも実例) は★別の門 (§4 の一本化)★でしか止まらぬ。
   ★∴ 三値化だけを実装して「直った」と report すれば、この上流の型は★また開き申す★
   (次に誰かが agent を一方の file にだけ足せば、また同じ形の便が死蔵される)。

★結論: 本設計は『提示された穴 (事態A/B の空文字混同)』は塞ぐが、★同型の穴が二か所
(例外分岐/二正本) 未対応のまま残る★。「これで再発は止まった」とは書かぬ。

## §4 registry と pc_mapping — どちらが正本か

**現状 (今のコード構造上の事実として)**: `pane_registry.yaml` が★手続き上の上位★に御座る。
理由= `inbox_write.sh` の全呼出しは、まず `_canon_lookup` (L419-462、コード自身のコメント
L415-417 が「canon 宛先集合 = registry」と明記) を通り、そこを★通らねば `_cross_pc_bridge`
にすら到達せぬ★ (fail-closed gate、L459-506)。∴ 構造的に `pane_registry` が先に評価される
門番であり、`pc_mapping` はその門を通過した後にのみ参照される★下流の経路情報★。

**然れど実測 (前段 + 本工区)**: 両者は★一致しておらぬ★ (二つの独立した不完全登録簿) —

| 方向 | 実例 | 件数 |
|---|---|---|
| pane_registry に在るが pc_mapping に不在 | takenaka / honda / sanada (前段実測) | 3件 |
| pc_mapping に在るが pane_registry に不在 | commander / fukuincho / kuro_desktop (本工区実測) | 3件 |

∴ 「どちらが上か」は★手続き上は registry★、★内容の完全性ではどちらも片翼★。

**将来 (一本化案、前段§4を維持)**: `pane_registry.yaml` の `pc:` 欄を正本とし、
`pc_mapping.agents[]` は★そこから生成・検算する側に回す★。理由は上記の手続き上の上位性が
既にそうなっている事実に沿うため (新しい上下関係を作るのではなく、既存の門番の役割を
追認する形)。★一本化の実装方式 (自動生成の仕組み・commander等の欠落分の扱い) は
当職単独で決めず、対の三工区との合意事項とする★ (前段からの継続)。

## §5 対に成る他工区

家老second 指定 (msg_20260805_142223_c14c10d5 逐語) =
- 足軽2号 = ⒝失敗報の門 (★停止中・足軽3号の禁則と衝突★)
- 足軽3号 = 出口の門 設計 (★同上★)
- 足軽7号 = archive 可読化 (⒞裁定済)
- 足軽5号 = intake_validator

★schema 合意は 四名で直に行わず、家老second を通す★ (下命に明記済・当職はこれに従う)。

## §6 未検めの残り (次段)

- Supabase 実配送 (`pc_handshake` INSERT) の成否は live 検証していない (前段と同じ理由=
  credential 探索の要る範囲、権限分類機が正当に拒否)。
- `_write_dead_letter` / `_notify_pc_dispatcher_of_unroutable` の呼出し引数の実シグネチャは
  本工区で読了済 (L491-502 の既存呼出しをそのまま模倣) だが、§2 の擬似コードは★未テスト★。
  実装段階で負テスト必須 (§3⑴-3 参照)。
- §4 の一本化そのもの (registry → pc_mapping 生成の具体的手段) は未設計。次段の合意事項。

## §7 己が直した誤り (必須欄)

- 前段 `scope_gate_design_karo_scope_field_a4.md` §4 では三値化の三値を挙げたが、
  ★埋込 python の `except Exception` 分岐 (L572-573) が同じく `''` に潰れる事★を
  見落としていた (前段は L440-441 相当の1箇所のみを指摘)。本工区で全出口を再列挙し、
  §1 の表で③番目に追加、§3⑼で「本設計自身が開ける新しい穴」として明記した。

---
**報告**: 家老second。実装は本設計の合意 (家老second 経由・対の三工区とのschema合意) 後に着手する。
