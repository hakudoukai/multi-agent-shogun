#!/usr/bin/env python3
"""L1-L5 escalation engine + ntfy notification + auto-answer for choice patterns.

Usage:
  # Classify a message and take action
  python3 hakudokai_escalation.py classify --message "どちらにしますか？1.A 2.B"

  # Send ntfy notification
  python3 hakudokai_escalation.py notify --level L3 --summary "新規cmd起票"

  # Wait for L4 approval from Supabase
  python3 hakudokai_escalation.py wait-approval --topic "schema_change_xyz" --timeout 1800

  # Auto-answer a choice-offering pattern
  python3 hakudokai_escalation.py auto-answer --message "1.A 2.B 3.C" --context "file refactoring"
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
CLINIC_ID = os.environ.get("HAKUDOKAI_CLINIC_ID", "hakudoukai_main")

# --- Escalation Level Definitions ---

L3B_KEYWORDS = [
    "新規cmd", "新規タスク", "instruction変更", "schema変更", "テーブル作成",
    "設計変更", "アーキテクチャ", "セキュリティ", "permission", "migration",
    "RED判定", "品質NG",
]

L4_KEYWORDS = [
    "課金", "契約", "API費用", "料金", "支払", "patient", "患者",
    "PII", "個人情報", "医療記録", "PayLight", "予約システム",
    "force push", "ブランチ削除", "agent追加", "agent削除",
    "CLAUDE.md変更", "規律変更", "7医院", "multi-clinic",
]

L5_KEYWORDS = [
    "セキュリティインシデント", "データ漏洩", "RLS bypass", "unauthorized",
    "暴走", "無限ループ", "urgent_stop",
]

CHOICE_PATTERNS = [
    r"(?:どちら|どれ|どの)(?:に|を|が)(?:しますか|良い|いい|する)",
    r"(?:1\.|①|A\))\s*.+(?:2\.|②|B\))\s*.+",
    r"(?:option|approach|方法|パターン|案)\s*[1-3ABCabc]",
    r"(?:以下|次)の(?:選択肢|オプション|方法).*(?:選|教えて)",
    r"(?:shall I|should I|would you|do you want|which)",
]

AUTO_ANSWER_RULES = {
    "refactor": "シンプルな方で進めろ。",
    "rename": "承認。実行せよ。",
    "test": "承認。テスト追加/修正して進めろ。",
    "file_create": "タスクスコープ内であれば承認。実行せよ。",
    "file_delete": "タスクスコープ内であれば承認。実行せよ。",
    "approach": "最もシンプルで実績のある方法を選択し、即実行せよ。",
    "default": "最善と判断する方を選び、即実行せよ。判断理由を報告に含めよ。",
}


def get_env():
    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    if not url or not key:
        env_file = os.path.expanduser("~/.openclaw/env")
        if os.path.exists(env_file):
            with open(env_file) as f:
                for line in f:
                    line = line.strip().replace("\r", "")
                    if line.startswith("SUPABASE_URL="):
                        url = line.split("=", 1)[1]
                    elif line.startswith("SUPABASE_SERVICE_ROLE_KEY="):
                        key = line.split("=", 1)[1]
    return url, key


def get_ntfy_config():
    """Load ntfy configuration from config/ntfy_auth.env or environment."""
    ntfy_url = os.environ.get("NTFY_URL", "")
    ntfy_topic = os.environ.get("NTFY_TOPIC", "")
    if not ntfy_url:
        env_file = os.path.join(PROJECT_ROOT, "config", "ntfy_auth.env")
        if os.path.exists(env_file):
            with open(env_file) as f:
                for line in f:
                    line = line.strip().replace("\r", "")
                    if line.startswith("NTFY_URL="):
                        ntfy_url = line.split("=", 1)[1]
                    elif line.startswith("NTFY_TOPIC="):
                        ntfy_topic = line.split("=", 1)[1]
    if not ntfy_url:
        ntfy_url = "https://ntfy.sh"
    if not ntfy_topic:
        ntfy_topic = "hakudokai-shogun"
    return ntfy_url, ntfy_topic


# --- Classification ---

def classify_message(message):
    """Classify a message into L1-L5 escalation level."""
    msg_lower = message.lower()

    # L5: Emergency keywords
    for kw in L5_KEYWORDS:
        if kw.lower() in msg_lower:
            return "L5", f"Emergency keyword detected: {kw}"

    # L4: Human approval required
    for kw in L4_KEYWORDS:
        if kw.lower() in msg_lower:
            return "L4", f"Approval-required keyword: {kw}"

    # Choice pattern detection → L1 auto-answer
    for pattern in CHOICE_PATTERNS:
        if re.search(pattern, message, re.IGNORECASE):
            return "L1_CHOICE", "Choice-offering pattern detected"

    # L3b: Important operational decisions
    for kw in L3B_KEYWORDS:
        if kw.lower() in msg_lower:
            return "L3b", f"Important decision keyword: {kw}"

    # L3a: Standard notifications
    if any(kw in msg_lower for kw in ["完了", "報告", "done", "green", "yellow"]):
        return "L3a", "Standard report/notification"

    # L2: Routine operations
    if any(kw in msg_lower for kw in ["ack", "heartbeat", "health", "status"]):
        return "L2", "Routine operation"

    # Default: L2
    return "L2", "No specific keywords matched"


# --- Notification ---

def send_ntfy(level, summary, details=""):
    """Send push notification via ntfy.sh."""
    ntfy_url, ntfy_topic = get_ntfy_config()
    url = f"{ntfy_url}/{ntfy_topic}"

    priority_map = {
        "L1": "1", "L1_CHOICE": "1",
        "L2": "2",
        "L3a": "3", "L3b": "3",
        "L4": "4",
        "L5": "5",
    }

    title_map = {
        "L1": "副医院長: 自動処理",
        "L2": "副医院長: 事後報告",
        "L3a": "副医院長: 通知",
        "L3b": "副医院長: デコポン協議済み",
        "L4": "副医院長: 承認要求",
        "L5": "副医院長: 緊急停止",
    }

    body = f"[{level}] {summary}"
    if details:
        body += f"\n{details[:300]}"

    try:
        data = body.encode("utf-8")
        req = urllib.request.Request(url, data=data, method="POST")
        req.add_header("Title", title_map.get(level, f"副医院長: {level}"))
        req.add_header("Priority", priority_map.get(level, "3"))
        if level in ("L4", "L5"):
            req.add_header("Tags", "warning")
        urllib.request.urlopen(req, timeout=10)
        print(f"ntfy sent: [{level}] {summary}", file=sys.stderr)
        return True
    except Exception as e:
        print(f"ntfy failed: {e}", file=sys.stderr)
        return False


# --- L4 Approval Wait ---

def wait_for_approval(topic, timeout=1800):
    """Wait for L4 approval via Supabase pc_handshake response."""
    url, key = get_env()
    if not url or not key:
        print("ERROR: Supabase credentials required for approval wait", file=sys.stderr)
        return "timeout"

    start = time.time()
    poll_interval = 15
    reminder_interval = 300  # Re-notify every 5 minutes
    last_reminder = start

    print(f"Waiting for approval on topic '{topic}' (timeout={timeout}s)...", file=sys.stderr)

    while time.time() - start < timeout:
        # Check for response
        query = (
            f"{url}/rest/v1/pc_handshake"
            f"?from_pc=eq.fukuincho&topic=like.*{topic}*"
            f"&message_type=in.(grant_permission,decline_permission)"
            f"&order=created_at.desc&limit=1"
        )
        try:
            req = urllib.request.Request(query)
            req.add_header("Authorization", f"Bearer {key}")
            req.add_header("apikey", key)
            resp = urllib.request.urlopen(req, timeout=10)
            data = json.loads(resp.read().decode())
            if data:
                msg_type = data[0].get("message_type", "")
                if msg_type == "grant_permission":
                    print(f"APPROVED: {data[0].get('content', '')[:200]}", file=sys.stderr)
                    return "approved"
                elif msg_type == "decline_permission":
                    print(f"REJECTED: {data[0].get('content', '')[:200]}", file=sys.stderr)
                    return "rejected"
        except Exception as e:
            print(f"Approval check error: {e}", file=sys.stderr)

        # Re-notify every 5 minutes
        if time.time() - last_reminder >= reminder_interval:
            send_ntfy("L4", f"承認待ち継続中: {topic}",
                      f"経過{int((time.time()-start)/60)}分。Supabaseで approved/rejected を返してください。")
            last_reminder = time.time()

        time.sleep(poll_interval)

    print(f"TIMEOUT: No approval received in {timeout}s", file=sys.stderr)
    return "timeout"


# --- Auto-Answer ---

def auto_answer(message, context=""):
    """Generate an auto-answer for choice-offering patterns."""
    msg_lower = (message + " " + context).lower()

    for key, answer in AUTO_ANSWER_RULES.items():
        if key == "default":
            continue
        if key in msg_lower:
            return answer

    return AUTO_ANSWER_RULES["default"]


# --- Codex Consultation (L3b) ---

def consult_codex(decision_summary, context=""):
    """Dispatch to Codex for L3b consultation."""
    prompt = f"""You are an independent technical reviewer (Codex/dekopon).
