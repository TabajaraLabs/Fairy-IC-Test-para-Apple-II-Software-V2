#!/usr/bin/env python3
"""Gera o manual modernizado do Fairy IC Test Card (PDF) a partir da transcrição."""
import sys, weasyprint, pathlib

VER = sys.argv[1] if len(sys.argv) > 1 else 'v1'
HERE = pathlib.Path(__file__).parent

def grid(items, cols=7):
    rows = [items[i:i+cols] for i in range(0, len(items), cols)]
    h = '<table class="ics">'
    for r in rows:
        h += '<tr>' + ''.join(f'<td>{x}</td>' for x in r) + '<td></td>' * (cols - len(r)) + '</tr>'
    return h + '</table>'

TTL_STD = """7400 7401 7402 7403 7404 7405 7406 7407 7408 7409 7410 7411 7412 7413 7414 7415
7416(7406) 7417(7407) 7420 7421 7425 7427 7428 7430 7432 7437 7438 7442 7445 7447 7448 7449 7473
7474 7475 7476 7483 7485 7486 7490 7492 7493 7495 7496 74107 74109 74125 74126 74132 74136 74139
74145 74147 74148 74151 74153 74155 74156 74157 74158 74160 74161 74162 74163 74164 74165 74166
74170 74173 74174 74175 74190 74191 74193 74194 74195 74197 74247 74248 74251 74257 74259 74266
74276 74279 74283 74365 74366 74367 74368 74393 74490""".split()
LS = """00 01 02 03 04 05 08 09 10 11 12 13 14 15 20 21 27 28 30 32 37 38 42 47 51 55 73 74 75 76 83 85
86 90 92 93 95 96 107 109 112 113 125 126 132 133 136 138 139 145 147 148 151 153 155 156 157 158
160 161 162 163 164 165 166 170 173 174 175 183 189 190 191 192 193 194 195 197 240 241 242 243
244 245 247 248 251 253 257 258 259 261 266 273 279 280 283 295 298 323 324 348 352 365 366 367
368 373 374 375 377 378 380 390 393 399 490 642 643 669 670""".split()
S = """00 03 04 05 08 09 10 11 15 20 30 32 37 38 51 55 74 85 86 107 112 113 132 133 135 138 139 151 153
157 158 160 161 162 163 174 175 194 195 197 240 241 251 257 258 260 280 283 299 373 374""".split()
L = """00 02 03 04 05 08 10 20 30 32 42 47 51 55 73 74 75 85 86 90 93 95 96 151 153 157 164 165 192 193""".split()
H = """00 01 04 05 10 11 15 20 30 51 55 73 74 76 183""".split()
RAM = "7489 74S89 74S189 74S201 74S287 74S288 74S289 74S471 74S472".split()
HC = """00 02 04 08 10 14 20 30 32 42 48 73 74 76 83 85 86 89 90 91 93 95 107 138 139 150 151 154 157
158 160 161 162 163 164 165 173 174 175 192 193 194 195 200 221 240 241 244 257 373 374 533 534""".split()
CD = """4000 4001 4002 4006 4007 4008 4009 4010 4011 4012 4013 4014 4015 4016 4017 4018 4019 4020 4021
4022 4023 4024 4025 4027 4028 4029 4030 4032 4035 4036 4038 4039 4040 4041 4042 4043 4044 4047 4049
4050 4051 4052 4053 4054 4055 4056 4060 4063 4066 4068 4069 4070 4071 4072 4073 4075 4076 4077 4078
4081 4082 4085 4086 4093 4094 4098 4099 40102 40103 40104 40106 40107 40160 40161 40162 40163 40174
40175 40182 40192 40193 40194 40195 40257 4501 4502 4503 4506 4508 4510 4511 4512 4514 4515 4516
4518 4519 4520 4521 4522 4526 4527 4528 4530 4531 4532 4538 4539 4543 4544 4547 4549 4551 4553 4554
4555 4556 4557 4558 4559 4560 4561 4562 4566 4569 4572 4582 4583 4585 4702 4732""".split()
MEM = "4164 2114 2125 2511 82S16 8216 8T26 8T28".split()
ADD_CD = """4000 4001 4002 4006 4008 4009 4010 4011 4012 4013 4014 4015 4016 4017 4020 4022 4023 4025 4027
4028 4030 4035 4040 4041 4042 4043 4044 4049 4051 4052 4053 4066 4068 4069 4071 4072 4073 4075 4076
4077 4078 4081 4082 4093 4099 40106 40107 40160 40161 40162 40163 40174 40175 40192 40193 40194 40195
40257 4501 4502 4503 4510 4511 4512 4516 4518 4519 4520 4532 4555 4556 4572""".split()
ADD_HC = """00 02 04 08 10 14 20 30 32 42 48 73 74 76 83 85 86 90 91 93 95 107 138 139 151 157 158 160 162
163 164 165 173 174 175 192 193 194 195 240 241 244 373 374 257 533 534""".split()

