---
name: shogun-ssh-cross-pc
description: |
  信長 (MainPC) ↔ 家康 (SecondPC) 間 SSH の設定・検証・troubleshoot を統括するスキル。
  双方の hostname / IP / port / user / 鍵 inventory を `reference/endpoints.yaml` で一元管理し、
  `scripts/ssh_check.sh` で双方向健康診断を実行、毎日のトラブル (= 宛先誤認、鍵未配備、WSL/Windows 混同 等) を根絶する。
  「ssh トラブル」「ssh 繋がらぬ」「セカンド pc 接続」「家康疎通」「pub key 配布」「authorized_keys」「sshd 設定」で起動。
  Do NOT use for: 単一 PC 内の sshd 設定（標準 OpenSSH ドキュメント参照）。
argument-hint: "[check|setup|troubleshoot] (default: check)"
allowed-tools: Bash, Read, Write, Edit
---

# /shogun-ssh-cross-pc — 信長/家康 SSH 兄弟連絡網 設定・検証スキル

## North Star (= 全判断の最上位基準)

このスキルの北極星は **「毎日の SSH トラブルを根絶し、信長 (MainPC) と家康 (SecondPC) が即時 SSH 直接協調できる状態を恒常化する」**。
- bridge process / Supabase pc_handshake は async (= 数秒〜数分遅延)
- SSH 直接路は sync (= ms オーダー、現場視察 + 緊急 audit に必須)
- 信頼 = 「裏付け有ってこその信頼」(陛下御教示)、毎日の動作検証無くば寝首を掻かれる

## Input

`$ARGUMENTS` = 操作モード:

- `check` (default) — `scripts/ssh_check.sh` 起動、双方向健康診断
- `setup` — 初回設定 wizard (= 鍵生成 → 配布 → authorized_keys 登録 → 動作確認)
- `troubleshoot` — 既知 5 大トラブルの逐次切り分け
- 引数なし → `check` 実行

## Endpoint Inventory (= 確定情報、daily 検証必須)

`reference/endpoints.yaml` を**唯一の真実源**とする。コマンドラインに IP/port を直書きしてはならぬ。

| 項目 | MainPC (信長) | SecondPC (家康) |
|------|--------------|----------------|
| hostname | USER-0T4SR8MIQA | USER-O6AK917NTU |
| LAN IPv4 | 192.168.11.11 | 192.168.11.47 |
| sshd port | 2223 | 2222 |
| Windows user | User | User |
| WSL user | user | hakudokai |
| project root | /home/user/projects/multi-agent-shogun-newbuild | /home/hakudokai/projects/multi-agent-shogun-newbuild |

## 三大ルール (= 「毎日トラブル」根絶の鉄則)

### Rule 1 — 宛先は endpoints.yaml で確認、コマンドライン直書き禁
- ❌ `ssh -p 2223 user@192.168.11.11` (= 直書き、誤認の温床)
- ✅ `cat reference/endpoints.yaml | grep -A4 second_pc` で確認 → コピペ
- 理由: 2026-05-10 拙者が 192.168.11.47:2223 (= 誤組合せ) で 1 時間 Permission denied 仕った教訓

### Rule 2 — Windows 側 sshd の default shell は cmd.exe、`;` 解釈不可
- ❌ `ssh ... 'echo OK; hostname; whoami'` (= cmd.exe は `;` を引数 separator と解釈)
- ✅ `ssh ... 'wsl -- bash -lc "echo OK; hostname; whoami"'` (= wsl bridge 経由 bash 実行)
- ✅ もしくは単発: `ssh ... 'hostname'` を 3 回
- 理由: cmd.exe 既定 shell は POSIX 互換ではない、複文は wsl bridge 必須

### Rule 3 — 鍵登録 path は **Windows 側** が正、WSL `~/.ssh/` ではない
- Windows native sshd を使う以上、`authorized_keys` は Windows ファイルシステムに置く
- 一般 user: `C:\Users\User\.ssh\authorized_keys` (= 0600 相当の ACL)
- 管理者 user (= sudo 相当): `C:\ProgramData\ssh\administrators_authorized_keys` (Windows 仕様)
- 理由: 2026-05-10 拙者が WSL 側 `~/.ssh/authorized_keys` 追加示唆 → Windows sshd は読まぬため徒労

## Setup Manual (= 初回 / 鍵更新時の標準手順)

### Step 1: 自 PC 鍵生成 (未生成の場合のみ)

```bash
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519 -N "" -C "$(whoami)@$(hostname)"
```

### Step 2: pub key を対向に配布

