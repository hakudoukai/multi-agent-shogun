# 専務殿への経路の実測 (足軽6号、2026-08-06・家老second下命)

## 境・限界・未測 (冒頭)

読取のみ(grep/cat/ps/diff実施のみ)。watcher(inbound/outbound双方)を起動・停止・編集していない。
専務殿へは試験含め一切送信していない。hakudokai-devへは一文字も書いていない。

測時=2026-08-06T09:21:41+0900(date -Iseconds実行結果)。HEAD=147d0d2f3cdd141175efa748ec5b332db792aeee
(git rev-parse HEAD実行結果)。

## ⒜ registry (実測・独立確認)

$ /usr/bin/grep -n "senmu\|専務" queue/pane_registry.yaml
(該当なし・0件)
**∴ 家老second殿の一次実測「不在」と一致。**

## ⒝ scripts/配下の専務宛helper

$ /usr/bin/grep -rln "senmu" scripts/
(該当なし・0件)
**∴ inbox_write.sh経由(canon gate)での専務宛送信は不可能——registryに無き宛先は弾かれる
(本日の他工区で確認済の設計と一致)。**

## ⒞ shim/hakudokai/senmu_desktop_route_watcher.{py,sh} (実在・稼働確認)

$ ls -la shim/hakudokai/ | grep -i senmu
senmu_desktop_route_watcher.py (8951 bytes・本日00:40更新)
senmu_desktop_route_watcher.py.bak-floor-seq137986-20260804T105001 (旧版)
senmu_desktop_route_watcher.sh

**内容(冒頭docstring実読)**=「Role-specific pc_handshake watcher pair」——inbound=DB row(pc_handshake)
→role別job→既存の監査済Windows actuator。outbound=role起源のDB row→local durable receipt ledger。
role=`senmu_codex_second`。宛先はSupabaseの`pc_handshake`テーブル(to_pc=senmu_codex_second)を
経由し、Windows側PowerShell(`trigger_senmu_role_bridge.ps1`)がactuatorとして動く設計。

$ ps -eo pid,ppid,lstart,args | grep -i "senmu_desktop_route_watcher" | grep -v grep
853230/853260 (inbound、2026-08-05 12:32起動、現に稼働)
3759956/3760024 (outbound、2026-08-04 10:50起動、現に稼働)

**∴ inbound/outbound双方とも★現に稼働中★——read-onlyのps確認のみ(起動・停止いずれも行っていない)。**

$ diff senmu_desktop_route_watcher.py.bak-floor-seq137986-20260804T105001 senmu_desktop_route_watcher.py
現用版(126行)は旧版(104行)に対し、①`EXPECTED_TITLE`をsha256検証付きへ強化②`SENMU_DESKTOP_MIN_SEQ`
による下限floor追加③`terminal_isolated`状態の追加、の3点差分あり——★現に開発が進行中の設計★。

## ⒟ 三値判定

**②経路は在るが当隊の権の外。** 理由=`senmu_desktop_route_watcher.{py,sh}`という物理的な経路
(Supabase pc_handshake経由のWindows desktop bridge)は★現に存在し稼働中★だが、①これは
`inbox_write.sh`のcanon gate/registryを経由する当隊の標準送信経路とは★別系統★(直接pc_handshake
テーブルへINSERTする必要があり、当職の権限・下命の禁(DB書込)に触れる)②`EXPECTED_TITLE_SHA256`等の
厳格な検証機構を見るに、★汎用メッセージングではなく特定の自動化floor専用に設計された狭い経路★である
公算が高く、一般的な「専務殿へ便を送る」用途に転用してよいかは設計者(足軽3号系統・当職未確認)の
判断を要する。

## ⒠ 零に理由・限界

registry/scripts/双方で「見つからず」であり「無い」とは断定しない——探索範囲は`queue/`・`scripts/`
配下のgrepに限られ、他PCの設定・未読のdocs等に別経路が記載されている可能性は排除できない。

## 【本工区で己が直した誤り】

初稿で「経路無し(③)」と即断しかけたが、shim/hakudokai/配下の実file確認で稼働中watcherを発見し、
「経路は在るが権の外(②)」へ書き直した(inbox_write.sh経由の不在のみを見て判断せず、物理的な
経路の実在まで確かめ直した)。

## ★母集団漏れの自己申告★

1. `trigger_senmu_role_bridge.ps1`(Windows側スクリプト)の中身は読んでいない(hakudokai-dev不触の
   禁に加え、Windows側filesystemへのアクセス自体が当職の権限外)。
2. pc_handshakeテーブルへの直接INSERTが技術的に可能か(権限・スキーマ)は検証していない
   (DB introspection自体が下命の範囲外・別件のhold対象)。

## 監査体制

暫定二者制(軍師+Gemini)。Codex leg停止中(2026-07-21事案)。

以上、専務殿への経路の実測への応答。watcher・hakudokai-dev・専務殿への送信いずれも不触。