LOGO = """<svg viewBox="0 0 200 200" width="{w}" height="{w}" xmlns="http://www.w3.org/2000/svg">
<polygon points="14,4 186,4 196,14 196,186 186,196 14,196 4,186 4,14" fill="none" stroke="#000" stroke-width="9"/>
<polygon points="4,4 26,4 4,26" fill="#000"/><polygon points="196,4 174,4 196,26" fill="#000"/>
<polygon points="4,196 26,196 4,174" fill="#000"/><polygon points="196,196 174,196 196,174" fill="#000"/>
<polygon points="100,22 182,72 100,122 18,72" fill="none" stroke="#000" stroke-width="5"/>
<line x1="128" y1="36" x2="156" y2="53" stroke="#000" stroke-width="9"/>
<line x1="44" y1="91" x2="72" y2="108" stroke="#000" stroke-width="9"/>
<text x="100" y="86" text-anchor="middle" font-family="Noto Serif CJK TC, Noto Serif CJK SC" font-weight="bold" font-size="38">毅能</text>
<text x="100" y="178" text-anchor="middle" font-family="DejaVu Sans" font-weight="bold" font-size="44">FAIRY</text>
</svg>"""

SYS_DIAG = """<svg viewBox="0 0 560 330" width="100%" xmlns="http://www.w3.org/2000/svg" font-family="DejaVu Sans" font-size="13">
<defs><marker id="a" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z"/></marker></defs>
<rect x="20" y="10" width="345" height="310" fill="none" stroke="#555" stroke-dasharray="7,5" stroke-width="1.5"/>
<rect x="45" y="45" width="150" height="85" fill="#f3f6fa" stroke="#000" stroke-width="1.5"/>
<text x="120" y="82" text-anchor="middle" font-weight="bold">APPLE II</text>
<text x="120" y="102" text-anchor="middle" font-size="11">(MAIN BOARD)</text>
<rect x="240" y="55" width="105" height="60" fill="#f3f6fa" stroke="#000" stroke-width="1.5"/>
<text x="292" y="80" text-anchor="middle" font-weight="bold">IC TEST</text>
<text x="292" y="98" text-anchor="middle" font-weight="bold">CARD</text>
<path d="M200,85 L235,85" stroke="#000" stroke-width="2" marker-end="url(#a)" marker-start="url(#a)"/>
<path d="M345,85 L440,85" stroke="#000" stroke-width="5"/>
<path d="M345,85 L440,85" stroke="#fff" stroke-width="2"/>
<rect x="440" y="50" width="90" height="75" fill="#f3f6fa" stroke="#000" stroke-width="1.5"/>
<rect x="470" y="65" width="28" height="45" fill="#fff" stroke="#000"/>
<text x="485" y="148" text-anchor="middle" font-weight="bold">TESTOOL</text>
<text x="485" y="164" text-anchor="middle" font-size="10">(ZIF socket)</text>
<path d="M120,215 L120,138" stroke="#000" stroke-width="2" marker-end="url(#a)"/>
<rect x="75" y="220" width="90" height="80" fill="#f3f6fa" stroke="#000" stroke-width="1.5"/>
<circle cx="120" cy="250" r="9" fill="none" stroke="#000"/><rect x="113" y="265" width="14" height="30" rx="7" fill="none" stroke="#000"/>
<text x="180" y="265" font-weight="bold">DISKETTE</text>
</svg>"""

