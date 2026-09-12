# order338 probe2 -- 7 本が save_treatment を どう呼ぶか の別を ast で切り分ける器
# 席 ashigaru-third-3 / 令338 / 走 0・讀取のみ・値は写さず名と数のみ
import ast, subprocess, sys

REPO = "/mnt/c/DentalBI"
TARGET = "save_treatment"
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

def probe(ref, path):
    src = show(ref, path)
    t = ast.parse(src)
    bare = 0      # save_treatment(...)  素の名で呼ぶ
    attrs = {}    # <recv>.save_treatment(...)  受け手名ごと
    impf = []     # from X import save_treatment
    impm = []     # import X  /  import X as Y  の module 名
    for n in ast.walk(t):
        if isinstance(n, ast.ImportFrom):
            for a in n.names:
                if a.name == TARGET:
                    impf.append(n.module or "")
        if isinstance(n, ast.Import):
            for a in n.names:
                impm.append(a.name)
        if isinstance(n, ast.Call):
            f = n.func
            if isinstance(f, ast.Name) and f.id == TARGET:
                bare += 1
            elif isinstance(f, ast.Attribute) and f.attr == TARGET:
                v = f.value
                r = v.id if isinstance(v, ast.Name) else (v.attr if isinstance(v, ast.Attribute) else "?")
                attrs[r] = attrs.get(r, 0) + 1
    tv = [m for m in impm if "treatment_validation" in m]
    return dict(bare=bare, attrs=attrs, impf=len(impf), impm=len(set(impm)), tv=len(set(tv)))

if __name__ == "__main__":
    ref = sys.argv[1] if len(sys.argv) > 1 else "main"
    for p in FILES:
        r = probe(ref, p)
        aa = ",".join([k + ":" + str(v) for k, v in sorted(r["attrs"].items())]) or "-"
        print(p.split("/")[-1],
              "bare=%d attr=[%s] fromimp=%d import=%d tvmod=%d" % (r["bare"], aa, r["impf"], r["impm"], r["tv"]))
