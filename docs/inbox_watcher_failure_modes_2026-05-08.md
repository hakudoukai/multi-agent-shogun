# inbox_watcher 反省点徹底抽出 — Phase 0 報告書

> 起案: 信長 (織田信長 / shogun)
> 日時: 2026-05-08 17:18 JST
> 命令:
>   - 理事長殿御命令『inbox_watcher 問題多すぎ。ゼロベース再設計し家康監査再修正の PDCA で改善した新システムに入れ換え』(2026-05-08 17:00)
>   - 理事長殿御命令『今回のゼロベース watcher 最優先で』(2026-05-08 17:08)
>   - 理事長殿御命令『信長と家康のみで進めよ。他は全停止で』(2026-05-08 17:18)
> 対象 cmd: cmd_inbox_watcher_zerobase_redesign_001 Phase 0
> 監査依頼先: 家康 (ieyasu, Codex Pro) — 唯一稼働中の家臣
> F001 一時 lift: 理事長殿明示直命により家臣群停止中、信長が直接執筆
> 形式: 各項目を (現状 / 真因 / 設計要件 / 検証方法) の 4 列で記録

## 0. 状況

本日 16:43-17:14 の 30 分間で inbox_watcher.sh が **3 度全死亡** (各 ~13 分 / 13 分 / 1 分)。
家老 (秀吉) への発令が配達不能、家臣群が完全停止に至った。
理事長殿明示直命により他家臣を全停止、信長 + 家康のみで本 Phase 0 を遂行する。

唯一稼働中の家康 (ieyasu, Codex Pro) は本日 16:00-17:00 にも `bash bulk_ack.sh` 固着で 40 分停止、信長緊急介入で復旧した経緯あり (= 反省点 t に統合)。

## 1. 反省点 23 項目 (a〜w)

### a) silent death — watcher 6 本が 13 分以下で全停止

| 列 | 内容 |
|---|---|
| 現状 | 16:43 起動 → 16:55 全停止 (12 分)、17:00 起動 → 17:13 全停止 (13 分)、17:13 起動 → 17:14 全停止 (1 分)。プロセス痕跡なし、ログ末尾は wake-up nudge 直後で停止。 |
| 真因 (5 Why) | 1st: watcher プロセスが意図せず終了。2nd: bash subshell の終了挙動 (= inotifywait pipeline + while ループの subshell 化) で SIGPIPE / 親 close で死ぬ可能性。3rd: nohup + disown 付きでも、bash 内部の `( ... ) &` 構造が outer parent に依存する可能性。4th: 元々設計が永続稼働を保証していない (= inotifywait -t 30 タイムアウト、event 1 回処理で終了する形)。5th: 設計時に「永続デーモン」要件が明文化されておらず、watcher_supervisor.sh の存在は認識されていたが本日の手動起動経路で経由されなかった。 |
| 設計要件 | (a1) supervisor process が必ず watcher を spawn (= 単独 nohup 起動禁止)。(a2) supervisor は systemd-timer 風 keep-alive、死亡検知 30 秒以内、retry cap 5 + escalation。(a3) 各 watcher は heartbeat を queue/watchers/<agent>.health に 60 秒間隔で書込。(a4) supervisor が heartbeat staleness を確認、必要時 spawn。 |
| 検証方法 | (V-a1) bats: watcher プロセスを kill -9 → 30 秒以内に supervisor が再起動を確認。(V-a2) bats: 1 時間連続稼働で死亡 0 件。(V-a3) 観測: queue/watchers/<agent>.health の更新間隔が 60s ± 5s。 |

### b) inotifywait -t 30 タイムアウトと永続稼働の不整合

| 列 | 内容 |
|---|---|
| 現状 | scripts/inbox_watcher.sh は inotifywait -q -t 30 でタイムアウト機能を持つが、while ループでの再 invocation が確実でない。 |
| 真因 | 1st: タイムアウトで inotifywait が exit 1 を返す。2nd: bash の `set -e` or pipefail で while ループが終了する。3rd: timeout は本来「死活監視 + 軽量再起動 trigger」のためだが、再起動経路が不在。 |
| 設計要件 | (b1) inotifywait は無限稼働、タイムアウトは廃止。(b2) 死活確認は heartbeat に分離 (= a3 と統合)。 |
| 検証方法 | (V-b1) code review: inotifywait に -t オプション無し。(V-b2) bats: 1 時間 inotifywait プロセスが同一 PID 維持。 |

### c) send-keys 連発による Codex interruption

| 列 | 内容 |
|---|---|
| 現状 | 本多 14:14 Conversation interrupted = 信長 Escape + Enter 連発が真因 (memory 永続化済)。本日の家康固着 (16:00-17:00) も類似経路。 |
| 真因 | 1st: send-keys を redraw 用途で連発。2nd: TUI 空白を「停止」と誤判定 → 入力で復活させようとする。3rd: TUI 描画問題と CLI 死亡を区別する手段なし。4th: capture-pane が空白を返す状況で「Claude session 生死」判定方法が未整備。5th: 本来 heartbeat で生死確認すべきところ、TUI 表示で判定する設計。 |
| 設計要件 | (c1) send-keys は safe_nudge wrapper 経由のみ、direct tmux send-keys は禁止 (除く supervisor / 信長緊急介入)。(c2) 120 秒 cooldown、Codex interruption guard。(c3) TUI 空白時は書面 (one-shot) 経路にフォールバック。(c4) pane heartbeat (= queue/session_health/<agent>.yaml) で生死判定。 |
| 検証方法 | (V-c1) grep: direct `tmux send-keys` 使用箇所が許可リスト以外で 0。(V-c2) bats: 120 秒以内の同一 agent への send-keys が queued/blocked。(V-c3) bats: TUI 空白 fixture で書面 nudge に切替。 |

