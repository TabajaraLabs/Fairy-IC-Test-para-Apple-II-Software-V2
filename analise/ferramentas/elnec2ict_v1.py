#!/usr/bin/env python3
"""Converte bibliotecas de vetores do Elnec (.lib) para o formato binário do motor
de testes da placa IC TEST CARD (Fairy/Yih-Lung) -- ICTLIB v1.

Soquete: ZIF de 20 posições, CI alinhado pelo GND (posição 10).
  posição s: 3..10 -> PA0..PA7 (índice 0..7)
             11..18 -> PB0..PB7 (índice 8..15)
             1, 2, 19 -> PC0, PC1, PC2 (índice 16..18)
             20 -> só VCC de CI de 20 pinos (sem porta)
Códigos de alimentação PD conhecidos: (VCC, GND) -> código.

Formato do arquivo:
  "ICTL" , versão(1), nº de CIs (2 bytes LE), família (1 byte de tamanho + texto, máx. 12)
  por CI: nlen, nome(ASCII), pinos, PD, nº de vetores (2 bytes LE), vetores * 10 bytes
  vetor: 19 nibbles (índice 0..18; byte k = nib[2k] | nib[2k+1]<<4), último nibble = 0
  nibble: 0=X/solto 1='0' 2='1' 3=L 4=H 5=Z 6=C 7=K 8=G secundário 9=V secundário
"""
import re, sys, struct

PD = {(17, 10): 0x87, (18, 10): 0x47, (20, 10): 0xC7, (8, 13): 0xC9, (7, 14): 0xD2, (7, 15): 0xE2}
CODE = {'X': 0, '0': 1, '1': 2, 'L': 3, 'H': 4, 'Z': 5, 'C': 6, 'K': 7}

def sock(p, pin):
    n = p // 2
    return pin + (10 - n) if pin <= n else 10 + (pin - n)

def idx(s):
    if 3 <= s <= 10: return s - 3
    if 11 <= s <= 18: return s - 3
    return {1: 16, 2: 17, 19: 18}.get(s)   # 20 -> None

def parse(fn):
    t = open(fn, encoding='latin-1').read()
    out = []
    for m in re.finditer(r'^\.(\S+)\s+(\d+)[^\n]*\n((?:(?!\.)[^\n]*\n)*)', t, re.M):
        vec = []
        for l in m.group(3).split('\n'):
            l = l.split(';')[0].strip().upper()
            if not l: continue
            l = re.sub(r'^V\d{3}\s*', '', l).replace(' ', '')
            vec.append(l)
        out.append((m.group(1).upper(), int(m.group(2)), vec))
    return out

def convert(dev):
    name, p, vecs = dev
    if p > 20: return None, 'mais de 20 pinos'
    if any(len(v) != p for v in vecs): return None, 'vetor com tamanho errado'
    G = sorted({sock(p, i + 1) for v in vecs for i, c in enumerate(v) if c == 'G'})
    V = sorted({sock(p, i + 1) for v in vecs for i, c in enumerate(v) if c == 'V'})
    prim = None
    for vc in V:
        for gg in ([10] if 10 in G else []) + G:
            if (vc, gg) in PD: prim = (vc, gg); break
        if prim: break
    if not prim:
        # como o original faz com o 4049/4050: usa um codigo cujo VCC cai num pino
        # sem uso (NC) e liga o VCC do CI pela porta (nivel 1, 'V' secundario)
        used = {sock(p, i + 1) for v in vecs for i, c in enumerate(v) if c != 'X'}
        for (vc, gg), code in PD.items():
            if gg in G and vc not in used:       # VCC do codigo cai num pino sem uso
                prim = (vc, gg); break
        if not prim: return None, f'alimentacao sem codigo (V{V} G{G})'
    rec = bytearray()
    nm = name.encode()[:8]
    if len(vecs) > 2000: return None, 'vetores demais'
    rec += bytes([len(nm)]) + nm + bytes([p, PD[prim], len(vecs) & 0xFF, len(vecs) >> 8])
    for v in vecs:
        nib = [0] * 20
        for i, c in enumerate(v):
            s = sock(p, i + 1)
            if s in prim: continue                     # alimentação primária: via PD
            k = idx(s)
            if c == 'G': code = 8
            elif c == 'V': code = 9
            else: code = CODE.get(c)
            if code is None: return None, f'caractere {c!r}'
            if k is None:
                if code in (0,): continue
                return None, f'pino {i+1} na posicao {s} sem porta'
            nib[k] = code
        rec += bytes(nib[2 * j] | nib[2 * j + 1] << 4 for j in range(10))
    return rec, None

def main(src, dst, fam):
    devs = parse(src)
    body = bytearray(); n = 0; skipped = []
    for d in devs:
        rec, err = convert(d)
        if err: skipped.append(f'{d[0]}: {err}'); continue
        body += rec; n += 1
    fb = fam.encode()[:12]
    data = b'ICTL' + bytes([1]) + struct.pack('<H', n) + bytes([len(fb)]) + fb + body + b'\x00'
    open(dst, 'wb').write(data)
    print(f'{src} -> {dst}: {n} CIs, {len(data)} bytes; ignorados {len(skipped)}')
    for s in skipped: print('   -', s)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3])
