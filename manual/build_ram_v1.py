#!/usr/bin/env python3
"""build_ram_v1.py - gera RAM_Tester_e_Adaptador_v1.pdf (opcao D do IC TESTER v2.0)"""
from weasyprint import HTML

CHIPS = [
  # nome, pinos, girado, jumper, PD, org, tipo, tempo
  ('2114', 18, False, True, '$C7', '1K × 4', 'SRAM', '≈ 4 s'),
  ('2147', 18, False, True, '$C7', '4K × 1', 'SRAM', '≈ 12 s'),
  ('4164', 16, True, False, '$47', '64K × 1', 'DRAM', '≈ 1 min 40 s'),
  ('41256', 16, True, False, '$47', '256K × 1', 'DRAM', '≈ 7 min'),
  ('4416', 18, True, True, '$C7', '16K × 4', 'DRAM', '≈ 40 s'),
  ('4464', 18, True, True, '$C7', '64K × 4', 'DRAM', '≈ 2 min 25 s'),
  ('6116', 24, None, False, '$C7', '2K × 8', 'SRAM (adaptador)', '≈ 6 s'),
  ('6264', 28, None, False, '$C7', '8K × 8', 'SRAM (adaptador)', '≈ 22 s'),
]
PINOUT = {
 '2114': {1:'A6',2:'A5',3:'A4',4:'A3',5:'A0',6:'A1',7:'A2',8:'/CS',9:'GND',10:'/WE',11:'I/O4',12:'I/O3',13:'I/O2',14:'I/O1',15:'A9',16:'A8',17:'A7',18:'VCC'},
 '2147': {1:'A0',2:'A1',3:'A2',4:'A3',5:'A4',6:'A5',7:'DOUT',8:'/WE',9:'GND',10:'/CS',11:'DIN',12:'A6',13:'A7',14:'A8',15:'A9',16:'A10',17:'A11',18:'VCC'},
 '4164': {1:'NC',2:'DIN',3:'/WE',4:'/RAS',5:'A0',6:'A2',7:'A1',8:'VCC',9:'A7',10:'A5',11:'A4',12:'A3',13:'A6',14:'DOUT',15:'/CAS',16:'GND'},
 '41256': {1:'A8',2:'DIN',3:'/WE',4:'/RAS',5:'A0',6:'A2',7:'A1',8:'VCC',9:'A7',10:'A5',11:'A4',12:'A3',13:'A6',14:'DOUT',15:'/CAS',16:'GND'},
 '4416': {1:'/OE',2:'DQ1',3:'DQ2',4:'/WE',5:'/RAS',6:'A6',7:'A5',8:'A4',9:'VCC',10:'A7',11:'A3',12:'A2',13:'A1',14:'A0',15:'DQ3',16:'/CAS',17:'DQ4',18:'GND'},
}
PINOUT['4464'] = PINOUT['4416']

def pin_at(pos, p, rot):
    n = p // 2
    if not rot:
        if pos <= 10:
            k = pos - (10 - n); return k if 1 <= k <= n else 0
        k = n + (pos - 10); return k if pos - 10 <= n else 0
    if pos >= 11:
        k = pos - 10; return k if k <= n else 0
    k = pos + (p - 10); return k if k > n else 0

def portname(pos):
    if 3 <= pos <= 10: return 'PA%d' % (pos - 3)
    if 11 <= pos <= 18: return 'PB%d' % (pos - 11)
    return {1: 'PC0', 2: 'PC1', 19: 'PC2', 20: 'VCC'}[pos]

