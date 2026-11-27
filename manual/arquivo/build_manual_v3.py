#!/usr/bin/env python3
"""build_manual_v3.py - manual do Fairy IC Test Card RESTAURADO (folhas A5, visual da impressao
de 1984) + secao (V) com a Version 2.0 Expanded (CIs novos e teste de memorias).
Reaproveita o texto transcrito e os desenhos do build_manual.py (v1/v2)."""
import json, pathlib, re, weasyprint

HERE = pathlib.Path(__file__).parent
BASE = HERE / 'build_manual_v2.py' if (HERE / 'build_manual_v2.py').exists() else HERE / 'build_manual.py'
src = BASE.read_text()
ns = {'__file__': str(BASE)}
exec(src[:src.index('def socket_svg')], ns)          # listas, LOGO, SYS_DIAG, VR_DIAG, FLOW
TTL_STD, LS, S, L, H, RAM = (ns[k] for k in ('TTL_STD', 'LS', 'S', 'L', 'H', 'RAM'))
HC, CD, MEM, ADD_CD, ADD_HC = (ns[k] for k in ('HC', 'CD', 'MEM', 'ADD_CD', 'ADD_HC'))
ADDED = json.load(open(HERE / 'added_v2.json'))

SERIF = "'TeX Gyre Termes'"
TITLE = "'TeX Gyre Schola'"
SANS = "'TeX Gyre Heros'"

def mono(svg, font=SERIF):
    """desenhos em preto e branco, com a fonte da impressao original"""
    svg = re.sub(r'font-family="[^"]*"', f'font-family="{font.strip(chr(39))}"', svg)
    return svg.replace('#f3f6fa', '#fff').replace('#e9f3ee', '#fff')

SYS_DIAG = mono(ns['SYS_DIAG'])
VR_DIAG = mono(ns['VR_DIAG'])
FLOW = mono(ns['FLOW'])

def pre(xs, p): return [p + x for x in xs]

def grid(items, cols=7):
    rows = [items[i:i + cols] for i in range(0, len(items), cols)]
    h = '<table class="ics">'
    for r in rows:
        h += '<tr>' + ''.join(f'<td>{x}</td>' for x in r) + '<td></td>' * (cols - len(r)) + '</tr>'
    return h + '</table>'

# ---------------------------------------------------------------- capa: "IC" vazado
COVER_IC = f'''<svg viewBox="0 0 120 110" width="30mm" xmlns="http://www.w3.org/2000/svg">
<text x="2" y="98" font-family="TeX Gyre Heros Cn" font-weight="bold" font-size="122" fill="#fff"
 stroke="#000" stroke-width="3.2" letter-spacing="-2">IC</text></svg>'''

# ---------------------------------------------------------------- tela do monitor (estilo do original)
def screen(lines, ic='74-LS – 138', note=False, w='100mm'):
    body = ''
    for kind, t in lines:
        if kind == 'c':
            body += f'<div class="c">{t}</div>'
        elif kind == 'l':
            body += f'<div class="l">{t}</div>'
        elif kind == 'box':
            n = ' <span class="red">(*</span>' if note else ''
            body += f'<div class="icbox">{ic}{n}</div>'
        elif kind == 'sp':
            body += '<div class="sp"></div>'
    return f'<div class="crt" style="width:{w}">{body}</div>'

SCR_ORIG = screen([('c', 'UNIVERSAL IC TESTER'), ('c', 'BY YIH LUNG ENTERPRISE CO., LTD.'), ('sp', ''),
                   ('c', '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;COPYRIGHT 1984'), ('c', 'TEST IC NO.'), ('box', ''),
                   ('l', 'CTRL-S &nbsp;: SEARCH IC NO.'), ('l', 'CTRL-C &nbsp;: CHANGE IC NO.'),
                   ('l', 'CTRL-L &nbsp;: LOOP TEST'), ('l', 'SPACE &nbsp;&nbsp;&nbsp;: START TESTING'),
                   ('l', 'CTRL-S, CTRL-C, CTRL-L OR SPACE ? <span class="cur">▨</span>'),
                   ('l', 'RESULT : TEST OK')], note=True)

SCR_V2 = screen([('c', 'UNIVERSAL I.C. TESTER (PART-II)'), ('sp', ''), ('c', '195 ICS AVAILABLE FOR TEST'), ('sp', ''),
                 ('c', 'BY YIH-LUNG ENTERPRISES CO.,LTD.'), ('c', 'VERSION 2.0 EXPANDED BY TABAJARA LABS'),
                 ('c', '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;COPYRIGHT 1984/2026'), ('sp', ''),
                 ('c', 'TESTED IC NO.'), ('box', ''),
                 ('l', 'CTRL-S : SEARCH IC. NO.'), ('l', 'CTRL-C : CHANGE IC. NO.'), ('l', 'CTRL-L : LOOP TEST'),
                 ('l', 'SPACE &nbsp;&nbsp;: START TESTING'), ('l', 'CTRL-S, CTRL-C, CTRL-L, OR SPACE ?'),
                 ('l', 'RESULT : TEST OK')], ic='74-LS – 036')

