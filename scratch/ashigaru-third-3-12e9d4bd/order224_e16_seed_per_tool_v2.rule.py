# -*- coding: utf-8 -*-
"""order224 / E16 芯 ―― ★器ごとに『其の器の網』×『其の器の母』で数へる★。

★何故 之が要るか★:
  o224 の追ひ(v1/v2/v3)は ★己が拵へた一つの網★ を ★己が選んだ一つの母★ に当てた。
  然るに ㊁㊂ の器は ★各々 別の網と 別の母★ を持つ。
  ∴ 「2 件以上が現に立つか」は ★器ごとに★ しか答へられぬ。
  一つの網の数を 五つの器へ配れば、それは ★別の物を数へた数★ である（條 二百三十八）。

★網も母も 器の逐語から写した★（写した事を此処に書く ―― 床⑸）。

★v1 から v2 で直した二つ（★網は一字も変へて居らぬ★・條 百七十四）★:
  ㋐ 締めの数 ―― v1 は probe() の戻り(★枚数★)を足して「13 / 5」と刷つた。
     ★器の数と 枚数を足した★ = 単位の混同（家老 新條「差が出たら『何の単位が違ふか』を先に問へ」）。
     v2 は ★立つた器の数★ を 1 ずつ数へる。
  ㋑ 母が ★空★ の時 v1 は「現に立たぬ」と刷つた。
     ★空の母から『立たぬ』は言へぬ★ ―― 正しくは ★測定不能★ である（三択語の誤用）。

★何処で走らせるか★（作法 五条目の補ひ）:
  cwd = /home/hakudoukai/multi-agent-shogun / host = momizi-dx / user = hakudoukai
  argv = python3 scratch/ashigaru-third-3-12e9d4bd/order224_e16_seed_per_tool_v1.rule.py
"""
import io, os, re, glob

BS = chr(92)  # ★逆斜線を 直に書かず 符で置く（heredoc の食ひ違ひを避ける為）★
D = "scratch/ashigaru-third-3-12e9d4bd/"
OUT = D + "order224_e16_seed_per_tool_v2.raw.txt"
L = []
def say(x):
    L.append(x)

def mine(f):
    return os.path.basename(f).startswith("order224_")

say("=== order224 / E16 芯 ―― 器ごとに『其の器の網』×『其の器の母』で数へる ===")
say("※★己の一族(order224_*)は 母から除く★（條 二百六十四・v3 で紙にも掛かると判つた故）")
say("")

def probe(tag, where, pat, mother, note):
    """mother = [(名, 中身)] の列。"""
    rx = re.compile(pat)
    z0 = z1 = z2 = 0
    multi = []
    for nm, t in mother:
        n = len(rx.findall(t))
        if n == 0:
            z0 += 1
        elif n == 1:
            z1 += 1
        else:
            z2 += 1
            multi.append((nm, n))
    say("--- %s ―― %s ---" % (tag, where))
    say("  網(逐語) = %s" % pat)
    say("  母 = %s ＝ %d 件" % (note, len(mother)))
    say("  当たり 0 = %d / 1 = %d / ★2 件以上 = %d★" % (z0, z1, z2))
    for nm, n in multi:
        say("    ★2 件以上★ %s = %d 件" % (nm, n))
    if not mother:
        say("  ⇒ ★測定不能★（★母が空★ ―― 空の母から『立たぬ』は言へぬ）")
        say("")
        return None
    say("  ⇒ ★%s★" % (u"現に立つ" if z2 else u"現に立たぬ（今の母では）"))
    say("")
    return z2 > 0

def md_texts(fs):
    out = []
    for f in fs:
        if mine(f):
            continue
        out.append((os.path.basename(f), io.open(f, encoding="utf-8").read()))
    return out

stands = []   # ★器ごとに True/False/None を積む（★枚数を足さぬ★）★
def stands_add(*a):
    stands.append(probe(*a))

# ㊁-1 unmeasurable26_status_triage_v1.rule.py:12
allmd = sorted(glob.glob(D + "*.md"))
stands_add(
    u"㊁-1 unmeasurable26_status_triage_v1.rule.py:12",
    u"m=re.search(r'as_of[:：]?" + BS + u"s*(20" + BS + u"S+)',open(D+f).read())",
    r"as_of[:：]?\s*(20\S+)",
    md_texts(allmd),
    u"MD=sorted(f for f in os.listdir(D) if f.endswith('.md')) ＝ .md 悉く")