### d) TUI 空白時の無効 nudge

| 列 | 内容 |
|---|---|
| 現状 | hideyoshi/ashigaru1/ashigaru2 の capture-pane が空白の状態で nudge を送っても、Claude TUI が見えていないため何も表示されず、agent が反応したかも不明。 |
| 真因 | 1st: TUI 描画状態と Claude session 状態が不一致。2nd: TUI 描画が乱れた状態で Claude session は生きているが、画面が見えない。3rd: nudge は「画面が見えている前提」で設計、空白時の代替経路 (= 書面 mode) が watcher 経路に組み込まれていない。 |
| 設計要件 | (d1) TUI 状態を heartbeat ファイルで明示 (= nonempty / empty / stale / unknown)。(d2) 空白判定時は書面 nudge (= 信長 inbox に「book mode で確認せよ」alert)。(d3) send-keys を抑制、視認可能な状態に戻った時点で再度 nudge 試行。 |
| 検証方法 | (V-d1) bats: TUI 空白 fixture で nudge 抑制、書面 alert に切替。(V-d2) 観測: queue/session_health/<agent>.yaml の tui_capture_state が更新される。 |

### e) clear_command 強引 retry

| 列 | 内容 |
|---|---|
| 現状 | hideyoshi.log で「busy check 3×5s → proceeding anyway」= /clear 送信を 15 秒 busy 待ち後に強引送信。 |
| 真因 | 1st: busy check の判定基準が不明 (= TUI 表示文字列ベースか?)。2nd: agent が /clear 受領可能なタイミングを確認する仕様がない。3rd: /clear は破壊的 (context 全消去) なため、強引投入は agent の context 喪失 risk。4th: 設計時「busy=送信延期」を仕様化したが、cap=3 retry でその後強引、という安全装置不足。5th: 安全な /clear 投入には agent 側 ack ハンドシェイクが必要だが、未実装。 |
| 設計要件 | (e1) /clear は agent からの ready_for_clear ack 受領後のみ投入。(e2) ack 経路: queue/session_health/<agent>.yaml に ready_for_clear フラグ。(e3) ack 受領前の強引投入禁止。(e4) timeout 時は alert + 手動承認待ち。 |
| 検証方法 | (V-e1) bats: agent ready=false で /clear 送信 → 投入されないことを確認。(V-e2) 観測: clear_command 投入前に必ず ready_for_clear ack 確認ログ。 |

### f) post-reset 直後 nudge と Session Start 衝突

| 列 | 内容 |
|---|---|
| 現状 | hideyoshi.log で「[POST-RESET] Sending immediate post-reset nudge」と /clear 直後に nudge 送信。Session Start 進行中の agent に追加入力を投げる構造。 |
| 真因 | /clear 後の Session Start (instructions 読込 + memory 復元) は中断されてはならない。post-reset nudge は Session Start 完了を待たずに発火。agent が Session Start を完了したかの確認がない。 |
| 設計要件 | (f1) post-reset は agent からの ready_for_dispatch ack 受領後にのみ nudge。(f2) Session Start 完了 = queue/session_health/<agent>.yaml の ready_for_dispatch=true。 |
| 検証方法 | (V-f1) bats: ready_for_dispatch=false で nudge 送信 → 抑制。(V-f2) 観測: Session Start 中の nudge 投入 0。 |

### g) dedup 不在

| 列 | 内容 |
|---|---|
| 現状 | queue/inbox/<agent>.yaml に同一 message_id が複数回登場可能、watcher が再 invoke で同じ msg を二度処理する risk。 |
| 真因 | 1st: dedup table がない。2nd: idempotency 設計が一部のみ。3rd: msg_id は時刻ベース UUID で衝突回避はされるが、処理済追跡がない。 |
| 設計要件 | (g1) queue/message_dedup.yaml or sqlite で processed_message_ids を保持。(g2) 処理済 msg_id は再処理しない (= idempotent)。(g3) TTL で古い entry を cleanup。 |
| 検証方法 | (V-g1) bats: 同一 msg_id を 2 回 inbox_write → 2 回目はスキップ。(V-g2) 観測: dedup table のサイズが TTL で安定。 |

### h) retry 無限ループ risk