VR_DIAG = """<svg viewBox="0 0 300 140" width="300" xmlns="http://www.w3.org/2000/svg" font-family="DejaVu Sans" font-size="13">
<path d="M40,30 L250,30 L250,100 L190,100 L190,112 L95,112 L95,100 L40,100 Z" fill="#f3f6fa" stroke="#000" stroke-width="1.5"/>
<text x="46" y="20" font-weight="bold">VR1</text><text x="88" y="20" font-weight="bold">VR2</text>
<circle cx="58" cy="48" r="11" fill="#fff" stroke="#000" stroke-width="1.5"/><line x1="51" y1="48" x2="65" y2="48" stroke="#000" stroke-width="2"/>
<circle cx="100" cy="48" r="11" fill="#fff" stroke="#000" stroke-width="1.5"/><line x1="93" y1="48" x2="107" y2="48" stroke="#000" stroke-width="2"/>
<circle cx="58" cy="66" r="2.5"/><circle cx="114" cy="48" r="2.5"/>
<path d="M58,92 L58,72" stroke="#000" stroke-width="1.5"/><path d="M54,78 L58,70 L62,78" fill="#000"/>
<text x="52" y="107" font-weight="bold">P1</text>
<path d="M140,48 L120,48" stroke="#000" stroke-width="1.5"/><path d="M126,44 L118,48 L126,52" fill="#000"/>
<text x="145" y="53" font-weight="bold">P2</text>
<text x="215" y="127" text-anchor="middle" font-size="10">(edge connector)</text>
</svg>"""

def box(x, y, w, h, lines, bold=False, fs=11.5):
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#fff" stroke="#000" stroke-width="1.4"/>'
    for i, t in enumerate(lines):
        s += f'<text x="{x+8}" y="{y+17+i*15}" font-size="{fs}" {"font-weight=\"bold\"" if bold else ""}>{t}</text>'
    return s

def arrow(x1, y1, x2, y2):
    return f'<path d="M{x1},{y1} L{x2},{y2}" stroke="#000" stroke-width="1.4" marker-end="url(#ar)"/>'

FLOW = '<svg viewBox="0 0 640 752" width="100%" xmlns="http://www.w3.org/2000/svg" font-family="DejaVu Sans">' \
    '<defs><marker id="ar" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z"/></marker></defs>'
FLOW += box(210, 10, 260, 72, ["a. Open the cover of the APPLE II and plug", "   the IC TEST CARD into slot #1 – #7.",
                               "b. Insert the testing program diskette into", "   the floppy disk drive."])
FLOW += arrow(340, 82, 340, 108)
FLOW += box(210, 110, 260, 44, ["Turn on the power of the APPLE II.", "The display shows the testing picture."])
FLOW += f'<path d="M340,154 L340,200" stroke="#000" stroke-width="1.4"/>' + arrow(340, 170, 478, 170)
FLOW += '<text x="380" y="164" font-size="10">PICTURE WRONG</text>'
FLOW += box(480, 140, 150, 88, ["a. Turn off the power.", "b. Check that the TEST", "   CARD is plugged in", "   correctly and the disk-", "   ette inserted rightly."], fs=10.5)
FLOW += arrow(340, 200, 340, 214)
FLOW += box(210, 216, 260, 104, ["a. Put the IC to be tested on the Testool.", "b. Press CTRL-C.", "c. The cursor must be on the first position",
                                 "   of the IC NO. field.", "d. Key in the number of the IC to be tested.", "e. Press SPACE."])
