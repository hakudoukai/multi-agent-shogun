# W200 断面凍結(足軽6号、2026-08-04T18:39:54+0900)

★将軍second殿令(時が惜しゅうござる)への即応。分析より先に断面を凍結する。以下は行数+sha256
のみの機械実測であり、当職の解釈・裁定は一切加えていない。★

base_commit=502cbfe(実測=HEAD一致・working tree clean、本file作成前後で再確認)。
docs/incident_logs/配下の未追跡(`??`)ファイル数=39件(git status --short実測)。

## 断面時刻

`date '+%Y-%m-%dT%H:%M:%S%z'`実測=**2026-08-04T18:39:54+0900**

## _prune_events.log

- 行数=**93**行
- sha256=`466457d00b08b9d25375e72ce99ea04b1679e7eebf95ce283d07fc646b417093`
- ★参考(W200本体提出時点)★=92行だった。★この断面凍結までの間に既に1行増えている
  (母集団が縮んだのではなく、むしろ増えて/変化しており申した)★。

## 各agent archive file(行数+sha256、全件)

| file | 行数 | sha256 |
|---|---|---|
| `_test_cap_rotation_pruned.yaml` | 130 | `695c8d7ab5717484132fb2926445b0e3dd0596e3e91296af0db0f1ecf5a4e8a2` |
| `ashigaru1_pruned.yaml` | 1193 | `137cb2592d7ba679fae7860468a9c1d212174333619fd7aa47c7b76951324ee1` |
| `ashigaru2_pruned.yaml` | 1339 | `7b2e20edccccd34f1965d402bbd6de5785dad8116c2c2f6786dc01e796a6773d` |
| `ashigaru3_pruned.yaml` | 1118 | `5ddbb6ead8cbbc79ca9daf503d7f615350fa6c1ed90f0e94e9972003fccc2df2` |
| `ashigaru4_pruned.yaml` | 1050 | `14238c0ed2dd6e3044ea823b63e51b6d3d34432c0d9f4653b233a7f67105649c` |
| `ashigaru5_pruned.yaml` | 1160 | `509adc5932c9bc6adb6b97149c164156e694ef5a3a7f4805dda0021996677ed7` |
| `ashigaru6_pruned.yaml` | 1191 | `c13bc3716e5af5e88a343fdb9bc1f2a95a87c11ee6790b2940f5bff6b07b4e7f` |
| `ashigaru7_pruned.yaml` | 1001 | `a0201e2a961c5c6f5755fc0ef6d5e8dd23f69bad8c1a6a7b8714dddc5f77f2df` |
| `gunshi-second_pruned.yaml` | 2627 | `314ad87fe1b9d81834f41cac4d4f6f3249d1cc89854c12f3b705d67cbebe7f8f` |
| `karo-second_pruned.yaml` | 11945 | `0c54bd3994d62ade592af4c89860cf60ba4ca064085738021d2e720a4ce5ca48` |
| `shogun-second_pruned.yaml` | 5551 | `fb942f827730350389dc39a394b70faa0299546216379ef7d9dccb6130cc5657` |

★W200本体提出時点(先の便)では`karo-second_pruned.yaml`の行数は明記していなかった(python
safe_load_all経由の復元件数=667通のみ報告)。★行数そのものの断面はこの凍結が初出であり、
今後の差分検証はこの表を基準とされたし★。

以上、断面凍結のみ。分析・裁定は別途W200本体(既提出)およびgunshi-second監査を参照。