| 列 | 内容 |
|---|---|
| 現状 | CLAUDE.md §Watcher Design Principles で禁止されている無限ループ。inbox_watcher.sh のコード内で retry cap が一部のみ実装。 |
| 真因 | 設計時 retry cap が全 retry 経路に適用されていない。失敗ケースの terminal action が一部未定義。 |
| 設計要件 | (h1) 全 retry に cap=5。(h2) cap 超過時は dead-letter queue へ移動 + escalation。(h3) self-send 即 ack。(h4) TTL で古い msg を auto-ack。 |
| 検証方法 | (V-h1) 静的解析: 全 retry loop に cap がある。(V-h2) bats: 失敗継続 msg が 5 回後に dead-letter へ移動。 |

### i) heartbeat 不在

| 列 | 内容 |
|---|---|
| 現状 | watcher プロセスの生死を外部から検知する手段がない。死亡から検知まで時間差大。 |
| 真因 | heartbeat 設計が CLAUDE.md §Error Design では明示されているが、inbox_watcher.sh では未実装。 |
| 設計要件 | (i1) queue/watchers/<agent>.health に 60 秒間隔で {alive, uptime, last_action, last_seen, version, pid} JSON 書込。(i2) 5 分以上更新なし = 死亡判定。(i3) supervisor が死亡検知 → 自動再起動。 |
| 検証方法 | (V-i1) bats: watcher 起動後 60s で health ファイル作成。(V-i2) bats: watcher kill -9 → 30s 以内に supervisor が再起動。 |

### j) lock file stale 残存

| 列 | 内容 |
|---|---|
| 現状 | scripts/inbox_watcher.sh に flock 多用、cleanup 不備で stale lock 残存可能性。LOCKFILE.d ディレクトリ + sleep loop 経路もあり。 |
| 真因 | 異常終了時 flock 解放されないケースあり。mkdir lock 経路が trap EXIT に依存、SIGKILL で解放漏れ。 |
| 設計要件 | (j1) 全 lock に PID 記録、stale 検出時は force release。(j2) mkdir lock 経路を廃止、flock のみ使用。(j3) 起動時に stale lock cleanup。 |
| 検証方法 | (V-j1) bats: watcher kill -9 → lock 解放確認。(V-j2) 観測: 起動時 stale lock 0。 |

### k) sleep-based fallback と inotify 経路の混在

| 列 | 内容 |
|---|---|
| 現状 | scripts/inbox_watcher.sh が macOS (fswatch) と Linux (inotifywait) で経路分岐 + sleep fallback も持つ。1 ファイルに 3 経路混在で複雑化。 |
| 真因 | 1 つの watcher で 3 経路 (inotify / fswatch / sleep) サポート → 複雑化。各経路で挙動微妙に異なる。 |
| 設計要件 | (k1) 環境別に別 watcher binary を選択 (= adapter pattern)。(k2) sleep fallback は廃止 (= inotify/fswatch 必須)。 |
| 検証方法 | (V-k1) code review: 単一経路化。(V-k2) bats: Linux 環境で inotify のみ使用確認。 |

### l) macOS/Linux 分岐の破壊点

| 列 | 内容 |
|---|---|
| 現状 | k と同じ。fswatch と inotifywait で event 名が異なる、 if/else で分岐。本 project 主要環境は WSL2 (Linux) ゆえ macOS 経路は test されにくい。 |
| 真因 | 1 file 内で OS 分岐 → 片方の経路が test されにくい。 |
| 設計要件 | (l1) adapter 関数で abstraction layer。(l2) 両 OS で bats fixture。 |
| 検証方法 | (V-l1) bats: fswatch fixture + inotifywait fixture 両方 PASS。(V-l2) code review: OS 分岐が adapter のみに局在。 |

### m) cli_adapter.sh の CLI 状態判定 drift

| 列 | 内容 |
|---|---|
| 現状 | cli_adapter.sh が claude / codex (node) を判定、判定 drift で誤動作。 |
| 真因 | pane_current_command で「node」を「Codex」と判定するが、他の Node プロセスも混入 risk。@agent_id ベースで判定すべき。 |
| 設計要件 | (m1) pane_registry.yaml で persona ↔ cli を明示マップ。(m2) pane_current_command との不一致を drift として alert。 |
| 検証方法 | (V-m1) bats: pane_registry の cli=claude だが pane_current_command=node → drift detect。 |

### n) pane identity 検証なし → agent drift 時の誤配

| 列 | 内容 |
|---|---|
| 現状 | send-keys 前の pane @agent_id 確認がない、本日 0.3↔0.4 drift 状態でも気付かれずに動作。 |
| 真因 | skills/pane-identity-verify/SKILL.md の検証手順が watcher で未呼出。pane_registry.yaml と tmux 実態が drift していても検出されない。 |
| 設計要件 | (n1) 全 send-keys 前に pane @agent_id 検証必須。(n2) drift 時は send-keys 拒否 + alert。 |
| 検証方法 | (V-n1) bats: drift fixture で send-keys 拒否。(V-n2) 観測: pane_identity.sh が send-keys path で呼ばれる。 |

### o) dead-letter queue 不在

| 列 | 内容 |
|---|---|
| 現状 | 失敗継続 msg の最終的な格納先がない、watcher で永遠に retry。 |
| 真因 | dead-letter queue 設計が §Watcher Design Principles で明示されているが、実装なし。 |
| 設計要件 | (o1) queue/dead_letter/<agent>/ 新設。(o2) retry cap 超過 msg を移動。(o3) 信長 inbox に dead-letter 通知。 |
| 検証方法 | (V-o1) bats: cap=5 超過 msg が dead-letter へ移動。 |

