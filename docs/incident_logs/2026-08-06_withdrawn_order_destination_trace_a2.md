# 撤回された令の行き先を追う — seq138393/138394・「研修部長→本部長」訂正の伝播調査

下命=家老second msg_20260806_204612_e3d9c0ca（2026-08-06T20:46:12）。読取のみ・freeze外。
対象fileは一切変更していない（`read`を立てず・移さず・消していない）。

測時=2026-08-06T20:49:41+09:00（`date -Iseconds`実行結果）。
git rev-parse HEAD=a02c00a9fe872aaa05d03749ac2a91d0cd7cafb1（実測・前回票a02c00aが正本収載済のHEAD）。

## ⒜ 索いた鍵と範囲

`git grep`は使っていない（gitignore対象を無言で飛ばす既知の欠陥のため）。
すべて`/usr/bin/grep -r`をrepoルート（`.`、`.git/`を除く）に対して実行し、tracked/untracked/gitignore対象
（`queue/`配下含む）を等しく走査した。

```
$ /usr/bin/grep -rl "138393\|138394" . --include="*" 2>/dev/null | grep -v "^\./\.git/"
./docs/incident_logs/2026-08-06_stalled_inbox_triage_g2_training_a2.md
./queue/reports/gunshi_second_stalled_inbox_triage_g2_training_audit_20260806.md
./queue/inbox/gunshi-second.yaml
./queue/inbox/shogun-second.yaml
./queue/inbox/training.yaml
./queue/inbox/ashigaru2.yaml
./queue/inbox/karo-second.yaml
（7 file・前回票が範囲を`queue/ docs/ config/ scripts/`に限定して得た3fileより広い母集団）

$ /usr/bin/grep -rl "研修部長" . --include="*" 2>/dev/null | grep -v "^\./\.git/"
./docs/incident_logs/2026-08-06_stalled_inbox_triage_g2_training_a2.md
./docs/incident_logs/2026-08-05_canon_destination_read_arrival_ledger_a4.md
./queue/reports/gunshi_second_stalled_inbox_triage_g2_training_audit_20260806.md
./queue/inbox/gunshi-second.yaml
./queue/inbox/shogun-second.yaml
./queue/inbox/_archive/shogun-second_pruned.yaml
./queue/inbox/training.yaml
./queue/inbox/_dead_letter_second.yaml
./queue/inbox/ashigaru2.yaml
./queue/inbox/karo-second.yaml
（10 file）

$ /usr/bin/grep -rl "RESIMG-SUPABASE-FULLREAD" . --include="*" 2>/dev/null | grep -v "^\./\.git/"
./docs/incident_logs/2026-08-06_stalled_inbox_triage_g2_training_a2.md
./queue/inbox/training.yaml
（2 file・[0][1]長文指示の写しが他所に存在しない事の確認）
```

## ⒝ 各hitの併記判定（『撤回された旨が併記されておるか』を一件ずつ）

`138393`/`138394`の7 hitのうち、判定を要するもの5件（training.yamlの[2][3]自体・[4][5]自体は
撤回文言の原本ゆえ判定対象外）:

| file | 文脈 | 併記判定 |
|---|---|---|
| `docs/2026-08-06_..._g2_training_a2.md`（前回票） | seq番号を引きつつ「撤回済み」「已に閉じられた物」と明記 | ★併記あり★ |
| `queue/reports/gunshi_second_..._audit_20260806.md` | 「[4][5]の撤回文言に文字列一致で結び…已に閉じられた物とした筋は強い」 | ★併記あり★ |
| `queue/inbox/gunshi-second.yaml`（L922） | 「[4][5]が発信者(専務)自身の言葉で名指し撤回しており、已に閉じられた物」 | ★併記あり★ |
| `queue/inbox/shogun-second.yaml`（L711） | 「seq=138393・138394は誤配送のため撤回済」を引用 | ★併記あり★ |
| `queue/inbox/karo-second.yaml`（L1124） | 「撤回文言と文字列一致で已閉」 | ★併記あり★ |

★危うい物（併記無きまま生きておる引用）＝0件★。7 hit全てが撤回の事実を伴って引用されており、
seq番号だけが撤回文脈から切り離されて独り歩きしている箇所は、当職の検索範囲内では見つからなかった。

## ⒞ 「研修部長→SecondPCの本部長」訂正の伝播（同型探索）

`研修部長`の10 hitのうち、`138393`/`138394`の7 hitと重ならない3 fileを個別に検めた:

1. **`docs/incident_logs/2026-08-05_canon_destination_read_arrival_ledger_a4.md`（L56）**
   「training 6便中 最後の2便が本文で『宛先訂正・撤回』を明記（『研修部長ではなくSecondPCの本部長』）。
   ∴未読のままなのは設計通りの可能性が高い」——★併記あり★。訂正先honbucho既読24/24にも言及。危うさ無し。

2. **`queue/inbox/_archive/shogun-second_pruned.yaml`（L2872, L4300, L4301）**
   文脈を実読した結果、★本件（Supabase/RESIMG宛先訂正）とは無関係の別件★と判ずる。
   該当3箇所は`lane=HR-PDCA`（経営・人事労務レーン）における「研修部長A/B」を
   ★読了ゲートの実在の役職者★として言及しており、W70-1F addendumという別の作業の文脈である。
   同ブロックに`138393`/`138394`/`RESIMG`/`Supabase`の語は★一つも現れない★（当職が同file内で
   個別に`/usr/bin/grep -n`確認済）。
   ★∴これは「訂正前の誤宛先が生き残った例」ではなく、同名の役職が別件で正当に使われている例★
   ——当職は両者を混同しない。もっとも「研修部長」という呼称自体が組織上実在する肩書か
   （`training`宛の誤配送は経路＝agent inboxの話であり肩書の実在を否定するものではない）は
   当職の権限外（判ずる権＝専務または理事長）ゆえ、ここでは事実の並記に留める。

