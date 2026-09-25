# 赤本R8 残り24頁 ―― 原画像を目視で書き起こした(板 9a50be63 / goal board dr-m-remaining24-vision-recheck-230273af)

担当: ashigaru-mac-2(專任2) ／ 発注: goal file 2026-09-25 12:49 gakushu-bucho(総監督許可 seq372454)＋監督の下命「頁ごとに印字の頁番号と本文を書き起こせ・推測で埋めるな」

## 0. 結論

1. ★対象24頁の24/24で、原画像を私がファイル読込で開き、印字の頁番号と本文を書き起こした★(`pages/pNNNN.md`・1頁1file)。
   - 読めずに推測で埋めた頁は0。本文に採るか否かは ★ドクターM が決める★。私は採否を判じて居らぬ。
   - 字の確からしさに疑いが残った所は、各頁の「読めなかった所・註」に書いた。★確信を持てぬ★と書いた所は3頁ある(p0440・p0450・p0493。いずれも歯式の横線が上か下か)。
2. 印字の頁番号は、表紙(1)と広告(2)が無し。351〜495 の22頁は、いずれも ★画像の頁番号−142★ に当たった(209〜353)。
3. 画像の同一性(`raw/02_image_table.tsv`・rc=0):
   - JSONL の `image_sha256` は、入力A・B とも 24/24 で `/Users/momizimac/akahon-r8/.evidence-370771/images/pNNNN.png`(900x1276)の disk sha256 と一致した。★A と B が指す画像は同じ★である。
   - 私が書き起こしに使ったのは原寸の `/Users/momizimac/akahon-r8/out/akahon/png/赤本R8_pNNNN.png`(1638x2323)。sha256 は JSONL と ★0/24 一致★する。縮小して描き直した版だからである。表には両方の path と sha256 を並べた。
   - 此の数が言わぬ事: 900x1276 の方が原寸の縮小版だという見立ては、寸法の比と目で見た内容から来ている。画素の比較はして居らぬ。
4. 入力の JSONL(`raw/01_inputs.txt`):
   - A = `remaining24-vision-recheck.jsonl` sha256 12f7d41b…ee1f、24行。
   - B = `remaining24-vision.jsonl` sha256 695dad25…7191、24行。
   - sha256 は2本とも goal file の値と一致した。★両方を保持し、どちらを主にするかはドクターM が決める★。
   - goal file に書かれた commit 230273af… と 64b60120… は、multi-agent-shogun の repo では ★2本とも object として無い★(rc=128・`raw/03_input_commits.txt`)。
   - JSONL の `vision_text` は候補であり、結果として転記して居らぬ。書き起こしは画像から直に書いた。

## 1. 24頁の表(path は下の §2)

