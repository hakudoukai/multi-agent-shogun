# km-225 提出 ―― ★双子の runbook が雛形⑥ を構造的に塞いで居る★

提出者: 家老mac (karo-mac) ／ 刻: 2026-09-20T06:01:30+0900（各測りの刻は raw の冠に在る ―― 本紙は raw の後に書いた）
雛形: `queue/reports/karo-mac/judge-submission-bundle-template-v1.3.md`（11341B / sha256 頭16桁 `31823f69977a358c`）
上申: 委員長へ seq341096(1/3) / seq341097(2/3) / seq341098(3/3)・悉く `--parent-seq 340068`

## ★先に當職の落度を二つ述べる★

⑴ ★當職の初手の見立ては逆であつた★。「大文字側 `docs/runbooks/ERR-EKARTE-001.md` が
   disk と食ひ違ふ」と見たが、實測は ★樹ごとに入替はる★。共有樹では disk = 大文字側の
   blob `e6de627b…` ゆゑ ★小文字側★ が ` M` と出、他の三樹では逆である。
   ∴ 當職は「どちらが汚れて居るか」を測らずに口にした。測つて向きを正した（raw/10）。

⑵ ★當職は配下へ「⑥ clean = porcelain が空」を條として渡し續けた★。
   之は此の repo では ★構造上 満たせぬ★ 條であり、專任1 の km-221 ⑥ の porcelain 1行も、
   軍師mac が km-219 へ求めた ⑥clean_raw（seq341082）も、★席の落度ではない★。
   命に穴が在つたのは當職である。

## ■① 対象 tuple

```
ref名  = karo-mac/km-225-futago-no-runbook-ga-mon6-wo-fusagu-20260920
親     = 6bde7170ce574090a6139ba2dfe3aa4cb6db8634 (= origin/main ―― ★1弾1枝★で切つた)
commit = ★本紙を彫つた後に決まる★ ∴ 納め便に40桁で記す（紙は己を含む commit を書けぬ）
tree   = 同上
検算   = git rev-parse <ref> が commit と一致する事を納め便で示す（祖先を出さぬ）
```

## ■② 成果物

紙・raw の path / sha256 / bytes / lines は ★臺帳 `MANIFEST.txt` に載る★。
★本紙は己の sha256 を書けぬ★ ゆゑ、本紙の sha256 / bytes / lines は納め便に記す。

- `docs/evidence/karo-mac_futago-no-runbook-ga-mon6-wo-fusagu-20260920/01_teishutsu.md`（本紙）
- 同上 `raw/10_futago_sokutei.txt` ―― 双子の骨（argv1〜7・各 rc）
- 同上 `raw/20_yomikaeshi_seq341096.txt` / `…341097.txt` / `…341098.txt` ―― 上申三通の讀み返し
- 同上 `raw/30_mon6_clean_sokutei.txt` ―― ★雛形⑥ clean の實測★
- 同上 `raw/31_shinju_de_saigen_suru.txt` ―― ★白紙の新樹で再現する★
- 同上 `raw/32_taishou_to_bogen.txt` ―― 陽性/陰性対照 と 母数
- 器は作つて居らぬ（測るのみ・code 変更 0）

## ■③ 実走の raw

各 raw の冠に ★刻 / cwd / HEAD / argv を逐語 / rc★ を焼いて在る。
二射（共有樹 と 新樹）は ★別 file に分けた★（10 と 31）。
空の出力は ★「出力は空である」と非空白字で1行書いた★（裁310228⑶・seq339959 の形）。

## ■④ 依存の境界

lockfile = ★N/A（本弾は測るのみ・依存を引く code を一行も書いて居らぬ）★
外部 node_modules / 外部 symlink 参照 = ★無し★（歩いたのは git と coreutils と /opt/homebrew/bin/python3 のみ）

## ■⑤ 件数

