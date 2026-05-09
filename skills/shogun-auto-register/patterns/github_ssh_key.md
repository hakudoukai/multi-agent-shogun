# Pattern: GitHub SSH Key 登録

**初回確立**: 2026-05-10 (= 家康鍵を hakudoukai アカウントに登録)
**所要時間**: 約 1 分 (= 陛下の browser 認可 1 click)
**自動化率**: 95% (= browser 認可のみ手動)

## 適用条件

- gh CLI が target GitHub アカウントで認証済 (= `gh auth status` で確認)
- 登録したい pub key が手元にある (= `~/.ssh/id_*.pub` 等)
- gh CLI に `admin:public_key` scope **未保有** (= 保有なら Step 1 skip)

## 工程

### Step 0 — 事前確認

```bash
# 認証アカウント確認 (= 別アカウントだと別人の鍵に登録される)
gh auth status

# 期待: "Logged in to github.com account <target_account>"
# Token scopes に "admin:public_key" 有無確認
```

### Step 1 — scope 取得 (= 陛下 browser 認可、1 click)

```bash
gh auth refresh -h github.com -s admin:public_key
```

→ 端末に `device code` (例: `8851-1AF7`) と `https://github.com/login/device` 表示。

**陛下御作業**:
1. URL を browser で開く (= `explorer.exe https://github.com/login/device` で自動 open 試行)
2. device code 貼付
3. **target アカウントで login 確認** (= 違うアカウントなら logout → 再 login)
4. **Authorize** クリック
5. ターミナル `✓ Authentication complete.` 表示で完遂

⚠ **gh プロセスを background + stdin 工作で起動するな** (= 早期 exit の罠、本日 07:47 失敗事例)。
   foreground 駆動、もしくは scope 反映を polling で確認してから Step 2。

### Step 2 — 鍵登録 (= 完全自動化)

```bash
PUB_KEY="ssh-ed25519 AAAA... comment"
TITLE="ieyasu-secondpc-20260509"  # 識別名、後で見て分かるもの

echo "$PUB_KEY" | gh ssh-key add - --title "$TITLE" --type authentication
```

期待 output: `✓ Public key added to your account`

### Step 3 — 検証 (= 全数主義、寝首掻かれぬ)

```bash
# 登録一覧で確認
gh ssh-key list | grep "$TITLE"

# 実 SSH 接続で動作確認 (= target 環境から)
ssh -T git@github.com
# 期待: "Hi <account>! You've successfully authenticated..."

# git fetch で実用検証
git fetch origin
```

### Step 4 — 関係者通知

```bash
# bridge 経由で SecondPC 家康に成功 ack
python3 shim/hakudokai/hakudokai_inbox_write.py sakura \
  "GitHub 鍵登録完遂、git pull 即動可" \
  --type status_update --from kouchan --priority high
```

## 失敗 pattern + 対処

### F1: HTTP 404 / `admin:public_key scope needed`
**原因**: Step 1 完了前に Step 2 起動。
**対処**: `gh auth status` で `admin:public_key` scope 反映確認後に再実行。

### F2: 別アカウントに登録されてしまった
**原因**: `gh auth status` 確認怠り、別アカウントで login 中だった。
**対処**:
1. 誤登録先で削除 (= web UI or `gh ssh-key delete <id>`)
2. `gh auth logout` → 正アカウントで `gh auth login`
3. Step 1 から再実行

### F3: device code 入力時に「invalid」表示
**原因**: code expire (= 15 分制限) or 別 user で login 中
**対処**: gh プロセス kill → Step 1 再実行 (= 新 code 取得)

### F4: gh プロセスが即 exit してしまった
**原因**: stdin 操作 (= `printf '\n'` 等) で gh が EOF 検知し終了。
**対処**: gh は foreground 起動、stdin に何も流さぬ。

## 教訓 (= 2026-05-10 当日)

1. **race condition**: background + stdin 工作で gh 即 exit、Step 2 が scope 未反映状態で起動 → HTTP 404
2. **復旧**: 陛下の Authorize 完遂後、scope 反映確認 → Step 2 再実行で成功 (= 1 line で完遂)
3. **教訓 skill 化**: 本 pattern doc が以後の同種作業で「迷わず 1 分で完遂」を保証
