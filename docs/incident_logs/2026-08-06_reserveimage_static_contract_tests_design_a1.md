# F1〜F3 静的契約 test 設計 + source (足軽1号)

- 断面秒: 2026-08-06T09:54:06+0900
- 下命: 家老second msg_20260806_095028_24600cdb「静的契約 test の 設計と source（適用は権が立ちて後）」
- 依拠: `docs/incident_logs/2026-08-06_reserveimage_cycle2_3claims_ternary_a1.md`
  (足軽1号 自筆・78行・sha256=35aedb0e7c6550aa82ba0ee285e0d478ef810bfa7b2abf8393f2c1ac3206d5e3・commit 147d0d2、
  軍師second PASS 09:16:43 済)。以下 F1/F2/F3 = 当該 doc の ①②③ に対応。
- ★本 doc は 設計と source に留まる。適用・実行・apply・hakudokai-dev 書込み・DB 接続・commit(当職以外) は一切なし★。
- ★source は未実行 (下命通り「走らせるな」順守。ゆえに以下 code は syntax 上の設計であって、動作実証済ではない)★。

## 母集団宣言 (読了範囲)

- 読んだのは上記 F1/F2/F3 判定 doc (78行全行) のみ。hakudokai-dev 側の実 file (appointment_service.py /
  booking_concurrency_root.py / booking_service.py 本体) は本工区では ★再取得していない★
  (禁則「hakudokai-dev へ一文字も書くな」を安全側で解し、read も含め当該 repo への接触を本工区中は行わなかった)。
  ∴ 以下の設計・行番号引用は ★引用元 doc に記載された file:line をそのまま用いる★ もので、
  当職が本工区で独立に再確認したものではない。この点は限界として明記する。
- 足軽4号の別便「不能の因」とは論点が異なる (当職は test の形と脆さのみを扱う。実行不能の理由には立ち入らない)。

---

## F1 (①): staff 経路 (appointment_service.py) に idempotency 機構が未配線

### (a) 契約設計

**契約**: `appointment_service.py` の `create_appointment` 関数本体が、idempotency 関連の名前
(`acquire_idempotency` / `complete_idempotency` / `idempotency_key` のいずれか) を
一つも参照していなければ FAIL。

**方式**: AST 走査 (grep でなく `ast` を使う理由 = コメント・docstring 内の文字列一致による
偽陽性を避けるため。ただし後述の通り偽陰性は別に残る)。

### (b) source (未実行・設計のみ)

```python
import ast

IDEMPOTENCY_SYMBOLS = {"acquire_idempotency", "complete_idempotency", "idempotency_key"}


def contract_f1_staff_idempotency_wired(source: str, target_fn: str = "create_appointment") -> bool:
    """契約: target_fn 内に IDEMPOTENCY_SYMBOLS のいずれかへの名前参照が存在すること。
    True = 契約成立 (PASS)。False = ①の欠陥を再現 (FAIL)。
    対象関数が見つからなければ LookupError (契約適用対象なし = 別問題)。
    """
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == target_fn:
            referenced = set()
            for sub in ast.walk(node):
                if isinstance(sub, ast.Name):
                    referenced.add(sub.id)
                elif isinstance(sub, ast.Attribute):
                    referenced.add(sub.attr)
                elif isinstance(sub, ast.arg):
                    referenced.add(sub.arg)
            return bool(referenced & IDEMPOTENCY_SYMBOLS)
    raise LookupError(f"{target_fn} not found in source")
```

### (c) 「欠陥が在れば必ず FAIL か」

★書ける★。①の欠陥定義そのものが「IDEMPOTENCY_SYMBOLS への参照が0件」であり、本契約の FAIL 条件と
定義上一致する。∴ ①が現状の形 (完全不参照) で存在する限り、本契約は必ず FAIL する。
ただし ★将来 PASS へ寝返る形での偽陽性 (=偽の安全) が起こり得る★ (次項参照)。

### 脆さ

