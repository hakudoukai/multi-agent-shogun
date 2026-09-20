# ⑻ 條ごとの母數一覧

| 節 | 母數 | 器 | rc | 刻 |
|---|---|---|---|---|
| ⑸ 実例再現 | 1 (a1 inbox 内の該当便1通) | `git cat-file` 不要・Read/grep on queue/inbox/ashigaru-mac-1.yaml | 0 | 2026-09-21 |
| ⑹㋐ 行番号(四版) | 4 (disk/index/HEAD/main) × 4項目(Dedup開始/guard判定/id生成/type焼込) = 16セル | `git cat-file -p <blob40>` 抽出 + own grep | 0 | 2026-09-21 |
| ⑹㋑ 箱内件数 | scripts/= 6件(grep -rln)、箱4つ(a1/a2/a3/karo-mac) | own `grep -rln` / `grep -c` | 0 | 2026-09-21 |
| ⑹㋒ 上限探索 | 4版 × 1探索式 = 4セル(raw/ver_*.sh 四本走査) | own `grep -nE` | 0 | 2026-09-21 |
| ⑹㋒ 砂箱模型 | 1回(3時間=10800秒 worst-case) | 自作 `sandbox/kanjyou_sim.py`(python3) | 0 | 2026-09-21 |
| ⑹㋓ 命名 | 1 (一言) | 文章 | N/A | 2026-09-21 |
| ⑺ 提案 | 3案 | 文章(コード編集0件) | N/A | 2026-09-21 |

## 零の四つの札(該当箇所)

- ⑹㋒「counter/cooldown-on-total-cycles」の該当ヒット数=**0**(四版とも)。
  母數=4版×1探索式、器=own `grep -nE`(sandbox/03_yontsu_no_fuda_kagen_nashi.md 記載の正規表現)、
  rc=0(4回とも完遂・エラー無し)、刻=2026-09-21。
- 箱 a2/karo-mac の `msg_auto_recovery` 件数=**0**。
  母數=2箱、器=own `grep -c`(パイプを介さず直接実行)、
  rc=**1**(両箱とも ― `grep -c` は該当0件の時 rc=1 を返すのが正しい挙動であり、
  rc=0 と書けば誤りに成る。實測: `grep -c ... queue/inbox/ashigaru-mac-2.yaml` → rc=1、
  `grep -c ... queue/inbox/karo-mac.yaml` → rc=1)、刻=2026-09-21。
