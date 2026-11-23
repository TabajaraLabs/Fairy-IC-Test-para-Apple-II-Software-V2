; =====================================================================
; RAMTEST.ENG v1 - teste de memorias RAM na placa IC TEST CARD
; (Fairy / Yih-Lung 1984) - "VERSION 2.0 EXPANDED BY TABAJARA LABS"
;
; Carregado pelo ICTESTER.SYSTEM em $0800 (opcao D). Volta ao menu: JMP $B800.
; Usa $3000-$377F para tabelas de imagens de porta (planares).
;
; Alimentacao (bancada 2026-11-20): PD = 8 chaves independentes
;   b0/b1/b6/b7 = VCC nas posicoes 7/8/17/18 (ativas em 0)
;   b2/b3/b4/b5 = GND nas posicoes 10/13/14/15 (ativas em 1)
;   posicao 20 = VCC fixo
; Indice k das linhas: 0-7 = PA0-7 (pos 3-10), 8-15 = PB0-7 (pos 11-18),
;   16 = PC0 (pos 1), 17 = PC1 (pos 2), 18 = PC2 (pos 19)
;
; Memorias:
;   2114, 2147        normal, encostada embaixo, jumper ZIF 19-20, PD $C7
;   4164, 41256       GIRADA 180 graus, encostada embaixo, PD $47
;   4416, 4464        GIRADA 180 graus, encostada embaixo, jumper 19-20, PD $C7
;   6116, 6264        adaptador (latch 74HC574 p/ enderecos altos), PD $C7
;
; Testes:
;   SRAM: xadrez + xadrez invertido em todos os enderecos, depois teste das
;         linhas de endereco (bits "andando", detecta linha presa/em curto).
;   DRAM: por linha (row): xadrez + invertido nas colunas da linha (o proprio
;         acesso as colunas faz o refresh da linha); depois teste das linhas
;         de endereco de linha (row) e de coluna.
; =====================================================================

MENU    = $B800
HOME    = $FC58
COUT    = $FDED
CROUT   = $FD8E
RDKEY   = $FD0C
PRBYTE  = $FDDA
WAIT    = $FCA8
BELL    = $FF3A
VTAB    = $FC22
CH      = $24
CV      = $25

ptr     = $06
tp      = $08
dp      = $EB              ; ponteiro do descritor

T_SRAM  = 0
T_DRAM  = 1
T_ADPT  = 2
F_ROT   = 1
F_JMP   = 2
F_ADP   = 4
NONE    = $FF

; tabelas planares: plano PA na pagina P, PB em P+1, PC em P+2;
; parte alta (valores 0-15) na pagina P+3, deslocamentos +0/+$10/+$20
ROWPG   = $30              ; $3000-$3320
COLPG   = $34              ; $3400-$3720
DIMGA   = $3740            ; imagens de dado (0-15): $3740/$3750/$3760
COLHA   = $3700

        .org $0800

start:  cld
        ldx #$FF
        txs
        jsr HOME
        ldx #<t_slot
        ldy #>t_slot
        jsr print
@k:     jsr RDKEY
        and #$7F
        cmp #$1B
        bne @k1
        jmp MENU
@k1:    cmp #'1'
        bcc @k
        cmp #'8'
        bcs @k
        pha
        ora #$80
        jsr COUT
        pla
        and #$07
        sta slotn
        asl
        asl
        asl
        asl
        sta slot16
        lda slotn
        ora #$C0
        sta cmpadr+2       ; comparador em $Cn00
        jsr hwinit

; ---------------------------------------------------------- menu de memorias
chmenu: jsr hwsafe
        jsr HOME
        ldx #<t_menu
        ldy #>t_menu
        jsr print
@k:     jsr RDKEY
        and #$7F
        cmp #$1B
        bne @k1
        jsr hwsafe
        jmp MENU
@k1:    cmp #'1'
        bcc @k
        cmp #'9'
        bcs @k
        sec
        sbc #'1'
        asl
        tax
        lda desctab,x
        sta dp
        lda desctab+1,x
        sta dp+1
        lda nametab,x
        sta cname
        lda nametab+1,x
        sta cname+1
        jsr diagram
@w:     jsr RDKEY
        and #$7F
        cmp #$1B
        beq chmenu
        cmp #' '
        bne @w
        jsr runtest
        jsr report
        jsr RDKEY
        jmp chmenu

; ---------------------------------------------------------- desenho do ZIF
; Mostra o ZIF visto de cima (posicao 1 em cima a esquerda, 20 em cima a
; direita, 10 embaixo a esquerda = GND) e onde cada pino do chip fica.
diagram:
        jsr HOME
        ldx cname
        ldy cname+1
        jsr print
        jsr CROUT
        ldy #1
        lda (dp),y
        sta pins
        lsr
        sta n
        iny
        lda (dp),y
        sta flags
        and #F_ADP
        beq @zif
        ldx #<t_adp
        ldy #>t_adp
        jsr print
        jmp @tail
@zif:   ldx #<t_ziftop
        ldy #>t_ziftop
        jsr print
        lda #1
        sta row
@r:     lda #' '|$80
        jsr COUT
        lda row
        jsr pr2            ; posicao esquerda
        lda row
        jsr pinat
        sta lpin
        lda #21
        sec
        sbc row
        sta rpos
        jsr pinat
        sta rpin
        lda lpin
        jsr prpinl
        jsr body
        lda rpin
        jsr prpinr
        lda rpos
        jsr pr2            ; posicao direita
        lda row
        cmp #10
        bne @ng
        ldx #<t_gnd
        ldy #>t_gnd
        jsr print
@ng:    lda flags
        and #F_JMP
        beq @nj
        lda rpos
        cmp #20
        bne @n19
        ldx #<t_j20
        ldy #>t_j20
        jsr print
        jmp @nj
@n19:   cmp #19
        bne @nj
        ldx #<t_j19
        ldy #>t_j19
        jsr print
