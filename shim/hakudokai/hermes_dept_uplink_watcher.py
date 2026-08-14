#!/usr/bin/env python3
from __future__ import annotations

import json
import fcntl
import os
import pathlib
import shutil
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

BASE = pathlib.Path(os.environ.get("HERMES_DEPT_BASE", "/home/hakudoukai/hermes-departments"))
OUTBOX = BASE / "state" / "upstream_outbox"
PENDING = OUTBOX / "pending"
SENT = OUTBOX / "sent"
DEAD = OUTBOX / "deadletter"

# 2026-08-09 委員長: 上申先を可変化。送信器 hermes-dept-upstream-send と★同じ環境変数・同じ既定★。
# 由来=実測: 送信側だけを iincho へ変え、受け側が fukuincho 固定のままだったため全便が deadletter へ落ちた。
# ★両端を1つのsourceで揃える★。戻し方= HERMES_DEPT_UPSTREAM_TARGET=fukuincho（1語）。
UPSTREAM_TARGET = os.environ.get('HERMES_DEPT_UPSTREAM_TARGET', 'iincho')
# 移行中は旧宛先も受理する（既に pending に居る旧封筒を落とさないため）。
ACCEPTED_TARGETS = {UPSTREAM_TARGET, 'fukuincho'}
RECEIPTS = OUTBOX / "receipts"
ALERTS = OUTBOX / "alerts"
INTERVAL = int(os.environ.get("HERMES_DEPT_UPLINK_INTERVAL", "5"))
MAX_ATTEMPTS = int(os.environ.get("HERMES_DEPT_UPLINK_MAX_ATTEMPTS", "5"))

TRANSIENT_ERROR_NAMES = {"TimeoutError", "URLError", "ConnectionError"}

def transient_retry_delay(attempts: int) -> int:
    return min(300, 5 * (2 ** min(max(attempts - 1, 0), 6)))

def is_transient_error(exc: Exception) -> bool:
    # HTTPError subclasses URLError, so it must be judged FIRST: a 400/401/403 is permanent
    # and must age toward deadletter+alert instead of being retried forever.
    if isinstance(exc, urllib.error.HTTPError):
        return exc.code == 429 or 500 <= exc.code < 600
    return isinstance(exc, (TimeoutError, urllib.error.URLError, ConnectionError))

def log(message: str) -> None:
    print(f"[hermes_dept_uplink] {time.strftime('%Y-%m-%dT%H:%M:%S%z')} {message}", flush=True)

def ensure_dirs() -> None:
    for path in (PENDING, SENT, DEAD, RECEIPTS, ALERTS):
        path.mkdir(parents=True, exist_ok=True, mode=0o700)

