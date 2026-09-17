# 家老mac ―― origin の mac 系枝 60本を歩き、★不要 15本★を名指す(消さず)

裁 **seq325493**(総監督→家老mac)逐語:「origin ls-remote で自分の枝を数え、不要な枝が在れば★消さず★「不要」と名指しで報せ(消すのは総監督)」。

- 刻: **2026-09-17T14:39:02+09:00**(器が自ら刷つた・`raw/50_summary.txt` 一行目)
- 器: `driver/10_eda_bunrui.py`(読取のみ・枝を一本も触らぬ)
- 出: `raw/10_lsremote.txt` / `raw/20_mac_eda.tsv` / `raw/30_hoyuu.tsv` / `raw/40_fuyou.tsv` / `raw/50_summary.txt`

## 一 数

| 欄 | 値 |
|---|---|
| origin 全枝 | **240**(`git ls-remote --heads origin` rc=0) |
| mac 系 母數 | **60**(`karo-mac/*` ＋ `ashigaru-mac-*/*`) |
| 手許に物の無い枝 | **0**(60/60 `git cat-file -e <sha>^{commit}` rc=0 ―― 測れぬ枝は無い) |
| ★不要★ | **15** |
| 残 | **45** |
| 残枝に保持先を持たぬ不要枝 | **0** |

## 二 「不要」の定義 ―― ★main に入つた の意に非ず★

`origin/main` は **`4be3ee19e1c5`**。**其に取り込まれた mac 枝は 60本中 ★1本★のみ**(`karo-mac/skills-tools-20260908b`)。

∴ 本紙の「不要」は次の一義に限る:

> **其の枝の tip が、★origin に現に在る他の枝★の祖先である** ―― 即ち枝を消しても **commit は一つも失はれぬ**。

**「main へ入つたから要らぬ」ではない。Mac の仕事は 59/60 が未だ main に無い。**
判ずるのは「内容の重複」だけであり、**枝名が持つ由緒(どの弾の産か)の要否は総監督の裁である**。

## 三 不要 15本(名指し・★消すな★)

保持先＝其の枝を消しても内容を抱へ続ける**残45本の側の枝**(一例)。

| sha12 | 枝 | 保持先(残枝) |
|---|---|---|
| `2992eecab19d` | `karo-mac/a3-r39-fix-20260917` | `ashigaru-mac-1/a1-jishu-kuumoji-kiten-20260917` |
| `e872fafbe662` | `karo-mac/gate-hook-fix-20260916` | `karo-mac/hantei-saiteishutsu-20260917` |
| `707df7914723` | `karo-mac/gate4-20260909` | `ashigaru-mac-1/a1-jishu-kuumoji-kiten-20260917` |
| `e8470d8c4536` | `karo-mac/gate5-20260909` | `ashigaru-mac-1/a1-jishu-kuumoji-kiten-20260917` |
| `e8470d8c4536` | `karo-mac/gate5-note-20260909` | `ashigaru-mac-1/a1-jishu-kuumoji-kiten-20260917` |
| `43808f8363e9` | `karo-mac/km-50-47-20260917` | `ashigaru-mac-1/a1-jishu-kuumoji-kiten-20260917` |
| `638807f3ba68` | `karo-mac/km-73-otsu-dash-ichido-no-kane-20260917` | `karo-mac/km-76-repogai-no-ichikasho-wo-nushi-he-watasu-20260917` |
| `6dbe09e67c04` | `karo-mac/km-74-otsu-wo-kyouyuuki-yonhon-he-sueru-20260917` | `karo-mac/km-76-repogai-no-ichikasho-wo-nushi-he-watasu-20260917` |
| `e768e71471a9` | `karo-mac/km-75-shikii-no-nokori-hitotsu-wo-tojiru-20260917` | `karo-mac/km-76-repogai-no-ichikasho-wo-nushi-he-watasu-20260917` |
| `b82b98c91222` | `karo-mac/km-dead-inbox-gate-20260917` | `ashigaru-mac-1/a1-jishu-kuumoji-kiten-20260917` |
| `363d5fb06084` | `karo-mac/km-gate-kou-otsu-20260917` | `ashigaru-mac-1/a1-jishu-kuumoji-kiten-20260917` |
| `a6587c02ae87` | `karo-mac/km-gate4-kou-otsu-20260917` | `ashigaru-mac-1/a1-jishu-kuumoji-kiten-20260917` |
| `ab2a1f161bf9` | `karo-mac/km-shikii-yokotenkai-20260917` | `ashigaru-mac-1/km-72-tasekki-no-fusagikata-wo-kami-de-yabure-20260917` |
| `f0d59a3b6315` | `karo-mac/manifest-verify-20260909` | `ashigaru-mac-1/a1-jishu-kuumoji-kiten-20260917` |
| `6e9d40600a80` | `karo-mac/skills-tools-20260908b` | `ashigaru-mac-1/a1-jishu-kuumoji-kiten-20260917` |