@nj:    jsr CROUT
        inc row
        lda row
        cmp #11
        bne @r
        jsr CROUT
        lda flags
        and #F_ROT
        beq @n
        ldx #<t_rot
        ldy #>t_rot
        jsr print
        jmp @j
@n:     ldx #<t_norm
        ldy #>t_norm
        jsr print
@j:     lda flags
        and #F_JMP
        beq @tail
        ldx #<t_jmp
        ldy #>t_jmp
        jsr print
@tail:  ldx #<t_go
        ldy #>t_go
        jmp print

; corpo do chip numa linha; "()" marca a linha do pino 1 (lado do chanfro)
body:   lda lpin
        bne @occ
        ldx #<t_empty
        ldy #>t_empty
        jmp print
@occ:   cmp #1
        beq @notch
        lda rpin
        cmp #1
        beq @notch
        ldx #<t_body
        ldy #>t_body
        jmp print
@notch: ldx #<t_notch
        ldy #>t_notch
        jmp print

; A = posicao (1..20) -> pino do chip ali (0 = vazio)
pinat:  sta tmp
        lda flags
        and #F_ROT
        bne @rot
        ; normal, encostado embaixo:
        ; esquerda (1-10): pino = s-(10-n); direita (11-20): pino = n+(s-10)
        lda tmp
        cmp #11
        bcs @nr
        lda #10
        sec
        sbc n
        sta tmp2
        lda tmp
        sec
        sbc tmp2
        beq @z
        bcc @z
        rts                ; 1..n
@nr:    sec
        sbc #10
        cmp n
        beq @r1
        bcs @z
@r1:    clc
        adc n
        rts
@rot:   ; girado 180: direita (11-20): pino = s-10 (1..n)
        ;             esquerda (1-10): pino = s+(p-10) (n+1..p)
        lda tmp
        cmp #11
        bcc @rl
        sec
        sbc #10
        cmp n
        beq @ok
        bcs @z
@ok:    rts
@rl:    lda pins
        sec
        sbc #10
        clc
        adc tmp            ; pino candidato
        sta tmp2
        lda n
        cmp tmp2
        bcs @z             ; n >= candidato -> vazio
        lda tmp2
        rts
@z:     lda #0
        rts

; pino a esquerda: " 9=" / "16=" / " --"
prpinl: cmp #0
        bne @p
        ldx #<t_dl
        ldy #>t_dl
        jmp print
@p:     jsr pr2
        lda #'='|$80
        jmp COUT
; pino a direita: "=9 " / "=16" / "-- "
prpinr: cmp #0
        bne @p
        ldx #<t_dr
        ldy #>t_dr
        jmp print
@p:     pha
        lda #'='|$80
        jsr COUT
        pla
        pha
        jsr prdec
        pla
        cmp #10
        bcs @e
        lda #' '|$80
        jsr COUT
@e:     lda #' '|$80
        jmp COUT
; numero com 2 casas (espaco a esquerda)
pr2:    cmp #10
        bcs @t
        pha
        lda #' '|$80
        jsr COUT
        pla
@t:     jmp prdec

; ---------------------------------------------------------- preparacao
; descritor: tipo, pinos, flags, PD, nrow, ncol, dbits, shared,
;            linha[nrow], coluna[ncol], din[dbits], dout[dbits],
;            CS, WE, OE, RAS, CAS, LATCH
setup:  ldy #0
        lda (dp),y
        sta ctype
        ldy #3
        lda (dp),y
        sta pdcode
        iny
        lda (dp),y
        sta nrow
        iny
        lda (dp),y
        sta ncol
        iny
        lda (dp),y
        sta dbits
        iny
        lda (dp),y
        sta shared
        iny
        sty li_row
        tya
        clc
        adc nrow
        sta li_col
        clc
        adc ncol
        sta li_din
        clc
        adc dbits
        sta li_dout
        clc
        adc dbits
        sta li_ctl
        ldx #2
        lda #0
@z:     sta base,x
        sta ddrw,x
        sta ddrr,x
        dex
        bpl @z
        ; enderecos: sempre saida
        lda nrow
        ldy li_row
        jsr markout
        lda ncol
        ldy li_col
        jsr markout
        ; controles: saida; inativos = 1 (o latch fica inativo em 0)
        ldx #0
@c:     stx ci
        txa
        clc
        adc li_ctl
        tay
        lda (dp),y
        cmp #NONE
        bne @cy
        ldx ci
        lda #NONE
        sta ctlp,x
        jmp @cn
@cy:    jsr kmask          ; X = porta, tmask = bit
        txa
        ldx ci
        sta ctlp,x
        lda tmask
        sta ctlm,x
        ldy ctlp,x
        lda ddrw,y
        ora tmask
        sta ddrw,y
        lda ddrr,y
        ora tmask
        sta ddrr,y
        cpx #5
        beq @cn
        lda base,y
        ora tmask
        sta base,y
@cn:    ldx ci
        inx
        cpx #6
        bne @c
        ; dados de escrita: saida na escrita; se forem pinos separados (DIN),
        ; saida sempre
        lda #0
        sta ci
@d:     lda ci
        cmp dbits
        beq @de
        clc
        adc li_din
        tay
        lda (dp),y
        jsr kmask
        lda ddrw,x
        ora tmask
        sta ddrw,x
        lda shared
        bne @dn
        lda ddrr,x
        ora tmask
        sta ddrr,x
@dn:    inc ci
        bne @d
@de:    ; PC: bits 3-7 sempre saida (mux do comparador e PC6/PC7), PC7 = 1
        lda ddrw+2
        ora #$F8
        sta ddrw+2
        lda ddrr+2
        ora #$F8
        sta ddrr+2
        lda base+2
        ora #$80
        sta base+2
        ; mascara do CAS (para gerar a imagem com CAS baixo)
        lda #$FF
        sta cm
        sta cm+1
        sta cm+2
        ldx ctlp+4
        bmi @nc
        lda ctlm+4
        eor #$FF
        sta cm,x
        stx casp
        txa
        asl
        ora slot16
        sta casx
