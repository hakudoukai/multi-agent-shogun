# 第4段 ―― Hermes 0.20.4 を新地に建て 現に走らせたる記（可逆分の完了）

- 起草: shogun-second（pid 1924984）
- as_of: 2026-08-21T23:29:46+09:00
- 認可: 本部長 seq203560「Stage4 local Hermes 0.20.4 … per-role dist-info check。**Do not re-consult per role; resolve reversible blockers locally, report blocker4 only.**」
- 既存三樹・launcher・wrapper・役 venv・稼働 pane へ **一指 0**。共有樹 `status --porcelain` = **0 行**（前後不変）。

---

## 一 ―― 令の前提三つが器に無かつた事（blocker4・前報の再掲）

| # | 令の前提 | 器の実際 |
|---|---|---|
| ㊀ | 「frozen shogun-main clone」より取れ | **当機に其の clone 無し**。hermes の remote は悉く `https://github.com/NousResearch/hermes-agent.git` |
| ㊁ | 「per-role local install」を検めよ | 役 venv の `direct_url.json` は `{"dir_info":{"editable":true},"url":"file:///home/hakudokai/hermes-runtimes/hermes-agent-v2026.8.3"}` ＝ **per-role の実体は無く 共有樹を指すのみ** |
| ㊂ | 0.20.4 | 共有樹の**作業樹は 0.20.0**。`0.20.4` は `origin/main` ref にのみ在り |

⇒ 令の「可逆なる障りは己にて解け」に依り、**新地に一本 建てた**（御下知を待たず・可逆ゆゑ）。

---

## 二 ―― 新地の来歴（PROVENANCE）

- 地: `/home/hakudokai/hermes-staging-0.20.4/`
- `hermes-agent/` ＝ 共有樹の `origin/main` を **`git archive | tar -x`** にて展きたる樹（`version = "0.20.4"`）
  - **source_commit = `6a3d50c6e05ee9a3c1e5ecf2268524c5d0627b9f`**
  - 源は**読取のみ**・**network 0**（局所 path よりの取り出し）
- 共有樹は **shallow clone** ―― `git fetch` は `rejected … shallow roots are not allowed to be updated` を返す。**history は引けぬ**ゆゑ `git archive`（樹のみ）に改めた。
- `venv/` ＝ `python3.12 -m venv`（新規・空より）

---

## 三 ―― 上流が **wheel を己で拒む**（最も重き發見）

`pip install --no-build-isolation <tree>` は失敗す。逐語:

```
RuntimeError: Building wheels or sdists for hermes-agent is not supported.
Hermes is distributed via the shell installer, Docker image, or Nix.
If you are developing, use an editable install instead:
  uv sync          # or: uv pip install -e .
```

`setup.py` の機構（逐語）――

```python
class _GuardedBdistWheel(bdist_wheel):
    def run(self, *args, **kwargs):
        if not _IN_NIX_BUILD:
            raise RuntimeError(_BLOCK_MESSAGE)
        return super().run(*args, **kwargs)
```

> **⇒ 「役ごとに local install」なる形は ―― wheel を作りて配る事では 成し得ぬ。**
> **上流の認むる道は editable ただ一つ。**
> ∴ 役 venv が悉く `editable:true` にて共有樹を指し居たるは **怠りに非ず・設計**。
> ∴ 委員長 seq200891「**ABI差ゆゑ copy/rsync 不可**」は、ABI 以前に **build その物が禁ぜられて居る**事にて 更に強く裏付く。
> ∴ 真の per-role 化とは **役ごとに樹を持ち・其の樹へ editable する事**（成果物の複写に非ず）。

---

## 四 ―― 現に建ち 現に走つた（実測・截らず）

editable にて（上流の認むる道）:

```
Successfully built hermes-agent
Successfully installed hermes-agent-0.20.4
```

**dist-info check の型（令の「per-role dist-info check」に対する 答の形）**:

```
site-packages/hermes_agent-0.20.4.dist-info
importlib.metadata.version('hermes-agent') == 0.20.4
```

依存を具へて（PyPI より）:

| 物 | 0.20.4 の要 | 役 venv の現状 | staging 実測 |
|---|---|---|---|
| `cryptography` | `==50.0.0` | **48.0.1** | **50.0.0** ✔ |
| `nemo-relay` | `>=0.7.1,<0.8` | **0.6.0** | **0.7.3** ✔ |

走行の證（HOME を staging へ逸らして）:

```
$ hermes --version
Hermes Agent v0.20.4 (2026.8.18)
Install directory: /home/hakudokai/hermes-staging-0.20.4/hermes-agent
Python: 3.12.3
OpenAI SDK: 2.24.0
rc=0
```

**⇒ blocker4 の「依存の壁」は 崩れた。網は通ず**（`setuptools==83.0.0` の取得にて先に證し、全依存 62 個が現に入つた）。

---

## 五 ―― 三つの罠（後の者へ）

### 罠㊀ ―― **dist 名 ≠ module 名**

`import hermes_agent` は `ModuleNotFoundError`。而して之は**不全に非ず**――
頂の module は `hermes_cli` / `run_agent` / `agent` / `gateway` … にて `hermes_agent` なる module は**元より無い**。
console script は `hermes = hermes_cli.main:main`。

> **條 ―― 「import できぬ」は 「入つて居らぬ」を意味せぬ。問ひの側が誤り得る。**

### 罠㊁ ―― **import その物が 状態を生む**（最も危ふい）

`import hermes_cli` ただ一行にて、`$HOME/.hermes/` が **現に生まれた** ――
`state.db` / `SOUL.md` / `memories` / `cron` / `hooks` / `skills` / `pairing` / `image_cache` / `audio_cache` …

> **條 ―― 「読むだけ」の心算が 書く。**
> ∴ **役ごとの dist-info check を 素の HOME にて打てば ―― 其の役の hermes state に手を入れる事になる。**
> 本記の測りは悉く `HOME=<staging>/fakehome` に逸らして打つた。**之は用心に非ず 必須**。

### 罠㊂ ―― **editable wheel の sha は 版を判ぜぬ**

同じ樹より二度建てたるに `4cc0dc45…` と `e0e2c2a3…` ―― **sha 相違**。

> **條 ―― 成果物の sha は 樹の同一を證せぬ（editable は path 等を焼き込む）。版は `dist-info` と `--version` にて判ぜよ。**

---

## 六 ―― 樹の差 ―― 恐れたる「局所 commit を落とす」は **薄れた**（自訂）

前報（`2026-08-20_stage4_provenance_and_tree_binding`）にて「共有樹 HEAD の ahead 1 ＝ `refactor(skills): move polymarket to optional-skills/finance` は**此の PC 固有**ゆゑ 素な checkout は之を落とす」と札した。実測にて**薄れた**――

| 樹 | `optional-skills/finance/polymarket` | files | agg sha256(16) |
|---|---|---|---|
| 共有 (0.20.0) | **在り** | 3 | `2dd34ac6e6570249` |
| staging (0.20.4) | **在り** | 3 | `d8bafbc530733354` |

- **path は両樹に在り** ⇒ 其の**移設は 0.20.4 にも既に在る**（此の PC 固有の細工に非ず）。
- 中身の sha は相違 ―― 而して之は **版の差**であつて 局所の差とは限らぬ。
- `HEAD...origin/main` の ahead/behind ＝ **`1 / 1`**。origin/main の頭は `fix(tui): allow the ESC byte in the SGR param matcher`。

> **測つた事**: path の存在は両樹に在り・files は 3 と 3・中身の sha は相違。
> **測つて居らぬ事（UNMEASURED）**: 其の ahead 1 の commit が **移設の他に 上流に無い変更を担ぐや否や**（shallow ゆゑ親が引けぬ）。

---

## 七 ―― 猶 御下知を要する分（human GO / 上位裁）

| # | 事 | 何ゆゑ止まるか |
|---|---|---|
| ㊀ | 共有樹への書込・cutover・restart | **Commander `seq202566` の明示禁**「Do not write/cutover/restart」 |
| ㊁ | launcher / wrapper 三枚の書換 | **hermes 系 file 改変禁**。launcher は `RT=$ROLE_HOME/run/hermes-agent-v2026.8.3` と**逐語の絶対 path** にて pin・env 上書き無し ⇒ **書換無しには 新樹を向かせられぬ** |
| ㊂ | `%24` / `%36` / `%26` を `--continue` にて起こし直す | 稼働 role の再起動＝不可逆 |
| ㊃ | 役ごとの樹を建てる順 | 委員長承認済の順 ＝ **a7 樹（1役）先 → gunshi 樹（2役）後**。但し「provenance blocker が解けるまで実行するな」 ⇒ **provenance は本記にて解けた**（源 commit・取り出し法・network 0 を明記） |

---

## 八 ―― 環境の一件（附）

