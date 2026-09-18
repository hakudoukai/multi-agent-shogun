# km-196 ―― 手元 main が origin/main より 29 commit 先んじる ―― 誰の作か・押す要否の census(紙のみ・押さず)

- 板 = queue/tasks/ashigaru-mac-1.yaml `tsugi_no_tama_196_20260918T2102`(task_id km-196・総監督 seq334049 の御下命・板 b774c90f)/ 書手 ashigaru-mac-1 / 宛 karo-mac
- 刻 = 紙を書き始めた刻 2026-09-18T21:13:13+0900 / 着手便は km-195 の納めの後(順)/ 測り 21:09〜21:11
- 枝 = `ashigaru-mac-1/km-196-tesoto-main-29-no-census-20260918`(origin/main 6bde7170ce574090a6139ba2dfe3aa4cb6db8634 から・己の樹 ~/wt/a1-km196)。★押さず・ls-remote(読み)のみ★。束名は家老の指定。
- ★先に「手元 main」の正体★: 家老・総監督の申す `d8e3aa58b9eeac6f97f0d60928fbdc40c7c93f11` は refs/heads/main ではない。refs/heads/main = `82f23b429a03b88c504cb64917ff37647c07e0a5`(origin/main より先んず ★0★)。d8e3aa58 は ★共有樹の HEAD = 枝 ashigaru-mac-3/km-51-tasekki-no-hakari-wo-kami-de-yabure-20260917 の tip★(席3 の枝)。∴ 29 は「main」でなく「共有樹が checkout して居る席3 の枝」が origin/main より先んずる数。d8e3aa58 は origin/main の裔でない(merge-base --is-ancestor no = 枝分かれ)。

## ㋐ 結語