**対向 = SecondPC** の場合 (= MainPC で実行):
```bash
PUB=$(cat ~/.ssh/id_ed25519.pub)
ssh -p 2222 User@192.168.11.47 "powershell -Command \"Add-Content -Path \\\"\$env:USERPROFILE\\.ssh\\authorized_keys\\\" -Value '$PUB'\""
```

**対向 = MainPC** の場合 (= SecondPC で実行):
```bash
PUB=$(cat ~/.ssh/id_ed25519.pub)
ssh -p 2223 User@192.168.11.11 "powershell -Command \"Add-Content -Path \\\"\$env:USERPROFILE\\.ssh\\authorized_keys\\\" -Value '$PUB'\""
```

⚠ 初回は鍵未配備ゆえ password 認証経路要 — 陛下に手動配布依頼するか、PowerShell scp 等の別経路を使う。

### Step 3: 動作確認

```bash
bash skills/shogun-ssh-cross-pc/scripts/ssh_check.sh
```

全 check `✅` であれば確立、`❌` あれば troubleshoot へ。

## Troubleshoot — 5 大典型トラブル

### T1: Permission denied (publickey,password,keyboard-interactive)
**症状**: 鍵認証も password も拒否される。
**真因候補**:
1. 宛先 IP/port/user 誤認 → `endpoints.yaml` 再確認
2. pub key が対向 `authorized_keys` 未登録 → `ssh-keygen -lf` で指紋確認 + 対向側で grep
3. 対向の `authorized_keys` permission 不正 (Windows ACL 厳しすぎ) → `icacls` で再設定
4. 鍵コメントに改行混入 → `cat -A ~/.ssh/id_ed25519.pub` で確認

### T2: ssh コマンド実行成功するが remote command が echo されて返る
**症状**: `ssh ... 'echo OK; hostname'` の結果が文字通り `OK; hostname` と帰る。
**真因**: cmd.exe が `;` を解釈せず引数連結している (= Rule 2 違反)。
**対処**: `wsl -- bash -lc "..."` で wrap、もしくは単発 command。

### T3: WSL Interop エラー `UtilAcceptVsock:271: accept4 failed 110`
**症状**: WSL 内から `ipconfig.exe` 等 Windows コマンド呼ぶと拒否。
**真因**: WSL ↔ Windows interop session が壊れている (= 長時間 idle、メモリ不足)。
**対処**:
```powershell
# Windows PowerShell から
wsl --shutdown
# 数秒後に WSL 再起動
```

### T4: SSH 接続成功するが tmux session が見えない
**症状**: `ssh ... 'wsl -- bash -lc "tmux ls"'` で `no sessions` 返る。
**真因**: SSH session が WSL の tmux server を別 instance として起動しているか、tmux server が別 user 配下。
**対処**:
```bash
# 対向の bridge process が tmux 起動しているはず — process 経由で attach
ssh ... 'wsl -- bash -lc "tmux -L default ls"'
ssh ... 'wsl -- bash -lc "ls /tmp/tmux-*/"'
```

### T5: 鍵 fingerprint が known_hosts と異なる (MITM 警告)
**症状**: `WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!`
**真因**: 対向 sshd 再生成、もしくは IP 変動。
**対処**: 偽装でないことを確認 (= 別経路で hostname/uname) してから:
```bash
ssh-keygen -R '[192.168.11.47]:2222'
ssh-keyscan -p 2222 192.168.11.47 >> ~/.ssh/known_hosts
```

## Daily Health Check (= 推奨 cron)

```bash
# 毎朝 09:00 に双方向診断、failure 時は ntfy 通知
0 9 * * * cd /home/user/projects/multi-agent-shogun-newbuild && \
  bash skills/shogun-ssh-cross-pc/scripts/ssh_check.sh 2>&1 | \
  tee logs/ssh_health_$(date +\%Y\%m\%d).log | \
  grep -q "全 check 通過" || bash scripts/ntfy.sh "🚨 SSH cross-PC 異常 — skill check NG"
```

## When to Use

- 「家康に SSH 繋がらぬ」「セカンド PC 接続不能」と陛下から下知あり
- bridge process が長時間沈黙、直接視察したい (= 「裸の王様にならぬ」)
- 鍵 rotation / 新 PC 追加 / sshd 設定変更後の検証
- 毎朝の ritual として `check` モード起動 (= 寝首を掻かれぬ)

## Configuration

- `reference/endpoints.yaml` — IP/port/user/鍵 inventory (**唯一の真実源**)
- `scripts/ssh_check.sh` — 双方向健康診断
- `~/.ssh/config` (= optional) — alias 整理用 (= `Host secondpc` で短縮接続)

