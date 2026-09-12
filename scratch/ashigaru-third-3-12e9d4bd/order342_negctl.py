# order342 : negative control. Load the product module read-only and show that
# today's code actually falls when the three keys carry null. No DB, no env read,
# no values printed. Run count: this script is started exactly once.
import importlib.util, traceback, sys

SRC = "/mnt/c/DentalBI/backend/utils/abbreviation_checker.py"
print("SRC=" + SRC)

# ---- gate (read only, before any call)
spec = importlib.util.spec_from_file_location("abbrev_ck_ro", SRC)
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

fire("A null-valued keys (positive control)", lambda: m.set_cache(dict((k, None) for k in KEYS)))
fire("B keys absent (negative control)", lambda: m.set_cache({}))
fire("C empty lists (negative control)", lambda: m.set_cache(dict((k, []) for k in KEYS)))
fire("D cache cleared (negative control)", lambda: m.clear_cache())
print("DONE")
