#!/usr/bin/env python3
"""
hakudokai_role_init.py — ~/.openclaw/role.json 生成・更新ヘルパー。

minimal_install.sh の内部 + 単独実行両対応。

Usage:
    hakudokai_role_init.py --role kouchan [--idle-dir /tmp] [--print]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone

VALID_ROLES = ("fukuincho", "yama", "kuro", "sakura", "kouchan")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="hakudokai role.json initializer")
    parser.add_argument("--role", required=True, choices=VALID_ROLES)
    parser.add_argument("--idle-dir", default="/tmp")
    parser.add_argument("--shogun-version", default="v4.6.0")
    parser.add_argument("--patch-version", default="v0.1")
    parser.add_argument(
        "--clinic-id",
        default=os.environ.get("HAKUDOKAI_CLINIC_ID", "hakudoukai_main"),
        help="Phase B-4 task 3: clinic_id を role.json に格納 (default: HAKUDOKAI_CLINIC_ID env or hakudoukai_main)",
    )
    parser.add_argument("--print", action="store_true", help="print current role.json and exit")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    role_dir = os.path.expanduser("~/.openclaw")
    role_file = os.path.join(role_dir, "role.json")

    if args.print:
        if os.path.isfile(role_file):
            with open(role_file, encoding="utf-8") as fh:
                sys.stdout.write(fh.read())
        else:
            sys.stderr.write(f"[role_init] {role_file} not found\n")
            return 1
        return 0

    # Phase B-4 task 3: clinic_id format check (^[a-z0-9_]+$ 3-64)
    import re as _re
    if not _re.match(r"^[a-z0-9_]+$", args.clinic_id) or not (3 <= len(args.clinic_id) <= 64):
        sys.stderr.write(
            f"[role_init] FATAL: invalid --clinic-id '{args.clinic_id}' "
            f"(must match ^[a-z0-9_]+$ length 3-64)\n"
        )
        return 2

    payload = {
        "role": args.role,
        "clinic_id": args.clinic_id,
        "idle_flag_dir": args.idle_dir,
        "installed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "shogun_version": args.shogun_version,
        "minimal_patch_version": args.patch_version,
    }

    if args.dry_run:
        json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
        return 0

    os.makedirs(role_dir, exist_ok=True)
    with open(role_file, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    # Codex audit fix #5: chmod 失敗を silent でなく warn 出力 (Win 環境では chmod 不完全な場合あり)
    try:
        os.chmod(role_file, 0o600)
    except OSError as exc:
        sys.stderr.write(
            f"[role_init] WARN chmod 600 failed on {role_file}: {exc} "
            f"(POSIX 権限非対応環境? secret 露出リスクあり、適切な権限を別途設定してください)\n"
        )
    sys.stdout.write(f"[role_init] wrote {role_file} role={args.role}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
