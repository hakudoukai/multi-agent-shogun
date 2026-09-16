# -*- coding: utf-8 -*-
"""30_ate.py — 396組(18閾 × 22形)を ★束内の写しから抜いた番人★ へ当てる。
   ★生器は一度も走らせぬ★ ―― 走るのは ki/guard_*.sh (写しから逐語で抜いた番人) のみ。
   出目: raw/30_ate.tsv  欄は行頭の #colspec を見よ。
"""
import base64, importlib.util, os, subprocess, sys, pathlib

HERE = pathlib.Path(__file__).resolve().parent          # <束>/ki
BUNDLE = HERE.parent                                     # <束>
def load(name, fn):
    spec = importlib.util.spec_from_file_location(name, HERE / fn)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
K = load("kata", "10_kata.py")
S = load("shikii", "20_shikii.py")

STUB = """#!/usr/bin/env bash
{setflags}
LOG="${{KM52_LOG:-/dev/null}}"
{th_say}
{guard}
__ES="$(env_state "$1")"
fix_threshold "$1" "$2" "$3"
__RC=$?
eval "__V=\\"\\${{$3-}}\\""
{{
  printf 'ENVSTATE=%s\\n' "$__ES"
  printf 'RC=%s\\n' "$__RC"
  printf 'VALUE_B64=%s\\n' "$(printf '%s' "${{__V}}" | base64 | tr -d '\\n')"
}} > "$KM52_OUT"
"""

def build_stubs():
    paths = {}
    for key, meta in S.KI.items():
        guard = (HERE / meta["guard"]).read_text(encoding="utf-8")
        p = HERE / ("stub_%s.sh" % key)
        p.write_text(STUB.format(setflags=meta["setflags"], th_say=meta["th_say"], guard=guard),
                     encoding="utf-8")
        paths[key] = p
    return paths

def main():
    stubs = build_stubs()
    outdir = BUNDLE / "raw"; outdir.mkdir(exist_ok=True)
    logdir = outdir / "30_logs"; logdir.mkdir(exist_ok=True)
    rows = []
    n_run = n_unmeasurable = 0
    for key, name, dflt, outvar, line in S.SHIKII:
        for tag, kname, val in K.KATA:
            rep = outdir / ".30_report.tmp"
            logf = logdir / ("%s_%s_%s.log" % (key, name, tag))
            env = dict(os.environ)
            for _k, _n, _d, _o, _l in S.SHIKII:      # 他の閾は環境から除く(相互汚染防止)
                env.pop(_n, None)
            env["KM52_OUT"] = str(rep); env["KM52_LOG"] = str(logf)
            note = ""
            if val is None:
                env.pop(name, None)
            else:
                env[name] = val
            if rep.exists(): rep.unlink()
            try:
                # ★NUL は execve(2) が拒む ―― 番人の手前で死ぬ(dict へは載る)★
                pr = subprocess.run(["/bin/bash", str(stubs[key]), name, dflt, outvar],
                                    env=env, capture_output=True)
            except ValueError as e:
                rows.append((key, name, dflt, outvar, tag, kname, "測れぬ", "execve拒", "―",
                             "―", "", base64.b64encode(
                                 ("%s: %s" % (e.__class__.__name__, e)).encode()).decode()))
                n_unmeasurable += 1
                continue
            n_run += 1
            got = {}
            if rep.exists():
                for ln in rep.read_text(encoding="utf-8").splitlines():
                    if "=" in ln:
                        k2, _, v2 = ln.partition("="); got[k2] = v2
            value = base64.b64decode(got.get("VALUE_B64", "")).decode("utf-8", "replace")
            said = (pr.stderr or b"") + (pr.stdout or b"")
            narrow = "鳴" if said.strip() else "黙"
            accepted = "受" if (val is not None and value == val) else "倒"
            rows.append((key, name, dflt, outvar, tag, kname, got.get("ENVSTATE", "?"),
                         got.get("RC", "?"), narrow, accepted,
                         base64.b64encode(value.encode()).decode(),
                         base64.b64encode(said).decode()))
    hdr = ("#colspec\t器\tenv名\t既定\t受け皿\t形札\t形名\tenv_state\trc\t鳴黙\t受倒\t"
           "採用値_b64\t吐いた文_b64")
    with open(outdir / "30_ate.tsv", "w", encoding="utf-8") as fh:
        fh.write(hdr + "\n")
        for r in rows:
            fh.write("\t".join(str(x) for x in r) + "\n")
    print("組=%d (走=%d・測れぬ=%d)" % (len(rows), n_run, n_unmeasurable))
    assert len(rows) == 18 * 22 == 396, len(rows)

main()