def zif_svg(name, p, rot, jumper):
    W, H = 520, 420
    s = [f'<svg viewBox="0 0 {W} {H}" width="{W}" height="{H}" xmlns="http://www.w3.org/2000/svg" font-family="DejaVu Sans" font-size="11">']
    s.append(f'<rect x="150" y="10" width="220" height="400" rx="10" fill="#f3f3f3" stroke="#555"/>')
    s.append('<text x="260" y="28" text-anchor="middle" fill="#555">ZIF (vista de cima)</text>')
    n = p // 2
    rows = [r for r in range(1, 11) if pin_at(r, p, rot)]
    y0 = 40 + (min(rows) - 1) * 36 - 6; y1 = 40 + (max(rows) - 1) * 36 + 30
    s.append(f'<rect x="200" y="{y0}" width="120" height="{y1-y0}" rx="4" fill="#222"/>')
    s.append(f'<text x="260" y="{(y0+y1)/2+5}" text-anchor="middle" fill="#fff" font-size="15" font-weight="bold">{name}</text>')
    ny = y0 if not rot else y1
    s.append(f'<path d="M245 {ny} a15 15 0 0 {0 if not rot else 1} 30 0" fill="#f3f3f3" stroke="#f3f3f3"/>')
    for r in range(1, 11):
        y = 40 + (r - 1) * 36 + 12
        for pos, x, anchor, tx in ((r, 185, 'end', 140), (21 - r, 335, 'start', 380)):
            k = pin_at(pos, p, rot)
            fill = '#c33' if k else '#fff'
            s.append(f'<circle cx="{185 if pos<=10 else 335}" cy="{y}" r="7" fill="{fill}" stroke="#333"/>')
            lbl = f'pos {pos} ({portname(pos)})'
            if pos == 10: lbl += ' GND'
            if pos == 20: lbl = 'pos 20 (VCC fixo)'
            px = 172 if pos <= 10 else 348
            s.append(f'<text x="{px}" y="{y+4}" text-anchor="{"end" if pos<=10 else "start"}" font-size="9" fill="#666">{"" if k else ""}</text>')
            xl = 120 if pos <= 10 else 400
            s.append(f'<text x="{xl}" y="{y+4}" text-anchor="{"end" if pos<=10 else "start"}" font-size="10">{lbl}</text>')
            if k:
                nm = PINOUT[name][k]
                xi = 196 if pos <= 10 else 324
                s.append(f'<text x="{xi+ (8 if pos<=10 else -8)}" y="{y+4}" text-anchor="{"start" if pos<=10 else "end"}" fill="#ffd" font-size="10">{k} {nm}</text>')
    if jumper:
        ya, yb = 40 + 12, 40 + 36 + 12
        s.append(f'<path d="M343 {ya} C 395 {ya}, 395 {yb}, 343 {yb}" fill="none" stroke="#06c" stroke-width="3"/>')
    s.append('</svg>')
    return ''.join(s)

def adapter_svg():
    return '''<svg viewBox="0 0 640 380" width="640" height="380" xmlns="http://www.w3.org/2000/svg" font-family="DejaVu Sans" font-size="11">
<rect x="10" y="40" width="130" height="300" rx="6" fill="#eee" stroke="#444"/>
<text x="75" y="30" text-anchor="middle" font-weight="bold">Plugue 20 pinos (no ZIF)</text>
<text x="20" y="70">pos 3-9: PA0-PA6</text><text x="20" y="90">pos 11-18: PB0-PB7</text>
<text x="20" y="110">pos 1: PC0</text><text x="20" y="130">pos 2: PC1</text><text x="20" y="150">pos 19: PC2</text>
<text x="20" y="170">pos 20: VCC</text><text x="20" y="190">pos 10: GND</text>
<rect x="250" y="40" width="130" height="120" rx="6" fill="#dfe9f7" stroke="#246"/>
<text x="315" y="30" text-anchor="middle" font-weight="bold">74HC574 (latch)</text>
<text x="260" y="70">D0-D5 ← PB0-PB5</text><text x="260" y="90">CLK ← PC0</text><text x="260" y="110">/OE → GND</text>
<text x="260" y="130">Q0-Q5 → A7-A12</text><text x="260" y="150">D6,D7 → GND</text>
<rect x="470" y="40" width="160" height="300" rx="6" fill="#222"/>
<text x="550" y="30" text-anchor="middle" font-weight="bold">Soquete 28 pinos</text>
<text x="480" y="70" fill="#fff">A0-A6 ← PA0-PA6</text><text x="480" y="90" fill="#fff">A7-A12 ← Q0-Q5</text>
<text x="480" y="110" fill="#fff">D0-D7 ↔ PB0-PB7</text><text x="480" y="130" fill="#fff">/OE (22) ← PC1</text>
<text x="480" y="150" fill="#fff">/WE (27) ← PC2</text><text x="480" y="170" fill="#fff">/CE1 (20) → GND</text>
<text x="480" y="190" fill="#fff">CE2 (26) → VCC</text><text x="480" y="210" fill="#fff">VCC (28) ← pos 20</text>
<text x="480" y="230" fill="#fff">GND (14) ← pos 10</text>
<text x="480" y="260" fill="#ffd">J1 no pino 23:</text><text x="480" y="280" fill="#ffd">6264 → Q4 (A11)</text><text x="480" y="300" fill="#ffd">6116 → PC2 (/WE)</text>
<text x="250" y="200">100 nF entre VCC e GND</text>
<text x="250" y="216">junto a cada CI.</text>
<text x="250" y="250" fill="#a33">PA0-6, PB, PC1, PC2:</text>
<text x="250" y="266" fill="#a33">direto ao soquete</text>
<text x="250" y="290" fill="#246">PB0-5 e PC0: ao latch</text>
</svg>'''

