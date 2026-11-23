#!/usr/bin/env python3
"""Simula ELNEC.ENG + biblioteca com um modelo da placa (confirmado pelo ICTDIAG)
e modelos funcionais de CIs (independentes dos vetores do Elnec).
uso: simeng.py ELNEC.ENG LIB chip comandos...
chips: 7400, 7400bad, 7405, 7474, 4011, vazio
"""
import sys
from py65.devices.mpu6502 import MPU
from py65.memory import ObservableMemory

eng, libf, chip = sys.argv[1], sys.argv[2], sys.argv[3]
cmds = sys.argv[4:]
SLOT = 4
mem = ObservableMemory()
m = MPU(memory=mem)
for i, b in enumerate(open(eng, 'rb').read()): mem[0x800 + i] = b
for i, b in enumerate(open(libf, 'rb').read()): mem[0x2000 + i] = b

base = 0xC084 + SLOT * 16
regs = {p: {'ddr': 0, 'dat': 0, 'cr': 0} for p in range(6)}
PDMAP = {0x87: (17, 10), 0x47: (18, 10), 0xC7: (20, 10), 0xC9: (8, 13), 0xD2: (7, 14), 0xE2: (7, 15)}

def kof(s):  # posição -> (porta, bit)
    if 3 <= s <= 10: return (0, s - 3)
    if 11 <= s <= 18: return (1, s - 11)
    return {1: (2, 0), 2: (2, 1), 19: (2, 2)}.get(s)

def sockof(p, pin):
    n = p // 2
    return pin + (10 - n) if pin <= n else 10 + (pin - n)

# ---- modelos de CI: pinos de entrada, função ----
class Chip:
    pins = 14; vcc = 14; gnd = 7
    def __init__(s): s.state = {}
    def out(s, inp): return {}

class NAND(Chip):
    bad = False
    G = [(1, 2, 3), (4, 5, 6), (9, 10, 8), (12, 13, 11)]
    def out(s, i):
        o = {}
        for n, (a, b, y) in enumerate(s.G):
            v = 0 if (i[a] and i[b]) else 1
            if s.bad and n == 2: v = 1
            o[y] = v
        return o
class NANDbad(NAND): bad = True
class INV_OC(Chip):
    G = [(1, 2), (3, 4), (5, 6), (9, 8), (11, 10), (13, 12)]
    def out(s, i): return {y: (0 if i[a] else None) for a, y in s.G}
class NAND4011(NAND):
    G = [(1, 2, 3), (5, 6, 4), (8, 9, 10), (12, 13, 11)]
class DFF(Chip):  # 7474: 1CLR 1, 1D 2, 1CLK 3, 1PRE 4, 1Q 5, 1/Q 6; 2Q 9, 2/Q 8, 2PRE 10, 2CLK 11, 2D 12, 2CLR 13
    F = [(1, 2, 3, 4, 5, 6), (13, 12, 11, 10, 9, 8)]
    def __init__(s): s.q = [0, 0]; s.lastclk = [1, 1]
    def out(s, i):
        o = {}
        for n, (clr, d, clk, pre, q, nq) in enumerate(s.F):
            if i[clk] and not s.lastclk[n]: s.q[n] = i[d]
            s.lastclk[n] = i[clk]
            if not i[clr] and not i[pre]: o[q] = 1; o[nq] = 1; continue
            if not i[clr]: s.q[n] = 0
            elif not i[pre]: s.q[n] = 1
            o[q] = s.q[n]; o[nq] = 1 - s.q[n]
        return o

CHIPS = {'7400': NAND, '7400bad': NANDbad, '7405': INV_OC, '7474': DFF, '4011': NAND4011}
ic = CHIPS[chip]() if chip in CHIPS else None