FLOW += f'<path d="M340,320 L340,380" stroke="#000" stroke-width="1.4"/>'
FLOW += arrow(340, 345, 150, 345) + '<text x="200" y="338" font-size="9.5">IC PUT INVERSELY</text><text x="196" y="360" font-size="9.5">OR SHORT CIRCUIT</text>'
FLOW += box(10, 322, 138, 46, ['Display shows "LEVEL', 'ERROR, POWER LOW".'], fs=10.5)
FLOW += arrow(340, 345, 478, 345) + '<text x="358" y="338" font-size="9.5">IC NUMBER WRONG</text>'
FLOW += box(480, 300, 150, 92, ['a. Display shows "THIS', '   NUMBER IS NOT', '   AVAILABLE".', 'b. Cursor jumps to the', '   first position again.'], fs=10.5)
FLOW += arrow(555, 228, 555, 298)
FLOW += arrow(340, 380, 340, 394)
FLOW += box(210, 396, 260, 210, ['a. Shows the result: a good IC gives', '   "TEST OK" (BEEEP, one long sound);', '   a failed IC gives "TEST ERROR"',
                                 '   (BI, BI, BI, BI, BI: five short sounds).', 'b. To test more ICs of the same type,',
                                 '   just take out the tested IC, put the', '   new one on the Testool and press SPACE.',
                                 'c. To test a different IC type, take out', '   the tested IC, put the new one on the',
                                 '   Testool, press CTRL-C and key in the', '   new IC number.'])
FLOW += box(480, 430, 150, 74, ['a. Testing an IC with no', '   number printed: put it', '   on the Testool.', 'b. Press CTRL-S.'], fs=10.5)
FLOW += arrow(555, 392, 555, 428)
FLOW += arrow(555, 504, 555, 556)
FLOW += box(480, 558, 150, 104, ['a. Display shows', '   "(IC NUMBER) OVER".', 'b. If the IC is bad or', '   not in the tested', '   category, the display', '   shows "OVER".'], fs=10.5)
FLOW += f'<path d="M340,606 L340,660" stroke="#000" stroke-width="1.4"/>'
FLOW += arrow(340, 640, 150, 640) + '<text x="178" y="633" font-size="9.5">IC AGED OR UNSTABLE</text>'
FLOW += box(10, 600, 138, 140, ['a. To test an unstable', '   or aged IC, press', '   CTRL-L after putting', '   it on the Testool.', 'b. A weak IC shows', '   "LEVEL ERROR".', 'c. A good IC shows', '   "TEST OK".'], fs=10.5)
FLOW += arrow(340, 660, 340, 674)
FLOW += box(210, 676, 260, 70, ['a. Test completed: turn off the power', '   of the computer first.', 'b. Take out the diskette and pull out', '   the Test Card.'])
FLOW += '</svg>'

