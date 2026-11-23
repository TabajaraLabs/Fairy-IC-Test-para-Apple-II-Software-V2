#!/usr/bin/env python3
"""Lista e extrai arquivos de imagem DOS 3.3 (.dsk ordem DOS)."""
import sys, os

def sec(d, t, s):
    o = t*4096 + s*256
    return d[o:o+256]

TYP = {0: 'T', 1: 'I', 2: 'A', 4: 'B', 8: 'S', 0x10: 'R', 0x20: 'a', 0x40: 'b'}

def main(src, outdir):
    d = open(src, 'rb').read()
    os.makedirs(outdir, exist_ok=True)
    v = sec(d, 17, 0)
    print(f"VTOC: cat T{v[1]:02X} S{v[2]:02X} DOS{v[3]} vol {v[6]}")
    print("bitmap livre por trilha:")
    for t in range(35):
        b = v[0x38+t*4:0x38+t*4+2]
        print(f"  T{t:02X}: {b[0]:02X}{b[1]:02X}", end='\n' if t % 7 == 6 else '')
    t, s = v[1], v[2]
    while t:
        c = sec(d, t, s)
        for e in range(7):
            ent = c[0x0B+e*35:0x0B+e*35+35]
            if ent[0] in (0, 0xFF):
                continue
            ft, fs = ent[0], ent[1]
            typ = ent[2]
            name = bytes(x & 0x7F for x in ent[3:33]).decode().rstrip()
            ln = ent[33] | (ent[34] << 8)
            # le T/S list
            data = b''
            tsl = []
            tt, ss = ft, fs
            while tt:
                ts = sec(d, tt, ss)
                for i in range(122):
                    a, b2 = ts[0x0C+i*2], ts[0x0D+i*2]
                    if a == 0 and b2 == 0:
                        continue
                    tsl.append((a, b2))
                    data += sec(d, a, b2)
                tt, ss = ts[1], ts[2]
            lock = '*' if typ & 0x80 else ' '
            info = ''
            if typ & 0x7F == 4 and len(data) >= 4:
                addr = data[0] | data[1] << 8
                blen = data[2] | data[3] << 8
                info = f"addr=${addr:04X} len=${blen:04X}"
                body = data[4:4+blen]
            elif typ & 0x7F in (1, 2) and len(data) >= 2:
                blen = data[0] | data[1] << 8
                info = f"len=${blen:04X}"
                body = data[2:2+blen]
            else:
                body = data
            print(f"{lock}{TYP.get(typ & 0x7F,'?')} {ln:03d} {name:30s} TS=T{ft:02X}S{fs:02X} {info} secs={tsl[:3]}...")
            safe = ''.join(ch if ch.isalnum() or ch in '.-_' else '_' for ch in name)
            open(os.path.join(outdir, f"{safe}.{TYP.get(typ & 0x7F,'X')}"), 'wb').write(body)
        t, s = c[1], c[2]

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
