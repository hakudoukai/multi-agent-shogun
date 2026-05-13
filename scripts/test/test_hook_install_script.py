"""Tests for scripts/install_pre_commit_hook.sh — presence, chmod, idempotent install.

Scope (= task YAML AC2):
- ashigaru2 自身は script + 設計 evidence のみ verify。
- live all-pane install verify (= 全 ashigaru pane で .git/hooks/pre-commit が active 化したか) は
  karo/infra scope で別実行、本 task の完遂 blocker ではない。

Refs:
- scripts/install_pre_commit_hook.sh
- queue/tasks/subtask_cmd020_scope_contamination_prevention_v2.yaml AC2 / step_2
"""
from __future__ import annotations

import os
import shutil
import stat
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
INSTALL_SCRIPT = REPO_ROOT / "scripts" / "install_pre_commit_hook.sh"


def _git(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True
    )


def test_install_script_present_and_executable() -> None:
    assert INSTALL_SCRIPT.is_file(), f"missing {INSTALL_SCRIPT}"
    mode = INSTALL_SCRIPT.stat().st_mode
    assert mode & stat.S_IXUSR, (
        f"install_pre_commit_hook.sh is not user-executable (mode={oct(mode)})"
    )


def test_install_script_has_required_sections() -> None:
    body = INSTALL_SCRIPT.read_text(encoding="utf-8")
    # shebang + idempotent overwrite + chmod + dry-run + framework option
    assert body.startswith("#!/usr/bin/env bash")
    assert "chmod +x" in body, "missing chmod +x (= hook must be executable after install)"
    assert "--dry-run" in body, "missing --dry-run option"
    assert "--with-framework" in body, "missing --with-framework option"
    assert "check_file_path_owner.sh" in body, (
        "shim must invoke scripts/lint/check_file_path_owner.sh"
    )
    assert "pre_commit_author_verify.sh" in body, (
        "shim must invoke scripts/pre_commit_author_verify.sh (= author drift defense)"
    )


def test_install_writes_executable_hook_in_temp_repo(tmp_path: Path) -> None:
    repo = tmp_path / "r"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.name", "install-test")
    _git(repo, "config", "user.email", "i@example.local")
    # Run installer with cwd=repo to target this temp repo's .git/hooks
    result = subprocess.run(
        ["bash", str(INSTALL_SCRIPT)],
        cwd=repo,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"installer failed: {result.stderr}"
    hook_path = repo / ".git" / "hooks" / "pre-commit"
    assert hook_path.is_file(), "hook was not written"
    mode = hook_path.stat().st_mode
    assert mode & stat.S_IXUSR, f"hook is not executable (mode={oct(mode)})"
    content = hook_path.read_text(encoding="utf-8")
    assert "Auto-generated" in content
    assert "check_file_path_owner.sh" in content


def test_install_is_idempotent(tmp_path: Path) -> None:
    repo = tmp_path / "r"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.name", "install-test")
    _git(repo, "config", "user.email", "i@example.local")
    # First install
    first = subprocess.run(
        ["bash", str(INSTALL_SCRIPT)], cwd=repo, capture_output=True, text=True
    )
    assert first.returncode == 0
    hook_path = repo / ".git" / "hooks" / "pre-commit"
    content_1 = hook_path.read_text(encoding="utf-8")
    # Second install (= idempotent overwrite)
    second = subprocess.run(
        ["bash", str(INSTALL_SCRIPT)], cwd=repo, capture_output=True, text=True
    )
    assert second.returncode == 0
    content_2 = hook_path.read_text(encoding="utf-8")
    assert content_1 == content_2, "idempotent install produced different content"


def test_install_with_framework_includes_delegation(tmp_path: Path) -> None:
    repo = tmp_path / "r"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.name", "install-test")
    _git(repo, "config", "user.email", "i@example.local")
    result = subprocess.run(
        ["bash", str(INSTALL_SCRIPT), "--with-framework"],
        cwd=repo,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    content = (repo / ".git" / "hooks" / "pre-commit").read_text(encoding="utf-8")
    assert "pre-commit run" in content, (
        "--with-framework should embed pre-commit framework delegation"
    )


def test_install_dry_run_does_not_write(tmp_path: Path) -> None:
    repo = tmp_path / "r"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.name", "install-test")
    _git(repo, "config", "user.email", "i@example.local")
    hook_path = repo / ".git" / "hooks" / "pre-commit"
    assert not hook_path.exists()
    result = subprocess.run(
        ["bash", str(INSTALL_SCRIPT), "--dry-run"],
        cwd=repo,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "DRY RUN" in result.stdout
    assert not hook_path.exists(), "dry-run should not write the hook file"
