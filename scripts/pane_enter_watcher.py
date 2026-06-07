#!/usr/bin/env python3
"""Commander 自動 Enter watcher 本体 (副院長令 889ee02c [P1])

機能:
  - commander-third pane の入力欄 (最下部 prompt 行) を監視
  - 未送信テキストあり + STALE 秒変化なし → Enter 送出
  - 空欄: 打たない
  - 変化中: 打たない
  - 送出後: 内容変化まで再送しない (冪等)
  - 対象 pane 全滅: 自己終了

LIVE / DRY-RUN 切替:
  - env LIVE=1 で実 Enter 送出 (本番)
  - env LIVE 不在 or LIVE=0 で DRY-RUN (ログのみ、誤爆ゼロ実証)

設計: 副院長令 889ee02c 仕様準拠
監視対象: commander-third pane ただ1つ (将軍/家老/足軽は対象外)
"""
import argparse
import logging
import os
import re
import subprocess
import sys
import time
from typing import Optional

DEFAULT_STALE_SEC = 300  # 既定 5 分
DEFAULT_POLL_SEC = 10    # 10秒 poll
TARGET_PANE = "commander-third:0.0"
LOGFILE = "/tmp/pane_enter_watcher.log"


def setup_logger() -> logging.Logger:
    logger = logging.getLogger("pane_enter_watcher")
    logger.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    fh = logging.FileHandler(LOGFILE)
    fh.setFormatter(fmt)
    logger.addHandler(fh)
    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    logger.addHandler(sh)
    return logger


def pane_exists(target: str) -> bool:
    """対象 pane 存在判定 (= alive 確認)"""
    try:
        r = subprocess.run(
            ["tmux", "display-message", "-t", target, "-p", "#{pane_id}"],
            capture_output=True, text=True, timeout=5
        )
        return r.returncode == 0 and r.stdout.strip().startswith("%")
    except Exception:
        return False


def capture_pane_text(target: str) -> Optional[str]:
    """pane 全文 capture"""
    try:
        r = subprocess.run(
            ["tmux", "capture-pane", "-t", target, "-p"],
            capture_output=True, text=True, timeout=5
        )
        return r.stdout if r.returncode == 0 else None
    except Exception:
        return None


# 副院長令 863a8453 根治版 — 入力欄を ★枠線構造★ で厳密判定
# claude TUI 入力欄: 行頭が枠線 '│' (BOX DRAWINGS LIGHT VERTICAL) or '┃' (HEAVY VERTICAL)、
# その内側に '>' / '❯' / '›' から始まるテキストがある形式
# 本文出力 (echo/URGENT/引用 '> ') は行頭 '│' 枠なしで構造的除外
# 8/8 テスト PASS (副院長令 863a8453 明示)
BOX_PROMPT_LINE_RE = re.compile(r"^[│┃]\s*[>❯›]\s*(.*?)\s*[│┃]?\s*$")


def extract_prompt_input(pane_text: str) -> Optional[str]:
    """入力欄 (最下部 box prompt 行) の未送信テキスト抽出 (枠線構造厳密).

    判定:
      - 行頭が '│' or '┃' (= claude TUI 入力欄の枠) + 内側に '>' / '❯' / '›' → 入力欄
      - それ以外 (本文出力 echo / URGENT 表示 / 引用 '> ' / pure '> ') → 除外

    Returns:
        - 未送信テキスト (str): box 内に文字あり
        - None: box prompt 行未検出 (= 入力欄なし、別状態)
        - "": box 在るが空欄
    """
    if not pane_text:
        return None
    lines = pane_text.rstrip("\n").split("\n")
    # 最下部から逆走査、box prompt 行 (│ 枠 + > 内側) を探す
    for line in reversed(lines):
        stripped = line.rstrip()
        m = BOX_PROMPT_LINE_RE.match(stripped)
        if m:
            return m.group(1).rstrip()
    return None


def send_enter(target: str, dry_run: bool, logger: logging.Logger) -> bool:
    """Enter 送出 (LIVE / DRY-RUN 切替).

    Returns: True 成功 / False 失敗
    """
    if dry_run:
        logger.info("[DRY-RUN] Enter would be sent to %s", target)
        return True
    try:
        r = subprocess.run(
            ["tmux", "send-keys", "-t", target, "Enter"],
            capture_output=True, text=True, timeout=5
        )
        if r.returncode == 0:
            logger.info("[LIVE] Enter sent to %s", target)
            return True
        logger.warning("[LIVE] send-keys failed rc=%d stderr=%s", r.returncode, r.stderr)
        return False
    except Exception as e:
        logger.error("[LIVE] send-keys exception: %s", e)
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Commander auto-Enter watcher")
    parser.add_argument("--target", default=TARGET_PANE,
                        help=f"対象 pane (既定 {TARGET_PANE})")
    parser.add_argument("--stale-sec", type=int,
                        default=int(os.environ.get("STALE_SEC", DEFAULT_STALE_SEC)),
                        help=f"未送信テキスト stale 判定秒 (既定 {DEFAULT_STALE_SEC})")
    parser.add_argument("--poll-sec", type=int,
                        default=int(os.environ.get("POLL_SEC", DEFAULT_POLL_SEC)),
                        help=f"poll 間隔秒 (既定 {DEFAULT_POLL_SEC})")
    args = parser.parse_args()

    live = os.environ.get("LIVE", "0") == "1"
    logger = setup_logger()
    logger.info("=== pane_enter_watcher start ===")
    logger.info("  target=%s stale_sec=%d poll_sec=%d LIVE=%s",
                args.target, args.stale_sec, args.poll_sec, live)

    last_text: Optional[str] = None
    last_change_at: float = time.monotonic()
    sent_for_text: Optional[str] = None  # 送出済テキスト (冪等)

    while True:
        if not pane_exists(args.target):
            logger.info("target pane %s vanished, exit", args.target)
            return 0

        pane_text = capture_pane_text(args.target)
        prompt_input = extract_prompt_input(pane_text or "")

        now = time.monotonic()

        if prompt_input is None:
            # prompt 行未検出 — 出力中 or 別状態、reset
            last_text = None
            last_change_at = now
            sent_for_text = None
        elif prompt_input == "":
            # 空欄 — 打たない、reset
            if last_text != "":
                logger.debug("input empty, reset")
            last_text = ""
            last_change_at = now
            sent_for_text = None
        else:
            # 未送信テキストあり
            if prompt_input != last_text:
                # 変化中 — 打たない、stale 計時 reset
                last_text = prompt_input
                last_change_at = now
                sent_for_text = None
                logger.debug("input changed: %r", prompt_input[:60])
            else:
                # 変化なし — stale 経過判定
                elapsed = now - last_change_at
                if elapsed >= args.stale_sec and sent_for_text != prompt_input:
                    logger.info("STALE detected (elapsed=%.0fs, text=%r), sending Enter",
                                elapsed, prompt_input[:60])
                    if send_enter(args.target, dry_run=not live, logger=logger):
                        sent_for_text = prompt_input
                        # send-keys Enter 後の挙動: pane は新行へ遷移する想定、
                        # 次 cycle の capture-pane で入力欄空欄→reset 期待

        time.sleep(args.poll_sec)


if __name__ == "__main__":
    sys.exit(main())