SCR_MENU = screen([('sp', ''), ('l', '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;A: TTL 54/74 SERIES'), ('sp', ''),
                   ('l', '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;B: CMOS 40/45 SERIES'), ('sp', ''),
                   ('l', '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;C: HCMOS 74HC SERIES'), ('sp', ''),
                   ('l', '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;D: MEMORY (RAM)'), ('sp', ''),
                   ('l', '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;WHICH ONE ? A , B , C OR D'), ('sp', '')], w='88mm')

SCR_MEM = screen([('c', 'MEMORY TESTER - VERSION 2.0'), ('sp', ''),
                  ('l', '1: 2114 &nbsp;&nbsp;SRAM &nbsp;1K X 4 &nbsp;(JUMPER)'), ('l', '2: 2147 &nbsp;&nbsp;SRAM &nbsp;4K X 1 &nbsp;(JUMPER)'),
                  ('l', '3: 4164 &nbsp;&nbsp;DRAM 64K X 1 &nbsp;(REVERSED)'), ('l', '4: 41256 DRAM 256K X 1 (REVERSED)'),
                  ('l', '5: 4416 &nbsp;&nbsp;DRAM 16K X 4 &nbsp;(REV+JUMPER)'), ('l', '6: 4464 &nbsp;&nbsp;DRAM 64K X 4 &nbsp;(REV+JUMPER)'),
                  ('l', '7: 6116 &nbsp;&nbsp;SRAM &nbsp;2K X 8 &nbsp;(ADAPTER)'), ('l', '8: 6264 &nbsp;&nbsp;SRAM &nbsp;8K X 8 &nbsp;(ADAPTER)'),
                  ('sp', ''), ('l', 'WHICH ONE ? (1-8, ESC = MENU)')], w='92mm')

# ---------------------------------------------------------------- posicao das memorias no Testool
PIN = {
 '2114': {1:'A6',2:'A5',3:'A4',4:'A3',5:'A0',6:'A1',7:'A2',8:'CS',9:'GND',10:'WE',11:'I/O4',12:'I/O3',13:'I/O2',14:'I/O1',15:'A9',16:'A8',17:'A7',18:'VCC'},
 '2147': {1:'A0',2:'A1',3:'A2',4:'A3',5:'A4',6:'A5',7:'DOUT',8:'WE',9:'GND',10:'CS',11:'DIN',12:'A6',13:'A7',14:'A8',15:'A9',16:'A10',17:'A11',18:'VCC'},
 '4164': {1:'(A8)',2:'DIN',3:'WE',4:'RAS',5:'A0',6:'A2',7:'A1',8:'VCC',9:'A7',10:'A5',11:'A4',12:'A3',13:'A6',14:'DOUT',15:'CAS',16:'GND'},
 '4416': {1:'OE',2:'DQ1',3:'DQ2',4:'WE',5:'RAS',6:'A6',7:'A5',8:'A4',9:'VCC',10:'A7',11:'A3',12:'A2',13:'A1',14:'A0',15:'DQ3',16:'CAS',17:'DQ4',18:'GND'},
}

def pin_at(pos, p, rot):
    n = p // 2
    if not rot:
        if pos <= 10:
            k = pos - (10 - n); return k if 1 <= k <= n else 0
        return n + (pos - 10) if pos - 10 <= n else 0
    if pos >= 11:
        k = pos - 10; return k if k <= n else 0
    k = pos + (p - 10); return k if k > n else 0

