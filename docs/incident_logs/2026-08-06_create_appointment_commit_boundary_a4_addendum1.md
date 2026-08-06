# addendum1 — 正本ref訂正 (足軽4号)

親report: `docs/incident_logs/2026-08-06_create_appointment_commit_boundary_a4.md`
訂正契機: 家老second便 `msg_20260806_133506_9161024a`「木 /mnt/c/Projects/hakudokai-dev は正本に非ず」

## §0 基準ref・sha16・読んだpath（下命④の三点）

- 基準ref＝`origin/wp-a1-a3-3-20260723`。当職が本addendum作成時に`git fetch`した断面＝`feb945cf7d0a7ab7757449b07a2b20f8ce1e3b3d`（家老second引用の`78573ba7`より新しい。★fetchでrefが動いた事を隠さず明記★）。
- ★念のため実測＝`git diff --stat 78573ba7 feb945cf -- <対象6file>`＝差分0（両shaで対象fileの中身は同一）。∴ どちらのshaを基準にしても本addendumの結論は変わらぬ。
- 読んだpath＝`git -C /mnt/c/Projects/hakudokai-dev show <ref>:<path>` を一時fileへ吐かせて読取（★木を汚さず・commit零★）。

## §1 独立再検証（親reportが対象とした6file全て）

| file | /mnt/c実測(親report記載) | 正本実測(本addendum) | 判定 |
|---|---|---|---|
| appointment_service.py | 740行 sha16=3f12ab3cd03b68a4 | 740行 sha16=**2aa999da70fe8405** | ★内容一致(git diff -b=0行)。sha16のみCRLF由来で不一致★ |
| booking_validator.py | 693行 sha16=b03efeb3c4dbef34 | 700行 sha16=**5c30548b93a06285** | ★実の差あり(`staff_is_available`呼出7行が正本で削除済)。親reportは同fileの内部行番号を1件も引用しておらぬ ∴ 親reportの結論(commit=0件)への影響を実測=下記§2 |
| diagonal_service.py | 445行 sha16=20df9fcaeb1f8181 | 445行 sha16=**58c31683c7087af8** | 内容一致(git diff -b=0行)。sha16のみ不一致 |
| prediction_service.py | 575行 sha16=302104152651126e | 575行 sha16=**543750d495099bd3** | 内容一致(git diff -b=0行)。sha16のみ不一致 |
| appointment_log_service.py | 72行 sha16=30af5fec0e6c8f09 | 72行 sha16=**64e938e072e26a8e** | 内容一致(git diff -b=0行)。sha16のみ不一致 |
| appointment_lock.py | 37行 sha16=9ce1715ce1c1b692 | 37行 sha16=**38703b9196a76f91** | 内容一致(git diff -b=0行)。sha16のみ不一致(本fileは親reportの結論に不使用) |

★判定方法★＝`git diff -b <ref> -- <file>`（whitespace無視）の出力行数で判定。0行＝完全一致（CRLF以外の差なし）。booking_validator.pyのみ非0。

## §2 booking_validator.pyの実の差が親reportへ与える影響＝実測で無影響

親reportはbooking_validator.pyについて「sha16のみ・commit()出現数=0件」の2点のみを引用し、内部行番号は1件も引用していない（親report §0・㈣参照）。
実の差分＝`staff_is_available`のimport1行＋呼出block6行（`_check_basic`内・`.commit(`を含まぬ純チェック処理）の削除のみ。
正本(feb945cf)でのcommit出現数を実測＝`git show feb945cf:.../booking_validator.py | /usr/bin/grep -c "\.commit("` = **0**。
∴ ★親report ㈠〜㈤の結論(commit境界=appointment_service.py内L221/L230+呼出先6件・置ける/置けぬ点の分析)は 一切変更を要さぬ★。

## §3 訂正すべき値（親report内・置換対象）

親reportの§0・㈡(b)表・㈤に記載した以下のsha16のみを、正本値へ置換する必要がある（他の記述=行番号・関数境界・commit境界・acquire/complete候補・置けぬ理由・三値の判定は無変更）：

| 親reportでの記載 | 誤(CRLF木由来) | 正(origin/wp-a1-a3-3-20260723) |
|---|---|---|
| appointment_service.py | 3f12ab3cd03b68a4 | 2aa999da70fe8405 |
| booking_validator.py | b03efeb3c4dbef34 | 5c30548b93a06285（★かつ700行・355行定義。行数・def位置も訂正★） |
| diagonal_service.py | 20df9fcaeb1f8181 | 58c31683c7087af8 |
| prediction_service.py | 302104152651126e | 543750d495099bd3 |
| appointment_log_service.py | 30af5fec0e6c8f09 | 64e938e072e26a8e |
| appointment_lock.py | 9ce1715ce1c1b692 | 38703b9196a76f91 |

## §4 三値

- ★訂正の要否＝実測済・要（sha16 6件+booking_validator.pyの行数/def位置）★。★内容面の結論の要否＝実測済・不要（appointment_service.py含む5fileは内容完全一致、booking_validator.pyの実差は親reportの引用範囲外）★。
- 家老second条⑤（「木の名は正しさを与えぬ。正本と一致するかを書け」）への当職の適用＝本addendumの§1表がそれに当たる（一致/不一致を実測で判定し、木の名ではなくgit diff -bの行数で示した）。
