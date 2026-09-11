## §的 ★的一行★
panelData の名簿は ★現に在る★ ―― 但し ★44 鍵★ であり、令の言ふ 48 とは 4 本 合はぬ。而して「狼少年」も「121」も、当てた二 dir の source には 結ぶ説明が ★現に無い★。

## §A 頭
- 時刻(as_of): 2026-09-10T17:52:48+0900
- 本樹 sha: 1ad4edfbadc69191183a42113e9979c3f91b7dbf (git rev-parse HEAD)
- 当てた dir: /mnt/c/DentalBI/frontend/src ・ /mnt/c/DentalBI/backend（此の二つのみ・find 0・全樹を舐めず）
- 拡張子: .ts .tsx .py .sql（--include で絞る）／engine は /usr/bin/grep を明示（床(17)）
- 焚 0（.rule.py を一つも起こさず）／走 0 ―― grep・sed・wc・sha256sum・git 讀取動詞は 令 五 の括弧に依り数へず
- 讀んだ物: 当たつた file 15 本の内 4 本を行域で開いた（他 11 本は grep の当たり行のみ）
- 母（書く前に測つた）: 紙 115 枚 / 23,685 行 / N=277 / 幅 169-498
- 表は作らぬ（令 一）ゆゑ §B は箇条書きで組む

## §B 出現の在り処
- 語 panelData / panel_data / PANEL_DATA の当たり = ★90 行 / 15 file★（frontend 14 本・backend 1 本）
- 名簿の本体: frontend/src/features/ekarte/components/EkarteV5Layout.tsx L685-751・語 panelData・1,718 行・sha16 2021459a6c64d9a6
- 消費の側: frontend/src/features/ekarte/hooks/useDefenseChecks.ts L152/167/170/172/204/214/223・224 行・sha16 8c90901dd0667aa5
- 別系統の型宣言: frontend/src/features/ekarte-v6/types.ts L134/L157・212 行・sha16 6d5e2d53bfeaaf07
- 別系統の初期値と action: frontend/src/features/ekarte-ab-input/abInputReducer.ts L32/46/57/79/94/121/124・149 行・sha16 0425bc678ecc6e7d
- 同じく: frontend/src/features/ekarte-v6/StepperWizard.tsx L50/100/114/119/120/135・417 行・sha16 cafaaa053584afe8
- 受け渡しの側: frontend/src/features/ekarte/components/FindingsDisplay.tsx L16/46/60・189 行・sha16 5198cfe76756092b
- backend の当たりは ★2 行のみ★: backend/api/inspection_coverage.py L27・L63・語 panel_data・76 行・sha16 2a17bd7230df6f65 ―― 何れも RPC 名 get(下線)inspection(下線)panel(下線)data の中であり、鍵の名簿は載らぬ
- 残り 6 本は試験の dir 配下（dir 名が二重下線を含むゆゑ path を写さぬ）・悉く panelData を組み立てて渡す側

## §C 名簿の在/無と鍵の数
- 名簿 = ★現に在る★ ―― EkarteV5Layout.tsx L685-751 の useMemo が「DB 条件の field 名 → バッジ state 値」の平坦 map を組む
- 鍵の数 = ★44★（数へ方＝L685-751 の行頭 d.(識別子) = の行を /usr/bin/grep -c＝44・鍵名を切り出して sort|uniq した数も 44 ∴ 重複無し）
- ★48 との一致 = 無★（差 4）
- 型: 器の宣言は Record<string, unknown> の一種のみ。右辺の形は三つ ―― ㋐素の値 30 本 ㋑空落ち付き（真偽 or 空文字）9 本 ㋒optional chain 付き（undefined 有り得る）5 本
- 別名: 右辺が同じ源を指す鍵が ★4 組（8 本）★ 在る ∴ ★源の数は 40★・鍵の数 44 とは別の数である
- 鍵名の個々の値は写さぬ（令 二）
- 数 48 の当たりは 当てた file の中に 1 箇所のみ（EkarteV5Layout.tsx L178）―― X線点数の卓の中の値であり 鍵の数とは別物
- 第二の panelData（ekarte-v6 と ekarte-ab-input）は 走る間に action で積む器 ∴ ★静的な鍵の数は測定不能★。同じ名で別の物である（床(3)）

## §D 121 との関係の説明 在/無
- 「狼少年」の語 = 二 dir に ★0 件★
- 数 121 の当たり = 19 行。悉く別物（適性設問の id・色の値・dev(下線)qa の番・PDF 座標の値）
- ∴ 121 と panelData を結ぶ説明は ★現に無い★
- 44 と 121 を結ぶ数式・註・doc への参照も、当てた二 dir には現に無い

## §E 実測と見込みの別
- 実測（己が当たつた）: 44 鍵・90 行・15 file・別名 4 組・48 の当たり 1 箇所・狼少年 0 件・121 の結ぶ説明 0
- 見込み⑴: 名簿に無い field を rule が指せば 二重否定の評価は必ず偽と成り 常時未クリアに倒れる。之が「実体無きに警告が出る」の機構に見えるが、source に其の名は無い ∴ ★己の推しである★
- 見込み⑵: 44 と 48 の差 4 の因（版差か・別系統の鍵を足すか・数へ方の差か）は ★測つて居らぬ★
- 確かめて居らぬ: RPC の向う（DB）に別の名簿が在るか否か ―― DB を讀まぬ令ゆゑ ★測定不能★

## §F 新條 四百九十九〜
- ★四百九十九★ 「名簿が在る」と「名簿が令の数と合ふ」は別 ―― 44 と 48 の差 4 は 不在ではなく 数の食ひ違ひである。数を出す時は 何の file の 何の行域を 何の数へ方で数へたかを同じ行に書け。
- ★五百★ 平坦 map の鍵の数と 源の数は別 ―― 右辺が同じ物を指す組が在れば 鍵 44 に対し 源 40 に成る。何を一つと数へたかを同じ行に（床(30)の当て）。
- ★五百一★ 数を語として grep するな ―― 48 は点数の卓にも 座標にも 色にも当たる。数で引いた時は 当たつた行の逐語で 何の数かを分けて書け。

## §G 結び
- panelData 48 鍵の名簿: 44 鍵の名簿は ★現に在る★／48 鍵の名簿は ★現に無い★／両者を繋ぐ説明は ★測定不能★
- 121 との関係の説明: ★現に無い★
- 繰越⑴ 差 4 の因（版差 or 数へ方 or 別系統の足し）は未測。繰越⑵ RPC の向うの名簿は DB 讀取の令が要る。