def levels():
    """nivel de cada posição 1..20: 1, 0 ou None (meio)"""
    pd = regs[3]['dat']
    vs, gs = PDMAP.get(pd, (None, None))
    lv = {}
    for s in range(1, 21):
        k = kof(s)
        drv = None
        if k:
            r = regs[k[0]]
            if r['ddr'] >> k[1] & 1: drv = r['dat'] >> k[1] & 1
        lv[s] = drv
    if gs: lv[gs] = 0
    if vs: lv[vs] = 1
    if ic:
        p = ic.pins
        powered = lv.get(sockof(p, ic.vcc)) == 1 and lv.get(sockof(p, ic.gnd)) == 0
        if powered:
            inp = {}
            for pin in range(1, p + 1):
                s = sockof(p, pin); v = lv[s]
                if v is None: v = 1 if (kof(s) and kof(s)[0] in (0, 2)) else 1  # TTL solto = 1
                inp[pin] = v
            for pin, v in ic.out(inp).items():
                s = sockof(p, pin)
                k = kof(s)
                if k and regs[k[0]]['ddr'] >> k[1] & 1: continue   # conflito: Apple ganha
                lv[s] = v
    return lv

def eff(s):
    """nivel final com pull-ups: lado PA/PC solto = 1, lado PB solto = meio (None)"""
    v = levels()[s]
    if v is None:
        k = kof(s)
        if k and k[0] in (0, 2): return 1
        if regs[2]['dat'] & 0x80 == 0: return 1   # PC7=0 -> pull-ups
        return None
    return v

def wr(a, v):
    off = a - base; p, c = off // 2, off % 2
    if c: regs[p]['cr'] = v
    elif regs[p]['cr'] & 4: regs[p]['dat'] = v
    else: regs[p]['ddr'] = v
    levels()   # atualiza estado do CI (bordas de clock)

def rd(a):
    off = a - base; p, c = off // 2, off % 2
    if c: return regs[p]['cr']
    r = regs[p]
    if not r['cr'] & 4: return r['ddr']
    val = 0
    for b in range(8):
        if r['ddr'] >> b & 1: val |= (r['dat'] >> b & 1) << b
        else:
            s = {0: 3 + b, 1: 11 + b, 2: [1, 2, 19][b] if b < 3 else None}[p] if p < 3 else None
            if s is None: continue
            v = eff(s)
            if v is None: v = 1 if not (regs[2]['dat'] & 0x40) else 0
            val |= v << b
    return val

def comp(a):
    pe, pf, pc = regs[4]['dat'], regs[5]['dat'], regs[2]['dat']
    sel = [3 + i for i in range(8) if pe >> i & 1] + [11 + i for i in range(8) if pf >> i & 1]
    sel += [s for s, b in ((1, 8), (2, 16), (19, 32)) if pc & b]
    if len(sel) != 1: return 0
    v = eff(sel[0])
    return {1: 1, 0: 2, None: 0}[v]

mem.subscribe_to_write(range(base, base + 12), wr)
mem.subscribe_to_read(range(base, base + 12), rd)
mem.subscribe_to_read([0xC000 + SLOT * 0x100], comp)
mem.subscribe_to_read([0xC000], lambda a: 0)

screen = []
def rts():
    lo = mem[0x100 + ((m.sp + 1) & 0xFF)]; hi = mem[0x100 + ((m.sp + 2) & 0xFF)]
    m.sp = (m.sp + 2) & 0xFF; m.pc = ((hi << 8) | lo) + 1
keys = list(b'4')
m.pc = 0x800; m.sp = 0xFF
for step in range(30_000_000):
    pc = m.pc
    if pc == 0xFDED:
        c = m.a & 0x7F; screen.append('\n' if c == 13 else chr(c)); rts(); continue
    if pc == 0xFD8E: screen.append('\n'); rts(); continue
    if pc == 0xFDDA: screen.append(f"{m.a:02X}"); rts(); continue
    if pc == 0xFD6A:
        if not cmds: break
        t = cmds.pop(0)
        screen.append(chr(mem[0x33] & 0x7F) + t + '\n')
        for i, ch in enumerate(t.encode()): mem[0x200 + i] = ch | 0x80
        mem[0x200 + len(t)] = 0x8D
        m.x = len(t); rts(); continue
    if pc in (0xFC58, 0xFCA8, 0xFF3A): rts(); continue
    if pc == 0xFD0C:
        if not keys: break
        m.a = keys.pop(0) | 0x80; rts(); continue
    if pc == 0x9000: screen.append('[MENU]'); break
    if pc >= 0xC000 or (mem[pc] == 0 and pc < 0x2000):
        print(f"!! PC ${pc:04X}"); break
    m.step()
print(''.join(screen))
print('PD final', hex(regs[3]['dat']))
