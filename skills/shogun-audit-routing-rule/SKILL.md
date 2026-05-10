---
name: shogun-audit-routing-rule
description: |
  軍師 audit routing rule の HARD ENFORCEMENT スキル。
  プログラム監査は **Codex 限定** (kuroda/naomasa)、Gemini (takenaka/acha) は plan/起草/戦略 doc 専担。
  陛下御差配 2026-05-10 で確立。
  「audit routing」「プログラム監査」「Codex 限定」「軍師 domain」で起動。
  Do NOT use for: 個別 audit 実行 (= audit_via_supabase.sh 直接利用)。
argument-hint: "[<target_scope>]  (= validation で routing を返す)"
allowed-tools: Bash, Read
---

# /shogun-audit-routing-rule — Codex/Gemini Domain 振分 HARD ルール

## North Star

陛下御差配 (2026-05-10):
> **「プログラム監査は CODEX のみに限定」**

## 鉄則

| Domain | 監査者 | 例 |
|--------|--------|-----|
| **Program / Code** | **Codex 限定** (kuroda / naomasa) | ashigaru deliverable、.py/.sh/.ts file、commit、implementation |
| **Plan / 起草 / 戦略** | Gemini (takenaka / acha) | cmd YAML、design doc、roadmap、acceptance_criteria |
| **Cross-domain** | 両軍師合同 | cmd YAML に code snippet 含 |

## 違反時 HARD STOP

`audit_via_supabase.sh` の `audit_run_local` / `audit_submit_async` で:
- `gunshi=takenaka|acha` + scope に `ashigaru|deliverable|implementation|code|file|commit|.py|.sh|.ts|.tsx` 含 → exit 90 で拒否
- エラー message で「Codex (kuroda/naomasa) を使え」を提示

## 自動振分 logic (= shogun が target → 軍師選定する際)

```
target が ashigaru* / 実装 file / commit hash → kuroda (MainPC) or naomasa (SecondPC)
target が cmd_* / design doc / strategy → takenaka (MainPC) or acha (SecondPC)
target が両 domain → 両軍師に並列 submit (= cross-domain 合同監査)
```

## 既存 doc 整合

`instructions/gunshi_audit_guidelines_v1.md` 1-4a section と整合:
- v1.1 Domain split をハード強制化
- doc-rule から code-enforced rule へ昇格

## When to Use

- プログラム deliverable を audit 投函する時 (= routing 確認)
- 新規 audit pipeline 設計時 (= rule 参照)
- 監査結果集計時 (= domain 別 verdict 集計)

## Memory

陛下御教示: 「プログラム監査は CODEX のみに限定。スキルかルールを作る」
→ 本 skill で **code 側 HARD enforce** + doc で明文化。
→ 違反試行は exit 90 で即座に refuse、運用ミス防止。

## Related

- `lib/audit_via_supabase.sh` — wrapper、本 rule の primary enforcement layer
- `instructions/gunshi_audit_guidelines_v1.md` 1-4a — doc 規定
- `skills/shogun-pdca-enforcer/` — PDCA 強制執行、本 rule に従って軍師 routing
