---
name: shogun-auto-register
description: |
  GitHub SSH 鍵、API token、OAuth scope、その他諸々の登録作業を**最大限自動化**するスキル。
  陛下の手数を「browser 1 click」以内に圧縮することを北極星とし、
  interactive な部分 (= browser auth, OTP, CAPTCHA) と自動化可能な部分を厳密に分離、
  自動化部分は事前 chain 化、interactive 部分は wait-and-resume で対応する。
  「鍵登録」「token 登録」「OAuth」「device flow」「公開鍵 GitHub に追加」「自動化」「登録作業」で起動。
  Do NOT use for: 認証情報そのものの管理 (= password manager 領分)。
argument-hint: "[pattern-name|new] (e.g. github-ssh-key, gemini-api-key, new)"
allowed-tools: Bash, Read, Write, Edit
---

# /shogun-auto-register — 鬼自動化登録スキル

## North Star (= 全判断の最上位基準)

このスキルの北極星は **「陛下の手数を browser 認可 1 click 以内に圧縮する」**。
- 陛下の時間 = 最高価値資源、無駄な手作業 = 寝首を掻かれる隙
- interactive 部分は web 認可・OTP・CAPTCHA など人間判断要部分のみに**最小化**
- 自動化可能部分 (= CLI 呼出、API call、検証、通知) は**全数 chain 化**
- 「裏付け有ってこその信頼」(陛下御教示) — 自動化結果は**検証して**から完了報告

## 自動化判定 flowchart (= pattern 追加時の鉄則)

```
新規登録作業
   ↓
Q1: 全工程 CLI/API で完結するか?
   ├─ YES → 完全自動化 chain (= 陛下に通知のみ)
   └─ NO  → Q2 へ
       ↓
Q2: interactive 部分は何か?
   ├─ browser auth (OAuth device flow)
   │   → device code 表示 + browser 自動 open + 完了 polling + auto-chain
   ├─ OTP/2FA code 入力
   │   → 陛下に code 表示要求、入力後 auto-chain
   ├─ CAPTCHA
   │   → 陛下に手動完遂依頼、完了通知後 auto-chain
   └─ 物理デバイス (= YubiKey 等)
       → 陛下に touch 依頼、完了 polling
       ↓
Q3: 自動化部分の race condition リスク?
   ├─ stdin/wait 工作で interactive 部分が早期 exit する罠
   ├─ scope/permission の伝播遅延 (= 数秒 delay 要)
   └─ → 検証 polling で確実に完了確認後に next step
```

## 三大鉄則 (= 「自動化失敗 race」根絶)

### 鉄則 1 — interactive を foreground 駆動、自動化を background chain
- ❌ interactive を background + stdin 工作 (= 早期 exit の罠)
- ✅ interactive は foreground、ユーザー作業中に自動化 chain script を**事前準備**
- ✅ もしくは状態遷移を**polling で確認**してから自動化を起動
- 教訓 (2026-05-10): `gh auth refresh` を background + `printf '\n' > stdin` で起動 → gh が即 exit、scope 反映前に Step 2 起動 → HTTP 404 で失敗

### 鉄則 2 — 全自動化 chain は最後に**検証**で締める
- 自動化 chain の最終 step は必ず**結果検証** (= API call、resource 存在確認、auth 状態確認)
- 検証 OK → 陛下/関係者に完遂通知
- 検証 NG → 詳細 log + 失敗箇所特定 + 再実行手順を提示
- 教訓: 「成功したように見える」自動化が一番危険

### 鉄則 3 — interactive 部分は陛下に**最大限の親切**
- ワンタイムコード/URL は**目立つ box** で表示 (= 一発でコピー可)
- browser 自動 open (= explorer.exe / xdg-open / open 等で OS 別対応)
- 失敗時の復旧手順を**事前提示**
- 「手動でやる場合の代替手順」を併記

## 既収録 patterns (= 再利用可能テンプレート)

| pattern | 用途 | interactive 部分 | script |
|---------|------|----------------|--------|
| `github-ssh-key` | SecondPC 鍵を GitHub アカウントに追加 | browser device auth (1 click) | `scripts/github_ssh_key_register.sh` |

(= 今後随時追加)

## 起動例

### 既存 pattern を使う

```
/shogun-auto-register github-ssh-key /path/to/pubkey "title"
```

→ pattern script 起動、陛下には device code 表示のみ、完了 chain 自動。

### 新規 pattern 追加 (= 設計支援)

```
/shogun-auto-register new
```

→ flowchart 質問起動、新 pattern を `patterns/{name}.md` + `scripts/{name}.sh` で起案、
   将来同種作業が来たら即時再利用可能となる。

## When to Use

- GitHub/GitLab/Bitbucket SSH 鍵 / token 登録
- API key 取得 + 環境登録 (= OpenAI、Gemini、Anthropic 等)
- OAuth scope 追加・更新 (= Google、Slack、Notion 等)
- npm/PyPI publish token 設定
- Cloudflare/AWS/GCP credential 登録
- 「これ何度も繰り返してる」と感じた登録作業全般

## Configuration

- `patterns/` — 自動化 pattern の手順書 + 教訓
- `scripts/` — 実行可能 template (= 引数化、再利用前提)
- 機密情報 (= token、key) は**絶対にコード/log にハードコード禁**、env or password manager 経由

## 兄弟連絡 (= cross-PC 自動化)

- 登録対象が SecondPC リソース (= 家康鍵 等) でも MainPC で完遂可
- 登録後の動作検証は SSH 直接路 (= shogun-ssh-cross-pc skill) 経由で SecondPC 側 ack 取得
- 家康殿に bridge 経由で完遂通知 (= shim/hakudokai_inbox_write.py)

## Memory

陛下御教示「自動化できる事は自動で行って」(2026-05-10) を本 skill で恒常化。
今後の登録作業は本 skill 起動 → pattern 該当あれば即実行、新規なら新 pattern 起案。

## Related Documents

- `skills/shogun-ssh-cross-pc/` — LAN SSH 兄弟連絡網
- `skills/skill-creator/` — skill 自体を作る meta-skill
- `instructions/shogun_fukuincho_audit_personas.md` — 「裏付け」三原則
- `memory/MEMORY.md` — 陛下御教示永続化
