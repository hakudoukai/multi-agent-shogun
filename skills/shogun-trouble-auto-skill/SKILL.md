---
name: shogun-trouble-auto-skill
description: |
  同種トラブルを N 回検知すると **自動で skill-creator を発火**し、再発防止 skill 草案を生成するメタスキル。
  陛下御教示「以後同じトラブルを自動で解決するスキルを作るスキル」を実装。
  検知対象: Lord の「毎日トラブル」「また」「何度も」「繰り返し」発話、dashboard 🚨要対応の長期残留、punishment_log 同根原因再発、shell command 同種失敗の累積。
  「skill 候補スキャン」「トラブル分析」「再発防止 skill」「skill 自動化」「skill_candidate」で起動。
  Do NOT use for: 個別 skill の設計 (= skill-creator が担当)、単発トラブル対応 (= 通常 troubleshoot)。
argument-hint: "[scan|aggregate|draft|status]"
allowed-tools: Bash, Read, Write, Edit
---

# /shogun-trouble-auto-skill — 鬼自動 skill 化メタスキル

## North Star (= 全判断の最上位基準)

このスキルの北極星は **「同種トラブル 3 回目で陛下に手を煩わせず再発防止 skill を草案化する」**。
- 1 回 = 偶発、2 回 = 警戒、**3 回 = 制度化** (= 武田信玄三度繰り返さば兵法に学ぶ)
- 陛下が同じ説教を 3 回為さるは寝首掻かれの予兆 (= 「裏付け有ってこその信頼」)
- 自動草案 = 拙者が下書き仕る、陛下御承認で本採用 (= 暴走防止)

## 4 段 Pipeline

```
[Stage 1: 検知] → [Stage 2: 集約] → [Stage 3: 閾値] → [Stage 4: 草案化]
   ↓                ↓                  ↓                ↓
phrase/log/cmd    candidates.yaml    >= 3 hits        skills/_draft/
監視               append-only        signature 単位    SKILL.md 起案
                                                      陛下承認待ち
```

### Stage 1 — 検知 (= 入力源 4 系統)

| 系統 | trigger | signature 抽出 |
|------|---------|---------------|
| **Lord 発話** | 「毎日トラブル」「また同じ」「何度も」「繰り返し」「もう一度」「またか」 | 直前 5 turn の話題 keyword |
| **dashboard 🚨** | 同 entry が >24h 残留 | 🚨 entry の summary |
| **punishment_log** | 同 root_cause が同月 ≥2 件 | root_cause |
| **shell 失敗** | 同 cmd で同 exit code が 7 日以内 ≥3 | cmd + error 1 行目 |

### Stage 2 — 集約 (`queue/skill_candidates.yaml`)

各検知を append-only で記録:

```yaml
candidates:
  - id: cand_20260510_001
    detected_at: 2026-05-10T07:30:00
    source: lord_speech
    signature: ssh_daily_trouble
    severity: blocking   # blocking|normal|cosmetic — N 閾値 2/3/5
    keywords: [SSH, 毎日, トラブル, 接続]
    context: |
      陛下「SSHは毎日接続でトラブル起こしてる」
      → 直近 7 日で 3 回目 (= 5/3, 5/7, 5/10)
    hit_count: 3        # 7 日窓内の同 signature 累積
    threshold_reached: true   # severity=blocking → N=2 超え
    status: drafted   # detected → aggregated → threshold_reached → drafted → approved
```

### Stage 3 — 閾値判定 (= 陛下御差配 2026-05-10)

severity 別可変、時間窓 **7 日**:

| severity | N | 例 |
|----------|---|----|
| **blocking** | **2** | SSH 接続不能、bridge process 停止、本番 deploy 失敗 (= 業務停止級) |
| **normal** (default) | **3** | 武田信玄三度法則、generic な再発 trouble |
| **cosmetic** | **5** | UI alignment、log format、軽微な warning |

```python
# 7 日内の hit_count を集計
recent_hits = [c for c in same_signature_entries
               if (now - c.detected_at).days <= 7]
threshold_n = {'blocking': 2, 'normal': 3, 'cosmetic': 5}[severity]
if len(recent_hits) >= threshold_n: → Stage 4
```

ただし Lord が「skill 化」を明示発言したら severity/N 無視で即 Stage 4 (= `explicit_skill_request: true`)。

severity 自動判定: signature の keywords に「停止」「不能」「failed」「エラー」「blocker」含む → blocking、
「UI」「format」「warning」のみ → cosmetic、その他 → normal。

### Stage 4 — 草案化 (= skill-creator 自動発火)