@nc:    ldx ctlp+3         ; RAS
        bmi @nr
        stx rasp
        lda base,x
        sta baser
        txa
        asl
        ora slot16
        sta rasx
@nr:    ; saida de dado para leitura rapida (x1)
        ldy li_dout
        lda (dp),y
        jsr kmask
        stx doutp
        lda tmask
        sta doutm
        ; tabelas
        lda #ROWPG
        sta tbh
        lda li_row
        sta lst
        lda nrow
        sta cnt
        jsr mktab
        lda ncol
        beq @nt
        lda #COLPG
        sta tbh
        lda li_col
        sta lst
        lda ncol
        sta cnt
        jsr mktab
@nt:    jmp mkdimg

; marca A linhas a partir de Y (descritor) como saida (ddrw e ddrr)
markout:
        sta cnt
        sty lst
@l:     lda cnt
        beq @e
        ldy lst
        lda (dp),y
        cmp #NONE
        beq @s
        jsr kmask
        lda ddrw,x
        ora tmask
        sta ddrw,x
        lda ddrr,x
        ora tmask
        sta ddrr,x
@s:     inc lst
        dec cnt
        jmp @l
@e:     rts

; k (A) -> X = porta (0/1/2), tmask = bit
kmask:  cmp #16
        bcs @c
        cmp #8
        bcs @b
        tax
        lda bits,x
        sta tmask
        ldx #0
        rts
@b:     and #7
        tax
        lda bits,x
        sta tmask
        ldx #1
        rts
@c:     sec
        sbc #16
        tax
        lda bits,x
        sta tmask
        ldx #2
        rts

; acumula em acc a imagem do bit "bi" da lista lst (se o bit esta em v)
accbit: lda lst
        clc
        adc bi
        tay
        lda (dp),y
        cmp #NONE
        beq @e
        jsr kmask
        lda acc,x
        ora tmask
        sta acc,x
@e:     rts

; monta tabela planar na pagina tbh a partir da lista lst (cnt linhas)
mktab:  lda #0
        sta v
@lo:    jsr clracc
        sta bi
@lb:    lda bi
        cmp cnt
        bcs @lbe
        cmp #8
        bcs @lbe
        tax
        lda v
        and bits,x
        beq @lbn
        jsr accbit
@lbn:   inc bi
        jmp @lb
@lbe:   lda #0
        sta tp
        lda tbh
        sta tp+1
        ldy v
        lda acc
        sta (tp),y
        inc tp+1
        lda acc+1
        sta (tp),y
        inc tp+1
        lda acc+2
        sta (tp),y
        inc v
        bne @lo
        ; parte alta (bits 8..cnt-1), valores 0..15
@hi:    jsr clracc
        lda #8
        sta bi
@hb:    lda bi
        cmp cnt
        bcs @hbe
        sec
        sbc #8
        tax
        lda v
        and bits,x
        beq @hbn
        jsr accbit
@hbn:   inc bi
        jmp @hb
@hbe:   lda tbh
        clc
        adc #3
        sta tp+1
        lda #0
        sta tp
        jsr sthi
        inc v
        lda v
        cmp #16
        bne @hi
        rts

clracc: lda #0
        sta acc
        sta acc+1
        sta acc+2
        rts

; grava acc em (tp)+v, +v+$10, +v+$20
sthi:   lda v
        tay
        lda acc
        sta (tp),y
        tya
        clc
        adc #$10
        tay
        lda acc+1
        sta (tp),y
        tya
        clc
        adc #$10
        tay
        lda acc+2
        sta (tp),y
        rts

; imagens de dado (valores 0..15) para x1/x4; x8 (adaptador) usa PB direto
mkdimg: lda li_din
        sta lst
        lda #0
        sta v
@l:     jsr clracc
        sta bi
@b:     lda bi
        cmp dbits
        bcs @e
        cmp #4
        bcs @e
        tax
        lda v
        and bits,x
        beq @n
        jsr accbit
@n:     inc bi
        jmp @b
@e:     lda #<DIMGA
        sta tp
        lda #>DIMGA
        sta tp+1
        jsr sthi
        inc v
        lda v
        cmp #16
        bne @l
        rts

; ---------------------------------------------------------- acesso comum
; cur |= tabela(tbh)[vlo] | alta[vhi]
addaddr:
        lda #0
        sta tp
        lda tbh
        sta tp+1
        ldy vlo
        lda (tp),y
        ora cur
        sta cur
        inc tp+1
        lda (tp),y
        ora cur+1
        sta cur+1
        inc tp+1
        lda (tp),y
        ora cur+2
        sta cur+2
        inc tp+1
        ldy vhi
        beq @e
        lda (tp),y
        ora cur
        sta cur
        tya
        clc
        adc #$10
        tay
        lda (tp),y
        ora cur+1
        sta cur+1
        tya
        clc
        adc #$10
        tay
        lda (tp),y
        ora cur+2
        sta cur+2
@e:     rts

; liga (ativo) / desliga o controle Y (0=CS 1=WE 2=OE 3=RAS 4=CAS 5=LATCH)
; ativo: CS/WE/OE/RAS/CAS em 0; LATCH em 1
ctlon:  ldx ctlp,y
        bmi @e
        lda ctlm,y
        cpy #5
        beq @set
@clr:   eor #$FF
        and cur,x
        sta cur,x
@e:     rts
@set:   ora cur,x
        sta cur,x
        rts
ctloff: ldx ctlp,y
        bmi @e
        lda ctlm,y
        cpy #5
        beq @clr2
        ora cur,x
        sta cur,x
@e:     rts
@clr2:  eor #$FF
        and cur,x
        sta cur,x
        rts

basecur:
        lda base
        sta cur
        lda base+1
        sta cur+1
        lda base+2
        sta cur+2
        rts

wrcur:  ldx slot16
        lda cur
        sta $C084,x
        lda cur+1
        sta $C086,x
        lda cur+2
        sta $C088,x
        rts
rdports:
        ldx slot16
        lda $C084,x
        sta rd
        lda $C086,x
        sta rd+1
        lda $C088,x
        sta rd+2
        rts