staging にて hermes が自ら告げた（逐語・要旨）――

> `linked SQLite 3.45.1 is vulnerable to the WAL-reset corruption bug … using journal_mode=DELETE instead of enabling WAL. Upgrade to SQLite 3.51.3+`

当機の system SQLite は役の hermes も同じ物を用ゐる。**0.20.0 の役が同じ告げを出すや否やは UNMEASURED**（役へ一指も触れぬゆゑ）。SQLite の入替は**己の枷の外**（上位裁）。

---

## 十 ―― **`source_commit` の独立検証 ―― 閉ぢたる（追記 `2026-08-21T23:50:25+09:00`）**

本部長殿 `23:36:40`（`nonce=HB-20260821-2337-STAGE4`）の逐語 ――

> 「staging tree は **git metadata 無しゆゑ source_commit 6a3d50c の独立検証は未完**。」

**御指摘は正しく、且つ 之は可逆にて解け申した**（令「resolve reversible blockers locally」に依り 御下知を待たず閉ぢた）。

### 手（読取のみ・網 0・書込 0）

`git archive` は `.git` を残さぬ ⇒ 樹の中に證が無い。**∴ 源の側の commit より blob の sha を引き、新地の file を `blob` header 付きの SHA-1 にて己で算じて突き合はせた**（`git hash-object` と同一の算法 ―― ★algorithm ＝ SHA-1 with `blob <len>\0` prefix★）。

- 源: `/home/hakudokai/hermes-runtimes/hermes-agent-v2026.8.3`（**読取のみ**）
  - `HEAD` = `0957277f2f468bac22bbfcfa7c43029858c9597e`（＝役の走る `0.20.0`・本部長殿の実測と**合致**）
  - `origin/main` = `6a3d50c6e05ee9a3c1e5ecf2268524c5d0627b9f`（＝新地の源・`cat-file -t` にて `commit` と確認）
- 新地: `/home/hakudokai/hermes-staging-0.20.4/hermes-agent`（`.git` 無し・`__pycache__` を除外）

### 結（`as_of 2026-08-21T23:50:07`）

| 項 | 数 |
|---|---|
| commit `6a3d50c` の blob | **9,738** |
| **sha 一致** | **9,729** |
| 不一致 | **9** |
| **欠（commit に在り 新地に無し）** | **0** |
| 余分（新地に在り commit に無し） | **6** |

- **余分 6 は 悉く `hermes_agent.egg-info/` の下** ＝ ★`pip install -e` の副産物★。∴ **源に無き code は 一片も入つて居らぬ**。
- **不一致 9 は 悉く `*.ps1`** ⇒ `.gitattributes` の eol 條に因る。**`CRLF→LF` に正規化して算じ直したるに ★9/9 悉く 一致★**（`crlf` の数 ＝ `4,834`／`788`／`323`… ⇒ 現に CRLF にて置かれ居る）。
  - ∴ ★差は **中身の差に非ず 改行の宣言の差**★。`git archive` が `.gitattributes` に従ひ checkout 時に変換したる物。

> **★判 ―― 新地は commit `6a3d50c6e05ee9a3c1e5ecf2268524c5d0627b9f` と ★内容一致★（宣言されたる eol 変換を除き byte 一致）。欠 0・混入 0。★**
> **⇒ 本部長殿の申されたる「独立検証 未完」は ―― ★本記にて 完★。**

### 條（本節より得たる物）

- **★條 ―― `.git` を持たぬ樹の来歴は 樹の中に無い。而して ★源の側の commit★ と ★己で算ずる blob sha★ にて 外から證し得る。★**
- **★條 ―― sha の不一致は「中身の差」を意味せぬ。★宣言されたる正規化★（eol・`export-subst`）を先に疑へ。★**
- **★條 ―― 「一致」を申す時は ★欠★ と ★余分★ を併せて数へよ。一致数のみでは 混入を捕へ得ぬ。★**

---

## 九 ―― 變ぜぬ物（本記の間 悉く 0）

共有樹書込 0／launcher・wrapper 書換 0／役 venv へ一指 0／`respawn` 0／`send-keys` 0／`kill` 系 0／既存 `~/.hermes` へ一指 0（HOME を逸らした）／push 0／pull 0／`queue/tasks` 書込 0／`dashboard.md` 0／`_archive` 不開／ccflare 一指 0／番人 0。

書いたるは **新地 `~/hermes-staging-0.20.4/` ただ一つ**（己が作りたる物のみ）と 本記。
