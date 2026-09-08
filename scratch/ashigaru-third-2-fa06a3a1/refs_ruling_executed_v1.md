# order19 執行録 v1 ── A ref を origin へ護り、local ref 2 本を消した記録
as_of: 2026-09-07T06:18:26+09:00
席: ashigaru-third-2 / 令: subtask_thirdpc_a2_refs_ruling_hs_bbf21d4e_push_a_keep_delete_b_001 (order_in_seat 19)
樹: /mnt/c/DentalBI (共有作業樹・当席は讀取と本令の 3 動詞のみ)
裁の逐語(令 parent_ruling より写す): 「総監督 hs_bbf21d4e (281850 受・裁): A=残す→origin へ枝 karo-third/a2-14c8ec72-fixed として push(可逆)し其の後 local ref を消してよい / B=消す(裁材紙 c763e3534a2997a8 に sha 記録済=可逆)」
raw: raw_order19/push_20260907.log sha16=35b1ff668ea87925 / lsremote_20260907.log sha16=200e4a207dd263b4 / delete_20260907.log sha16=517e48baaeb35922

## 節一 前測(削除の前に再刷・床(27))
- A a2-14c8ec72-fixed = 80814278bbbeb0d260b5939ed4f5b7b824d2bade
  件名 逐語: 14c8ec72: reject identity query on handover main template detail route before DB read
- B a2-fa06a3a1-collect-fixed = 4b9912e6c3d69cae6e231b628678e3db4de3a75c
- cat-file -e 両 commit exit=0 ⇒ 両者は 現に在る
- local branch 総数 = 74 本 (1 本 = git branch --list の 1 行 = local branch 1 本)

## 節二 push(当該 1 refspec のみ)
- 逐語 cmd: push origin refs/heads/a2-14c8ec72-fixed:refs/heads/karo-third/a2-14c8ec72-fixed
- exit = 0
- 逐語(尾 2 行): To https://github.com/hakudoukai/hakudokai-dev.git
  ` * [new branch]          a2-14c8ec72-fixed -> karo-third/a2-14c8ec72-fixed`
- 認証 prompt は 現に無い(credential.helper 設定 0 件・GIT_TERMINAL_PROMPT=0・URL 内 credential 0)

### 節二の副作用 ── 令に無い外部書込が hook 経由で起きた(開示)
当樹には pre-push hook が在り、push が之を発火させた。当席が命ぜられたのは push 1 本のみで、下記は当席が書いた物ではないが、当席の push を経て起きた事である。
- 逐語(hook 出力): `[dup-check] PASS: 新規path 2件を検査、二重実装0件` ★此の PASS は hook の語であり当席の判定語に非ず★
- 逐語: `[pre-push] source_code_cache sync starting...` / `-- Changed-only mode: 4 of 4148 files changed`
- 逐語: `-- TRANSIENT (HTTPStatusError): retry 1/2 in 1s`
- 逐語: `-- Upserted: 4, Skipped: 0, Errors: 0, Commit: ef426ea6c` (1 = 外部 table の行 1 行)
- 逐語: `-- WARNING: stale cleanup failed: Server error '500 Internal Server Error'`(url は supabase REST の source_code_cache)
- 逐語: `-- WARNING: count check failed: The read operation timed out`
∴ 外部 table への upsert 4 行と警告 2 本は 現に在る。当席は之を止める術を令の内に持たぬ(--no-verify は令の外ゆゑ打つて居らぬ)。
∴ 当席が先に「2 分半返らぬ」と観た吊りの因は網に非ず、此の hook(4148 file 走査+retry+timeout)であつた ── 之は測つた。

## 節三 ls-remote(令 step3・削除の前提)
- 逐語: `80814278bbbeb0d260b5939ed4f5b7b824d2bade	refs/heads/karo-third/a2-14c8ec72-fixed` / exit=0
- 節一の A と同一 sha ⇒ 前提は満たされた

## 節四 削除(前提の後にのみ打つた)
- `git branch -D a2-14c8ec72-fixed` exit=0 / 逐語 `Deleted branch a2-14c8ec72-fixed (was 80814278b).`
- `git branch -D a2-fa06a3a1-collect-fixed` exit=0 / 逐語 `Deleted branch a2-fa06a3a1-collect-fixed (was 4b9912e6c).`
- 後: `rev-parse --verify --quiet` 両名 exit=1 ⇒ local ref は 現に無い
- local branch 総数 = 72 本(前 74 本・減 2 本)

## 節五 削除後の到達性(1 本 = ref 1 本)
- A(80814278b) を含む ref = 1 本: `refs/remotes/origin/karo-third/a2-14c8ec72-fixed`
- B(4b9912e6c) を含む ref = 0 本
- object 自体は cat-file -e で A/B とも exit=0 ⇒ 現に在る(ref から辿れぬだけ)
- B の patch/diff 形の退避は order17 紙 c763e3534a2997a8 の測りで 0 件、当令でも新設して居らぬ ⇒ B の中身を file から起こす材は sha の記録のみ

## 節六 令の禁(遵守の実測)
--force 0 / push は当該 1 refspec のみ(他 refspec 0) / main・X・drs 枝への push 0 / worktree 0 / checkout 0 / commit 0 / D 樹 wt-964a06d0 触 0 / secret 0 字

## 節七 三択語の結び
- push の着 = 測つた(exit0 と ls-remote 一致の二重)
- local ref 2 本の不在 = 測つた
- B の object が今後も残るか = 測つて居らぬ(gc の時期は当席の測りの外)
- hook が外部 table へ書いた 4 行の中身 = 測れぬ(当席に其の讀取の権無し)