```
正      = 4/4  ―― 四つの樹で「必ず1行出る」を實測した
            ⑴ /Users/momizimac/multi-agent-shogun（共有樹・disk=e6de627b… ∴ 小文字側が M）
            ⑵ /Users/momizimac/wt/karo-km223  （disk=de00cbd9… ∴ 大文字側が M）
            ⑶ /Users/momizimac/wt/a1-km221    （disk=de00cbd9… ∴ 大文字側が M）
            ⑷ /Users/momizimac/wt/karo-km225  （本弾の樹・disk=de00cbd9… ∴ 大文字側が M）
★意味負★ = 391/425 ―― 全 ref を歩き、★大文字側 path を持つ ref は 391 本・持たぬ 34 本★。
            ∴ 「全ての ref が双子を持つ」は ★偽★ であり、本疵は恒真ではない。
            ★母数 425 の内 1 本は本弾の枝そのもの★（器が己を数へて居る事を宣す。
             測る前の母数は 424 / 390 であつた ―― 差 1 は當職が切つた枝である）。
陽性対照 = git status --porcelain -uall -- <双子の二名> → 1行（raw/32 argv1・★在る物★）
陰性対照 = git status --porcelain -uall -- docs/error-design-medical.md → 0行（raw/32 argv2）
            ＋ 同 path は ls-files に在る（argv3）∴ 「追跡外ゆゑ黙つた」のではない
```

## ■⑥ 復元 と clean

```
復元sha = ★N/A（code 変更が無い ―― 器を一本も作らず、追跡 file を一本も書き替へて居らぬ）★
再正    = ★N/A（同上）★
clean   = ★★零に成らぬ ―― 構造上 満たせぬ★★（raw/30 と raw/31 で實測）
   git status --porcelain -uall           → rc=0 / ★1行★ / ` M docs/runbooks/ERR-EKARTE-001.md`
   git status --porcelain -uall --ignored → rc=0 / ★6行★（上の1行 ＋ 本束の未追跡 5本が `!!`）
   ※ 当 repo の .gitignore 行7 は裸の `*` ゆゑ 追跡外は -uall に出ず --ignored にのみ出る。
     ∴ ★片方だけを見るのは偽の clean★ である（両方の行数を上に書いた）。
```

### ★因（測つた物のみ）★

```
git は ★二つの名を別 entry として索く★:
  100644 e6de627bd62eb9a4b417155f40748390f49369fe 0  docs/runbooks/ERR-EKARTE-001.md   (2596B / 79行)
  100644 de00cbd99d9909f4a923041ae17f0d2cbb587668 0  docs/runbooks/err-ekarte-001.md   (3471B / 67行)
macOS の fs は case 無差別 ∴ 両名は ★一つの inode★ に解け、實の dirent は
  小文字 `err-ekarte-001.md` ★一本のみ★（python の os.listdir で確かめた・raw/10）。
∴ disk の中身は必ず ★二 blob の一方★ と一致し、★他方が必ず " M" と出る★。
どの名が出るかは樹ごとに入替はる（disk の中身が違ふ故）。
★零にする手は無い★ ―― 双子の一方を index から落とさぬ限り。

★checkout 自身が汚す★（raw/31）: origin/main から白紙の detached 樹を切り、一指も触れず
porcelain を見たら ★1行出た★。因は書き順 ―― index は `ERR-`(0x45) が `err-`(0x65) より前ゆゑ
大文字側の中身を先に書き、小文字側の中身が ★後から同じ inode を上書きする★。
∴ 「席が汚した」ではなく ★此の repo は汚れて生まれる★。
```

## ■⑦ 法令根拠

N/A（本弾は git の索引と fs の case 取扱ひの測りであり、算定・記載要件に触れぬ）

## ★請裁（委員長へ・seq341096/341097/341098）★

㋐ 勝者はどちらか ―― `docs/runbooks/ERR-EKARTE-001.md`（2596B/79行）か
   `docs/runbooks/err-ekarte-001.md`（3471B/67行）か。
   ※ CLAUDE.md の索引は ★小文字★ を指して居る（`docs/runbooks/err-ekarte-001.md`）。
㋑ 双子の安全順（⑴`git rm --cached <loser>` ⑵`git checkout -- <winner>` ⑶verify
   ⑷`git add -f` + `git commit --only`）で當職が直して可か。
★許可が下りる迄 直さぬ★ ―― 正本 link に触れる故 変更統制と見た。素の `git rm` は踏まぬ。

## ★併せて上へ申す事★

⑴ 專任1 の km-221 ⑥ porcelain 1行 は ★落度に非ず★（本疵である）。
⑵ 軍師mac の km-219 REVISE ⑥clean_raw（seq341082）は ★席が零を出せぬ條★ である。
   席3 へは「⑥ は零ではなく ★1行（双子の疵・構造）★ と實測で書け」と渡す。
⑶ 雛形 v1.3 の ⑥「clean 確認 = git status --porcelain -uall が空」は、当 repo では
   ★満たせぬ欄★ である。雛形 条2 の言ふ「★此の欄が埋まらない構造に在る★」の形ゆゑ、
   力で直さず上げた。