; DDRs para escrita (A=0) ou leitura (A=1)
setddr: cmp curdir
        beq @e
        sta curdir
        cmp #0
        bne @r
        lda ddrw
        ldy #0
        jsr wrdir
        lda ddrw+1
        ldy #1
        jsr wrdir
        lda ddrw+2
        ldy #2
        jmp wrdir
@r:     lda ddrr
        ldy #0
        jsr wrdir
        lda ddrr+1
        ldy #1
        jsr wrdir
        lda ddrr+2
        ldy #2
        jmp wrdir
@e:     rts

; extrai o dado lido (dout) de rd -> A
getdata:
        lda dbits
        cmp #1
        bne @g
        ldx doutp
        lda rd,x
        and doutm
        beq @0
        lda #1
@0:     rts
@g:     lda #0
        sta acc
        sta bi
@l:     lda bi
        cmp dbits
        bcs @e
        clc
        adc li_dout
        tay
        lda (dp),y
        jsr kmask
        lda rd,x
        and tmask
        beq @n
        ldx bi
        lda bits,x
        ora acc
        sta acc
@n:     inc bi
        bne @l
@e:     lda acc
        rts

; ---------------------------------------------------------- SRAM
; endereco em alo/ahi, dado em wdata
srwrite:
        lda #0
        jsr setddr
        jsr adplatch
        jsr sraddr
        lda ctype
        cmp #T_ADPT
        bne @t
        lda wdata
        ora cur+1
        sta cur+1
        jmp @g
@t:     ldy wdata
        lda DIMGA,y
        ora cur
        sta cur
        lda DIMGA+$10,y
        ora cur+1
        sta cur+1
        lda DIMGA+$20,y
        ora cur+2
        sta cur+2
@g:     ldy #1
        jsr ctlon          ; WE primeiro (saidas do chip nunca ligam)
        jsr wrcur
        ldy #0
        jsr ctlon          ; CS: escrita controlada pelo CS
        jsr wrcur
        ldy #0
        jsr ctloff
        jsr wrcur
        ldy #1
        jsr ctloff
        jmp wrcur
srread: lda #1
        jsr setddr
        jsr adplatch
        jsr sraddr
        ldy #0
        jsr ctlon
        ldy #2
        jsr ctlon          ; OE
        jsr wrcur
        jsr rdports
        ldy #2
        jsr ctloff
        ldy #0
        jsr ctloff
        jsr wrcur
        lda ctype
        cmp #T_ADPT
        beq @x8
        jmp getdata
@x8:    lda rd+1           ; D0-D7 = PB0-PB7
        rts
; cur = base | endereco (adaptador: so os 7 bits baixos vao direto)
sraddr: jsr basecur
        lda #ROWPG
        sta tbh
        lda alo
        ldx ahi
        ldy ctype
        cpy #T_ADPT
        bne @n
        and #$7F
        ldx #0
@n:     sta vlo
        stx vhi
        jmp addaddr
; adaptador: trava A7.. (endereco >> 7) no 74HC574 quando muda
adplatch:
        lda ctype
        cmp #T_ADPT
        bne @e
        lda alo
        asl
        lda ahi
        rol
        cmp latched
        beq @e
        sta latched
        lda curdir
        pha
        lda #0
        jsr setddr         ; PB como saida para o latch
        jsr basecur
        lda latched
        ora cur+1
        sta cur+1
        jsr wrcur
        ldy #5
        jsr ctlon          ; borda de subida do CLK
        jsr wrcur
        ldy #5
        jsr ctloff
        jsr wrcur
        pla
        jsr setddr
@e:     rts

; ---------------------------------------------------------- DRAM
; imagens da linha atual (rlo/rhi) e do modo (dwrite): i1, i2, m3
drrow:  jsr basecur
        lda #ROWPG
        sta tbh
        lda rlo
        sta vlo
        lda rhi
        sta vhi
        jsr addaddr
        ldx #2
@1:     lda cur,x
        sta i1,x
        dex
        bpl @1
        ldy #3
        jsr ctlon          ; RAS
        ldx #2
@2:     lda cur,x
        sta i2,x
        dex
        bpl @2
        ldx rasp
        lda i2,x
        sta i2r
        jsr basecur        ; m3 = base + RAS + modo (sem o endereco de linha)
        ldy #3
        jsr ctlon
        ldy #1             ; escrita: WE
        lda dwrite
        bne @w
        ldy #2             ; leitura: OE (4416/4464)
@w:     jsr ctlon
        ldx #2
@3:     lda cur,x
        sta m3,x
        dex
        bpl @3
        rts

; um ciclo na coluna clo/chi da linha preparada (dado em wdata)
drcyc:  ldy clo
        ldx wdata
        lda m3
        ora $3400,y
        ora DIMGA,x
        sta i3
        lda m3+1
        ora $3500,y
        ora DIMGA+$10,x
        sta i3+1
        lda m3+2
        ora $3600,y
        ora DIMGA+$20,x
        sta i3+2
        lda chi
        beq @n
        lda i3
        ora COLHA+1
        sta i3
        lda i3+1
        ora COLHA+$11
        sta i3+1
        lda i3+2
        ora COLHA+$21
        sta i3+2
@n:     ldx casp
        lda i3,x
        and cm,x
        sta i4c            ; porta do CAS com o CAS baixo
        ; ----- sequencia rapida: RAS fica baixo ~70 us, CAS ~40 us
        ldx slot16
        lda i1
        sta $C084,x
        lda i1+1
        sta $C086,x
        lda i1+2
        sta $C088,x        ; endereco de linha, RAS alto
        ldy rasx
        lda i2r
        sta $C084,y        ; RAS desce (so a porta do RAS muda)
        lda i3
        sta $C084,x
        lda i3+1
        sta $C086,x
        lda i3+2
        sta $C088,x        ; endereco de coluna (+ WE/dado ou OE)
        ldy casx
        lda i4c
        sta $C084,y        ; CAS desce
        lda $C084,x
        sta rd
        lda $C086,x
        sta rd+1
        lda $C088,x
        sta rd+2
        ldy rasx
        lda baser
        sta $C084,y        ; RAS sobe primeiro
        lda base
        sta $C084,x
        lda base+1
        sta $C086,x        ; CAS sobe, WE/OE inativos
        lda base+2
        sta $C088,x
        rts

