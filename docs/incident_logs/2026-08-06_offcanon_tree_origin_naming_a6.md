# 別木4箇所のorigin列挙・呼び名の確定 (足軽6号、2026-08-06・将軍second⑹直命)

★★読取のみ(`git remote -v`実行のみ)。systemctl操作・symlink・unit編集・checkout操作は一切なし。
③姉妹clone(/home/hakudokai/multi-agent-shogun)は下命どおり★remote確認も含め一切不触★
(directory listingすら行っていない)。★★測時=2026-08-06T03:07:17+0900(date -Iseconds実行結果)。
HEAD=887235bbb5acecf4f8edfcbe1aa0145b04d58d49(git rev-parse HEAD実行結果)。

## 4箇所・origin実測 (命令+出力そのまま)

### ①`/home/hakudokai/projects/multi-agent-shogun`(当repo)

$ git remote -v
origin	git@github.com:hakudoukai/multi-agent-shogun.git (fetch)
origin	git@github.com:hakudoukai/multi-agent-shogun.git (push)

### ②`/home/hakudokai/projects/multi-agent-shogun-newbuild`

$ git remote -v
origin	git@github.com:hakudoukai/multi-agent-shogun-newbuild.git (fetch)
origin	git@github.com:hakudoukai/multi-agent-shogun-newbuild.git (push)
upstream	https://github.com/yohey-w/multi-agent-shogun.git (fetch)
upstream	https://github.com/yohey-w/multi-agent-shogun.git (push)

### ③`/home/hakudokai/multi-agent-shogun`(姉妹clone)

★下命により不触★=directory listing・`git remote -v`いずれも実行していない。対象外として明記のみ。

### ④`/home/hakudokai/scripts`(当職が発見した第三のtree)

$ git remote -v
fatal: not a git repository (or any of the parent directories): .git

**∴ ④はgit repositoryそのものではない(単なるplain directory)。「別origin」という問い自体が
④には適用されない——originを持つ/持たぬの前に、★repoか否か★という一段手前の分岐が要る。**

## 呼び名の確定 (将軍second殿の裁定「列挙は正しく、括りが誤り」を受けて)

- **①と②**=★origin URLが別(`multi-agent-shogun.git` vs `multi-agent-shogun-newbuild.git`)★。
  ②は★別repo★であり、当repoの「古い checkout」ではない。★正しい呼び名=「二つの別repoが分岐し、
  P0根治が一方(①)にのみ入っている」★(将軍second殿⑵の裁定と当職実測が完全一致)。
- **③**=当職は不触ゆえorigin確認していないが、下命本文に「姉妹clone・読取すら不可」と
  既に明記されており、②(newbuild)とは★別件★(混同禁、と将軍second殿⑺で既述)。
- **④**=git repositoryではない単なるdirectory。「別repoか同一repoの古い版か」という
  二択自体が適用されぬ★第三の形★(repoの外の、独立した実行ファイル置き場)。

## 【本工区で己が直した誤り】

初稿で④に対しても「origin URLを確認」と書きかけたが、実際に`git remote -v`を実行した所
「not a git repository」と返り、④がそもそもgit管理下にない事に気付いた。「別origin」を
問う前提(=そもそもrepoである事)を検めずに進めかけた誤りを、実行結果を見て訂正した。

## ★母集団漏れの自己申告★

1. ②newbuildのupstream(`yohey-w/multi-agent-shogun.git`)が実際にfork元として機能しているか
   (fetchされているか等)までは検証していない(originの文字列を実測したのみ)。
2. ④の内部に別途git管理下のsubdirectoryが存在するか(例=`~/scripts/.git`は無いが
   `~/scripts/some_subdir/.git`はあるか等)は確認していない。

## 監査体制

★暫定二者制(軍師+Gemini)。Codex leg停止中(2026-07-21事案)★。

以上、別木4箇所origin列挙・呼び名確定への応答。③は完全不触、④はgit外と判明。