def place_svg(title, key, p, rot, jumper):
    W, H = 290, 345
    x0, x1, y0, dy = 100, 190, 44, 27
    s = [f'<svg viewBox="0 0 {W} {H}" width="55mm" xmlns="http://www.w3.org/2000/svg" font-family="TeX Gyre Heros" font-size="9">']
    s.append(f'<text x="{(x0+x1)/2}" y="14" text-anchor="middle" font-size="12.5" font-weight="bold">{title}</text>')
    s.append(f'<rect x="{x0-13}" y="{y0-17}" width="{x1-x0+26}" height="{dy*9+34}" fill="none" stroke="#000" stroke-width=".8" stroke-dasharray="3 2"/>')
    rows = [r for r in range(1, 11) if pin_at(r, p, rot)]
    ya = y0 + (min(rows) - 1) * dy - 11; yb = y0 + (max(rows) - 1) * dy + 11
    s.append(f'<rect x="{x0-8}" y="{ya}" width="{x1-x0+16}" height="{yb-ya}" fill="#fff" stroke="#000" stroke-width="1.6"/>')
    cx = (x0 + x1) / 2
    ny = ya if not rot else yb
    s.append(f'<path d="M{cx-9} {ny} a9 9 0 0 {0 if not rot else 1} 18 0" fill="#fff" stroke="#000" stroke-width="1.6"/>')
    s.append(f'<text x="{cx}" y="{(ya+yb)/2+4}" text-anchor="middle" font-size="12" font-weight="bold">{key}</text>')
    for r in range(1, 11):
        y = y0 + (r - 1) * dy
        for pos, x in ((r, x0), (21 - r, x1)):
            k = pin_at(pos, p, rot)
            left = pos <= 10
            s.append(f'<rect x="{x-4.5}" y="{y-4.5}" width="9" height="9" fill="{"#000" if k else "#fff"}" stroke="#000"/>')
            px = x0 - 78 if left else x1 + 78
            s.append(f'<text x="{px}" y="{y+3.2}" text-anchor="{"end" if left else "start"}" font-size="8" fill="#555">{pos}</text>')
            if k:
                nm = f'{k}  {PIN[key][k]}' if left else f'{PIN[key][k]}  {k}'
                s.append(f'<text x="{x0-19 if left else x1+19}" y="{y+3.2}" text-anchor="{"end" if left else "start"}">{nm}</text>')
    s.append(f'<text x="{x0-78}" y="{y0+9*dy+15}" text-anchor="end" font-size="8" font-weight="bold">GND</text>')
    s.append(f'<text x="{x1+78}" y="{y0-15}" text-anchor="start" font-size="8" font-weight="bold">VCC</text>')
    if jumper:
        s.append(f'<path d="M{x1+4} {y0} C {x1+17} {y0}, {x1+17} {y0+dy}, {x1+4} {y0+dy}" fill="none" stroke="#000" stroke-width="2.6"/>')
    s.append(f'<text x="{cx}" y="{H-4}" text-anchor="middle" font-size="9">{("REVERSED : NOTCH DOWN" if rot else "NOTCH UP") + (" · JUMPER 19–20" if jumper else "")}</text>')
    s.append('</svg>')
    return ''.join(s)

PLACE1 = place_svg('2114', '2114', 18, False, True) + place_svg('2147', '2147', 18, False, True)
PLACE2 = place_svg('4164 / 41256', '4164', 16, True, False) + place_svg('4416 / 4464', '4416', 18, True, True)

ADP = '''<svg viewBox="0 0 360 232" width="80%" style="margin-left:10%" xmlns="http://www.w3.org/2000/svg" font-family="TeX Gyre Termes" font-size="11">
<defs><marker id="m" markerWidth="6" markerHeight="6" refX="5.5" refY="3" orient="auto" markerUnits="userSpaceOnUse"><path d="M0,0 L6,3 L0,6 z" fill="#000"/></marker>
<marker id="n" markerWidth="6" markerHeight="6" refX="0.5" refY="3" orient="auto" markerUnits="userSpaceOnUse"><path d="M6,0 L0,3 L6,6 z" fill="#000"/></marker></defs>
<rect x="8" y="30" width="86" height="194" fill="#fff" stroke="#000" stroke-width="1.4"/>
<text x="51" y="22" text-anchor="middle" font-weight="bold">TESTOOL (20P)</text>
<rect x="258" y="30" width="94" height="194" fill="#fff" stroke="#000" stroke-width="1.4"/>
<text x="305" y="22" text-anchor="middle" font-weight="bold">28P SOCKET</text>
<g>
<text x="16" y="52">PA0–PA6</text><text x="266" y="52">A0–A6</text><path d="M94,48 L258,48" fill="none" stroke="#000" marker-end="url(#m)"/>
<text x="16" y="72">PB0–PB7</text><text x="266" y="72">D0–D7</text><path d="M94,68 L258,68" fill="none" stroke="#000" marker-end="url(#m)" marker-start="url(#n)"/>
<text x="16" y="92">PC1</text><text x="266" y="92">OE (22)</text><path d="M94,88 L258,88" fill="none" stroke="#000" marker-end="url(#m)"/>
<text x="16" y="112">PC2</text><text x="266" y="112">WE (27)</text><path d="M94,108 L258,108" fill="none" stroke="#000" marker-end="url(#m)"/>
<text x="16" y="132">20: VCC</text><text x="266" y="132">VCC, CE2</text><path d="M94,128 L258,128" fill="none" stroke="#000"/>
<text x="16" y="152">10: GND</text><text x="266" y="152">GND, CE1</text><path d="M94,148 L258,148" fill="none" stroke="#000"/>
<text x="16" y="200">PC0</text><text x="266" y="200">A7–A12</text>
</g>
<circle cx="118" cy="68" r="2.2"/>
<path d="M118,68 L118,180 L140,180" fill="none" stroke="#000" marker-end="url(#m)"/>
<path d="M94,196 L140,196" fill="none" stroke="#000" marker-end="url(#m)"/>
<rect x="140" y="166" width="76" height="46" fill="#fff" stroke="#000" stroke-width="1.4"/>
<text x="178" y="161" text-anchor="middle" font-weight="bold">74HC574</text>
<text x="145" y="184" font-size="9.5">D0–D5</text><text x="145" y="200" font-size="9.5">CLK</text>
<text x="211" y="192" font-size="9.5" text-anchor="end">Q0–Q5</text>
<path d="M216,188 L238,188 L238,196 L258,196" fill="none" stroke="#000" marker-end="url(#m)"/>
</svg>'''