; ---------------------------------------------------------- acesso generico
; (usado no teste das linhas de endereco)
memwr:  lda ctype
        cmp #T_DRAM
        beq @d
        jmp srwrite
@d:     lda #1
        sta dwrite
        lda #0
        jsr setddr
        jsr drrow
        jmp drcyc
memrd:  lda ctype
        cmp #T_DRAM
        beq @d
        jmp srread
@d:     lda #0
        sta dwrite
        sta wdata
        lda #1
        jsr setddr
        jsr drrow
        jsr drcyc
        jmp getdata

; ---------------------------------------------------------- teste
; result: 0 OK, 1 erro de dado, 2 alimentacao
runtest:
        jsr setup
        lda #$FF
        sta curdir
        sta latched
        lda #0
        sta result
        jsr allin
        lda pdcode
        ldy #3
        jsr wrdat
        lda #$80
        jsr WAIT
        jsr powchk
        bcc @go
        lda #2
        sta result
        jmp @off
@go:    jsr basecur        ; dados primeiro (pinos ainda entradas): controles
        jsr wrcur          ; inativos antes de virarem saidas
        lda #0
        jsr setddr
        lda ctype
        cmp #T_DRAM
        bne @s
        jsr drinit
        jsr drtest
        lda result
        bne @off
        lda #1             ; linhas de endereco de linha (row)
        sta atmode
        lda nrow
        sta alen
        jsr addrtest
        lda result
        bne @off
        lda #2             ; linhas de endereco de coluna
        sta atmode
        lda ncol
        sta alen
        jsr addrtest
        jmp @off
@s:     jsr srtest
        lda result
        bne @off
        lda #0
        sta atmode
        lda nrow
        sta alen
        jsr addrtest
@off:   jsr allin
        lda #$C3
        ldy #3
        jmp wrdat

; GND na posicao 10 deve ler L (linha do comparador PE7)
powchk: lda #7
        sta mux
        jsr readmux
        cmp #2
        bne @bad
        clc
        rts
@bad:   sec
        rts

; ----- SRAM: xadrez e xadrez invertido em todos os enderecos
srtest: lda #0
        sta pass
@p:     jsr progress
        lda #0
        sta alo
        sta ahi
@w:     jsr srpat
        sta wdata
        jsr srwrite
        jsr ainc
        bcc @w
        lda #0
        sta alo
        sta ahi
@r:     jsr srread
        sta got
        jsr srpat
        sta expv
        cmp got
        beq @ok
        jmp fail
@ok:    lda alo
        bne @np
        jsr progress
@np:    jsr ainc
        bcc @r
        inc pass
        lda pass
        cmp #2
        bne @p
        rts

; padrao xadrez: $55 nos enderecos pares, $AA nos impares (passo 2 inverte)
srpat:  lda alo
        and #1
        tax
        lda chk,x
        ldx pass
        beq @m
        eor #$FF
@m:     ldx dbits
        and dmask-1,x
        rts

; avanca alo/ahi; C=1 ao passar de 2^nrow
ainc:   inc alo
        bne @h
        inc ahi
@h:     lda nrow
        ldx alo
        ldy ahi
        jmp lim

; C=1 se o contador X(lo)/Y(hi) chegou a 2^A
lim:    stx vlo
        sty vhi
        cmp #8
        bcs @big
        tax
        lda vhi
        bne @y
        lda vlo
        cmp bits,x
        bcc @n
@y:     sec
        rts
@big:   sec
        sbc #8
        tax
        lda vhi
        cmp bits,x
        bcc @n
        sec
        rts
@n:     clc
        rts

; ----- DRAM
drinit: lda #1             ; 8 ciclos de inicializacao (dados como entrada)
        jsr setddr
        lda #0
        sta rlo
        sta rhi
        sta clo
        sta chi
        sta dwrite
        sta wdata
        jsr drrow
        ldx #8
@l:     txa
        pha
        jsr drcyc
        pla
        tax
        dex
        bne @l
        rts

; por linha: escreve xadrez, le; escreve invertido, le
drtest: lda #0
        sta rlo
        sta rhi
        sta pass
        jsr progress
@row:   lda #0
        sta pass
@pp:    lda #1
        sta dwrite
        lda #0
        jsr setddr
        jsr drrow
        lda #0
        sta clo
        sta chi
@wc:    jsr drpat
        sta wdata
        jsr drcyc
        jsr cinc
        bcc @wc
        lda #0
        sta dwrite
        sta wdata
        lda #1
        jsr setddr
        jsr drrow
        lda #0
        sta clo
        sta chi
@rc:    jsr drcyc
        jsr getdata
        sta got
        jsr drpat
        sta expv
        cmp got
        beq @ok
        jmp fail
@ok:    lda #0
        sta wdata
        jsr cinc
        bcc @rc
        inc pass
        lda pass
        cmp #2
        bne @pp
        lda rlo
        and #$0F
        bne @np
        jsr progress
@np:    jsr rinc
        bcs @e
        jmp @row
@e:     rts

; xadrez fisico: (linha xor coluna) bit 0 -> $55/$AA; passo 2 inverte
drpat:  lda rlo
        eor clo
        and #1
        tax
        lda chk,x
        ldx pass
        beq @m
        eor #$FF
@m:     ldx dbits
        and dmask-1,x
        rts

cinc:   inc clo
        bne @h
        inc chi
@h:     lda ncol
        ldx clo
        ldy chi
        jmp lim
rinc:   inc rlo
        bne @h
        inc rhi
@h:     lda nrow
        ldx rlo
        ldy rhi
        jmp lim