- **名前依存**: `acquire_idempotency` 等を別名 (`claim_idem`, `dedupe_request` 等) で実装されれば
  スルーで PASS してしまう。
- **参照はするが機能しない実装**: 同名の関数を import・呼出しても、それが no-op スタブや到達不能な
  分岐内であれば、本契約は「参照あり」で PASS するが実際の重複排除は機能していない
  (契約は「名前の存在」のみを見ており「実効性」は見ていない)。
- **対象関数名の変更**: `create_appointment` がリネーム・分割されれば `LookupError` となり、
  契約自体が「適用不能」に陥る (FAIL でも PASS でもない第三状態。これを FAIL 扱いにするかは
  別途の運用判断=当職は裁定せず、契約実装の呼出側判断に委ねる)。

---

## F2 (②): apply_booking_concurrency_root は FK check 失敗時に已に commit 済・自己 rollback 無し

### (a) 契約設計

**契約**: `apply_booking_concurrency_root` 関数内で `conn.commit()` が呼ばれた ★後★ に
`"foreign_key_check"` を含む `conn.execute(...)` 呼出があるなら、その commit と
(FK check 失敗によって発生する) 直後の `raise` との間に `conn.rollback()` 呼出が
最低1つ存在すること。commit より前に FK check が完結している場合、または FK check
自体が存在しない場合は本契約の対象外 (別の契約が要る領域=対象外は PASS 扱いとする)。

**方式**: AST 上の行番号順序による ★近似★ (ヒューリスティック)。真の制御フロー解析
(try/except の到達可能性グラフ) ではない — 理由は下記脆さ参照。

### (b) source (未実行・設計のみ)

```python
import ast


def contract_f2_fk_check_has_rollback_guard(source: str, target_fn: str = "apply_booking_concurrency_root") -> bool:
    """契約: commit() 後に foreign_key_check が走るなら、その commit〜(FK失敗由来と思われる)raise の
    間に rollback() 呼出が最低1つあること。
    True = 契約成立 (PASS、または契約の対象外で判定不能=非該当としてPASS扱い)。
    False = ②の欠陥を再現 (FAIL)。
    """
    tree = ast.parse(source)
    fn = next((n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == target_fn), None)
    if fn is None:
        raise LookupError(f"{target_fn} not found in source")

    commit_lines, fk_lines, rollback_lines, raise_lines = [], [], [], []
    for node in ast.walk(fn):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr == "commit":
                commit_lines.append(node.lineno)
            elif node.func.attr == "rollback":
                rollback_lines.append(node.lineno)
            elif node.func.attr == "execute":
                for a in node.args:
                    if isinstance(a, ast.Constant) and isinstance(a.value, str) and "foreign_key_check" in a.value:
                        fk_lines.append(node.lineno)
        if isinstance(node, ast.Raise):
            raise_lines.append(node.lineno)

    if not fk_lines or not commit_lines:
        return True  # 契約の対象外 (FK check または commit そのものが不在)

    last_commit = max(commit_lines)
    for fk_line in fk_lines:
        if fk_line <= last_commit:
            continue  # FK check が commit より前 = ②の形ではない
        guard_candidates = [r for r in raise_lines if r >= fk_line]
        guard_line = min(guard_candidates) if guard_candidates else float("inf")
        if not any(last_commit < rb <= guard_line for rb in rollback_lines):
            return False  # FAIL: ②の欠陥を再現 (commit後・FK check失敗・rollback不在)
    return True
```

### (c) 「欠陥が在れば必ず FAIL か」

★書ける、ただし範囲限定付き★。判定 doc に記録された「commit(284) → FK check(293-295、try/except/finally 外) →
rollback 呼出 0件」という ★実測された具体形★ に対しては、本契約は必ず FAIL する
(commit行 < fk_line、かつ rollback_lines が空ゆえ `any(...)` が False → FAIL)。
∴ ★この具体的な欠陥形に対しては FAIL 保証あり★。
ただし ★一般に「同機能を壊す別の書き方」全てを捕捉する保証ではない★ (次項)。

