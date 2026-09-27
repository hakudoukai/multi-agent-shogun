# 板 97774de5 km-226 を main 版の門で走らせ直す（門の版を命に pin）―― 專任3（ashigaru-mac-3）

- 下命: `queue/goals/ashigaru-mac-3.yaml`（2026-09-27 17:02 gakushu-bucho・板 97774de5）。受入は板の current_step「門 sha256 を命に pin し main 版で再走した rc と raw」とした。
- 枝: `ashigaru-mac-3/97774de5-km226-main-gate-pin-20260928`。親は席2の km-226 commit `d5c8a847634460d67b6df37a07bb492440124659`。
- 対象: km-222 束（commit `74c16d0b8e70b35b18e04353f015166f13b4b3a2` から `git archive` で取り出した）の臺帳 manifest.txt と、席2が km-226 で使った25本（`raw/02_filelist_25.txt` を d5c8a847 から写した）。束は読むだけで、書き換えていない。

## 何を足したか（席2の km-226 との違い）

席2の km-226（d5c8a847）も main 門 04672e15 で走っていた。ただし sha256 は `raw/01_main_gate_sha256.txt` に別に刷っただけで、走らせる命は sha256 を確かめていなかった。
本弾は `run_pinned.sh` の中に門と依存2本の sha256 を書き込み、一つでも合わなければ門を走らせずに rc=90 で止まるようにした。

## 門（raw/gate/・origin/main `b9573b2d376e9a0a372234b696a733677feb7919` の blob から取り出した）

| file | git blob（raw/00） | sha256（raw/01・run_pinned.sh に pin） |
|---|---|---|
| karo_mac_dasumae_gate.sh | 04672e15b1edf4a02b7cea1f4f32cfb9a64e34d5 | 3b8b7182566cc8c4e81533d27d2f6c5d98a9b56429d2d7205dfca9d3a9295bac |
| karo_mac_manifest_verify.py | 155aeb7a3929786fe97bc58e3f909c710a99e796 | 9e831137f1d33f41b6ba88414b26d44dfb93ebc9c544d263f7c0c1d1234e4d8f |
| karo_mac_fukashiji.py | 20a28566c9b612ea01a9dd0b837b7dd3e23f1dfb | 8c06f5c58147ccba3b1e040c0930a6f10374987fb717d29b3cd5dc2e766800ad |

門の sha256 3b8b7182… は、席2の `raw/01_main_gate_sha256.txt` に刷られた値と同じである。

## 結果

| 測り | 結果 | raw |
|---|---|---|
| pin 3本の照合 | 3本とも want=got | 10_run_pinned.stdout |
| 門の rc（main 版・25本） | **0** | 70_gate_main.rc |
| 門の出力 | 條① 一致・條②③④ 全25本通・條⑤ byte和 4670151・「出す前 門 通」 | 70_gate_main.err / .out |
| 命全体の rc | 0（stderr は 0 byte。空の file は門の條④に掛かるため、byte 数だけを 10_run_pinned.stderr_bytes.txt に残して消した） | 10_run_pinned.rc |
| **陽性対照**: 門の複製の末尾に1行足して同じ命を走らせる | **rc=90**・「PIN不一致 karo_mac_dasumae_gate.sh ―― 走らせぬ」。門は走らず、出力 dir は 0 file | 20_posctrl_tampered.* / 20_posctrl_outdir_count.txt |
| 席2の raw（d5c8a847 の raw/70_gate_main.*）との比較 | err・rc は byte 一致。out は2行目の cwd だけが違う（席2 = /Users/momizimac/wt/a2-km222/…・本弾 = /Users/momizimac/wt/a3-97774de5-km222src/…） | 30_cmp_vs_seki2_d5c8a847.txt / 31_diff_out_vs_seki2.txt |

∴ main 版の門（sha256 を命に pin）で km-222 束25本は rc=0 で通る。席2 の km-226 の結果（主門 rc=0）と同じである。

**この結果が意味しないこと**
- 門の條①は臺帳にある行しか照らさない（席2 km-226 ㋐で実測済み）。臺帳に無い紙が束にあっても、rc=0 はそれが無いことを示さない。
- 舊門 054c442e は走らせ直していない。板の受入は main 版だけである。
- 門の依存は `dirname "$0"` で引く2本だけと、門の本文（L154・L227・L231）を読んで確かめた。python3 そのものの版は pin していない。

## やらなかったこと

main へ push していない。km-222 束と席2の束は書き換えていない。DB への書き込みは無い。歯式6file・design tokens・本番・secret には触れていない。
