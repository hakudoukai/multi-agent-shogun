# ⑷ 乙 の最小 patch ―― ★紙の上のみ。据ゑず・commit せず★

## 乙-1 臺帳を建てる器を repo の中へ(append.py)

★先に述べる★: 此の patch は ★既に家老mac が書いて居る★ ――
`refs/heads/karo-mac/manifest-append-track-20260917` = `61a9fe1c18beffddef6b40503766ba726b8b0a05`
(commit刻 2026-09-17 16:18:13 +0900 / 題「feat(checks): 臺帳 を建てる器 を ★repo の中へ★
 ―― karo_mac_manifest_append.py(裁 326512 可)」)。
且つ其の形は ★先例 f0d59a3(裁294773)と同じ★ である。本項は「新たに書く物」ではなく
★「既に在る物が、幹にも origin/main にも入つて居らぬ」★ を述べる物である。

```diff
--- a/.gitignore
+++ b/.gitignore
@@ -166,6 +166,7 @@
 # Pre-action check scripts (§19 Post-Incident Lessons Capture)
 !scripts/checks/
 !scripts/checks/*.sh
+!scripts/checks/karo_mac_manifest_append.py
 !scripts/checks/karo_mac_manifest_verify.py
```

`git add -f` は ★用ゐぬ★(先例 f0d59a3 の commit 本文に「可逆・-f 不使用」と在る)。
許し行を足せば `git add scripts/checks/karo_mac_manifest_append.py` が素で通る。

★戻し方(一行)★:
```
git revert --no-edit 61a9fe1c18beffddef6b40503766ba726b8b0a05
```
(未だ幹に入つて居らぬ間は、より軽く `git branch -D karo-mac/manifest-append-track-20260917` でも戻る)

## 乙-2 ★より静かな方★ ―― 幹が運ぶ二本の ★版が古い★

| 器 | 幹PR#20 が運ぶ版 | 手許の版 | 差 |
|---|---|---|---|
| `scripts/checks/karo_mac_dasumae_gate.sh` | `9cd550fc2cf963ca0475b3448bb33483b9aede6b` 310行 | `054c442eaee3886b2283f98f7c3a1ab8cb813b68` 321行 | +14 -3 |
| `scripts/checks/karo_mac_manifest_verify.py` | `b19ec9ea259653d9e65d052459128c635a44e93f` 127行 | `ebfc4c0ecc080c0fcac0cb49b8e83c284a61e579` 198行 | +76 -5 |

二本とも ★共有 index には幹と同じ古い版が在り、手許の新しい版は未だ index に入つて居らぬ★
(unstaged)。∴ 最小の patch は「此の二本を commit する」一手である。

```
git add scripts/checks/karo_mac_dasumae_gate.sh scripts/checks/karo_mac_manifest_verify.py
git commit -m 'fix(checks): 門と照合器の版を幹へ揃へる(旧形行の誤判を止める)'
```

★戻し方(一行)★: `git revert --no-edit <此の commit>`

★此の一手が何を治すか★ ―― 下の「⑸ と 的」に實測で示す通り、
幹の127行版は ★裁 seq321353⑴ が「拒むな」と定めた旧形行を 実体無 と撥ね、rc が 0→1 へ反転する★。
版を揃へねば、幹だけの世界で門は ★通る筈の束に鳴る★。
