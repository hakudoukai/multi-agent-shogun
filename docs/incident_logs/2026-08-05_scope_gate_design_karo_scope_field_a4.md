# registry scope欄 (lane=delivery-route-stabilization・第三) — 設計案 (実装前・足軽4号)

下命: 家老second msg_20260805_140553_b669efde (14:05:53)。第0段(六名分類・完了・別便で提出済)に続く本体。
★本ファイルは設計案のみ。registry / inbox_write.sh は★未変更(読むのみ)★。理由は §3 参照。★

## §0 検めた範囲

`scripts/inbox_write.sh` の canon check (`_canon_lookup`, L300-324) と cross-PC bridge (`_cross_pc_bridge`, L394-497) の
実コードを行番号つきで読了。`queue/pane_registry.yaml` 全文・`config/settings.yaml`・`config/settings_local.yaml` の
`pc_mapping` を実測突合。★Supabase 認証情報の探索・sb_curl 等の直接呼び出しは 権限分類機が★credential探索★として拒否
(正当な安全弁に御座る・ここで止め、迂回はせぬ)★ ∴ ★pc_handshake bridge の★実配送成否(live)は未検証★。

## §1 発見 — 「二つの名簿」がすでに存在し、しかも 食い違うておる

★委員長殿の下命は「registry に scope欄を新設せよ」であったが、実測の結果、★scope に相当する情報は既に別の場所に
存在しており、しかも registry と 一致しておらぬ★★ ことが判明いたした。

| 情報 | 出所 | 用途 |
|---|---|---|
| canon か否か (存在チェック) | `pane_registry.yaml` の `panes[].agent_id` (flat set・PC区別なし) | `_canon_lookup` (L300-317)。★どの PC かは一切見ぬ★ |
| どの PC が給仕するか (実際の配送判断) | `config/settings_local.yaml` (本 PC 優先) の `pc_mapping.<pc>.agents[]` | `_cross_pc_bridge` (L394-434)。★これが実質「scope」そのもの★ |

★実測差分(第0段で検めた六名で突合)★:

| 名 | pane_registry canon? | settings_local.yaml pc_mapping に出現? | 出現先 |
|---|---|---|---|
| shogun | ○ (pc: MainPC) | **○** | `main_pc.agents` (supabase_bridge=True) |
| karo | ○ (pc: MainPC) | **○** | `main_pc.agents` (supabase_bridge=True) |
| gunshi | ○ (pc: MainPC) | **○** | `main_pc.agents` (supabase_bridge=True) |
| takenaka | ○ (pc: MainPC・alias 有) | **✗ 皆無** | (settings.yaml にも settings_local.yaml にも 一切登場せぬ) |
| honda | ○ (pc: MainPC・alias 有) | **✗ 皆無** | 同上 |
| sanada | ○ (pc: MainPC・alias 有) | **✗ 皆無** | 同上 |

★∴ 家老second の note根拠 (⒝=shogun/karo/gunshi・⒜=takenaka/honda/sanada) は、★note の文言としては弱いが、
`pc_mapping` という★別の正本★で見ると★機序として裏付けられており申した★★——
shogun/karo/gunshi は bridge 設定が★実在する★ (配送を試みる経路がある) のに対し、
takenaka/honda/sanada は★どの PC の pc_mapping にも一度も登場せぬ★=★bridge する経路そのものが 存在せぬ★。
★∴ 当職の第0段の判定(「本PC証拠だけでは⒝を確定できぬ」)は★訂正を要する★=
★pc_mapping という『もう一つの正本』を見れば、⒝(shogun/karo/gunshi)は★機序で裏付けられる★。
takenaka/honda/sanada の⒜判定はより強固に確定する(bridge先が構造的に無い)★。
★これを本工区の【己が直した誤り】として記す(§5)★。

## §2 『門』の実際の欠陥 — scope欄が無いのではなく、★二値が潰れておる★

`_cross_pc_bridge` は末尾で `bridge_info` が空文字なら「ローカル、bridge不要」として **無警告で** 素通りさせ
`_write_message` (ローカル書込) へ進む (L440-441)。★然れど「空文字」は 二つの別の事態を 同じ記号で表しておる★:

- **事態A (正当)**: TARGET が★本PCの local_agents に在る★ → 本当にローカルで正しい。
- **事態B (欠陥)**: TARGET は canon だが★どの PC の agents リストにも見当たらぬ★ (= takenaka/honda/sanada の実態) →
  ★配送先が無いのに「ローカルでよい」と誤読され、無警告でローカルへ書かれ、誰にも読まれぬ★。