NET = [
 ('ZIF pos 3 (PA0)', 'soquete 10 (A0)'), ('ZIF pos 4 (PA1)', 'soquete 9 (A1)'), ('ZIF pos 5 (PA2)', 'soquete 8 (A2)'),
 ('ZIF pos 6 (PA3)', 'soquete 7 (A3)'), ('ZIF pos 7 (PA4)', 'soquete 6 (A4)'), ('ZIF pos 8 (PA5)', 'soquete 5 (A5)'),
 ('ZIF pos 9 (PA6)', 'soquete 4 (A6)'), ('ZIF pos 10 (GND)', 'soquete 14, 20 (/CE1); 574 pinos 1 (/OE), 10, 8, 9 (D6, D7)'),
 ('ZIF pos 11 (PB0)', 'soquete 11 (D0) e 574 pino 2 (D0)'), ('ZIF pos 12 (PB1)', 'soquete 12 (D1) e 574 pino 3 (D1)'),
 ('ZIF pos 13 (PB2)', 'soquete 13 (D2) e 574 pino 4 (D2)'), ('ZIF pos 14 (PB3)', 'soquete 15 (D3) e 574 pino 5 (D3)'),
 ('ZIF pos 15 (PB4)', 'soquete 16 (D4) e 574 pino 6 (D4)'), ('ZIF pos 16 (PB5)', 'soquete 17 (D5) e 574 pino 7 (D5)'),
 ('ZIF pos 17 (PB6)', 'soquete 18 (D6)'), ('ZIF pos 18 (PB7)', 'soquete 19 (D7)'),
 ('ZIF pos 1 (PC0)', '574 pino 11 (CLK)'), ('ZIF pos 2 (PC1)', 'soquete 22 (/OE)'),
 ('ZIF pos 19 (PC2)', 'soquete 27 (/WE) e J1 lado "6116"'), ('ZIF pos 20 (VCC)', 'soquete 28, 26 (CE2); 574 pino 20'),
 ('574 pino 19 (Q0)', 'soquete 3 (A7)'), ('574 pino 18 (Q1)', 'soquete 25 (A8)'), ('574 pino 17 (Q2)', 'soquete 24 (A9)'),
 ('574 pino 16 (Q3)', 'soquete 21 (A10)'), ('574 pino 15 (Q4)', 'J1 lado "6264"'), ('574 pino 14 (Q5)', 'soquete 2 (A12)'),
 ('J1 comum', 'soquete 23 (A11 no 6264; /WE no 6116)'),
]

rows = ''.join(f'<tr><td>{c[0]}</td><td>{c[6]}</td><td>{c[5]}</td><td>{"adaptador" if c[2] is None else ("GIRADA 180°" if c[2] else "normal")}</td>'
               f'<td>{"sim (19–20)" if c[3] else "não"}</td><td>{c[4]}</td><td>{c[7]}</td></tr>' for c in CHIPS)
diagrams = ''
for c in CHIPS:
    if c[2] is None: continue
    diagrams += f'<div class="dg"><h3>{c[0]} — {c[6]} {c[5]}{" — jumper (azul) entre as posições 19 e 20" if c[3] else ""}{" — girada 180°" if c[2] else ""}</h3>{zif_svg(c[0], c[1], c[2], c[3])}</div>'
netrows = ''.join(f'<tr><td>{a}</td><td>{b}</td></tr>' for a, b in NET)

