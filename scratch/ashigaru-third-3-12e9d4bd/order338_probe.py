# order338 probe -- backend/tests の 7 本が save_treatment を どう呼ぶか を ast で測る器
# 席 ashigaru-third-3 / 令338 / 走 0（pytest を起こさぬ）・讀取のみ
import ast, subprocess, sys

REPO = "/mnt/c/DentalBI"
REF = "main"
TARGET = "save_treatment"
NEWFN = "_resolve_comment_documentation_field_id"
FILES = [
    "backend/tests/test_r4_d02_non_drug_atomic_save.py",
    "backend/tests/test_r4_d03_periodontal_atomic_save.py",
    "backend/tests/test_r4_patient03_d04_d16_recipes.py",
    "backend/tests/test_receipt_disease_set_eligibility.py",
    "backend/tests/test_spt_eligibility_redo_regressions.py",
    "backend/tests/test_touyaku_product_save.py",
    "backend/tests/test_treatment_validation_save_landing.py",
]

def show(ref, path):
    return subprocess.check_output(
        ["git", "show", ref + ":" + path], cwd=REPO
    ).decode("utf-8", "replace")

def probe(ref, path):
    src = show(ref, path)
    tree = ast.parse(src)
    imported = 0
    direct = 0
    client = 0
    strhit = 0
    ntest = 0
    patched = 0
    for n in ast.walk(tree):
        if isinstance(n, ast.ImportFrom):
            for a in n.names:
                if a.name == TARGET:
                    imported += 1
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if n.name.startswith("test_"):
                ntest += 1
        if isinstance(n, ast.Call):
            f = n.func
            nm = f.id if isinstance(f, ast.Name) else (f.attr if isinstance(f, ast.Attribute) else "")
            if nm == TARGET:
                direct += 1
            if nm in ("TestClient", "post", "AsyncClient"):
                client += 1
            if nm in ("setattr", "monkeypatch", "patch"):
                patched += 1
        if isinstance(n, ast.Constant) and isinstance(n.value, str):
            if TARGET in n.value:
                strhit += 1
    cond = src.count("condition_rule")
    newn = src.count(NEWFN)
    return dict(imported=imported, direct=direct, client=client,
                strhit=strhit, ntest=ntest, patched=patched,
                cond=cond, newfn=newn, lines=src.count(chr(10)))

if __name__ == "__main__":
    ref = sys.argv[1] if len(sys.argv) > 1 else REF
    for p in FILES:
        r = probe(ref, p)
        print(p.split("/")[-1],
              "import=%d direct=%d client=%d str=%d ntest=%d patch=%d cond=%d newfn=%d lines=%d"
              % (r["imported"], r["direct"], r["client"], r["strhit"],
                 r["ntest"], r["patched"], r["cond"], r["newfn"], r["lines"]))
