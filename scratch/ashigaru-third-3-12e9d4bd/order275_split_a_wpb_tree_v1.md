## §的 ★的一行★
割れ㋐ の形は ★樹の違ひ★ である ―― A4 は /mnt/c/DentalBI 樹の相対 path に当てて「現に無い」と記し、WP-B 原本は ★此 repo の樹に 148 行で現に在る★。而して板の所在記録が載せる完全 SHA256 と 己の実測は ★一字も違はず一致する★ ∴ 別物ではなく同一の物である。

## §A 頭
- 時刻(as_of): 2026-09-10T18:07:52+0900／本樹 sha: 1ad4edfbadc69191183a42113e9979c3f91b7dbf
- 讀んだ先（令 二 の順・名指し以外は開かず）: seat-matrix-draft.md L38-60 → 名指しの DL-4 紙 1 本 → 其の紙が引く path 二つ（WP-B 原本・板 dump）のみ
- 焚 1（python 起動 1 回で完全 SHA256 と紙の鋳造を一括）／走 0・find 0・/mnt/c 書込 0・DB 0
- 讀んだ物: 4 file（seat-matrix 67 行・DL-4 紙 94 行・WP-B 原本 148 行・板 dump 16,560 行の内 逐語 1 行を DL-4 紙 経由で引いた）

## §B DL-4 紙の逐語
- DL-4 紙 = scratch/ashigaru-third-4-12e9d4bd/b3_prep_offroute842_v1.md（94 行・12,511 B・sha16 e8f2c53fedfba3c3・mtime 2026-09-06 05:13）
- 其の L32 逐語（樹の根を名指して居る一行）:
> 當席が`/mnt/c/DentalBI/scratch/st3_wpb_v6_defensive_link_inventory_20260828.md`を`ls`で確認したところ**現に無い**(該当pathにfile不在)。`find /mnt/c/DentalBI -iname "*wpb*"`(node_modules/.git除外)でも全木を掃引したが一致0件。`git log --all`で同path・同名の追加履歴も0件(scratch配下ゆゑ元来コミット対象外である可能性が高く、これ自体は異常の証跡ではない)。
- 其の L27 の見出し逐語: ★「§① WP-B 原本の所在記録は在る、原本そのものは現に無い」★
- 其の L30 逐語（板 dump の data_location フィールド）:
> `WP-B棚卸(讀取のみ): scratch/st3_wpb_v6_defensive_link_inventory_20260828.md sha256=c52861bab5ca26a0747c4e84a2798faf234b5eee00a090ad4247688e466f582d as_of=2026-08-28T10:31+09 (將軍third seq220906・板転記=総監督代行)`
- ∴ DL-4 紙は ★樹の根を /mnt/c/DentalBI と明記して居る★。「無い」は其の樹に就いての言である

## §C 二樹での在/無・行・sha16
- 相対 path: scratch/st3_wpb_v6_defensive_link_inventory_20260828.md
- ㋐ /mnt/c/DentalBI 樹: ★現に無い★（当該 path に file 不在。scratch dir 自体は在るゆゑ dir 不在ではない）／行・sha16 = 測れぬ
- ㋑ 此 repo（1ad4edf 系）: ★現に在る★／148 行・9,782 B・sha16 c52861bab5ca26a0
- 同名・同 sha か別物か: ★同一である★ ―― 板 dump の所在記録が載せる完全 SHA256 と 己の実測が全 64 桁 一致する（§E に併記）
- 逆向きの非対称: DL-4 紙が引くもう一つの path reports/_scratch/y-board-all.json は ★/mnt/c 樹にのみ在り★（981,859 B）此 repo には ★現に無い★
- ∴ 二つの紙が引く二つの file は ★各々 別の樹にのみ在る★。何れの席も己の樹だけを見れば片方を「無い」と読む

## §D 割れの形（裁かず併記）
- 三択（樹の違ひ／名の違ひ／時点の違ひ）の内 ★樹の違ひ★。名は一字も違はず、sha も一致ゆゑ 名の違ひでも時点の違ひでもない
- A4 の三つの根拠は ★何れも其の樹では正しい★ ―― ㋐ls 不在（/mnt/c 樹）㋑find 0 件（/mnt/c 樹）㋒git log --all 0 件（scratch は ignore ゆゑ git の目に初めから見えぬ・A4 自身が「異常の証跡ではない」と註して居る／條 四百九十六）
- 己の実測も ★此の樹では正しい★。∴ 割れは何れかの誤りではなく ★同じ相対 path が二樹で別の答を返した事★（床(2)）
- 同型の先例: 令272 で己が chunk-completion の相対 path に当てた時は ★逆向き★（此 repo に無く /mnt/c に在つた）。二度目ゆゑ偶然ではない
- 裁は上に仰ぐ（席は裁かぬ）

## §E 実測と見込みの別・完全 SHA256
- 実測（己が当たつた）: 二樹の在/無・148 行・9,782 B・板の所在記録との 64 桁一致・y-board-all.json の非対称・DL-4 紙 94 行
- 見込み: 何故 /mnt/c 樹に無いか（初めから此 repo にのみ置かれたか・移されたか・消されたか）は ★測つて居らぬ★。板の as_of 2026-08-28 と此 repo の file の mtime を突き合はせて居らぬ
- 確かめて居らぬ: y-board-all.json の当該 id の欄を己が直接開いては居らぬ（DL-4 紙 L30 の逐語を写した／床(10)(5)）
- 完全 SHA256（本紙を書く前に測つた・四本）:
  - c52861bab5ca26a0747c4e84a2798faf234b5eee00a090ad4247688e466f582d  scratch/st3_wpb_v6_defensive_link_inventory_20260828.md（★板の所在記録の値と全 64 桁 一致★）
  - e8f2c53fedfba3c310524f2dc3939844d7b381f6d43322dd645dc01acbe10cdc  scratch/ashigaru-third-4-12e9d4bd/b3_prep_offroute842_v1.md
  - 87f22d4af099a029ced5ea4b52ae95a57531ba3092d543eb4d259bdcb78ac581  /mnt/c/DentalBI/reports/seq224812-seat-matrix-draft.md
  - ee2863b29d910a3728af8fa10cbd1cd58c29c27c6a1a517b6b74fdbedf84180a  /mnt/c/DentalBI/reports/_scratch/y-board-all.json
- ★新條 五百三★ 相対 path で書かれた所在記録は ★樹を名指さねば半分しか指さぬ★ ―― 同じ相対 path が二樹で別の答を返す時、「現に無い」は「此の樹に現に無い」の謂ひである。所在記録には ★樹の根と sha を同じ行に★ 書け。sha が一致すれば 樹を跨いでも同一である事の証に成る。
- 結び: 二樹の在/無 ★/mnt/c=現に無い・此 repo=現に在る★／割れの形 ★樹の違ひ★／同一性 ★現に在る（sha 64 桁一致）★
