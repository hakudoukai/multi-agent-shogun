# 陰性対照 ―― 似て非なる形(檢出子 20 が拾つてはならぬ)。走らせぬ(讀むのみ)。
def neg(s, st, m, d):
    a = s[:1] in ('A', 'M')           # in の右が tuple(空文字は含まれぬ)
    b = s == 'A'                      # == の相手が非空の定数
    c = st or m                       # or の右が定数でない
    if s is None:                     # is None(真偽でない)
        pass
    e = m.group(1) if m is not None else m.group(2)   # else が定数でない
    f = s.startswith('A')             # startswith の引数が非空
    return a, b, c, e, f
