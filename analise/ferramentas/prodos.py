#!/usr/bin/env python3
"""Converte .dsk (ordem DOS) -> .po e lista/extrai arquivos ProDOS."""
import sys, os, struct

# setor fisico ProDOS-order: bloco b = trilha t, meia 0/1 -> setores DOS
DOS2PRO = [0, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 15]
# setor ProDOS lógico p (0..15) corresponde ao setor DOS DOS2PRO_MAP[p]
PRO_TO_DOS = [0, 0xE, 0xD, 0xC, 0xB, 0xA, 0x9, 0x8, 0x7, 0x6, 0x5, 0x4, 0x3, 0x2, 0x1, 0xF]

def dsk_to_po(d):
    out = bytearray(len(d))
    for t in range(35):
        for p in range(16):
            s = PRO_TO_DOS[p]
            out[t*4096 + p*256: t*4096 + p*256 + 256] = d[t*4096 + s*256: t*4096 + s*256 + 256]
    return bytes(out)

def blk(po, n):
    return po[n*512:(n+1)*512]

TYPES = {0xFF: 'SYS', 0x06: 'BIN', 0xFC: 'BAS', 0x04: 'TXT', 0x0F: 'DIR', 0xFA: 'INT', 0xFE: 'REL'}

def read_file(po, storage, key, eof):
    if storage == 1:
        data = blk(po, key)
    elif storage == 2:
        ib = blk(po, key)
        data = b''
        for i in range(256):
            b = ib[i] | (ib[256+i] << 8)
            if b == 0 and len(data) >= eof:
                break
            data += blk(po, b) if b else bytes(512)
    elif storage == 3:
        mb = blk(po, key)
        data = b''
        for j in range(128):
            m = mb[j] | (mb[256+j] << 8)
            if m == 0:
                continue
            ib = blk(po, m)
            for i in range(256):
                b = ib[i] | (ib[256+i] << 8)
                data += blk(po, b) if b else bytes(512)
    else:
        data = b''
    return data[:eof]

def walk_dir(po, keyblock, path, outdir, listing):
    b = keyblock
    first = True
    while b:
        d = blk(po, b)
        nxt = d[2] | (d[3] << 8)
        for e in range(13):
            off = 4 + e*39
            ent = d[off:off+39]
            st = ent[0] >> 4
            nl = ent[0] & 0xF
            if first and e == 0:
                if st in (0xF, 0xE):
                    name = ent[1:1+nl].decode('ascii', 'replace')
                    listing.append(f"# {'VOLUME' if st==0xF else 'SUBDIR'} /{name}")
                continue
            if st == 0:
                continue
            name = ent[1:1+nl].decode('ascii', 'replace')
            ftype = ent[0x10]
            key = ent[0x11] | (ent[0x12] << 8)
            blocks = ent[0x13] | (ent[0x14] << 8)
            eof = ent[0x15] | (ent[0x16] << 8) | (ent[0x17] << 16)
            aux = ent[0x1F] | (ent[0x20] << 8)
            listing.append(f"{path+name:30s} st={st:X} type=${ftype:02X}({TYPES.get(ftype,'?')}) aux=${aux:04X} key={key} blocks={blocks} eof={eof}")
            if st == 0xD:
                walk_dir(po, key, path+name+'/', outdir, listing)
            else:
                data = read_file(po, st, key, eof)
                fn = os.path.join(outdir, (path+name).replace('/', '_') + f"#{ftype:02X}{aux:04X}")
                open(fn, 'wb').write(data)
        first = False
        b = nxt

if __name__ == '__main__':
    src, outdir = sys.argv[1], sys.argv[2]
    os.makedirs(outdir, exist_ok=True)
    d = open(src, 'rb').read()
    po = dsk_to_po(d) if src.lower().endswith('.dsk') else d
    open(os.path.join(outdir, 'disk.po'), 'wb').write(po)
    listing = []
    walk_dir(po, 2, '', outdir, listing)
    print('\n'.join(listing))
    # blocos usados segundo bitmap
    vd = blk(po, 2)
    bm = vd[4+0x23] | (vd[4+0x24] << 8)
    total = vd[4+0x25] | (vd[4+0x26] << 8)
    print(f"bitmap block={bm} total_blocks={total}")
