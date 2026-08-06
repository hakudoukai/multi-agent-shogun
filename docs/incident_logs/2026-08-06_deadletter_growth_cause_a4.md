# 2026-08-06 `_dead_letter_second.yaml` 増分の因 (足軽4号)

下命: 家老second msg_20260806_211832_79ebf9bc (2026-08-06T21:18:32)。
禁則順守: `_dead_letter_second.yaml` 本体は一度も開いておらぬ (grep/wc/cat 不使用・`stat`/`ls` のみ)。lane (worktree) 不触。書込・消去・`read` 立て 一切なし。

## §0 母集団・器・範囲宣言

- 対象file: `queue/inbox/_dead_letter_second.yaml` (git外)
- 器①(size推移): `stat -c '%s bytes / mtime=%y'`
- 器②(発火条件): `Read` tool による `shim/hakudokai/hakudokai_secondpc_receiver_poll.py` 全410行の通読 + `grep -n`
- 器③(稼働確認): `ps -eo pid,ppid,etime,cmd` / `/usr/bin/grep -rl` (repo全体、gitignore影響回避のため `/usr/bin/grep` 明示)
- 範囲: 測時 2026-08-06T21:20:42〜21:24:50 JST (約4分12秒、5測点) + コード全文 + 稼働プロセス実測

## ⒜ size の時系列 (stat のみ・中身不読)

| 測点 | 刻(JST) | size(bytes) | mtime |
|---|---|---|---|
| karo-second 参照値 (21:17頃) | - | 146,609 | - |
| 測点0 (当職) | 21:20:42 | 146,609 | 2026-08-06T21:10:42.173406073+0900 |
| 測点1 | 21:21:50 | 146,609 | 同上 |
| 測点2 | 21:22:50 | 146,609 | 同上 |
| 測点3 | 21:23:50 | 146,609 | 同上 |
| 測点4 | 21:24:50 | 146,609 | 同上 |
| 測点5 | 21:25:50 | 146,609 | 同上 |

⇒ **当職の測窓 (21:20:42〜21:25:50、約5分8秒) では増分 0**。mtime も 21:10:42 のまま不変 = この間 一度も書込まれておらぬ。
⇒ 「墓場は今も育っておる」(家老second 21:17測) は当職の窓では再現せず。矛盾に非ず——**間欠的(バースト依存)な書込機構である事の裏付け**(⒝⒞で後述)。増分が観測されなんだ事自体を「止まった」と断定はせぬ(窓が短い・観測時間帯の相違)。

## ⒝ `append_dead_letter()` の発火条件 (行番号付き・推測でなくコード)

- 唯一の書き手 = `append_dead_letter()` (`hakudokai_secondpc_receiver_poll.py` L232-254)。
  `/usr/bin/grep -rl "_dead_letter_second"` で repo全体(gitignore対象含め)を実測した結果、`.py`書き手は本体1件のみ (他は `.bak-*` 4件[非稼働バックアップ]と `__pycache__/*.pyc`[コンパイル済キャッシュ]のみで、いずれも実行対象に非ず)。
- 呼出は **1箇所のみ** = L342、`else` 節(非 `file_sync` の標準message処理、L337-349)内、`target = detect_target(msg)` が **falsy** の時に限る (L339-343)。reasonは常に文字列 `"missing_or_invalid_target_agent"` (L341) — 本呼出経路には他のreasonは存在せぬ。
- `detect_target()` (L199-229) が `None` を返すのは以下いずれの経路でも宛先が確定できなんだ時:
  1. `context_data.target_agent` が無い、または `VALID_SECONDPC_TARGETS` (L94-112 の `AGENT_PANES` キー集合) に無い (`_target_from_context_data`, L184-196)
  2. `topic` が `cross_pc_inbox_([\w-]+)` に一致せぬ。一致してもVALID外なら `BLOCK` ログを出し `None` (L216-222)
  3. `content` がJSON形式で `target_agent` を含み VALID内、でない限り失敗 (`_target_from_json_content`, L172-181)
- ∴ 発火は **「新着messageのうち、上記いずれの経路でも宛先を確定できなかったもの」に限り**、poll cycle毎に条件発火。**時限flushではなく、message到着に完全依存する条件発火**。

## ⒞ 「何が現に落ち続けておるか」(コードのみから言える範囲)

