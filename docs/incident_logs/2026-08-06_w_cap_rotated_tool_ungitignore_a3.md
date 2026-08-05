# W: CAP_ROTATED 通知が指す道具 (scripts/read_pruned_archive.sh) — 現に引けぬ件 (足軽3号)

断面: HEAD=60c1c8bfb47657a337a854da52948b203aec791a (2026-08-06T02:38:42+0900) / 測時=2026-08-05T17:51:32Z (機械)
発令: karo-second msg_20260806_024648_82cb25b6 (2026-08-06T02:46:48)
提出先: 軍師second (直提出)。PASS まで commit せず。本 report は repo 外 (scratchpad)。

## ⒜ 現況実測

| 項目 | 値 |
|---|---|
| path | `scripts/read_pruned_archive.sh` |
| 存在 (ls) | 存在する (rwxrwxr-x, 2925 bytes, 82 行) |
| sha256 | `85a2251eda52cc95adb7988d91b0545c502ffd4b60440321a758e474274e4f83` |
| `git check-ignore -q scripts/read_pruned_archive.sh` 終了コード | `0` (=無視されておる) |
| `git check-ignore -v` | `.gitignore:7:*	scripts/read_pruned_archive.sh` (Step1 の全除外 `*` に捕捉、個別 whitelist 行は無し) |
| `git status --porcelain --ignored=matching -- scripts/read_pruned_archive.sh` | `!! scripts/read_pruned_archive.sh` |
| `git ls-files scripts/read_pruned_archive.sh` | (空) = tracked ではない |
| HEAD | `60c1c8bfb47657a337a854da52948b203aec791a` (2026-08-06T02:38:42+0900) |

**参照元 2箇所** (`scripts/inbox_write.sh` 内、grep 実測):
- L210: archive 側 (`*_pruned.yaml`) 冒頭に書き込む注釈コメント。
  `# multi-document YAML -- use yaml.safe_load_all(), not safe_load() (see scripts/read_pruned_archive.sh)`
- L245: CAP_ROTATED 通知本文 (受信者へ配送される `content` の一部)。
  `'yaml.safe_load_all() を用いよ (scripts/read_pruned_archive.sh 参照)。'`

両箇所とも同じ 1 file を指す。★当 repo 断面での不在★ (git 管理下に無い) が正しく、「無い」と断定はしない (他 PC ローカルに在る可能性は排除しない。現に third_pc 型の先例 — commander_send_shogun_second.sh — で同型の誤りが一度起きておる、§13 に倣う)。

## ⒝ .gitignore へ足す `!` 行 (起案のみ・.gitignore は不触・委員長裁可待ち)

00E 止血 (commit `6a8be08`) の個別名指し型に倣う。逐語・末尾へ append:

```
!scripts/read_pruned_archive.sh
```

適用前後 (.gitignore を編んでいない・下記は隔離 clone 内での実測値):
- 適用前: 426 行・sha256=`b99f6401d865d51a74ee569559887e3ad1233f48bba1ce9855cab4843383745d`
- 適用後 (隔離 clone 内のみ): 427 行・sha256=`f43168caf9a568b51fab3927a54c5e099bda9b5d28a2849cda90e5d6f703385d`
- ★ライブ repo の .gitignore は本作業を通じて一字も変えていない★ — 実測後 sha256 再確認=`b99f6401...` (不変)。

**注意 (⒟にも関連)**: `!` 行だけでは file は tracked に成らぬ。unignore は「`git add` を通す」だけであり、その後 別途 `git add scripts/read_pruned_archive.sh` + commit を要する。2段階。

## ⒞ 副作用実測 (隔離 clone 差分法)

手順: `git clone --no-hardlinks -q . <isolated-dir>` (本番 repo を一字も編まず、複製側でのみ検証) → 複製側の `.gitignore` へ提案行を追記 → 実測 → 複製削除。

