#!/usr/bin/env python3
"""Destokenizador Applesoft (corpo sem os 2 bytes de comprimento). Base $0801."""
import sys
TOK = ["END","FOR","NEXT","DATA","INPUT","DEL","DIM","READ","GR","TEXT","PR#","IN#","CALL","PLOT","HLIN","VLIN",
"HGR2","HGR","HCOLOR=","HPLOT","DRAW","XDRAW","HTAB","HOME","ROT=","SCALE=","SHLOAD","TRACE","NOTRACE","NORMAL","INVERSE","FLASH",
"COLOR=","POP","VTAB","HIMEM:","LOMEM:","ONERR","RESUME","RECALL","STORE","SPEED=","LET","GOTO","RUN","IF",
"RESTORE","&","GOSUB","RETURN","REM","STOP","ON","WAIT","LOAD","SAVE","DEF","POKE","PRINT","CONT","LIST","CLEAR",
"GET","NEW","TAB(","TO","FN","SPC(","THEN","AT","NOT","STEP","+","-","*","/","^","AND",
"OR",">","=","<","SGN","INT","ABS","USR","FRE","SCRN(","PDL","POS","SQR","RND","LOG","EXP",
"COS","SIN","TAN","ATN","PEEK","LEN","STR$","VAL","ASC","CHR$","LEFT$","RIGHT$","MID$"]

def ch(c):
    if c < 32:
        return f"<^{chr(c+64)}>"
    return chr(c)

def detok(b, base=0x801):
    out = []
    p = 0
    while p + 4 <= len(b):
        nxt = b[p] | b[p+1] << 8
        if nxt == 0:
            break
        ln = b[p+2] | b[p+3] << 8
        p += 4
        s = ''
        while p < len(b) and b[p] != 0:
            c = b[p]
            if c >= 0x80:
                i = c - 0x80
                s += (' ' + TOK[i] + ' ') if i < len(TOK) else f"<${c:02X}>"
            else:
                s += ch(c)
            p += 1
        p += 1
        out.append(f"{ln} {s}")
        # segue ponteiro real (pode haver lixo/escondido)
        realp = nxt - base
        if realp != p:
            out.append(f"   ;; ponteiro aponta ${nxt:04X} (offset {realp}) mas fim fisico em {p}")
            p = realp
    if p < len(b) - 2:
        out.append(f";; {len(b)-p} bytes apos o fim do programa")
    return '\n'.join(out)

if __name__ == '__main__':
    for f in sys.argv[1:]:
        print(f"===== {f}")
        print(detok(open(f, 'rb').read()))