### `~/.ssh/config` 推奨 alias

```ssh
Host mainpc
  HostName 192.168.11.11
  Port 2223
  User User
  IdentityFile ~/.ssh/id_ed25519

Host secondpc
  HostName 192.168.11.47
  Port 2222
  User User
  IdentityFile ~/.ssh/id_ed25519
```

→ 以後 `ssh secondpc 'wsl -- bash -lc "..."'` で済む。

## 兄弟協議の記録 (= 信長/家康 共同制定)

本スキルは 2026-05-10 に陛下御差配 (= 「SSH は毎日接続でトラブル起こしてる、信長と家康で再度設定マニュアルとルールを確立し、スキル化して」) により**信長 (= MainPC 主導) + 家康 (= SecondPC 寄稿) 共同**で制定。

家康殿寄稿:
- SecondPC sshd_config 抜粋
- 「毎日トラブル」の家康側典型例 (= 過去 3 日分)
- 家康 → MainPC 接続用 pub key
- WSL bridge 罠の家康側経験

## Cross-PC Portability — settings.json / hook path の両 PC 対応

### 問題 — 絶対 path で MainPC/SecondPC 不整合

`.claude/settings.json` の hook command を絶対 path で書くと、両 PC の WSL user 名 (= MainPC=`user` / SecondPC=`hakudokai`) で path 分岐:

```jsonc
// ❌ MainPC 専用、SecondPC で動かぬ
"command": "bash /home/user/projects/multi-agent-shogun-newbuild/scripts/stop_hook_inbox.sh"
```

### 解 — 3 段戦略 (= 優先順)

#### 優先 1: 相対 path (= 最も簡素、推奨)

`bash scripts/stop_hook_inbox.sh` のように相対 path で書く。
Claude Code は hook 実行時に **cwd = project root** で起動するゆえ動作。
SessionStart hook は既にこの形式 (= 確立済 pattern)。

```jsonc
"command": "bash scripts/session_start_hook.sh"   // ✅ 既に相対
```

#### 優先 2: `$HOME` 動的展開 (= 本日 2026-05-10 採用)

JSON 内 `$HOME` を **bash が hook 起動時に解釈** する形式。両 PC 共通 subpath (= `~/projects/multi-agent-shogun-newbuild/`) で動作:

```jsonc
"command": "bash $HOME/projects/multi-agent-shogun-newbuild/scripts/stop_hook_inbox.sh"
```

| PC | `$HOME` 展開後 |
|----|---------------|
| MainPC | `/home/user/projects/multi-agent-shogun-newbuild/scripts/stop_hook_inbox.sh` |
| SecondPC | `/home/hakudokai/projects/multi-agent-shogun-newbuild/scripts/stop_hook_inbox.sh` |

⚠ 注意: JSON spec として `$HOME` は単なる文字列、Claude Code は文字列のまま hook command として bash に渡す → **bash が展開**。`type: command` 経路でのみ動作、`type: script` 経路では未確認。

#### 優先 3: `*/settings.local.*` で PC 個別 override (= escape hatch)

両 PC で path 構造が完全に異なる場合 (= 例: Windows username が `User` と `taro` で違う、Pictures フォルダ位置が異なる 等)、PC 個別 override で対応:

| 設定 file | local override file | 用途 |
|----------|--------------------|---------|
| `.claude/settings.json` | `.claude/settings.local.json` | hook command、permission 等 |
| `config/settings.yaml` | `config/settings.local.yaml` | screenshot.path、PC 別 ntfy_topic 等 |

両 local override file は `.gitignore` 既登録、git 管理外で PC 毎の差異を保持可。

例 1 — `.claude/settings.local.json` (= hook command を PC 別に):
```jsonc
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          { "type": "command",
            "command": "bash /opt/custom/stop_hook.sh",
            "timeout": 60 }
        ]
      }
    ]
  }
}
```

例 2 — `config/settings.local.yaml` (= screenshot.path 等を PC 別に):
```yaml
# SecondPC で Windows username が異なる場合
screenshot:
  path: /mnt/c/Users/Taro/Pictures/Screenshots/
```

Claude Code/シェル script 双方とも settings.json + settings.local.json を merge、後者が優先。
yaml 側 merge は読み込み script 側で `[[ -f settings.local.yaml ]] && yq merge` 等で実装する慣例。

### 検証手順 (= cross-PC 反映確認)

