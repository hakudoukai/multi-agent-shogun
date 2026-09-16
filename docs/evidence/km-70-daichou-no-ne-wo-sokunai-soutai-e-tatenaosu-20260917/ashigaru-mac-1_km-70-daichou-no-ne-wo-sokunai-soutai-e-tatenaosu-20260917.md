# 第70弾 ―― 臺帳の根を束内相対へ建て直す(裁 322699 + 322949)―― km-47・km-50 の臺帳を ★cd 束の根 → append.py★ で新束 raw/saiken/ に建て直し(既成の束へ 0 字・舊形の儘固定)、三本の對照 ㋐明示基点→一致N/実体無0/rc0 ㋑既定→実体無N/rc1 ㋒出鱈目→rc1 を ★verify.py 直と門(KM_GATE_MANIFEST_BASE)の双方★ で示す ―― 答を先に(★數の出處 = raw/20_tatenaoshi.{txt,tsv} / raw/30_taishou.{txt,tsv} + 30_*.{out,err,rc} / raw/saiken/*_manifest.txt / raw/00_start.txt(起・宣・則)/ _after/60_gate_rcs.txt + 60_gate_top.r70.txt(門・紙の後に生れる故 紙は其の數を書けぬ)/ _after/96_after.txt / _after/63_sent.txt(實)★)

★臺帳の基点(一行)★: 本束の臺帳 `ashigaru-mac-1_km-70-daichou-no-ne-wo-sokunai-soutai-e-tatenaosu-20260917_manifest.txt` の path は ★束の根 `/Users/momizimac/multi-agent-shogun/docs/evidence/km-70-daichou-no-ne-wo-sokunai-soutai-e-tatenaosu-20260917/` からの相對(束内相対・裁 322699)★ ―― append.py を cwd = 束の根で呼ぶ故。照合は門に `KM_GATE_MANIFEST_BASE=<束の根>` を渡すか verify.py の第二引数に束の根を渡せ。既定基点(repo 根)で当てれば ★悉く実体無★ と出る ―― disk の欠けではなく基点の違ひ(本弾の對照㋑其の物)。raw/saiken/ の二本(km-47・km-50)も同じく ★各々の束の根 `docs/evidence/<束>/` からの相對★。第69弾までの臺帳(main 樹の根が基点)とは基点が違ふ ―― 基点の口を持つ門(commit 363d5fb)が入つた本弾から。

## 0. 断(先に)
1. **★建て直せた。★** km-47: 既成の臺帳 22 項 → 新 22 項・(相対名, sha256) 対一致 22 / 相違 0 / 旧のみ 0 / 新のみ 0・頭違ひ 0・束に無い名 0・append.py rc 0。km-50: 39 → 39・対一致 39 / 相違 0 / 旧のみ 0 / 新のみ 0・rc 0。★変つたのは path の頭 `docs/evidence/<束>/` が落ちた事だけ★(一行目 `path=an/A1_jikenme.err sha256=eaf1849054a8c0f…` / `path=km-50-kara-wa-todokazu-20260917.md sha25…`)。
2. **★三本の對照は悉く期待通り(verify 直・門 min・門 all の三器 × 二束)。★** ㋐ 明示基点 = 束の根 → 一致 22/39・実体無 0・rc 0。㋑ 基点無し(環境変数 unset・既定 = repo 根)→ ★実体無 22/39(= 母數)・rc 1★。㋒ 出鱈目 `/detarame/naki/ne` → 実体無 22/39・rc 1。讀めぬ行は全走 0。★三本とも期待通り ―― 明示基点で 一致 N / 実体無 0 / rc 0、既定基点と出鱈目で 実体無 N / rc 1。建て直せて居る。★
3. **門の基点の口は効いて居る。** 門の stderr は ㋐㋒ で `條① 基点=★引数 明示★(KM_GATE_MANIFEST_BASE)`、㋑ で `條① 基点=既定(器の在處から導いた repo 根・cwd に依らぬ) ―― ★倒した事を刷る(裁322952 乙)★` を刷つた ―― 倒した事が刷られる(乙)。門 sha16 e11f0d0142549086(00_start の刻 e11f0d0142549086 と同じ)。
4. **既成の束へ 0 字。** km-47・km-50 の印(通常 file の (相対名, sha256) の和)は 00_start が前を、60/96 が後を同じ器で取る。既成の臺帳は舊形(main 樹の根が基点)の儘 ―― 之が裁である。新臺帳は ★本束の raw/saiken/★ に在り、km-47/km-50 の束の門は今も既成の臺帳を見る。
5. **己の臺帳も束内相対(50・cd 束の根)。** 門 60 は KM_GATE_MANIFEST_BASE=束の根 で main/all を走らせ、加へて ★基点無しの一走(nobase)を門控に写す★ ―― 落ちて正。紙は己の門の數を書けぬ(紙の後に生れる)―― 期待: main rc 0 / all rc 0 / nobase rc 1・條① 実体無 = 母數。