### ★同一 sha の二枝★

`karo-mac/gate5-20260909` と `karo-mac/gate5-note-20260909` は **同じ `e8470d8c4536`**。
名が二つ・物は一つである(`raw/40_fuyou.tsv` 第4欄「同じsha の枝」に刷つた)。**片方は完全な写しに過ぎぬ。**

### ★鎖で重なる三本★

`km-73-otsu` ⊂ `km-74-otsu` ⊂ `km-75` ⊂ **`km-76`**。
四本は一筋の鎖で、**末の `km-76` 一本が前三本を悉く抱へる**。故に前三本が不要側、`km-76` は残側。

## 四 安全の検め ―― ★孤児 0★

15本を悉く消したとして、**其の内容を抱へる枝が「残45本」の側に在るか**を一本づつ測つた。

> **残枝に保持先を持たぬ不要枝 = ★0本★**

即ち 15本は**互ひに寄り掛かつて居らぬ**。15本同時に消しても、commit は一つも origin から消えぬ。
(器の逐語 = `driver/10_eda_bunrui.py` の `minashigo`。`set(anc[n][1]) & nokori` が空の枝を数へる。)

## 五 測り方(逐語・追試できる形)

```
git ls-remote --heads origin                       # 240行 rc=0
# mac 系だけ抜く: karo-mac/ か ashigaru-mac- で始まる ref
git cat-file -e <sha>^{commit}                     # 60/60 rc=0 ―― 物が手許に在る事の確かめ
git merge-base --is-ancestor <sha_A> <sha_B>       # rc=0 なら A は B に含まれる(60×59=3540 回)
git rev-parse refs/remotes/origin/main             # 4be3ee19e1c5
```

**★測つた根は「origin の枝の tip 同士」である★** ―― 手許の `main`(未押)を根に取れば数が変はる。
実測: 手許 `main` を根に取ると「取込済」は **9本**と出るが、其の 9本は **origin/main に無い**。
**故に手許 main を根に用ゐると「もう要らぬ」と読める枝が、実は origin では其の 15本の中でしか生きて居らぬ事になる。**
本紙は origin だけを根に取つた。

## 六 家老の申し條

1. **消すのは総監督**である。当席は一本も触れて居らぬ(器は読取のみ・`git push`/`git branch -d` を一度も呼ばぬ)。
2. 15本は**内容の上で安全**だが、**由緒の上で要るか否かは測れぬ**。弾番(km-73/74/75 等)を後から辿る為に枝名を残す御意向が在れば、消さずに置くのが正しい。
3. ★同一 sha の二枝★(`gate5-20260909` / `gate5-note-20260909`)だけは、**由緒の上でも片方が余り**である ―― 名が違ふのみで指す物が同一ゆゑ。**先づ此の一本から消すのが最も安全**と見立てる。
