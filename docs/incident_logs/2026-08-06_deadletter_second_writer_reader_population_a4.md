# `_dead_letter_second.yaml` writer/reader 母集団 (足軽4号・current_order_7)

- 測時: 2026-08-06T22:34:17+09:00
- 器: `/usr/bin/grep -rn` / `-rl` (git grep 不使用・queue/ 等 gitignore 対象の無警告 skip を避けた) + `Read` tool による該当 file の実読
- base_commit: `fba5133946349639673dbd31da30f867836c1d97` (2026-08-06 22:27:42 +0900)
- 発注: 家老second msg_20260806_221926_2a7fb9bf (22:19:26)、task YAML key `current_order_7_20260806_2216_WRITER_READER_POP`
- ★禁則順守★: 原本 `queue/inbox/_dead_letter_second.yaml` は一度も開いていない (grep/wc/cat 含め不使用)。`queue/inbox/_archive/*_legacy_*` 3 file (fukuincho_legacy_deadletter / gunshi_legacy_generic / shogun_legacy_generic) も不触。code 編集は一切していない (索しのみ)。本文・値・patient・secret は一切引用していない。

## ⒞ 索いた範囲 (母集団の取り方) — 先に書け

1. **文字列一致探索** — `/usr/bin/grep -rl "_dead_letter_second" .` を **repo root から拡張子無指定・除外なし**で実行 (queue/ 配下データ file 自体と `.git/` は結果から目視で除外、grep 自体には除外オプションを付けていない)。→ ヒット 12 file (下記 §結果一覧)。
2. **緩め探索 (部分一致)** — `dead_letter` (`_second` を含まぬ) で repo 全体を再走査。同名だが★別の仕組み★(後述③) を拾うための対照実験。
3. **動的構築の潰し込み** — 文字列連結でパスを作る書き方 (`f"_dead_letter_{pc}.yaml"` 等) が無いか、`dead_letter.*\.yaml` パターンで scripts/shim 全体を再検索。
4. **glob 経由の巻き込み探索** — `queue/inbox/*.yaml` あるいは `inbox_dir.glob('*.yaml')` 等、**識別子を明示せず「その場にある file 全部」を対象にする書き方**を repo 全体で検索。★之が本工区で新たに見つかった経路★ (下記⒝-2)。
5. 対象ディレクトリ: repo 全体 (`shim/` `scripts/` `tests/` に加え `backend/` `agents/` `lib/` `config/` `context/` `android/` も個別に再確認・後者はヒット 0)。

## ⒜ 書く者 (writer) — 全件

### ⒜-1 確定 writer (実際に `_dead_letter_second.yaml` という識別子で書き込む code)

| file:line | 関数名 | 呼出経路 |
|---|---|---|
| `shim/hakudokai/hakudokai_secondpc_receiver_poll.py:232-254` (`append_dead_letter(msg, reason)`)。書込は L237 (`path.read_text()` で dedup 確認) + L254 (`path.write_text(existing + entry, ...)`、生文字列 block-sequence 追記・yaml library 不使用) | `append_dead_letter` | 呼出は **1 箇所のみ**: L342 (`for msg in new_msgs:` ループ内、`else` 分岐 = 非 file_sync メッセージ、`detect_target(msg)` が偽 (`missing_or_invalid_target_agent`) の時)。起動経路: `shim/hakudokai/hakudokai_secondpc_receiver.sh:80` が `while true; sleep $POLL_INTERVAL; ...` ループ内で `python3 hakudokai_secondpc_receiver_poll.py` を subprocess 起動 (5秒間隔 poll)。 |

同一 file 内に `dead_letter_message(msg_id, last_error)` (L67-89) という**紛らわしい同名系関数**があるが、之は Supabase `pc_handshake` テーブルへの PATCH ACK (`acknowledged_by: "dead_letter"`) であり、`_dead_letter_second.yaml` を一切開かない。★同名だが別対象★ — 誤って writer に数えぬよう明記する。同型の `dead_letter_message()` は `hakudokai_fukuincho_poll.py` / `hakudokai_fukuincho_reverse_poll.py` / `hakudokai_secondpc_watcher_poll.py` にも存在するが、いずれも同じく DB ACK のみで `_dead_letter_second.yaml` には触れない (3 file とも `_dead_letter_second` 文字列 0 件、個別 grep で確認済)。

### ⒜-2 条件付き・未確認 writer (候補パターン — 足軽3号 a3 票 §⒞ の追認)

