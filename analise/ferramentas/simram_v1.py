#!/usr/bin/env python3
"""simram.py v1 - simula o RAMTEST.ENG com um modelo da placa IC TEST CARD
(PD = 8 chaves independentes, medido na bancada em 2026-11-20) e modelos
funcionais de memorias, escritos a partir das pinagens dos datasheets
(independentes das tabelas do RAMTEST).

uso: simram.py RAMTEST.ENG chip [falha] [--rows N] [--keys TECLAS]
  chip : 2114 2147 4164 41256 4416 4464 6116 6264
  falha: ok | stuck:BIT | alias:LINHA | dead | rev  (rev = chip invertido)
  --rows N : reduz o numero de linhas (row) da DRAM para acelerar
"""
import sys, argparse
from py65.devices.mpu6502 import MPU
from py65.memory import ObservableMemory

ap = argparse.ArgumentParser()
ap.add_argument('eng'); ap.add_argument('chip'); ap.add_argument('fault', nargs='?', default='ok')
ap.add_argument('--rows', type=int, default=0)
ap.add_argument('--lbl', default='')
ap.add_argument('--maxsteps', type=int, default=400_000_000)
a = ap.parse_args()

SLOT = 4
mem = ObservableMemory()
m = MPU(memory=mem)
code = open(a.eng, 'rb').read()
for i, b in enumerate(code): mem[0x800 + i] = b
base = 0xC084 + SLOT * 16
regs = [{'ddr': 0, 'dat': 0, 'cr': 0} for _ in range(6)]

def kof(s):
    if 3 <= s <= 10: return (0, s - 3)
    if 11 <= s <= 18: return (1, s - 11)
    return {1: (2, 0), 2: (2, 1), 19: (2, 2)}.get(s)

# ---------------- pinagens (datasheet) ----------------
P2114 = {1:'A6',2:'A5',3:'A4',4:'A3',5:'A0',6:'A1',7:'A2',8:'CS',9:'GND',10:'WE',
         11:'D3',12:'D2',13:'D1',14:'D0',15:'A9',16:'A8',17:'A7',18:'VCC'}
P2147 = {1:'A0',2:'A1',3:'A2',4:'A3',5:'A4',6:'A5',7:'DOUT',8:'WE',9:'GND',10:'CS',11:'DIN',
         12:'A6',13:'A7',14:'A8',15:'A9',16:'A10',17:'A11',18:'VCC'}
P4164 = {1:'A8',2:'DIN',3:'WE',4:'RAS',5:'A0',6:'A2',7:'A1',8:'VCC',9:'A7',10:'A5',11:'A4',
         12:'A3',13:'A6',14:'DOUT',15:'CAS',16:'GND'}
P4416 = {1:'OE',2:'D0',3:'D1',4:'WE',5:'RAS',6:'A6',7:'A5',8:'A4',9:'VCC',10:'A7',11:'A3',
         12:'A2',13:'A1',14:'A0',15:'D2',16:'CAS',17:'D3',18:'GND'}

CH = {
 '2114':  dict(kind='sram', pins=18, pinout=P2114, abits=10, dbits=4, rot=False, pd=0xC7, jumper=True),
 '2147':  dict(kind='sram', pins=18, pinout=P2147, abits=12, dbits=1, rot=False, pd=0xC7, jumper=True),
 '4164':  dict(kind='dram', pins=16, pinout=P4164, rbits=8, cbits=8, dbits=1, rot=True, pd=0x47, jumper=False),
 '41256': dict(kind='dram', pins=16, pinout=P4164, rbits=9, cbits=9, dbits=1, rot=True, pd=0x47, jumper=False),
 '4416':  dict(kind='dram', pins=18, pinout=P4416, rbits=8, cbits=6, dbits=4, rot=True, pd=0xC7, jumper=True, colA1=True),
 '4464':  dict(kind='dram', pins=18, pinout=P4416, rbits=8, cbits=8, dbits=4, rot=True, pd=0xC7, jumper=True),
 '6116':  dict(kind='adpt', abits=11, pd=0xC7, jumper=False),
 '6264':  dict(kind='adpt', abits=13, pd=0xC7, jumper=False),
}
cfg = CH[a.chip]
fault = a.fault
rev = fault == 'rev'