### p) self-send 即 ack 不在

| 列 | 内容 |
|---|---|
| 現状 | 過去事故 (2026-05-05 SecondPC 暴走) で self-send 検出時の即 ack ロジックがなく、無限 retry。本日 inbox_watcher.sh では一部実装、全件未網羅。 |
| 真因 | §Watcher Design Principles で原則明示済だが、実装が一部のみ。 |
| 設計要件 | (p1) from_pc == to_pc の self-send は即 acknowledged_at 更新 + ack_by=system。 |
| 検証方法 | (V-p1) bats: self-send fixture で再 retry 0。 |

### q) wake-up nudge と書面経路の不整合

| 列 | 内容 |
|---|---|
| 現状 | 本多 14:14 事故で「TUI 空白時の book mode」が議論されたが、watcher 経路には統合されず。 |
| 真因 | nudge 経路は send-keys 一択、書面経路 (= one-shot 報告 trigger) は別 system。 |
| 設計要件 | (q1) TUI 空白判定時、send-keys でなく書面通知 (= 信長 inbox + agent 自身の book mode entry)。(q2) agent が次回 idle 時に書面で確認。 |
| 検証方法 | (V-q1) bats: TUI 空白 fixture で書面通知のみ送信。 |

### r) cross-PC bridge 戻り ACK との連携不備

| 列 | 内容 |
|---|---|
| 現状 | SecondPC 既読が MainPC に反映されない (= sanada 報告 R1)。bridge は MainPC→SecondPC 配達のみ。 |
| 真因 | bridge 設計が one-way。戻り ACK 経路が cmd_secondpc_autonomy_pack_001 で別途対応予定だが、本 cmd と協調必要。 |
| 設計要件 | (r1) 本 cmd は MainPC 配達層に専念。(r2) cross-PC は cmd_secondpc_autonomy_pack_001 と協調、設計書で out_of_scope を明示。 |
| 検証方法 | (V-r1) 設計書で out_of_scope を明示。(V-r2) cmd_secondpc_autonomy_pack_001 起案時に整合性確認。 |

### s) 既存修復 commit の積み重ね効果

| 列 | 内容 |
|---|---|
| 現状 | 2f4b960 (type field bug) / addd03d (信長提案) / 8ae179e (家康監査) / 7511d77 (本多提案) / ad92603 (本多自己解決) / a25fb56 (sanada SecondPC 同期) を順次積み重ねたが、本日 16:43-17:14 で watcher silent death が再発 = 既存修復は十分でなかった。 |
| 真因 | 各修復は局所的、watcher 永続稼働への根本対処は未実施。watcher_supervisor.sh の存在は認識されていたが、実運用経路で使われていない。 |
| 設計要件 | (s1) 本 cmd で watcher_supervisor を実運用 path に組込。(s2) 過去修復 commit の知見を全て新 system に継承。(s3) 設計書に過去修復一覧 + 新 system での扱いを記載。 |
| 検証方法 | (V-s1) 設計書 mapping 表で過去 commit との対応を明示。 |

### t) queue/inbox symlink 経路と Codex sandbox writable root の整合

| 列 | 内容 |
|---|---|
| 現状 | queue/inbox/ → /home/user/.local/share の symlink、Codex sandbox writable_root 外として 16:00-17:00 家康固着 40 分。信長 send-keys "1" Enter 緊急介入で復旧。 |
| 真因 | symlink 経路が Codex sandbox 制約と不整合。~/.codex/config.toml の sandbox_mode=workspace-write でも本 path は許可外。 |
| 設計要件 | (t1) 本 cmd の新 inbox path は workspace 内に配置 (= queue/inbox_v2/)。(t2) migration tool で旧 inbox の msg を新 path に移動。(t3) ~/.codex/config.toml の path 許可登録は念のため別途。 |
| 検証方法 | (V-t1) bats: Codex pane で bulk_ack.sh 走らせ → プロンプトなし即実行。(V-t2) 設計書: inbox path を workspace 内に固定。 |

### u) bulk_ack.sh / inbox_write.sh / inbox_watcher.sh 三者間の inbox path 想定不一致

| 列 | 内容 |
|---|---|
| 現状 | 三者が異なる writable expectation を持つ可能性、symlink 経路で挙動分岐。各 script で path 解決ロジックが個別実装。 |
| 真因 | shared library で SSoT 化されていない。 |
| 設計要件 | (u1) 共通 lib (= scripts/lib/inbox_path.sh) で path 解決を統一。(u2) 全 script が共通 lib を使用。 |
| 検証方法 | (V-u1) code review: 全 script が共通 lib 使用。(V-u2) bats: 同 path で全 script の挙動一致。 |

### v) Codex agent 用 Supabase polling fallback 不在 (= 本日 17:30 検証で発覚)

