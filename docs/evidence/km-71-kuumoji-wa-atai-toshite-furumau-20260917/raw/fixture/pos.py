# 陽性対照 ―― 各形 一つづつ(檢出子 20 が拾はねばならぬ)。走らせぬ(讀むのみ)。
def pos(s, st, m, d):
    a = s[:1] in 'AM'                 # 形A 包含 in(右が str 定数)
    b = s == ''                       # 形B 等価 ==(空文字と比べる)
    c = st or 'default'               # 形C 既定落ち or(右が定数)
    if s:                             # 形D 真偽 if(裸の名)
        pass
    e = m.group(1) if m else '?'      # 形E 三項の既定(IfExp・else が定数)
    f = s.startswith('')              # 形F startswith('')(常に True)
    return a, b, c, e, f