; ----- teste das linhas de endereco ("bit andando")
; atmode 0 = endereco SRAM, 1 = linha DRAM (coluna 0), 2 = coluna DRAM (linha 0)
; alen = numero de linhas de endereco
; para cada polaridade P: grava P no endereco 0 e em todos os 2^b; para cada b:
; grava ~P em 2^b e confere que o 0 e os outros 2^j continuam P.
addrtest:
        lda #2
        sta pass
        jsr progress
        lda #0
        sta pol
@pl:    lda #NONE
        jsr setaddr
        jsr polv
        sta wdata
        jsr memwr
        lda #0
        sta ab
@w:     lda ab
        jsr setaddr
        jsr polv
        sta wdata
        jsr memwr
        inc ab
        lda ab
        cmp alen
        bne @w
        lda #0
        sta ab
@b:     lda ab
        jsr setaddr
        jsr polv
        eor #$FF
        ldx dbits
        and dmask-1,x
        sta wdata
        jsr memwr
        ; confere o endereco 0
        lda #NONE
        jsr setaddr
        jsr chkp
        bcs @f
        ; confere os outros
        lda #0
        sta aj
@j:     lda aj
        cmp ab
        beq @jn
        jsr setaddr
        jsr chkp
        bcs @f
@jn:    inc aj
        lda aj
        cmp alen
        bne @j
        ; restaura P em 2^b
        lda ab
        jsr setaddr
        jsr polv
        sta wdata
        jsr memwr
        inc ab
        lda ab
        cmp alen
        bne @b
        inc pol
        lda pol
        cmp #2
        beq @x
        jmp @pl
@x:     rts
@f:     jmp fail

; le o endereco atual e compara com P; C=1 se diferente
chkp:   jsr memrd
        sta got
        jsr polv
        sta expv
        cmp got
        beq @ok
        sec
        rts
@ok:    clc
        rts

; valor P da polaridade atual
polv:   lda pol
        beq @z
        lda #$FF
        bne @m
@z:     lda #$00
@m:     ldx dbits
        and dmask-1,x
        rts

; A = numero do bit (ou NONE = endereco 0) -> endereco conforme atmode
setaddr:
        sta tmp
        lda #0
        sta alo
        sta ahi
        sta rlo
        sta rhi
        sta clo
        sta chi
        sta vlo
        sta vhi
        lda tmp
        cmp #NONE
        beq @e
        cmp #8
        bcs @h
        tax
        lda bits,x
        sta vlo
        jmp @put
@h:     sec
        sbc #8
        tax
        lda bits,x
        sta vhi
@put:   lda atmode
        bne @1
        lda vlo
        sta alo
        lda vhi
        sta ahi
        rts
@1:     cmp #1
        bne @2
        lda vlo
        sta rlo
        lda vhi
        sta rhi
        rts
@2:     lda vlo
        sta clo
        lda vhi
        sta chi
@e:     rts

fail:   lda #1
        sta result
        rts

; ---------------------------------------------------------- tela
; linha 22 (o desenho do ZIF continua na tela): "TESTING  STEP n/3  ROW $xxx" (ou ADDRESS)
progress:
        lda #22
        sta CV
        jsr VTAB
        lda #0
        sta CH
        ldx #<t_pass
        ldy #>t_pass
        jsr print
        ldx pass
        lda stepn,x
        jsr COUT
        lda pass
        cmp #2
        beq @a
        lda ctype
        cmp #T_DRAM
        bne @s
        ldx #<t_row
        ldy #>t_row
        jsr print
        lda rhi
        jsr PRBYTE
        lda rlo
        jmp PRBYTE
@s:     ldx #<t_adr
        ldy #>t_adr
        jsr print
        lda ahi
        jsr PRBYTE
        lda alo
        jmp PRBYTE
@a:     ldx #<t_lines
        ldy #>t_lines
        jmp print

report: lda #20
        jsr clrln
        lda #21
        jsr clrln
        lda #22
        jsr clrln
        lda #20
        sta CV
        jsr VTAB
        lda #0
        sta CH
        lda result
        bne @bad
        ldx #<t_ok
        ldy #>t_ok
        jsr print
        jsr longbeep
        jmp @k
@bad:   cmp #2
        bne @err
        ldx #<t_power
        ldy #>t_power
        jsr print
        jsr beep5
        jmp @k
@err:   ldx #<t_err
        ldy #>t_err
        jsr print
        ldx pass
        lda stepn,x
        jsr COUT
        jsr CROUT
        lda pass
        cmp #2
        bne @np
        ldx #<t_abit
        ldy #>t_abit
        jsr print
        lda ab
        jsr prdec
        ldx atmode
        beq @np2
        dex
        bne @cl
        ldx #<t_arow
        ldy #>t_arow
        jsr print
        jmp @np2
@cl:    ldx #<t_acol
        ldy #>t_acol
        jsr print
@np2:   jsr CROUT
@np:    lda ctype
        cmp #T_DRAM
        bne @sa
        ldx #<t_erow
        ldy #>t_erow
        jsr print
        lda rhi
        jsr PRBYTE
        lda rlo
        jsr PRBYTE
        ldx #<t_ecol
        ldy #>t_ecol
        jsr print
        lda chi
        jsr PRBYTE
        lda clo
        jsr PRBYTE
        jmp @dv
@sa:    ldx #<t_eadr
        ldy #>t_eadr
        jsr print
        lda ahi
        jsr PRBYTE
        lda alo
        jsr PRBYTE
@dv:    ldx #<t_exp
        ldy #>t_exp
        jsr print
        lda expv
        jsr PRBYTE
        ldx #<t_got
        ldy #>t_got
        jsr print
        lda got
        jsr PRBYTE
        jsr beep5
@k:     jsr CROUT
        ldx #<t_key
        ldy #>t_key
        jmp print

; apaga a linha A da tela (39 espacos)
clrln:  sta CV
        jsr VTAB
        lda #0
        sta CH
        ldx #39
@l:     lda #' '|$80
        jsr COUT
        dex
        bne @l
        rts

