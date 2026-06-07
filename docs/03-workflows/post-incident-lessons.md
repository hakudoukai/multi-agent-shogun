# §19. Post-Incident Lessons Capture (mandatory) — 理事長殿御指示 2026-05-07

**原則: 事故・トラブル・誤作動が発生したら、復旧完了直後に必ず再発防止スキルを生成する。**

出典: CLAUDE.md (元「§19. Post-Incident Lessons Capture」節) からの移設実体 (副院長令 7de922ec 裁定、2026-06-04 Commander)。改訂責務は理事長殿の専権事項。詳細手順は `skills/lessons-to-skill/SKILL.md` を参照。

過去事例 (2026-05-07): 信長が pane 番号を `@agent_id` 確認なしで推測し、gunshi 重複 pane を作成。同種事故は再発する性質。本セクションで恒久対策を mandate 化する。

## §19.1 必須手順

```
事故認識 → 影響制止 → 復旧完了
              ↓
        /lessons-to-skill skill を invoke (= mandatory)
              ↓
        生成案を理事長殿へ提示
              ↓
        理事長殿明示承認
              ↓
        skill + check + 事故ログ commit
              ↓
        必要時: CLAUDE.md 追記 (= 別途承認)
```

詳細手順は `skills/lessons-to-skill/SKILL.md` を参照。

## §19.2 生成物

事故 1 件につき以下を生成 (= 既存 skill で重複なら拡張):

1. **`skills/<name>/SKILL.md`** — 再発防止スキル本体
2. **`scripts/checks/<name>.sh`** — 自動チェックスクリプト (exit 0/1/2、stderr 警告、timeout 5 秒)
3. **`.claude/settings.json` PreToolUse hook 登録案** (= `\|\| true` 必須、絶対ブロック禁止)
4. **`docs/incident_logs/<date>_<topic>.md`** — 5 Why 必須のインシデント記録
5. **CLAUDE.md 追記案** (= 必要時のみ、理事長殿承認後反映)

## §19.3 強制力ルール (= 誤作動ゼロ保証)

| 項目 | 制約 |
|------|------|
| skill 生成 | 理事長殿明示承認後にのみ commit |
| hook | **絶対にブロックしない** (= `\|\| true` + exit 0)、stderr 警告のみ |
| check スクリプト | timeout 必須、失敗時素通り |
| skill 名 | kebab-case |
| description | 1 行 100 文字以内 |
| 重複生成 | 禁止、既存 skill 拡張で対応 |

## §19.4 月次自己点検

`docs/skills_telemetry.md` を毎月 1 日に更新:
- 各 skill の invoke 回数 / false positive 率
- 3 ヶ月 invoke ゼロの skill → archive 候補
- false positive 率 > 3% → 要修正

## §19.5 禁止事項

- skill 生成を省略する (= 軽微でも 5 Why は実施)
- hook で操作をブロックする
- 理事長殿承認なしで CLAUDE.md を編集する
- 既存 skill との重複生成
- skill を動作確認なしで commit する

## §19.6 関連資産

| 資産 | 役割 |
|------|------|
| `skills/lessons-to-skill/SKILL.md` | 本ルールの実行手順 (= meta-skill) |
| `skills/pane-identity-verify/SKILL.md` | 第 1 号 skill (= pane 番号誤認防止) |
| `scripts/checks/pane_identity.sh` | 第 1 号 check スクリプト |
| `docs/incident_logs/2026-05-07_pane_misidentification.md` | 第 1 号インシデント記録 |
| `docs/skills_telemetry.md` | 月次自己点検記録 (= 次回月初生成予定) |
