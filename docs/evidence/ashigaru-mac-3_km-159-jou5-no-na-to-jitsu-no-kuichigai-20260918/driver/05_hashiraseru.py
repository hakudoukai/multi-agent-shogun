# -*- coding: utf-8 -*-
"""走らせ器 ―― 門を一度走らせ、out/err/rc を ★管を通さず★ 受ける。
rc は subprocess の returncode(= waitpid の出目)であり、shell の pipeline を通らぬ。
env は「渡す/渡さぬ」を分けて扱ふ ―― 未設定 と 空文字 は別物である。"""
import os
import subprocess

GATE = "scripts/checks/karo_mac_dasumae_gate.sh"


def hashiru(args, env_name=None, env_val=None, cwd=None, tmo=60):
    """env_val is None かつ env_name 有り → ★其の変数を消して★ 走らせる(未設定)。"""
    e = dict(os.environ)
    if env_name is not None:
        if env_val is None:
            e.pop(env_name, None)
        else:
            e[env_name] = env_val
    p = subprocess.run(["bash", GATE] + list(args), cwd=cwd, env=e,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=tmo)
    return p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace"), p.returncode


def mieru(s):
    """値を一行に見える形へ(空・空白・改行を潰さぬ)。"""
    if s is None:
        return "(未設定)"
    if s == "":
        return "(空文字)"
    return "«" + s.replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t") + "»"
