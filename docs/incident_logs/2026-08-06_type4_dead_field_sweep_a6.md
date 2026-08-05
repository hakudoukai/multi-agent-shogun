# 型④(在るが誰も使わぬ)横断棚卸し・小口 (足軽6号、2026-08-06・家老second下命)

★★読取のみ(grep実施のみ)。code不触・commit不触。当職の飽和(554.1k tokens)を理由に、
家老second殿より★小口で可★と明示許可済★★。測時=2026-08-06T00:22:12+0900(date -Iseconds実行結果)。

## 母集団・探索範囲(明記)

対象=`scripts/inbox_write.sh` / `scripts/inbox_watcher.sh` / `scripts/read_pruned_archive.sh`
の3fileのみ(飽和ゆえ、shim/hakudokai/全47file・scripts/全36fileの網羅は行っていない)。
検査=①bash関数定義(正規表現`^[a-zA-Z_]+\(\)`)を抽出し、scripts/+shim/全体での出現回数を実測
②足軽2号発見の型を仮説として`supersedes`/`expires_at`フィールドの消費有無を実測。

## ①候補チェック(仮説→棄却、健全例として報告)

`supersedes`/`expires_at`フィールド(message YAML内)を「書かれるが読まれぬ場」の候補として
実測した所、両方とも`scripts/inbox_watcher.sh:429,436-437,477,483-484`で実際に消費されている
事を確認(supersede処理・expiry判定のロジックに組み込み済)。**∴ 仮説は棄却=型④の実例ではない**。
自分の予想を検めずに報告しなかった事を明記する(健全な仮説棄却の実例)。

## ②関数呼び出し回数(実測・列挙)

`inbox_write.sh`の10関数・`inbox_watcher.sh`の27関数、計37関数を抽出し、scripts/+shim/全体での
出現回数(定義行含む)を実測。**結果=全37関数が2回以上出現(定義+最低1回の呼出)。出現1回(定義のみ・
呼出0)の関数=★測って0件★**。

## 結論

**本工区の狭い範囲(3file・37関数+2field)では、型④(定義/書込されるが消費されぬ物)の新規実例=
測って0件。** ただし母集団はshim/hakudokai/全47file・scripts/全36fileのうち3fileのみであり、
★網羅探索ではない★(飽和による意図的な縮小、家老second殿の許可済)。残る約80fileは未探索のまま
である事を明記する。

## ★母集団漏れの自己申告★

1. shim/hakudokai/配下(python file多数)は今回一切検査していない(足軽2号が発見した実例そのものが
   この配下=`senmu_desktop_route_watcher.py`であり、当職が検査した3fileとは別の population)。
2. python関数(def)・dict field個別の網羅チェックは行っていない(bash関数のみ)。
3. 呼出回数の実測は「grep一致」のみであり、動的呼出(eval・関数名を変数経由等)がある場合は
   見逃す(本日確立の教訓=道具の出力は道具の判定に非ず、を踏まえ限界として明記)。

## 【本工区で己が直した誤り】

初稿でsupersedes/expires_atを型④の実例として報告しかけたが、grep実測で両方とも実際に消費されて
いる事に気付き、仮説棄却として書き直した。

## 監査体制

★暫定二者制(軍師+Gemini)。Codex leg停止中(2026-07-21事案)★。

以上、型④横断棚卸し・小口への応答。飽和ゆえ以後本工区を打ち止め、次はkaro-second殿の指図を待つ。