NET = [('3–9 (PA0–PA6)', 'socket 10, 9, 8, 7, 6, 5, 4 (A0–A6)'),
       ('11–18 (PB0–PB7)', 'socket 11, 12, 13, 15, 16, 17, 18, 19 (D0–D7); PB0–PB5 also to 574 pins 2–7 (D0–D5)'),
       ('1 (PC0)', '574 pin 11 (CLK)'), ('2 (PC1)', 'socket 22 (OE)'), ('19 (PC2)', 'socket 27 (WE) and J1 “6116”'),
       ('20 (VCC)', 'socket 28 and 26 (CE2), 574 pin 20'), ('10 (GND)', 'socket 14 and 20 (CE1), 574 pins 1, 8, 9, 10'),
       ('574 Q0–Q5', 'socket 3 (A7), 25 (A8), 24 (A9), 21 (A10), J1 “6264” (A11), 2 (A12)'),
       ('J1 common', 'socket 23 (A11 on the 6264, WE on the 6116)')]
NETROWS = ''.join(f'<tr><td>{a}</td><td>{b}</td></tr>' for a, b in NET)

CSS = f"""
@page {{ size: A5; margin: 15mm 14mm 14mm 14mm;
  @bottom-center {{ content: "– " counter(page) " –"; font: 8.5pt {SERIF} }} }}
@page cover {{ @bottom-center {{ content: none }} }}
@page wide {{ margin: 10mm 8mm 10mm 8mm }}
body {{ font-family: {SERIF}; font-size: 9.6pt; line-height: 1.32; color: #000; text-align: justify; hyphens: auto }}
h1 {{ text-align: left; font-family: {TITLE}; font-weight: normal; font-size: 15pt; letter-spacing: 1.2pt; margin: 2pt 0 8pt }}
h2 {{ font-family: {SERIF}; font-weight: bold; font-size: 10pt; margin: 9pt 0 4pt; letter-spacing: .3pt }}
h3 {{ font-family: {SANS}; font-weight: normal; font-size: 9.3pt; letter-spacing: .5pt; margin: 9pt 0 4pt }}
h3 b {{ margin-right: 4pt }}
.page {{ page-break-before: always }}
.cover {{ page: cover; padding-top: 52mm }}
.cover .t {{ display:flex; align-items:flex-end; justify-content:center; gap: 3mm }}
.cover .tc {{ font-family:{SERIF}; font-size: 30pt; letter-spacing: 1pt; padding-bottom: 1mm }}
.cover .ap {{ text-align:center; font-family:{SERIF}; font-weight:bold; font-size: 21pt; margin-top: 9mm }}
.cover .v2 {{ text-align:center; font-family:{SERIF}; font-style: italic; font-size: 9.5pt; margin-top: 62mm; color:#222 }}
table.ics {{ border-collapse: collapse; width: 100%; font-family: {SANS}; font-size: 7.6pt; margin: 1pt 0 4pt 3mm }}
table.ics td {{ padding: 0 2pt; line-height: 1.22 }}
.crt {{ page-break-inside: avoid; margin: 3pt auto 5pt; border: 1.4pt solid #000; border-radius: 16pt 16pt 22pt 22pt / 12pt 12pt 16pt 16pt;
  padding: 6pt 10pt 7pt; font-family: {SERIF}; font-weight: bold; font-size: 8pt; line-height: 1.22 }}
.crt .c {{ text-align: center }} .crt .l {{ padding-left: 12mm }} .crt .sp {{ height: 5pt }}
.crt .icbox {{ width: 34mm; margin: 3pt auto 4pt; border: 2.2pt dotted #000; padding: 5pt 0; text-align:center }}
.red {{ color: #d00000; font-family: {SANS}; font-weight: normal }}
.redn {{ color: #d00000; font-family: {SANS}; font-size: 8.4pt; text-decoration: underline }}
table.keys {{ border-collapse: collapse; font-size: 9.1pt; line-height: 1.25 }} table.keys td {{ padding: 0 0 2pt 0; vertical-align: top }}
table.keys td.b {{ width: 3mm }} table.keys td.k {{ white-space: nowrap; padding-right: 4pt }}
ol {{ padding-left: 5mm }} ol li {{ margin-bottom: 6pt; padding-left: 1mm }}
.center {{ text-align: center }}
.ed {{ border: 0.6pt solid #000; padding: 4pt 6pt; font-size: 8.6pt; margin: 4pt 0 6pt }}
table.t {{ border-collapse: collapse; width: 100%; font-size: 8.4pt; margin: 3pt 0 6pt }}
table.t td, table.t th {{ border: 0.6pt solid #000; padding: 1.5pt 4pt; vertical-align: top; text-align: left }}
table.t th {{ font-family: {SANS}; font-weight: normal; font-size: 8pt; letter-spacing:.3pt }}
.small {{ font-size: 8.4pt }}
.pair {{ display:flex; justify-content: space-between }}
img.photo {{ border: 0.5pt solid #000 }}
"""