def pos_of(pin):
    p = cfg['pins']; n = p // 2
    rot = cfg['rot'] ^ rev
    if not rot:
        return pin + (10 - n) if pin <= n else 10 + (pin - n)
    return 10 + pin if pin <= n else pin - (p - 10)

def power_levels():
    pd = regs[3]['dat']
    lv = {}
    for b, s in ((0, 7), (1, 8), (6, 17), (7, 18)):
        if not pd >> b & 1: lv[s] = 1
    for b, s in ((2, 10), (3, 13), (4, 14), (5, 15)):
        if pd >> b & 1: lv[s] = 0
    lv[20] = 1
    if cfg['jumper']: lv[19] = 1
    return lv

stats = {'ras_max': 0, 'conflict': 0, 'decay': 0}
import collections
cpos = collections.Counter()
cyc = [0]

class Chip:
    def __init__(s):
        s.drive = {}
    def pinpos(s, name):
        return s.pos[name]

class Mem(Chip):
    def __init__(s):
        super().__init__()
        s.pos = {}
        if cfg['kind'] != 'adpt':
            for pin, nm in cfg['pinout'].items(): s.pos[nm] = pos_of(pin)
        s.data = {}
        s.lastras = 1; s.lastcas = 1; s.row = 0; s.col = 0; s.rasat = 0
        s.lastclk = 0; s.latch = 0
        s.rowtime = {}
    def addr(s, lv, names):
        v = 0
        for i, nm in enumerate(names):
            bit = lv.get(s.pos[nm], 1)
            if bit is None: bit = 1
            if fault.startswith('alias:') and i == int(fault[6:]): bit = 0
            v |= (bit & 1) << i
        return v
    def wrval(s, k, v):
        if fault == 'dead': return
        if fault.startswith('stuck:'):
            b = int(fault[6:]); v |= 1 << b
        s.data[k] = v & ((1 << cfg.get('dbits', 8)) - 1)
    def rdval(s, k):
        return s.data.get(k, 0x5A & ((1 << cfg.get('dbits', 8)) - 1))
    def dpins(s):
        d = cfg['dbits']
        return ['D%d' % i for i in range(d)] if 'D0' in s.pos else None
    def update(s, lv):
        s.drive = {}
        k = cfg['kind']
        if k == 'adpt': return s.upd_adpt(lv)
        if lv.get(s.pos['VCC']) != 1 or lv.get(s.pos['GND']) != 0: return
        g = lambda nm: 1 if lv.get(s.pos[nm]) is None else lv.get(s.pos[nm])
        if k == 'sram':
            ad = s.addr(lv, ['A%d' % i for i in range(cfg['abits'])])
            if g('CS') == 0:
                dp = s.dpins()
                if g('WE') == 0:
                    if dp:
                        v = sum((g(n) & 1) << i for i, n in enumerate(dp))
                    else:
                        v = g('DIN')
                    s.wrval(ad, v)
                else:
                    v = s.rdval(ad)
                    if dp:
                        for i, n in enumerate(dp): s.drive[s.pos[n]] = v >> i & 1
                    else:
                        s.drive[s.pos['DOUT']] = v & 1
            return
        # DRAM
        ras, cas = g('RAS'), g('CAS')
        if s.lastras == 1 and ras == 0:
            s.row = s.addr(lv, ['A%d' % i for i in range(cfg['rbits'])])
            s.rasat = cyc[0]
            # retencao: linha sem acesso ha mais de 2 s perde os dados
            last = s.rowtime.get(s.row)
            if last is not None and cyc[0] - last > 2_000_000:
                for key in [kk for kk in s.data if kk[0] == s.row]: del s.data[key]
                stats['decay'] += 1
            s.rowtime[s.row] = cyc[0]
        if s.lastras == 0 and ras == 1:
            d = cyc[0] - s.rasat
            if d > stats['ras_max']: stats['ras_max'] = d; stats['ras_pc'] = '%04X' % m.pc
        if ras == 0 and s.lastcas == 1 and cas == 0:
            names = ['A%d' % i for i in (range(1, 7) if cfg.get('colA1') else range(cfg['cbits']))]
            s.col = s.addr(lv, names)
            if g('WE') == 0:
                dp = s.dpins()
                v = sum((g(n) & 1) << i for i, n in enumerate(dp)) if dp else g('DIN')
                s.wrval((s.row, s.col), v)
        if ras == 0 and cas == 0 and g('WE') == 1 and ('OE' not in s.pos or g('OE') == 0):
            v = s.rdval((s.row, s.col))
            dp = s.dpins()
            if dp:
                for i, n in enumerate(dp): s.drive[s.pos[n]] = v >> i & 1
            else:
                s.drive[s.pos['DOUT']] = v & 1
        s.lastras, s.lastcas = ras, cas
    def upd_adpt(s, lv):
        if lv.get(20) != 1 or lv.get(10) != 0: return
        g = lambda p: 1 if lv.get(p) is None else lv.get(p)
        clk = g(1)
        if s.lastclk == 0 and clk == 1:
            s.latch = sum((g(11 + i) & 1) << i for i in range(8)) & 0x3F
        s.lastclk = clk
        ad = sum((g(3 + i) & 1) << i for i in range(7)) | (s.latch << 7)
        if fault.startswith('alias:'):
            ad &= ~(1 << int(fault[6:]))
        ad &= (1 << cfg['abits']) - 1
        oe, we = g(2), g(19)
        if we == 0:
            v = sum((g(11 + i) & 1) << i for i in range(8))
            s.wrval(ad, v)
        elif oe == 0:
            v = s.rdval(ad)
            for i in range(8): s.drive[11 + i] = v >> i & 1
    # para o adaptador dbits = 8
