# -*- coding: utf-8 -*-
# ★㋕ の下地 ―― 己の疵を「封じた物」と「封じて居らぬ物」に分ける器★
#
# ★封の定義を ★先に★ 書く(㋓で咎めた病を己が踏まぬ為)★
#   甲 ★機構封★ = ★己の手を離れても鳴る★物。門の條・hook・script の中の判定。
#                  己が忘れても、己が居なくても、次に触る者の前で鳴る。
#   乙 ★覚封★  = 覚(memory file)に在る。★己が讀めば★鳴る。讀まねば鳴らぬ。
#                 加へて索引 MEMORY.md が上限を越えて居れば ★載つて居ても讀まれぬ★。
#   丙 ★無封★  = 紙に書いたのみ。★誰の前でも鳴らぬ。★
#
# ★「直した」と「封じた」は別である。★ 本弾は ★変更0★ の札 ―― 故に本弾で見付けた疵は
# ★一つも機構封に出来ぬ★。之を「直した」と書けば偽りである。
import os, sys, time, hashlib

# ★走一は ここで倒れた★ ―― '..' を三つしか積まず、歩き根が docs/ を指した。
# ★門の path が解けず、陽性対照が『讀めぬ』を返し、器は零を刷らずに止まつた(81_fuuji.taoreta.out)。★
# ★對照が無ければ「封は一つも無い」と刷つて居た ―― 之は恒真の器が出す偽の答である。★
NE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..'))
OBOE = os.path.expanduser('~/.claude/projects/-Users-momizimac-multi-agent-shogun/memory')
SAKUIN = os.path.join(OBOE, 'MEMORY.md')
MON = os.path.join(NE, 'scripts/checks/karo_mac_dasumae_gate.sh')
SETT = os.path.join(NE, '.claude/settings.json')

out = []
def w(s): out.append(s)

def yomu(p):
    try:
        with open(p, 'rb') as f: return f.read()
    except Exception as e:
        return None

def sagasu(p, moji):
    """path の中に moji が在るか。戻り = (在/無/讀めぬ, 行番号 or 0)"""
    b = yomu(p)
    if b is None: return ('讀めぬ', 0)
    try: t = b.decode('utf-8')
    except UnicodeDecodeError: t = b.decode('utf-8', 'replace')
    for i, l in enumerate(t.split('\n'), 1):
        if moji in l: return ('在', i)
    return ('無', 0)

w('刻 = %s\n' % time.strftime('%Y-%m-%dT%H:%M:%S'))
w('歩き根 = %s\n' % NE)
w('覚の在り所 = %s\n' % OBOE)
w('')

# ── 零 ★対照 ―― 探し器が「在る」と「無い」を分けられるか★ ────────────
w('― 零 ★陽性対照・陰性対照(同じ探し器を通す)★ ―\n')
you = sagasu(MON, 'DASUMAE_MAX_BYTES')      # ★門に必ず在る字★
inn = sagasu(MON, '★此の字は門に在らぬ筈である_zzz★')  # ★在らぬ筈の字★
w('  陽性 「DASUMAE_MAX_BYTES」 in 門 → %s (L%d)\n' % you)
w('  陰性 「…在らぬ筈…zzz」    in 門 → %s (L%d)\n' % inn)
if you[0] != '在' or inn[0] != '無':
    w('  ★対照 倒★ ―― 探し器が信ぜられぬ。以下を刷らぬ。\n')
    sys.stdout.write(''.join(out)); sys.exit(2)
w('  ★対照 通 ―― 「無」は「見えなんだ」ではない。★\n\n')

# ── 一 ★索引の丈 ―― 覚封が本当に讀まれるか★ ──────────────────
w('― 一 ★覚の索引(MEMORY.md)を測る ―― 「書いた」は「讀まれる」を意味せぬ★ ―\n')
sb = yomu(SAKUIN)
if sb is None:
    w('  ★索引が讀めぬ ―― 覚封は悉く「測れぬ」へ落ちる。★\n')
    saku_lines, saku_map, JOUGEN = 0, {}, 200
