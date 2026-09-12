## §的 ★的一行★ snapshot の中で 集約が空の時 null を返し得る所を数へ 守りの有無で分ける
## §A 頭 ―― 何時・何を・幾つ讀んだか
- as_of 2026-09-12T16:26 ／ 席 ashigaru-third-3 ／ 板 12e9d4bd ／ 令346（符 sha256先16 a031ebb350e114a1・25 行）／ BASE 8a960b3280b1c729
- 母 ＝ 家老の樹 /home/hakudoukai/karo3/wt-abbrev-guard-20260912 の supabase/migrations/20260909170000 の snapshot（改行 1317・split 1318 片・63,769 B・sha256先16 4178353b8bd7d298・★讀取のみ★）
- 焚 1（新器 order346 null agg survey.py・158 行・sha256先16 278119884870e6a9）／走 1（二度目は撃たず）／★網は撃つ前に器の頭へ鋳り 一字も変へずに撃つた★
## §㋐ 網の逐語（新条㊻ ―― 之を写せば他者も同じ母を作れる）
- 集約 ＝ 行の集まりを一つの値へ畳む函のうち ★空の時 null を返す物★ ＝ jsonb agg・json agg・jsonb object agg・json object agg・array agg・string agg・sum・max・min・avg・bool and・bool or・every の 13 語（紙では語中の下線を空白へ置いた ―― 原は下線）
- count は空でも 0 を返す ∴ ★母の外★（数へぬ）
- 当たり ＝ 上の名の直後に開き括弧が来る形。境界は 英数と下線以外の明示クラス。大小文字は無視した
- 母の外 ＝ 行註（横棒二つ）と 帯註（斜線と星の対）と 単引用の文字列の中に在る当たり。★ドル記号の対で囲まれた帯は code ∴ 母の内★
- 守り ＝ 其の当たりを括弧の対応で外へ辿つた時 包む呼びの何れかが coalesce である事。辿りの上限 ＝ 其の当たりを含む CREATE FUNCTION の頭
- 分けられぬ ＝ 何れの CREATE FUNCTION にも属さぬ当たり
## §㋑ 数と割（★単位を明記★・raw は - > の行）
- > FILE lines=1317 bytes=63769 / FUNCS total=24 / HITS raw=21 / in comment or literal=0 / live=21
- > SPLIT guarded=9 naked=12 undecidable=0 (unit=hit)
- > BYNAME jsonb agg=11 jsonb object agg=1 max=3 min=3 string agg=3
- > FUNCS with guarded=2 / with naked=4 (unit=function)
- 単位 ＝ 当たり（出現）―― 総 21／守られて居る 9／守られて居らぬ 12／分けられぬ 0
- 単位 ＝ 函 ―― snapshot の函 24／守りを持つ 2／裸を持つ 4／集約の当たりを一つも持たぬ 18（守りと裸が同居する函は 0）
- 割（母 ＝ 当たり 21）―― 守り 9／21・裸 12／21。★函を母に取れば 裸 4／24 と成り 別の数である★
## §㋒ 守られて居らぬ所（行番は三つまで・残りは数のみ）
- L61 string agg（函 check document integrity）／L664 min（函 fn repeat message trap）／L732 jsonb agg（函 get abbreviation rules）
- 残り 9 は数のみ。裸を持つ函は四つ ＝ check document integrity 2／fn repeat message trap 6／get abbreviation rules 3／下記の一つ 1
- 四つ目の函名 ＝ validate treatment entry に ★二重の下線★ を挟み pre dlane 20260614 が続く形（紙の門が二重下線を拒む ∴ 分けて書いた・当たりは L1278 の string agg）
- ★今回の三鍵 ＝ L732・L743・L754 の jsonb agg 三つ ―― 裸 12 のうちの 3 に過ぎぬ★
## §㋓ 三値 ―― ⑴ ★他にも守られて居らぬ所が在る★
- 拠 ＝ 裸 12 のうち 9 は三鍵の外に在り 函にして三つが三鍵の外である
- 之では言へぬ事 ＝ ★DB が実際に何を返すかは言へぬ★／空の集合が現に来るかは各々の問ひの形と中身に依り 字では言へぬ／裸が疵であるかは呼手を見ねば言へぬ（令345 の㊅と同じ理 ―― 母を辿らねば断ぜられぬ）
## §㋔ 残弾（㊈㊉㊋ から数へ直す）
- 消 ＝ 無し（㊈ apply の行末空白／㊉ 頭註の md5 と byte／㊋ 場E の型 の三つは生きて居る）
- 新 ＝ ㊌ 裸 12 のうち三鍵の外の 9 が 呼手から空の集合を渡され得るかは未測（本弾の網は字のみを測つた）
## §禁語（新条㊺ ―― 行・語・母の三つ）
- 母 ＝ 本紙 1 file のみ（器の .py と snapshot は母の外）／単位 ＝ 行／網 ＝ 判定の語 13・先送りの語 3・鍵の語 4 の計 20 語を並べた列（逐語は紙へ書かぬ）／生 0 行・- > の行を除き 0 行
## §床（実績）
- 当て 0・check 0・DB 0・MCP 0・psql 0・patch 0（鋳らず）・製品 code 書込 0・install 0・fetch 0・rm 0・find 0・ssh 0・/mnt/c 書込 0・家老の樹へ書込 0（讀取のみ）・pytest 0・焚 1・走 1