if cfg['kind'] == 'adpt': cfg['dbits'] = 8
chip = Mem()

lvcache = {}
def recompute():
    lv = {}
    for s in range(1, 21):
        k = kof(s)
        if k and regs[k[0]]['ddr'] >> k[1] & 1: lv[s] = regs[k[0]]['dat'] >> k[1] & 1
        else: lv[s] = None
    for s, v in power_levels().items():
        if lv[s] is not None and lv[s] != v: stats['conflict'] += 1; cpos['pwr%d' % s] += 1
        lv[s] = v
    chip.update(lv)
    for s, v in chip.drive.items():
        if lv[s] is None: lv[s] = v
        elif lv[s] != v: stats['conflict'] += 1; cpos['chip%d' % s] += 1
    lvcache.clear(); lvcache.update(lv)

def eff(s):
    v = lvcache.get(s)
    if v is None:
        k = kof(s)
        if k and k[0] in (0, 2): return 1
        if regs[2]['dat'] & 0x80 == 0: return 1
        return None
    return v

def wr(addr, v):
    off = addr - base; p, c = off // 2, off % 2
    if c: regs[p]['cr'] = v
    elif regs[p]['cr'] & 4: regs[p]['dat'] = v
    else: regs[p]['ddr'] = v
    if p in (0, 1, 2, 3): recompute()

def rd(addr):
    off = addr - base; p, c = off // 2, off % 2
    if c: return regs[p]['cr']
    r = regs[p]
    if not r['cr'] & 4: return r['ddr']
    val = 0
    for b in range(8):
        if r['ddr'] >> b & 1: val |= (r['dat'] >> b & 1) << b
        else:
            s = {0: 3 + b, 1: 11 + b, 2: ([1, 2, 19][b] if b < 3 else None)}.get(p)
            if s is None: continue
            v = eff(s)
            if v is None: v = 1 if not (regs[2]['dat'] & 0x40) else 0
            val |= v << b
    return val

