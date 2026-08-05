# git外である事実の記録（dashboard.md）— 足軽1号（訂正版）

## 差し替え経緯（自己申告・隠さず記す）

- 家老second下命（msg_20260806_071213_890a593e、07:12:13）は当初「7件（instructions/6件+dashboard.md）を同じ形で全文複写せよ」だった。
- **07:14:44に家老secondより訂正**（msg_20260806_071444_18512268、将軍second裁）: 7件は同格ではない。instructions/6件は人が書いた canon（不変の正本）ゆえ全文複写で意味が救われるが、dashboard.mdは家老・軍師が絶えず書き換える状態表（生き物）ゆえ、全文複写すると「保全写しの札を付けた古い状態表」がgitに残り、後の読者が「当時の実状」と誤読しうる（幽霊正本の状態表版）。∴ dashboard.mdは全文複写せず「git外である事実」のみ記録する方式に改める。
- **★当職の落度★**: 訂正は当職が複写作業に着手する前（07:14:44）に届いていたが、複写完了・軍師second提出（07:44:10）まで当該inboxを再確認せず見落とした。∴ 旧版（全文複写）を一度作成し提出してしまった。
- **旧版の扱い**: 削除ではなく `docs/incident_logs/2026-08-06_role_canon_gitignored_preserved_copy_dashboard_a1_SUPERSEDED_full_text_v1.md` へ改名し保全した（「戻すより先に残して報せよ」の条 msg_20260806_072535_4519be9d 準拠。中身は無改変・rename のみ）。
- 本file（同一パス名で再作成）が訂正後の正式版。instructions/6件側（`2026-08-06_role_canon_gitignored_preserved_copy_instructions_a1.md`）は下命どおり全文保全のまま変更なし。

## 記録（git外である事実のみ・全文は含まない）

- path: `dashboard.md`
- 行数: 680
- bytes: 126552
- sha256（測定時点）: `2e9e4b742f5db0ae5c69a15ee7221de72392a25e4ce39f5d96497e86347476e7`
- `git check-ignore -q dashboard.md` 終了コード: 0（ignored）
- `git status --porcelain --ignored=matching` の表示: `!!` (ignored)
- 測定秒: UTC 2026-08-05T22:19:27Z / JST 2026-08-06T07:19:27+09:00
- HEAD（測定時点）: `d76b025`

## 性格（訂正指示の要旨）

生成物ゆえ失っても再び作り得る。∴ 救うべき意味は元より薄い。instructions/6件（人が書いたcanon）とは性が異なる — 括りは「git外」という場面ではなく、書き換えられるか否かという性で決めるべきだった。

## 復元条件

.gitignore の裁可が下り dashboard.md が tracked へ戻された折には、tracked 対象として残す（= 正本へ戻す）。本file・旧版(_SUPERSEDED)ともに以後は履歴としてのみ扱う。

## 未測・境界

- 本file はdashboard.mdの「git外であるという事実」の断面記録に過ぎず、内容（実際に何が書かれているか）は含まない。内容を知りたい場合は稼働中のSecondPC上の正本dashboard.mdを直接参照すること。
- 旧版(_SUPERSEDED)は既に軍師secondへ提出済（msg_20260806_074410_a35928a6）であり、本訂正版の提出は別途行う。
