#!/usr/bin/env python3
"""Extrai a lista de CIs suportados (despachantes por $0F4E/$0F4D) de um binário do IC TESTER."""
import sys, re

def load(fn):
    d = open(fn, 'rb').read()
    m = bytearray(0x10000); m[0x800:0x800+len(d)] = d
    return m

def chain(m, pc, var):
    """Segue LDA var / CMP #n / BNE +3 / JMP h ... ; retorna [(n,h)], fallback"""
    out = []
    assert m[pc] == 0xAD and m[pc+1] | m[pc+2] << 8 == var, hex(pc)
    pc += 3
    while True:
        if m[pc] == 0xD0 and m[pc+1] == 0x03 and m[pc+2] == 0x4C:
            out.append((0, m[pc+3] | m[pc+4] << 8)); pc += 5
        elif m[pc] == 0xC9 and m[pc+2] == 0xD0 and m[pc+3] == 0x03 and m[pc+4] == 0x4C:
            out.append((m[pc+1], m[pc+5] | m[pc+6] << 8)); pc += 7
        elif m[pc] == 0x4C:
            return out, m[pc+1] | m[pc+2] << 8
        else:
            return out, None

def find_vars(m):
    """acha (var_hi, var_lo): cadeia cujos alvos começam com LDA de outra variavel com cadeia"""
    from collections import Counter
    c = Counter()
    for i in range(0x800, 0x5000):
        if m[i] == 0xAD and m[i+3] in (0xC9, 0xD0) and m[i+4+(1 if m[i+3]==0xC9 else 0)] in (0x03, 0xD0):
            v = m[i+1] | m[i+2] << 8
            try:
                lst, _ = chain(m, i, v)
            except AssertionError:
                continue
            for _, t in lst:
                if m[t] == 0xAD:
                    c[(v, m[t+1] | m[t+2] << 8)] += 1
    return c.most_common(1)[0][0]

def main(fn, force=None):
    m = load(fn)
    VHI, VLO = force if force else find_vars(m)
    print(f"# variaveis: centena=${VHI:04X} dezena/unidade=${VLO:04X}")
    # despachante principal: procura LDA $0F4E seguido de cadeia
    res = {}
    starts = [i for i in range(0x800, 0x5000) if m[i] == 0xAD and (m[i+1] | m[i+2] << 8) == VHI
              and m[i+3] in (0xC9, 0xD0)]
    for s in starts:
        hi, fb = chain(m, s, VHI)
        for h, tgt in hi:
            todo = [tgt]; seen = set()
            while todo:
                t = todo.pop()
                if t in seen or t is None: continue
                seen.add(t)
                if m[t] == 0xAD and (m[t+1] | m[t+2] << 8) == VLO:
                    lo, fb2 = chain(m, t, VLO)
                    for n, hdl in lo:
                        res.setdefault((h, n), hdl)
                    todo.append(fb2)
    return res

if __name__ == '__main__':
    fn, pref = sys.argv[1], sys.argv[2]
    force = (int(sys.argv[3],16), int(sys.argv[4],16)) if len(sys.argv) > 4 else None
    r = main(fn, force)
    nums = sorted(r)
    names = [f"{pref}{h if h else ''}{n:02X}" for h, n in nums]
    print(f"# {fn}: {len(nums)} entradas")
    print(' '.join(names))
