# km-231 直しの commit（板 e7a24d81-7aff-4fb5-bb3a-cad9601a4bdb）

受入（副委員長 seq366102 逐語）: karo_mac_manifest_verify.py が disk/HEAD/origin-main の三所で違う事の実測 raw＋原因1行＋直した commit40桁。

## 三所の実測（2026-09-24 22:1x・共有樹 /Users/momizimac/multi-agent-shogun）
| 所 | blob40 | 由来 commit |
|---|---|---|
| disk | ebfc4c0ecc080c0fcac0cb49b8e83c284a61e579 | 0bb82bfb（09-17 16:48）版 |
| HEAD（席枝） | b19ec9ea259653d9e65d052459128c635a44e93f | af0dacfc（09-10）版 |
| origin/main | 155aeb7a3929786fe97bc58e3f909c710a99e796 | 571f3387 版 |
| 直した版 | 534da3bdbe588991c7086ed4546c27dfebdd6b66 | c1486ca1（枝 karo-mac/daini-no-for-wo-nozoku-20260917・main へ未 merge） |

## 原因1行
直し c1486ca1（第二の for 除去）が main へ merge されず枝に留まり、共有樹は main でない席枝を HEAD に持ち disk には更に別の版が置かれた ―― ∴ 三所が三版に割れた。

## 直した commit
枝 `ashigaru-mac-3/km-231-manifest-verify-naoshi-20260924`（origin/main から切る）に c1486ca1 を cherry-pick -x。
直しの commit40 = 下の本 commit の親（`git log -2` で引け）。blob は c1486ca1 と同一 534da3bd。

## 対照の実測（raw/summary.txt・四版×三試料）
- 陽性（在る path・正 sha）: 四版とも rc=0 一致1
- 陰性（在る path・誤 sha）: 四版とも rc=1 相違1
- 囮（主張 path 不在・行中に在る別 path）: main/disk/HEAD は ★rc=0 一致1（偽の通）★、直した版は rc=1
  ―― 但し直した版の札は「実体無」でなく「読めぬ行」。検出はするが診立ての名は正しくない（label= 形の path を取らぬ）。此の札の是非は本 commit では直して居らぬ。

## 為さぬ事
共有樹の disk・HEAD・index には一指も触れて居らぬ。main へは push せぬ（代行は総監督）。

## 正規化
raw/*.err は十二本とも実走時 0byte。門 條② が 0byte を撥ねる為、一行「(stderr 0byte ―― 正規化で此の一行を置いた)」を置いた。
