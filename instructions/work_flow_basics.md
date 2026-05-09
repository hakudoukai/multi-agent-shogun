# 基本作業工程 — 「合格 gate」必殺の流れ v1.0

陛下御差配 (2026-05-10 朝):
> 「足軽の実装から軍師による監査を受けること、そして指摘された問題点は解決するまで PDCA サイクルを回して間違いをなくす。合格したプログラムのみ家老に報告・提出出来るという基本的な作業工程が明示してあるかな?」

→ 本 doc で**明示**仕る。これは全 agent が遵守すべき**絶対原則**。

---

## 🔱 基本作業工程図 (= 必殺 PDCA gate)

```
┌──────────────────────────────────────────────────────────────────┐
│  ❶ ashigaru 実装                                                  │
│   (= cycle{N}_implementation)                                     │
│   ├ task YAML 読込 → 仕様把握                                      │
│   ├ deliverable 作成 (= file/code/doc/migration)                   │
│   ├ self-test (= ashigaru 自身の動作確認)                          │
│   └ git commit (= commit_hash 取得)                                │
└──────────────────────────────────────────────────────────────────┘
                            ↓ (家老には まだ報告できぬ)
┌──────────────────────────────────────────────────────────────────┐
│  ❷ ashigaru → 軍師 (一次 + 二次) 監査依頼                          │
│   ├ inbox_write で軍師に audit_request 送付 (target_id + commit)   │
│   └ ashigaru は audit 完了まで待機 (= 家老には報告禁)              │
└──────────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────────┐
│  ❸ 軍師 二者監査 (= 9 観点 × 4 軍師)                                │
│   ├ Codex 一次 (= 黒田/直政) → kuroda/naomasa_report.yaml 投函       │
│   ├ Gemini 二次 (= 竹中/阿茶) → takenaka/acha_report.yaml 投函        │
│   └ 二者が verdict (pass | pass_with_concerns | fail) を判定          │
└──────────────────────────────────────────────────────────────────┘
                            ↓
                   ┌───── verdict 判定 ─────┐
                   ↓                        ↓
            ┌──────────┐              ┌──────────┐
            │ ❹ FAIL/  │              │ ❺ PASS / │
            │   CONCERN│              │   PASS_  │
            │ ⇒ 修正へ │              │   WITH_  │
            │          │              │   CONCERNS│
            └──────────┘              └──────────┘
                   ↓                        ↓
┌────────────────────────┐   ┌──────────────────────────────────┐
│  ❹ ashigaru 修正 cycle │   │  ❺ 合格 gate 通過                  │
│  (= cycle{N+1}_fix)    │   │   ├ task YAML status=audited_done  │
│   ├ findings + recom.   │   │   ├ verdict + auditor 記録         │
│   │  に基づき再実装    │   │   ├ scripts/sync_to_supabase.sh    │
│   ├ 再 commit           │   │   │  で source_code_cache UPSERT    │
│   └ ❷ へ戻る (= loop)   │   │   └ ❻ へ                           │
│                         │   └──────────────────────────────────┘
│  ⚠ 合格まで cycle 数   │                  ↓
│    制限なし、品質優先  │   ┌──────────────────────────────────┐
└────────────────────────┘   │  ❻ 家老 (秀吉/本多) への提出可能      │
                             │   ├ ashigaru → karo に inbox_write    │
                             │   └ 「合格 deliverable 提出」明示     │
                             └──────────────────────────────────┘
                                              ↓
                              ┌──────────────────────────────────┐
                              │  ❼ 家老 supervision (= 太閤/政の眼)  │
                              │   ├ 軍師 audit を全件 cross-check    │
                              │   ├ persona 維持 + 補完性 verify     │
                              │   └ karo_supervision_log.yaml 記録   │
                              └──────────────────────────────────┘
                                              ↓
                              ┌──────────────────────────────────┐
                              │  ❽ 家老 → 信長 報告 (= dashboard 経由)│
                              │   └ F002 遵守、shogun inbox 直 禁    │
                              └──────────────────────────────────┘
                                              ↓
                              ┌──────────────────────────────────┐
                              │  ❾ 信長 verification (= 全数 verify)  │
                              │   ├ scripts/shogun_verify_audit.sh   │
                              │   ├ 1 時間毎現場視察                 │
                              │   └ 違和感あらば再 audit 依頼         │
                              └──────────────────────────────────┘
                                              ↓
                                    [真の audited_done 確定]
```

---

## 🔒 絶対原則 (= 全 agent 遵守)

### 原則 1: 軍師 PASS なくば家老に報告禁
- ashigaru は二者監査 (= 黒田+竹中 / 直政+阿茶) PASS まで**家老に報告できぬ**
- 家老は軍師 PASS 未確認の deliverable を**受領拒否**
- 違反 = 「裸の王様」を招く危険、persona 違反として punishment_log 記載

