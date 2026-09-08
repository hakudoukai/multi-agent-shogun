#!/usr/bin/env python3
# order88: git が pre-push hook を呼ぶ時の $0 を隔離 repo で実測する規
# 本物の hook (/mnt/c/DentalBI/.git/hooks/*) は ★讀むのみ・一指も触れぬ★。
# DB 0・network 0 (local path clone)・製品 0。
import subprocess, pathlib, shutil, hashlib, json, sys, os, time

LAB = pathlib.Path("scratch/ashigaru-third-2-fa06a3a1/o88_lab").resolve()
REAL_BAK = pathlib.Path("/mnt/c/DentalBI/.git/hooks/pre-push.bak-loadshed-20260907")
REAL_INSTALL = pathlib.Path("/mnt/c/DentalBI/scripts/git-hooks/install.sh")
BAKNAME = "pre-push.bak-loadshed-20260907"
T0 = time.time()
out = {}

def run(cmd, cwd=None, env=None):
    e = dict(os.environ); e.update(env or {})
    p = subprocess.run(cmd, cwd=cwd, env=e, capture_output=True, text=True, timeout=60)
    return {"argv": cmd, "rc": p.returncode, "out": p.stdout, "err": p.stderr}

def sha16(b):
    return hashlib.sha256(b).hexdigest()[:16]

if LAB.exists():
    shutil.rmtree(LAB)
LAB.mkdir(parents=True)

# ── 隔離 repo を建てる ─────────────────────────────
origin = LAB / "origin.git"
work = LAB / "work"
run(["git", "init", "--bare", "-q", str(origin)])
run(["git", "init", "-q", "-b", "main", str(work)])
for k, v in [("user.email", "a2@example.invalid"), ("user.name", "order88-lab"),
             ("commit.gpgsign", "false")]:
    run(["git", "config", k, v], cwd=work)
run(["git", "remote", "add", "origin", str(origin)], cwd=work)
(work / "seed.txt").write_text("order88 lab\n", encoding="utf-8")
run(["git", "add", "seed.txt"], cwd=work)
run(["git", "commit", "-q", "-m", "seed"], cwd=work)
hooks = work / ".git" / "hooks"

# ── 測① / ② : probe hook で $0 の生値と basename を録る ─────────
probe = '#!/bin/bash\n' \
        'echo "PROBE_DOLLAR0=[$0]"\n' \
        'echo "PROBE_BASENAME=[$(basename "$0")]"\n' \
        'echo "PROBE_PWD=[$PWD]"\n' \
        'exit 0\n'
(hooks / "pre-push").write_text(probe, encoding="utf-8")
os.chmod(hooks / "pre-push", 0o755)
out["m1_probe_push"] = run(["git", "push", "-q", "origin", "main"], cwd=work)

# ── 測④ : 名が .bak-… の時に呼ばれるか ─────────────────
(hooks / "pre-push").unlink()
(hooks / BAKNAME).write_text(probe, encoding="utf-8")
os.chmod(hooks / BAKNAME, 0o755)
(work / "b.txt").write_text("b\n", encoding="utf-8")
run(["git", "add", "b.txt"], cwd=work); run(["git", "commit", "-q", "-m", "b"], cwd=work)
out["m4_bakname_only"] = run(["git", "push", "-q", "origin", "main"], cwd=work)

# ── 測③ : 案文 C を当てた「本物 bak の写し」を pre-push の名で置く ──
real = REAL_BAK.read_bytes()
out["real_bak_sha16"] = sha16(real)
lines = real.decode("utf-8").split("\n")
gate = [
    '# ── 戻し防止の門（案文・隔離 repo でのみ当てた）──────────────',
    '# 此の版は 2026-09-07 の DB負荷止血より前の姿である（止血の門を持たぬ）。',
    '# 名を pre-push へ戻すと push 毎に source_code_cache の同期と stale 検査が走る。',
    '# 止血前の姿は git に残る: git show 4b1f7d293:scripts/git-hooks/pre-push',
    'if [ "$(basename "$0")" = "pre-push" ]; then',
    '  echo "[pre-push] BLOCKED: 之は止血前の退避版である（総監督 2026-09-07・dev_qa#822）。"',
    '  echo "[pre-push]   正規の hook を戻すには: bash scripts/git-hooks/install.sh"',
    '  exit 1',
    'fi',
    '',
]
gated = "\n".join([lines[0]] + gate + lines[1:])
out["gated_sha16"] = sha16(gated.encode("utf-8"))
out["gated_lines"] = gated.count("\n")
(hooks / BAKNAME).unlink()
(hooks / "pre-push").write_text(gated, encoding="utf-8")
os.chmod(hooks / "pre-push", 0o755)
(work / "c.txt").write_text("c\n", encoding="utf-8")
run(["git", "add", "c.txt"], cwd=work); run(["git", "commit", "-q", "-m", "c"], cwd=work)
out["m3_gated_as_prepush"] = run(["git", "push", "-q", "origin", "main"], cwd=work)

# ── 測③' : 同じ門付き file を .bak-… の名で置いた時 (門は鳴らぬ筈) ──
(hooks / "pre-push").unlink()
(hooks / BAKNAME).write_text(gated, encoding="utf-8")
os.chmod(hooks / BAKNAME, 0o755)
out["m3b_gated_as_bakname"] = run(["git", "push", "-q", "origin", "main"], cwd=work)

# ── 測⑤ : install.sh が退避 file を触らぬかの裏取り ────────────
srcdir = work / "scripts" / "git-hooks"
srcdir.mkdir(parents=True)
shutil.copy2(REAL_INSTALL, srcdir / "install.sh")
canon = '#!/bin/bash\n# 隔離 repo の正規版 (止血の門を持つ体)\n' \
        'if [ "${SYNC_SOURCE_CACHE_FORCE:-0}" != "1" ]; then\n' \
        '  echo "[pre-push] source_code_cache sync SKIPPED (lab)"\n  exit 0\nfi\n' \
        'echo "[pre-push] would sync (lab)"\nexit 0\n'
(srcdir / "pre-push").write_text(canon, encoding="utf-8")
before = sorted(p.name for p in hooks.iterdir())
out["m5_before"] = before
out["m5_bak_sha16_before"] = sha16((hooks / BAKNAME).read_bytes())
out["m5_install_run"] = run(["bash", "scripts/git-hooks/install.sh"], cwd=work)
after = sorted(p.name for p in hooks.iterdir())
out["m5_after"] = after
out["m5_bak_still_there"] = BAKNAME in after
out["m5_bak_sha16_after"] = sha16((hooks / BAKNAME).read_bytes()) if BAKNAME in after else None
out["m5_prepush_sha16_after"] = sha16((hooks / "pre-push").read_bytes()) if (hooks / "pre-push").exists() else None
out["m5_canon_sha16"] = sha16(canon.encode("utf-8"))
# install.sh の sed -i が src を汚したか (隔離 repo の作業樹)
out["m5_worktree_dirty"] = run(["git", "status", "--porcelain"], cwd=work)

out["elapsed_sec"] = round(time.time() - T0, 1)
p = LAB / "o88_result.json"
p.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps(out, ensure_ascii=False, indent=1))
