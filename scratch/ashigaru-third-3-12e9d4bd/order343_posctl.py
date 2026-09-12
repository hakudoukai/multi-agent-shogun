# order343 : positive control. Same instrument, same four cases as order342,
# pointed at the patched tree that karo built. Read only: no DB, no env read,
# no values printed, no writes. Run count: this script is started exactly once.
import importlib.util, traceback, sys

SRC = "/home/hakudoukai/karo3/wt-abbrev-guard-20260912/backend/utils/abbreviation_checker.py"
print("SRC=" + SRC)

# ---- gate (read only, before any call)
spec = importlib.util.spec_from_file_location("abbrev_ck_rw", SRC)
m = importlib.util.module_from_spec(spec)
try:
    spec.loader.exec_module(m)
    print("IMPORT=ok")
except Exception as e:
    print("IMPORT=fail type=" + type(e).__name__)
    sys.exit(0)
print("HAS set_cache=" + str(hasattr(m, "set_cache")) + " clear_cache=" + str(hasattr(m, "clear_cache")))

TEXT = "P"
FUNCS = ["check_unofficial_abbreviations", "check_disease_abbreviation_detail"]
KEYS = ["official", "corrections", "detail_required"]

def fire(tag, setup):
    print("---- CASE " + tag)
    setup()
    for fn in FUNCS:
        f = getattr(m, fn)
        try:
            r = f(TEXT)
            print("  " + fn + " -> no exception, returned " + type(r).__name__ + " len=" + str(len(r)))
        except Exception as e:
            tb = e.__traceback__
            last = None
            while tb is not None:
                last = tb
                tb = tb.tb_next
            print("  " + fn + " -> EXC type=" + type(e).__name__ + " line=" + str(last.tb_lineno if last else None))
            lines = [x.rstrip() for x in traceback.format_exc().split(chr(10)) if x.strip()]
            for x in lines[-3:]:
                print("    TB| " + x)

fire("A null-valued keys (was the failing case)", lambda: m.set_cache(dict((k, None) for k in KEYS)))
fire("B keys absent", lambda: m.set_cache({}))
fire("C empty lists", lambda: m.set_cache(dict((k, []) for k in KEYS)))
fire("D cache cleared", lambda: m.clear_cache())
print("DONE")
