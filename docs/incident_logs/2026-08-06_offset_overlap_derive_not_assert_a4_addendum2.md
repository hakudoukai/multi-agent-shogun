# 足軽4号 → 家老second: offset overlap導出票 追補2（③「閉じた」主張の撤回・needle:216独立検証）

下命=17:49:34便③④（guard列挙節の「閉じた」主張を撤回・訂正後の順=変えず）。

## §0 三sha+worktree欄

- worktree path=`/tmp/resimg-verify4-cycle2-20260806`
- 直前HEAD=`e1ace1cb4eb456413b2348d490e2bdb3f5acd867`（addendum1提出時点・不変）
- 提出直前確認=下記実測

```
$ date -Iseconds
2026-08-06T17:53:00+09:00
$ git rev-parse HEAD
e1ace1cb4eb456413b2348d490e2bdb3f5acd867
$ git status --short
(空・変更なし)
```
★本便はcode/test file変更なし（前便の記録の訂正のみ）★。

## §1 ②needle:216 独立検証（家老second殿の実測を根にせず、当職が独立に実読）

`backend/db/migrations/booking_concurrency_root.py`実読（当職worktree内・行番号は当職grep実測）:

```
214: def _appointments_ddl_without_broken_unique() -> str:
     needle = "            UNIQUE(clinic_id, unit_id, start_time, status)\n"
     if needle not in ddl: raise RuntimeError("expected appointments UNIQUE constraint not found")
     return ddl.replace(...)   # ★table制約を除いたDDLを返す★
240: conn.execute("ALTER TABLE appointments RENAME TO _appointments_pre_root")
241: conn.execute(_appointments_ddl_without_broken_unique())   # ★除去済DDLで再作成★
247: conn.execute("DROP TABLE _appointments_pre_root")
253: conn.execute("CREATE UNIQUE INDEX uq_appointments_active_exact_start "
                   "ON appointments(clinic_id,unit_id,start_time) "
                   "WHERE status NOT IN ('cancelled','no_show')")   # ★再作成後、単独で作られる唯一のunique★
```

rename→`_appointments_ddl_without_broken_unique()`で再作成→列コピー→drop→
`uq_appointments_active_exact_start`のみ新規CREATE、の順を当職自身の実読で確認した。
∴ ★post-root（root-cure適用後）に旧table制約`UNIQUE(...,status)`は残らず、DB層のunique guardは
部分index`uq_appointments_active_exact_start`一つのみ★——家老second殿の②を当職の実読で
独立に確認した（家老second殿の実測を根にせず、当職自身のgrep+実読で導いた）。
★needle不在ならRuntimeErrorで移行が止まる=陽性対照がmigration code自体に埋め込まれている事も確認済★。

## §2 ③「閉じた」の撤回・訂正後の三行

前便(addendum1)§3の「DB層＝★列挙により閉★」の★「閉」の語を撤回する
（結論=DB層のunique guard=1つ、は不変）★。

撤回理由=述語(検索条件)が★一形のみ★(`CREATE UNIQUE INDEX`)であり、除外が`*.py`のみ
(`.sql`は当職も前便で未検)だった——「閉じた集合を全部見た」の証明には未だ達していなかった。

★当職独立実測（.sql・前便addendum1では未検だった母集団を本便で追加確認）★:
```
$ find backend -name "*.sql" | wc -l
156
$ grep -rln "appointments" backend --include="*.sql" | wc -l
2
$ grep -rln "appointments" backend --include="*.sql"
backend/db/migrations/007_daily_kpi_fields.sql
backend/db/migrations/001_create_tables.sql
$ grep -rniE "unique|trigger|index" backend --include="*.sql" | grep -i appointment | wc -l
0
```
★.sql側でもappointments関連のunique/trigger/indexは0件——結論(DB層unique guard=1つ)は
当職の独立実測でも崩れず維持される★。ただし「列挙で閉じた」の主張自体は撤回し、
下命④の書式どおり三行に置き換える:

> ㈠ 二形(`CREATE UNIQUE INDEX`／table制約`UNIQUE(clinic_id,unit_id,start_time,status)`)とも
>   start_timeを含む ∴ offset(15分ずれ)には構造上無力（定義から・test不要、docstring既記載）。
> ㈡ DB層のunique guard＝1つ（`uq_appointments_active_exact_start`部分index）。旧table制約は
>   root-cureが除去する（`_appointments_ddl_without_broken_unique`:214-241実読で導出、本便§1で
>   当職独立確認）。`.py`462file＋`.sql`156file（当職独立実測、母集団=backend配下非test）で
>   これ以外のappointments関連unique/trigger/時間重複CHECKは検出せず。
> ㈢ application層(service層のin-memory conflict検査等)にguardが存在するか否かは★UNMEASURED★。
>   「列挙で閉じた」は本便時点で★未確立★とし、application層の精密列挙は次工区の候補として残す。

★当職自身が数えた462/156の数も、それ自体を「閉じた証」の根にはしない
（家老second殿の令「55も462も根にするな」に従う=㈠は定義からの導出、㈡は実測+導出、
㈢は未測、と性質の異なる三行を崩さず並べる事を優先した）。

## §3 順序確認（下命④・変えず）

①§3構造の一行=完了済(addendum1§1)。②docstring一行=完了済(commit`21f7a76`・addendum1§2で報告)。
③本節訂正=本便(addendum2)で完了。④⑶台帳四欄=完了済(別便
`docs/incident_logs/2026-08-06_ledger_site_reachable_case_a4.md`)。
∴ 下命④の四段は本便にて全て充足。

## §4 GREEN再確認（本便のため当職が実際に再実行・前便の数値の転記ではない）

```
$ date -Iseconds
2026-08-06T17:57:40+09:00
$ python3 -m pytest backend/tests/test_reserveimage_cycle2_barrier_concurrency_a4.py -q
5 passed in 15.21s
```
（code/test file変更なしゆえ前便addendum1§5(11.75s)と件数は同一・実行毎の秒数差は許容範囲）。

## §5 禁則遵守

本便はcode/test file変更なし(記録の訂正のみ)。production不触。push/PR/main/本番=一切なし。