else:
    st = sb.decode('utf-8', 'replace')
    rows = st.split('\n')
    saku_lines = len(rows)
    JOUGEN = 200   # ★走時が刷つた上限(warning 逐語: limit: 200)★
    saku_map = {}
    for i, l in enumerate(rows, 1):
        if '](' in l:
            nm = l.split('](', 1)[1].split(')', 1)[0]
            saku_map[nm] = i
    w('  索引 = %s\n' % SAKUIN)
    w('  行 = %d / 上限 = %d / ★超過 = %d 行★\n' % (saku_lines, JOUGEN, max(0, saku_lines - JOUGEN)))
    w('  sha16 = %s / %d byte\n' % (hashlib.sha256(sb).hexdigest()[:16], len(sb)))
    w('  ★走時の逐語 ≪WARNING: MEMORY.md is %d lines (limit: %d). Only part of it was loaded.≫★\n'
      % (saku_lines, JOUGEN))
    w('  ★∴ %d 行目より下に在る覚は、索引に在つても ★載らぬ★。覚封は其処で切れる。★\n' % JOUGEN)
w('')

# ── 二 ★疵の一覧と、其々の封の在り所★ ─────────────────────
# (弾, 一行, 封候補: [(層, path, 探す字)])
KIZU = [
 ('48-1', '走一の argv を $(cat) で組み、空白入りの名が割れ byte和が3少く出た',
   [('乙', 'feedback_space_in_name_counter_must_ask_the_disk.md', None),
    ('乙', 'reference_line_unit_instruments_break_on_newline_names.md', None)]),
 ('48-2', '陰性対照の汚し所を勘で選び、差に呑まれて 1/3 落とした',
   [('乙', 'feedback_a_zero_needs_four_tags_and_a_routed_control.md', None),
    ('乙', 'feedback_prove_the_negative_control_absent_before_using_it.md', None)]),
 ('48-3', '己の覚に在る法を己が踏んだ($p★ で bash 3.2 に ★ を喰はれ rc=1)',
   [('乙', 'reference_bash_var_name_absorbs_fullwidth_chars.md', None),
    ('乙', 'reference_multibyte_char_absorbed_into_var_name.md', None)]),
 ('48-4', '家老の「10532919」を着手便で検めずに受けた',
   [('乙', 'feedback_align_instruments_before_disputing_a_number.md', None)]),
 ('48-5', '「全ての生の産物に kaki を通す」を全うできなんだ(多byte割れの .err)',
   [('乙', 'feedback_every_raw_text_product_goes_through_kaki.md', None),
    ('甲', 'scripts/checks/karo_mac_dasumae_gate.sh', '條④')]),
 ('48-6', '則 乙 が「己の束を通す為の則」に見え得る(先に宣して逃げ道を塞いだ)',
   [('乙', 'feedback_naming_an_escape_hatch_hides_the_breach.md', None)]),
 ('50-A', '52 の見出しに「51 と同じ母集合」と書きながら別の數を刷つた(偽の題)',
   [('丙', None, None)]),
 ('50-B', '回転した箱を根に「追補 = 0 通」と結論しかけた(無い物から割れ目)',
   [('乙', 'reference_inbox_rotation_keeps_30_read_sender_triggers_no_sender_copy.md', None),
    ('乙', 'feedback_measure_before_calling_it_lost.md', None)]),
 ('50-C', '70 の刻換算で timegm-timezone と符號を違へ、9時間先の刻を作つた',
   [('丙', None, None)]),
 ('50-D', '70 の歩き根に .claude/ を丸ごと取り、他席の物 97 本を己の欄に置きかけた',
   [('乙', 'feedback_narrow_bogen_hides_your_own_conduct.md', None)]),
 ('50-E', '60 に藏を足して過剰採取し、他弾の便 8 通を第48弾の欄に入れかけた',
   [('乙', 'feedback_a_range_is_names_and_shas_not_a_count.md', None)]),
 ('50-F', '30 の母數「/ 21」を ★器でなく手で書いた★(實は 24 形) ―― 本弾が咎めて居る当の病',
   [('乙', 'feedback_do_not_declare_a_count_before_the_builder_runs.md', None),
    ('乙', 'feedback_the_instrument_printing_the_number_can_be_wrong.md', None)]),
]

