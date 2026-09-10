# -*- coding: utf-8 -*-
# A3 order269 : grill haisou route no yomi (read-only sokutei-chi wo ki ni motaseru)
# hashiraseru basho : /home/hakudoukai/multi-agent-shogun no cwd de python3
import sys, glob, re

def p(s):
    sys.stdout.write(s + chr(10))

ARU = u"ARU"; NAI = u"NASHI"; FUN = u"FUNO"
VALS = (ARU, NAI, FUN)

PROBES = [u"tmux_pane", u"sb_wrapper", u"inbox_jittai", u"route_daichou",
          u"registry_json", u"settings_cli_agents", u"mainpc_pane"]
assert len(PROBES) == 7, "PROBE7"

# yuka(30) : hitotsu = "yakushoku-mei sono mama no moji-retsu de atatta toki no jitsuzai" wo hitotsu to kazoeta
# (name, probes7, shibako?, haisen(J5), chuu)
ROWS = [
 (u"training-main",       [NAI, NAI, NAI, ARU, NAI, NAI, FUN], False, ARU,
  u"route wa aru ga to_role de naku from-gun no ichiin ; ate saki wa hermes2"),
 (u"kenshu-b",            [NAI, NAI, NAI, NAI, NAI, NAI, FUN], False, NAI,
  u"kono tsuzuri wa config scripts lib ni 0 ken ; daichou wa kenshu-underscore-bucho"),
 (u"kenshu_bucho",        [NAI, NAI, NAI, ARU, NAI, ARU, FUN], False, NAI,
  u"route 2 hon tomo mihaisen (poll process 0 ken to daichou ga iu)"),
 (u"handoverdocs",        [NAI, NAI, NAI, ARU, ARU, NAI, FUN], False, ARU,
  u"registry no role_id to shite aru ga hako no na wa hermes- tsuki"),
 (u"hermes-handoverdocs", [ARU, NAI, ARU, NAI, NAI, NAI, FUN], False, FUN,
  u"POSCTRL : pane mo hako mo gen ni aru"),
 (u"gunshi-third",        [NAI, NAI, ARU, FUN, NAI, FUN, FUN], True,  FUN,
  u"NEGCTRL2 : hako wa gen ni aru ga shibako ichiran ni aru"),
 (u"zzz-nonexistent",     [NAI, NAI, NAI, NAI, NAI, NAI, FUN], False, NAI,
  u"NEGCTRL1 : ari-enu na"),
]
for nm, pr, dd, hs, ch in ROWS:
    assert len(pr) == 7, "ROW7 " + nm
    for v in pr:
        assert v in VALS, "VAL " + nm
    assert hs in VALS, "HAISEN " + nm

JOKEN = [
 u"J1 inbox no jittai (file mata wa link) ga aru",
 u"J2 settings.yaml no cli.agents ni sono na ga aru",
 u"J3 shibako ichiran (IW-DEAD-DEFAULT) ni fukumarenu",
 u"J4 nudge no atesaki to naru tmux pane ga aru",
 u"J5 route daichou ni haisen-zumi no route ga aru",
 u"J6 registry.json ni role_id ga aru",
 u"J7 main PC gawa no pane ga jitsuzai suru",
]
assert len(JOKEN) == 7, "JOKEN7"

p(u"== 1 sou-hyou : yakushoku-mei sono mama de atatta san-taku ==")
p(u"  " + u"name".ljust(22) + u" ".join([x[:9].rjust(9) for x in PROBES]))
for nm, pr, dd, hs, ch in ROWS:
    p(u"  " + nm.ljust(22) + u" ".join([v.rjust(9) for v in pr]))

p(u"== 2 san-taku no dosuu (7 gyou x 7 hashira = 49 masu) ==")
cnt = {ARU: 0, NAI: 0, FUN: 0}
for nm, pr, dd, hs, ch in ROWS:
    for v in pr:
        cnt[v] += 1
p(u"  ARU=" + str(cnt[ARU]) + u"  NASHI=" + str(cnt[NAI]) + u"  FUNO=" + str(cnt[FUN]) + u"  gou=" + str(sum(cnt.values())))
assert sum(cnt.values()) == 49, "MASU49"
assert cnt[FUN] >= 7, "MAINPC-FUNO"

p(u"== 3 soutatsu-kanou jouken (7 jou) ==")
for j in JOKEN:
    p(u"  " + j)

p(u"== 4 jouken no atehame (mitasu jou no kazu / kakikomi-ka / yomare-uru) ==")
res = {}
for nm, pr, dd, hs, ch in ROWS:
    d = dict(zip(PROBES, pr))
    J1 = (d[u"inbox_jittai"] == ARU)
    J2 = (d[u"settings_cli_agents"] == ARU)
    J3 = (not dd)
    J4 = (d[u"tmux_pane"] == ARU)
    J5 = (hs == ARU)
    J6 = (d[u"registry_json"] == ARU)
    J7 = False  # sokutei funou yue "mitashita" to wa kazoenu
    mit = [J1, J2, J3, J4, J5, J6, J7]
    kaki = (J1 or J2) and J3
    yom = kaki and J4
    res[nm] = (sum([1 for x in mit if x]), kaki, yom)
    p(u"  " + nm.ljust(22) + u" mitasu=" + str(res[nm][0]) + u"/7"
      + u" kakikomi-ka=" + (u"tootta" if kaki else u"TOORANU")
      + u" yomare-uru=" + (u"tootta" if yom else u"TOORANU")
      + u" | " + ch)

