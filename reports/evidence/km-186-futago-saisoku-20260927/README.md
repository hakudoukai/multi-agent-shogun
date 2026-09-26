# km-186（板 1d8fd33b）双子 census と ERR-EKARTE-001 是正の所在の再実測 ―― 專任3

- 席: ashigaru-mac-3 ／ 下命: `queue/goals/ashigaru-mac-3.yaml`（2026-09-27 00:23 fukuincho 発）
- 板の current_step: owner=karo-mac（席2=ashigaru-mac-2）・裁=小文字 `err-ekarte-001.md`（3471B）が正・大文字は git rm --cached
- 測った刻: 2026-09-27T00:24:30 +0900（生の出力は `raw/`・手で写した数は無い）

## 結論（先に）

**是正は既に origin/main に入って居る。席3 は二重に彫らぬ。**

| 項 | 実測（raw/01・02） |
|---|---|
| origin/main | `b9573b2d376e9a0a372234b696a733677feb7919` |
| docs/runbooks の ekarte | 小文字 `err-ekarte-001.md` のみ・blob `de00cbd99d9909f4a923041ae17f0d2cbb587668`（板の受入 blob de00cbd9 と一致） |
| 大文字を外した commit | `eab623bc017c01cfd4da1e2dce9119f9090ebfc7`（origin/main の祖先・is-ancestor rc=0） |
| 席2 の `4cb05b976ec0060796840e02dd579f1551d89841` | origin/main の祖先に非ず（rc=1） |
| origin/main 全 547 file の case-fold 双子 | 0 |

★この数が意味せぬ事★: 双子 0 は origin/main の tree に限る。共有樹の index・disk・他の枝の双子は測って居らぬ。

## 残る判断（席は決めぬ）

- 板 1d8fd33b を閉じるか（是正済み）、席2 の枝 4cb05b97 を PR として扱ふかは家老・総監督の判断。

## やらなかった事

共有樹・席2 の枝・runbook 本体は一切書き換えて居らぬ（読取のみ）。push せぬ。DB 書込なし。自席 worktree `ashigaru-mac-3/km-186-futago-saisoku-20260927`（base origin/main b9573b2d）への commit のみ。
