# 審査順の直し ―― 証の目録 (board 12674e7c ㊀)

裁: 総監督 seq339911「㊀審査順の直し=GO（自枝で commit→PR。共有樹・main直pushは禁のまま）」
作りたる者: 家老second。★本 dir の物は悉く己の手が作りたる物に御座り、他席の証を含み申さぬ。★

## 一. 疵 ―― 「在れど遅し」

`DOWNLINK_OWNED_TARGETS`（gunshi-second / honbucho / dr-s）を避くる検めは★既に在りたり★。
併し其れは標準便の枝の中、`is_same_agent_send` の後に置かれ居りたり。
`is_same_agent_send` は送り手の名が context_data に無き時 ★True を返す（fail-closed）★。
∴ 封筒を持たぬ honbucho 宛の行は、己を守る筈の検めへ届く前に dead-letter せられ居りたり。

★在るか否かではなく、何れが先に裁くかが疵に御座りたる。★

## 二. 直し (15行増 6行減・器一本のみ)

`detect_target` による所有の裁きを `is_same_agent_send` より★前★へ移したり。
file_sync の枝は `is_file_sync` にて明に除く ―― file_sync の振舞ひは一字も変へ居り申さぬ。
旧き位置の検めは到達し得ざる死条となるゆゑ取り除き、其の旨を註に残したり。

## 三. 証

| 物 | sha256 | 丈 | 行 |
|---|---|---|---|
| raw/order_proof_20260920_021353.txt | 13859921…9284686e | 3241B | 59行 |
| artifact/receiver_poll.pre-order-fix.frozen | 190638e4…f116bc95 | — | 615行 |
| (直し後 器 作業樹) | 02801104…f882f6e5d0 | — | 624行 |

生証跡には cwd・host・枝・HEAD・python/pytest の版・argv・rc・各段の sha を記したり。

## 四. 対照 (軍師second第⑤軸への答)

- ★陽性対照★: 直し前の器へ戻して同じ試しを撃ちたるに `test_envelopeless_downlink_row_is_not_dead_lettered` ★のみ★ 落ちたり (rc=1)。
  即ち此の試しは疵を見て居る。残る3本は直し前にても通るゆゑ ★疵の検知手に非ず、振舞ひの保存を縛る条に御座る★。
- ★陰性対照 其一★: `test_negative_control_ordinary_target_still_dead_letters` ―― ashigaru1 宛の同形の行は今も dead-letter せらる。囲ひが広がり居らぬ証。
- ★陰性対照 其二★: `test_negative_control_file_sync_is_not_captured_by_the_guard` ―― honbucho 宛の file_sync は今も file を書く。
- ★他席の書きたる陰性対照★: `tests/test_watcher_hotfix.py::TestSecondpcReceiverRetry::test_self_send_detection` ―― 己の作に非ざる試しが、直し後も通る。

## 五. 回帰 (直し前後を同じ器で測りたり)

env `SUPABASE_SERVICE_ROLE_KEY=fake_key` を与へ、`tests/migrations/test_organizational_lessons_rls.py` 1本のみ除きたる全体:

- 直し前: 24 failed / 109 passed
- 直し後: 24 failed / 113 passed (+4 = 己の新しき試し 4本)
- ★落ちの集合は前後で完全に同じ（comm にて差 0）。己は一本も増やさず、一本も消し申さぬ。★

## 六. 己の欠 ―― 軍師second の判を仰ぐ前に自ら申す

1. ★bats 無し★。`tests/unit/*.bats` 15本は撃ち得ず (`command -v bats` = 無、`find / -maxdepth 4` にても無)。己の直しは python 一本ゆゑ影響は無しと★推★するが、★測り居らぬ★。
2. ★pgserver 無し★。`tests/migrations/test_organizational_lessons_rls.py` は import にて落つるゆゑ除外したり。己の直しと無縁と★推★す。
3. ★既存の赤 24本は直し居り申さぬ★。前後同一ゆゑ己の責に非ずと見るが、★緑に非ず★。
4. ★実機にて撃ち居り申さぬ★。稼働 receiver は HEAD/main/自枝の何れにも固定されぬ disk の生 file に御座り (事業部長 01:44 実測)、之を差し替ふるは共有機構の変更ゆゑ撃たず。
   ∴ 本証は ★試し器の上の緑★ であり、★実機の緑に非ず★。
5. ★lockfile・外部依存の測りは未だし★ (軍師second 第④軸)。

## 七. 後の者への註 (此の樹の罠)

`.gitignore` の7行目は裸の `*` に御座る。即ち★白名方式★にて、`!` の行に載らぬ物は悉く無視せらる。
`docs/evidence/` の白名は無し。∴ ★此の dir へ紙を置いても `git status` は黙る。`git add -f` を要する。★
実際、本証を作りたる時の `git status --porcelain` は2行しか吐かず、生れたばかりの本 dir を★一行も示さざりき★ (生証跡 ⑤節に其の儘残したり)。

## 八. 訂 ―― 生証跡 L6 の末尾空白を正規化したり (軍師second REVISE ④ artifact衛生 復命)

**★三節の表は消さず、下に訂を継ぐ（旧値も後の者が検め得る様に）。★**

軍師second の指摘（逐語）:
「fixed raw/order_proof_20260920_021353.txt:L6に末尾SPがありgit diff --check RC2。rawを正規化・再hashして固定束を再提出。」

己の器にて**完全に再現したり**:

```
$ git show --check 6fbe7981 -- docs/evidence/receiver-order-20260920/raw/order_proof_20260920_021353.txt
docs/evidence/receiver-order-20260920/raw/order_proof_20260920_021353.txt:6: trailing whitespace.
rc=2
```

当該行は `python=Python 3.12.3 (main, Aug 31 2026, 10:18:26) [GCC 13.3.0] ` ――
末尾の空白一つは `python -VV` 系の吐きたる**生の出力の一部**に御座る。

∴ **★正規化はするが、捕獲の由緒は殺さぬ★** ―― 前像の sha を此処に刻み、変じたるを一字まで示す。

| | sha256 | 丈 | 行 |
|---|---|---|---|
| raw **前像**（正規化前・commit 6fbe7981 の儘） | `138599210df0be863640817f81249cd858ba587fbd3e697394f569959284686e` | 3241B | 59行 |
| raw **後像**（正規化後・本 commit） | `bb70c026c8fd8018983642702b1e2eae218443e55726ad7568f13fb20d6f5097` | 3240B | 59行 |

**変じたるは 6行目 末尾の空白 一つ のみ。行数不変（59行）・丈 -1B・`git diff --numstat` は `1 1`。**
正規化後の `git diff --check` は **rc=0**。

束の他四紙（manifest 己・frozen 前像・試験・受信機）の末尾空白は**悉く零**にて、手は入れ居り申さぬ。

**★骨★: 捕獲せし生証跡を後より整へる時は、整へたる事と★前像の sha★を同じ紙に刻め。
刻まざれば、其れは最早「捕獲」に非ず「作文」に御座る。**
