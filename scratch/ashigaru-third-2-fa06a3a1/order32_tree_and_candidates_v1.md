# order32 樹の始末と 次弾候補 2 つ

as_of: 2026-09-07 14:12 JST / 席=ashigaru-third-2 / 令=order32
raw: scratch/ashigaru-third-2-fa06a3a1/order32_worktree_raw.txt
三択語: 測つた / 測つて居らぬ / 測れぬ。DB 0・走行 0・push 0・prune 0。

## §1 tip が local ref に在る事 (remove の前に測つた)
- `git rev-parse a2-fa06a3a1-sync-rewrite-v2` → `d4760d0556a4da05351c5dab361862a8b056a7bc`
- `git branch --contains d4760d055` → `+ a2-fa06a3a1-sync-rewrite-v2` (1 行 = 枝 1 本)
- ∴ 樹を畳んでも commit は枝に残る。

## §2 remove (自席樹 1 本のみ)
- `git worktree remove /home/hakudoukai/a2/wt-fa06a3a1-o31` rc=0
- remove 後の `git worktree list` は **5 行** (1 行 = 登録された樹 1 本)。o31 の行は★無い★。
- 残る当席の樹は `/home/hakudoukai/a2/wt-964a06d0-d3adf65b` の 1 本のみ (D 樹・不触)。
- remove 後に再測: `git rev-parse a2-fa06a3a1-sync-rewrite-v2` → 同じ `d4760d05…` (失はれて居らぬ)。
- `git worktree prune` は打つて居らぬ。共有 checkout (`/mnt/c/DentalBI` 本樹) への操作は 0。

## §3 次弾の候補 2 つ
| | ⓐ #2 CI の upsert に鍵を付す | ⓑ 15,271 の未説明を切り分ける |
|---|---|---|
| 目的 | `.github/workflows/sync-source-cache.yml` L169-170 の POST に `on_conflict=file_path` を足し、#1 と同じ鍵にする | source_code_cache 20,903 行のうち git で説明できぬ 15,271 の帰属 (#1 か #2 か別 root か) を絞る |
| 讀取のみか | ★否★ (patch を作る=file 書込)。但し走行は `--check`/lint まで、CI 起動 0・push 0 | ★是★ (SELECT 文を書くのみ・実行 0) |
| 所要 (分) | 30 (patch + 差分の紙) | 40 (SELECT 3〜5 本 + 読み方の紙) |
| 前提 | ★総監督裁 283660 の GO が要る★ (CI は当席の持ち場でない・#2 は order31 で触らず上申した) | ★SELECT を打つ者が要る★ (当席に DB の器は 0)。打ち手は総監督か家老 |
| 出る物 | patch (対象 1 file)・紙 ≤40 行 | SELECT 案・当て方の紙 ≤60 行 |
| 危険 | CI の upsert 挙動が変はる。誤れば全 file の書込が止まる ⇒ 裁の前に走らせぬ | 無し (讀取案のみ)。但し答は打ち手の手に在る |

- 当席の見立て: ⓑ は前提が軽く、ⓐ は裁が要る。孰れを先にするかは家老の裁を仰ぐ。

## §4 開示
1. ★総監督 seq284320 を直読せよ の令に応へられて居らぬ★。当席に pc_handshake を讀む器が無い
   (scripts/ ~/.local/bin を探して 0 本・他役職の watcher を借りるは持ち場違ひゆゑ打たず)。
   本文の代送、または当席で使へる讀取器の配備を請ふ (msg_20260907_140753_e4dc0df3 で既に上げた)。
2. 前樹 `/home/hakudoukai/a2/wt-964a06d0-d3adf65b` は軍師 D 判定待ちの裁ゆゑ不触・存置。
3. order31 の產物は樹を畳んだ後も repo 内 scratch に在る (紙 v2 e783d38e30bacf3d 75 行・
   patch v2 b99e75d8d356ec46 554 行・raw 33030a60599f5831 / 5d8f2f977b8590ee)。
