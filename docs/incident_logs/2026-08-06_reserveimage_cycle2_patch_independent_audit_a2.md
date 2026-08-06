# 2026-08-06 Reservation-Imaging Cycle2 Patch — 独立 read-only 監査 (足軽2号)

- 発注: 家老second msg_20260806_084137_85437ef9 (2026-08-06T08:41:37+0900)
- 実施: 足軽2号 (ashigaru2)
- 任: 家老secondの実測(①〜④)が誤っておらぬかを己の手で独立に測る。書込・apply(実適用)・新規worktree作成は一切なし。
- 提出報告: msg_20260806_084849_3e2e904e (2026-08-06T08:48:49+0900、家老secondのみ宛)
- 結論(先出し): 四件とも反証至らず。ただし②③④に精度差分あり(下記詳細)。

## 冒頭・但し書き/境/未測

- 書込・apply(実適用)・新規worktree 一切なし。実行したのは `--check`(非破壊)・`status --porcelain`・`show`(read-only抽出)・grep・diff のみ。
- hakudokai-dev の worktree群(`/mnt/c/Projects/hakudokai-dev*`)へは一字も書いておらぬ。findで所在を列挙したのみ(read-only)。
- 「patchの中身(ロジック)が正しいか」は未測。本監査は apply機序(件数/rc/母集団)のみのscope。gate2-4 test suite の pass/fail も未測。
- rc は悉く pipe を通さず、直後 `; rc=$?` で受けた(`cmd >/dev/null 2>&1; rc=$?` の形)。

## 己で取った値 (貴殿の値は写しておらぬ)

- path=`/home/hakudokai/hermes-departments/honbucho/reports/reserveimage-cycle2-gate2-4-handoff-20260806.patch`
- 己測: `ls -la` → 39313 bytes / `wc -l` → 932行 / `sha256sum`(己で実行)=`2542891ace734a458637fc634cf9712283faa1b25639c8d92de95ba7d5280835`
- 一致/不一致=**完全一致**(path/bytes/行数/sha256 の四点とも)

## ①diff --git 件数=6 —— 一致 (己測も6)

`grep -c '^diff --git'` で己測=6。内訳(`grep -n` で確認)= booking.py(L1) / appointment_service.py(L13) / booking_service.py(L60) / test_phase2_2_booking.py(L312) / booking_concurrency_root.py(L456・新規) / test_booking_concurrency_root_migration.py(L763・新規)。反証手掛かり無し。

## ②/tmp/resimg-cycle2-impl-20260806 の `git apply --check --reverse` rc=0 —— 一致 (己測もrc=0)

cd先で直接実行、rc=0確認。併せて申告=当職は追加で「worktreeの実diffとpatch本文を直接行diffで比べる」別法も試みたが、これは**己の手法の誤り**で偽陽性を出した——`git diff` の出力順(alphabetical: api→db→services→services→tests→tests)がpatchの記載順(api→services→services→tests→db→tests)と異なるだけで、`git add -N . && git diff` 後の並べ替え前diffを素朴比較したため大差分に見えた。ファイル集合(6件)を照合すると完全一致。`apply --check --reverse` は文脈行照合で判定する為、この確認だけで十分堅牢(④で示す通り、内容が僅かでも違えばreverseもrc≠0になる)——己の粗い二次確認法の方が誤っていたと分かり次第、破棄せず本便に明記する(直した誤りは無いが、試みて誤った手法を隠さぬ)。impl worktree は probe前後で `status --porcelain` 完全一致(4 M+2 ??)を確認、書込痕跡なし。

## ③清きbaseに当たる rc=0 —— 一致 (己測もrc=0)、二重の独立手法で確認

(a) 直接法: 母repo `/tmp/resimg-stage1-runtime-20260806` の HEAD=`7d463edae84c704edabbd9da5465078dc62e55b1`(=base指定値と一致)・`status --porcelain` 0行(清潔)を確認の上、その場で `git apply --check -p1` → rc=0。--check後も porcelain 0行のまま(非破壊確認)。

(b) 貴殿と同型の手法: 4個の既存file(migrationとtest_migration以外)を己のscratchpadへ `git show HEAD:path` で read-only抽出(mkdir -p + git show、母repoへの書込なし)。新規2fileは `git cat-file -e HEAD:path` → rc=128(fatal: does not exist in 'HEAD')で「baseに無い」ことも確認。その隔離scratchpad(.git無し)にて `git apply --check --unsafe-paths -p1` → rc=0。抽出物4fileのみ、--check後も4fileのまま(新規file生成なし=非破壊確認)。

