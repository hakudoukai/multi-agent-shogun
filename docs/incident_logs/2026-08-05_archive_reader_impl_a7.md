# `_archive/` 読み手helper 実装 (委員長裁可・設計→実装昇格) — 足軽7号

家老second殿下命(msg_20260805_141323_cb27ccd5、委員長殿裁可「照合完了を待たず先に直してよい・lane内ゆえ凍結対象外」)
への応答。先行=当職`2026-08-05_archive_readable_design_a7.md`(設計)。★書き手(`inbox_write.sh`)は不触★
(委員長殿御指摘どおり、multi-doc append自体は正当な設計・欠陥は読み手側)。⑵(archive先頭へcomment追加)は
karo-second殿が将軍second殿へ照会中ゆえ★保留★(⑴⑶のみ実施)。

台帳・他者成果物・影file・dd189・process・registry・inbox_write.sh本体、いずれも不触(読むのみ)。
bats実行なし(止血継続中)。★commitは未実行★(下記【境界の確認】参照・自己判断で実行せず)。

断面=2026-08-05T14:23:43+0900。base_commit=502cbfe(実測=HEAD一致)。

参照した正本: `scripts/inbox_write.sh`(L120-159、writer全文Read・不触確認用)/
`/tmp/claude-1000/.../71b9bdfa.../scratchpad/w134_archive_reader_trap_a4_20260804.md`
(足軽4号、208行、既にPASS監査済=`queue/reports/gunshi_second_w134_archive_reader_trap_audit_20260804.md`)/
当職先行設計`2026-08-05_archive_readable_design_a7.md`。

---

## 【本工区で己が直した誤り】

初稿の設計案(先行file)で「既存の読み手helperは皆無・新設は正当」と書いたが、実装着手前にW134(足軽4号、
既にPASS監査済)を発見・全文読了した所、★同じ結論(読み手0件)へ既に到達しており、かつ当職が今回踏むはずだった
None-document crash(`AttributeError: 'NoneType' object has no attribute 'get'`)を★前日15:21時点で既に実測済★
であった。Anti-Duplication徹底=当職の実装はW134のこの知見(None filter必須)を★踏襲する形で書き直した★
(独自に再発見して恩着せがましく書く事はしなかった、出典を明記)。

## Anti-Duplication確認(既存資産の再確認)

- 既存の同等helperは repo 全域で皆無(`/usr/bin/grep -rn "yaml\.safe_load" ...`で52件列挙、
  うち`_archive`/`_pruned`を対象とする物は`scripts/inbox_write.sh`(writer)のみと確認——W134の
  母集団確認と一致・当職も独立に再確認した)。
- ∴ 新設は正当(重複実装ではない)。

## 実装内容

新設: `scripts/read_pruned_archive.sh`(82行/sha256=85a2251eda52cc95adb7988d91b0545c502ffd4b60440321a758e474274e4f83)。
- `yaml.safe_load_all()`で multi-document stream を読み、`None` document(全fileで末尾に1件混入)を
  filterした上で`messages`を連結・件数と共にJSON出力する、★唯一の正規読み出し口★。
- 書込み一切なし(読み取り専用)。既存archive fileの中身・writer(`inbox_write.sh`)は無変更。

## ⑴全数列挙(safe_load→safe_load_allへ置換すべき箇所)

対象=`_archive`/`_pruned`を参照するsafe_load呼出。★実測=該当箇所は repo 全域で0件★
(`inbox_write.sh`のwriterのみ。読み手コードはW134実測時点(前日)から今日まで新設されておらず不変)。

**陽性対照(0件を探索失敗と区別)**: 同じgrep機構で`yaml\.safe_load`全般は★52件★ヒットする事を先に確認
(下記⑶の実出力に含む)——探索手段自体は生きており、「_archive/_pruned系だけ0件」は不在の証拠として扱ってよい。

∴ ⑴の実装対象は「既存呼出の置換」ではなく「★これから使われるべき正規口の新設★」となった
(委員長殿の「読み手がsafe_loadを使う事が欠陥」との所見は、★次に誰かが素朴に書けば的中する未然の欠陥★
という意味で成立し続ける——現に踏んだ実例=当職自身が本工区着手前に素朴な`safe_load`で同じComposerErrorを
再現している、下記⑶)。

## ⑶陽性対照(直す前/直した後、実出力そのまま)

**直す前(素朴なsafe_loadが現に落ちる、karo-second分で代表実演)**:
```
ComposerError: expected a single document in the stream
  in "queue/inbox/_archive/karo-second_pruned.yaml", line 1, column 1
but found another document
  in "queue/inbox/_archive/karo-second_pruned.yaml", line 282, column 1
```

