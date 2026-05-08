-- migrations/008_organizational_lessons_seed.sql
-- cmd_organizational_lessons_supabase_001 — 本朝事故 9 件初期 seed
--
-- 背景:
--   信長殿草案 docs/cmd_root_resolution_001_draft.md §2 表の本朝事故 9 件を初期 seed として投入。
--   本多 retrospective audit (cmd_phase16_3_honda_initial_audit_001) が UPDATE/拡張する出発点。
--
-- 適用前提:
--   - migrations/007 (organizational_lessons + audit table + RLS) apply 済
--   - service_role context で apply (= authenticated context だと RLS の writer policy で弾かれる
--     可能性がある。ただし `SET LOCAL app.current_agent = 'shogun'` でも writer 三人衆の 1 人ゆえ通過可)
--
-- 冪等性:
--   - WHERE NOT EXISTS で同 root_cause の二重投入を防止
--   - 再実行可能 (= idempotent)
--
-- License: MIT (shogun upstream credit 保持)

BEGIN;

-- seed 投入は信長殿の名で行う (= writer 三人衆の 1 人)
SET LOCAL app.current_agent = 'shogun';

-- ----------------------------------------------------------------
-- (1) §18.1 配置表 vs 実 pane drift
-- ----------------------------------------------------------------
INSERT INTO public.organizational_lessons (
    incident_date, category, root_cause, resolution, skill_impact, lessons, tags
)
SELECT
    '2026-05-08T00:00:00+09:00'::timestamptz,
    'pane_drift',
    'CLAUDE.md §18.1 配置表が静的 markdown で、Phase 4-5 体制改編 (家康 0.3 / ashigaru3 0.4 / 武田 0.5) に追従できなかった。queue/pane_registry.yaml と §18.1 が乖離し、信長自身が pane 番号を推測して gunshi 重複 pane を作成した実例 (= 2026-05-07 misidentification) を含む同型ドリフトが慢性化。',
    'cmd_root_resolution_001 Sub-Phase A (§18.1 訂正 + queue/pane_registry.yaml SSoT 昇格) + Sub-Phase H (CLAUDE.md §18.1 autogen 本格実装) で根絶予定。担当: ashigaru1 (= 本朝 split-window 復活させた当事者)。',
    'pane-identity-verify skill (= §19 第 1 号) の運用範囲を §18.1 SSoT 整合性 check まで拡張、改編時 hook で自動検証。',
    '【教訓】静的 markdown を組織編成 SSoT にすべきでない。改編は queue/pane_registry.yaml (= 機械可読) を SSoT とし、§18.1 は autogen + pre-commit hook で乖離検知。【再発防止】(1) queue/pane_registry.yaml を SSoT 昇格、(2) §18.1 autogen script + pre-commit hook、(3) 体制改編 checklist (Sub-Phase G) で必須更新箇所明示。',
    ARRAY['phase16','pane_drift','section18','self_audit','sub_phase_A','sub_phase_H']
WHERE NOT EXISTS (
    SELECT 1 FROM public.organizational_lessons
    WHERE root_cause LIKE 'CLAUDE.md §18.1 配置表が静的 markdown%'
);

-- ----------------------------------------------------------------
-- (2) inbox_watcher silent death (半日不在)
-- ----------------------------------------------------------------
INSERT INTO public.organizational_lessons (
    incident_date, category, root_cause, resolution, skill_impact, lessons, tags
)
SELECT
    '2026-05-08T00:00:00+09:00'::timestamptz,
    'watcher_silent_death',
    'inbox_watcher が SecondPC で半日 silent death、watchdog 不在で自動再起動なし。alive 確認なしの長時間放置で、SecondPC 配下の足軽群への nudge 経路が完全途絶していた。',
    'cmd_root_resolution_001 Sub-Phase B (SecondPC watchdog 新設、shim/hakudokai/hakudokai_watchdog_secondpc.sh) で根絶予定。手動停止フラグ ~/.openclaw/disable_secondpc_watchdog 尊重、restart_cap 5/h、escalation 信長 inbox。担当: ashigaru7 (SecondPC 在勤)。',
    'watchdog 系の skill 候補 — Watcher Design Principles §17 (CLAUDE.md) との整合性 check skill 新規 or 拡張。',
    '【教訓】非対話 daemon は watchdog なしでは silent death に陥る。SecondPC は MainPC subset の後付けで watchdog が省略されていた (= 2026-05-05 SecondPC 暴走対策の watchdog 自動再起動が D2 危険パターンとされ、安全装置設計が後手に回った)。【再発防止】(1) restart_cap + manual flag + escalation の 3 安全装置を必須化、(2) すべての watcher daemon にヘルスチェックファイル更新、(3) §15 SH パターン適用は危険パターン D1-D6 を必ず除外宣言。',
    ARRAY['phase16','watcher','silent_death','watchdog','sub_phase_B','secondpc']
