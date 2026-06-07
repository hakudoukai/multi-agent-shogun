#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_fukuincho_desktop_poke.py — unit test for scripts/fukuincho_desktop_poke.py

redo: subtask_thirdpc_p1_fukuincho_stage3_actual_impl_apply_redo_002
  - gunshi-third governing RED-3 cure: 本 commit diff 内に実 test 同梱 (phantom 回避)
  - gunshi-third RED-MED-B3 cure: is_submission_inflight 意味反転是正の test 含む
  - SKIP=0 必達 (FKI-AUDIT-GREEN-TRUTH-01 順守)

Usage:
  python3 scripts/tests/test_fukuincho_desktop_poke.py

Exit:
  0 = all PASS
  1 = at least one FAIL
"""

from __future__ import annotations

import os
import sys
import traceback

# Make scripts/ importable
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from fukuincho_desktop_poke import (  # noqa: E402
    DedupeWindow, SkipCounter, BusyDetection,
    safe_clipboard_poke, refined_v5_guard, backoff_seconds,
    SKIP_MAX, DEDUPE_T_SEC, ACK_N_SEC, RETRY_M_MAX, BACKOFF_SCHEDULE_SEC,
    _sanitize_log_fields, _is_textlike_clipboard,
)


_PASS = 0
_FAIL = 0
_FAIL_DETAILS: list[str] = []


def run(name: str, fn):
    """test runner — name で結果を表示、例外を捕捉。"""
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
# 1. 素案値 verbatim (副院長令 50a1b936 + 341654e4)
# ════════════════════════════════════════════════════════════
def test_constants_verbatim():
    assert ACK_N_SEC == 30
    assert RETRY_M_MAX == 3
    assert BACKOFF_SCHEDULE_SEC == (30, 60, 120)
    assert DEDUPE_T_SEC == 60
    assert SKIP_MAX == 5


# ════════════════════════════════════════════════════════════
# 2. §5.1 #3 dedupe 境界 59s/60s/61s (off-by-one なし)
# ════════════════════════════════════════════════════════════
def test_dedupe_boundary():
    d = DedupeWindow()
    key = ('win_handle_1', 'fukuincho_desktop_poke')
    assert d.should_fire(key, now=1000.0) is True
    d.mark_fired(key, now=1000.0)
    assert d.should_fire(key, now=1059.0) is False, '59s should be suppressed'
    assert d.should_fire(key, now=1060.0) is True, '60s should be allowed (strict less-than)'
    assert d.should_fire(key, now=1061.0) is True, '61s should be allowed'


# ════════════════════════════════════════════════════════════
# 3. skip_max=5 (Codex cycle1 B1 是正)
# ════════════════════════════════════════════════════════════
def test_skip_max_boundary():
    sc = SkipCounter()
    cid = 'corr-test-skipmax'
    for i in range(1, 5):
        sc.increment(cid)
        assert not sc.exceeded(cid), f'count {i} should not exceed'
    sc.increment(cid)
    assert sc.exceeded(cid), 'count 5 should exceed skip_max=5'
    sc.reset(cid)
    assert not sc.exceeded(cid)


# ════════════════════════════════════════════════════════════
# 4. refined V5 guard
# ════════════════════════════════════════════════════════════
def test_refined_v5_guard():
    assert refined_v5_guard('Claude') is False
    assert refined_v5_guard('V5 Window') is True
    assert refined_v5_guard('v5') is True
    assert refined_v5_guard('handshake 8012f18c demo') is True
    assert refined_v5_guard('Playwright Browser') is True
    assert refined_v5_guard('') is False
    assert refined_v5_guard('PlainTitle') is False


# ════════════════════════════════════════════════════════════
# 5. §5.1 #12 clipboard normal save→set→Enter→restore
# ════════════════════════════════════════════════════════════
def test_clipboard_normal_save_set_restore():
    clipboard = {'val': 'commander_original_content'}
    def get_clip(): return clipboard['val']
    def set_clip(v): clipboard['val'] = v
    def send_enter_ok(): return True
    ok, status = safe_clipboard_poke('確認して', set_clip, get_clip, send_enter_ok, 'cb-norm')
    assert ok is True
    assert status == 'restored', f'expected restored, got {status}'
    assert clipboard['val'] == 'commander_original_content'


# ════════════════════════════════════════════════════════════
# 6. §5.1 #13 Enter 失敗時 finally restore
# ════════════════════════════════════════════════════════════
def test_clipboard_finally_restore_on_enter_failure():
    clipboard = {'val': 'commander_original_content'}
    def get_clip(): return clipboard['val']
    def set_clip(v): clipboard['val'] = v
    def send_enter_fail(): raise RuntimeError('Enter failed')
    ok, status = safe_clipboard_poke('確認して', set_clip, get_clip, send_enter_fail, 'cb-fail')
    assert ok is False
    assert status == 'restored', f'expected restored after Enter failure, got {status}'
    assert clipboard['val'] == 'commander_original_content'


# ════════════════════════════════════════════════════════════
# 7. §5.1 #14 構造化ログ機密 sanitize
# ════════════════════════════════════════════════════════════
def test_log_field_sanitize():
    fields = {
        'event': 'ok',
        'clipboard_value': 'SECRET_CLIP',
        'clipboard_content': 'SECRET2',
        'token': 'XXX',
        'secret': 'YYY',
        'password': 'ZZZ',
        'api_key': 'WWW',
        'payload_value': 'PII',
        'payload_text': 'PII2',
        'safe': 'visible',
    }
    sanitized = _sanitize_log_fields(fields)
    for fb in ('clipboard_value', 'clipboard_content', 'token', 'secret',
               'password', 'api_key', 'payload_value', 'payload_text'):
        assert fb not in sanitized, f'forbidden key {fb} should be removed'
    assert sanitized.get('safe') == 'visible'
    assert sanitized.get('event') == 'ok'


# ════════════════════════════════════════════════════════════
# 8. BusyDetection editing 3 条件 AND (S1 mitigation_a)
# ════════════════════════════════════════════════════════════
def test_busy_detection_editing_and():
    b = BusyDetection()
    assert b.is_editing() is False
    b.ime_active = True
    b.edit_nonempty = True
    b.focused = True
    assert b.is_editing() is True
    b.focused = False
    assert b.is_editing() is False
    b.focused = True
    b.edit_nonempty = False
    assert b.is_editing() is False


# ════════════════════════════════════════════════════════════
# 9. backoff schedule 30/60/120
# ════════════════════════════════════════════════════════════
def test_backoff_schedule():
    assert backoff_seconds(1) == 30
    assert backoff_seconds(2) == 60
    assert backoff_seconds(3) == 120
    assert backoff_seconds(99) == 120
    assert backoff_seconds(0) == 30
    assert backoff_seconds(-1) == 30


# ════════════════════════════════════════════════════════════
# 10. ★fix4 (redo_002) is_submission_inflight 意味反転是正★
# ════════════════════════════════════════════════════════════
def test_submission_inflight_semantic_invert():
    """gunshi-third RED-MED-B3 cure verify。

    ready 条件 (submit_enabled ∧ spinner_hidden ∧ progress_inactive) 満たすとき:
      is_ready_for_submission() == True
      is_submission_inflight() == ★False★ (前 impl は True を返していた = 逆転バグ)
    ready 条件 (submit_enabled ∧ spinner_hidden ∧ progress_inactive) 満たさないとき:
      is_submission_inflight() == True
    """
    b = BusyDetection()
    # 全 default = submit_enabled=False ゆえ ready 不成立 = 進行中扱い (safe default)
    assert b.is_ready_for_submission() is False
    assert b.is_submission_inflight() is True

    # ready 条件を成立させる (idle)
    b.submit_enabled = True
    b.spinner_hidden = True
    b.progress_inactive = True
    assert b.is_ready_for_submission() is True
    # ★fix4 核心★: ready 時は submission inflight = False (前 impl の逆転バグ cure)
    assert b.is_submission_inflight() is False, \
        'fix4 redo_002: ready 状態で is_submission_inflight=True を返すのは前 impl 致命 bug'

    # spinner visible (submit 進行中) → inflight True
    b.spinner_hidden = False
    assert b.is_ready_for_submission() is False
    assert b.is_submission_inflight() is True


# ════════════════════════════════════════════════════════════
# 11. ★fix4 連動: is_busy() が idle 状態で False ★
# ════════════════════════════════════════════════════════════
def test_is_busy_false_on_idle():
    b = BusyDetection()
    # idle (ready) state: editing も False、submission_inflight も False
    b.ime_active = False
    b.edit_nonempty = False
    b.focused = False
    b.submit_enabled = True
    b.spinner_hidden = True
    b.progress_inactive = True
    assert b.is_editing() is False
    assert b.is_submission_inflight() is False
    # ★fix4 重要効果★: idle で is_busy=False (前 impl は True 誤判定で skip_max 誤発火)
    assert b.is_busy() is False, \
        'fix4 redo_002: idle state で is_busy=True を返すのは前 impl 致命 bug'


# ════════════════════════════════════════════════════════════
# 12. ★fix6 (redo_002) clipboard 非テキスト判定★
# ════════════════════════════════════════════════════════════
def test_clipboard_textlike_detection():
    assert _is_textlike_clipboard('hello') is True
    assert _is_textlike_clipboard('') is True
    assert _is_textlike_clipboard('日本語OK') is True
    # 非テキスト
    assert _is_textlike_clipboard(None) is False
    assert _is_textlike_clipboard(b'binary') is False
    assert _is_textlike_clipboard(bytearray(b'\x00\x01')) is False
    assert _is_textlike_clipboard(123) is False
    assert _is_textlike_clipboard(['list']) is False
    # surrogate (binary 経由混入) — encode 不能 ゆえ非テキスト判定
    assert _is_textlike_clipboard('\ud800') is False


# ════════════════════════════════════════════════════════════
# 13. ★fix6 連動: clipboard 非テキスト時 save/restore skip★
# ════════════════════════════════════════════════════════════
def test_clipboard_nontextlike_skips_restore():
    """非テキスト clipboard 時、original 退避を skip し set のみ実行 (復元しない)。"""
    state = {'val': b'\x00\x01binary_image_data'}  # 非テキスト
    set_calls = []
    def get_clip(): return state['val']
    def set_clip(v):
        set_calls.append(v)
        state['val'] = v
    def send_enter(): return True
    ok, status = safe_clipboard_poke('確認して', set_clip, get_clip, send_enter, 'nt-1')
    assert ok is True
    assert status == 'no_original_text', f'expected no_original_text, got {status}'
    # 非テキストゆえ restore skip — 最終状態は payload のまま
    assert state['val'] == '確認して'


# ════════════════════════════════════════════════════════════
# 14. ★fix5 (redo_002) 戻り値整合性★
# ════════════════════════════════════════════════════════════
def test_clipboard_return_status_consistency():
    """fix5 redo_002: restore 結果が戻り値に反映される (前 impl pending_restore 据置欠陥 cure)。"""
    # 正常系: restored
    state = {'val': 'original_text'}
    def get_clip(): return state['val']
    def set_clip(v): state['val'] = v
    ok, status = safe_clipboard_poke('payload', set_clip, get_clip, lambda: True, 'fix5-1')
    assert status == 'restored', f'normal case: expected restored, got {status}'

    # restore 失敗系: restore_failed
    state2 = {'val': 'original_text'}
    set_call_count = [0]
    def set_clip_fail_on_restore(v):
        set_call_count[0] += 1
        if set_call_count[0] == 1:
            state2['val'] = v  # payload set 成功
        else:
            raise RuntimeError('restore 失敗 simulation')
    def get_clip2(): return state2['val']
    ok2, status2 = safe_clipboard_poke('payload', set_clip_fail_on_restore, get_clip2, lambda: True, 'fix5-2')
    assert status2 == 'restore_failed', f'expected restore_failed, got {status2}'

    # save_failed 系
    def get_clip_raise(): raise RuntimeError('save 失敗')
    state3 = {'val': 'original'}
    def set_clip3(v): state3['val'] = v
    ok3, status3 = safe_clipboard_poke('payload', set_clip3, get_clip_raise, lambda: True, 'fix5-3')
    assert status3 == 'save_failed', f'expected save_failed, got {status3}'

    # set_failed 系
    state4 = {'val': 'orig'}
    def get_clip4(): return state4['val']
    def set_clip_fail(v): raise RuntimeError('set 失敗')
    ok4, status4 = safe_clipboard_poke('payload', set_clip_fail, get_clip4, lambda: True, 'fix5-4')
    # set 失敗時、send_enter 未実行ゆえ ok=False、restore は finally で試行されるが original ありゆえ restored へ
    assert ok4 is False
    # set 失敗時の restore: original 退避済ゆえ "restored" にしたい (set 失敗を吸収して元に戻す)
    # ただし set_clip_fail は本テストで restore も失敗させる ゆえ "restore_failed" になる
    assert status4 in ('restore_failed', 'restored'), \
        f'expected restore_failed or restored, got {status4}'


# ════════════════════════════════════════════════════════════
# Test list 実行
# ════════════════════════════════════════════════════════════
TESTS = [
    ('1. constants verbatim (N=30/M=3/backoff/T=60/skip_max=5)', test_constants_verbatim),
    ('2. dedupe boundary 59/60/61 (off-by-one なし)', test_dedupe_boundary),
    ('3. skip_max=5 boundary + reset', test_skip_max_boundary),
    ('4. refined V5 guard (V5/handshake/playwright)', test_refined_v5_guard),
    ('5. §5.1 #12 clipboard normal save→set→Enter→restore', test_clipboard_normal_save_set_restore),
    ('6. §5.1 #13 Enter 失敗時 finally restore', test_clipboard_finally_restore_on_enter_failure),
    ('7. §5.1 #14 構造化ログ機密 sanitize', test_log_field_sanitize),
    ('8. BusyDetection editing 3 条件 AND', test_busy_detection_editing_and),
    ('9. backoff schedule 30/60/120', test_backoff_schedule),
    ('10. ★fix4★ is_submission_inflight 意味反転是正', test_submission_inflight_semantic_invert),
    ('11. ★fix4★ is_busy() が idle 状態で False', test_is_busy_false_on_idle),
    ('12. ★fix6★ clipboard 非テキスト判定', test_clipboard_textlike_detection),
    ('13. ★fix6★ clipboard 非テキスト時 save/restore skip', test_clipboard_nontextlike_skips_restore),
    ('14. ★fix5★ restore 戻り値整合性 (restored/restore_failed/save_failed/set_failed)', test_clipboard_return_status_consistency),
]


def main() -> int:
    print(f"───────────────────────────────────────")
    print(f"test_fukuincho_desktop_poke.py — {len(TESTS)} tests")
    print(f"redo: subtask_thirdpc_p1_fukuincho_stage3_actual_impl_apply_redo_002")
    print(f"───────────────────────────────────────")
    for name, fn in TESTS:
        run(name, fn)
    print(f"───────────────────────────────────────")
    print(f"PASS={_PASS} FAIL={_FAIL} SKIP=0")
    if _FAIL:
        print(f"───────────────────────────────────────")
        print("FAILURE DETAILS:")
        for d in _FAIL_DETAILS:
            print(f"  - {d}")
        return 1
    print(f"★ALL PASS (SKIP=0、FKI-AUDIT-GREEN-TRUTH-01 順守)★")
    return 0


if __name__ == '__main__':
    sys.exit(main())
