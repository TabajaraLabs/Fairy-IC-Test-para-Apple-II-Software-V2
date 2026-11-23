#!/usr/bin/env python3
"""Simulação completa: ICTESTER.SYSTEM (carregador) + programa da Fairy + ELHOOK +
biblioteca + modelo da placa (confirmado pelo ICTDIAG) + modelo funcional do CI.
uso: simfull.py DIR chip "teclas"   (teclas: \\x83 = Ctrl-C, \\x93 = Ctrl-S)
"""
import sys, os
from py65.devices.mpu6502 import MPU
from py65.memory import ObservableMemory
sys.path.insert(0, os.path.dirname(__file__))

D, chip, keystr = sys.argv[1], sys.argv[2], sys.argv[3].encode('latin-1').decode('unicode_escape')
keys = [ord(c) for c in keystr]
SLOT = 4
mem = ObservableMemory(); m = MPU(memory=mem)
sysf = open(f'{D}/ICTESTER.SYSTEM', 'rb').read()
for i, b in enumerate(sysf): mem[0x2000 + i] = b
files = {n.encode(): open(f'{D}/{n}', 'rb').read() for n in os.listdir(D) if '.' in n and not n.endswith('.po')}

# ---------------- placa
base = 0xC084 + SLOT * 16
regs = {p: {'ddr': 0, 'dat': 0, 'cr': 0} for p in range(6)}
PDMAP = {0x87: (17, 10), 0x47: (18, 10), 0xC7: (20, 10), 0xC9: (8, 13), 0xD2: (7, 14), 0xE2: (7, 15)}
def kof(s):
    if 3 <= s <= 10: return (0, s - 3)
    if 11 <= s <= 18: return (1, s - 11)
    return {1: (2, 0), 2: (2, 1), 19: (2, 2)}.get(s)
def sockof(p, pin):
    n = p // 2
    return pin + (10 - n) if pin <= n else 10 + (pin - n)
class NAND:
    pins = 14; vcc = 14; gnd = 7
    G = [(1, 2, 3), (4, 5, 6), (9, 10, 8), (12, 13, 11)]
    def out(s, i): return {y: (0 if (i[a] and i[b]) else 1) for a, b, y in s.G}
class NAND4011(NAND):
    G = [(1, 2, 3), (5, 6, 4), (8, 9, 10), (12, 13, 11)]
class NOR(NAND):   # 7402
    G = [(2, 3, 1), (5, 6, 4), (8, 9, 10), (11, 12, 13)]
    def out(s, i): return {y: (0 if (i[a] or i[b]) else 1) for a, b, y in s.G}
class NOR00(NAND):   # 7436: NOR com pinagem do 7400
    def out(s, i): return {y: (0 if (i[a] or i[b]) else 1) for a, b, y in s.G}
CH = {'7400': NAND, '4011': NAND4011, '7402': NOR, '7436': NOR00}
ic = CH[chip]() if chip in CH else None
def levels():
    vs, gs = PDMAP.get(regs[3]['dat'], (None, None))
    lv = {}
    for s in range(1, 21):
        k = kof(s); drv = None
        if k and regs[k[0]]['ddr'] >> k[1] & 1: drv = regs[k[0]]['dat'] >> k[1] & 1
        lv[s] = drv
    if gs: lv[gs] = 0
    if vs: lv[vs] = 1
    if ic and lv.get(sockof(ic.pins, ic.vcc)) == 1 and lv.get(sockof(ic.pins, ic.gnd)) == 0:
        inp = {pin: (lv[sockof(ic.pins, pin)] if lv[sockof(ic.pins, pin)] is not None else 1) for pin in range(1, ic.pins + 1)}
        for pin, v in ic.out(inp).items():
            s = sockof(ic.pins, pin); k = kof(s)
            if k and regs[k[0]]['ddr'] >> k[1] & 1: continue
            lv[s] = v
    return lv
def eff(s):
    v = levels()[s]
    if v is None:
        k = kof(s)
        if k and k[0] in (0, 2): return 1
        if regs[2]['dat'] & 0x80 == 0: return 1
        return None
    return v
def wr(a, v):
    off = a - base; p, c = off // 2, off % 2
    if c: regs[p]['cr'] = v
    elif regs[p]['cr'] & 4: regs[p]['dat'] = v
    else: regs[p]['ddr'] = v
def rd(a):
    off = a - base; p, c = off // 2, off % 2
    if c: return regs[p]['cr']
    r = regs[p]
    if not r['cr'] & 4: return r['ddr']
    val = 0
    for b in range(8):
        if r['ddr'] >> b & 1: val |= (r['dat'] >> b & 1) << b
        elif p < 3:
            s = {0: 3 + b, 1: 11 + b, 2: ([1, 2, 19] + [None] * 5)[b]}[p]
            if s is None: continue
            v = eff(s)
            if v is None: v = 0 if regs[2]['dat'] & 0x40 else 1
            val |= v << b
    return val