## 1. 建て直し(20・㋐)―― 二束
| 束 | 既成の臺帳 | 旧 sha16 / B / 行 | 旧 項 | 讀めぬ | 頭違ひ | 束に無い | append rc | 新 封 sha256 | 新 B / 行 / 項 | 括つた | 対一致 / 相違 / 旧のみ / 新のみ | 員外 / disk | 判 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| km-47 | ashigaru-mac-3_km-47-yotsu-no-kazu-20260917_manifest.txt | 0bfdf2ff8b0092c2 / 3858 / 24 | 22 | 0 | 0 | 0 | 0 | 15e3c8f328fbbc802c35921c3e7ac0b23af6820cbefb2de77a74f5ed6f6e307a | 2912 / 24 / 22 | 1 | 22 / 0 / 0 / 0 | 8 / 30 | ★建て直せた★ |
| km-50 | km-50-kara-wa-todokazu-20260917_manifest.txt | ef413641b00e550a / 6502 / 41 | 39 | 0 | 0 | 0 | 0 | 43c8f0d73e13fd9ddfc51840189c5fa97ba13b7a66cac8c74102cf4684714d77 | 4708 / 41 / 39 | 0 | 39 / 0 / 0 / 0 | 8 / 47 | ★建て直せた★ |

- 手順: 既成の臺帳の行を ★讀み手と同じ器★(verify.py の paths_of・讀むのみ)で讀み、頭 `docs/evidence/<束>/` を落として相対名にし、★`cd <束の根>`★ で `karo_mac_manifest_append.py <新臺帳> <相対名…>` を呼んだ(append.py は cwd を root とし relpath を書く ―― 20 の subprocess cwd=束の根)。append.py sha16 f5ea5e1e85d64936。
- 括つた 1(km-47)= fixture の空白名 `fixture/naoshita/A10/a sha256_bbb… c.txt` ―― append.py の形②(空白名は括らねば讀み手が切り落す)。既成の臺帳でも括られて居た行である。
- 員外 km-47 8: ashigaru-mac-3_km-47-yotsu-no-kazu-20260917_gate.txt ashigaru-mac-3_km-47-yotsu-no-kazu-20260917_manifest.txt raw/kansa_send.err raw/kansa_send.out raw/osame_send.err raw/osame_send.out raw/tsuiichi_send.err raw/tsuiichi_send.out
- 員外 km-50 8: km-50-kara-wa-todokazu-20260917_gate_hashiri1.txt km-50-kara-wa-todokazu-20260917_gate_hashiri2.txt km-50-kara-wa-todokazu-20260917_manifest.txt raw/98_argv.txt raw/98_argv2.txt raw/99_mon_hashiri1.err raw/99_mon_hashiri2.err raw/A0_fumi.txt
- ★員外は「建て直しで落とした物」ではない★ ―― 既成の臺帳にも載つて居らぬ物(門控・臺帳自身・送信の出目 等)。母數は「既成の臺帳の項」であり「束の disk の file」ではない。
- 一行毎の対照は raw/20_tatenaoshi.tsv(束 / 相対名 / 旧 sha / 新 sha / 対一致 / 括つた)。