★∴ 本当の穴は「registry に scope欄が無い」ではなく、★`_cross_pc_bridge` の戻り値が 事態A と 事態B を
区別しておらぬ点★に御座る。scope欄を registry に足すだけでは、★この関数が★見ておる出所 (`pc_mapping`) とは
別の場所に情報を置く事になり、★三つ目の名簿★を作るのみで根治にならぬ★。

## §3 ★受入条件⑴ (この修正が新たに開ける穴)★ — 実装を今 急がなんだ理由

★もし『registry の pc: 欄をそのまま門の判定に使う』案を早合点で実装すれば、以下の穴が★確実に★開き申す★:

1. **既に正しく動いておる shogun/karo/gunshi 宛の bridge 配送を壊しかねぬ**——
   現在の順序は「①canon check→②bridge試行→③(bridge不要なら)ローカル書込」。
   ★もし②の前に『pc: が本PCでないなら即reject』という門を割り込ませれば、
   ②へ辿り着く前に shogun/karo/gunshi 宛の正当な bridge 対象便まで reject されてしまう★
   (★これが 委員長殿の御指定条件『cross-PC 便の正規経路(pc_handshake)を妨げておらぬか』が
   名指しで警告しておった穴、そのものに御座る★)。
2. **`pane_registry.yaml` (`pc:`欄) と `pc_mapping` (`agents[]`) の★二正本を三正本化する★**——
   scope欄を registry 側だけに新設すれば、★門(`_cross_pc_bridge`)が実際に読むのは今も `pc_mapping` のまま★ ゆえ、
   新設欄は★見た目の安心を作るだけで 実効を持たぬ(表示専用の飾り)★危険がある。

## §4 提案 (実装は次段・要 家老second/対の三工区との合意)

★scope の実体は既に `pc_mapping.agents[]` に在る★ ∴ 新設すべきは registry の新欄ではなく、
★`_cross_pc_bridge` の戻り値を三値化する事★=

- `LOCAL` (事態A) → 現状通りローカル書込
- `BRIDGED` (成功) → 現状通り exit 0
- **`UNROUTABLE`(新設・事態Bを名指し)** → ★ローカルには書かず、TARGET宛でなくFROM宛に delivery_failed 相当の通知を返す
  (既存の「canon だが unroutable」通知パターン L350-354 と★同型★に揃える)★

★registry 側は『scope欄を新設』ではなく、★`pane_registry.yaml` の既存 `pc:` を正本とし、`pc_mapping.agents[]` は
そこから★生成・検算する側に回す★(★どちらが正本か を先に一本化せねば、次に足す欄がまた四つ目の名簿になる★)。
★この一本化の方式(どちらを正本にするか)は当職が単独で決めず、対の三工区(足軽2号=失敗報の門/足軽5号=intake_validator/
足軽3号=出口の門)と★スキーマを揃えてから★着手する(採番・スキーマ衝突の型は本日何度も学んだ通り)★。

## §5 己が直した誤り (必須欄)

1. 第0段(六名分類)提出時点では「本PC証拠だけでは⒝(他PCで生きておる)を確定できぬ」と★判定不能のまま残した★が、
   本工区で `pc_mapping` を実測した結果、★shogun/karo/gunshi には実在する bridge 設定という機序的裏付けが在る事が
   判明し、判定不能から一歩進めるべきであった★事を認め、ここに訂正する。
2. 「scope欄を registry に足す」という下命をそのまま実装しかけたが、既存 `_cross_pc_bridge` を読んで
   ★scope相当の情報が既に別正本 (`pc_mapping`) に在ると気付き、実装前に立ち止まった★
   (実装してから気付けば「三正本化」という新たな穴を自分で開ける所であった)。

## §6 未検めの残り

- pc_handshake への実配送成否 (live) — credential 探索の要る範囲ゆえ本工区の縛り外。家老second/委員長殿の権限で
  別途確認要 (`誰が止めれば止まるか`=Supabase env を持つ役職のみ検証可)。
- `pane_registry.yaml` の `pc:` を正本化する場合の移行手順そのもの — 対の三工区との合意後に着手。

---
**報告**: 家老second。★実装(registry編集・commit)は本設計の合意後に着手する★。paired lane (足軽2/5/3号) との
スキーマ合意を待つ間、当職は他の安全な作業に切替可。