| 頁 | 印字の頁番号 | 頁の種類 | 原画像(書き起こしに使った) sha256 | JSONL の画像 sha256 |
|---|---|---|---|---|
| 1 | 無し | 表紙 | `6faefadcaf8a16d6df3aca3efa1f903bdcf78bcc20793a55a63cec3f52222ca7` | `f9c40683b87d3e1d57437d9d659cf633150f7f9ee3c3ab913739f35e4a8eccc6` |
| 2 | 無し | 広告 | `9d70981a83726829c65da491ff6423e1a71b8f4073f38ea5802a90fc88a0fbcd` | `88a44cdb42493e60c266d08e7ca7ead9914c826e0de976f65d4c33a7650bd45f` |
| 351 | 209 | 本文 | `5b7e10fa9190c9ca41effa05e0acb8530e19c994af62c2f4bc6542aa3d0f850a` | `d86e7eea5dd1dbb9105f141dd8300034358f421b2f1ceb138b1ab1f5dd920e5d` |
| 353 | 211 | 本文 | `7f8145271ee6dfbf268843f8bfe33667267785dfa09a2b03b3a3fcb4ed527f8b` | `604d108940effb02fa01e9261fcad2a14a4c2a0439daae48952b8732d38737a1` |
| 355 | 213 | 表 | `f11e8e0e120568e2c3fc2ac721363c6d730ca6e2aeccef18eb36c6f65455eb0b` | `29dd407d1c43d2bbe6c111d39d077294242c778b64529b94c411624ea06b601a` |
| 357 | 215 | 本文 | `e1c537d753da8fe6eec04e5cc25c97eb52bb87c3ed3a0a1708935e445cf7add4` | `c44b2591f4d29f844540458f46b8af619b65a11185a3da53ae78f5a5c12407d4` |
| 409 | 267 | 参考資料 | `67a86814a9e6324003d0dd193c47afc02fa5953fa92fac51dd0e7dea5e09d888` | `2b06cb192842a4b9a282c6a0ef0f46f439a58e0bce27283e3302da820a5a49c6` |
| 411 | 269 | 本文 | `24ed307d04820c75556b8eb6666ddd8be146f50c610b2e74c79100cb92ea4b6b` | `2dafac58ba71946ae852aa3e7e5bff3da93169c74ba29f0ef4f03648ff40f3dd` |
| 413 | 271 | 本文 | `491e3b92137a22102196f25f5f4b49617511fa6ec2c99e4e4b0f81a1966bf01b` | `31bd38f10bb01070176ef3c6b29c8fd2ef5d80d3871f57c4384bb28693ee3ddf` |
| 427 | 285 | 章扉を兼ねた本文 | `7cb5b37c9ac0caf33007730136861f49fe597a04160dcf85acda5bd565e78dcc` | `97b28fb006a51b75742f2798a7e6aed458ce99af49423daa148c1de18325ebf7` |
| 429 | 287 | 症例頁 | `443b41bb8dc1233cb4aae91af350a357a004d8d85ce375b62072a54fbd10e7d4` | `9c2c35f2a2006dbd06a31a719f03d6a3a25d7ac0ffebec7cc8201363402a8be9` |
| 433 | 291 | 症例頁 | `c63b5f4ae2c8858e1e315f23249858782ecb3816f842956cde9c4eed2dbd5bde` | `b79304d09b867fa1bfaa26085f86cc4394df56d5582b5155fea64dfbe949ecd1` |
| 437 | 295 | 本文 | `92b6499853d48b4b00c98461dce277a06e2204ba9f964da6e4cfc8ea5804cdbd` | `390876733565b2ff3473d0364df76b8a94b4caf430275d0a2957d51432e43567` |
| 440 | 298 | 表 | `cae7406d02571efde33e33fec22bac5645d9469ea01c5cbf9624deca399bf2bb` | `a5ea382d33502864c19e637dd7b91de76404f0200ac212f7e2cf9c649df63266` |
| 443 | 301 | 本文2段組 | `c441a9e0069f68ebc5afc80de14b7c1ad25b14bd5bbcf347eaaefed1246cb138` | `476074afbad95bf0ae4cc9f799bea113d255b849ef16342b8ca15b5302f24a33` |
| 450 | 308 | 症例 | `cfb2de8b0fc8583a8e948b3c822867d0f13fab61bf9bf176dba04217e9ddd43a` | `f2d6639bf44d9ce6adc577ce73a55763169d9912f3b36cc4b4660f3647c102d2` |
| 481 | 339 | 本文2段組＋表＋図 | `3384ea52d022a4a033e129116093d41720b3d3aa9eb280b17406fb168e5e8521` | `d3558a0e1d25e8def5507e4eca2b53e82251366c21fde7894f52d93f7a89f3c6` |
| 483 | 341 | 図＋本文2段組 | `8d1905199b690fb36969cde269e3e05057d26fc46e6a6c2d45f6b42a213b7b35` | `7b2444c558af88fac1bed26dcc813c03f9b1496e06cc92b9942af1f87ad04d98` |
| 485 | 343 | 本文2段組＋表＋例示枠 | `56be4f1d4b94dca322df62356d5bb591fabe451e3f8e41ba7dda2d106733d75a` | `a29bc21338505ebecadccd1c8a2fdb182a0e27d2a076a7a88d238638ce301730` |
| 489 | 347 | 本文2段組 | `30a2b82bf1c825a7f0e724bb67b8ba03c5a649c19a372efaea825b26e43ee21e` | `6753d883c57a093275dc9d5d1339e32b801de07a2ac66635d307706902a3779e` |
| 491 | 349 | 症例 | `a9efaf8cc3e427792c255e0ca9fd0275551df60430d74efa1a5294909e0477bb` | `a1807440a7516e2cd9a1528214741d93eaa6e43f083a8cc8ef128ff74d404948` |
| 493 | 351 | 症例 | `71b4fc898e6170bdcd4762b6ca6891ac3a347f106316e9e9a0d20723770950be` | `088202043cff09a5f64771433ebf40cc668404096b4bb6481531f63211aa8513` |
| 494 | 352 | 本文2段組 | `44c4a83555e7af91684ed8480583777595001cdfaa4bb7a5e5f60c1afc6fef81` | `f0594f13ebfd0faf9bbc66ea5ee9e5340790aef2b0646e7aa12bcb25a14e9e69` |
| 495 | 353 | 章扉見出し＋本文2段組 | `fb7368deb4f28993e6aca0dbe457a071c714341506079e579c975fea57398f25` | `4b0c8523e33c13b029c5cfa1051acf5eeee766b7f58a96b176023a25f49869d6` |

## 2. path

- 原画像(書き起こしに使った・1638x2323): `/Users/momizimac/akahon-r8/out/akahon/png/赤本R8_pNNNN.png`
- JSONL の画像(900x1276): `/Users/momizimac/akahon-r8/.evidence-370771/images/pNNNN.png`
- 全ての欄(寸法、A==disk、B==disk、orig==jsonl): `raw/02_image_table.tsv`

## 3. 書き起こしの約束(全頁共通)

- 右端の索引帯(A〜K の章名)と、裏写りらしい薄い字は書き起こして居らぬ。
- 図は、枠の中の字をそのまま並べた。図の形は書き起こして居らぬ。
- 歯式は `[歯式]` と書き、縦線・横線の位置を註に書いた。★どの象限を指すかは判じて居らぬ★。
- 丸付き数字のうち、赤丸や黒丸の見出し番号は `(N)` と書いた。①などの丸数字は原本の字のまま。
- 誤植らしい字も、印字のまま写した(例: p0357「標傍時間外」)。
- 合計点の検算はして居らぬ。
- `〃`・` / `・列名の補いなど、私が書き足した区切りは、各頁の註で明かした。

## 4. 限界

- 採否を判じて居らぬ。JSONL の候補との照合結果を「正/誤」と出しても居らぬ。本文の採否はドクターM が決める。
- 読んだのは1回きり(私1人の目)である。独立したもう1人の目の読みは経て居らぬ。

## 5. 触れた物・触れぬ物

- 書いたのは本束だけ(自席の worktree `/Users/momizimac/wt/a2-akahon-rem24`、枝 `ashigaru-mac-2/akahon-r8-rem24-20260925`)。
- 原画像、JSONL、DB、患者記録、歯式6file、design tokens、本番、secret はいずれも不変。有償 API は使って居らぬ。