def socket_svg():
    s = '<svg viewBox="0 0 520 330" width="100%" xmlns="http://www.w3.org/2000/svg" font-family="DejaVu Sans" font-size="11">'
    x0, y0, dy = 150, 30, 26
    s += f'<rect x="{x0}" y="{y0-18}" width="110" height="{dy*10+20}" rx="6" fill="#e9f3ee" stroke="#000" stroke-width="1.5"/>'
    s += f'<rect x="{x0+42}" y="{y0-12}" width="26" height="10" fill="#000"/><text x="{x0+55}" y="{y0-22}" text-anchor="middle" font-size="9">lever</text>'
    for r in range(10):
        y = y0 + r*dy + 4
        s += f'<rect x="{x0+10}" y="{y}" width="16" height="12" fill="#fff" stroke="#000"/><rect x="{x0+84}" y="{y}" width="16" height="12" fill="#fff" stroke="#000"/>'
    marks = [(20, 0), (18, 1), (16, 2), (14, 3)]
    for p, r in marks:
        y = y0 + r*dy + 10
        s += f'<line x1="{x0+102}" y1="{y}" x2="{x0+150}" y2="{y}" stroke="#000"/><text x="{x0+155}" y="{y+4}" font-weight="bold">{p} PIN</text>'
    yg = y0 + 9*dy + 10
    s += f'<line x1="{x0+8}" y1="{yg}" x2="{x0-40}" y2="{yg}" stroke="#000"/><text x="{x0-95}" y="{yg+4}" font-weight="bold">GND row</text>'
    s += f'<text x="{x0+55}" y="{y0+10*dy+22}" text-anchor="middle" font-size="10">20-pin ZIF socket (top view)</text>'
    s += '</svg>'
    return s

CSS = """
@page { size: A4; margin: 20mm 18mm 18mm 18mm;
  @bottom-center { content: counter(page); font: 9pt 'DejaVu Sans'; color:#666 }
  @top-right { content: 'Fairy IC Test Card – Manual'; font: 8pt 'DejaVu Sans'; color:#999 } }
@page cover { @bottom-center { content: none } @top-right { content: none } }
body { font-family: 'DejaVu Serif'; font-size: 10.8pt; line-height: 1.45; color:#111 }
h1 { font-family:'DejaVu Sans'; font-size: 17pt; margin: 0 0 8pt; border-bottom: 2px solid #1f4e79; color:#1f4e79; padding-bottom:3pt }
h2 { font-family:'DejaVu Sans'; font-size: 12.5pt; margin: 14pt 0 5pt; color:#1f4e79 }
h3 { font-family:'DejaVu Sans'; font-size: 11pt; margin: 10pt 0 4pt }
.page { page-break-before: always }
.cover { page: cover; text-align:center; padding-top: 35mm }
.cover .ic { font-family:'DejaVu Sans'; font-size: 46pt; font-weight:bold; letter-spacing:2pt }
.cover .sub { font-family:'DejaVu Serif'; font-size: 22pt; font-weight:bold; margin: 6mm 0 20mm }
.cover .man { display:inline-block; background:#111; color:#fff; font-family:'DejaVu Sans'; font-weight:bold; font-size:22pt; padding: 3mm 14mm; letter-spacing:3pt }
.cover .co { margin-top: 18mm; font-family:'DejaVu Sans'; font-size: 11pt; color:#333 }
table.ics { border-collapse: collapse; width:100%; font-family:'DejaVu Sans Mono'; font-size: 9.2pt; margin: 2pt 0 5pt }
table.ics td { border: 0.5pt solid #c8d3df; padding: 1.2pt 4pt }
table.ics tr:nth-child(odd) td { background:#f5f8fb }
.screen { font-family:'DejaVu Sans Mono'; font-size: 9pt; background:#0d1a0d; color:#7CFC7C; border-radius: 10pt; padding: 10pt 18pt; width: 118mm; margin: 6pt auto; white-space: pre; line-height:1.35 }
.keys td { padding: 2pt 6pt; vertical-align: top } .keys td.k { font-family:'DejaVu Sans Mono'; font-weight:bold; white-space:nowrap }
.note { border-left: 3pt solid #c0392b; background:#fbf1f0; padding: 4pt 8pt; font-size: 9.6pt; margin: 6pt 0 }
.ed { border-left: 3pt solid #1f4e79; background:#eef3f8; padding: 4pt 8pt; font-size: 9.6pt; margin: 6pt 0 }
.center { text-align:center }
.range { margin: 6pt 0 0 30mm; font-family:'DejaVu Sans' }
ol li { margin-bottom: 6pt }
img.photo { width: 100%; border: 0.5pt solid #999 }
.small { font-size: 8.6pt; color:#444; line-height:1.35 }
.cols { display:flex; gap: 8mm }
"""