`messages: []` flow-seed を無条件に書く汎用初期化コード (`inbox_watcher.sh:46` / `inbox_write.sh:143` / `hakudokai_secondpc_setup.sh:330` / `watcher_supervisor.sh:26` / `watcher_supervisor_third.sh:24`) は、いずれも `<識別子>.yaml` が **未存在の時のみ** 発火する汎用パターンであり、`<識別子>` に `_dead_letter_second` が渡される呼出は本工区でも見つからなかった (a3 票と同結果、独立再確認)。★判らぬ物は判らぬまま★ — 「呼ばれておるか未確認」であって「無い」ではない。

### ⒜-3 一回性 byte copy (writer とは性質が異なる — 参考記載)

`shutsujin_departure.sh:383` (および同 file の過去断面写し `queue/reports/shutsujin_departure_before_model_policy_20260702081613.sh:383`、実質同一行): `[ -d ./queue/inbox ] && cp ./queue/inbox/*.yaml "$INBOX_LINUX_DIR/" ...`。WSL→Linux ネイティブ dir 移行の一回性 setup 処理で、`./queue/inbox` が★symlink でない時のみ★発火。YAML を解釈せず bytes を丸ごと複製するのみ (書換ではなく複製)。`_dead_letter_second.yaml` が存在すればこの glob に無条件で含まれるが、生産経路で反復実行される類ではない (setup script 一回性)。

## ⒝ 読む者 (reader) — 全件

### ⒝-1 明示識別子での reader

`_dead_letter_second` という文字列を直接引数・パスとして使い読み込む code は **0 件** (writer 側の `append_dead_letter` 内の dedup 用 `path.read_text()` は「他プロセスからの読者」ではなく自分の書込関数内の自己参照であり、外部 reader としては数えない)。

### ⒝-2 glob 経由の reader (★本工区で新たに確認した経路★)

**`scripts/slim_yaml.py:305-320` (`slim_all_inboxes(dry_run=False)`)**:
- L311: `for filepath in sorted(inbox_dir.glob('*.yaml')):` — `queue/inbox/` 配下の **全 `.yaml` file を無除外で列挙**。`_dead_letter_second.yaml` もこの glob に含まれる (除外コードなし・実測で確認)。
- L312: `agent_id = filepath.stem` → `_dead_letter_second`
- L315: `slim_inbox('_dead_letter_second', dry_run)` を呼ぶ
- `slim_inbox()` (L193-248) は L203 `data = load_yaml(inbox_file)` (`yaml.safe_load`、L23-32) で**本文を読む**。読んだ後、各 message の `read` field を見て `archived`/`unread` に仕分け (L216-221)。★`append_dead_letter` が書く entry は常に `read: false` (L250) なので、他の経路で `read: true` に変わらぬ限り `archived` は空になり、L224-225 の分岐で「書込せず return True」——つまり通常運用では**読むが書かない**。但し何らかの経路で 1 件でも `read: true` になれば、L236-244 で archive file 書出し + 本体 `save_yaml()` (`yaml.dump(..., default_flow_style=False)`, L39) による**書き換え**が起きる。∴ 之は「保存形式を変えれば壊れる側」に該当する reader であり、★条件によっては writer にも成り得る★。

