# origin の當隊枝 検分 ―― 家老mac (裁 seq325493 の返し)

刻: 2026-09-17T13:32:36+0900
器: git ls-remote --heads origin / git cherry (patch-id) / git merge-base --is-ancestor
母數: origin の全枝 239本 の内、refs/heads/karo-mac/* と refs/heads/ashigaru-mac-*/* = ★59本★
      (karo-mac/ = 41本 / ashigaru-mac-*/ = 18本)

## ★不要の候補 9本★ ―― 己の寄与が 0本(git cherry <local main> <枝> の + が零)
定義: 「不要」= 枝の tip が指す中身が、基点(local main 363d5fb)に既に悉く在る事。
     即ち其の枝を辿らずとも main を辿れば同じ物に届く。

  - karo-mac/a3-r39-fix-20260917  2992eecab19d86872c4c0e01f660d38d16397f9a
  - karo-mac/gate4-20260909  707df79147233d183b373b440e33472ba4c99a32
  - karo-mac/gate5-20260909  e8470d8c453649c8fcbfd3bce459a346b46446b6
  - karo-mac/gate5-note-20260909  e8470d8c453649c8fcbfd3bce459a346b46446b6
  - karo-mac/km-50-47-20260917  43808f8363e9320d657f342e92e34a2bae35298d
  - karo-mac/km-dead-inbox-gate-20260917  b82b98c91222529e233d0f3f5ae1fb6756916775
  - karo-mac/km-gate-kou-otsu-20260917  363d5fb060845171338c067ef42bfcbef8ad9188
  - karo-mac/manifest-verify-20260909  f0d59a3b6315058b2af40bd57689b397243e32c9
  - karo-mac/skills-tools-20260908b  6e9d40600a801aa713ac238e2e62bbae06c9e683

  併せて: karo-mac/gate5-20260909 と karo-mac/gate5-note-20260909 は ★同一 sha★ (e8470d8c4536…) を指す。

## ★消す前に必ず読め ―― 今消しては ならぬ★
local main  = 363d5fb060845171338c067ef42bfcbef8ad9188
origin main = 4be3ee19e1c5113eb4c2490cd4b496e9b453c7d1 (ls-remote 時点)
patch-id で両向きに測つた:
  local main に在り origin/main に無い = ★14本★
  origin/main に在り local main に無い = ★8本★
∴ ★両向きに乖離して居る★。上の9本の中身は ★local main にしか無い★ ――
  origin/main を辿つても届かぬ。今 origin から消せば ★origin 側から中身が失せる★。
  ∴ 消すのは ★main の乖離(14/8)が解けた後★ にせられたい。

## 残 50本
寄与が同一の枝の組 = ★0組★。50本は各々 唯一の寄与を持つ ∴ 不要に非ず。

## 家老の断り(數が何を意味せぬか)
・「不要」は ★基点を local main に取つた時の値★ である。基点を origin/main に取ると
  同じ器で ★1本★(skills-tools-20260908b)しか出ぬ ―― 母數が違ふだけで、双方 正しい。
・消してよいか否かは本紙では断じて居らぬ。★消すのは総監督★ である(裁 seq325493)。
