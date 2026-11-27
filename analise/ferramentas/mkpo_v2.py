#!/usr/bin/env python3
"""Cria imagem ProDOS .po (140K, 280 blocos) com arquivos dados.
uso: mkpo.py saida.po VOLNOME arq:tipo:aux [...]"""
import sys, time

BLK = 512
NBLK = 280

def pdate():
    t = time.localtime()
    d = ((t.tm_year - 2000) << 9) | (t.tm_mon << 5) | t.tm_mday  # anos 2000+ (ProDOS 2.5 usa >=40=1940..., ok p/ maioria)
    tm = (t.tm_hour << 8) | t.tm_min
    return bytes([d & 0xFF, d >> 8, tm & 0xFF, tm >> 8])

def main():
    args = sys.argv[1:]
    boot = None
    if '--boot' in args:
        i = args.index('--boot'); boot = args[i+1]; del args[i:i+2]
    out, vol = args[0], args[1].upper()
    files = []
    for a in args[2:]:
        p, t, aux = a.split(':')
        name = p.split('/')[-1].upper()
        files.append((name, int(t, 16), int(aux, 16), open(p, 'rb').read()))
    img = bytearray(NBLK * BLK)
    used = set(range(0, 7))  # boot 0-1, dir 2-5, bitmap 6
    nxt = [7]
    def alloc():
        b = nxt[0]; nxt[0] += 1; used.add(b); return b
    now = pdate()
    entries = []
    for name, ftype, aux, data in files:
        nb = max(1, (len(data) + BLK - 1) // BLK)
        if nb == 1:
            key = alloc(); img[key*BLK:key*BLK+len(data)] = data
            st, blocks = 1, 1
        elif nb <= 256:
            key = alloc(); blocks = 1
            for i in range(nb):
                b = alloc(); blocks += 1
                img[b*BLK:b*BLK+BLK] = data[i*BLK:(i+1)*BLK].ljust(BLK, b'\0')
                img[key*BLK+i] = b & 0xFF; img[key*BLK+256+i] = b >> 8
            st = 2
        else:
            raise SystemExit('arquivo grande demais')
        e = bytearray(39)
        e[0] = (st << 4) | len(name); e[1:1+len(name)] = name.encode()
        e[0x10] = ftype; e[0x11] = key & 0xFF; e[0x12] = key >> 8
        e[0x13] = blocks & 0xFF; e[0x14] = blocks >> 8
        L = len(data); e[0x15] = L & 0xFF; e[0x16] = (L >> 8) & 0xFF; e[0x17] = L >> 16
        e[0x18:0x1C] = now
        e[0x1C] = 0; e[0x1D] = 0; e[0x1E] = 0xE3  # access
        e[0x1F] = aux & 0xFF; e[0x20] = aux >> 8
        e[0x21:0x25] = now
        e[0x25] = 2; e[0x26] = 0  # header pointer
        entries.append(e)
    # diretório do volume: blocos 2..5 encadeados
    for i, b in enumerate(range(2, 6)):
        o = b * BLK
        prev = b - 1 if b > 2 else 0; nx = b + 1 if b < 5 else 0
        img[o:o+2] = bytes([prev, 0]); img[o+2:o+4] = bytes([nx, 0])
    h = bytearray(39)
    h[0] = 0xF0 | len(vol); h[1:1+len(vol)] = vol.encode()
    h[0x18:0x1C] = now; h[0x1E] = 0xC3; h[0x1F] = 39; h[0x20] = 13
    h[0x21] = len(entries); h[0x22] = 0
    h[0x23] = 6; h[0x24] = 0; h[0x25] = NBLK & 0xFF; h[0x26] = NBLK >> 8
    img[2*BLK+4:2*BLK+4+39] = h
    slot = 1
    for e in entries:
        blk, idx = 2 + slot // 13, slot % 13
        o = blk*BLK + 4 + idx*39
        e[0x25] = 2
        img[o:o+39] = e
        slot += 1
    # bitmap: bit=1 livre
    for b in range(NBLK):
        if b not in used:
            img[6*BLK + b//8] |= 0x80 >> (b % 8)
    if boot:  # blocos 0-1 (carregador de boot) copiados de um disco ProDOS oficial
        img[0:2*BLK] = open(boot, 'rb').read()[0:2*BLK]
    open(out, 'wb').write(img)
    print(f"{out}: {len(entries)} arquivos, {len(used)} blocos usados")

main()
