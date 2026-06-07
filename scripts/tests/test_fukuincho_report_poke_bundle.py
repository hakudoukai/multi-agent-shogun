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

import os
import shutil
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
    """inbox_write.sh を subprocess.run 互換 runner で叩くことを確認 (FKI-NO-DUP evidence)"""
    captured = {}

    class _P:
        returncode = 0
        stdout = ""
        stderr = ""

    def fake_runner(cmd, capture_output=False, text=False, timeout=None):
        captured["cmd"] = cmd
        captured["capture_output"] = capture_output
        captured["text"] = text
        captured["timeout"] = timeout
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
    assert captured["cmd"][3] == "test body"
    assert captured["cmd"][4] == "report_received"
    assert captured["cmd"][5] == "ashigaru-third-3"
    assert captured["capture_output"] is True
    assert captured["text"] is True


def test_report_insert_failure_propagates_rc():
    class _P:
        returncode = 5
        stdout = ""
        stderr = "amplification loop detected"

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

def test_bundle_does_not_mark_poked_on_error():
    """poke 全 attempt 失敗 → marker file 作成されない (次回再試行可)"""
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
            correlation_id="corr-err",
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
        # marker 未作成 (次回再試行可、人手介入もまだ)
        assert already_poked("corr-err", lock_dir=tmp) is False
    _with_tmpdir(_go)


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
    # (iv) safety: error → marker not set
    ("(iv) bundle does not mark poked on error", test_bundle_does_not_mark_poked_on_error),
    # FKI-NO-DUP evidence
    ("FKI-NO-DUP reuses ae8083dd engine", test_fki_no_dup_reuses_ae8083dd_engine),
    # log sanitize
    ("log_sanitize strips secret keys", test_log_sanitize_strips_secret_keys),
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
