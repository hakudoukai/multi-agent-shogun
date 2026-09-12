# 令350 ―― ㊏ を撃つ：一般名 validate treatment entry の當たりを 網を直して分け直す

## §的 ★的一行★
- 令349 で己が申告した㊏を撃つた。一般名 validate treatment entry の 918 當たりを file の種で割り直し ㋐ code に限つて分け直した ―― code の呼手は ★現に在る★（三本の file の三行）。

## §A 頭（母・網・床）
- 母 ＝ 家老の樹 /home/hakudoukai/karo3/wt-abbrev-guard-20260912 の git 管理下 全体。樹の頭（git の id ＝ sha1）＝ 6b5ac1f730ba4f0c ―― 令349 と同じ事を符で示す。git ls-files ＝ 17,878 本（一つ ＝ path）。讀取のみ・書込 0。
- as_of 2026-09-12T17:42。器 ＝ scratch/ashigaru-third-3-12e9d4bd/order350_general_name_recount.py（wc -l ＝ 221・split の片 ＝ 222・符 7071819c4cf0a3ba ＝ sha256 頭16）。焚 1・走 1。器は消さず残した。産出は head にも pipe にも繋がず器の中で讀み切つた。
- 網（撃つ前に器の頭へ逐語で鋳つた・新条㊻）:
- > 交り ＝ 行頭か 英数と下線以外の字 ＋ validate treatment entry（下線は単一）＋ 英数と下線以外の字か行末。git grep の -I -n -E を ★一度だけ★ 打つた。一つ ＝ 當たり行。
- > 種分け ＝ 拡張子（path の末の点より後を小文字に均した物）で割る。㋐ code ＝ py と ts と tsx と sql／㋑ log と産出 ＝ log と json／㋒ 紙 ＝ md と txt／㋓ 其他 ＝ 残り。
- > ㊀呼ぶ ＝ 註の行を除き ㈠ rest/v1/rpc/ に続く名 ㈡ rpc の括弧開きに続く 引用符付きの名 ㈢★令350 で足した★ 行が 引用符に包まれた名のみ であり 上 3 行以内に rpc の括弧開きが在る ㈣ select か perform に続く 名と括弧開き。
- > ㊁定める ＝ 註の行を除き create（or replace を挟み得る）function に続く名 ―― 之に ★令350 で足した★ drop function と alter function と comment on function を加へた。
- > ㊂名のみ ＝ ㊀㊁ に当たらず 行頭が 二重の横棒 か 井桁 か 縦棒 か 横棒 か 星印 で始まるか 名と括弧開きの形が一度も現れぬ行。判じられぬ ＝ 残り。
- 固有名（二重の下線 ＋ pre dlane 20260614 が続く名）は 令349 の通り別の名として保つ ―― 境界が下線で切れる故 上の網に一つも掛からぬ。

## §㋐ file の種で割つた（一つ ＝ file と 當たり行・母 ＝ 上の 918 當たり）
- ㋐ code ＝ file 12・當たり 48。㋑ log と産出 ＝ file 4・當たり 812。㋒ 紙 ＝ file 22・當たり 58。㋓ 其他 ＝ file 0・當たり 0。合 file 38・當たり 918。㋑㋒㋓ は令の命に従ひ 数だけ出し 分けには入れて居らぬ。
- ㋑ の中身 ＝ v6-backend-8000-restart-20260629.log 738／local-e2e-backend-20260704-go.log 72／json 2 本 各 1。★令349 で ㊀呼ぶ と数へた 818 の大半は 此の走りの記録行であつた★。
- ★床(23)★ reports/_tmp_touyaku_t3_v4/treatment_validation.py と reports/_tmp_touyaku_t3_v5/backend/api/treatment_validation.py は 拡張子では code・棲家では産出の下に置かれた写しである。本紙は拡張子で割つた故 ㋐ に入れた。

## §㋑ ㋐ code に限つた四分け（★作法 八条目 ―― 物差しを動かした分を分けて書く★・一つ ＝ 當たり行）
- 令349 の儘の網（㊀は ㈠㈡㈣ のみ・㊁は create のみ）: ㊀呼ぶ 0・㊁定める 2・㊂名のみ 36・判じられぬ 10。
- 令350 の直した網（㊀に ㈢ を足し ㊁に drop と alter と comment on を足す）: ㊀呼ぶ 3・㊁定める 6・㊂名のみ 32・判じられぬ 7。差 ＝ ㊀ +3・㊁ +4・㊂ -4・判じられぬ -3 ―― ★之は母が増えたのでなく 網を広げた分である★（母 ＝ ㋐ code の 48 當たりで不動）。

## §㋒ 其の呼びが集合を渡し得るか
- ㊀呼ぶ の三行 ＝ backend/api/treatment_validation.py の 11866 行／reports/_tmp_touyaku_t3_v4/treatment_validation.py の 3994 行／reports/_tmp_touyaku_t3_v5/backend/api/treatment_validation.py の 4017 行。後の二本は前の一本の写しである（己が直に當たつた）。
- 呼びの名は 括弧開きの ★次の行★ に在る。令349 の網が 0 と数へたのは 同じ行のみを見て居た故である。
- 三行とも 下 24 行の内に 引数の鍵 8 つを渡す: p_set_code・p_patient_id・p_clinic_id・p_tooth_fdi・p_output_items・p_patient_conditions・p_episode_data・p_revision_code（★鍵の名のみ・値は一つも写して居らぬ★）。

## §㋓ 三値
- ⑴ を名指す ―― ★code の呼手が在る★。何本の何行か ＝ 上の §㋒ の 三本三行。其の呼びは 鍵 p_output_items と p_patient_conditions と p_episode_data を渡す形であり ★集合を渡し得る口が字の上に在る★。
- ⑵ は採らぬ ―― 818 は悉く log と産出ではなかつた（㋑ ＝ 812・残りは ㋒ 紙 と ㋐ code に散る）。⑶ も採らぬ ―― 種分けは悉く付いた（判じられぬ 7 は ㋐ の中に残るが 呼びか否かの軸では ㊂ 側である）。
- ★本紙が言はぬ事★ ―― 走りの時に其の呼びが何度起きたか・DB が実際に何を返すかは DB 0 の床の下では測定不能。

## §㋔ 残弾
- ㊏ を閉ぢた。残 ＝ ㊈（apply が行末空白を落とす）・㊉（頭註の値は DB 0 では測れぬ）・㊋（場E の型の出所）・㊌（半ば・四函の呼手）・㊎（鍵が残るか落ちるか）。

## §㋕ 禁語 と §床
- 禁語 ＝ 生 0 語・除（- > の行を除いた数）0 語（母 ＝ 本紙 1 本・単位 ＝ 語）。床 ＝ DB 0・psql 0・MCP 0・当て 0・check 0・patch 0・製品 code 書込 0・install 0・find 0・rm 0・ssh 0・/mnt/c 書込 0・家老の樹へ書込 0・焚 1・走 1。BASE ＝ 03a3b59898f5bea2。