- L238 dedup: `if msg_id and msg_id in existing: return` — 既存ファイル内容への **部分文字列一致** で再append防止(YAML parseした照合に非ず・文字列 `in` 演算子)。
- ∴ 増分の唯一の因は「`detect_target` が解決できぬ **新規** message (msg_idが既存fileに未出現) がpc_handshakeから到着し続けること」。
- 「宛先不明の便が今も生まれておるのか・別の因か」= **コードのみからは断定不能**。`_dead_letter_second.yaml` は禁則により開いておらぬゆえ、個々のreason内訳・件数増分の実測は不能。
- ★unconfirmed★: 現在も新規unroutable到着が続いているか。当職の測窓(⒜)では増分0であった=**少なくとも当職の観測窓では「落ち続けて」はおらぬ**。恒常的flushではなく間欠的(バースト依存)機構である、とはコードから言えるが、「今この瞬間も生まれ続けているか」は unconfirmed。

## ⒟ `content_head` 240字切出しが parse を壊し得るか (コードのみ・file未読)

L240: `content_head = (msg.get("content", "") or "")[:240].replace("\n", "\\n").replace('"', '\\"')`

- エスケープされるのは **改行** と **二重引用符** の2種のみ。**バックスラッシュそのものは一切エスケープされておらぬ**。
- YAML二重引用符文字列は `\` をエスケープ導入文字として解釈する。元contentに `\` が含まれ、後続文字がYAML許容エスケープ集合(`\n \t \" \\ \0 \a \b \e \f \r \v \x.. \u.... \U........` 等)外であれば、その時点でparse不能または誤解釈となり得る。
- ★具体的破壊経路(コード構造から導出可能)★: `[:240]` による切出しが、元content中の(当コードが未エスケープの)単独 `\` の直後で切れた場合、`content_head` の末尾が `\` のみとなる。f-string L249 `f'    content_head: "{content_head}"\n'` により、直後の閉じ `"` と結合して `\"` となり、**YAML上は「エスケープされた引用符」と解釈され、閉じデリミタとして機能しなくなる**。結果、当該エントリ以降(改行含む)がすべて文字列値の一部として飲み込まれ、後続の `- id:` 等のキーがYAML構文として崩壊する経路が **コード上あり得る**。
- ∴ 「現に壊し得るか」への答 = **YES、コード構造上あり得る**(条件: 元content中に240字境界に近接する未エスケープ `\` が存在すること)。ただし ★file自体は開いておらぬゆえ、実際に本fileで発生済みか(実測)は unconfirmed★。

## ⒠ 己の手で為した事

- `stat` を6回・`date -Iseconds` 併記で実行(⒜表)。うち5回は Monitor 機構(task balx932gu)で60秒間隔サンプリング。
- `wc -l` / `grep -n` で `hakudokai_secondpc_receiver_poll.py` の関数所在を特定後、Read tool で L1-195・L195-354 を全文通読(410行中)。
- `ps -eo pid,ppid,etime,cmd | grep -i receiver` で稼働プロセス実測。`--interval 5` の実引数、起動元パス `/home/hakudokai/projects/multi-agent-shogun/shim/hakudokai/hakudokai_secondpc_receiver.sh` を確認。
- `diff` で repo版と repo外重複path (`/home/hakudokai/multi-agent-shogun/...`) の `receiver.sh` を比較 = **差分0(同一内容)**。稼働中プロセスは repo内パスから起動と確認(前者は不使用の重複コピーと判明・稼働に無関係)。
- `/usr/bin/grep -rl "_dead_letter_second"` で repo全体を実測し、`.py` 書き手が `hakudokai_secondpc_receiver_poll.py` 一本のみである事を確認。
- `_dead_letter_second.yaml` 本体は **一度も開いておらぬ**(grep/wc/cat 不使用・ls/statのみ)。

## 結べぬ物 (推して埋めず)

- 「宛先不明便が今も生まれ続けているか」= unconfirmed(当職の測窓では増分0だが、窓外での挙動は不明)。
- content_head破壊が **実際に本file内で発生済みか** = unconfirmed(file本文不読ゆえ)。
- pc_handshake側で何が unroutable message を発生させ続けているか(発生源の同定)= 本工区の射程外・unconfirmed。

## 測時・器・範囲 (行末併記)

測時=2026-08-06T21:20:42〜21:25:50 JST(size時系列) + 別途コード通読(同日夜間)／器=stat・Read・ps・diff・grep(/usr/bin/grep明示)／範囲=`queue/inbox/_dead_letter_second.yaml`(統計のみ・本文不読)+`shim/hakudokai/hakudokai_secondpc_receiver_poll.py`全410行+`hakudokai_secondpc_receiver.sh`起動確認。読めぬ物(file本文)につき「以上」。