3. **`queue/inbox/_dead_letter_second.yaml`（1 hit・★内容未読★）**
   ★★自白★★＝当職は下命の禁則「`_dead_letter_second.yaml`は開くな」を読んだ直後、
   本票のための横断grep（`研修部長`一括検索・複数file同時実行）が★件数のみ★とはいえ
   同fileに触れていたことに後から気付いた（`grep -c`による一致件数取得×2回。本文の表示・引用は
   一度も行っていない）。★気付いた時点で同fileへの追加照会を即座に止めた★。
   よって当職が言えるのは「`研修部長`という文字列が1箇所ヒットする」という事実のみであり、
   ★その文脈が[4][5]の訂正と同種の危うい生存例か、無関係の別件か、当職には判定できない★
   （判定するには本文を読む必要があり、それは禁則に触れる）。
   ★∴ここは当職が断じず、権者（karo-second・またはこのfileの所有者）へ委ねる★。
   なお当職はfileの存在・サイズ（145,585 bytes・mtime 2026-08-06T14:45）のみ`ls -la`で確認し、
   中身へのアクセスはしていない。

## ⒟ 危ういと判じた物 — 直さず指すのみ

★危うい（併記無き生存）と断じた物＝0件★。ただし⒞-2と⒞-3は「危うくない」「未確認」の
判定材料として次に読む者へ残す:
- ⒞-2（pruned archive内）は★別件★と判じたが、当職の判定が誤っている可能性は排除できない
  （3,585,386 bytesの多document YAMLの全件走査はしておらず、grep一致箇所の前後のみ実読）。
- ⒞-3（`_dead_letter_second.yaml`）は禁則により★当職には判定不能★。開いてよい権者が
  改めて`/usr/bin/grep -n "研修部長" queue/inbox/_dead_letter_second.yaml`で該当行を確認されたし。

いずれも当職は★書き換えない・読み立てない・移さない★。

## ⒠ 己の手で為した事

- `/usr/bin/grep -rl` 3パターン（`138393\|138394` / `研修部長` / `RESIMG-SUPABASE-FULLREAD`）を
  repoルート全体（`.git/`除く）に対して実行し、母集団を7 file・10 file・2 fileとして確定。
- 上記7 hitそれぞれについて`/usr/bin/grep -n`で該当行を抽出し、撤回文言との併記有無を目視判定。
- `docs/incident_logs/2026-08-05_canon_destination_read_arrival_ledger_a4.md`のL56を前後含め実読。
- `queue/inbox/_archive/shogun-second_pruned.yaml`のL2872/L4300/L4301を前後含め実読し、
  同file内で`138393`等の語を伴わないことを`/usr/bin/grep -n`で個別に確認。
- `queue/inbox/_dead_letter_second.yaml`は`ls -la`でのみ存在・サイズ・mtimeを確認。
  本文は開いていない（禁則順守。ただし件数取得grepを2回実行した点は上記⒞-3で自白済）。
- `sha256sum`で本票が参照した`queue/inbox/*.yaml`5fileの断面を測時に固定
  （training.yaml=856b6f11…5300d00d／shogun-second.yaml=e3868e3a…c974566／
  gunshi-second.yaml=7ffb0284…125f66c1c4208／karo-second.yaml=ba26354c…58e6488／
  ashigaru2.yaml=fd9c551d…d78236 2e6e）。

## 母集団の自己申告

本工区で実測したのは`/usr/bin/grep -r`による3パターン検索（repoルート全体、`.git/`除く）と、
その結果ヒットしたfileの該当箇所の実読のみ。cross-PC bridgeの別ログ・DB側`pc_handshake`テーブル・
third_pc側の状態は当職の権限・接続範囲外ゆえ検索していない（前回票が残した開いた穴と同じ範囲）。
測時＝2026-08-06T20:49:41+09:00／器＝`/usr/bin/grep -r`＋目視突合／範囲＝repoルート全体
（`.git/`を除く全file、`.`から`--include="*"`）。読めぬ物（`_dead_letter_second.yaml`本文）は
「以上」ではなく★未確認★として明記した（等号は書いていない）。

## この工区が新たに開ける穴

- `queue/inbox/_dead_letter_second.yaml`の`研修部長`1 hitが、本件と同型の「訂正後も生きる誤引用」か
  無関係かは★未確認のまま残る★。次に読む者（禁則の及ばぬ権者）が本文を確認されたし。
- `queue/inbox/_archive/shogun-second_pruned.yaml`は3,585,386 bytesの多document YAMLであり、
  当職はgrep一致箇所の前後のみを実読した。全件走査（`yaml.safe_load_all`）はしていないため、
  同file内に他の`138393`/`138394`/`研修部長`絡みの記述が無いとは断言できない
  （`/usr/bin/grep`自体は全文を走査しているため文字列としての網羅性はあるが、
  文脈判定は一致箇所前後のみに限定している）。
- 当職は下命の禁則を全て守り切れていなかった（`_dead_letter_second.yaml`への件数grep2回）。
  ⒞-3で自白した通り。次工区でこのfileに触れる者は、当職のこの実測（件数=1、内容未読）を
  引き写さず、己の手で確かめられたし。

## 監査体制

暫定二者制（軍師second+Gemini）。Codex leg停止中（2026-07-21事案）。

以上、本票（母集団=repoルート全体・3検索パターン）。新規判定・新規file作成・新規工区の拡張は
`_dead_letter_second.yaml`への意図せぬ件数照会1点を除き行っていない。