1. ★名簿(raw/10)★: origin/main..d8e3aa58 = 29 本。author も committer も ★29/29 が同一 identity「MomiziMac <momizimac@MomiziMac-mini.local>」★(此の Mac の全席が同じ git identity)。author 刻≠committer 刻は 1 本。
2. ★29 は SHA の数・変更の数でない★(㋐): `git cherry origin/main d8e3aa58` = ★+27 / −2★(−2 = f0d59a3b・f2bfa26a は同じ patch が上流に在る)。patch-id(上流直近 200)でも一致 2 / 無 27(raw/11・13)。∴ 真に未到達な patch は 27 本。
3. ★誰の作か(㋑・二形)★: 形1(欄)= 甲 0 / 乙 0 / 丙 0 / ★丁(判じ得ぬ・同一 identity)29★ ―― 欄では分けられぬ(0 に丸めず 29 と書く)。形2(題の字面)= 甲(足軽mac 系: 專任3 14・專任2 2)16 / 乙(家老)4 / 丙(其の他)0 / 丁(km 番のみ・判じ得ぬ)9 → 和 29。Co-Authored-By 行 = 25 本(悉く `Claude Opus 5`・書手の席は判じ得ぬ)。★己の器 scripts/checks/* に触れる commit = 9 本★(file 延べ 9)。
4. ★押す要否の材(㋒・判は下さぬ)★: ⑴ file が origin/main に在る(既存を触る)= 延べ ★5★ / 無い(新設)= ★1390★(殆どが docs/evidence の束)。⑵ 同じ path(scripts/checks/*)を触る他の枝 = 手元 refs/heads に ★70 本余★(raw/20_bunrui_summary.txt 列挙)。⑶ 29 本を含む手元の枝 = 古い 6 本は 59 枝の土台、新しい 11 本は 1〜2 枝のみ(raw/21)。
5. ★遠の在否(㋓・raw/22〜24)★: 陽性 = `ls-remote origin refs/heads/main` 1 行(6bde7170)。29 本の 40 桁を ls-remote 全 367 ref に掛けると ★14 行★(0 でない)= 10 本が遠の ref の tip(karo-mac/gate4-20260909=refs/pull/12/head・gate5=PR#13・manifest-verify=PR#14 等)。origin/* の枝に ★祖先として含まれる本 = 18 / 29★・★遠に一本も無い(真に未到達)= 11 本★ = 6ba8fcb2・0039e132・260f2a06・75aa92f2・f02c7d90・3fe709b1・9af1a96c・4e4cfeeb・36b88f93・1df72e96・d8e3aa58(★悉く 09-17 08:07 以降の 專任3 の evidence 束 = 席3 の枝の尾★)。gate4.sh に触れる 4 本(a6587c02/e8470d8c/dafb2402/707df791)は ★悉く遠の枝に在り★(PR#12/#13/家老の枝・3〜6 枝が含む)―― origin/main に無いだけ。
6. 推し(判は総監督/委員長・裁 seq326810/327131): 27 patch の内 ⑴ 6 本(09-09〜09-10・門・臺帳照合)は PR#12/13/14 の頭に既に在り = 押す要は無く ★merge の判★ ⑵ 11 本(席3 の evidence 束)は席3 の枝で未押 = ★席3/家老の押し判★ ⑶ 残る 10 本(09-17 の專任2/3 束・家老の門の直し)は遠の他枝に含まれて居る = 押す要は無く merge の判。★當席が押す物は無い。★

## ㋑ 名簿(raw/10_meibo.tsv・29 行)

列 = 40 桁 / author 刻 / committer 刻 / author / committer / file 数 / +/− / 題。刻の範囲 2026-09-09T05:27 〜 09-18T17:52。最大 236 file(99ea2984・專任3 第46弾)・最小 1 file。増減の基準 = 各 commit の親(`git show --numstat`)。

## ㋒ cherry・patch-id(raw/11・12・13)

- `git cherry origin/main d8e3aa58`: `-` 2(f0d59a3b6315058b2af40bd57689b397243e32c9・f2bfa26a163dbee334861bd80bb0bd8affa0636d)・`+` 27。
- patch-id(--stable)を origin/main の直近 200 commit と照合: 一致 2(同じ 2 本)・無 27。★二器が一致★。
- ∴ 「29 本先んず」の実 = 27 patch(2 は cherry-pick 済)。

## ㋓ 誰の作か(raw/20)

| 形 | 甲(足軽mac 系) | 乙(家老mac) | 丙(其の他) | 丁(判じ得ぬ) | 和 |
|---|---|---|---|---|---|
| 形1 欄(author/committer) | 0 | 0 | 0 | ★29★(同一 identity) | 29 |
| 形2 題(專任N/家老/km) | 16(專任3 14・專任2 2) | 4 | 0 | 9(evidence(km-N) のみ・誰の束か題に無い) | 29 |

- 形1 と形2 の食ひ違ひ = 29(形1 は悉く丁)。★欄では誰の作かを判じ得ぬ★ ―― 此の Mac の git identity が席ごとに分かれて居らぬ(名指す・直さぬ)。
- Co-Authored-By: 25 本・悉く「Claude Opus 5 <noreply@anthropic.com>」(model の名・席の名でない)。
- scripts/checks/* に触れる 9 本: 707df791・dafb2402・e8470d8c・f0d59a3b・2320dbbb・f2bfa26a・363d5fb0・a6587c02・ab2a1f16(家老の門・臺帳照合・閾の横展開)。

## ㋔ 押す要否の材(raw/21・23・24・判は下さぬ)

| 群 | 本 | 遠の在否 | 手元の枝の土台 | 材 |
|---|---|---|---|---|
| A: 09-09〜10 門・臺帳照合 | 6(707df791 dafb2402 e8470d8c f0d59a3b 2320dbbb f2bfa26a) | 遠の枝に在り(PR#12/13/14 の head 等・6 枝) | 59 枝 | 2 本は cherry-pick 済・4 本は PR 待ち = 押す要無し・merge 判 |
| B: 09-17 家老の直し・專任2/3 束 | 12(f626f200〜a6587c02・ab2a1f16) | 遠の枝に在り(3〜6 枝) | 11〜55 枝 | 押す要無し・merge 判 |
| C: 09-17 08:07〜09-18 席3 の束 | ★11★(6ba8fcb2〜d8e3aa58) | ★遠に無い★ | 1〜2 枝(席3 の枝と main) | 席3 の枝 ashigaru-mac-3/km-51… の押し = 席3/家老/委員長の判 |

- 既存 file を触る変更は延べ 5(悉く A・B の門)・新設 1390(束)。同じ scripts/checks/* を触る手元の他枝 70 余(衝突の種は門の直しの重なり・raw/20_bunrui_summary.txt)。

## ㋕ 対照(raw/22)

- 陽性: `git ls-remote origin refs/heads/main` = 1 行 `6bde7170…`(器は生きて居る)。
- 陰性(裁の定石の形で): 29 本の 40 桁 × ls-remote 全 ref(367)= ★14 行★ = 0 でない ―― ∴「29 本は未到達」は ★偽★・正は「origin/main に未到達 29・遠のどの枝にも無いのは 11」。
- 遠に在る當席の枝 = 10 本(km-70・71・71b・72・86・92・97・140・167・a1-jishu = 委員長の代行押し)。

## ㋖ 測れぬ物

- 他 PC の remote 状態・push 権(當席は押さぬ・試さぬ)・reflog の外に落ちた物。
- 各 commit の「誰の席が打つたか」は git の欄からは測れぬ(同一 identity)。題と束の名からの読みは形2 として別に置いた。
- patch-id の照合は上流直近 200 commit まで(其の先は測れぬ)。

## ㋗ 疵

⑴ 「手元 main」の語が refs/heads/main と共有樹 HEAD(席3 の枝)で食ひ違ふ事を先に名指した(家老・総監督の疵ではなく語の粗)。⑵ 着手便は km-195 の納めの後(順)。

## 宣⇔實

宣ETA = 着手便に書く。實 = 納め便の刻。