def comp(addr):
    pe, pf = regs[4]['dat'], regs[5]['dat']
    sel = [3 + i for i in range(8) if pe >> i & 1] + [11 + i for i in range(8) if pf >> i & 1]
    if len(sel) != 1: return 0
    return {1: 1, 0: 2, None: 0}[eff(sel[0])]

mem.subscribe_to_write(range(base, base + 12), wr)
mem.subscribe_to_read(range(base, base + 12), rd)
mem.subscribe_to_read([0xC000 + SLOT * 0x100], comp)
mem.subscribe_to_read([0xC000, 0xC030], lambda x: 0)

# reduz linhas da DRAM (acelera) no descritor
chipidx = ['2114', '2147', '4164', '41256', '4416', '4464', '6116', '6264'].index(a.chip)
if a.rows:
    # acha desctab: procura o texto da primeira palavra... usa simbolos do listing
    pass

screen = [[' '] * 40 for _ in range(24)]
cur = [0, 0]
def put(ch):
    if ch == '\n':
        cur[0] = 0; cur[1] = min(cur[1] + 1, 23); return
    if cur[0] < 40: screen[cur[1]][cur[0]] = ch
    cur[0] += 1
    if cur[0] >= 40: cur[0] = 0; cur[1] = min(cur[1] + 1, 23)
def rts():
    lo = mem[0x100 + ((m.sp + 1) & 0xFF)]; hi = mem[0x100 + ((m.sp + 2) & 0xFF)]
    m.sp = (m.sp + 2) & 0xFF; m.pc = ((hi << 8) | lo) + 1
def dump():
    print('\n'.join(''.join(r).rstrip() for r in screen))
    print('-' * 40)

keys = list(b'4' + bytes([ord('1') + chipidx]) + b' ')
m.pc = 0x800; m.sp = 0xFF
lbl = {}
if a.lbl:
    for ln in open(a.lbl):
        t = ln.split()
        if len(t) >= 3: lbl[t[2].lstrip('.')] = int(t[1], 16)
for step in range(a.maxsteps):
    pc = m.pc
    cyc[0] = m.processorCycles
    if pc == 0xFDED: put(chr(m.a & 0x7F) if (m.a & 0x7F) != 13 else '\n'); rts(); continue
    if pc == 0xFD8E: put('\n'); rts(); continue
    if pc == 0xFDDA: put('%X' % (m.a >> 4)); put('%X' % (m.a & 15)); rts(); continue
    if pc == 0xFC58:
        for r in screen: r[:] = [' '] * 40
        cur[:] = [0, 0]; rts(); continue
    if pc == 0xFC22: cur[1] = mem[0x25]; cur[0] = mem[0x24]; rts(); continue
    if pc in (0xFCA8, 0xFF3A): rts(); continue
    if pc == 0xFD0C:
        if not keys: break
        k = keys.pop(0)
        if k == ord(' '):
            dump()
        m.a = k | 0x80; rts(); continue
    if pc == 0xB800: put('[MENU]'); break
    if a.rows and pc == lbl.get('drinit'): mem[lbl['nrow']] = a.rows
    if pc >= 0xC000: print(f"!! PC ${pc:04X}"); break
    m.step()
dump()
print('ciclos', m.processorCycles, '(%.1f s a 1,023 MHz)' % (m.processorCycles / 1.023e6))
print('RAS baixo max', stats['ras_max'], stats.get('ras_pc'), 'ciclos; conflitos', stats['conflict'], '; linhas perdidas por retencao', stats['decay'])
print('PD final', hex(regs[3]['dat']), dict(cpos))