def validate(env: dict) -> dict:
    # 2026-08-14 iincho: 許可集合はregistryから導出(リテラル複製の解消)。読めなければfail-closed
    try:
        with open("/home/hakudoukai/hermes-departments/registry.json") as _rf:
            allowed = {str(_r.get("role_id")) for _r in (json.load(_rf).get("roles") or []) if _r.get("role_id")}
    except Exception as _exc:
        raise ValueError("registry_unreadable") from _exc
    if not allowed:
        raise ValueError("registry_empty")
    context = env.get("context_data") or {}
    source_role = context.get("source_role") or context.get("from_role")
    if env.get("from_pc") != "hermes": raise ValueError("invalid_from_pc")
    if source_role not in allowed: raise ValueError("invalid_source_role")
    if env.get("to_pc") not in ACCEPTED_TARGETS: raise ValueError("invalid_initial_to_pc")
    if env.get("message_type") != "answer": raise ValueError("invalid_message_type")
    if not env.get("topic") or not env.get("content"): raise ValueError("missing_content")
    if str(env.get("topic")).lstrip().startswith("[環境部長]"):
        raise ValueError("topic_identity_mismatch:environment_director_requires_hermes2")
    if context.get("target_agent") not in ACCEPTED_TARGETS: raise ValueError("invalid_initial_target_agent")
    outbox_id = env.get("id")
    try:
        import uuid
        outbox_id = str(uuid.UUID(str(outbox_id)))
    except Exception as exc:
        raise ValueError("invalid_outbox_id") from exc
    context = dict(context)
    context["idempotency_key"] = outbox_id
    parent_id = env.get("parent_message_id") or context.get("parent_message_id")
    recipient = env["to_pc"]
    if parent_id:
        try:
            import uuid
            parent_id = str(uuid.UUID(str(parent_id)))
        except Exception as exc:
            raise ValueError("invalid_parent_message_id") from exc
        parent = fetch_parent(parent_id)
        # 2026-08-14 iincho: 宛先規約は2026-08-03にPC名+target_agentへ移行済。
        # 旧規約 to_pc=hermes だけを許すと、現行規約の親便(to_pc=third_pc等)に
        # parent を几帳面に付けた送信者だけが deadletter に落ちる(bianalyticsで実測)。
        # ∴ 「親便が自分(役職)宛だったか」を target_agent でも判定する。fail-closedは維持。
        parent_target = str(((parent.get("context_data") or {}).get("target_agent")) or "")
        if parent.get("to_pc") != "hermes" and parent_target != source_role:
            raise ValueError("parent_target_mismatch")
        parent_from = str(parent.get("from_pc") or "").strip()
        if not parent_from:
            raise ValueError("parent_from_pc_empty")
        # 2026-08-15 iincho: from_pcは★場所★であって返信先ではない(helperはfrom_pc=third_pcで投函する)。
        # 親が reply_to_role を明示していればそれが返信先(実害: bianalyticsの返信が
        # cross_pc_inbox_third_pc=誰の箱でもないtopicへ落ちた seq192018)。
        parent_ctx = parent.get("context_data") or {}
        recipient = str(parent_ctx.get("reply_to_role") or parent_from)
        context.update({"routing_intent":"direct_parent_recipient", "parent_from_pc":parent_from,
                        "writer_role":source_role, "writer_registry_version":1})
    else:
        context.update({"routing_intent":"management_report", "writer_role":source_role,
                        "writer_registry_version":1})
    if recipient == "fukuincho":
        # 委員長 policy裁定 seq156865 (2026-08-08): 副委員長は 2026-08-11 まで停止中。
        # fukuincho 宛のままだと「誰も読まない箱へ正しく届く」だけになるため iincho へ振り替える。
        # 8/11 復帰時に戻すかを再判断すること。差し替えたことは context_data に残す。
        context["policy_original_recipient"] = "fukuincho"
        context["policy_ref_seq"] = 156865
        recipient = "iincho"
    context["target_agent"] = recipient
    # pc_handshake MAIL_OR_TELEMETRY guard: an envelope that carries context_data.target_agent
    # MUST use a routable topic ('cross_pc_inbox_<recipient>'); a human subject there is a
    # message that is addressed but never delivered. Keep the subject as body line 1.
    human_subject = str(env["topic"]).strip()
    delivery_topic = f"cross_pc_inbox_{recipient}"
    body = env["content"]
    if human_subject and not str(body).lstrip().startswith(human_subject):
        body = f"{human_subject}\n{body}"
    context["subject"] = human_subject
    payload = {
        "from_pc": env["from_pc"], "to_pc": recipient,
        "message_type": env["message_type"], "priority": env.get("priority", "high"),
        "topic": delivery_topic, "content": body,
        "requires_response": bool(env.get("requires_response", False)),
        "clinic_id": env.get("clinic_id", "hakudoukai_main"), "context_data": context,
        "idempotency_key": outbox_id,
    }
    if parent_id:
        payload["parent_message_id"] = parent_id
    return payload

def fetch_parent(parent_id: str) -> dict:
    url = os.environ.get("SUPABASE_URL", "").rstrip("/")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    if not url or not key: raise RuntimeError("supabase_env_missing")
    query = urllib.parse.urlencode({"id": f"eq.{parent_id}", "select": "id,seq,from_pc,to_pc,context_data", "limit": "2"})
    req = urllib.request.Request(f"{url}/rest/v1/pc_handshake?{query}",
        headers={"Authorization": f"Bearer {key}", "apikey": key})
    with urllib.request.urlopen(req, timeout=20) as res:
        rows = json.loads(res.read().decode() or "[]")
    if len(rows) != 1: raise ValueError("parent_not_unique")
    return rows[0]

def post(payload: dict) -> list:
    url = os.environ.get("SUPABASE_URL", "").rstrip("/")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    if not url or not key: raise RuntimeError("supabase_env_missing")
    req = urllib.request.Request(
        f"{url}/rest/v1/pc_handshake", data=json.dumps(payload, ensure_ascii=False).encode(), method="POST",
        headers={"Authorization": f"Bearer {key}", "apikey": key,
                 "Content-Type": "application/json", "Prefer": "return=representation"},
    )
    with urllib.request.urlopen(req, timeout=20) as res:
        return json.loads(res.read().decode() or "[]")