| 列 | 内容 |
|---|---|
| 現状 | 本日 17:13 watcher 全死亡後、家康/本多 (Codex Pro) への通知経路は send-keys のみ。Supabase に書込んでも家康/本多 は polling せず気付かない (instructions/ieyasu.md + instructions/honda.md に Supabase polling 経路なし、grep ヒット 0)。F004 (polling loop) 禁止規定が full polling を阻んでいる。 |
| 真因 | 1st: Codex は prompt 駆動、自走 polling を組まない。2nd: F004 は quota 浪費理由で polling 全面禁止だが、watcher 死亡時の fallback として TTL 付き低頻度 polling は組込可能だった。3rd: 既存 organizational_lessons / pc_handshake table は MainPC↔SecondPC bridge 用途、agent receiver polling は組まれていない。 |
| 設計要件 | (v1) 各 Codex agent (家康・本多) instructions に Supabase polling fallback を限定的に組込: 60-300 秒間隔、TTL 30 分、watcher 生存時は disabled、watcher 死亡判定時のみ activated。(v2) **F004 例外条項を AGENTS / persona instructions / cmd acceptance に明記** (= watcher fallback 限定、quota 影響 monitoring 必須、enable/disable 状態を session_health または control_plane lease で可視化)。(v3) Supabase 専用 table `agent_message_fallback` 新設、agent_id + correlation_id + payload + ttl + read_at を保持。(v4) watcher_supervisor が watcher 死亡検知時、自動で fallback enable。 |
| 検証方法 | (V-v1) bats: watcher kill → 60 秒以内に Codex agent が Supabase fallback で task pull。(V-v2) 観測: fallback enabled 時の Supabase query 頻度が 60-300 秒間隔。(V-v3) 観測: watcher 生存時は fallback inactive (= 0 query/min)。(V-v4) F004 例外条項が AGENTS.md + instructions/ieyasu.md + instructions/honda.md + cmd acceptance criteria に grep ヒット (= 4 箇所明記)。 |

### w) Codex TUI 長文 send-keys + Enter submit 不確定挙動 (= 本日 17:25 家康・本多 で同型現象)

| 列 | 内容 |
|---|---|
| 現状 | 信長から家康 pane (multiagent:0.3) + 本多 pane (multiagent:1.0) への書面 nudge (= 長文 send-keys + Enter) で、Enter が改行扱いされ submit 確定しない可能性。両家臣で同型、入力欄に文字列残存。本多のみ追加 Enter 1 度で submit 成功 (Working 確認)、家康は不明。 |
| 真因 | 1st: tmux send-keys "<長文>" Enter は連結シーケンス、Codex TUI 側で「文字列 + 改行」と解釈される可能性。2nd: Codex multi-line input は意図的設計だが、外部からの自動投入で改行と submit を区別する手段がない。3rd: 単一 send-keys で長文 + 確定を保証するシーケンスが未確立。 |
| 設計要件 | (w1) safe_nudge wrapper が Codex pane への送信時、長文 (= 100 文字超) は短縮版 + 詳細 path 提示の 2 段階に分離。(w2) 短縮版送信後 1 秒待機 → Enter 単独再送 (= 「一度のみ優先」原則順守、最大 1 回追加 Enter)。(w3) submit 成否は capture-pane で "Working" マーカー確認、未確認時は alert + 信長介入待ち。 |
| 検証方法 | (V-w1) bats: 長文 nudge → Codex pane で Working 状態到達を確認。(V-w2) 観測: capture-pane に "Working" マーカー出現。 |

## 2. Phase 1 設計要件サマリ

上記 a〜w (= 23 項目) から抽出した必須要件 (Phase 1 設計書で実装方針を確定):

| # | 要件 | 該当反省点 |
|---|------|-----------|
| 1 | 永続稼働 (supervisor + heartbeat + 自動再起動) | a, b, i |
| 2 | send-keys 制御 (safe_nudge wrapper + cooldown + Codex guard + pane identity verify) | c, n |
| 3 | TUI 空白時の書面 mode フォールバック | d, q |
| 4 | /clear ack ハンドシェイク + post-reset ready_for_dispatch ack | e, f |
| 5 | dedup table | g |
| 6 | retry cap=5 + dead-letter queue + self-send 即 ack | h, o, p |
| 7 | lock 健全性 (PID-aware flock + stale cleanup) | j |
| 8 | adapter pattern (OS 分岐の局在化、sleep fallback 廃止) | k, l |
| 9 | CLI 状態判定 SSoT 化 (pane_registry.yaml ベース) | m |
| 10 | symlink 排除 (workspace 内 inbox path) | t, u |
| 11 | 共通 lib (path 解決統一) | u |
| 12 | observability (structured JSON log + correlation_id) | a, c, i |
| 13 | 過去修復 commit 知見の継承 | s |
| 14 | cross-PC bridge との協調 (out_of_scope 明示) | r |
| 15 | schema 検証 gate (蓬蓮草 v2 と統合) | (Phase 1 で蓬蓮草 v2 と協議) |
| 16 | Codex agent 用 Supabase polling fallback | v (新規追加、本日 17:30 検証で発覚) |
| 17 | Codex TUI 長文 send-keys + Enter submit 確認手順 | w (新規追加、本日 17:25 家康・本多 で同型現象) |

## 3. 残 risk + 次 cycle 候補

