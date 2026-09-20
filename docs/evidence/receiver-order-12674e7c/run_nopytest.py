# pytest 無き所にて 固定HEAD の10件を走らす ―― 標準庫のみ
# 依存する pytest 機構は組込 fixture `tmp_path` ただ一つ（実測）。之を自前で与ふ。
import importlib.util, pathlib, sys, tempfile, traceback
FILES = ["tests/test_secondpc_downlink_owned_order.py",
         "tests/test_secondpc_deadletter_envelope.py",
         "tests/test_secondpc_samepc_role_routing.py"]
ok = fail = 0
for rel in FILES:
    p = pathlib.Path(rel).resolve()
    spec = importlib.util.spec_from_file_location(p.stem, p)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    for name in sorted(n for n in dir(mod) if n.startswith("test_")):
        fn = getattr(mod, name)
        if not callable(fn): continue
        with tempfile.TemporaryDirectory() as td:
            try:
                fn(tmp_path=pathlib.Path(td)); ok += 1; print("PASS", rel, name)
            except BaseException:
                fail += 1; print("FAIL", rel, name); traceback.print_exc()
print(f"=== ok={ok} fail={fail} ===")
sys.exit(1 if fail else 0)