WHERE NOT EXISTS (
    SELECT 1 FROM public.organizational_lessons
    WHERE root_cause LIKE 'inbox_watcher が SecondPC で半日 silent death%'
);

-- ----------------------------------------------------------------
-- (3) SecondPC 自律機構欠落 (activity_monitor 不在)
-- ----------------------------------------------------------------
INSERT INTO public.organizational_lessons (
    incident_date, category, root_cause, resolution, skill_impact, lessons, tags
)
SELECT
    '2026-05-08T00:00:00+09:00'::timestamptz,
    'autonomy',
    'SecondPC が MainPC の subset として後付けで増設されたため、idle 検出 + alert 配信の activity_monitor が存在せず、SecondPC 配下足軽 (a5/a6/a7) の長時間 idle が検知不能。MainPC 側の dashboard.md ハートビートが 5/15/25 分閾値を超えても SecondPC 側で気付けない構造。',
    'cmd_root_resolution_001 Sub-Phase C (shim/hakudokai/hakudokai_activity_monitor_secondpc.sh 新設) で根絶予定。alert 配信: maeda inbox (= 一次対処) + 前田殿越え時は信長 inbox (= 二次対処)。担当: ashigaru5。',
    '§15 SH4 (stale lock 自動解除) の lock holder ヘルスチェック概念を idle 検出に流用、新規 skill 化は §19.5 順守で重複回避。',
    '【教訓】PC 増設は subset 後付けで自律機構を省略しがち。組織拡張時は MainPC と同等の自律 + 監視 + alert 配信を必須化すべき。【再発防止】(1) PC 単位の activity_monitor を必須化、(2) idle 閾値 5/15/25 分を全 agent に統一適用、(3) 二段階 escalation (前田 → 信長) で MainPC 一極集中を回避。',
    ARRAY['phase16','secondpc','autonomy','activity_monitor','sub_phase_C']
WHERE NOT EXISTS (
    SELECT 1 FROM public.organizational_lessons
    WHERE root_cause LIKE 'SecondPC が MainPC の subset として後付けで増設%'
);

-- ----------------------------------------------------------------
-- (4) maeda self-audit 機構なし
-- ----------------------------------------------------------------
INSERT INTO public.organizational_lessons (
    incident_date, category, root_cause, resolution, skill_impact, lessons, tags
)
SELECT
    '2026-05-08T00:00:00+09:00'::timestamptz,
    'self_audit',
    'maeda persona §4 セルフチェック規定が書面のみで enforce 機構なし。配下 (ashigaru5/6/7) idle 放置 + 自身の役割逸脱を maeda 自身が定期的にチェックする実装が存在せず、信長 inbox 経由の事後検出に依存していた。',
    'cmd_root_resolution_001 Sub-Phase D (scripts/maeda_self_audit.sh + cron 30 分間隔) で根絶予定。違反検知 (idle 配下放置 等) で maeda 自身 alert、結果は dashboard.md SecondPC セクション + 信長 inbox 月次サマリ。担当: maeda 自身 (= 自律性確立)。',
    '§19 mandate (post-incident lessons capture) の self-audit 版 — 「persona 規定が enforce 機構を伴う」という skill 候補、新規 skill 検討対象。',
    '【教訓】persona 規定は enforce 機構なしでは形骸化する。すべての中間管理職 persona には self-audit script + cron 化を必須化すべき。【再発防止】(1) maeda self-audit script 実装、(2) 全 persona §4 規定を enforce 化 (= 家康 / 本多 / 竹中 / maeda 全員)、(3) 月次サマリで信長検証。',
    ARRAY['phase16','maeda','self_audit','persona','sub_phase_D']
WHERE NOT EXISTS (
    SELECT 1 FROM public.organizational_lessons
    WHERE root_cause LIKE 'maeda persona §4 セルフチェック規定が書面のみ%'
);