def pre(xs, p): return [p + x for x in xs]

html = f"""<html><head><meta charset="utf-8"><style>{CSS}</style></head><body>
<div class="cover">
<div class="ic">IC TEST CARD</div>
<div class="sub">for the Apple ][ series</div>
<div class="man">MANUAL</div>
<div style="margin-top:4mm;font-style:italic;color:#444">– revised and corrected –</div>
<div style="margin-top:14mm">{LOGO.format(w=150)}</div>
<div class="co">YIH LUNG ENTERPRISE CO., LTD. · Copyright 1984</div>
</div>

<div class="page">
<h1>PREFACE</h1>
<p>Nowadays we use ICs frequently, because our technology is constantly invented and developed. Every technician has some ICs at hand, but he does not know exactly whether those ICs are good or bad. He has to spend much time inspecting and verifying them with an IC tester. Because an IC tester is expensive and testing takes a lot of time, we have designed and developed this easy-to-operate, low-price equipment called the IC TEST CARD.</p>
<p>This interface card is plugged into any of slots #1 – #7 of the APPLE II, which serves as the main board, and is connected to the Testool, which holds the IC being tested. Then just insert the diskette (the IC TEST CARD software) into the floppy disk drive. The result is shown on the display within a few milliseconds.</p>
<h1 style="margin-top:16pt">(I). SYSTEM DIAGRAM</h1>
{SYS_DIAG}
</div>

<div class="page">
<h1>(II). FUNCTIONS</h1>
<h2>A. Operating display</h2>
<div class="screen">            UNIVERSAL IC TESTER
   BY YIH LUNG ENTERPRISE CO., LTD.

                  COPYRIGHT 1984

           TEST IC NO.
         ┌──────────────────────┐
         │     74-LS – 138      │
         └──────────────────────┘
   CTRL-S : SEARCH IC NO.
   CTRL-C : CHANGE IC NO.
   CTRL-L : LOOP TEST
   SPACE  : START TESTING
   CTRL-S, CTRL-C, CTRL-L OR SPACE ? █
   RESULT : TEST OK</div>
<table class="keys">
<tr><td class="k">CTRL-S</td><td>Searches the number of the IC on the Testool and shows "138 OVER", "241 OVER", … If the IC is bad or not in the tested category, it shows "OVER".</td></tr>
<tr><td class="k">CTRL-C</td><td>Key in the number of the IC to be tested: 74S04, 74H123, 74LS74, 7486 …</td></tr>
<tr><td class="k">SPACE</td><td>Starts testing.</td></tr>
<tr><td></td><td>If the test is OK, the display shows "TEST OK" and the computer gives a long "BEEEP": the IC is good.</td></tr>
<tr><td></td><td>If the test fails, the display shows "TEST ERROR" and the computer gives five short beeps ("BI, BI, BI, BI, BI"): the IC is bad.</td></tr>
<tr><td></td><td>If the IC number keyed in is wrong, the display shows "THIS NUMBER IS NOT AVAILABLE".</td></tr>
<tr><td class="k">CTRL-L</td><td>Tests the IC on the Testool continuously. If the IC is aged or unstable, the display shows "LEVEL ERROR"; otherwise it shows "TEST OK".</td></tr>
</table>
<div class="note"><b>Note (annotation in the revised manual):</b> if the IC number has only two digits, add a leading zero (for example 74-LS-04, not 74-LS-4).</div>
<h2>B.</h2><p>Open-collector, tri-state … etc. TTL devices can be tested.</p>
<h2>C.</h2><p>Short-circuit protection: if the IC is put on the Testool the wrong way round, or the IC itself is short-circuited, the TEST CARD is not damaged and the display shows "LEVEL ERROR, POWER LOW".</p>
<h2>D.</h2><p>All input and output levels of the IC under test are checked. The High and Low levels used for the test can be set and adjusted.</p>
<div class="range">Range: &nbsp; High: 2.4 V – 4.5 V &nbsp;&nbsp;|&nbsp;&nbsp; Low: 0.4 V – 1.0 V</div>
</div>

<div>
<h1 style="margin-top:14pt">(III). OPERATION</h1>
<ol>
<li>The IC TEST CARD can be plugged into any slot. Take note of the slot the card is plugged into. When the display shows
<div class="center" style="font-family:'DejaVu Sans Mono';margin:4pt">CARD IN WHICH SLOT ?<br>(1, 2, 3, 4, 5, 6, 7) ?</div>
just press, on the keyboard, the number of the slot the IC TEST CARD is in.</li>
<li>The IC TEST CARD software is based on the ASCII code of APPLESOFT. If the printer is on, the IC TEST CARD is off.</li>
<li>The test levels can be adjusted. If the ICs being tested come from various brands and cannot be tested with the default levels, the user can adjust the levels as follows:
<div class="center" style="margin:8pt 0">{VR_DIAG}</div>
<table class="keys"><tr><td class="k">VR1</td><td>HIGH level — range 2.4 V ~ 4.5 V, default 2.6 V</td></tr>
<tr><td class="k">VR2</td><td>LOW level — range 0.3 V ~ 1.2 V, default 0.8 V</td></tr></table>
The levels can be checked with a multimeter, an oscilloscope, etc. The right way is to measure the voltage of P1 or P2 to ground.</li>
<li>All rights to this manual and software are reserved by YIH LUNG ENTERPRISE CO., LTD. If the software diskette is damaged by user modification, we do not offer a new diskette or any service. Please keep the diskette with its serial number, in order to exchange it for new software and further service later.</li>
</ol>
</div>

<div class="page">
<h1>(IV). LIST OF ICs TESTED</h1>
<h2>FLOPPY DISK I (TTL)</h2>
<h3>A. Standard TTL (54/7400 series)</h3>{grid(TTL_STD)}
<h3>B. Low-power Schottky TTL (54/74LS series)</h3>{grid(pre(LS,'74LS'))}
<h3>C. Schottky-clamped TTL (54/74S series)</h3>{grid(pre(S,'74S'))}
<h3>D. Low-power TTL (54/74L series)</h3>{grid(pre(L,'74L'))}
<h3>E. High-speed TTL (54/74H series)</h3>{grid(pre(H,'74H'))}
<h3>F. Random-access memory (54/74 series)</h3>{grid(RAM)}
<h2 style="page-break-before:always">FLOPPY DISK II (CMOS)</h2>
<h3>A. TTL-equivalent CMOS devices (54/74HC series)</h3>{grid(pre(HC,'74HC'))}
<h3>B. CD 45/4000 series (or MC 145/140 series) CMOS devices</h3>{grid(pre(CD,'CD'))}
<h3>C. Memory</h3>{grid(MEM)}
</div>

<div class="page">
<h1>ATTENTION</h1>
<p>We have added CMOS ICs to the diskette, as follows:</p>
<h3>CD 4000 / 4500 series</h3>{grid(pre(ADD_CD,'CD'),9)}
<h3>74HC series</h3>{grid(pre(ADD_HC,'74HC'),9)}
<p>Because of the new items, the program on the diskette has changed as follows. When you run the program it will show:</p>
<table class="keys">
<tr><td class="k">PICTURE 1</td><td>Our marks.</td></tr>
<tr><td class="k">PICTURE 2</td><td>Right location of the IC pins.</td></tr>
<tr><td class="k">PICTURE 3</td><td>A. TTL 54/74 SERIES<br>B. CMOS 40/45 SERIES<br>C. HCMOS 74HC SERIES<br>WHICH ONE? A, B OR C?<br><i>After selecting, press RETURN; it will then show:</i></td></tr>
<tr><td class="k">PICTURE 4</td><td>Our mark &amp; WAITING.</td></tr>
<tr><td class="k">PICTURE 5</td><td>CARD IN WHICH SLOT? (1, 2, 3, 4, 5, 6 or 7)?<br><i>After selecting, it shows the operating display described in this manual.</i></td></tr>
</table>
<p>Press CTRL-C, then:</p>
<table class="keys">
<tr><td>If you selected <b>A</b>, press:</td><td class="k">74- &nbsp; or &nbsp; 74-S- &nbsp; or &nbsp; 74-LS-</td></tr>
<tr><td>If you selected <b>B</b>, press:</td><td class="k">CD-40- &nbsp; or &nbsp; CD-45-</td></tr>
<tr><td>If you selected <b>C</b>, press:</td><td class="k">74-HC-</td></tr>
</table>
<p>All other operations are the same as described in this manual.</p>
</div>

<div class="page">
<h1>(VI). FLOW DIAGRAM OF TESTING OPERATION</h1>
{FLOW}
</div>

<div class="page">
<h1>APPENDIX — Hardware and notes on this edition</h1>
<div class="ed">This appendix is not part of the original manual. It was added in this edition (Tabajara Labs, 2026) to document the hardware and how the transcription was made.</div>
<h2 style="margin-top:4pt">The IC TEST CARD and the Testool</h2>
<img class="photo" style="width:58%;margin-left:21%" src="img/card_top.jpg">
<p class="small">The interface card: three MC6821 PIAs (IC10 and others), five CD4066 analog switches, comparators with the VR1/VR2 level trimmers, a 74LS368 and the power-switching transistors. Photo: AppleBox / J.E.H. Walsh (applefritter.com).</p>
<div class="cols"><div style="flex:1"><img class="photo" style="width:78%" src="img/testool.jpg"></div>
<div style="flex:1"><div style="width:82%">{socket_svg()}</div>
<p class="small">Position of the IC on the Testool ("Picture 2"): the IC always sits with its <b>GND row at the bottom</b> of the 20-pin ZIF socket. Pin 1 of a 14-, 16-, 18- or 20-pin IC sits at the matching mark.</p></div></div>
<h2 style="margin-top:6pt">Notes on the transcription</h2>
<ul class="small">
<li>Source: the 9 scanned pages of the manual published by AppleBox (applefritter.com/appleii-box). The page with section (V) was not scanned, so the numbering goes from (IV) straight to (VI), as in the original.</li>
<li>The text was re-typeset with spelling corrected (e.g. "casued" → "caused", "catagory" → "category", "ociloscope" → "oscilloscope"), keeping the original meaning.</li>
<li>The note about a leading zero for two-digit numbers is an annotation in the "revised and corrected" scan, not part of the 1984 print.</li>
<li>Section II-D gives a High range of 2.4–4.5 V and a Low range of 0.4–1.0 V; section III-3 gives 2.4–4.5 V (default 2.6 V) and 0.3–1.2 V (default 0.8 V). Both are kept as printed.</li>
<li>"74HC373" in the Floppy Disk II list is smudged in the scan; it is confirmed by the ATTENTION list.</li>
<li>In the ATTENTION list, the CD4000 column entry printed as "4031" was read as <b>4051</b> (the sequence 4049 → 4051 → 4052, and the 4051 test present in the software).</li>
<li>The lists show everything the manufacturer advertised. The diskette version studied here (TEST.2 / CMOS.2 / HMOS.2) implements 158 TTL, 68 CMOS 40xx and 49 74HC types; the CMOS memories (4164, 2114 …) are not implemented in it.</li>
</ul>
</div>
</body></html>"""

out = HERE / f'Fairy_IC_Test_Card_Manual_{VER}.pdf'
weasyprint.HTML(string=html, base_url=str(HERE)).write_pdf(out)
print(out)