; ---------------------------------------------------------- hardware
portx:  tya
        asl
        ora slot16
        tax
        rts
wrdir:  pha
        jsr portx
        lda #0
        sta $C085,x
        pla
        sta $C084,x
        lda #4
        sta $C085,x
        rts
wrdat:  pha
        jsr portx
        pla
        sta $C084,x
        rts
hwinit: lda #$FF
        ldy #3
        jsr wrdir
        lda #$C3
        ldy #3
        jsr wrdat
        lda #$FF
        ldy #4
        jsr wrdir
        lda #$FF
        ldy #5
        jsr wrdir
        lda #0
        ldy #4
        jsr wrdat
        lda #0
        ldy #5
        jsr wrdat
        jmp allin
hwsafe: jsr allin
        lda #$C3
        ldy #3
        jmp wrdat
allin:  lda #0
        ldy #0
        jsr wrdir
        lda #0
        ldy #1
        jsr wrdir
        lda #$F8
        ldy #2
        jsr wrdir
        lda #0
        ldy #0
        jsr wrdat
        lda #0
        ldy #1
        jsr wrdat
        lda #$80
        ldy #2
        jmp wrdat
; comparador da linha mux (0..15 = PE/PF) -> A (1 = H, 2 = L, 0 = meio)
readmux:
        lda mux
        cmp #8
        bcs @f
        tax
        lda bits,x
        ldy #4
        jsr wrdat
        jmp @rd
@f:     and #7
        tax
        lda bits,x
        ldy #5
        jsr wrdat
@rd:    ldy #40
@d:     dey
        bne @d
cmpadr: lda $C400
        and #3
        pha
        lda #0
        ldy #4
        jsr wrdat
        lda #0
        ldy #5
        jsr wrdat
        pla
        rts

; ---------------------------------------------------------- texto/som
longbeep:
        ldx #120
@l:     lda $C030
        ldy #200
@d:     dey
        bne @d
        dex
        bne @l
        rts
beep5:  lda #5
        sta tmp
@b:     jsr BELL
        lda #$60
        jsr WAIT
        dec tmp
        bne @b
        rts
print:  stx ptr
        sty ptr+1
        ldy #0
@l:     lda (ptr),y
        beq @e
        ora #$80
        jsr COUT
        iny
        bne @l
@e:     rts
prdec:  ldx #0
@t:     cmp #10
        bcc @u
        sbc #10
        inx
        bne @t
@u:     pha
        txa
        beq @s
        ora #'0'|$80
        jsr COUT
@s:     pla
        ora #'0'|$80
        jmp COUT

; ---------------------------------------------------------- dados
bits:   .byte $01,$02,$04,$08,$10,$20,$40,$80
dmask:  .byte $01,$03,$07,$0F,$1F,$3F,$7F,$FF   ; indice dbits-1
chk:    .byte $55,$AA
stepn:  .byte "123"

; descritor: tipo, pinos, flags, PD, nrow, ncol, dbits, shared,
;            linha[nrow], coluna[ncol], din[dbits], dout[dbits],
;            CS, WE, OE, RAS, CAS, LATCH   (k = indice da linha da placa)
d2114:  .byte T_SRAM,18,F_JMP,$C7,10,0,4,1
        .byte 3,4,5,2,1,0,17,15,14,13          ; A0..A9
        .byte 12,11,10,9                       ; I/O1..4
        .byte 12,11,10,9
        .byte 6,8,NONE,NONE,NONE,NONE
d2147:  .byte T_SRAM,18,F_JMP,$C7,12,0,1,0
        .byte 17,0,1,2,3,4,10,11,12,13,14,15   ; A0..A11
        .byte 9                                ; DIN
        .byte 5                                ; DOUT
        .byte 8,6,NONE,NONE,NONE,NONE
d4164:  .byte T_DRAM,16,F_ROT,$47,8,8,1,0
        .byte 12,14,13,3,2,1,4,0               ; A0..A7 (linha)
        .byte 12,14,13,3,2,1,4,0               ; (coluna)
        .byte 9                                ; DIN
        .byte 5                                ; DOUT
        .byte NONE,10,NONE,11,6,NONE
d41256: .byte T_DRAM,16,F_ROT,$47,9,9,1,0
        .byte 12,14,13,3,2,1,4,0,8             ; A0..A8
        .byte 12,14,13,3,2,1,4,0,8
        .byte 9
        .byte 5
        .byte NONE,10,NONE,11,6,NONE
d4416:  .byte T_DRAM,18,F_ROT|F_JMP,$C7,8,6,4,1
        .byte 3,2,1,0,15,14,13,17              ; A0..A7 (linha)
        .byte 2,1,0,15,14,13                   ; A1..A6 (coluna)
        .byte 9,10,4,6                         ; DQ1..4
        .byte 9,10,4,6
        .byte NONE,11,8,12,5,NONE
d4464:  .byte T_DRAM,18,F_ROT|F_JMP,$C7,8,8,4,1
        .byte 3,2,1,0,15,14,13,17
        .byte 3,2,1,0,15,14,13,17
        .byte 9,10,4,6
        .byte 9,10,4,6
        .byte NONE,11,8,12,5,NONE
d6116:  .byte T_ADPT,24,F_ADP,$C7,11,0,8,1
        .byte 0,1,2,3,4,5,6,NONE,NONE,NONE,NONE ; A0..A6 direto; A7.. no latch
        .byte 8,9,10,11,12,13,14,15
        .byte 8,9,10,11,12,13,14,15
        .byte NONE,18,17,NONE,NONE,16
d6264:  .byte T_ADPT,28,F_ADP,$C7,13,0,8,1
        .byte 0,1,2,3,4,5,6,NONE,NONE,NONE,NONE,NONE,NONE
        .byte 8,9,10,11,12,13,14,15
        .byte 8,9,10,11,12,13,14,15
        .byte NONE,18,17,NONE,NONE,16