併せて一つ前提を検めた= 「base_commit=7d463edaeは実在の履歴か、それとも本監査用に用意された孤立repoの値か」——`git remote -v` で `/tmp/resimg-stage1-runtime-20260806` と `/tmp/resimg-cycle2-impl-20260806` の両方が origin=`git@github.com:hakudoukai/hakudokai-dev.git`(blob:none partial clone)を指すことを確認。かつ `git log -1 7d463edae…` → author=ashigaru4-stage1・"fix(reservation-cycle1): GREEN — align web booking to staff appointments/history contract"(2026-08-06 02:05:00)。孤立値ではなく実dev repoの実履歴と確認(read-onlyのlog/remote参照のみ)。

## ④/tmp/resimg-cycle2-base-audit rc=1 —— 大枠は一致するが、機序に精度差分あり (これが本監査の唯一の実質的な上積み)

`status --porcelain`=1行のみ( M backend/tests/web_reservation/test_phase2_2_booking.py)を確認、これはpatchの対象6fileの一つ。`git apply --check -p1` を再現し同じ error(`patch failed: …py:6 / patch does not apply`)を得た。

ここで止めず、この1fileのdirty diffの中身とpatch本文の同fileへの追加内容を突き合わせた:

- patch側hunk(144行) vs worktree実diff(116行)を index行を除いてdiff。
- 差分=**2箇所のみ**: (1) import行1本 `from backend.db.migrations.booking_concurrency_root import apply_booking_concurrency_root` がpatch側にのみ在る。(2) 新規test関数 `test_durable_idempotency_key_and_slot_claims_after_migration`(22行・migration適用後の冪等性検証)がpatch側にのみ在る。
- 残り約92行(fixture `_open_file_db`・barrier系の真の2接続競合test等)は**バイト完全一致**。

結論の精度化: 「rc=1はpatchの瑕でなく、当該worktreeが単に無関係な理由でdirty」という粗い読みだと不正確。実際は**当該worktreeのdirtyな中身が、patchが加えようとしている同一Cycle2追加分の"先行・部分版"(migration統合のimportと最終testを欠く版)そのもの**であった。∴ rc=1の直接因は「同じ追加を、より浅い版で既に持っている状態にpatchを当てようとして文脈行(L6import・L330台のtest本体末尾)が食い違った」こと。これは貴殿の①⑤(零に理由/同じ行に一致不一致)には反しないが、②で申告した通り"内容が僅かでも違えばrc≠0になる"実例そのものであり、④の「patchの瑕でない」という主張は**支持されるが、機序の説明としては本便の方がより精密**。

## 総括 (一致・不一致を同じ行に)

①一致(件数6=6) ②一致(rc=0=0、ただし当職の粗い二次検証法自体に誤りがあり自己申告のうえ破棄) ③一致(rc=0=0、二重手法+base_commitの実履歴照合まで実施) ④大枠一致(rc=1でpatch瑕でないという結論は支持)・機序は不一致(「無関係な理由でdirty」ではなく「同一追加の部分版が既に居る」)——反証には至らず、精度の上積みのみ。

## 対に成る他工区

無し(探した範囲=queue/inbox/ashigaru2.yaml・queue/tasks/ashigaru2.yaml。同型の独立監査発注は他レーンには見当たらず)。

## 本工区で己が直した誤り

無し(貴殿の四点はいずれも維持。但し②の二次検証で己が一時的に誤った手法(diff順序を揃えぬ素朴比較)を用いた事は上記②内で申告済・本文を破棄せず記録)。

## 附記 (2026-08-06T09:xx・家老second指摘への回答・本追記のみ後日追加)

家老secondより「貴殿は hakudokai-dev の worktree群を `/mnt/c/Projects/hakudokai-dev*` と書いたが、家老secondの実測では `/tmp/resimg-*` 配下であった。食い違い」との指摘を受け、当PC上での hakudokai-dev clone/worktree の総数を read-only で再列挙した (詳細は本便提出時の追伸メッセージ参照)。結論: **両方とも実在し、食い違いではなく別々の worktree 集合**である。当職の本文冒頭「hakudokai-dev の worktree群(`/mnt/c/Projects/hakudokai-dev*`)へは一字も書いておらぬ」という記述自体は、当職が read-only 確認のため `find` で列挙した対象を指しており誤りではないが、本監査の実対象(patch適用先)は `/tmp/resimg-*` 配下であった点は明記が不足していた。
