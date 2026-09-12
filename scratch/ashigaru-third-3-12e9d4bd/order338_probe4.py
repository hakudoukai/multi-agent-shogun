# order338 probe4 -- 当てた10行が入る門(if)の条件に立つ名を ast で取り、7本の試験に其の名が在るか数へる器
# 席 ashigaru-third-3 / 令338 / 走 0・讀取のみ・名と数のみ(値は写さぬ)
import ast, subprocess, sys

REPO = "/mnt/c/DentalBI"
BR = "karo-third/fa06a3a1-caller-20260912"
SRCF = "backend/api/treatment_validation.py"
LO, HI = 13663, 13672   # 令337 で取つた追加域(当て後)
NEWFN = "_resolve_comment_documentation_field_id"
FILES = [
    "backend/tests/test_r4_d02_non_drug_atomic_save.py",
    "backend/tests/test_r4_d03_periodontal_atomic_save.py",
    "backend/tests/test_r4_patient03_d04_d16_recipes.py",
    "backend/tests/test_receipt_disease_set_eligibility.py",
    "backend/tests/test_spt_eligibility_redo_regressions.py",
    "backend/tests/test_touyaku_product_save.py",
    "backend/tests/test_treatment_validation_save_landing.py",
    "backend/tests/test_c1_dml_migration_pkg_isolated_harness.py",
]

def show(ref, path):
    return subprocess.check_output(["git", "show", ref + ":" + path], cwd=REPO).decode("utf-8", "replace")

src = show(BR, SRCF)
tree = ast.parse(src)

# 追加域を覆ふ最小の If を探し、其の門の条件に立つ名を集める
gates = []
for n in ast.walk(tree):
    if isinstance(n, ast.If):
        a = getattr(n, "lineno", 0)
        b = getattr(n, "end_lineno", 0)
        if a <= LO and b >= HI:
            names = set()
            for x in ast.walk(n.test):
                if isinstance(x, ast.Name):
                    names.add(x.id)
                elif isinstance(x, ast.Attribute):
                    names.add(x.attr)
            gates.append((a, b, b - a, sorted(names)))
gates.sort(key=lambda g: g[2])
print("GATES覆ふIfの数=%d" % len(gates))
for g in gates[:4]:
    print("  if L%d-L%d 幅%d 条件の名=%s" % (g[0], g[1], g[2], ",".join(g[3])))

inner = set()
for g in gates[:3]:
    inner.update(g[3])
print("内側3門の名の和=%s" % ",".join(sorted(inner)))

# 追加域そのもので立つ名
adds = set()
for n in ast.walk(tree):
    ln = getattr(n, "lineno", None)
    if ln is not None and LO <= ln <= HI:
        if isinstance(n, ast.Name):
            adds.add(n.id)
        elif isinstance(n, ast.Attribute):
            adds.add(n.attr)
print("追加域で立つ名=%s" % ",".join(sorted(adds)))

probe = sorted(inner | adds)
print("== 7本+harness に其の名が当たるか(行数) ==")
for p in FILES:
    try:
        s = show(BR, p)
    except Exception:
        print(p.split("/")[-1], "MISSING"); continue
    hits = []
    for nm in probe:
        c = s.count(nm)
        if c:
            hits.append(nm + ":" + str(c))
    nf = s.count(NEWFN)
    print(p.split("/")[-1], "newfn=%d hit=[%s]" % (nf, ",".join(hits) or "-"))
