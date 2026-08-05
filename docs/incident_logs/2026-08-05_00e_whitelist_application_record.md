# 00E — .gitignore へ `!` 三行を適用した記録（委員長殿 裁可・家老second 実行）

作成 = 家老second / 測時 2026-08-05T21:53:27+09:00 前後（機械）
出所 = 委員長殿 裁可（将軍second 経由 msg_20260805_215319_ae8a0608）
起案 = 足軽1号（00E 門 追補4 / commit 16e76f6）

証拠は code fence の外・素の文字で記す。

## 一 ★本裁可は「止血」である（委員長殿 明示・必ず読むこと）★

> **本裁可は ★止血★ に御座る。根治＝「落ちた事がうるさく分かる門（門①・委員長殿 裁定済）」の
> 装着をもって完了。**

理由: 本案は三 file を **個別名指し**で通す ∴ **新しい file が増えるたびに `!` の追加が要る**。
∴ **00E の根本（whitelist 方式が★無警告で落とす★）は解けていない。**

> **★止血の成功を「機構が不要になった証拠」と読むな。★**

## 二 適用の実測（五点）

適用前 .gitignore = 423行 sha256=ab86e6cfc50c8921ad0b20536dff7f37628329be76f230c8e528eab512d564ab
適用後 .gitignore = 426行 sha256=b99f6401d865d51a74ee569559887e3ad1233f48bba1ce9855cab4843383745d
追加した三行（末尾へ append・逐語）=
!docs/00e_gate_release_ledger.md
!scripts/lib/ignored_active_predicate.sh
!scripts/lib/00e_gate_thresholds.sh

- **③ 変更行数 = 3**（凍結写しとの diff の一致行数。他の 423 行に触れていない。止まれ条件クリア）
- **① 三 file が実際に追跡された = 3件**（`git ls-files` を集計。head は掛けていない）
- **② 他が増えていない = `git ls-files` 総数 534 → 537、差 3**
- **④ commit は未了**（HEAD は 16e76f6 のまま。三 file は staged のみ。軍師second PASS 後に commit する）
- **⑤ secret 走査 = ★走らせ得ず★**（下記 三節）

## 三 ★⑤ secret 走査は走らせ得なかった —— 黙って飛ばしていない★

- 指定された `scripts/security/scan_supabase_secrets.py` は **当 repo に存在しない**
  （hakudokai-dev の origin/main に在るとの由。**repo を跨ぐ**）
- 汎用走査具（gitleaks / trufflehog / detect-secrets / git-secrets）は **`command -v` で四つとも不在**
- ∴ **走らせ得ない。**「0件」ではなく **「未実施」** である

**代わりに行ったこと（これは専用走査ではない）**: 家老second が手動 grep で
password / secret / token / api_key / private_key / BEGIN PRIVATE / JWT 様 / sk- / xox / AKIA /
supabase / service_role を三 file に当て、**該当 0 件**。
file 種別も確認（三つとも UTF-8 テキスト・最大 4820 bytes ∴ 巨大 binary ではない）。

> **★これは「走査した」ではなく「目視の当たりを付けた」に過ぎない。★専用走査の代替にはならない。**

## 四 ★decoy 未実測（逐語・消さないこと）★

足軽1号の申告（逐語）:
> 「もし将来 scripts/lib/ 直下に secret_credentials.sh や patient_data.sh の如き file が
> 生まれた場合も通らぬか」の decoy 実験は、当職が clone 上で試みた際に **許可 dialog で拒否され申した**
> （dummy file 作成 + 5MB 疑似 binary 書込を含むコマンドが弾かれ申した・理由は当職には分かり申さぬ）。
> ∴ この一点は **未実測** に御座る。
> 但し pattern が anchored かつワイルドカード無しの完全一致ゆえ「別の名前の file が誤って通る」事は
> **git の pattern-matching 仕様上 構造的に起こり得ぬ**（**理屈による保証・実行による保証ではない
> —— 両者は別物と心得申す**）。

委員長殿の裁定（逐語）:
> 本件は **理屈で足りる**。根拠 = anchored ＋ワイルドカード無し ＝ マッチ対象が 1 パスに限定されるのは
> git の仕様であり、**「3件のみ変化した」という実測が、その仕様が現に働いておる証拠**である
> ∴ decoy 実験は **既に実測された仕様の別の現れ**を再確認するに過ぎない。

> ### **★一般則: 理屈で足りるのは、その理屈が現に働いている事を★別の形で実測できている★時のみ。★**
> ### **★実測が一つも無い理屈は、理屈ですらない。★**

## 五 起案手法（委員長殿 §48-d-62 として様式に採用・★検定済★）

足軽1号は **隔離 clone**（`git clone --no-hardlinks`）を作り、その clone の .gitignore にのみ
候補行を試し、実測後に **clone 自体を削除**した。**本番の .gitignore は一文字も編まずに実測を得た。**

様式に採られた三点 = ①`--ignored=matching -uall` で測る ②母集団は repo 全 file
（変わっていない物も含めて diff）③**実測後に複製を消す**（残せばそれ自体が未追跡の滞留）

**賞に費用を添える**（本日制定）: 本手法は隔離 clone 作成＋全 file diff＋削除の費用を要した
∴ **安く試された賞ではない。実費を払って得た手法** ∴ **★検定済★** と記す
（本日の賞のうち、これが最初の「検定済」。他は悉く「未検定」）。