def comp(a):
    pe, pf, pc = regs[4]['dat'], regs[5]['dat'], regs[2]['dat']
    sel = [3 + i for i in range(8) if pe >> i & 1] + [11 + i for i in range(8) if pf >> i & 1]
    sel += [s for s, b in ((1, 8), (2, 16), (19, 32)) if pc & b]
    if len(sel) != 1: return 0
    return {1: 1, 0: 2, None: 0}[eff(sel[0])]
mem.subscribe_to_write(range(base, base + 12), wr)
mem.subscribe_to_read(range(base, base + 12), rd)
mem.subscribe_to_read([0xC000 + SLOT * 0x100], comp)

# ---------------- tela
SCR = [[' '] * 40 for _ in range(24)]
def rowaddr(r): return 0x400 + (r & 7) * 0x80 + (r >> 3) * 0x28
def putc(c):
    ch, cv = mem[0x24], mem[0x25]
    c &= 0x7F
    if c == 13: mem[0x24] = 0; mem[0x25] = min(cv + 1, 23); return
    if c < 32: return
    if cv < 24 and ch < 40:
        SCR[cv][ch] = chr(c); mem[rowaddr(cv) + ch] = c | 0x80
    ch += 1
    if ch >= 40: ch = 0; mem[0x25] = min(cv + 1, 23)
    mem[0x24] = ch
def home():
    for r in range(24):
        SCR[r] = [' '] * 40
        for c in range(40): mem[rowaddr(r) + c] = 0xA0
    mem[0x24] = 0; mem[0x25] = 0
def rts():
    lo = mem[0x100 + ((m.sp + 1) & 0xFF)]; hi = mem[0x100 + ((m.sp + 2) & 0xFF)]
    m.sp = (m.sp + 2) & 0xFF; m.pc = ((hi << 8) | lo) + 1
def w(a): return mem[a] | mem[a + 1] << 8
opened = {}
log = []
m.pc = 0x2000; m.sp = 0xFF
mem[0x280] = 0
for step in range(60_000_000):
    pc = m.pc
    if pc in (0xFDED, 0xFDF0): putc(m.a); rts(); continue
    if pc == 0xFD8E: putc(0x8D); rts(); continue
    if pc == 0xFDDA:
        for c in f"{m.a:02X}": putc(ord(c))
        rts(); continue
    if pc == 0xFC58: home(); rts(); continue
    if pc in (0xFE84, 0xFB2F, 0xFE93, 0xFE89, 0xFF3A, 0xFE80, 0xFC22, 0xFBDD, 0xFCA8): rts(); continue
    if pc in (0xFD0C, 0xFD35):
        caller = w(0x100 + ((m.sp + 1) & 0xFF)) - 2
        if not keys: log.append(f"[espera tecla em ${caller:04X}]"); break
        log.append(f"tecla {keys[0]:02X}@${caller:04X}")
        m.a = keys.pop(0) | 0x80; rts(); continue
    if pc == 0xBF00:
        ret = w(0x100 + ((m.sp + 1) & 0xFF)); cmd = mem[ret + 1]; parm = w(ret + 2); err = 0
        if cmd == 0xC7: mem[w(parm + 1)] = 0
        elif cmd == 0xC8:
            pa = w(parm + 1); name = bytes(mem[pa + 1:pa + 1 + mem[pa]])
            if name in files: opened[1] = files[name]; mem[parm + 5] = 1
            else: err = 0x46
            log.append(f"OPEN {name.decode()} {'ok' if not err else 'ERRO'}")
        elif cmd == 0xCA:
            data = opened[1]; dst = w(parm + 2); n = min(w(parm + 4), len(data))
            for i in range(n): mem[dst + i] = data[i]
            log.append(f"READ ${dst:04X}-${dst + n - 1:04X}")
        rts(); m.pc = ret + 4; m.a = err; m.p = (m.p | 1) if err else (m.p & ~1); continue
    if pc >= 0xC000 or mem[pc] == 0:
        log.append(f"!! PC ${pc:04X}"); break
    m.step()
print(' | '.join(log))
print('+' + '-' * 40 + '+')
for r in SCR: print('|' + ''.join(r) + '|')
print('+' + '-' * 40 + '+')
print(f"$DA=${mem[0xDA]:02X} PD=${regs[3]['dat']:02X} CICLOS={m.processorCycles} (~{m.processorCycles/1.023e6:.1f} s)")
import re as _re
lst=open('/home/claude/ict/src/elhook.lst').read()
def sym(n):
    mm=_re.search(r'^([0-9A-F]{6}).{0,40}?\b'+n+r':',lst,_re.M)
    return int(mm.group(1),16) if mm else None
k=sym('key'); kl=sym('keylen')
if k: print('key=',bytes(mem[k:k+mem[kl]]),'keylen',mem[kl])
print('campo prefixo/dígitos HMOS $0F45..$0F49:',bytes(x&0x7f for x in mem[0x0F45:0x0F4A]))
print('lib $4F00:',bytes(mem[0x4F00:0x4F10]))
