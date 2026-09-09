# -*- coding: utf-8 -*-
# order235 E31 v3 : cross-table of window-sign (proxy) vs hand-label (this seat)
# read-only. no product run. burns only this instrument.
import io, os, re, collections
D  = u"scratch/ashigaru-third-3-12e9d4bd"
RAW = os.path.join(D, u"order235_e31_hand_label_v1.raw.txt")
A = chr(0x32D0); B = chr(0x32D1); C = chr(0x32D2); E = chr(0x32D3); W = u"MONGON"
SIGN = {u"U+32D0": A, u"U+32D1": B, u"U+32D2": C, u"U+32D3": E}

# hand labels, this seat, read by eye from the 53 windows (stage 1..5)
HAND = (A,A,W,C,C,A,A,A,A,C,W,W,
        B,A,C,B,A,B,W,B,A,C,C,W,
        C,W,B,C,W,A,A,C,C,C,C,A,
        C,W,W,A,A,B,W,A,A,B,B,W,
        A,A,W,B,W)

t = io.open(RAW, encoding="utf-8").read().split(chr(10))
hdr = []
for ln in t:
    m = re.match(r"^---- #(\d+)\s+(\S+):(\d+)\s+sign=(U\+[0-9A-F]{4})\s+home=(\S+)", ln)
    if m: hdr.append((int(m.group(1)), m.group(2), int(m.group(3)), SIGN[m.group(4)], m.group(5)))
assert len(hdr) == 53, "HDR=%d" % len(hdr)
assert len(HAND) == 53, "HAND=%d" % len(HAND)

cross = collections.defaultdict(int); agree = 0; agree_ids = []
sign_n = collections.Counter(); hand_n = collections.Counter()
home_by_hand = collections.defaultdict(collections.Counter)
for (i, f, l, s, home), h in zip(hdr, HAND):
    cross[(s, h)] += 1; sign_n[s] += 1; hand_n[h] += 1
    home_by_hand[h][home] += 1
    if s == h: agree += 1; agree_ids.append(i)

print("== sign (window proxy) vs hand (this seat) : n=53 ==")
KIND = [A, B, C, E]
print("sign\\hand  " + "  ".join(KIND) + "  " + W + "   tot")
for s in KIND:
    row = [cross[(s, h)] for h in KIND] + [cross[(s, W)]]
    print("   %s      %s   %3d" % (s, "  ".join(" %d" % v for v in row), sign_n[s]))
print("hand tot   " + "  ".join(" %d" % hand_n[h] for h in KIND) + "   %d" % hand_n[W])
print("")
print("agree = %d / 53 = %.1f%%  ids=%s" % (agree, 100.0*agree/53, ",".join("%02d" % i for i in agree_ids)))
for s in KIND:
    hit = cross[(s, s)]; tot = sign_n[s]
    print("  sign %s : hit %d / %d" % (s, hit, tot))
print("")
print("== hand label by home (where the line lives) ==")
for h in KIND + [W]:
    print("  %s : %s" % (h, dict(home_by_hand[h])))
print("")
print("== new-instance accounting (per stage of 12) ==")
cum = 12
for s0 in range(0, 53, 12):
    grp = HAND[s0:s0+12]
    ni = sum(1 for x in grp if x != W); mg = sum(1 for x in grp if x == W)
    cum += ni
    print("  STAGE %d : cand %2d..%2d  new=%2d  mongon=%2d  12->%d" % (s0//12+1, s0+1, min(s0+12,53), ni, mg, cum))
print("  total new = %d / mongon = %d / 12 -> %d" % (sum(1 for x in HAND if x != W), sum(1 for x in HAND if x == W), cum))