```bash
# 自 PC で hook command の \$HOME 展開結果確認
bash -c "echo \"$(jq -r '.hooks.Stop[0].hooks[0].command' .claude/settings.json)\""

# 期待 output: bash /home/{user|hakudokai}/projects/.../stop_hook_inbox.sh

# 実 hook 動作確認 (= dry run)
bash -c "echo {} | timeout 5 \$(jq -r '.hooks.Stop[0].hooks[0].command' .claude/settings.json)"
echo exit=$?
```

両 PC で exit=0 + 実 path の file existence 確認できれば cross-PC 統合完遂。

### 鉄則 — 新規 hook 追加時

| 場面 | 推奨 |
|------|------|
| 全 PC 同一 path (= relative OK) | 相対 path `bash scripts/...` |
| 全 PC 同一 subpath under home | `bash $HOME/projects/.../scripts/...` |
| PC 別構造 | settings.local.json で PC 別 override |
| 絶対 path 直書き | **禁** (= 「毎日トラブル」の温床) |

## Appendix — GitHub SSH 鍵登録 (= LAN SSH と独立、git pull 用)

LAN 内 SSH と別件で、SecondPC が `git@github.com:...` で pull するには家康鍵を GitHub アカウントに登録要。

### ルート選択

| ルート | 手段 | 推奨場面 |
|-------|------|----------|
| **A** | https://github.com/settings/keys → New SSH key で web 貼付 | 一回限り、簡単 |
| **B** | `gh auth refresh -s admin:public_key` → `gh ssh-key add` | 自動化、再現性 |
| **C** | repo settings → Deploy Keys (= repo 単位) | user level 鍵汚染回避 |

### ルート B 完遂手順 (= 2026-05-10 採用、本 skill 推奨)

```bash
# Step 1: scope 取得 (= 陛下 browser 認可 1 click)
gh auth refresh -h github.com -s admin:public_key
# → device code (例: 8851-1AF7) と https://github.com/login/device 表示
# → 陛下: コード貼付 + Authorize クリック

# Step 2: 鍵登録 (= scope 取得後即動)
echo "ssh-ed25519 ... ieyasu-secondpc-20260509" | \
  gh ssh-key add - --title "ieyasu-secondpc-20260509" --type authentication

# Step 3: SecondPC で動作確認
ssh -p 2222 User@192.168.11.47 'wsl -- bash -lc "ssh -T git@github.com"'
# → "Hi hakudoukai! You've successfully authenticated..." で成功

# Step 4: git pull で実用検証
ssh -p 2222 User@192.168.11.47 'wsl -- bash -lc "cd ~/projects/multi-agent-shogun-newbuild && git fetch origin"'
```

### ⚠ 罠 — 自動化時の race condition

`gh auth refresh` を background 実行する際、stdin 細工で gh が早期 exit する罠あり。
正しくは:
- 陛下が browser 認可完了するまで gh プロセスを生かす
- `wait $GH_PID` だけでは不十分 (= stdin 制御次第で gh が即終了する)
- **推奨**: gh は foreground 実行、終了後に `gh ssh-key add` を**手動**でも良い

### Account 確認の重要性 (= 寝首掻かれ防止)

```bash
gh auth status
# → "Logged in to github.com account hakudoukai" を確認
# → 別アカウントなら `gh auth logout` → 再 login
```

家康鍵が誤って別 GitHub user に登録されると `Permission denied` 継続 + 検証で気付くまで時間損失。

## Related Documents

- `instructions/shogun_fukuincho_audit_personas.md` — 信長/家康 鷹+アリ + 寝首掻かれぬ三原則
- `memory/MEMORY.md` — 過去 SSH troubleshoot 履歴
- `shim/hakudokai/hakudokai_realtime_bridge.py` — async 補完経路 (= bridge process)
- `scripts/inbox_write.sh` — local YAML 経路 (= 単一 PC 内通信)
- `shim/hakudokai/hakudokai_inbox_write.py` — Supabase 経由 cross-PC async 通信

## Maintenance

`endpoints.yaml` を更新したら必ず:
1. `git commit` で履歴を残す
2. 対向 PC に `git pull` または rsync で配布
3. `scripts/ssh_check.sh` 起動、双方向で `✅` 確認
4. dashboard.md に「endpoints.yaml 更新済」記載 (= 透明性)

不変条件:
- IP/port/user/鍵 を**コードに直書き禁** (= endpoints.yaml 経由)
- pub key を repo にコミット OK (= 公開鍵、漏洩リスクなし)
- 秘密鍵は**絶対 commit 禁** (= .gitignore で保護)