| ID | 残 risk | 次 cycle 対応 |
|----|---------|--------------|
| R-a | watcher 死亡の真因 (= 1st-5th Why の 2nd Why「bash subshell 終了」) は確証なし | Phase 1 設計時に code reading + strace で確定 |
| R-b | supervisor の自動再起動 retry cap=5 を超える死亡パターンが残る可能性 | Phase 5 retrospective で観察、超過時の根本対処は別 cmd |
| R-c | cross-PC bridge との協調は cmd_secondpc_autonomy_pack_001 と並走必要 | Phase 1 設計時に cmd 間 interface を定義 |
| R-d | TUI 描画問題 (= 本多事例) と CLI 死亡を判別する heartbeat 仕様の精緻化が必要 | Phase 1 設計時に session_health/<agent>.yaml 仕様確定 |
| R-e | symlink 経路廃止 + migration が SecondPC 系にも影響、SecondPC との同期が必要 | Phase 4 cutover 前に SecondPC 側の対応確認 |

## 4. 既存資産との重複 (Anti-Duplication Rule 順守)

| 項目 | 既存資産 | 新規作成判断 |
|------|---------|-------------|
| supervisor | scripts/watcher_supervisor.sh (既存だが本日の経路で未使用) | **既存改修** (= 永続稼働 path に組込) |
| heartbeat | (既存なし、CLAUDE.md §Error Design に仕様のみ) | **新規作成** |
| dedup | (既存なし) | **新規作成** |
| dead-letter | (既存なし) | **新規作成** |
| safe_nudge | scripts/safe_nudge.sh (= 蓬蓮草 v2 W4 の予定だったが本 cmd に吸収) | **新規作成** |
| Codex interruption guard | scripts/codex_interruption_guard.sh (= 同上) | **新規作成** |
| pane identity verify | scripts/checks/pane_identity.sh + skills/pane-identity-verify/SKILL.md (既存) | **既存活用** (= 本 cmd は呼出経路を整備) |
| schema gate | scripts/checks/communication_contract_check.py (= 蓬蓮草 v2 で別途実装) | **蓬蓮草 v2 に委譲** (= 本 cmd は schema 利用側) |
| inbox_path lib | (既存なし、各 script で個別実装) | **新規作成** (scripts/lib/inbox_path.sh) |
| migration tool | (既存なし) | **新規作成** (= 旧 → 新 inbox path 移行) |

## 5. 自動復旧 SH パターン適用判定 (CLAUDE.md §15)

| パターン | 適用判定 | 注釈 |
|---------|---------|------|
| SH1 Circuit Breaker | ✅ 適用 | watcher 連続失敗時に cooldown |
| SH2 Exponential Backoff Retry | ✅ 適用 | retry 1s → 2s → 4s → 8s |
| SH3 Fallback (Graceful Degradation) | ✅ 適用 | inotify 不可時 fswatch、両者不可時 sleep-poll の最終手段は廃止 (= k 違反、別案検討) |
| SH4 Stale Lock 自動解除 | ✅ 適用 | j 要件 |
| SH5 Connection Pool 自動再接続 | 不適用 | DB 接続なし |
| SH6 Self-Restart (限定的) | ✅ 適用 | 手動停止フラグ尊重必須、CLAUDE.md §15 SH6 cap |
| SH7 Cache 自動無効化 | 不適用 | キャッシュなし |
| SH8 Idempotent Retry | ✅ 適用 | g 要件 |
| SH9 State Machine 復元 | △ Phase 5 検討 | 状態遷移の複雑度次第 |
| SH10 Health-based Routing | 不適用 | 単一 agent 単一 watcher |
| **危険 D1-D6** | **全件不適用 (= 該当なし)** | データ書換自動修復なし、無限再起動なし、認証昇格なし、患者データ自動マージなし、課金自動再試行なし、migration 自動 rollback なし |

## 6. 過去 §X 違反監査

| ルール | 違反有無 | 注釈 |
|--------|---------|------|
| Boy Scout Rule §14 | △ | 既存 inbox_watcher.sh は廃止 (cutover) ゆえ Boy Scout 整備対象外。新 system は §14 順守必須。 |
| Watcher Design Principles | ❌ 既存違反 (h, o, p で判明) | 新 system で全項目順守 |
| Anti-Duplication Rule | ✅ §4 で全件チェック済 | |
| Root Cause 4 Patterns | ⚠ 旧版 (inbox_watcher.sh) と新版 (message_delivery_v2/) の併存 risk | cutover 完遂後に旧版 archive で対処 |
| §18 PC × Account × Agent Allocation | ✅ 順守 | watcher は MainPC 5+1 / SecondPC 3+1 配置に整合 |
| §19 Lessons-to-Skill | ⚠ 本日の watcher silent death は §19 適用候補 | Phase 5 retrospective で skill 化判定 |

## 7. PDCA cycle 想定の token 予算

