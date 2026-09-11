## §的 ★origin/main へ函を戻す道を patch に鋳る（当てるな・apply --check 迄）★
### §A 頭
- as_of=2026-09-11T10:37:45+0900／母=origin/main(50a9e20c3e978d2e)・源=59b9f4dd8／製品樹 書込 0・DB 0・押しは自席枝のみ
- 讀んだ紙=scratch/k3_orders/order297_a3.txt 12行 2355B sha256頭16=323b494c75fd8e1d
- 打数=git讀取動詞の起動 ★10／上限12★・焚 0・走 0・当ては ★apply --check 2回のみ★・cd 0・redirect 0・find 0
### §B ㋐ 家老の数を独立に当て直す（三値）
- 59b9f4dd8 の当該 file の行数 ＝ ★5,624★ ∴ ★一致★／def の行 ＝ ★L4295★ ∴ ★一致★／呼手の行 ＝ ★L5091★ ∴ ★一致★
- c6ea84e56 の当該 file の当該名 ＝ ★0件★ ∴ ★一致★（陽性対照 ＝ _select_comment_template_key が ★2件★・L11429 def／L12409 呼手 ∴ 命は効く。file は 13,720 行）
- ★不一致 一つ★ ―― 次の top-level ＝ 家老 L4329／己の実測 ★L4328★（逐語 ＝ router の get デコレータ行）∴ 塊の終りは ★L4327★
### §C ㋑ 塊の範
- 開始 ＝ L4295（def の頭）／終り ＝ L4327（空行）／行数 ＝ ★33行★。終端 anchor は実物で先に取つた（條502・L4328 が次の top-level）
- 塊の形 ＝ 引数 ★2★（client: Any, set_code: Optional[str]）・try/except＋logger の warning・doc_order 昇順の limit 1・行 0件は None・★409 を投げぬ★ ―― 令289 patch(409 一箇所) とも 甲樹の頂(409 三箇所) とも ★別の形★
### §D ㋒ 鋳た patch
- path=scratch/ashigaru-third-3-12e9d4bd/order297_function_restore_v1.patch
- 行数 ＝ ★43行★(split-1)／1,507 B／sha256頭16 ＝ ★67db351e5480d002★
- ★生の行末 ＝ LF★（difflib で鋳り newline を LF に指して書いた ∴ 均した後ではなく 生が LF）
- hunk ＝ 一つ（12413 の行から 6 行を 40 行へ）。足す行 ＝ ★34★ ＝ 塊 33 ＋ 区切りの空行 1
- 足す先 ＝ origin/main の当該 file の ★L12418 の直前★（既存 def の頭）
- ★理由（一行）★ 同じ comment 系の private helper が並ぶ帯で 直前 2 行が空行 ∴ デコレータの途中に割り込まぬ ★top-level 境界★ である（anchor を実物で確かめてから鋳た・床(28)）
### §E 塊が使ふ名が母に在るか（当てる前に讀取で確かめた）
- Optional ＝ L24 の typing の import に現に在る／Any ＝ 同行・使用 363 箇所／logger ＝ L118 で定義・使用 35 箇所 ∴ ★三つとも現に在る★
### §F ㋓ apply --check
- 根 ＝ /mnt/c/DentalBI ・ 剥がし数 ＝ -p1（條493 に従ひ 根と -p を同じ行に置く）
- rc ＝ ★0★ ・ 出力 ＝ ★0行★。★--check のみ ・ 当てて居らぬ★
- 併記 ＝ origin/main の当該 file の blob と 作業樹 HEAD の blob は ★同符 b23c0298ebfaf5c1★ ∴ 作業樹基準の --check は origin/main と同じ中身を測つて居る
### §G ㋔ SKIP の扱ひ
- ★SKIP は FAIL ・ skipif の新設は禁 ∴ harness を避ける道は一切鋳つて居らぬ★（本 patch が触る file は ★1本★ ＝ 製品 py のみ・試験 file に一字も触れて居らぬ）
### §H ㋕ 陽性対照 二つ（出力と exit を併記）
- 当たる側 ＝ -p1 ―― 出力 ★0行★／exit ★0★
- 当たらぬ側 ＝ 同じ patch・同じ根で 剥がし数だけ -p0 へ替へた ―― 出力 ★1行★（b/ 付きの path が見当たらぬ旨の error）／exit ★1★
### §I 実測／見込み／確かめて居らぬ／数が意味せぬ事
- 実測 ＝ §B の 5624/4295/5091/0件・§C の 33行・§D の 43行と 34行・§E の 363と35・§F の rc0・§H の exit 0と1
- 見込み ＝ 無し（本紙に推し量りの行を置いて居らぬ）
- 確かめて居らぬ ＝ ❸当てた後の姿（--check 迄ゆゑ）❹★本塊の引数は 2・令290/令296 が測つた harness の呼手 L642 は 3 位置 ∴ 数が違ふ★ ―― 之は讀取で見える差であり 当てた後の挙動は測つて居らぬ❺塊 33 行の中の説き書きの逐語（紙に写して居らぬ）
- 数が意味せぬ事 ＝ ❸rc 0 は「当てれば試験が通る」を意味せぬ（--check は文脈の噛み合ひのみ）❹43行 は「足す code が 43 行」を意味せぬ（頭 3 行と文脈 6 行を含み 足す行は 34）❺「名が母に在る」は「実行時に解決する」を意味せぬ
