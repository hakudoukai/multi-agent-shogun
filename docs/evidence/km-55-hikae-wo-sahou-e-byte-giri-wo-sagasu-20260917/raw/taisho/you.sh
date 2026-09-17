#!/bin/bash
# ★陽性対照★ 七形を一形づつ、且つ ★印の下流★ を一本 混ぜる
echo "$v" | cut -b1-40            # ①cut_b
echo "$v" | cut -c1-40            # ②cut_c
x="${v:0:40}"                     # ③bash_sl(非下流)
y="${_ft_vp:0:40}"                # ③bash_sl(★下流★)
printf '%.40s\n' "$v"             # ④pf_prec
echo "$v" | head -c 40            # ⑤head_c
echo "$v" | dd bs=40 count=1      # ⑥dd_bs
awk '{print substr($0,1,40)}'     # ⑦awk_sub
echo "$_ft_vp" | cut -b1-40       # ①cut_b(★下流★)
