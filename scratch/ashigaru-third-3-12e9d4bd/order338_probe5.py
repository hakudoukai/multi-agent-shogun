# order338 probe5 -- harness が新函名をどう呼ぶか / 8本の識別子境界での当たり直し
# 席 ashigaru-third-3 / 令338 / 走 0・讀取のみ・名と数のみ
import ast, re, subprocess

REPO = "/mnt/c/DentalBI"
BR = "karo-third/fa06a3a1-caller-20260912"
NEWFN = "_resolve_comment_documentation_field_id"
SAVE = "save_treatment"
HARN = "backend/tests/test_c1_dml_migration_pkg_isolated_harness.py"
FILES = [
    "backend/tests/test_r4_d02_non_drug_atomic_save.py",
    "backend/tests/test_r4_d03_periodontal_atomic_save.py",
    "backend/tests/test_r4_patient03_d04_d16_recipes.py",
    "backend/tests/test_receipt_disease_set_eligibility.py",
    "backend/tests/test_spt_eligibility_redo_regressions.py",
    "backend/tests/test_touyaku_product_save.py",
    "backend/tests/test_treatment_validation_save_landing.py",
    HARN,
]
PROBE = ["cr", "dict", "condition_rule", "doc_field_id", "set_code", "visit_identity"]

def show(ref, path):
    return subprocess.check_output(["git", "show", ref + ":" + path], cwd=REPO).decode("utf-8", "replace")

def idcount(s, nm):
    # 識別子境界(床18: 明示クラス)で行数を数へる
    pat = re.compile("(^|[^A-Za-z0-9_])" + nm + "($|[^A-Za-z0-9_])")
    return sum(1 for ln in s.split(chr(10)) if pat.search(ln))

# harness の呼び方
s = show(BR, HARN)
t = ast.parse(s)
bare = attr = imp = 0
savecall = 0
ntest = 0
for n in ast.walk(t):
    if isinstance(n, (ast.Import, ast.ImportFrom)):
        for a in n.names:
            if a.name == NEWFN or a.asname == NEWFN:
                imp += 1
    if isinstance(n, ast.Call):
        f = n.func
        if isinstance(f, ast.Name):
            if f.id == NEWFN: bare += 1
            if f.id == SAVE: savecall += 1
        elif isinstance(f, ast.Attribute):
            if f.attr == NEWFN: attr += 1
            if f.attr == SAVE: savecall += 1
    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name.startswith("test_"):
        ntest += 1
print("HARNESS newfn bare呼=%d attr呼=%d import=%d / save_treatment呼=%d / test関数=%d / 行=%d"
      % (bare, attr, imp, savecall, ntest, s.count(chr(10))))

print("== 8本 識別子境界の当たり行数 ==")
for p in FILES:
    s = show(BR, p)
    cells = [nm + ":" + str(idcount(s, nm)) for nm in PROBE]
    print(p.split("/")[-1], " ".join(cells))