### 脆さ

- **行番号ヒューリスティックの限界**: 真の try/except スコープを見ておらず、行番号の前後関係のみで
  判定している。commit と FK check の間に ★無関係な rollback() 呼出★
  (例: 別の try/except ブロックが同一関数内にあり、それが偶然行番号レンジ内に入る) があれば、
  実際には FK 失敗経路を保護していなくても本契約は PASS してしまう (偽陰性)。
- **API 形の変更に弱い**: `conn.commit()`/`conn.rollback()` という attribute 名前依存。
  ORM の `session.commit()` へ移行、`with conn:` のコンテキストマネージャ化 (暗黙 commit/rollback)、
  関数分割 (commit を呼ぶ関数と FK check を呼ぶ関数が別々になる) のいずれでも、
  本契約は「対象外」= PASS 扱いに落ちてしまう (=検出できない)。
- **FK check 文字列依存**: `"foreign_key_check"` という部分文字列一致。SQL 文字列を変数化・
  f-string化・PRAGMA を関数でラップされると `ast.Constant` として拾えず見逃す。
- **raise 行の対応付けが粗い**: `fk_line` 以降で最初に現れる `raise` を「その FK check に対応する raise」
  とみなしているが、無関係な raise が間に挟まれば誤対応する可能性がある。

---

## F3 (③): idempotency_key 未使用時、_check_conflict 未通過の早期 return 経路

### (a) 契約設計

**契約**: `_check_conflict(...)` 呼出より ★前★ に位置する `return` 文は、
その `return` を包む最も内側の `if` の条件式に `idempotency_key` という識別子が
含まれていなければならない (=idempotency_key が偽の時に到達可能な早期 return は禁止)。

**方式**: AST 上で `return` ノードの祖先を辿り、直近の `ast.If` の条件式 (`test`) を
`ast.dump` した文字列に `idempotency_key` が含まれるかを見る。

### (b) source (未実行・設計のみ)

```python
import ast


def contract_f3_no_conflict_bypass(source: str) -> bool:
    """契約: _check_conflict() 呼出より前にある return は、直近の if 条件式が
    idempotency_key を参照していなければならない。
    True = 契約成立 (PASS、または _check_conflict 自体が不在=対象外としてPASS扱い)。
    False = ③の欠陥を再現 (FAIL)。
    """
    tree = ast.parse(source)

    check_conflict_lines = [
        node.lineno
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "_check_conflict"
    ]
    if not check_conflict_lines:
        return True  # 契約の対象外 (_check_conflict 自体が不在)
    first_check_line = min(check_conflict_lines)

    parents = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            parents[child] = node

    for node in ast.walk(tree):
        if not isinstance(node, ast.Return):
            continue
        if node.lineno >= first_check_line:
            continue
        cur = node
        guarded = False
        while cur in parents:
            cur = parents[cur]
            if isinstance(cur, ast.If):
                if "idempotency_key" in ast.dump(cur.test):
                    guarded = True
                    break
            if isinstance(cur, ast.FunctionDef):
                break
        if not guarded:
            return False  # FAIL: ③の欠陥を再現
    return True
```

### (c) 「欠陥が在れば必ず FAIL か」

