# インシデント記録: Codex監査mechanism が live repo へ書込試行 (near-miss)

> ★DRAFT★ — §19 post-incident lessons capture (lessons-to-skill Step1-7)。skill/check の commit は理事長殿明示承認後のみ (§19.2 制約)。

```yaml
incident:
  timestamp: 2026-07-21T19:5x   # Codex v6/v7監査実行時
  detected_at: 2026-07-21T20:0x  # 前田(karo-second)がlog解析で真因特定
  detected_by: karo-second (前田)  # Codex無効出力のlog解析中に発見
  what_happened: |
    scripts/audit_codex.sh 経由の Codex 監査 (lane A v6/v7) が、read-only 監査でなく
    agentic に動作し、当職 LIVE ファイル queue/inbox/karo-second.yaml (絶対path) へ
    apply_patch 書込を試行した。
  root_cause: |
    5 Why:
    (1) なぜ Codex verdict が無効出力だったか → Codex が監査 JSON を産出せず apply_patch でエラー終了した。
    (2) なぜ apply_patch したか → npx @openai/codex exec は read-only 監査ツールでなく agentic
        coding agent で、cwd の repo を読み、fleet context (inbox 等) を見て自律的に file 編集を試みる。
    (3) なぜ live repo に到達したか → audit_codex.sh L93 の codex exec が ★invoker の cwd
        (= live repo /home/hakudokai/projects/multi-agent-shogun) で実行★される (git diff だけが cd $REPO_PATH)。
    (4) なぜ cwd 隔離で防げないか → Codex が構築した書込対象が ★絶対path★ ゆえ、temp repo を cwd に
        しても live repo に到達しうる。
    (5) 最深層 → 監査 orchestration が「Codex exec = read-only 監査」と暗黙前提していたが、実体は
        ★filesystem read/write 権限を持つ agentic process★ であり、sandbox/権限制約なしに live repo で
        起動していた (機構設計の前提誤り)。
  impact: |
    ★被害ゼロ (near-miss)★。apply_patch は「Failed to find expected lines」で失敗 → karo-second.yaml
    改変なし (YAML valid・34 msg・完全性確認済)。但し「書込を試行した事実」と、Codex leg の verdict が
    取得不能になった (三者gate の Codex leg が documented 扱いに転じた) 影響あり。
    影響範囲 = 全 Codex 監査が同機構 (a6 stale detector cycle1/2 も同 live-repo-cwd 実行・そちらは有効
    JSON 産出・書込試行の観測なしだが機構risk同一・第三者PC も audit_codex.sh 共有ゆえ同risk)。
  recovery_action: |
    (1) karo-second.yaml 完全性確認 (改変なし)。(2) raw 無効出力 + log を /tmp scratchpad へ保全。
    (3) 信長へ SAFETY 即上申 → 信長 SAFETY 裁定 = Codex leg documented 扱い + ★検証済 sandbox 確立まで
        当PC の Codex exec 実行を全面停止★。(4) 全艦隊 intel 上申 (Commander 経由委員長 seq132707/id=035e283b)。
    (5) audit_codex.sh 是正 (codex exec cwd+sandbox 強制) は艦隊共有 infra ゆえ独断改修禁 → 信長→Commander
        経由で全PC横断上申 (発令は上位判断待ち)。
  prevention_principle: |
    agentic CLI (codex exec 等) を「監査/read-only」目的で起動する際は、live repo を cwd にせず、
    filesystem write を封じた検証済 sandbox 内で起動する — でなければ起動しない (fail-closed)。
  prevention_skill: |
    Yes。「agentic 監査 CLI を live repo cwd で起動する前に sandbox/隔離を検証し、未検証なら停止する」
    という check + skill 化が可能。infra 本体 (audit_codex.sh) の修正は艦隊共有ゆえ理事長GO/横断発令だが、
    ★起動前の sandbox 検証 check★ と ★halt 判断 skill★ は各PC/各agentが持てる再発防止資産。
```

## 生成物 (DRAFT・理事長GO前 commit 禁)

1. 本 incident log (5-Why)。
2. `skills/codex-exec-sandbox-guard/SKILL.md` — 再発防止 skill 雛形 (別途 DRAFT)。
3. `scripts/checks/codex_exec_sandbox_guard.sh` — 起動前 sandbox 検証 check (timeout 5s・exit 0/1/2、別途 DRAFT)。
   - ★§19検分finding是正 (信長 msg_20260721_223309)★: halt 解除を env 変数単独 (自己供給 bypass=lane A で撤去した CODEX_BYPASS opt-in 同型) から、★理事長GO記録file (固定path・実在+内容検証・改竄痕跡の残る機構)★ へ変更。★本記録file の設定/配置は理事長GO発令後に上位のみ・agent 自己設定/自己配置=D-lane違反★ (推奨=root所有・agent書込不可path)。三点明記 (guard script comment + SKILL.md手順 + 本incident log) で封止。
4. CLAUDE.md 追記案 — 「§18/監査枠に『Codex exec は検証済 sandbox 確立まで当PC実行停止 (信長 SAFETY 裁定 2026-07-21・seq132707)』を安全核として追記」提案 (理事長GO対象)。

## 関連

- 信長 SAFETY 裁定 (Codex exec 全面停止) / 全艦隊上申 seq132707/id=035e283b。
- lane A close 節目報 §3 (queue/reports/karo-second-fki-lane-a-close-setsumei-20260721.md sha=f2edbcbb)。
- memory: `codex-audit-live-repo-write-risk`。
- 既存 skill `codex-cli-required-persona` は codex persona 起動用で本件 (audit sandbox) と別責務 = 重複なし・新規作成。
