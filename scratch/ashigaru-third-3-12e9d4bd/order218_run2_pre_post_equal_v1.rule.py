# -*- coding: utf-8 -*-
"""order218 走2 ―― 直し前後で ★同値★ かを器に言はせる (家老令 9a112d42)
条①stage2 を直に呼ぶ ②前後の生を両方残す ③同値でなければ止めて申す ④紙へ一行
「前」の姿は git に無い ∴ ★己が挿れた字を機械で剥いで★ 作る (剥ぐ字は下の DEL に逐語)
"""
import io, os, sys, contextlib

HERE = os.path.dirname(os.path.abspath(__file__))

# ―― 挿れた字 (剥ぐ対象・逐語)。何れも % を一字も含まぬ ――
DEL = {
 "order179_recall_and_toolfix_v1.rule.py": [
   "\u30fb\u2605\u4eba\u304c\u540d\u3092\u8b80\u3081\u306a\u3093\u3060\u4ef6\u3092\u542b\u3080\u2605",
   " \u2015\u2015 \u2605\u5206\u5b50\u306f \u32d0 \u3086\u3091 \u8b80\u3081\u306a\u3093\u3060\u4ef6\u3092\u542b\u307e\u306c \u2234 \u5206\u5b50\u3068\u5206\u6bcd\u306f\u5225\u306e\u6bcd\u3067\u3042\u308b\u2605",
   "\u30fb\u8b80\u3081\u306a\u3093\u3060\u4ef6\u3092\u542b\u3080",
   " \u2605\u5206\u5b50\u306f\u542b\u307e\u306c\u2234\u5225\u6bcd\u2605",
 ],
 "order180_window_widen_v1.rule.py": [
   "\u3002\u2605\u4f46\u3057\u6b64\u306e\u5206\u6bcd\u306f \u4eba\u304c\u540d\u3092\u8b80\u3081\u306a\u3093\u3060\u4ef6\u3092\u542b\u307f\u3001\u5206\u5b50\u306f\u542b\u307e\u306c \u2234 \u5225\u6bcd\u3067\u3042\u308b\u2605",
   "  \u2015\u2015 \u2605\u9069\u5408\u306e\u5206\u6bcd\u306f\u8b80\u3081\u306a\u3093\u3060\u4ef6\u3092\u542b\u307f \u5206\u5b50\u306f\u542b\u307e\u306c=\u5225\u6bcd\u2605",
 ],
 "order181_vocab_window_both_v1.rule.py": [
   "(\u2605\u5225\u6bcd:\u53d6\u308c\u305f\u4ef6\u306f\u8b80\u3081\u306a\u3093\u3060\u3092\u542b\u307f/\u5206\u5b50\u306f\u542b\u307e\u306c\u2605)",
 ],
 "order182_asym_and_two_bands_v1.rule.py": [
   "(\u2605\u5225\u6bcd:\u53d6\u308c\u305f\u4ef6\u306f\u8b80\u3081\u306a\u3093\u3060\u3092\u542b\u307f/\u5206\u5b50\u306f\u542b\u307e\u306c\u2605)",
 ],
 "order183_frame_precision_v1.rule.py": [
   "(\u2605\u5225\u6bcd:\u53d6\u308c\u305f\u4ef6\u306f\u8b80\u3081\u306a\u3093\u3060\u3092\u542b\u307f/\u5206\u5b50\u306f\u542b\u307e\u306c\u2605)",
 ],
}

# ―― 各器で呼ぶ函 (o179 のみ __main__ が stage2 を呼ばぬ ∴ 直に呼ぶ) ――
CALL = {
 "order179_recall_and_toolfix_v1.rule.py": ["stage2"],
 "order180_window_widen_v1.rule.py":       ["stage2"],
 "order181_vocab_window_both_v1.rule.py":  ["stage1", "stage2"],
 "order182_asym_and_two_bands_v1.rule.py": ["stage1", "stage2", "stage3"],
 "order183_frame_precision_v1.rule.py":    ["stage1", "stage2", "stage3"],
}

def run_one(path, src, calls):
    ns = {"__name__": "__o218_driver__", "__file__": path}
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        exec(compile(src, path, "exec"), ns)
        for fn in calls:
            ns[fn]()
    return buf.getvalue()

def main():
    cwd_keep = os.getcwd()
    os.chdir(HERE)
    sys.path.insert(0, HERE)
    pre_all, post_all, verdicts = [], [], []
    for fn in sorted(DEL):
        path = os.path.join(HERE, fn)
        post_src = io.open(path, encoding="utf-8").read()
        pre_src = post_src
        for d in DEL[fn]:
            assert pre_src.count(d) >= 1, "DEL_MISS " + fn + " " + repr(d[:20])
            pre_src = pre_src.replace(d, "")
        assert pre_src != post_src, "NO_DIFF " + fn
        assert "%" not in "".join(DEL[fn]), "DEL_HAS_PERCENT " + fn

        post_out = run_one(path, post_src, CALL[fn])
        pre_out  = run_one(path, pre_src,  CALL[fn])

        norm = post_out
        for d in DEL[fn]:
            norm = norm.replace(d, "")
        same = (norm == pre_out)
        verdicts.append((fn, same, len(pre_out.split(chr(10))), len(post_out.split(chr(10)))))
        pre_all.append("######## " + fn + " (\u524d) ########" + chr(10) + pre_out)
        post_all.append("######## " + fn + " (\u5f8c) ########" + chr(10) + post_out)

    os.chdir(cwd_keep)
    io.open(os.path.join(HERE, "order218_stage2_pre.raw.txt"), "w", encoding="utf-8").write(chr(10).join(pre_all))
    io.open(os.path.join(HERE, "order218_stage2_post.raw.txt"), "w", encoding="utf-8").write(chr(10).join(post_all))

    print("== \u524d\u5f8c\u306e\u7a81\u5408 (\u6311\u3093\u3060\u5b57\u3092\u5265\u3044\u3066\u5168\u6587\u6bd4\u8f03) ==")
    bad = 0
    for fn, same, np_, ns_ in verdicts:
        print("  " + ("SAME" if same else "DIFF") + "  " + fn + "  pre_split=" + str(np_) + " post_split=" + str(ns_))
        if not same:
            bad += 1
    print("== \u9069\u5408\u30fb\u518d\u73fe\u306e\u884c (\u5f8c) ==")
    for ln in chr(10).join(post_all).split(chr(10)):
        if ("\u9069\u5408" in ln) or ("\u518d\u73fe" in ln):
            print("  | " + ln.strip()[:160])
    print("BAD=" + str(bad))

main()