w('― 二 ★疵ごとの封 ―― 現物を当たる★ ―\n')
kou, otsu, otsu_kire, hei, hakare = [], [], [], [], []
for kid, hito, fudas in KIZU:
    w('  ★疵 %s★ %s\n' % (kid, hito))
    if not fudas or fudas[0][0] == '丙':
        w('      層丙 ★無封★ ―― 紙に書いたのみ。機構も覚も無い。★誰の前でも鳴らぬ。★\n')
        hei.append(kid); continue
    tuita = False
    for sou, p, moji in fudas:
        if sou == '甲':
            ap = os.path.join(NE, p)
            r, ln = sagasu(ap, moji)
            w('      層甲 %s に「%s」 → %s (L%d)\n' % (p, moji, r, ln))
            if r == '在':
                tuita = True; kou.append((kid, p, ln))
                # ★封が疵の全部に当たるとは限らぬ ―― 當たる所を書く★
                w('           ★但し 條④ が見るのは ★結果(EOF 改行の欠け)★ であつて、\n')
                w('             ★kaki を通さなんだ事★ 其の物ではない。多byte割れの .err は\n')
                w('             ★改行が揃つて居れば門を通る★。∴ 此の封は ★疵の一部にしか当たらぬ★。\n')
        else:
            ap = os.path.join(OBOE, p)
            aru = os.path.isfile(ap)
            gyo = saku_map.get(p, 0)
            nose = (0 < gyo <= JOUGEN)
            w('      層乙 覚 %s → %s / 索引 L%s / %s\n'
              % (p, ('在' if aru else '★無★'),
                 (gyo if gyo else '★索引に無し★'),
                 ('★載る★' if nose else '★上限の外 ―― 載らぬ★' if gyo else '★索引に無し ―― 載らぬ★')))
            if aru and nose: tuita = True; otsu.append((kid, p, gyo))
            elif aru: otsu_kire.append((kid, p, gyo))
    if not tuita:
        hakare.append(kid)
        w('      ★∴ 現に鳴る封は無い(覚は在るが索引の外/索引に無し)。★\n')
w('')

# ── 三 ★分けた結果★ ───────────────────────────────
w('― 三 ★封じた / 封じて居らぬ★ ―\n')
# ★欄の名に単位を焼き込む ―― 「15 件」と刷りながら 10 の疵を列ねれば、
#   ★本弾が咎めて居る当の病(どの數が何を数へて居るか)★ を己が犯す。★
w('  甲 機構封(己の手を離れて鳴る)  疵 %d 件 / 封 %d 本  %s\n'
  % (len(set(k for k, _, _ in kou)), len(kou), ' '.join(sorted(set(k for k, _, _ in kou))) or '―'))
w('  乙 覚封・索引に載る(讀めば鳴る) 疵 %d 件 / 覚 %d 本  %s\n'
  % (len(set(k for k, _, _ in otsu)), len(otsu), ' '.join(sorted(set(k for k, _, _ in otsu))) or '―'))
w('  乙\' 覚は在るが索引の外(載らぬ)  疵 %d 件 / 覚 %d 本  %s\n'
  % (len(set(k for k, _, _ in otsu_kire)), len(otsu_kire),
     ' '.join(sorted(set(k for k, _, _ in otsu_kire))) or '―'))
w('  丙 無封(紙のみ)                 = %d 件  %s\n'
  % (len(hei), ' '.join(hei) or '―'))
w('\n  ★本弾(50-*)の疵は %d 件 ―― 其の内 機構封 = 0 件★\n'
  % len([k for k, _, _ in KIZU if k.startswith('50')]))