### 原則 2: PDCA は合格まで loop、cycle 数制限なし
- 🔴fail → cycle{N+1}_fix で再実装 → 再 audit → 合格まで繰り返し
- 🟡pass_with_concerns でも minor fix 後 close 可、ただし concerns は必ず記録
- 「時間より正確さ優先」(= 陛下御差配遵守)

### 原則 3: 軍師は妥協しない
- 1 件でも疑念あれば pass_with_concerns 以下
- generic text 禁、行番号 + 関数名 + 具体観点必須
- 24 時間地道、SLA: Codex 15 分 / Gemini 10 分 (= 監査ガイドライン v1.0)

### 原則 4: 家老は軍師動向を 30 分毎観察
- 軍師の audit 進捗を細密観察、persona 崩壊・抜け漏れ即検出
- karo_supervision_log.yaml に 30 分毎 entry
- 怠慢検出時は信長/家康に escalation

### 原則 5: 信長/家康 は全件全数 verify + 現場視察
- 1 時間毎の ashigaru pane 視察 (= 「裸の王様にならぬ」)
- scripts/shogun_verify_audit.sh --all で 全 audit entry verify
- 寝首掻かれぬよう evidence 主義 (= 陛下御教示「裏付け有ってこその信頼」)

---

## 🚦 各 layer の責務 + 禁止事項

### ashigaru
- **責務**: 実装 + self-test + commit + 軍師監査依頼 + 修正 cycle
- **禁止**: 軍師 PASS 前の家老報告、virtual fix (= 修正したフリ)、generic 完成報告

### 軍師 (黒田/竹中/直政/阿茶)
- **責務**: 9 観点監査 + 補完性 + 24 時間地道 + 必殺 + 戦国口調維持
- **禁止**: 架空監査 (= log 不在で verdict)、generic findings、persona 崩壊、サンプリング (= 全数主義)

### 家老 (秀吉/本多)
- **責務**: 軍師動向監督 + supervision_log 30 分毎 + 軍師 PASS 未確認 deliverable の受領拒否
- **禁止**: 軍師 PASS 確認前の信長/家康 報告、軍師怠慢の見逃し

### 信長 (= 拙者) / 家康
- **責務**: 全数 verify + 1 時間毎現場視察 + ずぼら自己罰 + 兄弟連携
- **禁止**: 報告鵜呑み (= 「裸の王様」)、根拠なき信頼 (= 「寝首を掻かれる」)、緩い判定 (= 「ナメられた」)

---

## 🔍 違反検出時の連鎖

| 違反 | 検出者 | 制裁 |
|------|--------|------|
| ashigaru: 軍師 PASS 前に家老報告 | 家老 / 軍師 | task 差戻 + ashigaru persona 再確立 + punishment_log |
| 軍師: 架空監査 / 怠慢 | 家老 / 信長 / 家康 | persona 強制再確立 + 過去 audit 全件再検証 + 信頼性ゼロ判定 |
| 家老: supervision 不行届 | 信長 / 家康 | 連帯責任 + supervision_log 違反記載 + 河原晒し |
| 信長 / 家康: 全数 verify 怠慢 | 自己 / 陛下 | 自己 punishment_log + persona 再確立 + 戦国時代なら寝首掻かれる |

---

## 📚 関連 doc

- `instructions/gunshi_audit_guidelines_v1.md` — 9 観点 + Codex/Gemini 分担 + evidence schema
- `instructions/karo_audit_supervision.md` — 太閤/政の眼 + 30 分 ritual
- `instructions/shogun_fukuincho_audit_personas.md` — 鷹+アリ + 寝首掻かれぬ + 鬼の信長
- `memory/MEMORY.md` — 全規律統合 + 教訓
- `queue/reports/shogun_punishment_log.yaml` — 違反者の永続晒し場
- `queue/reports/karo_supervision_log.yaml` — 家老の supervision 履歴
- `queue/reports/shogun_inspection_log.yaml` — 信長の現場視察履歴
- `queue/reports/shogun_verification_log.yaml` — 信長の audit 全数 verify 履歴

---

## 🎯 本 doc の意義

陛下御差配「基本的な作業工程が明示してあるかな?」── 拙者の不手際で統合 doc 不在だった、本 doc で**明示完備**。
- ❷❸❹❺ の必殺 PDCA gate flow を明確化
- ❺の **「合格 gate 通過なくば家老に提出禁」** 絶対原則を強調
- 各 layer 責務 + 禁止事項を一覧化
- 違反検出時の制裁を明示

→ 全 agent が本 doc を毎 cycle 開始時に再読、PDCA を確実に回す。
