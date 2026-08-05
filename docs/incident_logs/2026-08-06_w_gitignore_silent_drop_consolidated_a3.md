# .gitignore silent drop — 統合起案 (① 足軽3号本務 + ③-⑪ 足軽2号引継ぎ分)

断面: HEAD=46939a4b93c1ce12c02f243180c4cce48d7bae2c (2026-08-06T02:52:40+0900) / 測時=2026-08-05T17:56:33Z (機械)
引継ぎ元: msg_20260806_025416_861aca64 (足軽2号→足軽3号、家老second msg_20260806_025323_49a340ba 経由委任)
既存本務: karo-second msg_20260806_024648_82cb25b6 (① scripts/read_pruned_archive.sh)
提出先: 軍師second (直提出予定・下記②「委任確認未了」参照)。PASS まで commit せず。本 report は repo 外 (scratchpad)。

## 母集団 (足軽2号申告の再現・独立検算)

コマンド: `git status --porcelain --ignored=matching -- scripts/ | grep '^!!' | grep -v '\.bak' | grep -v '__pycache__'`

独立実行結果 = 足軽2号申告と★完全一致 (11件)★:
```
!! scripts/alive_to_productive_monitor_v0_2_once.sh
!! scripts/design-pipeline/design_pipeline.sh
!! scripts/design-pipeline/extract_prototype.py
!! scripts/design-pipeline/generate_mockup.py
!! scripts/karo_second_reception_check.sh   ← ② (足軽2号既報・本統合案から除外)
!! scripts/karo_second_send_iincho.sh
!! scripts/read_pruned_archive.sh            ← ① (本職既報)
!! scripts/setup_shogun_sc.sh
!! scripts/setup_shogun_standard.sh
!! scripts/shogun_self_check.sh
!! scripts/test_secondpc_monitor_v2.py
```

② `scripts/karo_second_reception_check.sh` は足軽2号が別途既報済ゆえ★本統合案には含めず★ (二重起案防止)。

## ⒜ 各 file 実測 (③-⑪、① は既報のため再掲省略)

| # | path | 行数 | sha256 | git check-ignore -v | tracked |
|---|---|---|---|---|---|
| ③ | scripts/alive_to_productive_monitor_v0_2_once.sh | 404 | e8bce96573bbbac5be899c60ea8455d0a6503165c72704f98c8b095e9970ca5d | .gitignore:7:* | 否 |
| ④ | scripts/design-pipeline/design_pipeline.sh | 106 | 29c31496300d952aef4311f25f8c129e4fd68b9e7c29e2a855367fdeb45bef76 | .gitignore:7:* | 否 |
| ⑤ | scripts/design-pipeline/extract_prototype.py | 113 | c46f084096c0bbbce1c07cdacd1f2c75cc0a4db270b47a47fe1a949b28111080 | .gitignore:7:* | 否 |
| ⑥ | scripts/design-pipeline/generate_mockup.py | 153 | 6f9890dfcce8aa739452a05f3ca13de41283ffa5cba5837b47b8a012d47de0cc | .gitignore:7:* | 否 |
| ⑦ | scripts/karo_second_send_iincho.sh | 168 | b0926ca02e88b43f06fa0fc6a740ab575fff6f69eb227924ffb94db1a6b3c867 | .gitignore:7:* | 否 |
| ⑧ | scripts/setup_shogun_sc.sh | 56 | fe1890258b3afa17dbd22d7fb4789e6d3064122c572e5c3479d3143520e25ebf | .gitignore:7:* | 否 |
| ⑨ | scripts/setup_shogun_standard.sh | 175 | a91cf7139206f7c5a4c002e5178f0b54fe8e27d3ca7a197a5989a7586a002b9a | .gitignore:7:* | 否 |
| ⑩ | scripts/shogun_self_check.sh | 34 | 5b13c964087db516b1d4a7ce2c0bb6d9fb8da9b14c210d80c9abdb6c08b21c32 | .gitignore:7:* | 否 |
| ⑪ | scripts/test_secondpc_monitor_v2.py | 229 | 81fd979ee28cb1978c16800cd824a56469763bcc6466d8a85ae5704efed15db0 | .gitignore:7:* | 否 |

全9件、①同様に .gitignore:7 の全除外 `*` (Step1) に捕捉。個別 whitelist 行は無し。全て `git ls-files` 空=untracked。

**secret 走査 (手動 12-pattern grep・専用 scanner 代替に非ず、00E 先例と同じ限界を継承)**:
- 7件=0 hits。
- ⑦ karo_second_send_iincho.sh = 3 hits、内容は `SUPABASE_URL`/`SUPABASE_SERVICE_ROLE_KEY` の★変数名参照とunset時のfatal文言のみ★ (リテラル値の埋め込み無し)。
- ⑨ setup_shogun_standard.sh = 3 hits、内容は `SERVICE_ROLE_KEY` の★継承コメント + Doppler 経由の rotation key script 呼出しパスの変数名★のみ (リテラル値の埋め込み無し)。
- ★これは目視の当たりであって専用走査の代替にならない (00E 先例の教訓を継承・断定しない)★。

