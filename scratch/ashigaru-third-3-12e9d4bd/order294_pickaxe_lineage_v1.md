## §的 ★此の函の名が main の履歴に一度でも運ばれたかを pickaxe で測り、salvage 二符を name-only で引き直す★

## §A 頭
- as_of: 2026-09-11T09:58:54+0900（紙を書き終へた後に date で取つた）。的の樹 = /mnt/c/DentalBI（git -C のみ・★cd 0★）。符は悉く git の id ≡ sha1。作業樹 HEAD `53412b7bcda2f8ae`／tree `d57a2e0b2ffc4a52`。`origin/main` = `50a9e20c3e978d2e`／tree `6b7e131ddb739843`。★注意★ 令293 で引いた局所 `main` は `3165e90450f3de74` ―― `origin/main` と ★別符★ である（本紙の main 側は悉く `origin/main`）。
- 讀んだ紙 = 1 本 `scratch/k3_orders/order294_a3.txt`（8 行(wc 改行数)／9 片(split)／1,695 B／sha256 頭16 `366f9d12b25f5c5b`・家老の訂正便 09:49:26 と同値）。
- 打数 = git 讀取動詞の起動 ★11／上限 12★。焚（.rule.py の起動） 0／上限 1。走 0・当て 0・押し 0（紙の押しを除く）・製品 code 書込 0・/mnt/c 書込 0・find 0・★リダイレクト 0★。床の超過 現に無し。
- ★器が /tmp へ置いた物（己は消さず・己が書いた物でもない）★: `bgyp5rbtr.output`（09:55:36・1,356 B・`ec4e88709659767b`）／`b8dkj2r2x.output`（09:55:37・63 B・`3fe20b302c504951`）／`bkcqyipg0.output`（09:56:17・0 B・`e3b0c44298fc1c14`）。在処 = harness の tasks dir。

## §B pickaxe 四走り（`log -S` ・符 ＝ 挙がつた commit を 1 と数へた数）
| 走り | 範 | pathspec | 符の数 | 挙がつた符 |
|---|---|---|---|---|
| ㋐ | `origin/main` | 無（全 path） | ★1★ | `7f3f371b9`（2026-09-02 22:38:22） |
| ㋑ | `origin/main` | `backend/api/treatment_validation.py` | ★0★ | ―― |
| ㋒ | `--all` | 無（全 path） | ★6★ | `db86b2099`(09-05 15:15)／`7f3f371b9`(09-02 22:38)／`c6ea84e56`(09-02 21:20)／`7f39168d3`(07-23 15:37)／`8a23afa8a`(07-23 01:14)／`59b9f4dd8`(07-23 00:34) |
| ㋓ | `--all` | 同上 | ★1★ | `59b9f4dd8`（令291 と同値） |

## §C 何時 入り 何時 消えたか（■二・推し量りを置かず符のみで）
- ★名★ は `origin/main` へ ★一度だけ入つた★ ―― `7f3f371b9`（2026-09-02 22:38:22・題 `salvage(safe): ... 既存fileを一字も上書きせぬ 28本 ...`）。㋐ が挙げた符は此の一つのみゆゑ ★消えた符は現に無い★（＝今も在る）。★函★（`backend/api/treatment_validation.py` の側）は ㋑ が 0 ゆゑ ★一度も運ばれて居らぬ★。

## §D salvage 二符の name-only（■三・己で引き直した）
| 符 | file 数 | `backend/api/treatment_validation.py` | harness | `origin/main` の祖先か |
|---|---|---|---|---|
| `c6ea84e56`（題に「38 file」） | 38 | ★1（含む）★ | 1 | ★否（`--is-ancestor` rc=1）★ |
| `7f3f371b9`（題に「28本」） | 28 | ★0（含まぬ）★ | 1 | 是（㋐ が挙げた） |
- ∴ 令291 §E の「7f3f371b9 の 28 本に `treatment_validation.py` は含まれぬ」は ★当たり★（己で引き直して同値）。併せて ★新たに判つた事★ ―― 一つ前の salvage `c6ea84e56` は函を ★含んで居た★ が、其の符は `origin/main` の祖先に非ず。`db86b2099`（09-05・題 `test(backend): restore isolated harness collection`）も同じく祖先に非ず（rc=1）。

## §E 陽性対照
- ㋐ ★pickaxe★ ―― ㋑ と ㋓ は ★同じ命の形で ref だけ替へた★ 対。㋑ が 0 の傍らで ㋓ は `59b9f4dd8` を挙げた ∴ 命は効いて居る。加へて名だけ替へた走り（`_select_comment_template_key`・`origin/main`・全 path）は ★2 符★（`9715f6d58`／`bc1357c3a`）を挙げた。
- ㋑ ★name-only★ ―― 同じ命の形で符だけ `8a23afa8a` へ替へると file 4・`treatment_validation.py` ★1★。∴ §D の 0 は ★命の不発でなく 現に含まぬ★。

## §F 実測／見込み／確かめて居らぬ ＋ 数が意味せぬ事
- ★実測★: 四走りの符の数（1／0／6／1）／name-only の 38 と 28／含む 1・含まぬ 0／祖先 rc 二本（共に 1）／対照 三本（㋓ 1 符・別名 2 符・name-only 1）。
- ★見込み★: 現に無し（本紙に推し量りで埋めた升は一つも無い）。★因は書かぬ★ ―― 何故 `c6ea84e56` が祖先でないかは本令の範の外。
- ★確かめて居らぬ★: `db86b2099` の中身（name-only を引いて居らぬ）／`origin/main` の harness が今も名を書くか（本令では grep して居らぬ ―― 令290 は ★作業樹★ で数へた）。
- ★数が意味せぬ事★: 「㋒ が 6 符」は ★名の出現数が変つた符の数★ であり、★名を含む符の数★ でも ★函が編まれた回数★ でもない（出現数を変へぬ改めは `-S` に映らぬ ―― 之が令291 §D を誤らせた形）。「38」「28」は ★其の符が触れた file の数★ であり ★運ばれた成果の数★ ではない。
