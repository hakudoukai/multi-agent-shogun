# order340: 板 354dc26f 受入「3鍵に COALESCE」を patch に鋳る器
# 走らせるのは己のみ。DB へは触れぬ。git は讀取動詞のみ。
import subprocess, io, hashlib, re

REPO = "/mnt/c/DentalBI"
REF = "origin/main"
SNAP = "supabase/migrations/20260909170000_snapshot_live_public_functions.sql"
SEAT = "/home/hakudoukai/multi-agent-shogun/scratch/ashigaru-third-3-12e9d4bd"
NEWMIG = "supabase/migrations/20260912150000_get_abbreviation_rules_coalesce.sql"

def show(path):
    return subprocess.check_output(["git", "show", REF + ":" + path], cwd=REPO).decode("utf-8", "replace")

s = show(SNAP)
L = s.split(chr(10))

# ---- ㋐ 函の行域（頭註・CREATE・尻）を字で当てる ----
def find_all(pred):
    return [i + 1 for i in range(len(L)) if pred(L[i])]

heads = find_all(lambda x: "CREATE OR REPLACE FUNCTION" in x)
note = find_all(lambda x: x.startswith("-- =====") and "get_abbreviation_rules" in x)
tail = [n for n in find_all(lambda x: x.strip() == "$function$;") if n > 723]
print("HEADS=%d NOTE=%s CREATE=%s" % (len(heads), note, [n for n in heads if 720 < n < 730]))
print("TAIL_first_after_723=%s" % (tail[0] if tail else None))
print("NOTE_to_CREATE_gap=%d" % (min([n for n in heads if n > note[0]]) - note[0]))

# 三鍵の jsonb_agg 行と、其の包みの有無
for n in (732, 743, 754):
    prev = L[n - 2]
    print("KEY_at_L%d jsonb_agg=%s wrapped_prev=%s" % (n, "jsonb_agg" in L[n - 1], "COALESCE" in prev))

# 正対照の包みの字の形（一つだけ引く）
print("CTRL_L781=%s" % L[780].strip())
print("CTRL_L792=%s" % L[791].strip())

# ---- patch を鋳る（新 migration file を足す unified diff・当てぬ） ----
B = []
b = B.append
b("-- get_abbreviation_rules(date) : 3鍵の jsonb_agg を COALESCE で包む")
b("-- 板 354dc26f 受入 = 3鍵に COALESCE")
b("-- 依存 = 20260909170000_snapshot_live_public_functions.sql の着地後に適用する事")
b("-- 形 = CREATE OR REPLACE（postgres は函の本体を部分置換出来ぬ ゆゑ丸ごと置き直す）")
b("CREATE OR REPLACE FUNCTION public.get_abbreviation_rules(p_diagnosis_date date DEFAULT CURRENT_DATE)")
b(" RETURNS jsonb")
b(" LANGUAGE plpgsql")
b(" STABLE")
b(" SET search_path TO 'public'")
b("AS $function$")
b("BEGIN")
b("  RETURN jsonb_build_object(")
b("    'official', COALESCE((")
b("      SELECT jsonb_agg(jsonb_build_object(")
b("        'abbreviation', abbreviation,")
b("        'official_name', official_name,")
b("        'category', category,")
b("        'requires_detail', requires_detail")
b("      ))")
b("      FROM official_abbreviations")
b("      WHERE is_active = true")
b("        AND in_revision_scope(valid_from, valid_to, p_diagnosis_date)")
b("    ), '[]'::jsonb),")
b("    'corrections', COALESCE((")
b("      SELECT jsonb_agg(jsonb_build_object(")
b("        'unofficial', unofficial,")
b("        'official_abbreviation', official_abbreviation,")
b("        'official_name', official_name,")
b("        'correction_type', correction_type")
b("      ))")
b("      FROM abbreviation_corrections")
b("      WHERE is_active = true")
b("        AND in_revision_scope(valid_from, valid_to, p_diagnosis_date)")
b("    ), '[]'::jsonb),")
b("    'detail_required', COALESCE((")
b("      SELECT jsonb_agg(abbreviation)")
b("      FROM official_abbreviations")
b("      WHERE requires_detail = true AND is_active = true")
b("        AND in_revision_scope(valid_from, valid_to, p_diagnosis_date)")
b("    ), '[]'::jsonb)")
b("  );")
b("END;")
b("$function$;")

P = []
p = P.append
p("diff --git a/" + NEWMIG + " b/" + NEWMIG)
p("new file mode 100644")
p("--- /dev/null")
p("+++ b/" + NEWMIG)
p("@@ -0,0 +1," + str(len(B)) + " @@")
for x in B:
    p("+" + x)

patch = chr(10).join(P) + chr(10)
out = SEAT + "/order340_coalesce_3keys.patch"
io.open(out, "w", encoding="utf-8", newline=chr(10)).write(patch)

h = hashlib.sha256(patch.encode("utf-8")).hexdigest()[:16]
print("PATCH=%s sql_lines=%d patch_lines=%d bytes=%d sha256_16=%s" % (out, len(B), len(P), len(patch.encode("utf-8")), h))
print("COALESCE_in_patch=%d jsonb_agg_in_patch=%d" % (patch.count("COALESCE"), patch.count("jsonb_agg")))
