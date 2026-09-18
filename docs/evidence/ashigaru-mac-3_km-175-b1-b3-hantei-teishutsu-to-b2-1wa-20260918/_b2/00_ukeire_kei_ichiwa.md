# B2 ―― 残 117 話の ★演出テンプレ受入形★ を「一話だけ」切る

> **一話しか切らぬ。★残 116 話は次弾へ残す★**(家老令 km-175 ㋔ 逐語)。
> 刻 `2026-09-18T17:29:39+0900` ／ 席=專任3(ashigaru-mac-3) ／ 板 `6caf8ca2`(B2) ／ 親裁 `332152`。

**★此の紙が新たに定めた規則は 0 条である★** ―― 受入の門は既に製品樹に在り、本紙は其れを
**名指して並べ、一話を実際に通した出目を置いた**だけである(Anti-Duplication Rule 順守)。

## 四札(此の紙の数が何處から来たか)

| 札 | 実 |
|---|---|
| 刻 | 2026-09-18T17:29:39+0900(器 driver/60・61・62・65 の走りは各 raw/*.tsv の刻) |
| 根と深さ | `/Users/momizimac/DentalBI/frontend/src/features/child-passport/story-engine/`(読取のみ)＋本束 `_b2/` |
| rc | CLI 本走り **0** ／ 陰性対照 **1** ／ app の test **0**(悉く subprocess の returncode ―― ★管を通さぬ★) |
| 対照 | ⑴陰性= `authoring-sample-broken-cap.md`(必ず落ちる紙)⑵suite 内蔵の陽性對照(空表→未解決 15)⑶『26 本現に走つた』(0 本の緑は緑に非ず) |

---

## 一 ①受入形の ★項目と型★(18 行)

各行の「定義の在処」が **★唯一の出所★** である ―― 本紙は写しを持たぬ(写せば二重定義に成る)。

| 項目 | 型 | 定義の在処(★唯一の出所★) | 條 |
|---|---|---|---|
| episode.id | string | frontend/src/features/child-passport/story-engine/episodes/episode.ts:16 | 『S<数>-EP<数>』・file 名と一致(EPISODE_ID_RE) |
| episode.title | string | frontend/src/features/child-passport/story-engine/episodes/episode.ts:17 | 空でない string |
| episode.visit | number | frontend/src/features/child-passport/story-engine/episodes/episode.ts:19 | ★1 以上の整数★ |
| episode.season | string | frontend/src/features/child-passport/story-engine/episodes/episode.ts:21 | 'S3' 等の season 記号 |
| episode.audience | string | frontend/src/features/child-passport/story-engine/episodes/episode.ts:23 | '5-6' 等の年齢帯 |
| episode.mission | string | frontend/src/features/child-passport/story-engine/episodes/episode.ts:25 | 脚本の 🦷 行 をそのまま |
| episode.badge | string | frontend/src/features/child-passport/story-engine/episodes/episode.ts:27 | 脚本の 🏅 行 をそのまま |
| episode.parent_explanation_ref | string | frontend/src/features/child-passport/story-engine/episodes/episode.ts:34 | ★保護者解説の id('S3-EP1' 形)★ ―― 1:1 の鍵 |
| scenes[] | Scene[] | frontend/src/features/child-passport/story-engine/episodes/episode.ts:39 | ★1 場 以上★・場 id は 'episode.id-' で始まる・id 重複禁 |
| scene.background | string | frontend/src/features/child-passport/story-engine/types.ts:118 | 同じ場所は同じ名を使ひ回す |
| scene.actors[].id | ActorId(10 値) | frontend/src/features/child-passport/story-engine/types.ts:6 | you/papa_dino/koron/… の 10 値のみ |
| scene.actors[].anim | AnimName?(5 値) | frontend/src/features/child-passport/story-engine/types.ts:27 | idle/blink/walk/joy/surprise・既定 idle |
| scene.actors[].position | Position(3 値) | frontend/src/features/child-passport/story-engine/types.ts:32 | left/center/right |
| scene.lines[].speaker | SpeakerId(11 値) | frontend/src/features/child-passport/story-engine/types.ts:22 | actor 10 値 + narrator |
| scene.lines[].choices | [opt,opt]? | frontend/src/features/child-passport/story-engine/types.ts:95 | ★丁度 2 択★・label ≤20 字 |
| scene.effects[].type | EffectType(10 値) | frontend/src/features/child-passport/story-engine/types.ts:43 | enter/exit/pause/… transition_mp4 |
| scene.effects[].at | number | frontend/src/features/child-passport/story-engine/types.ts:110 | 同 scene の lines index |
| (門)未知 key | ― | frontend/src/features/child-passport/story-engine/episodes/validateEpisode.ts:52 | ★封筒・top-level とも 未知 key は赤★ |

### 一.二 ★『項目の数』は数へた階で変はる★(板の註 31 との突合)

板 `38dcde86` は「全階層 再帰= episode.\* 9 + scenes.\* 22 = 31／scene 階のみなら 6」と記す。
當席の表は **18 行**。★之は矛盾ではなく、数へた階が違ふ★ ―― 器 `driver/61` で並べた:

| 何を数へたか | 数 | 言 |
|---|---|---|
| Episode の宣言 field | 2 | episode + scenes の 2 ―― ★之を『項目』と呼ぶ者は居らぬ★ |
| episode.* (meta 8 + scenes[] 1) | 9 | 板の『episode.* 9』と ★一致★ |
| Scene の宣言 field | 6 | 板の『scene 階のみなら 6』と ★一致★ |
| scenes.* 再帰(甲=参照毎) | 24 | 板の『scenes.* 22』と ★食ひ違ふ★ |
| scenes.* 再帰(乙=同型一度) | 22 | 板の『scenes.* 22』と ★一致★ |
| Episode 全階層 再帰(甲) | 34 | 板の『31』と ★食ひ違ふ★ |
| Episode 全階層 再帰(乙) | 32 | 板の『31』と ★食ひ違ふ★ |
| ★當席の受入形の表★ | 18 | ★受入で人が書く項目★= episode 階 9 + scene 階の代表 8 + 門 1 ―― 再帰の総数ではない |
| ★差 1 の始末★ 乙 32 − 封筒の鍵 episode 1 | 31 | 板の 31(=episode.* 9 + scenes.* 22)と ★一致★ ―― ★差は丸めず名指した★: 板は封筒の鍵 `episode` を項目に数へず、當席の再帰は数へる |
| ★陰性対照★(在らぬ型) | 0 | 0 が正 ―― 解けぬ型を黙つて数へぬ |

**★差 1 を丸めず名指す★**: 板の 31 と當席の再帰(乙)32 の差は **封筒の鍵 `episode` を項目に
数へるか否か** の一点であり、他に食ひ違ひは無い。甲(参照毎)なら 34/24 に成る ――
`choices?: [SceneChoiceOption, SceneChoiceOption]` の同型 2 参照を二度展開する故。
**∴ 『31』も『22』も『18』も『6』も正しく、★足してはならぬ★。**

---

## 二 ②実データを ★1 話だけ★ 流し込んだ見本

**★見本は作らず、現に書かれた 1 話を使つた★** ―― 脚本 md は此の mac に **15 本**(15 話分)在り、
其の内 `S3-EP1` を **本束へ写して** 製品樹の CLI に通した。**製品樹へは一字も書いて居らぬ**。

```
cd /Users/momizimac/DentalBI/frontend
npm run --silent validate:episode-md -- <本束の写し>/_b2/S3-EP1.md
```

(`tools/md2scene.ts:414` が `process.argv[2]` から path を取る故、★製品樹の外の紙でも通る★ ――
之が「他席の生きた樹へ書かずに実データを通す」道である。)

| 何を | 在処 | 数 or rc | 言 |
|---|---|---|---|
| 脚本 md(現物) | frontend/src/features/child-passport/story-engine/episodes/scripts/S3-EP1.md | 2396 | c9ad47d2e6ab71f2ef0889e1085f43c67cf091009f5648aebc1967e0752c2a00 |
| 写し(本束) | _b2/S3-EP1.md | 2396 | c9ad47d2e6ab71f2ef0889e1085f43c67cf091009f5648aebc1967e0752c2a00 |
| 載つて居る data | frontend/src/features/child-passport/story-engine/episodes/S3-EP1.json | 5308 | 699c6fae562cc5de8c009f27af24198e23a72aeb6f542acdf78ac89a67efd062 |
| CLI 本走り rc | npm run --silent validate:episode-md <写し> | 0 | 出目 4520 字 |
| ★陰性対照★ cap 束 rc | frontend/src/features/child-passport/story-engine/episodes/scripts/_sample/authoring-sample-broken-cap.md | 1 | ★落ちた(正)★ [md2scene] fail-closed(静的門番): scene(S9-EP21-1): at=0 の effect 束が cap(3 |
| 場の数(変換 / 載つて居る) | scenes | 3 / 3 | 一致 |
| 行の数(変換 / 載つて居る) | lines | 14 / 14 | 一致 |

**読み方**: 変換の出目と ★現に載つて居る `S3-EP1.json`★ が **場 3 / 3・行 14 / 14** で一致した。
∴ 受入形は「絵に描いた型」ではなく、**★現に 15 話が通つて居る型★** である。
脚本 md `sha256=c9ad47d2e6ab71f2ef0889e1085f43c67cf091009f5648aebc1967e0752c2a00` ／ 載つて居る data `sha256=699c6fae562cc5de8c009f27af24198e23a72aeb6f542acdf78ac89a67efd062`。

陰性対照 `authoring-sample-broken-cap.md` は **rc=1** で落ち、門番の文言は
`at=0 の effect 束が cap(3) を超える(実測 4)` であつた ―― **★門は現に噛んで居る★**。

### 二.二 ★118 話目を実データで埋める事は出来ぬ★(不在を黙つて埋めぬ)

| 何を | 本数 | 言 |
|---|---|---|
| 脚本 md(episodes/scripts) | 15 | S3-EP1.md, S3-EP10.md, S3-EP11.md, S3-EP12.md … |
| 話の data(episodes/*.json) | 15 | S3-EP1.json, S3-EP10.json, S3-EP11.json, S3-EP12.json … |
| ★残 117 話の脚本★ | 0 | ★此の mac に無し★(Box 『てりはキョウリュウおうこく_物語制作』が出所・find で *物語* 0 件・∴ ★118 話目を実データで埋める事は出来ぬ★) |

残 117 話の脚本は **0 本** ―― 出所は Box『てりはキョウリュウおうこく_物語制作』であり、
此の mac の disk に無い。**∴ 『117 話分の受入形を通した』とは書けぬ。書けるのは
『受入形は 15 話で現に立ち、118 話目も同じ CLI で受かる』までである。**

---

## 三 ③『保護者解説 1:1 維持』を ★何で測るか(一行)★

> **★`episodes/*.json` の `parent_explanation_ref` を app 自身の解決器 `resolveParentExplanation` に
> 掛け、①話数=鍵数 ②未解決 0 ③孤児 0 ④ref の重なり 0 ―― の四条が同時に立つ事で測る
> (器= 製品樹の既存 test `episodes/__tests__/episodes.test.tsx`・實測 rc=0 / 26 本通 / skip 0)。★**

**★器は二つ在り、上下が在る★**:

| 何を | 値 | 言 | 判 |
|---|---|---|---|
| 器 | npx vitest run src/features/child-passport/story-engine/episodes/__tests__/episodes.test.tsx | cwd=/Users/momizimac/DentalBI/frontend | 2026-09-18T17:27:47+0900 |
| rc(★管を通さぬ★) | 0 | 0 が緑 | ★緑★ |
| 走つた本数 | 26 | 母數 26 | ★0 本で緑は緑に非ず★ ―― 26 本現に走つた |
| skip | 0 | SKIP=FAIL の條 | ★skip 無し★ |
| 1:1 の断(逐語) | it('2. 1:1: 15 話の ref は自話の id と等しく、重複が無い(link の形は不斷)', () => { | episodes.test.tsx | - |
| ★内蔵 負対照★ | it('4. ★陽性對照★: 同じ器へ ★空の雛形★ を渡せば 15 件が未解決へ戻る(上の 0 が盲でない證)', () => { | 空表を渡すと未解決が 15 に成る断 | ★対照在り★ |
| 己の二の器(regex) | driver/60 → raw/63_b2_hogosha_1to1.tsv | 話15・鍵15・未解決0・孤児0・重なり0 | ★鍵の在否のみ ―― 中身の空は見ぬ(∴一の器が要る)★ |

**一の器(app の解決器)が上である理由**: `hooks/useParentExplanationLink.ts` の `isS3S4EntryEmpty` が
**★空の雛形を fail-closed で null にする★** ―― ∴ **「鍵が在る」は「解決する」の證に成らぬ**。
己の regex(二の器)は鍵の在否しか見ぬ故、單独で 1:1 を宣してはならぬ。

**實測**: 話 15 ／ 解説の鍵 15 ／ 未解決 0 ／ 孤児 0 ―― **1:1 は ★立つ★**。

| 何を | 数 | 言 |
|---|---|---|
| 話の数 | 15 | episodes/*.json の episode.id |
| ref の数(重複除く) | 15 | ★重なり 0 件★(1:1 ゆゑ 0 が條) |
| 解説の鍵の数 | 15 | parentExplanations.ts + .S3S4.ts の 'S3-EP1': explanation( 行 |
| ★未解決(ref→解説が無い)★ | 0 | 0 件 |
| ★孤児(解説→話が無い)★ | 0 | 0 件 |
| 1:1 か | ★立つ★ | 條= 話数=鍵数 かつ 未解決0 かつ 孤児0 かつ 重なり0 |

---

## 四 ★二重実装を作らなんだ證★(受入の門は既に在る)

| 受入の何を | 既に在る門(★唯一の出所★) | 當席が足した物 |
|---|---|---|
| 脚本 md の書式 | `episodes/AUTHORING.md` §1 書式(4段)・§3 cap 宣言・§4 演出行・§5 禁則 | **0 行** |
| md→JSON 変換と型の当否 | `tools/md2scene.ts` → 動的 import で `validateEpisode`(`md2scene.ts:376`) | **0 行** |
| schema へ丸投げ出来ぬ検め | `validator.ts` の `checkSceneStaticGate`(`md2scene.ts:428`) | **0 行** |
| 場の中身の可否 | a2 の `validateScene`(`validateEpisode.ts` が委ねる・二重定義を作らぬ) | **0 行** |
| 1 話を足す手順 | `episodes/README.md` §9.2「10分手順」 | **0 行** |
| 受入形の雛形 | `episodes/TEMPLATE.json`(既存 test『TEMPLATE.json は そのままで valid』が守る) | **0 行** |
| 1:1 の断 | `episodes/__tests__/episodes.test.tsx` 2.(1:1) / 3.(未解決0) / 4.(空表→15) | **0 行** |

**∴ B2 の『受入形』は ★新たに設計する物ではなく、既に在る物を一話で實證する物★ であつた。**

---

## 五 ★此の紙が意味せぬ事★

| 書いた事 | ★意味せぬ事★ |
|---|---|
| 受入形の項目 18 行を並べた | 18 が『全ての field』ではない(再帰なら 32・板の数へ方なら 31) |
| S3-EP1 が CLI rc=0 で通つた | 残 117 話が通る證に成らぬ(★脚本が此の mac に無い★)。通るのは『同じ書式で書かれた 1 話』のみ |
| 場 3 / 3・行 14 / 14 が一致した | 画で正しく再生される證に成らぬ ―― ★通し再生の實視は browser を要し、本弾の外★ |
| 1:1 が立つ(話 15 / 鍵 15) | S5 以降・118 話目の解説が書かれて居る證に成らぬ。立つのは ★今 在る 15 話の範★ |
| app の test が rc=0 / 26 本通つた | frontend 全 suite の青を意味せぬ ―― ★先住の赤(6 file / 20 落ち)は名指すのみで触れて居らぬ★(家老令 ㋑) |
| 門が陰性対照で rc=1 と落ちた | 門が悉くの誤りを捕へる證に成らぬ(捕へたのは cap 束 一種) |

---

## 六 ★己の疵(報ずる前に己で捕へた)★

| 疵 | 何が起きたか | 如何に直したか |
|---|---|---|
| ⑴ 器が 0 を刷つて rc=0 の儘だつた | `driver/61` 初版の field regex が行末 `;` を要求したが、此の樹の TS に `;` は無く、Episode/EpisodeMeta/Scene 悉く ★field 0★ と刷つた | regex を `;?` へ改め、源の形を `grep -n` で先に見た。★『rc=0』は『測れた』の證に成らぬ★ |
| ⑵ 負対照の檢出子が行單位で AND を取つた | `emptyTable` と `unresolved` は別行ゆゑ、現に在る對照を ★『対照が見えぬ』★ と刷つた | `it(` の塊で切り直し『★対照在り★』を得た。★對照の不在は對照の不在を意味せぬ★ |
| ⑶ test の出目を一度 `/tmp` へ置いた | `--reporter=basic` が此の版に無く落ちた折、出目を `/tmp/.vt.out` へ採つた(證を /tmp に置く禁を踏んだ) | 器 `driver/62` に積み直し、out/err/rc を kaki で ★束の中へ★ 収めた |

---

## 七 次弾へ残す物

- **★残 116 話★**(家老令 逐語「残116話は次弾へ残せ」) ―― 脚本の入手(Box)が先。
- **通し再生の實視** ―― browser を要す(板 `6caf8ca2` の『通し再生の実視(AI6h)』)。
- **S5 以降の保護者解説** ―― 1:1 の範を広げる時は `parentExplanations.S3S4.ts` へ貼る(★埋めるな★の註が在る)。