w('  ★因は明白である ―― 本弾の札は ★変更0★。生器へ一字も据ゑぬ。★\n')
w('  ★∴ 本弾で見付けた疵を「直した」と書けば偽りとなる。★書けるのは「紙に据ゑた」迄である。★\n')
w('  ★封ずるには ⑴委員長の許可 ⑵生器への据ゑ ⑶門で鳴る事の確認 の三つが要る。★\n')
w('  ★己の手で出来るのは ⑴の願ひ出だけである。★\n')
# ★覚が載つて居ながら踏んだ疵 ―― 覚封の強さを測る唯一の現物★
FUMI = {'48-3': '第48弾の紙が己で「★己の MEMORY に在る法を己が踏んだ★」と書いて居る(逐語・L235)',
        '50-F': '本弾 ―― 覚二本(L60・L70)が索引に載つて居りながら、母數を手で書いた'}
nose = set(k for k, _, _ in otsu)
w('\n  ★覚封の強さ ―― 「載つて居りながら踏んだ」疵★\n')
for k, riyu in sorted(FUMI.items()):
    w('    %s ★踏んだ★ ―― %s\n' % (k, riyu))
w('    ★覚封 %d 件の内 %d 件が「載つて居りながら踏まれた」。★\n'
  % (len(nose), len([k for k in FUMI if k in nose])))
w('    ★∴ 覚封は「鳴る事が在る封」であつて「鳴る封」ではない。★\n')
w('')

# ── 四 ★索引の外へ落ちた覚 ―― 「在る」が「載る」を意味せぬ現物★ ──────
w('― 四 ★索引の %d 行目より下に在る覚(★書いたが載らぬ★)★ ―\n' % JOUGEN)
soto = sorted([(g, n) for n, g in saku_map.items() if g > JOUGEN])
if not soto:
    w('  ★零 ―― 上限を越えた行に覚の項は無い(超過 %d 行は註か空行)。★\n'
      % max(0, saku_lines - JOUGEN))
    w('  ★但し零は「安全」を意味せぬ ―― 次に一項足せば %d 行目が外へ出る。★\n' % (JOUGEN + 1))
else:
    for g, n in soto:
        w('  L%-4d %s\n' % (g, n))
    w('  ★計 %d 件 ―― 之等は覚の file が在つても、次の走りの目には入らぬ。★\n' % len(soto))
    # ★四.五 ―― 落ちた覚の中に ★本弾の題★ が在るか。字で当たる(勘で選ばぬ)★
    KAGI = ['fail-open', 'fail_open', '門', '閾', 'gate', 'threshold', 'DASUMAE']
    w('\n  ★四.五 落ちた覚の中身を当たる ―― 鍵 = %s★\n' % ' / '.join(KAGI))
    atari = 0
    for g, n in soto:
        bb = yomu(os.path.join(OBOE, n))
        if bb is None:
            w('    L%-4d %s ―― ★讀めぬ★\n' % (g, n)); continue
        tt = bb.decode('utf-8', 'replace')
        setsu = ''
        for l in tt.split('\n'):
            if l.startswith('description:'): setsu = l[12:].strip(); break
        hit = [k for k in KAGI if k in tt]
        if hit:
            atari += 1
            w('    ★当★ L%-4d %s\n' % (g, n))
            w('           鍵 = %s\n' % ' '.join(hit))
            w('           逐語(description) ≪%s≫\n' % setsu[:160])
    w('  ★落ちた %d 件の内 ★%d 件★ が本弾の題(門・閾・fail-open)に触れて居る。★\n' % (len(soto), atari))
    w('  ★∴ ㋐(空の閾)・㋑(閾0 の恒真)で己が踏んだ穴は、★既に覚に書いて在つた★。\n')
    w('    書いて在り、file も在り、索引にも在り、★然し載らなんだ★。\n')
    w('    ★之が「覚封は封に非ず」の現物である。★機構封との差は此処に在る。★\n')
w('  ★上の二で「載る」と出た %d 件も、★索引が伸びれば黙つて外へ出る★。\n' % len(set(k for k, _, _ in otsu)))
w('    封は ★固定されて居らぬ★ ―― 之は機構封との決定的な差である。★\n')

sys.stdout.write(''.join(out))