- 適用前 `git ls-files | wc -l` = 620
- 提案行追記後 `git check-ignore -q scripts/read_pruned_archive.sh` 終了コード = `1` (=無視されなく成る、狙い通り)
- **重要な発見**: 新規 clone には元々 `scripts/read_pruned_archive.sh` 自体が存在しない (`ls` → No such file)。★gitignore された file は git 履歴に一度も入っておらぬゆえ、clone しても複製されぬ★ — これは「file が存在しない」ことの直接証拠でもある (他 PC の clone にはそもそも渡っていない)。
- `git add -n scripts/` (file 不在状態) → 出力なし = ★他の file を巻き込まぬ (副作用ゼロ)★。
- 本番の実 file を複製へコピー入れ、`git add -n scripts/read_pruned_archive.sh` を実行 → `add 'scripts/read_pruned_archive.sh'` の 1 件のみ表示。他 file への波及なし。
- 複製削除: `rm -rf` が権限拒否 (harness 判断・destructive op 扱いの模様)。同一 command を再試行せず、複製は scratchpad 配下 (`/tmp/claude-1000/.../scratchpad/isolated_clone_w_readpruned`) に残置のまま。★session 隔離領域・非 repo・非 git-push 対象ゆえ実害なし★だが、削除完了はできていない旨を明記する (完了と書かぬ)。

結論: 提案行の副作用スコープ = 対象 1 file のみ・巻き込み 0件。

## ⒟ この修正が新たに開ける穴

1. **「unignore」と「tracked」の混同**: `!` 行の commit だけを見て「直った」と読む者が出れば、実際には file 内容がまだ commit されておらぬ (2段階目未了) 状態が起こり得る。★止血の commit を「完了」と読むな★ (00E 先例と同型の罠)。
2. **secret 走査 未実施**: 当 repo に secret scanner が一つも無い (00E 先例と同状況)。手動 12-pattern grep は 0 件だが、これは目視の当たりであって専用走査の代替にならない (00E 先例の教訓をそのまま継承)。
3. **参照元コメント (L210) の陳腐化リスク**: `inbox_write.sh` が archive file 冒頭に書き込む `# ... see scripts/read_pruned_archive.sh` は★内容が固定文字列として量産され続ける★。将来この script が rename/移動された場合、過去に書かれた大量の archive file 内コメントは追随せず、古い path を指したまま残る (=新しい phantom canon の芽)。今回の unignore はこの芽を摘まない。
4. **`git add scripts/` の一括実行時の巻き込みは実測上ゼロだが、`git add -A` 等の広い操作は本検証の対象外**。ここでの実測は `scripts/` 配下限定・当該 file 限定であり、他ディレクトリでの類似 whitelist 漏れ (未捜索) まで安全と保証するものではない。

## 一問への回答 (案のみ・裁定はせぬ)

★通知本文が git 外の道具を指す事それ自体をどう扱うが良いか★:
道具が git 外でも通知だけで内容が読める形にする案 = CAP_ROTATED 通知本文 (L245 付近) に、`read_pruned_archive.sh` が不在の場合のフォールバック一文を足す。例: 「本 script が無ければ `python3 -c "import yaml,sys;[print(d) for d in yaml.safe_load_all(open(sys.argv[1]))]" <path>` で代替可」という 1 行併記。これなら unignore の裁可を待たずとも、通知単体で完結する。★案のみ・実装は本工区の範囲外 (inbox_write.sh は書換対象外・別途 dispatch 要)★。

## 母集団 / 判定不能の明示

- 抽出対象は karo-second 発令書が明示した 1 file (`scripts/read_pruned_archive.sh`) のみ。CLAUDE.md 全体を対象とした網羅 grep (W32 相当) は本工区の範囲外。
- 「他 PC ローカルに存在するか」は★判定不能★ (当 repo からは検めようがない・SSH 等での他 PC 実査は本工区の禁則)。

## 禁則順守の申告

- `.gitignore` は一字も編んでいない (提案は隔離 clone 内のみで検証・上記 sha256 で証明)。
- 実装 file (`scripts/inbox_write.sh` / `scripts/read_pruned_archive.sh`) は一字も編んでいない。
- commit / push / stage は行っていない。
- 隔離 clone の削除 1 件が未了 (harness 権限拒否・repo 外・実害なし)。

## 【本工区で己が直した誤り】
無し。

## 【この工区と対に成る他工区】
無し (探した範囲=karo-second 発令書本文・CLAUDE.md Anti-Duplication 節・queue/tasks/ashigaru3.yaml 履歴。同型 dispatch の重複は見当たらず)。