## ⒝ 統合 `!` 起案 (逐語・末尾へ append・.gitignore は不触・委員長裁可待ち)

```
!scripts/read_pruned_archive.sh
!scripts/alive_to_productive_monitor_v0_2_once.sh
!scripts/design-pipeline/design_pipeline.sh
!scripts/design-pipeline/extract_prototype.py
!scripts/design-pipeline/generate_mockup.py
!scripts/karo_second_send_iincho.sh
!scripts/setup_shogun_sc.sh
!scripts/setup_shogun_standard.sh
!scripts/shogun_self_check.sh
!scripts/test_secondpc_monitor_v2.py
```

(② karo_second_reception_check.sh は含めない — 足軽2号の既報ラインで別途起案される想定。同一 file を二経路で起案しない。)

## ⒞ 隔離 clone 差分法 (10行まとめて再実測)

- 適用前 (隔離 clone): 426行・sha256=`b99f6401d865d51a74ee569559887e3ad1233f48bba1ce9855cab4843383745d`・git ls-files=621
  (★ライブ repo 側は本作業中に足軽6号 commit 46939a4 が入り HEAD が進んだが、.gitignore 自体の sha256 は不変のまま★=`b99f6401...`。断面が動いた事と .gitignore が動いていない事は別、と明記する)。
- 統合10行 append 後: 436行・sha256=`cb04220acb2ee680d271590c134ec39b5082f88afb34eff16032b45dce9e7bee`
- 10 file 全てで `git check-ignore -q` 終了コード = `1` (=狙い通り無視解除)
- `git add -n scripts/` (file 不在の新規clone状態) → 0行 = 巻き込み無し
- 実 file 10件を複製へコピー入れた後の `git add -n scripts/` → ★出力ちょうど10行、対象10 file と完全一致・他 file 無し★
- ★ライブ repo 側 .gitignore は本作業を通じて一字も変えていない★ (実測後 sha256 再確認=`b99f6401...`、不変)。
- 隔離 clone 2件目 (`isolated_clone_consolidated`) の削除 = 1件目同様 `rm -rf` が harness 権限拒否・scratchpad 内残置 (非repo・実害無しと判断・削除完了とは書かず)。

結論: 統合10行の副作用スコープ = 対象10 file のみ・巻き込み 0件 (① 単独の時と同じ形の結果)。

## ⒟ この修正が新たに開ける穴 (① 既報分に追加)

1. (① 既報と同型) unignore ≠ tracked の二段階混同リスクは 10 file 全てに等しく当てはまる。
2. secret 走査未実施は 10 file 全てに等しく当てはまる (上記手動grep 3件ヒットは変数名のみと確認済だが、専用走査の代替にならない旨は変わらず)。
3. **★統合固有の新穴★**: 10 file を一括 `!` append する提案ゆえ、実際に commit する段になった際「1 file だけ査読漏れ」が起き得る (レビューが 1 file 単位でなく 10 file 一括になりがちなため)。00E 先例は 3 file の一括 append だったが、査読は各 file 個別に sha256 突合されていた。★本統合案も 10 file 個別の sha256 突合を維持しており (上表)、この穴は表の形で予防済★。
4. ② (karo_second_reception_check.sh) を意図的に除外している。もし足軽2号の別ラインでの起案が遅延・見送りされた場合、②だけが「誰の起案にも乗らない」まま宙に浮くリスクがある。★本職からは②の状況を確認できない (足軽2号の担当範囲)★。

## 委任確認の未了点 (裁定せず・明示のみ)

家老second からの直接指示メッセージは本職の inbox に届いていない (足軽2号経由の伝聞のみ)。★家老second msg_20260806_025323_49a340ba の内容そのものは本職未読★。ゆえに:
- 本統合案は「足軽2号の伝聞 + 独立検算で内容一致」を根拠に起草した。
- ★家老second 本人からの直接確認 (委任の事実・軍師second への提出ルート指定) は未取得★。
- 軍師second への提出前に、家老second 宛にも本統合案の写しを送り、委任内容の確認を仰ぐ。

## 禁則順守の申告

- `.gitignore` は一字も編んでいない (統合提案も隔離 clone 内のみで検証・sha256 で証明)。
- 対象10 file (実装) は一字も編んでいない。
- commit / push / stage は行っていない。
- 隔離 clone 2件の削除が未了 (harness 権限拒否・repo 外・実害無し)。

## 【本工区で己が直した誤り】
無し。

## 【この工区と対に成る他工区】
② scripts/karo_second_reception_check.sh (足軽2号 既報・別ライン起案想定・本職では追跡不能)。

## 追記 (2026-08-06T02:56:20 家老second msg_20260806_025620_e8cf34cb 受領後)

★上記「委任確認の未了点」節は解消★= 家老second が「同人(足軽2号)へは貴殿へ直に渡すよう伝え済」と明示。委任の事実は確認済に成った。
併せて本 file 自体の置き場も scratchpad → `docs/incident_logs/` へ移設 (家老second 指示・足軽1号 本日同型 FAIL の教訓反映)。中身 (本文) は元 scratchpad 版から一字も変えていない (本追記節のみ末尾追加)。