| Phase | 主担当 | 推定 token 消費 | 注釈 |
|-------|-------|----------------|------|
| Phase 0 | 信長執筆 + 家康監査 | ~30k (本書 + 監査結果) | 本書は ~28k 文字 |
| Phase 1 | 信長執筆 + 家康監査 | ~50k (設計書 + 監査) | 詳細設計 |
| Phase 2 | 信長 / 家康 (ashigaru 停止中) | ~150k (実装 + bats + PDCA cycles) | 1-3 cycle 想定 |
| Phase 3 | 信長 + 家康 + 観察 | ~30k (shadow 24h 観察ログ) | |
| Phase 4 | 信長 cutover + 家康監査 | ~20k | |
| Phase 5 | 信長 retrospective + 家康監査 | ~40k | postmortem |
| **合計** | | **~320k** | MainPC quota 内、shogun + ieyasu のみ消費 |

quota 影響: shogun (= claude opus) + ieyasu (= codex Pro) の 2 アカウント分散ゆえ、§18 配分に影響軽微。

## 8. 家康監査依頼

本書を家康 (ieyasu, Codex Pro) に **Phase 0 一次監査** として依頼する。

**監査軸**: Codex 6 軸 (security / bugs / types / tests / duplication / git)

**PASS 条件**:
- 各項目 (a〜w、= 23 項目) の 4 列記録に欠落なし
- 設計要件 (a1〜u2) の整合性 + 実装可能性
- 検証方法 (V-a1〜V-u2) の bats / 観測手段の妥当性
- §4 Anti-Duplication / §5 SH 適用 / §6 §X 違反監査 / §7 token 予算 の妥当性
- 残 risk (R-a〜R-e) の Phase 1 引継ぎ妥当性

**FAIL 時の対応**: 信長が修正、PDCA cycle 上限 5 回 (= cmd 内 PDCA 規定)。

家康 verdict 受領後、**Phase 1 設計書** (= 真田担当だが家臣停止中ゆえ信長執筆予定) に進む。

## 9. 信長最終進言

上様、watcher の死は単なるバグにあらず。永続稼働の設計要件不在、TUI と CLI の混同、retry の終端不在、symlink と sandbox の不整合、これらが重なって本日の崩壊を生み出したでござる。

ゼロベース再設計とは、配達インフラを「いかに壊れないか」から「壊れた時に必ず気付き自動で立ち直れるか」へ思想転換することにござる。supervisor + heartbeat + dead-letter + safe wrapper、この 4 本柱を新 system に据えれば、watcher は二度と silent death せぬ。

本書を以て Phase 0 を完遂する。家康殿の監査を仰ぎ、PASS なれば Phase 1 設計書へ進める所存。

## 10. 信長自己再監査 (= 理事長殿『最後に自己再監査ご実施』2026-05-08 17:30 御命令)

家康監査と並走、信長自身で Phase 0 docs を Codex 6 軸 self-audit。

### Axis 1: security

| 観点 | 判定 | 所見 |
|------|------|------|
| 認証・認可境界 | ✅ PASS | 反省点 t (symlink + Codex sandbox 整合) で security 境界を明示。新 path は workspace 内固定、~/.codex/config.toml の許可 path も別途登録。 |
| 通信路傍受 risk | ✅ PASS | 全配達は同一 PC 内 file system 経由、network 経由は SecondPC bridge (= cmd_secondpc_autonomy_pack_001 範疇)。 |
| 権限昇格 risk | ✅ PASS | watcher は root 権限不要、SH パターン D3 (認証昇格自動) は §5 で不適用宣言。 |
| 秘匿情報漏洩 | ✅ PASS | log structured JSON は agent_id / correlation_id のみ、payload masking 必須を Phase 1 で詳細化。 |

### Axis 2: bugs

| 観点 | 判定 | 所見 |
|------|------|------|
| 反省点網羅性 | ✅ PASS | 23 項目 (a〜w)、watcher silent death の 1st-5th Why + 既知事故 8 件 + 新発見 2 件 (v/w) を全件記録。 |
| 真因確証性 | △ 部分 PASS | a 2nd Why「bash subshell 終了」は仮説、R-a として残 risk 化。Phase 1 で strace + code reading で確定。 |
| 連鎖事故 risk | ✅ PASS | watcher 死 → 配達不能 → agent 停止 → cmd 進行不能 の連鎖を a/c/d/i 横断で記録。 |
| 緊急介入手段 | ✅ PASS | 信長 send-keys 緊急介入 (= 本日 16:00 家康固着解除) を反省点 c/w に統合、safe_nudge wrapper で恒久化。 |

### Axis 3: types

| 観点 | 判定 | 所見 |
|------|------|------|
| schema 整合 | ✅ PASS | inbox_message.schema.json は蓬蓮草 v2 (cmd_communication_resilience_pack_v2_001) 委譲、本 cmd は schema 利用側ゆえ責務分離明確。 |
| YAML/JSON 妥当性 | ✅ PASS | 反省点 j (lock file) / r (cross-PC) で YAML 健全性 + cleanup を要件化。 |
| heartbeat JSON schema | ⚠ Phase 1 詳細化 | i 設計要件で {alive, uptime, last_action, last_seen, version, pid} を明示、Phase 1 設計書で schema fixate。 |
| correlation_id 形式 | ⚠ Phase 1 詳細化 | log 設計要件 12 で言及、Phase 1 で UUID v7 / KSUID / 自前形式の選定。 |