1. signature から skill 名を機械生成 (例: `ssh_daily_trouble` → `shogun-ssh-recovery`)
2. `skills/_draft/{skill-name}/SKILL.md` を起案 (= skill-creator pattern 踏襲)
3. context (= Stage 2 で集めた keywords + 直近 5 turn) を「North Star + Trigger」に反映
4. dashboard.md 🚨要対応 に「skill 草案承認待ち: {skill-name}」追記
5. 陛下承認 (= `/{skill-name}` 起動 + 「採用」発言) で `_draft/` → `skills/` 移動

## 起動方式

### 自動 (= 推奨)
- `scripts/skill_candidate_scan.sh` を **session_start_hook** で 1 日 1 回起動 (= rate-limited)
- Stage 1〜3 自動、Stage 4 草案化も自動 (= ただし `_draft/` 配置で本採用は陛下承認要)

### 手動
```
/shogun-trouble-auto-skill scan      # 今すぐ検知 + 集約 + 閾値判定
/shogun-trouble-auto-skill aggregate # 既検知の hit_count 再集計
/shogun-trouble-auto-skill draft     # 閾値超え candidate を即草案化
/shogun-trouble-auto-skill status    # candidates.yaml の現状一覧
```

## Detection Rules (= 検知 ruleset、scripts/skill_candidate_scan.sh と双子)

### Rule 1: Lord 発話 phrase matching

```python
TROUBLE_PHRASES = [
    "毎日トラブル", "毎日.*トラブル", "また.*同じ", "何度も",
    "繰り返し", "もう一度", "またか", "また.*起きた",
    "毎回", "同じ問題", "前にも", "前回も",
]
SKILL_REQUEST_PHRASES = [
    "スキル化", "skill 化", "自動化して",
]
```

→ 直近 conversation で hit、signature = 周辺 5 turn の話題 keyword (= 例: ssh, 接続, 鍵)

### Rule 2: dashboard 🚨 残留

```bash
# dashboard.md の 🚨要対応 section から、24h 以上残留 entry 抽出
git log --diff-filter=A --since="48 hours ago" -- dashboard.md  # 追加された 🚨
git log --diff-filter=D --since="48 hours ago" -- dashboard.md  # 削除された 🚨
# diff = 残留中
```

### Rule 3: punishment_log 同根

```python
import yaml
log = yaml.safe_load(open('queue/reports/shogun_punishment_log.yaml'))
from collections import Counter
this_month = [e for e in log['entries'] if e['date'].startswith('2026-05')]
recurring = Counter(e['root_cause'] for e in this_month).most_common()
# count >= 2 → candidate
```

### Rule 4: shell command failure 同種

```bash
# bash history + tool result で exit code !=0 の同 cmd を集計
# (= 実装は session_start_hook 連携、conversation transcript から)
```

## 三大鉄則 (= 暴走防止)

### 鉄則 1 — `_draft/` 直行、本 skills/ 直接配置禁
- 自動草案は必ず `skills/_draft/{name}/` 配置
- 陛下承認 (= 明示発言 「採用」「本採用」「approve」) で `mv` で `skills/` 入り
- 暴走防止: 拙者が誤検知しても本採用されぬ

### 鉄則 2 — hit_count 改竄禁
- candidates.yaml は **append-only** (= edit by id、削除禁)
- 同 signature の重複は `hit_count++` で集約、entry 統合禁
- 陛下が直接 `status: rejected` 設定で却下のみ可

### 鉄則 3 — 草案 SKILL.md は skill-creator 規格遵守
- frontmatter 必須項目漏れなし (= name, description, allowed-tools)
- description = What + When + ネガティブトリガー (= skill-creator 7 項目)
- 1024 文字以内、`< >` 禁、トリガーワード明記

## When to Use

- 陛下が「また同じトラブル」「何度も」と仰せの時
- dashboard 🚨要対応 が長期残留の時
- 月次 retrospective で「再発防止策」検討時
- 新人 ashigaru の onboarding で「過去トラブル一覧」展示時

## Configuration

- `queue/skill_candidates.yaml` — append-only 検知 log
- `scripts/skill_candidate_scan.sh` — Stage 1〜3 自動化 script
- `skills/_draft/` — 自動草案配置先 (= 陛下承認前)
- `instructions/shogun.md` — Skill 設計 ritual と整合 (= L256-258)

## Related Skills

- `skills/skill-creator/` — Stage 4 で実際に SKILL.md 設計する依頼先
- `skills/shogun-auto-register/` — registration 系 trouble の specific pattern 集
- `skills/shogun-ssh-cross-pc/` — SSH trouble 専用 (= 本 skill が母体となって生まれた事例)

## Memory

陛下御教示 (2026-05-10):
> 「以前このような色々なトラブルが起きた時に 以後同じトラブルを自動で解決するスキルを作るスキルを装備したと思うけど」

→ skill-creator は装備済だが**自動 trigger は未装備**だった事を発見、本 skill で実装。
今後「同じトラブル 3 回」で自動草案、陛下御一言「採用」で本採用、寝首掻かれず。