-- ----------------------------------------------------------------
-- (5) misroute bug 同型再発
-- ----------------------------------------------------------------
INSERT INTO public.organizational_lessons (
    incident_date, category, root_cause, resolution, skill_impact, lessons, tags
)
SELECT
    '2026-05-08T00:00:00+09:00'::timestamptz,
    'misroute',
    'shim/hakudokai/hakudokai_secondpc_receiver_poll.py の valid_secondpc / AGENT_PANES が hardcode で、体制改編 (maeda 追加 等) に追従できず misroute bug が同型再発。lib/_section18_roles.sh + shim/hakudokai/_section18_roles.py という SSoT 候補は存在するが、receiver は hardcode のまま乖離。',
    'cmd_root_resolution_001 Sub-Phase E (routing SSoT 化) で根絶予定。lib/_section18_roles.sh + shim/hakudokai/_section18_roles.py を SSoT として参照、hardcode 廃止。担当: ashigaru6 (cmd_secondpc_receiver_routing_fix と integrated)。直近 fix: commit 7777a9b ''secondpc-receiver: maeda valid_secondpc 登録'' は対症療法で、構造的根絶は本 Sub-Phase E。',
    '同型 bug 検知 skill — routing hardcode 検出 + SSoT 整合性 check の skill 新規 or 既存 pre-build-check 拡張で対処。',
    '【教訓】配置 / routing / role を hardcode した時点で「改編に追従しない」と確定する。SSoT を 1 箇所に集約し、receiver / dispatcher は SSoT 参照のみ許可。【再発防止】(1) routing SSoT 化、(2) 体制改編 simulation で SSoT 1 箇所更新 → 全 receiver 自動反映を acceptance criteria 化、(3) hardcode 検出 lint を pre-commit hook 追加。',
    ARRAY['phase16','misroute','ssot','routing','sub_phase_E']
WHERE NOT EXISTS (
    SELECT 1 FROM public.organizational_lessons
    WHERE root_cause LIKE 'shim/hakudokai/hakudokai_secondpc_receiver_poll.py%'
);

-- ----------------------------------------------------------------
-- (6) token 蓄積限界 (243.6k 限界後 input lost)
-- ----------------------------------------------------------------
INSERT INTO public.organizational_lessons (
    incident_date, category, root_cause, resolution, skill_impact, lessons, tags
)
SELECT
    '2026-05-08T00:00:00+09:00'::timestamptz,
    'token_limit',
    'agent の token 累積を 80% 閾値で検出する機構が存在せず、243.6k 限界に到達してから input lost (= 受信不能) が発覚。事前の自動 /clear escalation がなく、context size 警告 inbox 通知のみで agent 自身に判断委ねていた (= 本朝 ashigaru1 inbox に 1:54 / 3:12 / 4:29 / 5:46 / 7:03 と複数回警告蓄積、reactive 対応にとどまった)。',
    'cmd_root_resolution_001 Sub-Phase F (scripts/agent_health_check.sh 強化) で根絶予定。tmux capture-pane で "Xk tok" pattern 検出、80% 閾値 → maeda or 秀吉 inbox 警告、95% 閾値 → 信長 inbox + 自動 /clear command 発動 (= preempt input lost)。担当: ashigaru2。',
    'token_limit_escalation skill 候補 — 既存 pane-identity-verify と同列の advisory + auto-action skill 新規。',
    '【教訓】reactive 通知のみでは agent 自身の判断遅延で限界突破する。preemptive な auto-action (自動 /clear) を 95% 閾値で発動すべき。【再発防止】(1) token capture-pane detection 80%/95% 二段階、(2) 95% で自動 /clear、(3) 履歴を本 organizational_lessons table に蓄積。',
    ARRAY['phase16','token','limit','clear_escalation','sub_phase_F']
WHERE NOT EXISTS (
    SELECT 1 FROM public.organizational_lessons
    WHERE root_cause LIKE 'agent の token 累積を 80%% 閾値で検出%'
);

-- ----------------------------------------------------------------
-- (7) Phase 4-5 体制改編の追従漏れ
-- ----------------------------------------------------------------
INSERT INTO public.organizational_lessons (
    incident_date, category, root_cause, resolution, skill_impact, lessons, tags
)
SELECT
    '2026-05-08T00:00:00+09:00'::timestamptz,
    'regime_change',
    'Phase 4-5 体制改編 (maeda / 武田 / 竹中 等の persona 追加) で必須更新箇所 (§18.1 / config/settings.yaml / lib/_section18_roles.sh / shim 各 receiver / shutsujin scripts) のチェックリストが不在、maeda が valid_secondpc に未登録のまま運用開始 → misroute (項目 5) の遠因となった。',
    'cmd_root_resolution_001 Sub-Phase G (docs/regime_change_checklist.md 新規 + post-改編 audit cmd template) で根絶予定。担当: 本多 (組織改革専門、Phase 16-3 と integrated)。',
    'regime_change_checklist skill 候補 — 本多実働化 (Phase 16-2 完遂、scripts/audit_meta_codex.sh) と integrated。',
    '【教訓】体制改編は影響範囲が複数 file に及ぶため、checklist 不在では追従漏れが必ず発生する。【再発防止】(1) docs/regime_change_checklist.md で必須更新箇所明示、(2) post-改編 audit cmd template 標準化、(3) 改編 commit に checklist consumption tag 必須化。',
    ARRAY['phase16','regime_change','checklist','maeda_unregistered','sub_phase_G']