def keys(rows):
    h = '<table class="keys">'
    for b, k, t in rows:
        h += f'<tr><td class="b">{"•" if b else ""}</td><td class="k">{k}</td><td>{t}</td></tr>'
    return h + '</table>'

A, B, C = ADDED['A'], ADDED['B'], ADDED['C']

html = f"""<html><head><meta charset="utf-8"><style>{CSS}</style></head><body>

<div class="cover">
<div class="t">{COVER_IC}<div class="tc">TEST CARD</div></div>
<div class="ap">for the Apple ][ series</div>
<div class="v2">Version 2.0 Expanded — Tabajara Labs, 2026</div>
</div>

<div class="page">
<h1>PREFACE :</h1>
<p>&nbsp;&nbsp;Nowadays, we use IC frequently because our technology is invented and developed rapidly. Every technician has some ICs in hand, but he does not know exactly whether those ICs are good or fail. He has to take much time to inspect and verify them by IC TESTER. For IC TESTER is expensive and costs much time for testing, we have designed and developed this easy-operation and low-price equipment called IC TEST CARD.</p>
<p>This interface card is plugged on #1 — #7 slot of APPLE II which is served as main board, and connected with Testool which holds the IC being tested. Then just insert the Diskette (software of IC TEST CARD) to floppy disk drive. The result will be showed on display within few milliseconds.</p>
<h1 style="margin-top:14pt">( I ). SYSTEM DIAGRAM</h1>
<div style="width:96%;margin:6pt auto 0">{SYS_DIAG}</div>
</div>

<div class="page">
<h1>( II ). FUNCTIONS :</h1>
<h2>A. OPERATING DISPLAY :</h2>
{SCR_ORIG}
{keys([
 (1, 'Press &nbsp;CTRL &nbsp;S :', 'Searching number of IC being tested on Testool, and showing “138 OVER”, “241 OVER”, …… If IC being tested is fail or not in category of IC tested, then it shows “OVER”.'),
 (1, 'Press &nbsp;CTRL &nbsp;C :', 'KEY IN number of IC being tested: 74S04, 74H123, 74LS74, 7486 … <span class="redn">(* =&gt; if IC has only 2 numbers, add a pre-leading 0 !</span>'),
 (1, 'Press &nbsp;SPACE &nbsp;:', 'Start testing'), ])}
<table class="keys"><tr><td class="b">•</td><td>If testing OK, it shows “TEST OK” and generate “BI————” a long sound which means this IC good.</td></tr>
<tr><td class="b">•</td><td>If testing error, it shows “TEST ERROR” and generate “BI, BI, BI, BI, BI” 5 short sounds which means this IC fail.</td></tr>
<tr><td class="b">•</td><td>If IC number input is wrong, it shows “THIS NUMBER IS NOT AVAILABLE”.</td></tr></table>
{keys([(1, 'Press &nbsp;CTRL &nbsp;L :', 'Testing the IC being tested on Testool continuously. If this IC is aged or unstable, it shows “LEVEL ERROR”, otherwise it shows “TEST OK”.')])}
<p style="margin:4pt 0 2pt">B. Being able to test OPEN–COLLECTOR, TRI–STATE …… etc. TTL.</p>
<p style="margin:2pt 0">C. Containing protection design of IC's short circuit. If putting IC being tested on Testool inversely or short circuit of IC itself, it does not damage the TEST CARD and shows “LEVEL ERROR, POWER LOW”.</p>
<p style="margin:2pt 0">D. All input and output level of IC being tested can be tested completely. The High–Low Level of IC being tested can be set up or adjusted.</p>
<table style="margin:4pt 0 0 30mm;font-size:9.4pt"><tr><td rowspan="2">It's range is :&nbsp;</td><td style="border-left:1pt solid #000;padding-left:4pt">High : 2.4V – 4.5V</td></tr>
<tr><td style="border-left:1pt solid #000;padding-left:4pt">Low &nbsp;: 0.4V – 1.0V</td></tr></table>
</div>

<div class="page">
<h1>( III ). OPERATION</h1>
<ol>
<li>This IC TEST CARD can be plugged on any slot optionally. Please be noted which slot the card plugged. When display shows
<div class="center" style="font-weight:bold;margin:5pt 0 2pt">CARD IN WHICH SLOT?</div>
<div class="center" style="font-weight:bold;margin-bottom:4pt">(1, 2, 3, 4, 5, 6, 7)?</div>
Just press the number of slot which IC TEST CARD is on on keyboard.</li>
<li>The software of this IC TEST CARD is based on ASCII code of APPLESOFT. If printer is on, the IC TEST CARD is off.</li>
<li>The level tested can be adjusted. If the ICs being tested are various brands and can not be tested by the level defaulted, the level can be adjusted by user as follows:
<div class="center" style="margin:8pt 0 6pt">{VR_DIAG}</div>
VR1 for HIGH LEVEL, range: 2.4V ~ 4.5V default: 2.6V<br>
VR2 for LOW LEVEL, range: 0.3V ~ 1.2V default: 0.8V<br>
It can be checked by MULTI-FUNCTION METER, OSCILLOSCOPE METER …. etc. The right way is to check the voltage of P1 or P2 to ground.</li>
<li>All right of this manual and software are reserved by YIH LUNG ENTERPRISE CO., LTD.. If the damage of software diskette was caused by user's modification, we do not offer the new diskette or any service. Please keep the diskette with the serial number on it in order to ask to change the diskette of new software and more service the day after.</li>
</ol>
</div>

<div class="page">
<h1>( IV ). LIST OF IC TESTED :</h1>
<h2 style="font-family:{TITLE};font-weight:normal;font-size:11pt;letter-spacing:1pt">FLOPPY DISK I ( TTL )</h2>
<h3><b>A.</b> STANDARD TTL ( 54/7400 SERIES )</h3>{grid(TTL_STD)}
<h3><b>B.</b> LOW POWER SCHOTTKY TTL (54/74LS SERIES)</h3>{grid(pre(LS, '74LS'))}
<h3><b>C.</b> SCHOTTKY-CLAMPED TTL (54/74S SERIES)</h3>{grid(pre(S, '74S'))}
<h3><b>D.</b> LOW POWER TTL (54/74L SERIES)</h3>{grid(pre(L, '74L'))}
<h3><b>E.</b> HIGH-SPEED TTL (54/74H SERIES)</h3>{grid(pre(H, '74H'))}
<h3><b>F.</b> RANDOM-ACCESS MEMORY ( 54/74 SERIES )</h3>{grid(RAM)}
<h2 class="page" style="font-family:{TITLE};font-weight:normal;font-size:11pt;letter-spacing:1pt">FLOPPY DISKS II ( CMOS )</h2>
<h3><b>A.</b> TTL EQUIVALENT CMOS DEVICE (54/74HC SERIES)</h3>{grid(pre(HC, '74HC'))}
<h3><b>B.</b> CD 45/4000 SERIES (OR MC 145/140 SERIES) CMOS DEVICES</h3>{grid(pre(CD, 'CD'))}
<h3><b>C.</b> MEMORY</h3>{grid(MEM)}
</div>

<div class="page">
<h2 style="margin-top:0">ATTENTION:</h2>
<p style="margin:0 0 3pt">We have added CMOS IC to the diskette as follows:</p>
<h3 style="margin-top:3pt">CD 4000 / 4500</h3>{grid(ADD_CD, 9)}
<h3>74HC</h3>{grid(ADD_HC, 9)}
<p>Due to adding new items, we have our program in the diskette changed as follows:<br>
When you run the program, it will show:</p>
<table class="keys" style="margin-left:2mm">
<tr><td class="k">PICTURE 1 :</td><td>OUR MARKS.</td></tr>
<tr><td class="k">PICTURE 2 :</td><td>RIGHT LOCATION OF IC PINS.</td></tr>
<tr><td class="k">PICTURE 3 :</td><td>A. TTL 54/74 SERIES<br>B. CMOS 40/45 SERIES<br>C. HCMOS 74HC SERIES<br>WHICH ONE? A, B OR C?<br>※ After selecting, press “RETURN”, then it will show:</td></tr>
<tr><td class="k">PICTURE 4 :</td><td>OUR MARK &amp; WAITING.</td></tr>
<tr><td class="k">PICTURE 5 :</td><td>CARD IN WHICH SLOT?<br>(1, 2, 3, 4, 5, 6 or 7)?<br>※ After selecting, it will show “OPERATING DISPLAY PICTURE” as in the manual.</td></tr>
</table>
<p>Press “CTRL” “C”<br>
If you select A, then Press: 74– &nbsp;or 74–S– &nbsp;or 74–LS–<br>
If you select B, then Press: CD–40– &nbsp;or CD–45–<br>
If you select C, then press: 74–HC–<br>
Other operation is the same as the manual.</p>
</div>

<div class="page">
<h1>( V ). VERSION 2.0 EXPANDED</h1>
<div class="ed">Section (V) of the original manual was not preserved (the surviving copy goes from (IV) to (VI)).
This section is new: it describes the Version 2.0 Expanded program by Tabajara Labs (2026), which runs from
ProDOS (hard disk, CompactFlash, BOOTI …) on an Apple II with 64K, keeps the whole original program and
adds new ICs and the memory test announced in the original list.</div>
<h2>A. STARTING THE PROGRAM :</h2>
<p>Run <b>ICTESTER.SYSTEM</b> from ProDOS (it can be the startup program of the volume). It shows PICTURE 3 with one more line:</p>
{SCR_MENU}
<p>Press A, B or C without RETURN. The program asks “CARD IN WHICH SLOT?” as before and shows the operating display.
D starts the memory test (see E). Q returns to ProDOS. RESET always returns to this picture.</p>
</div>
<div class="page">
<h2 style="margin-top:0">B. OPERATING DISPLAY :</h2>
{SCR_V2}
<p>The number of ICs available is shown for the series selected: <b>A = 195</b>, <b>B = 94</b>, <b>C = 159</b>.
The operation is the same as the manual: CTRL-C, the IC number, SPACE; CTRL-S also finds the new ICs; CTRL-L as before.</p>
</div>

<div class="page">
<h2 style="margin-top:0">C. LIST OF IC ADDED :</h2>
<p class="small" style="margin-top:0">These ICs are tested with test patterns added to the program. Key them in exactly like the original ones (CTRL-C, prefix, number, SPACE).</p>
<h3><b>A.</b> TTL 54/74 SERIES ( {len(A)} TYPES )</h3>{grid(A)}
<p class="small">In series A the added types are accepted with any prefix: 74–, 74–LS–, 74–S–, 74–L–, 74–H– … Prefixes that the original program refuses (74F, 74ALS, 74AS …) are now tested by the number with the same patterns: 74F00 is tested as 7400.</p>
<h3><b>B.</b> CMOS 40/45 SERIES ( {len(B)} TYPES )</h3>{grid(pre(B, 'CD'))}
<h3><b>C.</b> HCMOS 74HC SERIES ( {len(C)} TYPES )</h3>{grid(pre(C, '74HC'))}
<h3><b>D.</b> MEMORY ( OPTION D )</h3>{grid(['2114', '2147', '4164', '41256', '4416', '4464', '6116 *', '6264 *'], 8)}
<p class="small">* with the memory adapter (see F).</p>
<p class="small">Total of types: series A 158 + 37 = 195; series B 68 + 26 = 94; series C 49 + 110 = 159; memory 8.</p>
</div>

<div class="page">
<h2 style="margin-top:0">E. MEMORY TEST ( OPTION D ) :</h2>
<p>The MEMORY option of the list (IV) is now available. Press D in PICTURE 3 and key in the slot of the card. The display shows:</p>
{SCR_MEM}
<ol>
<li>Select the memory (1 – 8). The display draws the Testool with the position of every pin of the memory, the notch and the jumper. <b>Put the memory as shown before pressing SPACE</b>: the power is applied only after SPACE.</li>
<li>Press SPACE. The display shows the step being tested (1/3, 2/3, 3/3) and the address or row. ESC returns to the list.</li>
<li>A good memory shows “TEST OK !” (BI———— long sound). A bad memory shows “TEST ERROR END, STEP n”, the address (or ROW and COL) and the data EXPected and GOT (BI, BI, BI, BI, BI). “BAD ADDR BIT n” means an address line open or shorted. The different bits of EXP and GOT show the bad data pin (bit 0 = I/O1, DQ1, D0).</li>
</ol>
</div>
<div class="page">
<h2 style="margin-top:0">MEMORIES TESTED :</h2>
<table class="t"><tr><th>MEMORY</th><th>TYPE</th><th>ON THE TESTOOL</th><th>TIME</th></tr>
<tr><td>2114</td><td>SRAM 1K×4</td><td>normal, jumper 19–20</td><td>4 s</td></tr>
<tr><td>2147</td><td>SRAM 4K×1</td><td>normal, jumper 19–20</td><td>12 s</td></tr>
<tr><td>4164</td><td>DRAM 64K×1</td><td>reversed</td><td>1 min 40 s</td></tr>
<tr><td>41256</td><td>DRAM 256K×1</td><td>reversed</td><td>7 min</td></tr>
<tr><td>4416</td><td>DRAM 16K×4</td><td>reversed, jumper 19–20</td><td>40 s</td></tr>
<tr><td>4464</td><td>DRAM 64K×4</td><td>reversed, jumper 19–20</td><td>2 min 25 s</td></tr>
<tr><td>6116 / 6264</td><td>SRAM 2K×8 / 8K×8</td><td>adapter</td><td>6 s / 22 s</td></tr></table>
<p class="small"><b>Reversed</b> = turned 180°, notch down, pushed to the bottom (GND row). The jumper is a short wire between
positions 19 and 20 of the Testool (position 20 is the fixed VCC). The test writes and reads a checkerboard pattern and its
inverse in all cells, then checks every address line. The dynamic RAMs are tested row by row (the access refreshes the row).
Times at 1 MHz. 4116, 4027, 2102 and 2125 can not be tested (other power supplies or pins).</p>
</div>

<div class="page">
<h2 style="margin-top:0">POSITION OF THE MEMORY ON THE TESTOOL :</h2>
<p class="small" style="margin-top:0">Top view, as drawn on the display. Black = used position; pin number and name beside it; the position number outside.</p>
<div class="pair">{PLACE1}</div>
<div class="pair" style="margin-top:4pt">{PLACE2}</div>
</div>

<div class="page">
<h2 style="margin-top:0">F. MEMORY ADAPTER ( 6116 / 6264 ) :</h2>
<p>The Testool has 20 positions and the 6264 needs 23 signals. The adapter has a 20-pin plug for the Testool, a 28-pin
socket for the memory and a 74HC574 which keeps the high address lines A7–A12. PB0–PB7 carry the data and, when PC0
clocks the 74HC574, the high address. Power: VCC from position 20, GND from position 10 (100 nF beside each IC).</p>
{ADP}
<table class="t"><tr><th>TESTOOL POSITION</th><th>TO</th></tr>{NETROWS}</table>
<p class="small">The 6116 is put pushed to the bottom of the 28-pin socket (pin 1 of the 6116 on pin 3 of the socket). Jumper J1:
“6264” = socket pin 23 to Q4 (A11); “6116” = socket pin 23 to PC2 (WE). Use a 74HC574 or 74HCT574.</p>
</div>

<div class="page" style="page: wide">
<h1>( VI ). FLOW DIAGRAM OF TESTING OPERATION :</h1>
{FLOW}
</div>

<div class="page">
<h1>APPENDIX</h1>
<div class="ed">Not part of the original manual. Added in this restored edition (Tabajara Labs, 2026).</div>
<h2>THE IC TEST CARD AND THE TESTOOL</h2>
<img class="photo" style="width:80%;margin-left:10%" src="img/card_front.jpg">
<p class="small center">Original version, with the black “IC TEST” label. Photo: AppleBox / J.E.H. Walsh (applefritter.com).</p>
<img class="photo" style="width:80%;margin-left:10%" src="img/card_and_socket.jpg">
<p class="small center">Alternative version (all components exposed: 3 × MC6821, CD4066, comparators, VR1/VR2) and the Testool. Photo: AppleBox / J.E.H. Walsh.</p>
</div>

<div class="page">
<h2 style="margin-top:0">NOTES ON THIS EDITION</h2>
<ul class="small">
<li>Pages (I)–(IV), ATTENTION and (VI) restore the 1984 manual (A5 sheets) from the 9 pages scanned by AppleBox, with the same text and layout; obvious spelling errors were corrected (“casued”, “catagory”, “ociloscope”).</li>
<li>The red note “if IC has only 2 numbers, add a pre-leading 0” is written in the surviving copy, as here.</li>
<li>Section (V) was not preserved; the number was used for the Version 2.0 information.</li>
<li>Section (II)-D gives Low 0.4–1.0 V and section (III)-3 gives 0.3–1.2 V; both kept as printed.</li>
<li>The lists (IV) and ATTENTION are what the manufacturer announced. The diskette studied (TEST.2, CMOS.2, HMOS.2) implements 158 TTL, 68 CMOS 40/45 and 49 74HC types; section (V)-C lists only what Version 2.0 adds to it, and the totals shown on the display.</li>
<li>The added test patterns come from the device libraries of the Elnec programmer software (74 TTL, 74HC and 4000), converted for this card. Library entries that can not be keyed in on the card (4063B, 4311, 744538, 7440102, 8097, 8098) are not listed and not counted.</li>
<li>Version 2.0 also removes the old copy protections, which stopped the program from working outside the original diskette; the manufacturer's copyright is kept on every display.</li>
</ul>
</div>
</body></html>"""

out = HERE / 'Fairy_IC_Test_Card_Manual_v3.pdf'
weasyprint.HTML(string=html, base_url=str(HERE)).write_pdf(out)
print(out)