### Axis 4: tests

| 観点 | 判定 | 所見 |
|------|------|------|
| bats fixture 数 | ✅ PASS | 各項目に V-a1〜V-w2 で検証方法明示、25 件以上の test case 想定。 |
| TUI シミュレーション難度 | ⚠ R-d で残 risk | v/w は Codex pane simulation が複雑、tmux fixture + capture-pane mock で対応想定だが Phase 1 で実装可否確定。 |
| coverage 想定 | ✅ PASS | unit + integration + shadow 24h + cutover 検証 = Phase 2-4 で多層 test。 |
| FAIL 時 PDCA | ✅ PASS | cmd 内 PDCA cycle max=5、家康一次 + 信長 self-audit + 本多 governance + Codex self + Gemini で多層チェック。 |

### Axis 5: duplication

| 観点 | 判定 | 所見 |
|------|------|------|
| Anti-Duplication Rule | ✅ PASS | §4 で 10 項目を新規/既存改修/既存活用/委譲で全件分類。watcher_supervisor.sh + pane_identity.sh + skills/pane-identity-verify は既存活用、schema gate は蓬蓮草 v2 委譲。 |
| 蓬蓮草 v2 W4 統合 | ✅ PASS | shogun_to_hideyoshi.yaml で蓬蓮草 v2 W4 を本 cmd に吸収済、out_of_scope 明示。 |
| SSoT 是正連携 | ✅ PASS | pane_registry.yaml が真値、本 cmd watcher_supervisor が唯一参照源、cmd_section18_topology_consensus_001 Phase 2 完遂後に Phase 4 cutover の依存を関連 cmd 節で明示。 |
| 中期 Supabase polling | ✅ PASS | 別 cmd 起案を回避、本 cmd Phase 1/2 で v 設計要件として実装、二重実装根絶。 |

### Axis 6: git

| 観点 | 判定 | 所見 |
|------|------|------|
| 過去修復 commit 継承 | ✅ PASS | 反省点 s で 2f4b960 / addd03d / 8ae179e / 7511d77 / ad92603 / a25fb56 を一覧、新 system に知見継承。 |
| migration tool 計画 | ✅ PASS | §4 で migration tool 新規作成を明示、Phase 4 cutover で旧 archive。 |
| rollback path | ✅ PASS | cmd command 節で「archive から復元、watcher_supervisor 旧版で起動」の rollback path 明示。 |
| commit message 規範 | ⚠ Phase 1-5 適用 | Phase 1 設計書 commit / Phase 2 実装 commit 等で git 規範を順守、ECRule (Boy Scout / Watcher Design Principles) 順守。 |

### 自己再監査 verdict

**総合判定: PASS (= Phase 1 設計書執筆へ進行可)**

**残 risk (= R-a〜R-e に追加):**
- R-f: heartbeat JSON schema + correlation_id 形式の詳細化を Phase 1 で確定
- R-g: Codex pane simulation の bats fixture 実装可否を Phase 1 で確証

**家康一次監査との関係**: 本 self-audit は信長視点の self-check、家康一次監査 (Codex 6 軸) と並走で多層チェック。家康 verdict が独立して PASS/FAIL 判定する。両者 PASS で Phase 0 close。

**本多二次審査との関係**: 本多に governance 視点 (M1-M4) + Anti-Duplication 二次審査を依頼済 (= multiagent:1.0 send-keys 完了、Working 確認)。本多 verdict も独立記録、3 者一致 PASS で Phase 0 final close。

---

*信長 (織田信長) 2026-05-08 17:32 JST、Phase 0 自己再監査 完遂、verdict PASS*

## 11. 本多 governance 追記 (= M1-M4 retrospective)

> 追記: 本多正信 / honda
> 日時: 2026-05-08 19:00 JST
> 関連 report: `queue/reports/honda_report.yaml`

### M1 process

Phase 0 は watcher silent death を単一障害ではなく、send-keys、TUI、symlink、schema、retry 終端、pane drift へ分解した点で進行可。ただし Phase 1 以降は「設計 doc」「runtime watcher」「pane registry」の責務境界を acceptance criteria に明記し、後続 cmd へ丸投げせぬこと。

### M2 efficiency

新 watcher / supervisor / heartbeat の骨格を先に shadow 稼働させた判断は妥当。旧 inbox_watcher の延命に quota を燃やすより、message_delivery_v2 を中核へ寄せる方が効率的。ただし production cutover は safe_nudge / dedup / dead-letter / schema validation 完了まで不可。

### M3 responsibility

F004 fallback、pane registry 真値裁定、§18.1 改訂は責務が重い。理事長殿専権の topology 判断と、信長・家康・本多の監査責務を分け、家臣停止中の F001 lift を恒常化させぬこと。

### M4 improvement

再発防止の中核は「沈黙を正常扱いしない」ことにある。heartbeat、delivery_state、safe_nudge gate、pane_identity 4-way audit を同じ operational flow に接続し、watcher 死亡と pane drift を別々の事故として扱わぬこと。

**本多 verdict**: PASS_WITH_CONDITIONS。Phase 1/2 へ進行可。ただし cutover gate 未完のまま旧 system を archive することは不可。
