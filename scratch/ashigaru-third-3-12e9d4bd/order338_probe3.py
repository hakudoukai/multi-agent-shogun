# order338 probe3 -- 受け手名 tv が何処で束縛されるかを ast で測る器
# 席 ashigaru-third-3 / 令338 / 走 0・讀取のみ・名と数のみ
import ast, subprocess, sys

REPO = "/mnt/c/DentalBI"
RECV = "tv"
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
    return subprocess.check_output(["git", "show", ref + ":" + path], cwd=REPO).decode("utf-8", "replace")

def kinds(node):
    # 右辺の形を一語で名指す
    if isinstance(node, ast.Call):
        f = node.func
        nm = f.id if isinstance(f, ast.Name) else (f.attr if isinstance(f, ast.Attribute) else "?")
        return "call:" + nm
    if isinstance(node, ast.Name):
        return "name:" + node.id
    if isinstance(node, ast.Attribute):
        return "attr:" + node.attr
    return type(node).__name__

def probe(ref, path):
    src = show(ref, path)
    t = ast.parse(src)
    binds = []     # tv = <...>  の右辺の形
    asimp = []     # import X as tv / from X import Y as tv
    args = 0       # def f(tv): fixture 引数
    fixt = 0       # @pytest.fixture が付く def の数
    for n in ast.walk(t):
        if isinstance(n, ast.Assign):
            for tgt in n.targets:
                if isinstance(tgt, ast.Name) and tgt.id == RECV:
                    binds.append(kinds(n.value))
        if isinstance(n, (ast.Import, ast.ImportFrom)):
            for a in n.names:
                if a.asname == RECV:
                    asimp.append(a.name)
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for a in n.args.args:
                if a.arg == RECV:
                    args += 1
            for d in n.decorator_list:
                nm = ""
                if isinstance(d, ast.Attribute):
                    nm = d.attr
                elif isinstance(d, ast.Name):
                    nm = d.id
                elif isinstance(d, ast.Call):
                    f = d.func
                    nm = f.attr if isinstance(f, ast.Attribute) else (f.id if isinstance(f, ast.Name) else "")
                if nm == "fixture":
                    fixt += 1
    return dict(binds=binds, asimp=asimp, args=args, fixt=fixt)

if __name__ == "__main__":
    ref = sys.argv[1] if len(sys.argv) > 1 else "main"
    for p in FILES:
        r = probe(ref, p)
        print(p.split("/")[-1],
              "bind=%s asimp=%s arg=%d fixture=%d" % (",".join(r["binds"]) or "-", ",".join(r["asimp"]) or "-", r["args"], r["fixt"]))