The AI副医院長 wants to make the following decision:

Decision: {decision_summary}
Context: {context}

Evaluate:
1. Is this decision sound? (yes/minor_concern/major_concern)
2. Any risks or better alternatives?
3. Should this be escalated to the human 理事長 (L4)?

Reply in this exact format:
SEVERITY: [no_concern|minor_concern|major_concern]
SUGGESTIONS: [your suggestions]
ESCALATE: [yes|no]
"""
    output_file = f"/tmp/hakudokai_codex_consult_{int(time.time())}.txt"
    try:
        result = subprocess.run(
            ["npx", "@openai/codex", "exec", "--ephemeral",
             "-o", output_file, prompt],
            capture_output=True, timeout=300, cwd=PROJECT_ROOT
        )
        if os.path.exists(output_file):
            with open(output_file) as f:
                response = f.read()
            os.unlink(output_file)

            severity = "no_concern"
            escalate = False
            if "major_concern" in response.lower():
                severity = "major_concern"
            elif "minor_concern" in response.lower():
                severity = "minor_concern"
            if "ESCALATE: yes" in response:
                escalate = True

            return {
                "severity": severity,
                "escalate": escalate,
                "response": response[:500],
            }
    except Exception as e:
        print(f"Codex consultation failed: {e}", file=sys.stderr)

    return {"severity": "unknown", "escalate": False, "response": "Consultation failed"}


# --- Main ---

def main():
    parser = argparse.ArgumentParser(description="L1-L5 Escalation Engine")
    parser.add_argument("action", choices=[
        "classify", "notify", "wait-approval", "auto-answer", "consult-codex"
    ])
    parser.add_argument("--message", default="")
    parser.add_argument("--level", default="")
    parser.add_argument("--summary", default="")
    parser.add_argument("--details", default="")
    parser.add_argument("--topic", default="")
    parser.add_argument("--context", default="")
    parser.add_argument("--timeout", type=int, default=1800)
    args = parser.parse_args()

    if args.action == "classify":
        level, reason = classify_message(args.message)
        print(json.dumps({"level": level, "reason": reason}))

    elif args.action == "notify":
        level = args.level or "L3a"
        send_ntfy(level, args.summary, args.details)

    elif args.action == "wait-approval":
        if not args.topic:
            print("ERROR: --topic required", file=sys.stderr)
            sys.exit(1)
        result = wait_for_approval(args.topic, args.timeout)
        print(json.dumps({"result": result}))

    elif args.action == "auto-answer":
        answer = auto_answer(args.message, args.context)
        print(json.dumps({"answer": answer}))

    elif args.action == "consult-codex":
        result = consult_codex(args.summary or args.message, args.context)
        print(json.dumps(result))


if __name__ == "__main__":
    main()
