# 令288 ―― 名 treatment_set_documentation の出所狩り v1

## §的 ★的一行★
的の名は ★現に在る★ ―― `supabase/migrations/20260323114647_create_treatment_set_tables.sql` の 70 行目が ★table 其の物を CREATE して居る★（定数でも 綴りの近い別名でもない）。∴ 令287 道 ㊂ の塞がりは ★table が無い★ のではなく ★table を引く函が失はれた★ である ―― 二つは別の事であり、道 ㊂ は「定義を戻す道」から ★書き起こす道★ へ形を変へる。

## §A 頭
- as_of 2026-09-11T08:42:41+0900。席 ashigaru-third-3／的の樹 `/mnt/c/DentalBI`（HEAD `53412b7bcda2f8aec4c5f5cdd157e819e8e91c02`）。當 repo の HEAD `1ad4edf` 不動。己の compact 境界 ―― 本窓は一度 compact を経て居り、★本紙の数は悉く 本令で己が引いた★。
- 打数 ―― git 讀取 7／上限 8（ls-tree 2・grep 5）・成果を産む器 2／上限 3（本紙を上限 35 行へ収める為 ★押す前に同じ path で一度鋳り直した★・数と結びは不変）。走 0・当て 0・install 0・DB 0・find 0・grep -r 0・/mnt/c 書込 0。

## §B 引いた pathspec と命（逐語・★測つた範★）
- `git -C /mnt/c/DentalBI grep -n treatment_set_documentation -- backend/`／同 `-c` 形／同 `-- backend/api/` 形 の三命。
- `git -C /mnt/c/DentalBI grep -in 'create table[^;]*treatment_set_documentation' -- backend/`
- `git -C /mnt/c/DentalBI grep -n treatment_set_documentation -- supabase/`
- ★範の申告★ ―― 当たつたのは ★pathspec 二つ（backend/ と supabase/）★ のみ。的の樹の頂の dir は ★29★ 在り ★残り 27 は一度も当たつて居らぬ★ ∴ 本紙は「此の二つの範での在無」しか言はぬ。

## §C 出所の在無（表）
| 何処（file） | 行 | 其の名を何が作つて居るか |
|---|---|---|
| supabase/migrations/20260323114647_create_treatment_set_tables.sql | 70 | ★table の CREATE 本体★（RDB の table）。同 file 138 に索引・155 に RPC の中の参照・203 に COMMENT |
| supabase/migrations/20260324024343_add_revision_tracking_to_treatment_sets.sql | 41 | ALTER ―― 同じ table へ有効期間の列を足す |
| backend/db/migrations/049_karte_visit_items_documentation_identity.sql | 51 | FK の参照先（REFERENCES）＝ ★作らず引くのみ★ |
| backend/tests の隔離 harness 二枚（c1 dml pkg ／ migration 049 ddl） | 117 ／ 55 | ★試験の中の CREATE TABLE★ ＝ harness が己の DB に立てる写し |
| backend/api/（pathspec を名指して当てた） | ― | ★0 行（出力は空）★ |
- 数 ―― backend/ の範で当たつた file は ★5 枚★・行の数は ★56 行★（per-file の数 3・21・3・27・2 の和）。supabase/ の範は ★4 枚★（頭 8 行のみ見た ∴ ★行の総数は測つて居らぬ★）。

## §D 之で道 ㊂ は動くか
- ★動く形が変はる★。台（table）は現に在る ∴ 「名は在るが函が無い」と言へる（條 四百九十七「名は定義ではない」の裏返し）。
- 而して `backend/api/treatment_validation.py` は 此の table を ★一度も引いて居らぬ★（令286 §D・0 行）∴ ★戻すべき定義は 的の file の中に今も無い★。
- ∴ 道 ㊂ は ★失はれた函を新たに書き起こす道★ と成る。要る物は 令287 §C 道 ㊁ と同じ二つ（backend の owner の手＋backend 書込の GO）＋ ★函の形（引数 2 と 3 の二形・戻りは active 行の id 一つ）を誰が決めるかの裁★。★当席の権では踏めぬ★。

## §E 三別
- ★実測★ = §B の五命と §C の file・行・数（5 枚 56 行・backend/api は空）。悉く己で引いた。
- ★見込み★ = 「函を書き起こせば試験が通る」事 ―― ★走らせて居らぬ★ ゆゑ見込みに留める。
- ★確かめて居らぬ★ = 残り 27 の頂 dir・supabase/ の行の総数・當該 RPC が返す形・板 fa06a3a1 の札（家老の便からの写し）。
