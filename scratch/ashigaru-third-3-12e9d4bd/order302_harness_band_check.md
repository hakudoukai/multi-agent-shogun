## §的 ★harness の帯 L636-639 が三受け口版で現に満たされるかを 符だけで断ずる★
## §A 頭書
- as_of 2026-09-11T17:08:30+0900 ／ 讀取 10/12・焚 0・走 0・★当て 0（apply も --check も打たず）★・製品樹へ書込 0・DB 0
- 席 ashigaru-third-3・板 12e9d4bd・本紙は前紙を書き換へず新たに鋳た
- 令 = scratch/k3_orders/order302_a3.txt 11 行(wc)/12 片・1,506 B・sha256頭16 cfe6d519dfae7e8a（己が実読）
- ★家老便に本紙の紙名の指定は無い ∴ 名は己が付けた（條 四百九十九の趣旨）★
- 母① harness = origin/main:backend/tests/test_c1_dml_migration_pkg_isolated_harness.py（git blob sha1頭16 1134bc165e1a85cc・702 行(wc)/703 片）
- 母② 受け口 = 8a23afa8a:backend/api/treatment_validation.py L4295-4383（89 行・三受け口版・前紙 order301 で実読）
- HEAD 1ad4edfbadc69191（不動）／origin/main 50a9e20c3e978d2e／同 py の origin/main blob sha256頭16 b23c0298ebfaf5c1・15,009 行(wc)
## §B ㋐ 帯の逐語 ―― L636-639（★表示名は伏す★）
- > 636:    """finding001の最終証明: 本物の _resolve_comment_documentation_field_id を
- > 637:    直接importし、実際のKENSA comment 2件 (★表示名二つ・伏す★、
- > 638:    いずれもdocumentation_field_name未設定=field_name=Noneで呼ばれる) が
- > 639:    409を出さず、移行後の唯一のactive行idへ一意に解決されること。"""
## §C ㋑ L641 の呼（2 渡し）が入る枝 ―― 行番は 8a23afa8a の当該 py
- L4296 の signature は三受け口（位置3 = field_name は既定 None）∴ L641 の 2 渡しは位置3 を渡さぬ
- 枝 = L4323 偽 → L4325-4331 問ひ（★set_code のみで絞る★）→ L4332 rows ← resp.data or [] → L4333 偽
- → L4335 active_rows を篩ふ → L4336 偽 → ★L4350 if field_name: は偽★ → L4367 真
- ★返る物の形 ＝ 行の id 一個（rows の要素の "id" 鍵の値・str() で比べ得る）。値は紙へ写さぬ★
## §D ㋒ 「唯一の active 行」に成る条件の逐語
- > 4335:    active_rows = [r for r in rows if r.get("is_active")]
- > 4367:    if len(active_rows) == 1:
- > 4368:        return active_rows[0].get("id")
- active 行が 2 件以上の時 ＝ L4369-4381 の raise HTTPException(status_code=409, … "comment_documentation_identity_ambiguous" … "active_field_count": len(active_rows))
- 三値 ―― 「409 を投げる枝が符に現に在る」＝★現に在る★／「実行時に其処へ入るか」＝★測定不能★（走 0 ゆゑ）
## §E ㋓ 締めの三値
- ★測れぬ★
- 根 ―― L632 の assert (total, active) == (7, 1) は _kensa_counts の母（set_code ＋ migration_ref の二条件）から見た数であり、resolver の母（set_code のみ）と同じ母である事は符だけでは閉ぢぬ（床⑷）
- 添 ―― seed 7 行の set_code は 2 種で ★KENSA の set_code を負ふ seed 行は 0 件★（己が数へた）∴ KENSA を負ふ行は移行が作る物のみと読めるが 其の件数は走らねば測れぬ
## §F ㋔ 陽性対照（同じ命形・出力行数と exit を併記・己が当たつた）
- 命形 = timeout 300 git -C /mnt/c/DentalBI show origin/main:(harness) | /usr/bin/grep -cE "(^|[^A-Za-z0-9_])(名)([^A-Za-z0-9_]|$)"
- 当たる名 expected_active_id → 2 行・exit 0 ／ 当たる名 _kensa_counts → 16 行・exit 0 ／ 当たらぬ名 ZZNoSuchNameZZ → 0 行・exit 1
## §G 床の守り
- 讀取 10/12・焚 0・走 0・当て 0・製品樹へ書込 0・DB 0・一時 file 0・リダイレクト 0・値/表示名/患者本文 0 行
- 本紙 35 行(wc)/36 片・as_of は紙の中身を固めた後に date で取つた