**直した後(新helperで実際に読めた件数、母集団11file全数、コマンドそのまま再現可能)**:
```
$ bash scripts/read_pruned_archive.sh queue/inbox/_archive/karo-second_pruned.yaml --count-only
{"file": "...karo-second_pruned.yaml", "documents_total": 73, "documents_none": 1, "messages_total": 974}
$ bash scripts/read_pruned_archive.sh queue/inbox/_archive/shogun-second_pruned.yaml --count-only
{"documents_total": 23, "documents_none": 1, "messages_total": 436}
$ bash scripts/read_pruned_archive.sh queue/inbox/_archive/gunshi-second_pruned.yaml --count-only
{"documents_total": 13, "documents_none": 1, "messages_total": 219}
$ bash scripts/read_pruned_archive.sh queue/inbox/_archive/ashigaru1_pruned.yaml --count-only
{"documents_total": 5, "documents_none": 1, "messages_total": 80}
$ ashigaru2: {"documents_total": 6, "documents_none": 1, "messages_total": 98}
$ ashigaru3: {"documents_total": 6, "documents_none": 1, "messages_total": 94}
$ ashigaru4: {"documents_total": 5, "documents_none": 1, "messages_total": 79}
$ ashigaru5: {"documents_total": 5, "documents_none": 1, "messages_total": 80}
$ ashigaru6: {"documents_total": 6, "documents_none": 1, "messages_total": 100}
$ ashigaru7(当職自身): {"documents_total": 5, "documents_none": 1, "messages_total": 71}
$ _test_cap_rotation: {"documents_total": 2, "documents_none": 1, "messages_total": 21}
```
11file全てで成功(エラー0件)、★かつ全fileで末尾に`None` document 1件を検出・安全にfilter済★
(W134が前日発見した穴を再現・本helperで解消)。legacy単一document 3file(fukuincho/gunshi/shogun)も
後方互換で正常動作を確認(fukuincho=25993件・gunshi=31件・shogun=810件、いずれもエラー無し)。

**総量=他者に測らせる為、上記コマンドはそのまま貼り付け実行可能な形で記した**(当職の暗算・転記に依らず、
軍師second殿が同じコマンドで独立に再現できる)。

## 【新たに開ける穴】(①、隠さず記す——本工区最大の発見)

★実装した`scripts/read_pruned_archive.sh`は現在★.gitignoreにより除外され、git追跡対象外★★——
実測:
```
$ git check-ignore -v scripts/read_pruned_archive.sh
.gitignore:7:*	scripts/read_pruned_archive.sh
$ git status --short --branch | grep read_pruned
(該当無し=git statusにも一切出現しない)
```
本repoの`.gitignore`は「Step1: 全て除外→Step2: dir探索のみ許可→Step3: 個別fileを`!path`で明示許可」
という★whitelist方式★(`scripts/inbox_write.sh`等は`.gitignore:115`等で個別に許可済だが、新設した
`read_pruned_archive.sh`はどこにも許可行が無い)。∴ ★このまま放置すると『動くが誰にも見えない
(git履歴に残らない)』という、本工区の主題(『保存されておるのに読めぬ』)と★同型の穴★を、
当職自身が新たに開けてしまった事になる。

**是正に要る一手**: `.gitignore`へ`!scripts/read_pruned_archive.sh`を1行追加すれば解決するが、
★これは`.gitignore`という全agent共有の設定fileへの変更であり、当職の裁量で決めてよい範囲か
判定不能ゆえ、⑵ (archive先頭commentの可否) と同様、★上位の確認を仰ぐまで実行せず保留する★。

## 誰が止めれば止まるか

本helperは★追加のみ・他fileへの依存や書込みが一切無い★新規fileゆえ、停止手段は`rm scripts/read_pruned_archive.sh`
一つのみ(実行すれば即座に無害化・他の何も壊れない、既存archive/writerは無変更のまま)。

## 【境界の確認】commitは実行せず

下命は「commit前にgit statusの出力をそのまま貼れ」と手順を示すのみで、明示的な「commit実行可」の
文言までは含んでおらぬと当職は読んだ——かつ上記の通り★.gitignoreの是正がまだ済んでおらぬ(新規fileが
git追跡対象外のまま)★ゆえ、現時点でcommitしても本fileは含まれ得ない。∴ commitは実行せず、
.gitignore是正の可否と併せて上位の判断を仰ぐ。(git status出力は上記【新たに開ける穴】節に実出力を同梱済)

## 母集団漏れの自己申告

1. `queue/tasks/archive/`・`queue/archive/`(W134が「参考実測・reader 0件」と付記した類縁archive)は
   本工区の対象外(下命の主題=`queue/inbox/_archive/*_pruned.yaml`のみ)。
2. W134原文はscratchpad path(他agent由来)から読んだ——本人による今この瞬間の追認は得ていない
   (書かれた内容自体はPASS監査済のため、内容の信頼性とは別問題として明記)。

## 監査体制

暫定二者制(軍師+Gemini)。Codex leg停止中(2026-07-21事案)。

以上、実装+陽性対照、家老second殿の受理判断へ供する。.gitignore是正の可否、御指示願いたし。
