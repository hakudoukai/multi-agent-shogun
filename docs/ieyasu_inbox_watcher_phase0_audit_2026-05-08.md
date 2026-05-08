# 家康 一次監査 — inbox_watcher ゼロベース Phase 0

> 監査者: 家康 (ieyasu / Codex Pro)  
> 日時: 2026-05-08 18:04 JST  
> 対象: `docs/inbox_watcher_failure_modes_2026-05-08.md`  
> 対象 cmd: `cmd_inbox_watcher_zerobase_redesign_001` Phase 0  
> 監査軸: security / bugs / types / tests / duplication / git  
> verdict: **PASS_with_required_corrections**

## 0. 総評

Phase 0 の目的である「本日 watcher 3 度全死亡の反省点を、現状・真因・設計要件・検証方法へ分解する」は概ね達成済みでござる。特に silent death、send-keys 連発、post-reset nudge、dedup/dead-letter 不在、symlink + Codex sandbox、Codex TUI submit 不確定挙動まで含めた点は、Phase 1 設計へ進む材料として十分。

ただし、Phase 0 文書そのものに整合性の乱れがある。これは実装着手前に修正すべきであり、未修正のまま Phase 1 acceptance criteria に転写すると、以後の検証が曖昧になる。

## 1. Findings

### F1. bugs/tests — 「21 項目」「a〜u」と実体「23 項目」「a〜w」が不整合

**Severity: medium / Phase 1 前修正必須**

文書は §1 で「反省点 21 項目」、§2 と §8 PASS 条件で「a〜u」と記す。一方、実体は `a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,v,w,u` の 23 見出しで、`u` が `v/w` の後に置かれている。

これは監査 acceptance の対象集合を曖昧にする。信長自己再監査では「23 項目 (a〜w)」と訂正的に書かれているため、本文全体を **23 項目 (a〜w、u/v/w含む)** に統一すべし。

### F2. security/process — Supabase polling fallback は F004 例外条項が先

**Severity: medium / Phase 1 設計 gate**

反省点 v の fallback は妥当。ただし AGENTS / gunshi instructions では polling loop が forbidden であり、文書内にも「F004 例外条項を明文化」とある。これは Phase 1 実装要件ではなく、実装前 gate として扱うべきでござる。

要件 v は次の順で分けるべし:

1. watcher 死亡時のみ activation。
2. TTL 30 分、60-300 秒間隔、query budget 記録。
3. F004 例外を `watcher fallback 限定` として AGENTS / persona instructions / cmd acceptance に明記。
4. enable/disable 状態を `queue/session_health/<agent>.yaml` または control-plane lease で可視化。

### F3. tests — sleep fallback の扱いが k/l と §5 で揺れている

**Severity: low-to-medium**

k/l は sleep fallback 廃止を設計要件にしている。一方、§5 SH3 は「inotify 不可時 fswatch、両者不可時 sleep-poll の最終手段は廃止」と書かれ、Fallback と廃止が同じ行で混在して読める。

Phase 1 では明確にすべし:

- Linux: inotify 必須
- macOS: fswatch 必須
- 両者不可: watcher 起動 FAIL + dead-letter/alert
- sleep-poll は採用しない

### F4. duplication — schema gate の責務分離は妥当だが interface が未定義

**Severity: medium**

§4 で schema gate を蓬蓮草 v2 に委譲する判断は Anti-Duplication として妥当。しかし本 cmd は watcher 側の利用者なので、Phase 1 で最低限の interface を固定すべき。

最低限必要:

- inbox message schema の required fields
- delivery_state enum
- correlation_id format
- validation failure 時の扱い (reject / dead-letter / alert)

これがないと、蓬蓮草 v2 と watcher v2 が互いに「相手が決める」として責務空白になる。

### F5. git/migration — symlink 排除は正しいが cutover plan がまだ粗い

**Severity: medium**

t/u の workspace 内 inbox path 固定は、家康固着真因に対する正道でござる。ただし `queue/inbox/gunshi.yaml -> ieyasu.yaml` のような互換 alias が現役であり、SecondPC bridge も旧 path を想定しうる。

Phase 1 では migration を以下に分けるべし:

- read compatibility window
- write freeze
- message copy with digest
- alias/canonical mapping update
- rollback path
- SecondPC receiver との同期確認

## 2. 6 軸判定

| 軸 | 判定 | 理由 |
|---|---|---|
| security | PASS_with_concerns | send-keys / symlink sandbox / TUI leak risk は抽出済み。Supabase fallback は F004 例外と query budget が gate。 |
| bugs | PASS_with_required_corrections | 主要 failure mode は網羅。ただし項目数・見出し範囲の不整合は修正必須。 |
| types | PASS_with_concerns | heartbeat / correlation_id / delivery_state は方向性あり。schema interface の固定が未完。 |
| tests | PASS_with_concerns | V-a〜V-w の検証案は十分多い。sleep fallback 廃止と SH3 表現の揺れを直すべし。 |
| duplication | PASS_with_concerns | 既存活用と新規作成の分類は妥当。蓬蓮草 v2 schema gate との interface が未定義。 |
| git | PASS_with_concerns | 過去修復 commit 継承と migration 方針あり。cutover/rollback を Phase 1 で具体化要。 |

## 3. Phase 1 進行条件

Phase 1 設計書へ進行してよい。ただし、設計書の冒頭で以下を必ず反映すること。

1. 反省点は **23 項目 (a〜w)** と統一し、`u/v/w` の順序を整える。
2. F004 例外条項を watcher fallback 限定で明文化する。
3. sleep-poll fallback 不採用を明記する。
4. 蓬蓮草 v2 schema gate との interface を最低限固定する。
5. symlink 排除 cutover の read/write/migration/rollback window を書く。

## 4. Verdict

**PASS_with_required_corrections**

Phase 0 close は許容。ただし上記 5 点を Phase 1 設計書の入力条件として固定せよ。特に F1 は単なる表記揺れではなく、以後の acceptance criteria を曖昧化するため、最初に直すべきでござる。