## 2. 對照(30・㋑)―― 二束 × 三本 × 三器(verify 直 / 門 min / 門 all)+ 参考 ㋓
- cwd = main 樹(㋓のみ束の根)。門 min = 臺帳を file としても渡す(條②〜⑤を清い一本に掛け條①を孤立させる)/ 門 all = 臺帳の項 悉くを file として渡す。
- 期待: ㋐ rc 0・一致 N・実体無 0 / ㋑ rc 1・一致 0・実体無 N / ㋒ rc 1・一致 0・実体無 N / ㋓ rc 0(cwd に依る故 使はぬ・第69弾 _after/98 の再現)。門 all は條①で判ず(條②〜④が既成束の file で鳴つても條①と混ぜぬ)。

| 束 | 對照 | 器 | 渡した | rc | 母數 | 一致 | 相違 | 実体無 | 讀めぬ | 旧形 | 基点の文言 | 期待通り |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| km-47 | ㋐明示基点=束の根 | verify | docs/evidence/km-47-yotsu-no-kazu-20260917 | 0 | 22 | 22 | 0 | 0 | 0 | 1 | 引数(明示) | True |
| km-47 | ㋑基点無し(既定=repo根) | verify | (無) | 1 | 22 | 0 | 0 | 22 | 0 | 1 | 既定(器の在處から導いた repo 根 /Users/momizimac/multi-agent-shogun ―― ★ | True |
| km-47 | ㋒出鱈目 | verify | /detarame/naki/ne | 1 | 22 | 0 | 0 | 22 | 0 | 1 | 引数(明示) | True |
| km-47 | ㋓参考 基点""・cwd=束の根 | verify | "" | 0 | 22 | 22 | 0 | 0 | 0 | 1 | 引数(明示) | True |
| km-47 | ㋐明示基点=束の根 | 門 min | 1 | 0 | 22 | 22 | 0 | 0 | 0 | 1 | 引数(明示) | True |
| km-47 | ㋐明示基点=束の根 | 門 all | 22 | 0 | 22 | 22 | 0 | 0 | 0 | 1 | 引数(明示) | True |
| km-47 | ㋑基点無し(unset・既定=repo根) | 門 min | 1 | 1 | 22 | 0 | 0 | 22 | 0 | 1 | 既定(器の在處から導いた repo 根 /Users/momizimac/multi-agent-shogun ―― ★ | True |
| km-47 | ㋑基点無し(unset・既定=repo根) | 門 all | 22 | 1 | 22 | 0 | 0 | 22 | 0 | 1 | 既定(器の在處から導いた repo 根 /Users/momizimac/multi-agent-shogun ―― ★ | True |
| km-47 | ㋒出鱈目 | 門 min | 1 | 1 | 22 | 0 | 0 | 22 | 0 | 1 | 引数(明示) | True |
| km-47 | ㋒出鱈目 | 門 all | 22 | 1 | 22 | 0 | 0 | 22 | 0 | 1 | 引数(明示) | True |
| km-50 | ㋐明示基点=束の根 | verify | docs/evidence/km-50-kara-wa-todokazu-20260917 | 0 | 39 | 39 | 0 | 0 | 0 | 0 | 引数(明示) | True |
| km-50 | ㋑基点無し(既定=repo根) | verify | (無) | 1 | 39 | 0 | 0 | 39 | 0 | 0 | 既定(器の在處から導いた repo 根 /Users/momizimac/multi-agent-shogun ―― ★ | True |
| km-50 | ㋒出鱈目 | verify | /detarame/naki/ne | 1 | 39 | 0 | 0 | 39 | 0 | 0 | 引数(明示) | True |
| km-50 | ㋓参考 基点""・cwd=束の根 | verify | "" | 0 | 39 | 39 | 0 | 0 | 0 | 0 | 引数(明示) | True |
| km-50 | ㋐明示基点=束の根 | 門 min | 1 | 0 | 39 | 39 | 0 | 0 | 0 | 0 | 引数(明示) | True |
| km-50 | ㋐明示基点=束の根 | 門 all | 39 | 0 | 39 | 39 | 0 | 0 | 0 | 0 | 引数(明示) | True |
| km-50 | ㋑基点無し(unset・既定=repo根) | 門 min | 1 | 1 | 39 | 0 | 0 | 39 | 0 | 0 | 既定(器の在處から導いた repo 根 /Users/momizimac/multi-agent-shogun ―― ★ | True |
| km-50 | ㋑基点無し(unset・既定=repo根) | 門 all | 39 | 1 | 39 | 0 | 0 | 39 | 0 | 0 | 既定(器の在處から導いた repo 根 /Users/momizimac/multi-agent-shogun ―― ★ | True |
| km-50 | ㋒出鱈目 | 門 min | 1 | 1 | 39 | 0 | 0 | 39 | 0 | 0 | 引数(明示) | True |
| km-50 | ㋒出鱈目 | 門 all | 39 | 1 | 39 | 0 | 0 | 39 | 0 | 0 | 引数(明示) | True |

- 外れ 0 行。★三本とも期待通り ―― 明示基点で 一致 N / 実体無 0 / rc 0、既定基点と出鱈目で 実体無 N / rc 1。建て直せて居る。★
- ★四数の讀み方★: 「実体無 N」は ㋑㋒ で母數と等しい ―― 照合器自身の註「実体無は disk に物が無いとは限らぬ・基点が違ふ事が在る」の通り、同じ臺帳が ㋐ で 実体無 0 になる。∴ ㋑ の rc 1 は ★建て直しが正しい證★(束内相対の臺帳は既定基点で落ちねばならぬ ―― 落ちなければ path が repo 根からの相対の儘である)。
- 旧形 1(km-47・全走)= 括つた空白名の行。讀み手は引用符を含む行を「旧形」と札し ★拒まぬ★(裁 321353⑴)。之は禁破りではなく、空白名にとつて括りは唯一讀める形(append.py 形②)。★讀み手の札「旧形」は「新規に書いた空白名の括り」と「古い引用符の行」を見分けぬ★ ―― 數 1 は其の両方を意味し得る。
- 條⑤ byte和(門 all): km-47 141818 / km-50 223187(閾 10MB 未満)。門 min: 2912 / 4708(= 臺帳自身の bytes)。

## 3. 己の臺帳と門(50・59・60)―― 紙の後に生れる故 期待のみ書く
- 50: `cd /Users/momizimac/multi-agent-shogun/docs/evidence/km-70-daichou-no-ne-wo-sokunai-soutai-e-tatenaosu-20260917` → append.py <臺帳> 紙 + raw/ 配下の通常 file(_after/ と門控は員外)。基点 = 束の根。
- 59: 門の前に 條②③④ と 0byte を己で当てる(鳴つたら直してから門へ)。
- 60: 錠(raw/ 0555/0444)→ 歩哨 → 門 selftest / main(紙+臺帳・基点明示)/ all(項 悉く・基点明示)/ ★nobase(main と同じ argv・環境変数 unset)★ → 門控 `ashigaru-mac-1_km-70-daichou-no-ne-wo-sokunai-soutai-e-tatenaosu-20260917_gate.txt` + `_after/60_gate_top.r70.txt`(三走の stderr 逐語)→ 禁域と既成束の印 前後。期待 main 0 / all 0 / nobase 1。
- 96: 門の後の raw/ に後から生れた物 0・錠の下で 1 byte 書けぬ(EACCES)・己の臺帳を verify 基点=束の根 → 一致 N / 基点無し → 実体無 N・既成束の印 前後 同。

## 4. 本弾が意味せぬ事(八つ)
1. **「建て直せた」は「既成の臺帳が改まつた」を意味せぬ。** km-47/km-50 の束には一字も書いて居らぬ(印 前後で證す)。既成の臺帳は舊形の儘固定(裁)。新臺帳は km-70 の raw/saiken/ に在る ―― km-47/km-50 の門が新臺帳を見る様になるかは家老の采配。
2. **㋐ の「一致 N」は「file が正しい」を意味せぬ。** 新旧の sha256 が同じ事(対一致 N)を言ふのみ。旧の sha が正しいかは第47・50弾の監査の事であり本弾は觸れぬ。
3. **㋑ の「実体無 N」は disk の欠けを意味せぬ。** 同じ臺帳が ㋐ で実体無 0。基点の違ひのみ。
4. **旧形 1(km-47)は「引用符禁を破つた」を意味せぬ。** 空白名の括り(形②)であり讀める唯一の形。讀み手の札は其れを見分けぬ。
5. **門 all rc 0 は「束の file が悉く清い」を意味せぬ。** 渡したのは臺帳の項(22/39)であつて員外(8/8)は渡して居らぬ ―― 員外の條②③④は測つて居らぬ。
6. **㋓(基点 "" ・cwd = 束の根)の rc 0 は「使へる形」を意味せぬ。** cwd に依る(第69弾 98 で既定基点が cwd に依らぬ様に直された理由其の物)。門に KM_GATE_MANIFEST_BASE="" を渡した時の挙動(門は空文字も set と見る・cwd 相対の明示として通す・L193 の註)は ★本弾で測つて居らぬ★。
7. **三本の對照が「門の基点の口は正しい」を悉く證するのではない。** 測つたのは set(束の根)/ unset / set(出鱈目)の三態のみ。空文字・空白のみ・相対 path・末尾 / 無し 等は未測(乙の env_state は閾の口の話で、基点の口には無い)。
8. **「all の rc が條①と同じ向きだつた」は「all の rc だけで條①を判ぜる」を意味せぬ。** 既成束の file が偶々 條②③④ で鳴らなかつた(鳴 0)故に一致しただけ。rc は條で割つて讀め(30 は割つて書いた)。

## 5. 宣⇔實 ―― 實は _after/63_sent.txt(両基準)
- 起 2026-09-17T05:35:25(着手便・器 05)/ 宣 = 起 + 42 分 = 06:17:25 / 端点 = 納め便 1 本目を inbox_write.sh へ渡す直前の date 刻。建て方 = 器 10 × 2.78 分/器 × 1.5(2.78 = 67: 3.95 / 68: 2.39 / 69: 2.01 の平均・第69弾は 3.2 で +27.9 分の過大 → 平均を三弾へ延ばした)。家老基準は札が無い故 発注便の刻 05:29:46 を起とする。
- 宣は二方向に外れる ―― 過大なら過大と、過少なら過少と 63 が書く。

## 6. 己の疵(消さず残す)
1. 05 の胴が 366 → 330 → 312 字と三度 己の G5(≤300)で鳴つた(.first/.second/.third)。「削るより割れ」の條に反して削つた ―― 着手便は一通の條を優先した。四走目 300 字で通。
2. 束の骨組み(mkdir・kaki/10_run の cp・.first の cp)と 20 の一行の sed patch(`b chr(10)` の書き損じ)を手で打つた。
3. 札 queue/tasks/ashigaru-mac-1.yaml は km-69 done の儘で km-70 の札は無い ―― 命は箱の便(msg_20260917_052946_7760b288)のみ。62 は km-70 の札が在れば印を打ち、無ければ「札無し」と 63 に書く(km-69 の札へは触れぬ)。
4. 主樹の枝名が本弾の間に変つた(会話の頭 `karo-mac/km-gate4-kou-otsu-20260917` → 00_start の刻 `karo-mac/km-shikii-yokotenkai-20260917`・HEAD は a6587c0 で同じ)―― 家老が主樹で働いて居る。席は置くのみ。

## 7. 出處
- 器: raw/00_start.py(起・宣・則・印)/ 05_chakushu.py(着手便・門 G1〜G7・對照 3)/ 10_run.py / 20_tatenaoshi.py / 30_taishou.py / 50_build_manifest.py / 59_prescan.py / 60_gate_run.py / 62_letters.py / 67_git_add.py / 96_after.py / 70_paper.py(此の紙)/ kaki.py。
- 生器(讀むのみ・sha16): append.py f5ea5e1e85d64936 / verify.py a507c998c7bd6485 / 門 e11f0d0142549086。禁域の前後は 00_start ⇔ 60 ⑤。
- 着手便: 1 本 'msg_20260917_053525_c17f00aa'・300 字・inbox_write rc 0。
