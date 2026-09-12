import importlib.util

SRC = "/home/hakudoukai/karo3/wt-abbrev-guard-20260912/backend/utils/abbreviation_checker.py"
spec = importlib.util.spec_from_file_location("abbrev_ck_oldget", SRC)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
print("IMPORT=ok")

norm = getattr(mod, "_normalize_rpc_result")
empt = getattr(mod, "_empty_rules")
print("HAS normalize=%s empty=%s" % (norm is not None, empt is not None))

KEYS = ["official", "corrections", "detail_required"]


def old_get(rules):
    out = []
    for k in KEYS:
        try:
            out.append(str(len(rules.get(k, []))))
        except Exception as e:
            out.append("EXC:" + type(e).__name__)
    return out


CASES = [
    ("A null valued keys", {"official": None, "corrections": None, "detail_required": None}),
    ("B keys absent", {}),
    ("C empty lists", {"official": [], "corrections": [], "detail_required": []}),
    ("D non dict (None)", None),
]

for name, data in CASES:
    try:
        r = norm(data)
        exc = "none"
    except Exception as e:
        r = None
        exc = type(e).__name__
    print("---- CASE %s" % name)
    if r is None:
        print("   normalize raised %s" % exc)
        continue
    present = len([k for k in KEYS if k in r])
    types = ",".join([type(r.get(k)).__name__ for k in KEYS])
    nones = len([k for k in KEYS if r.get(k) is None])
    print("   normalize exc=%s / keys present=%d of 3 / types=%s / none valued=%d" % (exc, present, types, nones))
    print("   old get lens=%s" % ",".join(old_get(r)))

probe = {"official": 5, "corrections": [], "detail_required": []}
print("---- CASE E int valued key (counter example, not null)")
print("   raw dict (normalize wo toosazu) lens=%s" % ",".join(old_get(probe)))
print("   via normalize lens=%s" % ",".join(old_get(norm(probe))))
print("DONE")