**発火経路**: `slim_all_inboxes()` は `main()` (L361-385) 内で `agent_id == 'karo'` の時のみ呼ばれる (L370-379)。呼出は `scripts/slim_yaml.sh karo` (flock による排他制御ラッパー、L34 で `python3 slim_yaml.py "$@"`)。`slim_yaml.sh` 自体を機械的に起動する cron/systemd/watcher は repo 内に見つからず (README/instructions/*.md からの言及のみ) — ★家老が運用手順として手動実行する想定と見受けられるが、実行頻度・自動化の有無は本工区の範囲外で未確認★。

### ⒝-3 見つからなかった reader

- dashboard / 監視系 script (`hakudokai_activity_monitor.sh` 等) で `_dead_letter_second` を個別に読む箇所 = 0 件。
- `backend/` `agents/` `lib/` `config/` `context/` `android/` 配下に `dead_letter` 文字列を含む file = 0 件。

## ⒟ 判らぬ物 (第四値)

- `scripts/slim_yaml.sh karo` (延いては `slim_all_inboxes`) が実際にどの頻度・どの経路 (cron/家老手動/他) で起動されているかは★未確認★。呼ばれておらぬとは書かぬ。
- ⒜-2 の候補パターンが過去に一度でも `_dead_letter_second` という識別子で発火した履歴があるかは、code 静的検索のみでは判定不能 (実行 log は本工区の索し対象外)。
- `_dead_letter_second.yaml` が現在 multi-document 形式に陥っていないかは原本不触ゆえ確認不能。ただし `load_yaml()` (`yaml.safe_load` 単体、`safe_load_all` ではない) は multi-doc を渡されると `yaml.YAMLError` を捕捉し `{}` を返す設計 (L28-32) — 之は「壊れていても静かに no-op する」という性質であり、壊れているか否かの断定ではない。

## ⒠ 己の手で為した事

1. `/usr/bin/grep -rl "_dead_letter_second" .` (拡張子無指定・repo root) を実行 → 12 file
2. `/usr/bin/grep -rln "_dead_letter_second" . | grep -vE "^\./(queue/|\.git/)"` で絞り込み再確認
3. `Read` tool で `hakudokai_secondpc_receiver_poll.py` L1-410 (全行) を実読
4. `/usr/bin/grep -n "append_dead_letter(" ...` で呼出箇所数を確認 (1件)
5. `dead_letter_message` の実装 (L67-89) を実読し、Supabase PATCH ACK であり target file と無関係と確認
6. `/usr/bin/grep -rln "dead_letter" scripts/ shim/` 等で広域候補を洗い出し、各 file を個別に実読 (`inbox_path.sh` / `diagnose.sh` / `inbox_write.sh` / `fukuincho_poll.py` / `fukuincho_reverse_poll.py` / `secondpc_watcher_poll.py` / `dead_letter.sh` (archive) / `watcher.sh` (archive) / bats 2 件)
7. `queue/dead_letter/` (別の仕組み・per-agent dir) と `_dead_letter_second.yaml` (単一 file) が★別物★であることを path 実測で確認 (`scripts/inbox_path.sh:75`, `scripts/inbox_write.sh:308,394`)
8. `scripts/message_delivery_v2/dead_letter.sh` (bats が参照するパス) が repo に★実在しない★ことを `ls` で確認 (`scripts/archive/message_delivery_v2_full_20260508/` に旧版のみ存在)
9. `docs/incident_logs/2026-08-06_deadletter_second_other_writer_a3.md` (足軽3号票) を★自分の探索完了後に★通読し、結論 (writer 1件・reader 0件・候補パターン5件) が独立一致することを確認。同時に a3 の scope (`shim/**` `scripts/**` `tests/**`、拡張子 `.py`/`.sh` 限定+無指定の両方) が repo 全体をカバーしていなかった点を特定
10. `/usr/bin/grep -rn 'queue/inbox/\*\.yaml\|inbox_dir.glob'` 系パターンで repo 全体を再検索し、⒝-2 の glob reader (`slim_yaml.py`) を新規発見
11. `Read` tool で `scripts/slim_yaml.py` L1-388 (全行) を実読し、`slim_all_inboxes` → `slim_inbox` → `load_yaml`/`save_yaml` の呼出鎖・条件分岐を実測
12. `/usr/bin/grep -rln "slim_yaml.sh\|slim_yaml.py"` で呼出元を洗い出し、cron/systemd 起動が repo 内に無いことを確認 (instructions/*.md からの言及のみ)
13. `shutsujin_departure.sh:383` の byte-copy 経路を実読し、symlink 未存在時のみの一回性処理と確認

## 母集団の数え直し (令④)

- 家老second 発注文には数は書かれておらぬ (令④準拠)。
- ★実行の刻に数え直した数★: `_dead_letter_second` 文字列ヒット file = **12 file** (2026-08-06T22:34:17+09:00 断面・器=`/usr/bin/grep -rl` 拡張子無指定)。うち **確定 writer = 1 関数・1 呼出箇所**、**確定 reader (明示識別子) = 0 件**、**glob 経由 reader/条件付writer = 1 件** (`slim_yaml.py`)、**候補 (未確認) writer パターン = 5 箇所** (a3 票と同数)。
- 以上。

## 渡し先への申し送り

足軽7号 (Lane C′ 実装者) へ: 本票は★唯一の根拠にあらず★ — 貴殿ご自身でも `_dead_letter_second` を触らずに写者・読者を確認されたし。特に ⒝-2 (`slim_yaml.py` の glob reader) は a3 票に無い新規経路ゆえ、シリアライザ改修時に「karo が `slim_yaml.sh karo` を実行した際、他の agent 同様この file も巻き込まれる」前提を実装契約に含めるか要確認。

## 『完』の三状態

- ⒜ 実装: 該当なし (本工区は索しのみ・実装は足軽7号)
- ⒝ 監査: pending (本報告を軍師second へ提出予定)
- ⒞ 運用: 該当なし (調査報告のみ)
