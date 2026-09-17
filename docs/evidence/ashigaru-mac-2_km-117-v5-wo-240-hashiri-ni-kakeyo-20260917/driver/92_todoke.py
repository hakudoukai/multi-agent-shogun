# -*- coding: utf-8 -*-
"""★送つた(rc=0)は届いたに非ず★(memory「Sent is not delivered」)。箱の尾を讀んで證す ―― 刻の窓で当てるのではなく胴を照合する。"""
import io, os, sys, time, yaml
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(B)))
sys.path.insert(0, os.path.join(B, "driver"))
from kaki import kaku

hako = os.path.join(REPO, "queue", "inbox", "karo-mac.yaml")
d = yaml.safe_load(io.open(hako, encoding="utf-8").read())
ms = d["messages"]
last = ms[-1]
body = last.get("content", "")
okuri = io.open(os.path.join(B, "raw", "90_fumi.txt"), encoding="utf-8").read()
onaji = body.strip() == okuri.strip()

o = ["# km-114 納めの届け ―― ★箱の尾で證した★(送りの rc だけでは足らぬ)",
     "# 刻 " + time.strftime("%Y-%m-%dT%H:%M:%S%z"),
     "",
     "箱\tqueue/inbox/karo-mac.yaml",
     "送る前の項数\t35",
     "送つた後の項数\t%d" % len(ms),
     "送りの rc\t0",
     "尾の id\t%s" % last.get("id"),
     "尾の from / type / read\t%s / %s / %s" % (last.get("from"), last.get("type"), last.get("read")),
     "尾の timestamp\t%s" % last.get("timestamp"),
     "尾の胴 字数\t%d" % len(body),
     "束の便(raw/90_fumi.txt) 字数\t%d" % len(okuri),
     "差\t%d 字(末の改行のみ)" % (len(okuri) - len(body)),
     "★胴の一致(strip 後の全文照合)★\t%s" % ("一致" if onaji else "★不一致★"),
     "",
     "  註 2000字で切る路は★跨PC橋(Supabase)★の側のみ(inbox_write.sh L208)。",
     "     家老mac は同PCゆゑ橋を通らず、局所箱へ★全文★が入つた ―― 之を字数で確かめた。",
     "",
     "## 己の札",
     "queue/tasks/ashigaru-mac-2.yaml status\tassigned → done(completed_at 2026-09-17T19:15:43+0900)",
     "  註 ★己の yaml のみ触つた★(他席の yaml 不触)。commit・push は★せず★。",
     "",
     "## 員外(本紙も加はる)",
     "  本紙 raw/92_todoke.txt と driver/92_todoke.py は★臺帳凍結後★の産物ゆゑ員外。",
     "  ∴ 員外は 9 → 11 本。名と理は raw/91_ingai.txt の通り ―― ★増える事自体が臺帳が時点の写しである證★。",
     "",
     "## 之が意味せぬ事",
     "  ・「箱に入つた」は「家老殿が讀んだ」を意味せぬ ―― read=False である。",
     "  ・字数の一致は「中身が正しい」を意味せぬ ―― 送つた物と入つた物が同じ、だけを云ふ。",
     "  ・軍師mac への監査提出は★己では出来ぬ★(rc=68 の死箱)。回付を家老殿に請うた ―― ★請うた事は回付された事に非ず★。",
     ]
kaku(os.path.join(B, "raw", "92_todoke.txt"), "\n".join(o))
print("\n".join(o))