desctab: .word d2114,d2147,d4164,d41256,d4416,d4464,d6116,d6264
nametab: .word n2114,n2147,n4164,n41256,n4416,n4464,n6116,n6264
n2114:  .byte "2114  STATIC RAM 1K X 4",0
n2147:  .byte "2147  STATIC RAM 4K X 1",0
n4164:  .byte "4164  DYNAMIC RAM 64K X 1",0
n41256: .byte "41256 DYNAMIC RAM 256K X 1",0
n4416:  .byte "4416  DYNAMIC RAM 16K X 4",0
n4464:  .byte "4464  DYNAMIC RAM 64K X 4",0
n6116:  .byte "6116  STATIC RAM 2K X 8",0
n6264:  .byte "6264  STATIC RAM 8K X 8",0

t_slot: .byte "MEMORY TESTER - VERSION 2.0",$0D
        .byte "EXPANDED BY TABAJARA LABS",$0D,$0D
        .byte "SLOT OF THE I.C. TEST CARD (1-7) ? ",0
t_menu: .byte "     MEMORY TESTER - VERSION 2.0",$0D,$0D
        .byte " 1: 2114   SRAM  1K X 4  (JUMPER)",$0D
        .byte " 2: 2147   SRAM  4K X 1  (JUMPER)",$0D
        .byte " 3: 4164   DRAM 64K X 1  (REVERSED)",$0D
        .byte " 4: 41256  DRAM 256K X 1 (REVERSED)",$0D
        .byte " 5: 4416   DRAM 16K X 4  (REV+JUMPER)",$0D
        .byte " 6: 4464   DRAM 64K X 4  (REV+JUMPER)",$0D
        .byte " 7: 6116   SRAM  2K X 8  (ADAPTER)",$0D
        .byte " 8: 6264   SRAM  8K X 8  (ADAPTER)",$0D,$0D
        .byte " WHICH ONE ? (1-8, ESC = MENU) ",0
t_ziftop: .byte $0D,"     POS PIN          PIN POS",$0D,0
t_gnd:  .byte " GND",0
t_empty:.byte " :    : ",0
t_body: .byte "|      |",0
t_notch:.byte "|  ()  |",0
t_dl:   .byte "   ",0
t_dr:   .byte "    ",0
t_j20:  .byte " <+",0
t_j19:  .byte " <+ JUMPER",0
t_rot:  .byte "REVERSED: NOTCH () DOWN, PIN 1 AT",$0D
        .byte "POSITION 11 (LOWER RIGHT).",$0D,0
t_norm: .byte "NOTCH () UP, PUSHED TO THE BOTTOM",$0D
        .byte "(LAST PIN AT POSITION 10 = GND).",$0D,0
t_jmp:  .byte "PUT A JUMPER WIRE: POSITION 19 TO 20.",$0D,0
t_adp:  .byte $0D,"INSERT THE 6116/6264 ADAPTER IN THE",$0D
        .byte "ZIF (ALL 20 POSITIONS, ADAPTER PIN 1",$0D
        .byte "= ZIF POSITION 1) AND THE CHIP IN THE",$0D
        .byte "ADAPTER, PUSHED TO THE BOTTOM OF THE",$0D
        .byte "28-PIN SOCKET, NOTCH UP.",$0D,$0D
        .byte "JUMPER J1: 6264 = A11   6116 = /WE",$0D,0
t_go:   .byte $0D,"SPACE = TEST    ESC = BACK",0
t_pass: .byte "TESTING... STEP ",0
t_row:  .byte "/3  ROW $",0
t_adr:  .byte "/3  ADDRESS $",0
t_lines:.byte "/3  ADDRESS LINES    ",0
t_ok:   .byte "TEST OK !",0
t_power:.byte "LEVEL ERROR, POWER LOW",0
t_err:  .byte "TEST ERROR END, STEP ",0
t_abit: .byte "BAD ADDR BIT ",0
t_arow: .byte " ROW",0
t_acol: .byte " COL",0
t_erow: .byte "ROW $",0
t_ecol: .byte " COL $",0
t_eadr: .byte "ADDRESS $",0
t_exp:  .byte " EXP ",0
t_got:  .byte " GOT ",0
t_key:  .byte "PRESS ANY KEY",0

; ---------------------------------------------------------- variaveis
slotn:  .byte 0
slot16: .byte 0
cname:  .word 0
pins:   .byte 0
flags:  .byte 0
row:    .byte 0
rpos:   .byte 0
lpin:   .byte 0
rpin:   .byte 0
n:      .byte 0
tmp:    .byte 0
tmp2:   .byte 0
ctype:  .byte 0
pdcode: .byte 0
nrow:   .byte 0
ncol:   .byte 0
dbits:  .byte 0
shared: .byte 0
li_row: .byte 0
li_col: .byte 0
li_din: .byte 0
li_dout:.byte 0
li_ctl: .byte 0
ci:     .byte 0
cnt:    .byte 0
lst:    .byte 0
tmask:  .byte 0
v:      .byte 0
bi:     .byte 0
tbh:    .byte 0
acc:    .res 3
base:   .res 3
ddrw:   .res 3
ddrr:   .res 3
cur:    .res 3
rd:     .res 3
i1:     .res 3
i2:     .res 3
m3:     .res 3
i3:     .res 3
i4c:    .byte 0
i2r:    .byte 0
rasp:   .byte 0
casp:   .byte 0
rasx:   .byte 0
casx:   .byte 0
baser:  .byte 0
cm:     .res 3
ctlp:   .res 6
ctlm:   .res 6
doutp:  .byte 0
doutm:  .byte 0
curdir: .byte 0
latched:.byte 0
vlo:    .byte 0
vhi:    .byte 0
alo:    .byte 0
ahi:    .byte 0
rlo:    .byte 0
rhi:    .byte 0
clo:    .byte 0
chi:    .byte 0
wdata:  .byte 0
dwrite: .byte 0
got:    .byte 0
expv:   .byte 0
pass:   .byte 0
result: .byte 0
mux:    .byte 0
atmode: .byte 0
alen:   .byte 0
pol:    .byte 0
ab:     .byte 0
aj:     .byte 0