def find_existing(idempotency_key: str) -> list:
    url = os.environ.get("SUPABASE_URL", "").rstrip("/")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    query = urllib.parse.urlencode({"idempotency_key": f"eq.{idempotency_key}", "select": "id,seq"})
    req = urllib.request.Request(
        f"{url}/rest/v1/pc_handshake?{query}",
        headers={"Authorization": f"Bearer {key}", "apikey": key},
    )
    with urllib.request.urlopen(req, timeout=20) as res:
        return json.loads(res.read().decode() or "[]")

def alert(path: pathlib.Path, reason: str) -> None:
    body = {"file": path.name, "reason": reason,
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%S%z")}
    tmp = ALERTS / f".{path.name}.tmp"
    tmp.write_text(json.dumps(body, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(tmp, ALERTS / path.name)

def process(path: pathlib.Path) -> None:
    try:
        env = json.loads(path.read_text(encoding="utf-8"))
        payload = validate(env)
    except Exception as exc:
        shutil.move(str(path), str(DEAD / path.name))
        alert(path, f"validation:{type(exc).__name__}")
        log(f"deadletter file={path.name} reason=validation:{exc}")
        return

    now = time.time()
    if float(env.get("next_retry_epoch", 0) or 0) > now:
        return
    attempts = int(env.get("delivery_attempts", 0))
    transient_attempts = int(env.get("transient_attempts", 0))
    # Migrate rows created by the old watcher, which counted network timeouts
    # toward the permanent deadletter ceiling.
    if not transient_attempts and env.get("last_error_type") in TRANSIENT_ERROR_NAMES:
        transient_attempts = attempts
        attempts = 0
        env["delivery_attempts"] = 0
    try:
        try:
            rows = post(payload)
        except urllib.error.HTTPError as exc:
            if exc.code != 409:
                raise
            rows = find_existing(payload["idempotency_key"])
            if not rows:
                raise
        row = rows[0] if rows else {}
        # Persist the normalized retry state before archiving the envelope.
        # Otherwise a successfully delivered item migrated from the old
        # timeout policy still looks like a deadletter candidate in SENT.
        env["delivery_attempts"] = attempts
        env["transient_attempts"] = transient_attempts
        env.pop("last_error_type", None)
        env.pop("next_retry_epoch", None)
        env["delivery_status"] = "delivered"
        env["delivered_seq"] = row.get("seq")
        path.write_text(json.dumps(env, ensure_ascii=False) + "\n", encoding="utf-8")
        receipt = {"outbox_id": env.get("id"), "seq": row.get("seq"), "row_id": row.get("id"),
                   "delivered_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "from_pc": env.get("from_pc")}
        (RECEIPTS / path.name).write_text(json.dumps(receipt, ensure_ascii=False) + "\n", encoding="utf-8")
        shutil.move(str(path), str(SENT / path.name))
        log(f"delivered role={(env.get('context_data') or {}).get('source_role')} seq={row.get('seq')} file={path.name}")
    except Exception as exc:
        env["last_error_type"] = type(exc).__name__
        if isinstance(exc, urllib.error.HTTPError):
            try:
                detail = exc.read().decode("utf-8", "replace")[:500]
            except Exception:
                detail = "<body_unavailable>"
            env["last_error_code"] = exc.code
            env["last_error_detail"] = detail
            log(f"http_error file={path.name} code={exc.code} detail={detail}")
        if is_transient_error(exc):
            transient_attempts += 1
            delay = transient_retry_delay(transient_attempts)
            env["transient_attempts"] = transient_attempts
            env["next_retry_epoch"] = time.time() + delay
            path.write_text(json.dumps(env, ensure_ascii=False) + "\n", encoding="utf-8")
            log(f"transient_retry_pending file={path.name} transient_attempts={transient_attempts} delay={delay}s error={type(exc).__name__}")
            return
        attempts += 1
        env["delivery_attempts"] = attempts
        env["next_retry_epoch"] = time.time() + INTERVAL
        path.write_text(json.dumps(env, ensure_ascii=False) + "\n", encoding="utf-8")
        if attempts >= MAX_ATTEMPTS:
            shutil.move(str(path), str(DEAD / path.name))
            alert(path, f"delivery:{type(exc).__name__}:attempts={attempts}")
            log(f"deadletter file={path.name} attempts={attempts} error={type(exc).__name__}")
        else:
            log(f"retry_pending file={path.name} attempts={attempts} error={type(exc).__name__}")

def main() -> int:
    ensure_dirs()
    lock_path = OUTBOX / "watcher.lock"
    lock_file = lock_path.open("w")
    try:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        log("another_instance_running")
        return 0
    log(f"started interval={INTERVAL}s")
    while True:
        for path in sorted(PENDING.glob("*.json")):
            process(path)
        time.sleep(INTERVAL)

if __name__ == "__main__":
    raise SystemExit(main())
