# 第2段 ★blocker★ ―― second_pc は ★已に 2.1.237 に成って居る★ が ★起動し得ぬ★（native binary 不在）／今 一体でも入替へれば ★其の会話は戻らぬ★

- **as_of: 2026-08-20T11:20:58+09:00**／起案 shogun-second (pid 389804)／second_pc／**read-only・変更 0・install 0・restart 0・pane 入力 0・`systemctl` 0**
- 契機: 委員長 **seq201103**（11:14:22）「★理事長ご指示★=第2段の線を★2.1.237★に定める… second 8/8=236 …★手順は不変★=一体ずつ・`--resume`・1体1uuid重複禁・**打つ前に8080を測る**・前後実視」
- **本紙は「打つ前に測った」結果にして、★執行を止めるべき理由★ にござる。**

---

## 一 ★結論（先に述ぶ）★

**second_pc にて今 第2段を打てば、入替へた体は ★起動に失敗し・会話は戻らぬ★ 公算 大。**
理由は「版が古い」ではない ―― **★版は已に 237 に成って居る★**（今朝 11:06:20 に自動で）。**併し其の 237 には ★実行体（platform native binary）が入って居らぬ★。**
∴ **second の 8/8=236 は「入替へれば閉ぢる gap」ではなく、「入替へれば ★8 体を失ふ★ 罠」にござる。** 委員長 seq199833 ⑴「**★会話を失うな★**」に直撃。

## 二 ★実測（悉く read-only）★

| 問 | 実測 | 逐語／出所 |
|---|---|---|
| PATH の `claude` は何処か | `/home/hakudokai/.npm-global/bin/claude` → `…/lib/node_modules/@anthropic-ai/claude-code/bin/claude.exe`（**500 B の wrapper**） | `lstat`・mtime **2026-08-20 11:06:20** |
| 其の package の版 | **`2.1.237`** ★＝目標の線★ | `package.json`（npm-global） |
| 実行体は在るか | **`node_modules/@anthropic-ai` ＝ `[]`（★空★）** ⇒ `@anthropic-ai/claude-code-linux-x64` **不在** | `os.listdir` |
| 起動するか | **★せぬ★** | `claude --version` ⇒ `Error: claude native binary not installed. … the platform-native optional dependency was not downloaded (--omit=optional). Run the postinstall manually: node node_modules/@anthropic-ai/claude-code/install.cjs` |
| 走って居る 8 体は何を実行して居るか | **悉く `…/@anthropic-ai/.claude-code-wTkEzMFd/bin/claude.exe` ★(deleted)★** | `readlink /proc/<pid>/exe`（43213 / 54326 / 56457 / 58218 / 59890 / 61670 / 63955 / 389804 ―― ★8 体全て★） |
| 逃げ道は在るか | `~/.local/lib/node_modules/…/claude.exe` ＝ **235 MB の実 ELF**（`\x7fELF`）。**★併し版は `2.1.187`★** 且つ **PATH の順で npm-global に負ける** | `package.json` / magic |

## 三 ★自動更新は「success」と記して居る ―― 而して使へぬ★

```
~/.claude/.last-update-result.json
{"timestamp":"2026-08-20T02:06:20.241Z","path":"npm-global","outcome":"success","status":"success",
 "version_from":"2.1.236","version_to":"2.1.237","error_code":null}
```

**＝ 11:06:20 JST（委員長 seq201103 の ★8 分前★）に、誰の手も借りず 236→237 が走り、`success` と記された。**
**★併し `error_code:null` は「動く」の意に非ず★** ―― optional dependency の取り零しは npm の作法上 **失敗に数へられぬ**。
⇒ **「更新は成功した」を根拠に打てば、8 体を失ふ。**（[[tool-output-is-not-tool-verdict]] / [[cli-alive-not-functional-false-green]] の実物）

## 四 ★(deleted) inode ―― 「生きて居る」は「生き返れる」に非ず★

8 体は **削除済みの 236 の inode** を握って走って居る（節二）。
∴ **今 8 体が健やかに見えるのは ★過去の実行体を掴んで居るから★ であって、器が健全だからではない。**
**★一体でも落とせば、其の体は二度と同じ物を掴めぬ。★**（拙者の commit `91cbfa4`「(deleted)/inode は版を判ぜぬ」の、更に一段先の含意にござる。）

## 五 ★具申★

1. **★second_pc の第2段は ★0/8 のまま停止★★** ―― GO が出ても、**実行体が入る迄 打たぬ**。
2. **★直しは環境 owner の物★** ―― 手は判って居る（`node …/claude-code/install.cjs` を打つ／`--omit=optional` 無しで入れ直す）。**併し之は環境の変更**ゆゑ、**委員長の許可の下・環境部長（hermes2）の手**にて。**当職は打たぬ。**
3. **★全 PC への一手（本件の最大の実り）★** ―― 委員長の「打つ前に 8080 を測る」に **一項 加へられたし**:
   **「打つ前に ★`claude --version` が答へるか★ を測れ」**。
   一秒の read-only にして、**入替の前に「起動し得ぬ器」を必ず捕へる**。main は 8/8=237 ゆゑ健全と見ゆるが、**third（236/235）・mac（237/236/235/231 混在）は ★未測★**。**同じ自動更新が同じ刻に走った公算が在る。**
4. **`~/.local` の 2.1.187 を逃げ道に据ゑるな** ―― 版が線より **50 も古く**、PATH の順も違ふ。**繋ぎ換へは環境の変更**にて、当職の範ではない。

## 六 ★未測（UNMEASURED）★

- **third / mac / main の同事象の有無** ―― 他 PC へは SSH 0 ゆゑ**当職の器では測れぬ**。owner ＝ 各 PC の將軍／環境部長。
- **11:06:20 の自動更新を ★何が★ 起こしたか**（Claude 内蔵の auto-updater か外の timer か）―― **UNMEASURED**。
- **install.cjs を打てば直るか** ―― **打って居らぬゆゑ UNMEASURED**（推論に留む）。

## 七 為さぬ事

install / postinstall / npm / PATH の改変 / symlink の張替へ / restart / cutover / pane 入力 / `set-option` / 番人の停止・timer 改変 / `systemctl` の実行 / 他 PC への SSH ―― **悉く 0**。本紙は `lstat`・`readlink`・`os.listdir`・`package.json` の読取のみ。
