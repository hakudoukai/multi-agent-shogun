# -*- coding: utf-8 -*-
"""★見本を建てる★ ―― 引数= 建てる先の dir。

★何故 束の中に見本を置かぬか★
  見本 s_A は ``c d.txt`` ―― ★名に空白を含む★。
  之を束の中へ置けば、束の臺帳に ``path=c d.txt `` の行が要る。
  然るに ★此の紙が証して居る疵が直る迄★、repo の照合器は其の行を
  「実体無」と讀む ―― ★己の門が己の束に鳴る★。
  ∴ 見本は此の driver が走る毎に ★束の外へ★ 建てる。
  固定再現は「見本の実体」ではなく「見本を建てる手順」で担保する。
"""
import hashlib, os, sys

def main(argv):
    if len(argv) < 2:
        print("usage: 10_mihon_wo_tateru.py <建てる先>", file=sys.stderr)
        return 2
    fx = argv[1]
    for d in ("s_A", "s_B", "s_C", "s_D", "s_E", "s_F", "s_G"):
        os.makedirs(os.path.join(fx, d), exist_ok=True)

    def put(d, name, data):
        open(os.path.join(fx, d, name), "wb").write(data)
        return hashlib.sha256(data).hexdigest(), len(data), data.count(b"\n")

    def man(d, row):
        open(os.path.join(fx, d, "manifest.txt"), "w", encoding="utf-8").write(row + "\n")

    # s_A ★素の空白名★ ―― 裁 seq321353⑵ ゆゑ新規行は括れぬ。之が表せぬ物。
    h, b, l = put("s_A", "c d.txt", b"abc\n")
    man("s_A", "path=c d.txt sha256=%s bytes=%d lines=%d" % (h, b, l))
    # s_B ★舊形(括つた)★ ―― 既存行ゆゑ拒んではならぬ(裁 seq321353⑴)
    h, b, l = put("s_B", "e.txt", b"def\n")
    man("s_B", 'path="e.txt" sha256=%s bytes=%d lines=%d' % (h, b, l))
    # s_C ★陰性対照★ ―― 清い名。四版悉く通らねばならぬ。
    h, b, l = put("s_C", "kiyoi.txt", b"ghi\n")
    man("s_C", "path=kiyoi.txt sha256=%s bytes=%d lines=%d" % (h, b, l))
    # s_D ★陽性対照★ ―― 実体の無い名。★直した後も必ず鳴らねばならぬ★。
    #     「候補を足す」直しが門を fail-open へ開いて居らぬ事を、之だけが示す。
    man("s_D", "path=nai.txt sha256=%s bytes=4 lines=1" % ("0" * 64))
    # ★s_E 共存(軍師mac REVISE seq327560 の見本)★ ―― ``a`` と ``a b.txt`` が★共に実在★。
    #     臺帳が主張するのは full の ``a b.txt``。短縮 ``a`` が先に昇れば sha が食ひ違ひ
    #     ★正しい物が rc=1 で鳴る(偽陰性)★。第二版は full を選ぶ故 rc=0 でなければならぬ。
    put("s_E", "a", b"AAA\n")                      # ★短縮の名が実在する★
    h, b, l = put("s_E", "a b.txt", b"jkl\n")
    man("s_E", "path=a b.txt sha256=%s bytes=%d lines=%d" % (h, b, l))
    # ★s_F 家老の穴(自訴 seq327562 の見本)★ ―― 臺帳の主張 ``README.md bak`` は★不在★、
    #     prefix ``README.md`` は★実在★し、其の sha が臺帳の sha と一致する。
    #     短縮が昇れば ★誤つた物が rc=0 で通る(偽陽性=fail-open)★。
    #     ★第二版は rc≠0 で鳴らねばならぬ ―― 之が委員長裁 seq327582「不在は rc≠0」。★
    h, b, l = put("s_F", "README.md", b"mno\n")
    man("s_F", "path=README.md bak sha256=%s bytes=%d lines=%d" % (h, b, l))
    # ★s_G 誤 hash(軍師mac「誤hash 負1は維持」)★ ―― 名は正しく、sha だけ誤る。
    #     直しても ★必ず rc=1 で鳴らねばならぬ★(相違を見落さぬ事の證)。
    h, b, l = put("s_G", "g.txt", b"pqr\n")
    man("s_G", "path=g.txt sha256=%s bytes=%d lines=%d" % ("1" * 64, b, l))
    print("見本 七本 建てた: %s" % fx)
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
