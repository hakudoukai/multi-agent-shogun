# watcher log 偽 の是正案 ―― 案b(log を実体へ) 提示

- 発注: 総監督→Mac事業部長 seq321154(2026-09-16T23:30:39) → Mac事業部長→家老mac seq321169(23:32:29)
- owner: **家老mac**(前便 seq321413 で誤つて Mac事業部長へ返した。seq321529 で引き、受け持ちを己へ戻した)
- 種別: **提示のみ。据ゑて居らぬ**(working tree 無変更・commit/push 無し)
- 刻: 2026-09-17T00:32:06+0900  / HEAD=f2bfa26a163dbee334861bd80bb0bd8affa0636d

## 一 疵の実体(逐語 + 行番号)

収集器(python・`scripts/inbox_watcher.sh` L501-509)は **busy を問はず**特種便を悉く既読にする:

```
    if specials or expire_supersede_changed:
        for m in messages:
            if not m.get("read", False) and m.get("type") in special_types:
                m["read"] = True
```

然る後、殻側の二箇所が「**次周期へ繰延**」と刷る:

- L572  `[SKIP] Agent is busy — /clear deferred to next cycle (agent=$AGENT_ID)`
- L1245 `[SKIP] Agent $AGENT_ID is busy — /clear (clear_command) deferred to next cycle`

**次周期は無い。** 便は既に read=True ゆゑ二度と `unread` に入らぬ。∴ log は偽。

## 二 負試験 ―― ★実史で測つた★(生席を壊さぬ為、生の busy 注入は行はず)

- 歩き根: `logs/inbox_watcher*.log` **8本**(母數)
- 「deferred to next cycle」と刷つた回数 = **★16★**(L572形 6 / L1245形 10)
- 内 **其の便が次周期に真に送られた = ★0★**
- 内 別経路(task_assigned の CONTEXT-RESET)が後で来ただけ = 13
- 内 何も続かず(箱は既読のまま) = 3
- **陽性対照**: log 全体の `[SEND-KEYS] Sending CLI command to … : /clear` = **12行**在り
  → 器は真の送出を見得る。「0」は器の盲目に非ず。
- **判別の締め直し(己の疵)**: 初回、CONTEXT-RESET 経路が刷る同じ `[SEND-KEYS]` 行を「真の再送」と数へ 1 と出した。
  窓内で先に現れた方を採る形へ直し **0** と確定。★別経路の刷りを己の検出語が拾ふ★

**此の數が意味せぬ事**: 13/3 は「/clear が一度も飛ばなかつた」の意に非ず(別経路・後の新便で飛んだ場合を含む)。
測つたのは「**其の便が繰延されて次周期に送られたか**」の一点のみ。

**生の busy pane 注入を行はぬ理由**: 検めと watcher の判定の間に席が idle へ落ちれば /clear が真に飛び、
稼働中の席の文脈を壊す。★稼働中 agent を憶測で止めない★(FKI-KARO-VISUAL-ASHIGARU-PATROL-20260807)に触れる。

## 三 案b の実体(1行×2・挙動変化 無し)

    --- docs/evidence/karo-mac-watcher-log-gi-zesei-20260917/inbox_watcher.sh.before	2026-09-12 23:52:47
    +++ docs/evidence/karo-mac-watcher-log-gi-zesei-20260917/inbox_watcher.sh.after	2026-09-17 00:31:07
    @@ -569,7 +569,7 @@
         # clear_command inbox processor also checks busy, but this is a defense-in-depth guard.
         # Sending /clear during Working destroys in-progress context and causes data loss.
         if [[ "$cmd" == "/clear" ]] && agent_is_busy; then
    -        echo "[$(date)] [SKIP] Agent is busy — /clear deferred to next cycle (agent=$AGENT_ID)" >&2
    +        echo "[$(date)] [SKIP] Agent is busy — /clear DROPPED, not deferred (special marked read at collection; no retry) (agent=$AGENT_ID)" >&2
             return 0
         fi
     
    @@ -1242,7 +1242,7 @@
                     # Busy guard: skip /clear if agent is currently processing.
                     # Sending /clear during active work destroys in-progress context.
                     if agent_is_busy && [[ "$AGENT_ID" != "shogun" ]]; then
    -                    echo "[$(date)] [SKIP] Agent $AGENT_ID is busy — /clear (clear_command) deferred to next cycle" >&2
    +                    echo "[$(date)] [SKIP] Agent $AGENT_ID is busy — /clear (clear_command) DROPPED, not deferred (marked read at collection; no next cycle)" >&2
                         continue
                     fi
                 fi

- 差分行数(+/-) = 4 ＝ **2行の置換のみ**
- `bash -n` = **rc 0**(after 実体で実行)

## 四 変更前後 SHA(full)

| 物 | path | 行 | SHA256 |
|---|---|---:|---|
| 変更前(working tree の写し) | `docs/evidence/karo-mac-watcher-log-gi-zesei-20260917/inbox_watcher.sh.before` | 1613 | `f8a0160c0bff47c9c151fc53d8c1c811e29bd0f86ee3f2b21e41b6cd5699a40e` |
| 変更後(案の実体) | `docs/evidence/karo-mac-watcher-log-gi-zesei-20260917/inbox_watcher.sh.after` | 1613 | `12dfe1700e6bef6222c3ec882b505e740135a7cfea7e3cd44a2f380d7f9adc99` |
| 差分 | `docs/evidence/karo-mac-watcher-log-gi-zesei-20260917/zesei.patch` | - | `0f8143e36ef19d9b72159e8e6cc4c0d0ad206a10da1210816bf507e6bd49bce9` |
| 生きて居る器(此の刻) | `scripts/inbox_watcher.sh` | 1613 | `f8a0160c0bff47c9c151fc53d8c1c811e29bd0f86ee3f2b21e41b6cd5699a40e` |

**註**: 「変更前」は **working tree の版**であり HEAD の版ではない。当器は既に staged-modified(`M`)＝**既存 dirty**。
案は其れに**触れて居らぬ**(既存変更と混ぜぬ の令を守る為、working tree を書き換へず別実体として置いた)。

## 五 戻し方(一手)

```
cp -p docs/evidence/karo-mac-watcher-log-gi-zesei-20260917/inbox_watcher.sh.before scripts/inbox_watcher.sh
shasum -a 256 scripts/inbox_watcher.sh   # → f8a0160c0bff47c9c151fc53d8c1c811e29bd0f86ee3f2b21e41b6cd5699a40e に戻る
```

据ゑて居らぬ故、**今は戻す物が無い**。据ゑた後に此の一手で原状へ戻る(byte 一致)。

## 六 此の案が **直さぬ** 物(★明示★)

1. **破棄其の物は直らぬ。** 案b は log を正直にするだけで、busy 時の clear_command は依然 **消える**。
2. 真の治療は **案a**(注入成功の後に read=True へ順序を直す)。之は**挙動変化**ゆゑ変更統制の事前1便が要り、
   収集器(python)と殻の間で「送れたか」を返す道が要る＝1行では済まぬ。**別発注を要す**。
3. L569-570 / L721 の**註釈も「defer」と書いて居り同じく偽**。本案は註釈に触れて居らぬ(発注=1行の故)。
   直すなら同束で。
4. 16回の母數は **logs/ に残つて居る分のみ**。回転で落ちた分は測れて居らぬ。