# ㊁-2 order196_magazine_v1.rule.py:24
PAT196 = re.compile(u"^order(1[89][0-9])_.*" + BS + BS + u".md$")
m196 = [f for f in allmd if PAT196.match(os.path.basename(f))]
stands_add(
    u"㊁-2 order196_magazine_v1.rule.py:24",
    u'm = re.search(u"as_of[:：]?' + BS + BS + u's*`?([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9:+]+)", t)',
    u"as_of[:：]?" + BS + u"s*`?([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9:+]+)",
    md_texts(m196),
    u"names = order18x/19x の .md（PAT で名で判ず）")

# ㊁-3 order197_head_reproof_v1.rule.py:42
PAPERS = [u"order187_second_pair_and_source_v1", u"order188_split_sixteen_v1",
          u"order189_falsepos_cure_v1", u"order190_seventeen_sources_v1",
          u"order191_lot_self_close_v1", u"order192_test_escape_census_v1",
          u"order193_escape_surface_fix_v1", u"order195_typed_reproof_v1"]
m197 = []
for f in PAPERS:
    ap = D + f + u".md"
    if os.path.exists(ap):
        m197.append((f + u".md", io.open(ap, encoding="utf-8").read()))
    else:
        say("  ※ %s.md は ★現に無い★（母から落ちる）" % f)
stands_add(
    u"㊁-3 order197_head_reproof_v1.rule.py:42",
    u'm = re.search(u"as_of[^0-9]*([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9:]+)", s)',
    u"as_of[^0-9]*([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9:]+)",
    m197,
    u"PAPERS ＝ 名指しの 8 枚")

# ㊂-1 order184_rule_number_ledger_v1.rule.py:28
box = "queue/inbox/ashigaru-third-3.yaml"
t = io.open(box, encoding="utf-8").read()
blocks = []
cur = None
for ln in t.split(chr(10)):
    if ln.startswith("- id: "):
        if cur is not None:
            blocks.append(chr(10).join(cur))
        cur = [ln]
    elif cur is not None:
        cur.append(ln)
if cur is not None:
    blocks.append(chr(10).join(cur))
stands_add(
    u"㊂-1 order184_rule_number_ledger_v1.rule.py:28",
    u'frm = re.search(r"from: (' + BS + BS + u'S+)", b)',
    r"from: (\S+)",
    [(u"block#%d" % i, b) for i, b in enumerate(blocks)],
    u"己の箱の便 block")

# ㊂-2 order200_escape_shape_ast_v1.rule.py:251
f192 = D + u"order192_test_escape_census_v1.rule.py"
m200 = [(u"order192_test_escape_census_v1.rule.py", io.open(f192, encoding="utf-8").read())] \
       if os.path.exists(f192) else []
stands_add(
    u"㊂-2 order200_escape_shape_ast_v1.rule.py:251",
    u'm = re.search(r"ROOT' + BS + BS + u's*=' + BS + BS + u's*u?[' + BS + u'"' + chr(39) + u']([^' + BS + u'"' + chr(39) + u']+)", t)',
    "ROOT\\s*=\\s*u?[\"']([^\"']+)",
    m200,
    u"fp = order192_test_escape_census_v1.rule.py ★一枚のみ★")

say("=== 締め ===")
say("★器 %d 本を当てた★：現に立つ = %d 本 / 現に立たぬ = %d 本 / ★測定不能(母が空) = %d 本★"
    % (len(stands), sum(1 for x in stands if x is True),
       sum(1 for x in stands if x is False), sum(1 for x in stands if x is None)))
say("※★之は『器の本数』であつて『枚数』ではない★ ―― v1 は此の二つを足して誤つた。")
say("※★之は『疵が n 件』の意に非ず★ ―― 立つとは『最初の当たりで決めると 別の当たりを取り落し得る母が 現に在る』の意である。")
say("")
say("--- 負の対照 ---")
say("★現に無い網★ を 同じ形で当てる（0 が出る口が在るかを見る）")
stands_neg = probe(u"負-1 現に無い網",
      u"（作り物）",
      r"zzzz_no_such_pattern_o224_[0-9]{9}",
      md_texts(allmd),
      u".md 悉く（己の一族を除く）")
say("★己の一族を除いた母である事の証★ = 除いた枚数 %d 枚"
    % len([f for f in allmd if mine(f)]))

io.open(OUT, "w", encoding="utf-8").write(chr(10).join(L) + chr(10))
print("wrote %s lines=%d" % (OUT, len(L)))
