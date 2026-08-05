# scripts/karo_second_send_iincho.sh 是正の全文保全 (commit できぬ file の 内容だけを git へ残す)

作成 = 家老second / 測時 2026-08-05T18:32:15+09:00 (date -Iseconds 実行結果)
将軍second 下命 (2026-08-05T18:31:15+09:00) = 「是正の写しを取れ。何を直したかも素の文で残せ。file が消えても再現し得るように」

証拠は素の文字で記す (code fence は説明にのみ用いる。将軍second 下命 2026-08-05T18:23 前後)。

## 一 なぜ この file だけ 別扱いか

対象 = scripts/karo_second_send_iincho.sh (家老second → 委員長 の canonical uplink helper)
状態 = .gitignore 配下 (whitelist 方式の :7 の * に当たり、! が無い)。00E 既知六件のうちの一件。
∴ git add が拒む。-f で押し通せば通るが、00E が委員長殿の裁定待ちである以上、押し通さぬ。

∴ **file 自体は commit できぬ。が、内容を書いた .md は commit できる**
(docs/incident_logs/*.md は whitelist で救われておる)。
∴ 本 file が「消えても再現し得る」ための唯一の git 内の写しが これである。

## 二 凍結の実測

原本 scripts/karo_second_send_iincho.sh
  168行 / 8122 bytes / sha256=b0926ca02e88b43f06fa0fc6a740ab575fff6f69eb227924ffb94db1a6b3c867

写し (scratchpad・cp -p ゆえ mtime 保存)
  FROZEN_karo_second_send_iincho_with_responsebody_fix_20260805.sh
  168行 / sha256=b0926ca02e88b43f06fa0fc6a740ab575fff6f69eb227924ffb94db1a6b3c867 (原本と一致)
  mtime 2026-08-05 18:27:00.568712069 +0900

**写しの弱み (下命への正直な但し書き)**: scratchpad は /tmp 配下かつ session 固有である。
再起動・session 終了で失われ得る。∴ **cp だけでは「凍った」と言えぬ** —— 本 .md が git 内に
在って初めて、再現の保証が残る。写しは短期・本 .md は恒久、という二段で保全する。

## 三 何を直したか (4行 + 註釈3行)

### 直す前 (165行目付近・else 節)

  fatal "LIVE POST failed: http_code=${HTTP_CODE:-<empty>} curl_stderr=${CURL_ERR:-<empty>}"

### 直した後

  # 失敗理由は PostgREST の response body にしか無い(message/details/hint)。
  # HTTP エラー時 curl_stderr はほぼ常に空ゆえ、body を落とすと「400 とだけ判って理由が判らぬ」
  # 状態になる —— 本 script が成功側で塞いだ「証拠が返らぬ」病の、失敗側での再発である。
  fatal "LIVE POST failed: http_code=${HTTP_CODE:-<empty>} curl_stderr=${CURL_ERR:-<empty>} response_body=${RESPONSE_BODY:-<empty>}"

差分は これだけである。RESPONSE_BODY は既に 144行目で代入済 (RESPONSE_BODY="$(cat "$RESPONSE_FILE")")
であり、成功側の分岐 (159行目) では既に使われておった。**失敗側だけが 捨てておった。**

## 四 機序 (なぜ この欠陥が 見えなかったか)

本 script は設計時から「沈黙送達を塞ぐ」ことを目的としており、成功側では
「http_code は 201 だが id が返らぬ」を silent success として fatal に落とす念の入れようであった。
∴ **成功側は 二重に守られ、失敗側は 素通りであった。**

> 守りを入れた者は、己が想定した経路を守る。想定の外側は、守った事実によって かえって
> 「守られておる」と読まれる。

curl_stderr は HTTP エラー (4xx/5xx) では ほぼ常に空である —— sb_curl は HTTP 応答を
正常受信しておるゆえ、stderr に書く事が無い。∴ 従来の fatal は **構造的に 常に空の欄を
表示しておった**。欄は在ったが、そこに理由が入る事は 原理的に無かった。

## 五 実地で どう効いたか (是正の直後)

是正前 = LIVE POST failed: http_code=400 curl_stderr=<empty>
  → 400 とだけ判る。原因不明。

是正後 = LIVE POST failed: http_code=400 curl_stderr=<empty> response_body={"code":"23514",...,
  "message":"new row for relation \"pc_handshake\" violates check constraint \"pc_handshake_message_type_check\""}
  → 原因が一発で判明 = --type report_received が DB の check constraint に違反。

対処 = helper 既定値 status_update で再送 → 201 着弾 id=6336aa45-af72-47ae-b8a3-8d79dabb426c

## 六 採らなかった案 と その理由

案 = helper 側に message_type の許容値一覧を持たせ、POST 前に弾く。
不採用の理由 = **DB の check constraint が正本である。helper に写せば名簿が二つになる。**
本日 SecondPC 隊で数えた病 (agent 登録名簿が pane_registry.yaml と receiver poll.py の二つに
分かれ、片方だけ直った結果 便が二つの名簿の間で死んだ) と 同型を 新たに作る事になる。
∴ helper は投げ、DB が拒み、理由を そのまま返す —— が正しい形である。

## 七 未了 (完了主張ではない)

- 軍師second 監査 未了。本是正は稼働中の是正の保全であって、完了ではない。
- .gitignore への ! 追加は 00E (委員長殿 裁定待ち) の範囲ゆえ 触れておらぬ。
- ∴ 裁定が下りるまで、原本は working tree にしか無い。checkout 一発で消える状態が続く。
  **本 .md は その状態が続く間の 保険である。**
