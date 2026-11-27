#!/usr/bin/env python3
"""Simula ICTDIAG.SYSTEM com um modelo das 3 PIAs (6821) e do comparador."""
import sys
from py65.devices.mpu6502 import MPU
from py65.memory import ObservableMemory

SLOT = 4
keys = list(b'4' + b'x' + b'x' + b'S' + b'x')
mem = ObservableMemory()
m = MPU(memory=mem)
code = open(sys.argv[1], 'rb').read()
for i, b in enumerate(code):
    mem[0x2000 + i] = b

base = 0xC084 + SLOT * 16
regs = {p: {'ddr': 0, 'dat': 0, 'cr': 0} for p in range(6)}

def wr(addr, val):
    off = addr - base
    p, isc = off // 2, off % 2
    if isc: regs[p]['cr'] = val
    elif regs[p]['cr'] & 4: regs[p]['dat'] = val
    else: regs[p]['ddr'] = val

def rd(addr):
    off = addr - base
    p, isc = off // 2, off % 2
    if isc: return regs[p]['cr']
    r = regs[p]
    if not r['cr'] & 4: return r['ddr']
    return (r['dat'] & r['ddr'])      # entradas lidas como 0 (soquete vazio)

def comp(addr):
    # linha do mux selecionada
    pe, pf, pc = regs[4]['dat'], regs[5]['dat'], regs[2]['dat']
    sel = []
    for i in range(8):
        if pe >> i & 1: sel.append((0, i))
        if pf >> i & 1: sel.append((1, i))
    for i, b in enumerate((0x08, 0x10, 0x20)):
        if pc & b: sel.append((2, i))
    if len(sel) != 1: return 0
    port, bit = sel[0]
    r = regs[port]
    if r['ddr'] >> bit & 1:
        return 2 if r['dat'] >> bit & 1 else 1
    return 0

mem.subscribe_to_write(range(base, base + 12), lambda a, v: wr(a, v))
mem.subscribe_to_read(range(base, base + 12), lambda a: rd(a))
mem.subscribe_to_read([0xC000 + SLOT * 0x100], lambda a: comp(a))

screen = []
def rts():
    lo = mem[0x100 + ((m.sp + 1) & 0xFF)]; hi = mem[0x100 + ((m.sp + 2) & 0xFF)]
    m.sp = (m.sp + 2) & 0xFF; m.pc = ((hi << 8) | lo) + 1

ROM = {0xFC58, 0xFE84, 0xFB2F, 0xFE93, 0xFE89, 0xFCA8}
m.pc = 0x2000; m.sp = 0xFF
for step in range(5_000_000):
    pc = m.pc
    if pc == 0xFDED:
        c = m.a & 0x7F; screen.append('\n' if c == 13 else chr(c)); rts(); continue
    if pc == 0xFD8E: screen.append('\n'); rts(); continue
    if pc == 0xFDDA: screen.append(f"{m.a:02X}"); rts(); continue
    if pc in ROM: rts(); continue
    if pc == 0xFD0C:
        if not keys: break
        m.a = keys.pop(0) | 0x80; rts(); continue
    if pc == 0xBF00: print('[MLI QUIT]'); break
    if pc >= 0xC000 or mem[pc] == 0:
        print(f"!! PC ${pc:04X}"); break
    m.step()
print(''.join(screen))
print('PD final', hex(regs[3]['dat']), 'PE', regs[4]['dat'], 'PF', regs[5]['dat'])
