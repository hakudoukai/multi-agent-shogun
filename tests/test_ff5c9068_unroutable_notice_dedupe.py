#!/usr/bin/env python3
"""ff5c9068 — second receiver の unroutable 通知は ★同 handshake id につき一度★。

受入 (本部長・逐語):
  ⑴ 同 source_id 二走査 = 通知 1
  ⑵ 別 row 通知あり
  ⑶ 撥ね返し保持

之まで:
  - escalate_unroutable の docstring は "once per handshake id" と名乗り乍ら
    函の内に dedupe が ★無く★、一度性は呼手の processed_file に頼つて居た
    (argv[2] にて外から渡る = 別 path を渡さるれば通知は再び出る)。
  - POST が投げれば except が呑み log 一行のみ、然るに ★同じ枝が processed_file
    へ書く★ ゆゑ 通知は永久に出でず row は処理済に成つた (静かな失敗)。
"""
import json, os, sys, tempfile, pathlib
from unittest.mock import patch, MagicMock

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.join(HERE, "..")
MODULE = os.path.join(REPO, "shim", "hakudokai", "hakudokai_secondpc_receiver_poll.py")


def _unroutable_row(msg_id):
    """A row with no resolvable target: no context_data, no cross_pc_inbox topic."""
    return {
        "id": msg_id,
        "from_pc": "main_pc",
        "to_pc": "second_pc",
        "message_type": "status_update",
        "topic": "some_topic_without_target",
        "content": "no structured target here",
    }


def _run(rows, workdir, processed_name="processed.txt", urlopen_fails=False):
    """Exec the receiver against `rows`; return (processed_ids, notified_ids, post_count)."""
    resp = os.path.join(workdir, "resp.json")
    with open(resp, "w", encoding="utf-8") as f:
        json.dump(rows, f)

    processed_file = os.path.join(workdir, processed_name)
    if not os.path.exists(processed_file):
        open(processed_file, "w").close()

    notified_file = os.path.join(workdir, "_unroutable_notified.txt")
    retry_file = os.path.join(workdir, "retry.json")

    posts = []

    def _fake_urlopen(req, *a, **kw):
        posts.append(req)
        if urlopen_fails:
            raise OSError("HTTP 500 (simulated)")
        m = MagicMock()
        m.__enter__ = MagicMock(return_value=m)
        m.__exit__ = MagicMock(return_value=False)
        return m

    env = {
        "SECONDPC_RECEIVER_UNROUTABLE_NOTIFIED_FILE": notified_file,
        "SECONDPC_RECEIVER_RETRY_TRACKER_FILE": retry_file,
        "SUPABASE_SERVICE_ROLE_KEY": "fake_key",
    }
    argv = ["test", resp, processed_file, workdir, "http://localhost:54321/rest/v1"]

    with patch.dict(os.environ, env), patch("sys.argv", argv), \
            patch("urllib.request.urlopen", side_effect=_fake_urlopen):
        source = open(MODULE, encoding="utf-8").read()
        try:
            exec(compile(source, MODULE, "exec"), {"__name__": "__test__"})
        except SystemExit:
            pass

    processed = set()
    if os.path.exists(processed_file):
        processed = {l.strip() for l in open(processed_file, encoding="utf-8") if l.strip()}
    notified = set()
    if os.path.exists(notified_file):
        notified = {l.strip() for l in open(notified_file, encoding="utf-8") if l.strip()}
    return processed, notified, len(posts)


def test_same_source_id_twice_notifies_once():
    """受入⑴: 同 source_id 二走査 = 通知 1。★processed_file を空に戻しても★ 一度。"""
    with tempfile.TemporaryDirectory() as d:
        row = [_unroutable_row("hs-aaaa-1111")]

        _, notified1, posts1 = _run(row, d)
        assert posts1 == 1, f"first scan should notify once, got {posts1}"
        assert "hs-aaaa-1111" in notified1

        # 二走査目 ―― ★呼手の processed_file を空にして★ 走らせる。
        # 一度性が processed_file に寄り掛かつて居れば 此処で二度目が飛ぶ。
        open(os.path.join(d, "processed.txt"), "w").close()
        _, notified2, posts2 = _run(row, d)
        assert posts2 == 0, f"second scan must NOT re-notify, got {posts2}"
        assert notified2 == {"hs-aaaa-1111"}


def test_a_different_row_still_notifies():
    """受入⑵: 別 row には通知が出る (dedupe が広く効き過ぎて居らぬ事)。"""
    with tempfile.TemporaryDirectory() as d:
        _, _, posts1 = _run([_unroutable_row("hs-aaaa-1111")], d)
        assert posts1 == 1
        _, notified, posts2 = _run([_unroutable_row("hs-bbbb-2222")], d)
        assert posts2 == 1, f"a different handshake id must notify, got {posts2}"
        assert notified == {"hs-aaaa-1111", "hs-bbbb-2222"}


def test_failed_notice_keeps_the_bounce():
    """受入⑶: 通知が倒れたる時 ―― row を処理済に埋めず・通知済にも記さぬ。"""
    with tempfile.TemporaryDirectory() as d:
        row = [_unroutable_row("hs-cccc-3333")]
        processed, notified, posts = _run(row, d, urlopen_fails=True)
        assert posts == 1, "it must have tried"
        assert notified == set(), "a failed POST must NOT be recorded as notified"
        assert "hs-cccc-3333" not in processed, \
            "a row whose notice failed must NOT be buried as processed"


def test_failed_then_recovered_notice_lands_exactly_once():
    """倒れたる後に立ち直れば ―― 通知は出で、而して ★一度だけ★。"""
    with tempfile.TemporaryDirectory() as d:
        row = [_unroutable_row("hs-dddd-4444")]
        _run(row, d, urlopen_fails=True)
        processed, notified, posts = _run(row, d)
        assert posts == 1
        assert notified == {"hs-dddd-4444"}
        assert "hs-dddd-4444" in processed
        _, notified3, posts3 = _run(row, d)
        assert posts3 == 0, "after recovery it must not notify again"
        assert notified3 == {"hs-dddd-4444"}
