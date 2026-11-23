#!/usr/bin/env python3
"""Simulador mínimo: roda IC.TESTER.SYSTEM com MLI e ROM interceptados."""
import sys
from py65.devices.mpu6502 import MPU

files = {b'TEST.2': open('out/TEST.2','rb').read(),
         b'CMOS.2': open('out/CMOS.2','rb').read(),
         b'HMOS.2': open('out/HMOS.2','rb').read()}
keys = list(sys.argv[1].encode()) if len(sys.argv) > 1 else list(b'A1 ')
m = MPU()
mem = m.memory
sysf = open('out/ICTESTER.SYSTEM','rb').read()
mem[0x2000:0x2000+len(sysf)] = list(sysf)
mem[0x280] = 0  # sem caminho
screen = []
io = []
opened = {}
prefix = b''
ROMRTS = {0xFC58:'HOME',0xFE84:'SETNORM',0xFB2F:'INIT',0xFE93:'SETVID',0xFE89:'SETKBD',
          0xFF3A:'BELL',0xFE80:'SETINV',0xFC22:'VTAB',0xFBDD:'BELL1',0xFD8E:'CROUT'}
def rts():
    lo = m.memory[0x100 + ((m.sp+1)&0xFF)]; hi = m.memory[0x100 + ((m.sp+2)&0xFF)]
    m.sp = (m.sp+2)&0xFF
    m.pc = ((hi<<8)|lo) + 1
def w(a): return mem[a] | mem[a+1]<<8
m.pc = 0x2000
m.sp = 0xFF
steps = 0
jumped = False
while steps < 3_000_000:
    pc = m.pc
    if pc == 0x0800 and not jumped:
        jumped = True; screen.append('\n[[JMP $0800]]\n')
    if pc in (0xFDED, 0xFDF0):
        c = m.a & 0x7F; screen.append('\n' if c == 13 else chr(c) if c >= 32 else ''); rts(); continue
    if pc == 0xFDDA:
        screen.append(f"{m.a:02X}"); rts(); continue
    if pc in ROMRTS:
        if pc == 0xFD8E: screen.append('\n')
        rts(); continue
    if pc in (0xFD0C, 0xFD35):
        if not keys:
            break
        m.a = keys.pop(0) | 0x80; screen.append(f"<{chr(m.a&0x7f)}>"); rts(); continue
    if pc == 0xBF00:
        ret = w(0x100 + ((m.sp+1)&0xFF))
        cmd = mem[ret+1]; parm = w(ret+2)
        err = 0
        if cmd == 0xC7:  # GET_PREFIX
            mem[w(parm+1)] = 0
        elif cmd == 0xC8:
            pa = w(parm+1); name = bytes(mem[pa+1:pa+1+mem[pa]])
            if name in files:
                opened[1] = files[name]; mem[parm+5] = 1
            else: err = 0x46
            io.append(f"OPEN {name} buf=${w(parm+3):04X} err={err:02X}")
        elif cmd == 0xCA:
            data = opened[mem[parm+1]]; dst = w(parm+2); req = w(parm+4)
            n = min(req, len(data)); mem[dst:dst+n] = list(data[:n])
            mem[parm+6] = n & 0xFF; mem[parm+7] = n >> 8
            io.append(f"READ -> ${dst:04X} len=${n:04X} req=${req:04X}")
        elif cmd == 0xCC:
            io.append("CLOSE")
        else:
            io.append(f"MLI {cmd:02X}")
        # retorno: pula 3 bytes após JSR
        rts(); m.pc = ret + 4
        m.a = err
        m.p = (m.p | 1) if err else (m.p & ~1)
        continue
    if 0xC000 <= pc:
        print(f"!! PC em ${pc:04X} (ROM nao tratada)"); break
    if mem[pc] == 0x00:
        print(f"!! BRK em ${pc:04X}"); break
    m.step(); steps += 1
print('\n'.join(io))
print(''.join(screen))
print(f"PC final ${m.pc:04X} passos={steps}")