★書ける、ただし範囲限定付き★。判定 doc の実測形 (249行目 `if root_enabled and idempotency_key:` の
枝分かれで、270行目 `if existing and not (root_enabled and idempotency_key):` を通って
271-278行目で `_check_conflict`(280行目) より前に `return` する) に対しては、
271-278行目の `return` の直近 `if` (270行目) の条件式に `idempotency_key` という識別子が
★含まれている★ ため、実は ★本契約は素朴な形では PASS してしまう★
(条件式は `idempotency_key` を参照してはいるが、`not (... and idempotency_key)` という
★否定を含む論理式★ ゆえに、idempotency_key が偽の時こそ return へ到達する、という
「idempotency_key に言及している」以上の意味論までは本契約は見ていない)。
∴ ★この具体的な欠陥形に対しては、素朴な「識別子を含むか」判定だけでは FAIL を保証できない★。
契約を「識別子を含む」ではなく「`idempotency_key` を要求する形 (`and idempotency_key` を含み、
かつ `not (...)` で丸ごと否定されていない)」まで狭めれば FAIL させられるが、
それは論理式の意味解析に踏み込むことになり、単純な静的契約の範囲を超える。
★∴ (c) の問いに対する誠実な答=「識別子存在チェックのみでは FAIL 保証できない。
本 doc の (b) source は自己点検の結果、③を捕捉しない設計のまま提出する
(理由=偽の FAIL 保証を書かない事を優先した)」★。

### 脆さ (かつ (c) で露見した設計欠陥そのもの)

- **識別子存在と論理的要求の混同**: 上記の通り、`idempotency_key` という識別子が条件式に
  ★現れている★ことと、その条件式が「idempotency_key を要求している」ことは別。
  `not (X and idempotency_key)` は識別子を含むが、実際には idempotency_key が偽の時に
  真になる式であり、本契約はこの否定を見抜けない。
- **改善の方向性 (未実装・設計のみ言及)**: `ast.BoolOp`/`ast.UnaryOp(Not)` を辿り、
  `idempotency_key` が最外周の `not` の内側に無いことまで確認すれば、本件は捕捉できる可能性がある。
  ただし一般の論理式 (`or` を挟む・別変数への代入を経由する等) では静的解析の限界に近づく。
  ★本工区では設計止まりとし、実装はしていない★ (下命「不能なら〜」の趣旨に照らし、
  ここが③の「静的契約では捕捉しきれない」境界と考える)。
- **`_check_conflict` の呼出名依存**: 関数名変更・メソッド化 (`self._check_conflict`) で
  `ast.Name` から `ast.Attribute` に変わると検出漏れになる (本 source は `ast.Name` のみ対応)。

---

## まとめ (F1/F2/F3 横断)

| # | 契約は書けたか | 欠陥形に対し FAIL 保証あるか | 主な脆さ |
|---|---|---|---|
| F1 | 書けた | ★あり★ (定義上一致) | 別名実装・no-op スタブで偽 PASS |
| F2 | 書けた | ★あり★ (実測の具体形に限る) | 行番号ヒューリスティック、API形変更で偽 PASS |
| F3 | 書けた (が) | ★無い★ (識別子存在≠論理的要求。自己点検で判明) | 否定を含む論理式を見抜けない |

★静的契約 test 全般の共通限界★: いずれも「名前・行順序・識別子の存在」という構文的近似であり、
意味論 (実際にその値が effective に効いているか) までは保証しない。
∴ 下命の「脆さも書け」に対する総括=★静的契約は『欠陥が居なくなった』ことの証明にはならず、
『この特定の構文形の欠陥が再発したら気付ける』程度の網である★。F3 は現状その網の目が
最も粗く、契約を書いた当職自身がそれを FAIL 保証できないと明記する。

## 境界・自己申告

- 本工区中、hakudokai-dev・DB・他 PC への接触は一切なし。apply/worktree/走行も一切なし。
- 上記3件の source は ★未実行★ (下命通り)。ゆえに構文エラーの有無すら当職は実行確認していない
  (肉眼レビューのみ)。適用時は先に単体で構文チェックすることを推奨する (これも当職が今回行うのは越権と判断し実施せず)。
- 足軽4号の「不能の因」別便とは重ならない設計としたが、当職は当該便の内容を読んでいないため
  ★重複していないことの確認は当職単独ではできていない★ (家老second による束ね待ち)。
- 本工区が新たに開ける穴: F2/F3 の source が「契約 PASS = 欠陥なし」と誤読されるリスク
  (実際は「この構文形の欠陥は無い」の意でしかない)。適用時の README/docstring で
  この限定を明記しない場合、将来の読者が過信する穴になり得る。
