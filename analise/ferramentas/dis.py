#!/usr/bin/env python3
"""Desmonta binário 6502 com py65. uso: dis.py arquivo base [ini fim]"""
import sys
from py65.devices.mpu65c02 import MPU
from py65.disassembler import Disassembler

def load(fn, base):
    m = MPU()
    d = open(fn, 'rb').read()
    for i, b in enumerate(d):
        m.memory[base+i] = b
    return m, d

def dis(fn, base, ini=None, fim=None):
    m, d = load(fn, base)
    ds = Disassembler(m)
    pc = ini if ini is not None else base
    end = fim if fim is not None else base + len(d)
    out = []
    while pc < end:
        n, txt = ds.instruction_at(pc)
        raw = ' '.join(f"{m.memory[pc+i]:02X}" for i in range(n))
        out.append(f"{pc:04X}  {raw:9s} {txt}")
        pc += n
    return '\n'.join(out)

if __name__ == '__main__':
    fn = sys.argv[1]; base = int(sys.argv[2], 16)
    ini = int(sys.argv[3], 16) if len(sys.argv) > 3 else None
    fim = int(sys.argv[4], 16) if len(sys.argv) > 4 else None
    print(dis(fn, base, ini, fim))