p(u"== 5 taishou ==")
assert res[u"hermes-handoverdocs"][1] is True, "POSCTRL-KAKI"
assert res[u"hermes-handoverdocs"][2] is True, "POSCTRL-YOMI"
assert res[u"zzz-nonexistent"][1] is False, "NEG1"
assert res[u"gunshi-third"][1] is False, "NEG2"
p(u"  POSCTRL hermes-handoverdocs : kakikomi-ka mo yomare-uru mo tootta (2/2)")
p(u"  NEGCTRL1 zzz-nonexistent : kakikomi-ka TOORANU (nozomi doori)")
p(u"  NEGCTRL2 gunshi-third : hako wa ARU nagara J3 ga kamu yue kakikomi-ka TOORANU")
p(u"  yue J3 (shibako mon) wa gen ni kiite oru ; J1 dake de wa kimaranu")

p(u"== 6 sanmato no kotae (order269 ka-ro ga tou 3 mei) ==")
for nm in [u"training-main", u"kenshu-b", u"kenshu_bucho"]:
    d = dict([(a, b) for a, b in zip(PROBES, [r[1] for r in ROWS if r[0] == nm][0])])
    p(u"  " + nm.ljust(16) + u" seki no hako = " + d[u"inbox_jittai"]
      + u" / tmux pane = " + d[u"tmux_pane"]
      + u" / sb wrapper = " + d[u"sb_wrapper"]
      + u" / mainpc pane = " + d[u"mainpc_pane"])

# ---- ki-2 : haha no ami (order268 no v2 to onaji ; kowarete mo route no bun wa sude ni sunda) ----
p(u"== 7 haha no ami (N no gyou wo tasu) ==")
try:
    DIG = [chr(c) for c in (0x4E00,0x4E8C,0x4E09,0x56DB,0x4E94,0x516D,0x4E03,0x516B,0x4E5D)]
    TEN = chr(0x5341); HUN = chr(0x767E); SEN = chr(0x5343)
    JOU = chr(0x689D); JO = chr(0x6761); STAR = chr(0x2605); NO = chr(0x306E)
    DIGSET = u"".join(DIG) + TEN + HUN
    BOUND = set(DIGSET)
    def okb(ln, j, L):
        if j > 0 and ln[j-1] in BOUND: return False
        if j + L < len(ln) and ln[j+L] in BOUND: return False
        return True
    def val(s):
        n = 0; cur = 0
        for ch in s:
            if ch in DIG: cur = DIG.index(ch) + 1
            elif ch == HUN: n += (cur if cur else 1) * 100; cur = 0
            elif ch == SEN: n += (cur if cur else 1) * 1000; cur = 0
            elif ch == TEN: n += (cur if cur else 1) * 10; cur = 0
        return n + cur
    KOU  = re.compile(u"^#+ .*A3 [" + JOU + JO + u"] ([" + DIGSET + u"]+)")
    OTSU = re.compile(u"^- " + re.escape(u"**") + u"([" + DIGSET + u"]+)" + re.escape(u"**"))
    HEI  = re.compile(u"^- " + STAR + u"([" + DIGSET + u"]+)" + STAR)
    NEWF = re.compile(u"^#+ .*A3 " + NO + u"[" + JOU + JO + u"] ([" + DIGSET + u"]+)")
    WIDE = [(u"kou", KOU), (u"otsu", OTSU), (u"hei", HEI), (u"kou2", NEWF)]
    DD = "scratch/ashigaru-third-3-12e9d4bd/"
    FILES = sorted(glob.glob(DD + "order*.md"))
    tot = 0; got = {}
    for f in FILES:
        fh = open(f, "rb"); body = fh.read().decode("utf-8", "replace"); fh.close()
        lines = body.split(chr(10))
        tot += len(lines) - 1
        for ln in lines:
            for nmp, rx in WIDE:
                m = rx.match(ln)
                if m and okb(ln, m.start(1), len(m.group(1))):
                    v = val(m.group(1))
                    if 100 <= v <= 999: got.setdefault(v, nmp)
    p(u"  haha = " + str(len(FILES)) + u" mai / " + str(tot) + u" gyou (order*.md ; kono kami wa mada nai)")
    p(u"  ami (yon-kei) = " + str(len(got)) + u" hon")
    p(u"  N = " + str(len(got) + 49) + u"  (chuu : 49 = order268 ji no 303 - 254 ; utsushi 0 te 0)")
except Exception as e:
    p(u"  SWEEP-TOORANU : " + repr(e)[:120])

p(u"== 8 shimai ==")
