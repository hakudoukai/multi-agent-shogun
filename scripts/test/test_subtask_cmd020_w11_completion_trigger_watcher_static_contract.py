"""Static source-contract tests for cmd_020 W11 completion trigger watcher.

Targets:
  - scripts/watch_w11_trigger.sh                                  (= ops one-shot script)
  - systemd/dashboard-w11-trigger.service                          (= systemd unit)
  - systemd/dashboard-w11-trigger.timer                            (= systemd timer)
  - docs/cmd020_w11_trigger_worker_eval_gate_check.md              (= worker_eval 13 fields)
  - queue/reports/ashigaru5_subtask_cmd020_w11_completion_trigger_watcher_inventory.yaml

Test nature: static source-contract grep + structural assertion (= network /
Supabase / agent unrelated)。pytest 単独実行で完結する。

Cycle5 naomasa pre_audit (= queue/reports/naomasa_cmd020_w11_trigger_preaudit_cycle5_20260513.yaml)
conditions 直接反映:
  - all worker_eval fields populated
  - no persistent sleep loop (= resident process 禁)
  - direct audited_done absent
  - timer/service files named explicitly

Repo: multi-agent-shogun-newbuild (= hakudokai-dev 関与禁、本 task 範囲外)。
Pattern: scripts/test/test_dashboard_layer_e_static_contract.py 規範整合。
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
WATCHER_SCRIPT = REPO_ROOT / "scripts" / "watch_w11_trigger.sh"
SYSTEMD_SERVICE = REPO_ROOT / "systemd" / "dashboard-w11-trigger.service"
SYSTEMD_TIMER = REPO_ROOT / "systemd" / "dashboard-w11-trigger.timer"
EVAL_GATE_DOC = REPO_ROOT / "docs" / "cmd020_w11_trigger_worker_eval_gate_check.md"
INVENTORY_YAML = (
    REPO_ROOT
    / "queue"
    / "reports"
    / "ashigaru5_subtask_cmd020_w11_completion_trigger_watcher_inventory.yaml"
)

# worker_eval 13 fields (= docs/background_worker_eval_gate.md §Decision Record Template)
WORKER_EVAL_FIELDS = [
    "id",
    "proposed_by",
    "failure_mode",
    "trigger_type",
    "cadence_reason",
    "max_runtime_sec",
    "retry_count",
    "backoff",
    "audit_trail_path",
    "health_signal",
    "stop_or_disable",
    "pii_secret_policy",
    "completion_gate_interaction",
]

# 6 questions Q1〜Q6 (= 正本 §Evaluation Gate)
SIX_QUESTIONS = ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6"]

# Anti-Patterns 6 件 (= 正本 §Anti-Patterns)
ANTI_PATTERNS = [
    "Polling loop where an event exists",
    "Always-on manager without ownership",
    "Unbounded retry",
    "Narrative-only trust score",
    "Silent repair",
    "Completion by side effect",
]


@pytest.fixture(scope="module")
def watcher_text() -> str:
    assert WATCHER_SCRIPT.is_file(), f"watcher script missing: {WATCHER_SCRIPT}"
    return WATCHER_SCRIPT.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def service_text() -> str:
    assert SYSTEMD_SERVICE.is_file(), f"systemd service missing: {SYSTEMD_SERVICE}"
    return SYSTEMD_SERVICE.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def timer_text() -> str:
    assert SYSTEMD_TIMER.is_file(), f"systemd timer missing: {SYSTEMD_TIMER}"
    return SYSTEMD_TIMER.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def eval_doc_text() -> str:
    assert EVAL_GATE_DOC.is_file(), f"worker_eval doc missing: {EVAL_GATE_DOC}"
    return EVAL_GATE_DOC.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def inventory_text() -> str:
    assert INVENTORY_YAML.is_file(), f"inventory yaml missing: {INVENTORY_YAML}"
    return INVENTORY_YAML.read_text(encoding="utf-8")


# ─────────────────────────────────────────────────────────────────────
# Test 1: worker_eval 13 fields all populated (= cycle5 finding §6_test 解消)
# ─────────────────────────────────────────────────────────────────────
def test_worker_eval_13_fields_all_populated(eval_doc_text: str) -> None:
    """docs/cmd020_w11_trigger_worker_eval_gate_check.md に 13 fields 全件 +
    decision=approve_with_concerns 以上 + 6 質問 1-to-1 mapping + anti-pattern
    自検 全件が存在する。"""

    # 13 fields の anchor 出現 (= self-check table 行 + yaml block 行 両方で証跡)
    missing_fields = [f for f in WORKER_EVAL_FIELDS if f not in eval_doc_text]
    assert not missing_fields, (
        f"worker_eval 13 fields 未記載: {missing_fields}"
    )

    # 6 質問 Q1〜Q6 が独立 section として出現
    for q in SIX_QUESTIONS:
        assert re.search(rf"###\s+{q}\b", eval_doc_text), (
            f"6 questions 1-to-1 mapping 不足: {q} section anchor 不在"
        )

    # decision = approve_with_concerns 以上 (= approve_with_concerns / approve)
    assert re.search(
        r"decision:\s*(approve_with_concerns|approve)\b", eval_doc_text
    ), "decision: approve_with_concerns 以上 が yaml block に無い"

    # anti-pattern 全件自検 evidence
    missing_anti = [ap for ap in ANTI_PATTERNS if ap not in eval_doc_text]
    assert not missing_anti, (
        f"Anti-Patterns 自検 evidence 不足: {missing_anti}"
    )


# ─────────────────────────────────────────────────────────────────────
# Test 2: no persistent sleep loop (= resident process 禁、Anti-Pattern guard)
# ─────────────────────────────────────────────────────────────────────
def test_no_persistent_sleep_loop(watcher_text: str, service_text: str) -> None:
    """scripts/watch_w11_trigger.sh が resident process 化していない:
    - while true / for(;;) 等の永続 loop 不在
    - sleep <large> による delay loop 不在
    - systemd service の Type=oneshot 明示
    """
    # while true / while : / for (;;) などの永続 loop guard
    forbidden_loop_patterns = [
        r"while\s+true\b",
        r"while\s+:\s*;",
        r"for\s*\(\s*;\s*;\s*\)",
    ]
    for pat in forbidden_loop_patterns:
        assert not re.search(pat, watcher_text), (
            f"watcher script に persistent loop 検出: pattern={pat}"
        )

    # sleep N (N >= 30) の resident delay loop guard
    # (timer tick 内の bounded sleep <30s は許容、ただし本 watcher は使用しない)
    sleep_matches = re.findall(r"\bsleep\s+(\d+)", watcher_text)
    for num in sleep_matches:
        assert int(num) < 30, (
            f"watcher script に長 sleep 検出 (resident 化 risk): sleep {num}"
        )

    # systemd service Type=oneshot 明示
    assert re.search(r"^Type=oneshot\b", service_text, re.MULTILINE), (
        "systemd service に Type=oneshot 明示が無い (= resident 化 risk)"
    )


# ─────────────────────────────────────────────────────────────────────
# Test 3: direct audited_done 禁 (= completion_gate_interaction guard)
# ─────────────────────────────────────────────────────────────────────
def test_no_direct_audited_done_write(watcher_text: str, eval_doc_text: str) -> None:
    """watcher script は audited_done / shogun_verified の status 直接書込を
    含まず、completion_gate_interaction の禁則は doc に明記される。"""
    # 書込操作系の anchor (= echo > / printf > / sed -i / cat <<EOF >) と
    # audited_done / shogun_verified の組合せが script に同居しないことを確認。
    write_ops = ["echo", "printf", "cat <<", "sed -i", "tee"]
    for line in watcher_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        if "audited_done" in stripped or "shogun_verified" in stripped:
            # コメント外で出現すること自体が禁
            pytest.fail(
                f"watcher script の非コメント行に audited_done/shogun_verified が出現: '{line}'"
            )
        # write op と shogun_verification_log の組合せも禁
        if "shogun_verification_log" in stripped and any(op in stripped for op in write_ops):
            pytest.fail(
                f"watcher script で shogun_verification_log への書込 op 検出: '{line}'"
            )

    # doc に completion_gate_interaction の禁則明記がある
    assert "direct" in eval_doc_text and "audited_done" in eval_doc_text, (
        "worker_eval doc に direct audited_done 禁の明記が無い"
    )
    assert re.search(
        r"completion_gate_interaction\s*:", eval_doc_text
    ), "worker_eval doc に completion_gate_interaction field が無い"


# ─────────────────────────────────────────────────────────────────────
# Test 4: systemd timer / service files named explicitly + cadence integrity
# ─────────────────────────────────────────────────────────────────────
def test_timer_service_files_named_and_bounded(
    service_text: str, timer_text: str, eval_doc_text: str
) -> None:
    """systemd unit が名指しで存在し、cadence (10-15 min) + TimeoutStartSec
    (60s) + Persistent=true + 名指し ExecStart が整合する。"""
    # service: ExecStart に watch_w11_trigger.sh が含まれる
    assert "watch_w11_trigger.sh" in service_text, (
        "service の ExecStart に watch_w11_trigger.sh anchor が無い"
    )
    # service: TimeoutStartSec=60 (= max_runtime_sec 整合)
    assert re.search(r"^TimeoutStartSec=60\b", service_text, re.MULTILINE), (
        "service の TimeoutStartSec=60 anchor が無い (= max_runtime_sec=60 整合)"
    )

    # timer: OnUnitActiveSec が 600〜900 (= 10〜15 min) の範囲
    m = re.search(r"^OnUnitActiveSec=(\d+)s?\b", timer_text, re.MULTILINE)
    assert m, "timer に OnUnitActiveSec= anchor が無い"
    cadence_sec = int(m.group(1))
    assert 600 <= cadence_sec <= 900, (
        f"OnUnitActiveSec={cadence_sec}s は 600〜900 範囲外 (= 10-15min cadence 整合違反)"
    )

    # timer: Persistent=true (= 系統復帰時 catch up)
    assert re.search(r"^Persistent=true\b", timer_text, re.MULTILINE), (
        "timer に Persistent=true anchor が無い"
    )

    # timer: Unit=dashboard-w11-trigger.service (= 名指し binding)
    assert re.search(
        r"^Unit=dashboard-w11-trigger\.service\b", timer_text, re.MULTILINE
    ), "timer の Unit= binding に dashboard-w11-trigger.service が無い"

    # doc 側に "dashboard-w11-trigger" anchor が存在 (= cycle5 finding §6_test 解消)
    assert "dashboard-w11-trigger.timer" in eval_doc_text, (
        "worker_eval doc に dashboard-w11-trigger.timer 名指し anchor が無い"
    )
    assert "dashboard-w11-trigger.service" in eval_doc_text, (
        "worker_eval doc に dashboard-w11-trigger.service 名指し anchor が無い"
    )


# ─────────────────────────────────────────────────────────────────────
# Test 5: AC0 inventory + target W11 候補 + scope_exclusion 整合
# ─────────────────────────────────────────────────────────────────────
def test_inventory_and_target_w11_candidates(
    inventory_text: str, watcher_text: str, eval_doc_text: str
) -> None:
    """inventory yaml に W11 2 候補 + worker_eval 関連 6 component が記載され、
    watcher script と doc に同じ 2 候補が明示される。"""
    # inventory yaml に W11 2 候補
    for cand in ("C-V29-W11DDA", "C-V30-W11DDB"):
        assert cand in inventory_text, (
            f"inventory yaml に W11 候補 {cand} anchor が無い"
        )
        assert cand in watcher_text, (
            f"watcher script に W11 候補 {cand} anchor が無い"
        )
        assert cand in eval_doc_text, (
            f"worker_eval doc に W11 候補 {cand} anchor が無い"
        )

    # inventory に 6 新規 component (= absent 立証)
    required_components = [
        "watch_w11_trigger_script",
        "dashboard_w11_trigger_systemd_unit",
        "watch_w11_trigger_run_log",
        "watch_w11_trigger_heartbeat",
        "watch_w11_trigger_log_file",
        "worker_eval_gate_check_doc",
    ]
    for comp in required_components:
        assert comp in inventory_text, (
            f"inventory yaml に新規 component {comp} anchor が無い"
        )

    # scope_exclusion で hakudokai-dev 不在明示 (= multi-agent-shogun-newbuild only)
    assert "hakudokai-dev" in inventory_text, (
        "inventory yaml に hakudokai-dev scope_exclusion anchor が無い"
    )
    assert "multi-agent-shogun-newbuild" in inventory_text, (
        "inventory yaml に multi-agent-shogun-newbuild repo 明記が無い"
    )
