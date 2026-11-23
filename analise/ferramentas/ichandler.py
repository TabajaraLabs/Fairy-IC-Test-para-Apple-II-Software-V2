#!/usr/bin/env python3
"""Decodifica handlers padrão (tabela) do TEST.2: direções, VCC, vetores."""
import sys
exec(open(sys.path[0]+'/iclist.py').read().split("if __name__")[0])
def table(fn, VHI, VLO):
    m=load(fn); res={}
    for s in [i for i in range(0x800,0x5000) if m[i]==0xAD and (m[i+1]|m[i+2]<<8)==VHI and m[i+3] in (0xC9,0xD0)]:
        hi,_=chain(m,s,VHI)
        for h,t in hi:
            todo=[t];seen=set()
            while todo:
                t=todo.pop()
                if t in seen or t is None: continue
                seen.add(t)
                if m[t]==0xAD and (m[t+1]|m[t+2]<<8)==VLO:
                    lo,fb=chain(m,t,VLO)
                    for n,hd in lo: res.setdefault((h,n),hd)
                    todo.append(fb)
    return m,res
w=lambda m,a:m[a]|m[a+1]<<8
def decode(m,h):
    pc=h; info={'jsr':[],'ldx':[],'ldy':[],'zp':{},'port':[]}
    for _ in range(80):
        op=m[pc]
        if op==0x20: info['jsr'].append(w(m,pc+1)); pc+=3
        elif op==0xAE: info['ldx'].append(w(m,pc+1)); pc+=3
        elif op==0xAC: info['ldy'].append(w(m,pc+1)); pc+=3
        elif op==0xA2: info['ldx'].append(('#',m[pc+1])); pc+=2
        elif op==0xA0: info['ldy'].append(('#',m[pc+1])); pc+=2
        elif op==0xA9:
            v=m[pc+1]
            if m[pc+2]==0x85: info['zp'][m[pc+3]]=v; pc+=4
            elif m[pc+2]==0x9D: info['port'].append((w(m,pc+3),v)); pc+=5
            else: pc+=2
        elif op==0x4C: info['jmp']=w(m,pc+1); break
        elif op==0xAD: pc+=3
        elif op in (0xC9,0xB0,0x90,0xF0,0xD0): pc+=2
        else: info['op?']=(pc,op); break
    return info
