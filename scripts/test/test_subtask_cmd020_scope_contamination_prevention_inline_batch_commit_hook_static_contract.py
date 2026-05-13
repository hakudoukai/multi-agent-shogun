"""Static source-contract tests for cmd_020 scope_contamination 根本治療 deliverables.

Targets:
  - docs/scope_contamination_prevention.md (= 規範 source-of-truth)
  - .pre-commit-config.yaml (= staged-residual-check hook 装備)
  - scripts/lint/check_staged_residual.sh (= pre-commit hook entrypoint)

Test nature: markdown / yaml / shell-script grep + section/field/anchor presence check
(= 静的 source-contract、network / Supabase / agent unrelated). pytest 単独実行で完結する。

Repo: multi-agent-shogun-newbuild (= hakudokai-dev 関与禁、本 task 範囲外).
"""
from __future__ import annotations

import os
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
DOC = REPO_ROOT / "docs" / "scope_contamination_prevention.md"
HOOK_CFG = REPO_ROOT / ".pre-commit-config.yaml"
HOOK_SH = REPO_ROOT / "scripts" / "lint" / "check_staged_residual.sh"


@pytest.fixture(scope="module")
def doc_text() -> str:
    assert DOC.is_file(), f"scope_contamination_prevention.md missing: {DOC}"
    return DOC.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def cfg_text() -> str:
    assert HOOK_CFG.is_file(), f".pre-commit-config.yaml missing: {HOOK_CFG}"
    return HOOK_CFG.read_text(encoding="utf-8")


def test_pre_commit_config_has_staged_residual_check(cfg_text: str) -> None:
    """`.pre-commit-config.yaml` に `id: staged-residual-check` hook + entrypoint 記載がある。"""
    assert "id: staged-residual-check" in cfg_text, (
        ".pre-commit-config.yaml に `id: staged-residual-check` hook が無い (= 規範 ii 未装備)"
    )

    entry_pattern = re.compile(
        r"entry:\s*bash\s+scripts/lint/check_staged_residual\.sh"
    )
    assert entry_pattern.search(cfg_text), (
        "staged-residual-check hook の entrypoint (= bash scripts/lint/check_staged_residual.sh) が無い"
    )

    # 既存 hook (secret-detect-staged / deliverable-tracked) も retain されている
    assert "id: secret-detect-staged" in cfg_text, (
        "既存 hook (secret-detect-staged) が retain されていない (= 規範文書 §5 cross-reference 違反)"
    )
    assert "id: deliverable-tracked" in cfg_text, (
        "既存 hook (deliverable-tracked) が retain されていない (= 規範文書 §5 cross-reference 違反)"
    )


def test_scope_contamination_prevention_doc_4_measures_present(doc_text: str) -> None:
    """規範文書 §3 に再発防止策 4 件 sub-section (= §3.1 〜 §3.4) 全件 anchor がある。"""
    required_subsections = [
        r"^###\s+3\.1[^\n]*inline batch commit",
        r"^###\s+3\.2[^\n]*pre-commit hook",
        r"^###\s+3\.3[^\n]*audit gate",
        r"^###\s+3\.4[^\n]*pre-commit verify",
    ]
    missing = []
    for pat in required_subsections:
        if not re.search(pat, doc_text, re.MULTILINE):
            missing.append(pat)
    assert not missing, f"再発防止策 4 件 sub-section から欠落: {missing}"

    # main §3 anchor も存在
    main_section = re.compile(r"^##\s+3\.\s+再発防止策\s+4\s*件", re.MULTILINE)
    assert main_section.search(doc_text), (
        "§3 main section (= '## 3. 再発防止策 4 件') が無い"
    )


def test_check_staged_residual_script_present_and_executable() -> None:
    """`scripts/lint/check_staged_residual.sh` が存在し executable bit が立っている。"""
    assert HOOK_SH.is_file(), f"check_staged_residual.sh missing: {HOOK_SH}"
    mode = HOOK_SH.stat().st_mode
    assert mode & 0o111, (
        f"check_staged_residual.sh が executable でない (mode={oct(mode)})"
    )

    body = HOOK_SH.read_text(encoding="utf-8")
    # shebang + 集合差ロジック anchor
    assert body.startswith("#!/usr/bin/env bash"), "shebang が無い or 想定外"
    assert "git diff --cached --name-only" in body, (
        "集合差検査の staged_set 取得 (= git diff --cached --name-only) anchor が無い"
    )
    assert "residual" in body, "residual 検出ロジック anchor が無い"
    assert "exit 1" in body, "exit 1 (= 検出時の中止) が script 内に無い"


def test_audit_gate_staged_check_section_present(doc_text: str) -> None:
    """規範文書 §3.3 に直政 audit gate「staged 残存 check」追加項目の明文化がある。"""
    # §3.3 sub-section 自体
    subsection = re.compile(r"^###\s+3\.3[^\n]*audit gate", re.MULTILINE)
    assert subsection.search(doc_text), "§3.3 sub-section が無い"

    # 事前監査 + 事後監査 双方の check 項目 anchor
    assert "事前監査" in doc_text, "事前監査 anchor が §3.3 内に無い"
    assert "事後監査" in doc_text, "事後監査 anchor が §3.3 内に無い"

    # staged 残存 / 残存ゼロ keyword の双方
    residual_count = len(re.findall(r"staged\s*残存", doc_text))
    assert residual_count >= 3, (
        f"'staged 残存' anchor が {residual_count} 件、最低 3 件要 (= §2 + §3.2 + §3.3)"
    )


def test_ashigaru_report_pre_commit_verify_field_section_present(doc_text: str) -> None:
    """規範文書 §3.4 に完遂報告 yaml `pre_commit_verify` field の field schema 明示がある。"""
    subsection = re.compile(r"^###\s+3\.4[^\n]*pre-commit verify", re.MULTILINE)
    assert subsection.search(doc_text), "§3.4 sub-section が無い"

    # field name 出現
    assert "pre_commit_verify:" in doc_text, "pre_commit_verify field name が doc 内に無い"

    required_subfields = [
        "staged_residual_zero_after_commit",
        "commits_atomic_count",
        "cross_agent_contamination_risk_check",
        "verify_command",
        "verify_evidence",
    ]
    missing = [name for name in required_subfields if name not in doc_text]
    assert not missing, (
        f"pre_commit_verify field schema sub-field から欠落: {missing} (= 規範 iv 未完)"
    )

    # field 義務化の明文 (= 「必須」 / 「義務」 keyword)
    obligation_kw = ("必須", "義務")
    assert any(k in doc_text for k in obligation_kw), (
        f"field 義務化 keyword ({obligation_kw}) が doc 内に無い (= 規範 iv の効力欠落)"
    )