html = f'''<html><head><meta charset="utf-8"><style>
@page {{ size: A4; margin: 18mm 16mm; @bottom-center {{ content: "IC TESTER V2.0 — Teste de memórias RAM — " counter(page); font-size: 8pt; color:#777 }} }}
body {{ font-family: "DejaVu Sans", sans-serif; font-size: 10.5pt; line-height: 1.4; }}
h1 {{ font-size: 20pt; margin-bottom: 0 }} h2 {{ font-size: 14pt; border-bottom: 1px solid #999; margin-top: 18pt }}
h3 {{ font-size: 11pt; margin: 6pt 0 }}
table {{ border-collapse: collapse; width: 100%; font-size: 9.5pt }} td, th {{ border: 1px solid #aaa; padding: 3pt 5pt }}
th {{ background: #eee }} .dg {{ page-break-inside: avoid; }} code, pre {{ font-family: "DejaVu Sans Mono"; font-size: 9pt }}
pre {{ background:#f4f4f4; padding:6pt }} .warn {{ background:#fff3d6; border-left:4px solid #e0a000; padding:6pt }}
</style></head><body>
<h1>IC TESTER — Teste de memórias RAM</h1>
<p>Opção <b>D: MEMORY (RAM)</b> do IC TESTER VERSION 2.0 EXPANDED BY TABAJARA LABS (imagem <code>IC_Tester_ProDOS_v11.po</code>,
programa <code>RAMTEST.ENG v1</code>). Placa Fairy / Yih-Lung "Universal I.C. Tester", 1984. Documento v1 — 20/11/2026.</p>
<p>O manual original anunciava a opção MEMORY, mas ela nunca foi fornecida. Esta é uma implementação nova, feita a partir
do mapeamento do hardware confirmado na bancada (PD = 8 chaves de alimentação independentes; posição 20 do ZIF = VCC fixo).</p>

<h2>1. Como usar</h2>
<ol>
<li>No menu principal tecle <b>D</b>. Informe o slot da placa (1–7).</li>
<li>Escolha a memória (1–8). A tela desenha o ZIF visto de cima com o número de cada pino do chip na posição em que ele fica,
o chanfro (marcado com <code>()</code>) e, quando necessário, o jumper entre as posições 19 e 20.</li>
<li>Coloque o chip <b>com tudo desligado</b> (o programa só liga a alimentação quando você tecla ESPAÇO) e tecle <b>ESPAÇO</b>.
ESC volta à lista.</li>
<li>Durante o teste a linha 22 mostra o passo (1/3, 2/3, 3/3) e o endereço/linha em andamento. No fim: <b>TEST OK !</b>
(bip longo) ou a mensagem de erro (5 bips). Qualquer tecla volta à lista; ESC na lista volta ao menu principal.</li>
</ol>
<div class="warn"><b>Atenção:</b> um chip colocado ao contrário recebe a alimentação invertida e pode ser danificado — a placa
não tem como perceber isso antes de ligar. Confira o desenho da tela antes de teclar ESPAÇO. As DRAMs (4164, 41256, 4416, 4464)
vão <b>giradas 180°</b> (chanfro para baixo) — isso é o certo, não um erro.</div>

<h2>2. Memórias suportadas</h2>
<table><tr><th>Chip</th><th>Tipo</th><th>Organização</th><th>Orientação</th><th>Jumper</th><th>PD</th><th>Tempo (1 MHz)</th></tr>{rows}</table>
<p>Tempos medidos no simulador (ciclos do 6502 a 1,023 MHz). As DRAMs são lentas porque cada acesso passa por várias escritas
nas portas do 6821.</p>
<p><b>Não suportadas:</b> 4116 / 4027 (precisam de +12 V e −5 V); 2102 / 2125 (VCC no pino 10 e GND no pino 9 caem em posições
sem chave de alimentação); qualquer memória de 24/28 pinos sem o adaptador. As 7489, 74S189 e 74S201 já são testadas pela opção A.</p>

<h2>3. Por que girar ou usar jumper</h2>
<p>A placa só tem VCC chaveado nas posições 7, 8, 17, 18 (e fixo na 20) e GND nas posições 10, 13, 14, 15. Um chip de
16 pinos encostado embaixo tem o GND na posição 18 e o VCC na 10 — o contrário do que existe. Girando o chip, o pino 8 (VCC)
cai na posição 18 e o pino 16 (GND) na posição 10: código PD <code>$47</code>. Um chip de 18 pinos normal tem o VCC (pino 18)
na posição 19, que é uma linha de porta (PC2) sem chave: o jumper 19–20 leva o VCC fixo da posição 20 até ele, e o programa
deixa a PC2 sempre como entrada. As 4416/4464 têm VCC no pino 9, por isso vão giradas e também com jumper.</p>

<h2>4. Posição de cada memória no ZIF</h2>
<p>Pinos em vermelho = ocupados. Ao lado de cada furo: posição do ZIF e a linha da placa (porta do 6821).</p>
{diagrams}

<h2>5. O que o teste faz</h2>
<h3>SRAM (2114, 2147, 6116, 6264)</h3>
<ul><li><b>Passo 1:</b> grava $55/$AA alternados (xadrez) em todos os endereços e confere.</li>
<li><b>Passo 2:</b> o mesmo padrão invertido — cada célula é testada em 0 e em 1, e bits vizinhos com valores opostos.</li>
<li><b>Passo 3 — linhas de endereço:</b> grava um valor no endereço 0 e em cada endereço 2<sup>b</sup>; depois troca um de cada
vez e confere se nenhum outro mudou. Detecta linha de endereço aberta, presa ou em curto (o defeito aparece como
<code>BAD ADDR BIT n</code>).</li></ul>
<p>A escrita é controlada pelo /CS (o /WE desce antes), de modo que as saídas do chip nunca brigam com as portas.</p>
<h3>DRAM (4164, 41256, 4416, 4464)</h3>
<p>Não há refresh por hardware e o refresh por software é lento demais (uma varredura das 256 linhas pela placa leva ~25 ms,
o datasheet pede 4 ms). Por isso o teste é organizado <b>por linha</b>: cada linha é gravada e lida inteira em seguida — o
próprio acesso às colunas mantém a linha atualizada. Passos 1 e 2: xadrez físico (linha xor coluna) e invertido, linha por
linha. Passo 3: linhas de endereço de linha (ROW) e de coluna (COL), pelo mesmo método da SRAM, em poucos acessos rápidos.</p>
<p>Cada ciclo é: endereço de linha → /RAS desce → endereço de coluna (+ /WE e dado, ou /OE) → /CAS desce → leitura → /RAS sobe.
O /RAS fica baixo cerca de 75 µs; o datasheet especifica no máximo 10 µs. Na prática a maioria das DRAMs aceita /RAS longo
(o limite protege a carga da linha, que aqui é regravada a cada acesso), mas é o ponto mais frágil do método: <b>se uma DRAM
boa conhecida falhar sempre, a causa é esta e não o chip</b>.</p>
<h3>Mensagens</h3>
<table><tr><th>Mensagem</th><th>Significado</th></tr>
<tr><td>TEST OK !</td><td>todos os passos passaram</td></tr>
<tr><td>LEVEL ERROR, POWER LOW</td><td>o GND da posição 10 não chegou a nível baixo (placa, PD ou curto)</td></tr>
<tr><td>TEST ERROR END, STEP n</td><td>falhou no passo n; segue o endereço (SRAM) ou ROW/COL (DRAM), o valor esperado (EXP) e o lido (GOT)</td></tr>
<tr><td>BAD ADDR BIT n [ROW|COL]</td><td>no passo 3: a linha de endereço n não funciona ou está em curto com outra</td></tr></table>
<p>Na comparação EXP/GOT, os bits diferentes indicam o pino de dado com defeito (bit 0 = I/O1/DQ1/D0).</p>

<h2>6. Adaptador para 6116 / 6264</h2>
<p>O ZIF tem 20 posições e só 19 linhas de porta; uma 6264 precisa de 13 endereços + 8 dados + 2 controles. O adaptador usa as
8 linhas PB como barramento de dados <b>e</b> como entrada de um latch 74HC574 que guarda os endereços altos A7–A12. O programa
só regrava o latch quando o endereço alto muda (a cada 128 endereços).</p>
{adapter_svg()}
<h3>Ligações (lista completa)</h3>
<table><tr><th>De</th><th>Para</th></tr>{netrows}</table>
<p>O plugue de 20 pinos pode ser feito com barra de pinos torneados ou com um soquete de 20 pinos usado como plugue; o pino 1
do adaptador fica na posição 1 do ZIF. A 6116 entra <b>encostada embaixo</b> no soquete de 28 (pino 1 da 6116 no pino 3 do
soquete): assim o GND da 6116 (pino 12) cai no pino 14, o VCC (24) no 26 — que é o CE2 da 6264, ligado a VCC —, o /CS (18) no
20 (GND) e o /OE (20) no 22. O único pino que difere é o 23 (A11 na 6264, /WE na 6116), escolhido pelo jumper J1.</p>
<p>No adaptador, o 74HC574 é alimentado pelo mesmo VCC/GND da memória (PD <code>$C7</code>: VCC na 20, GND na 10). Use 74HC574 ou 74HCT574 (o 74LS374 faz a mesma função, mas a pinagem é outra). Coloque 100 nF junto de cada CI.</p>

<h2>7. Arquivos</h2>
<ul><li><code>analise/fonte/ramtest_v1.s</code> — fonte (ca65), carregado em $0800; tabelas de imagens de porta em $3000–$377F.</li>
<li><code>analise/ferramentas/simram_v1.py</code> — simulador: placa (PD por chaves) + modelos funcionais de SRAM, DRAM
(RAS/CAS, retenção) e adaptador, escritos a partir dos datasheets, com falhas injetáveis (bit preso, linha de endereço
aberta, chip morto, chip invertido). Todos os casos testados foram aprovados ou reprovados corretamente.</li></ul>
</body></html>'''
HTML(string=html).write_pdf('RAM_Tester_e_Adaptador_v1.pdf')
print('ok')
