# 案⑵-乙 ―― 除いた四本の宣(裁 seq329271)

刻= 2026-09-17 23:18:51 / 歩き根= docs/evidence / 器= os.walk(followlinks=False) + islink除 + isfile
親= origin/main 82f23b429a03b88c504cb64917ff37647c07e0a5

## 数

| 区 | 本 | byte |
|---|---:|---:|
| 三束の全 | 182 | 4,967,052 |
| 載せた(乙) | 178 | 2,489,887 |
| 除いた | 4 | 2,477,165 |

## 除いた四本

| path | bytes | sha256 | 臺帳に宣有 |
|---|---:|---|---|
| docs/evidence/ashigaru-mac-2_km-117-v5-wo-240-hashiri-ni-kakeyo-20260917/driver/__pycache__/99_shimai.cpython-314.pyc | 9,498 | a96e78187f4fc675c6c1de1057ff869d0dcf13d157e83787c183cfbbce3a96cc | 無 |
| docs/evidence/ashigaru-mac-2_km-117-v5-wo-240-hashiri-ni-kakeyo-20260917/driver/__pycache__/kaki.cpython-314.pyc | 2,142 | 84ba3aa9165b6c33a1842b904f8d6e8ab7642e023b00ac6645e3126ec2816cac | 有 |
| docs/evidence/ashigaru-mac-2_km-117-v5-wo-240-hashiri-ni-kakeyo-20260917/raw/31_daini_for.tsv | 1,160,233 | 9eae5b4b4f18ec379761e02d58bcf1a9aa22a350adab378171fa3542104dd67b | 有 |
| docs/evidence/ashigaru-mac-2_km-122-pr24-ga-akeru-to-no-mukou-20260917/raw/30_hairu.tsv | 1,305,292 | c7440079df33721b5729a8cc8cb0510b14133d692d572f9476b14bf39dd480ed | 有 |

## ★此の数が意味せぬ事★

- **disk の束が欠けた訳ではない。** disk には今も 182本が揃つて居る。欠けるのは ★此の commit の木の中だけ★ である。
- **★除いた四本の内 三本は其の束の臺帳に宣されて居る★** ∴ commit した木の上で門を走らせれば、條①(臺帳↔実体)が ★三つ鳴る★。
  鳴る行は下記の三本で、鳴りは疵ではなく ★本裁の選択そのもの★ である。
  - path=driver/__pycache__/kaki.cpython-314.pyc sha256=84ba3aa9165b6c33a1842b904f8d6e8ab7642e023b00ac6645e3126ec2816cac bytes=2142 lines=15
  - path=raw/31_daini_for.tsv sha256=9eae5b4b4f18ec379761e02d58bcf1a9aa22a350adab378171fa3542104dd67b bytes=1160233 lines=3312
  - path=raw/30_hairu.tsv sha256=c7440079df33721b5729a8cc8cb0510b14133d692d572f9476b14bf39dd480ed bytes=1305292 lines=7508
- 除いた因= __pycache__ 2本(生成物)・1MiB超 2本。裁 seq329208 が案A を斥けた理由と同じ物を、案⑵にも当てた。

## 載せ方

素の `git add` は .gitignore:7 の裸の `*` に遮られ、rc=0・err 0行で ★載つた0本★ を返す(專任2 実測)。
∴ 本 commit は `git add -f` で 178本を名指しした。`.gitignore` は書換へて居らぬ。
本番の .git/index・HEAD・worktree には一指も触れず、捨て index(GIT_INDEX_FILE)と commit-tree で枝を立てた。

## 本紙を作る器が踏んだ疵(記録)

初走では器を zsh の二重引用符に入れて渡した為、本文中の `…` 三箇所を zsh が ★走らせた★
(`*` → AGENTS.md へ展開・`git add -f` → 引数無しで実走)。
本番 .git/index の sha256 は前後同一(ff2be85f221a8e5016d8a24bf6af02663c157086ebc008fb04598d05a33c3c81)、
HEAD・porcelain 1036行 も不動ゆゑ repo への害は無し。紙のみ三語が落ち、本稿で書き直した。