WHERE NOT EXISTS (
    SELECT 1 FROM public.organizational_lessons
    WHERE root_cause LIKE 'Phase 4-5 体制改編 (maeda / 武田 / 竹中 等%'
);

-- ----------------------------------------------------------------
-- (8) CLAUDE.md §18.1 lock-in
-- ----------------------------------------------------------------
INSERT INTO public.organizational_lessons (
    incident_date, category, root_cause, resolution, skill_impact, lessons, tags
)
SELECT
    '2026-05-08T00:00:00+09:00'::timestamptz,
    'section18_lockin',
    'CLAUDE.md §18.1 が静的 markdown ゆえ、コードや registry との乖離を CI で検知する仕組みなし。改編が反映されない / 反映が遅れる → 配下が古い情報で動作する → pane_drift / misroute の温床となる構造的欠陥。',
    'cmd_root_resolution_001 Sub-Phase H (CLAUDE.md §18.1 autogen 本格実装) で根絶予定。queue/pane_registry.yaml + lib/_section18_roles.sh から §18.1 自動生成、pre-commit hook で §18.1 と registry の整合性 check。担当: ashigaru1 (Phase A と integrated)。',
    'pane-identity-verify skill (§19 第 1 号) と integrated、CLAUDE.md ↔ registry 整合性 check skill として拡張候補。',
    '【教訓】重要な構造定義を「人手で書く markdown」に置くと、改編で必ず置き去りになる。autogen + pre-commit が必須。【再発防止】(1) §18.1 autogen、(2) pre-commit hook で乖離検知、(3) registry 改編は §18.1 自動再生成を伴う commit 単位で運用。',
    ARRAY['phase16','section18','autogen','static_markdown','sub_phase_H']
WHERE NOT EXISTS (
    SELECT 1 FROM public.organizational_lessons
    WHERE root_cause LIKE 'CLAUDE.md §18.1 が静的 markdown ゆえ%'
);

-- ----------------------------------------------------------------
-- (9) §19 skill が破られる (信長自陳)
-- ----------------------------------------------------------------
INSERT INTO public.organizational_lessons (
    incident_date, category, root_cause, resolution, skill_impact, lessons, tags
)
SELECT
    '2026-05-08T00:00:00+09:00'::timestamptz,
    'skill_violation',
    '§19 mandate で生成された skill (= 第 1 号 pane-identity-verify) が advisory hook (= ブロックせず stderr 警告のみ、|| true 必須) ゆえ実効性が低く、信長自身が pane 番号推測で gunshi 重複 pane を作成する違反を犯した (= 2026-05-07 misidentification の再発要因)。skill 違反履歴の永続蓄積基盤も未整備。',
    'cmd_root_resolution_001 Sub-Phase J (§19 skill 強化) で根絶予定。skills/pane-identity-verify/SKILL.md の advisory hook 強化、信長自身も適用、skill 違反履歴を本 organizational_lessons table に蓄積 (= cmd_organizational_lessons_supabase_001 と integrated)。担当: 本多 (retrospective audit + 改革提言と integrated)。',
    'pane-identity-verify skill 自体の強化 — advisory hook の段階的 enforcement (= warn → require ack → block) を §19.3 強制力ルールと両立させる設計検討。',
    '【教訓】advisory only の skill は「破ってもよい」と解釈される構造的弱点を持つ。enforce 段階を時間経過 + 違反回数で escalate させる仕組み必要。【再発防止】(1) skill 違反は本 table に必ず INSERT、(2) 違反回数 N 件超過で hook を warn → ack 要求 → block へ自動 escalate、(3) 信長自身も skill 適用対象、自陳録 commit で透明化。',
    ARRAY['phase16','section19','skill','advisory_hook','shogun_self_confession','sub_phase_J']
WHERE NOT EXISTS (
    SELECT 1 FROM public.organizational_lessons
    WHERE root_cause LIKE '§19 mandate で生成された skill%'
);

COMMIT;

-- ============================================================
-- 動作確認 SQL (= apply 後の検証用、参考)
-- ============================================================
-- SELECT count(*) FROM public.organizational_lessons;        -- 期待: 9 (初回 apply) or 既存数
-- SELECT category, count(*) FROM public.organizational_lessons GROUP BY category ORDER BY 1;
-- SELECT count(*) FROM public.organizational_lessons_audit
--   WHERE operation = 'INSERT';                              -- 期待: 9 (= 初回 seed の trigger 記録)
