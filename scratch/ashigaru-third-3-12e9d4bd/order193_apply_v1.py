# -*- coding: utf-8 -*-
u"""order193 直し器 v1 ―― 行番号で当てて飾りを一行づつ置換する(置換のみ・挿入を混ぜぬ=床(28))。

当てる前に実物の行を照合し、違へば ANCHOR_MISS で止める。触るは試験 file のみ。
製品 code に一字も書かぬ。同一 file 内は下から上へ当てる(行番号が動かぬ為)。
"""
import io, os

ROOT = u"/home/hakudoukai/a3/wt-bundle-fix4"

JOBS = [('tests/test_step_r_ui.py', 282, '@pytest.mark.skip(reason="EmptyState.tsx', '@pytest.mark.skipif(\n    not (FRONTEND_ROOT / "components" / "shared" / "EmptyState.tsx").exists(),\n    reason="EmptyState.tsxは共有UI刷新で撤去・2026-07-15棚卸し / order193: 条件を器に測らせる形へ移した(的が戻れば試験も自ら起きる)",\n)'), ('tests/test_step_a4_handover_sheet.py', 377, '@pytest.mark.skip(reason="useSheetPagination.ts', '@pytest.mark.skipif(\n    not (FRONTEND_DIR / "hooks" / "useSheetPagination.ts").exists(),\n    reason="useSheetPagination.tsは申し送りA4設計刷新で撤去・2026-07-15棚卸し / order193: 条件を器に測らせる形へ移した(的が戻れば試験も自ら起きる)",\n)'), ('tests/test_step_q.py', 461, '@pytest.mark.skip(reason="useBillingRules.ts', '@pytest.mark.skipif(\n    not (Path(__file__).resolve().parent.parent / "frontend" / "src" / "hooks" / "useBillingRules.ts").exists(),\n    reason="useBillingRules.tsは検証エンジン(treatment_validation)へ統合され撤去・2026-07-15棚卸し / order193: 条件を器に測らせる形へ移した(的が戻れば試験も自ら起きる)",\n)'), ('tests/test_step_s3.py', 664, '@pytest.mark.skip(reason="後続設計で廃止', '@pytest.mark.skipif(\n    not (ROOT / "frontend" / "src" / "features" / "kanban" / "CheckoutModal.tsx").exists(),\n    reason="後続設計で廃止(CheckoutModal/ComplaintForm/ProductivitySectionはkanban/dashboard刷新で撤去・2026-07-15棚卸し) / order193: 条件を器に測らせる形へ移した(的が戻れば試験も自ら起きる)",\n)'), ('tests/test_step_s3.py', 678, '@pytest.mark.skip(reason="後続設計で廃止', '@pytest.mark.skipif(\n    not (ROOT / "frontend" / "src" / "features" / "kanban" / "ComplaintForm.tsx").exists(),\n    reason="後続設計で廃止(CheckoutModal/ComplaintForm/ProductivitySectionはkanban/dashboard刷新で撤去・2026-07-15棚卸し) / order193: 条件を器に測らせる形へ移した(的が戻れば試験も自ら起きる)",\n)'), ('tests/test_step_s3.py', 692, '@pytest.mark.skip(reason="後続設計で廃止', '@pytest.mark.skipif(\n    not (ROOT / "frontend" / "src" / "features" / "kanban" / "ComplaintForm.tsx").exists(),\n    reason="後続設計で廃止(CheckoutModal/ComplaintForm/ProductivitySectionはkanban/dashboard刷新で撤去・2026-07-15棚卸し) / order193: 条件を器に測らせる形へ移した(的が戻れば試験も自ら起きる)",\n)'), ('tests/test_step_s3.py', 703, '@pytest.mark.skip(reason="後続設計で廃止', '@pytest.mark.skipif(\n    not (ROOT / "frontend" / "src" / "features" / "dashboard" / "ProductivitySection.tsx").exists(),\n    reason="後続設計で廃止(CheckoutModal/ComplaintForm/ProductivitySectionはkanban/dashboard刷新で撤去・2026-07-15棚卸し) / order193: 条件を器に測らせる形へ移した(的が戻れば試験も自ら起きる)",\n)'), ('tests/test_step_s3.py', 715, '@pytest.mark.skip(reason="後続設計で廃止', '@pytest.mark.skipif(\n    not (ROOT / "frontend" / "src" / "features" / "dashboard" / "ProductivitySection.tsx").exists(),\n    reason="後続設計で廃止(CheckoutModal/ComplaintForm/ProductivitySectionはkanban/dashboard刷新で撤去・2026-07-15棚卸し) / order193: 条件を器に測らせる形へ移した(的が戻れば試験も自ら起きる)",\n)'), ('tests/test_step_s3.py', 726, '@pytest.mark.skip(reason="後続設計で廃止', '@pytest.mark.skipif(\n    not (ROOT / "frontend" / "src" / "features" / "dashboard" / "ProductivitySection.tsx").exists(),\n    reason="後続設計で廃止(CheckoutModal/ComplaintForm/ProductivitySectionはkanban/dashboard刷新で撤去・2026-07-15棚卸し) / order193: 条件を器に測らせる形へ移した(的が戻れば試験も自ら起きる)",\n)'), ('tests/test_step_s4.py', 753, '@pytest.mark.skip(reason="担当Dr/DH', '@pytest.mark.skipif(\n    not _has_text(ROOT / "frontend" / "src" / "features" / "handover-sheet" / "SheetHeader.tsx", "assignedDr"),\n    reason="担当Dr/DH上部固定inputは06df2bd1 R2で廃止(右ペインblockへ移行)・2026-07-15棚卸し / order193: 条件を器に測らせる形へ移した(的が戻れば試験も自ら起きる)",\n)'), ('tests/test_step_s4.py', 769, '@pytest.mark.skip(reason="SheetPrintView', '@pytest.mark.skipif(\n    not (ROOT / "frontend" / "src" / "features" / "handover-sheet" / "SheetPrintView.tsx").exists(),\n    reason="SheetPrintViewは後続の印刷設計刷新で撤去・2026-07-15棚卸し / order193: 条件を器に測らせる形へ移した(的が戻れば試験も自ら起きる)",\n)')]


def apply_line(rel, lineno, old_prefix, new_block):
    p = os.path.join(ROOT, rel)
    t = io.open(p, encoding="utf-8").read()
    lines = t.split(u"\n")
    cur = lines[lineno - 1]
    assert cur.strip().startswith(old_prefix), u"ANCHOR_MISS %s:%d" % (rel, lineno)
    indent = cur[:len(cur) - len(cur.lstrip())]
    nb = u"\n".join([(indent + x) if x.strip() else x for x in new_block.split(u"\n")])
    lines[lineno - 1] = nb
    io.open(p, "w", encoding="utf-8").write(u"\n".join(lines))
    return 1


if __name__ == "__main__":
    done = 0
    for rel, ln, op, nb in sorted(JOBS, key=lambda j: (j[0], -j[1])):
        done += apply_line(rel, ln, op, nb)
    print(u"applied=%d/%d" % (done, len(JOBS)))
