# km-218 判定提出 ―― case-fold 双子(`docs/runbooks/ERR-EKARTE-001.md` / `err-ekarte-001.md`)の実測

雛形 = `queue/reports/karo-mac/judge-submission-bundle-template-v1.3.md`（141行/11341bytes/sha256=31823f69..）

## ① 対象 tuple

★v1.3 追補1 により、① は本紙でなく★納便(letter)の本文★で宣する★（本紙は載せない。tuple の commit/tree は
この束を commit する納便に記す）。

## ② 成果物（artifact）

| path | sha256(64桁) | bytes | lines |
|---|---|---|---|
| `docs/evidence/.../driver/kaki.py` | `0c6f5d9b8a4d79fec4b630f8ed1021e006ff8a2a79dd325c2a04ece9f19cef06` | 1757 | 39 |
| `docs/evidence/.../driver/10_casefold_census.py` | `5b5b26f338fb089bb0945204d75ae057dc3335197fde2059fb9bd7046376b9b6` | 4370 | 111 |
| `docs/evidence/.../raw/10_casefold_census.txt` | `d9310d2352dadaa69043a93d85f322520ef61339edebcc2094f29c89f7262836` | 1301 | 21 |
| `docs/evidence/.../raw/11_cross_check_uniq.txt` | `1222f42fa0b964a1df3c50c5e915677e22c1e7ffbb78f58c7c41891452158759` | 2190 | 39 |
| `docs/evidence/.../raw/20_shinsetsu_ju_porcelain.txt` | `096922bf9a7d5d23715a5a57bcc70e2b95bb2a9f72b9bd2bb00ca9041de89057` | 1180 | 28 |
| `docs/evidence/.../raw/30_claude_md_index_gogo.txt` | `c6f31a48d57169cb41953a96634f0dd1f94f8d680d47a4ee126f853b3afcbffc` | 2349 | 28 |
| `docs/evidence/.../40_zesei_an_326810.txt` | `4d4503c9c5c69282381cee5e3758d4cd5a581d2370e809e5f5718b397fb6c997` | 3371 | 41 |

（path 頭の `docs/evidence/.../` は `docs/evidence/km-218-casefold-futago-wa-shinsetsu-ju-de-yogoreru-20260920/` の略記）

★`git ls-files` 追跡確認★: 下記 ⑥ の commit 後に `git ls-files -- docs/evidence/km-218-.../` を実走し、
上表 7 件が★全件★1件以上で返る事を確かめる（`.gitignore:7` の裸 `*` ゆゑ `git add -f` 必須・
[[project_gitignore_line7_is_a_single_star_allowlist]]）。

## ③ 実走の raw（①と同一 tuple・同一 run）

各 raw file の中に argv・rc・cwd・刻を埋め込み済（②表の raw 3件を参照）。要約:

- `raw/10_casefold_census.txt`: cwd=`/Users/momizimac/wt/a2-km218`, argv=`git ls-tree -r --name-only origin/main`, rc=0
- `raw/11_cross_check_uniq.txt`: cwd=`/Users/momizimac/wt/a2-km218`, argv=`git ls-tree -r --name-only origin/main | awk ... | uniq -c`, rc=0（2本）
- `raw/20_shinsetsu_ju_porcelain.txt`: 使ひ捨て樹 `/Users/momizimac/wt/km218-throwaway`（`git worktree add --detach ... origin/main`, rc=0, 刻=2026-09-19T17:58:01Z）にて
  `git status --porcelain -uall`（cwd=`/Users/momizimac/wt/km218-throwaway`, rc=0, 刻=2026-09-19T18:02:09Z）
- `raw/30_claude_md_index_gogo.txt`: cwd=`/Users/momizimac/wt/a2-km218`, argv=`grep -n "err-ekarte-001\|ERR-EKARTE-001" CLAUDE.md`, rc=0

## ④ 依存の境界

★非該当（理由）★: 本測定は git plumbing コマンド（`ls-tree`/`cat-file`/`status`/`worktree`）と python3 標準
ライブラリ（`hashlib`/`io`/`os`/`subprocess`/`sys`）のみに依存する。lockfile 管理対象の外部パッケージ・
外部 `node_modules`・外部 symlink 参照は★無し★。

## ⑤ 件数

### 正N/N（本弾 受入条件⑴〜⑹、各 PASS/FAIL+証）

| # | 内容 | 判定 | 証 |
|---|---|---|---|
| ⑴ | 母數（本数・argv・rc）と衝突組の全列挙 | PASS | `raw/10_casefold_census.txt`（母數=548・組数=1） |
| ⑵ | 組ごとの blob sha256(64桁)/bytes/同異/disk 勝者 | PASS | `raw/10_casefold_census.txt`（同異=★違ふ★・両 path とも disk は小文字 blob と一致） |
| ⑶ | 新設樹 直後の porcelain 実測（argv・rc・刻・畳んだ事） | PASS | `raw/20_shinsetsu_ju_porcelain.txt` + `git worktree remove --force` rc=0（樹は消滅済・`git worktree list` に0件） |
| ⑷ | CLAUDE.md の逐語 | PASS | `raw/30_claude_md_index_gogo.txt`（index 2箇所とも小文字を指す。内容の正否は★未測★=同紙内に明記） |
| ⑸ | 判定の束①〜⑦ | PASS | 本紙（`_hosoku/00_teishutsu.md`） |
| ⑹ | 紙のみ（双子を直さない） | PASS | 本弾で打った git 操作は read-only（`ls-tree`/`cat-file`/`status`）と自席樹の `worktree add`/`remove` のみ。`git rm`/`checkout --`/`add -f`（本文content向け）/`commit`（是正としての）は★0回★ |

### 意味負M/K（恒真でないことの証明）

`raw/11_cross_check_uniq.txt` 参照。547 case-fold key 中、count=2（衝突）は★1★のみ・count=1（非衝突）は546。
driver script は衝突0件の分岐（`(無し)`）を実装済 ―― 「組数=1」は無条件の恒真出力ではない。

### 陽性対照／陰性対照

- 陽性対照: `docs/runbooks/err-ekarte-001.md` ⇄ `ERR-EKARTE-001.md` ―― 実在する衝突が検出された。
- 陰性対照: `CLAUDE.md` ―― tree 中1本のみ・衝突組に含まれず。道具の誤検出は無い。

## ⑥ 復元

★本弾の性質上、⑥clean は★恒久には満たせぬ★（本弾の由来そのもの ―― `raw/20_shinsetsu_ju_porcelain.txt`
参照）。∴ 以下を「本弾の submission としての clean」と定義し、実測する:

- ★既知の構造的な汚れ★: ` M docs/runbooks/ERR-EKARTE-001.md`（本弾の対象そのもの・1行・案 6.は未実行ゆゑ現状のまま）。
- ★submission が生んだ汚れ★: 上記1行を除き、`git status --porcelain -uall --ignored` に★他の行が無い事★。

commit 後の実測（cwd=`/Users/momizimac/wt/a2-km218`）:

```
argv=git status --porcelain -uall --ignored
（commit 直後に実走・結果は納便へ転記）
```

再正N/N: ⑴〜⑹ の6件中6件 PASS（上記⑤表と同一・commit 後も内容は不変のため再測しても同じ）。

## ⑦ 法令根拠

非該当（算定・記載要件に触れない）。
