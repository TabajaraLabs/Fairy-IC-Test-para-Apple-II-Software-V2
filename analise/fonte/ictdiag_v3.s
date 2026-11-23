; =====================================================================
; ICTDIAG.SYSTEM v3 - diagnostico do hardware da placa IC TEST CARD
; (Fairy / Yih-Lung, 1984).  Rodar com o SOQUETE VAZIO.
;
; Modelo do hardware (deduzido do software original):
;   3 x MC6821 em $C084-$C08F + slot*16
;     PA=$84/$85 PB=$86/$87 PC=$88/$89 PD=$8A/$8B PE=$8C/$8D PF=$8E/$8F
;     (CR=0 -> acesso ao DDR; CR=4 -> acesso ao registro de dados)
;   PA0-7, PB0-7, PC0-2 = 19 pinos do soquete (o 20o e' GND fixo)
;   PE0-7, PF0-7, PC3-5 = multiplexador que liga 1 pino ao comparador
;   comparador lido em $Cn00, bits 0-1 (00 = nivel intermediario)
;   PC6/PC7 = controle (pull-up/down?)   PD = codigo de alimentacao
;
; Teste 1: mapa bit de porta -> linha do mux, e significado dos bits
; Teste 2: efeito de PC6/PC7 com pinos soltos
; Teste 3: codigos de alimentacao conhecidos (só os do software original)
; =====================================================================

MLI     = $BF00
HOME    = $FC58
COUT    = $FDED
CROUT   = $FD8E
RDKEY   = $FD0C
PRBYTE  = $FDDA
WAIT    = $FCA8
SETNORM = $FE84
INIT    = $FB2F
SETVID  = $FE93
SETKBD  = $FE89

ptr     = $06

        .org $2000

start:  cld
        sta $C00C          ; 40 colunas
        sta $C000
        sta $C00E
        jsr SETNORM
        jsr INIT
        jsr SETVID
        jsr SETKBD
        jsr HOME
        ldx #<t_title
        ldy #>t_title
        jsr print
askslot:
        jsr RDKEY
        and #$7F
        cmp #'1'
        bcc askslot
        cmp #'8'
        bcs askslot
        sta slotch
        jsr COUT1h
        and #$07
        sta slot
        asl
        asl
        asl
        asl
        sta slot16
        lda slot
        ora #$C0
        sta rdcmp+2        ; LDA $Cn00 (auto-modificado)
        jsr CROUT
        jsr hwinit
        ldx #<t_menu
        ldy #>t_menu
        jsr print
@m:     jsr RDKEY
        and #$7F
        cmp #'2'
        bne @m1
        jmp explore
@m1:    cmp #'1'
        bne @m

; ---------------------------------------------------------- TESTE 1
; duas telas: pino ligado em 1, depois em 0. Cada linha: nome do pino
; + os 19 valores do comparador (linhas E0..E7 F0..F7 C3 C4 C5).
        lda #1
        sta lvl1
t1page: jsr HOME
        ldx #<t_t1
        ldy #>t_t1
        jsr print
        lda lvl1
        jsr prdig
        jsr CROUT
        ldx #<t_hdr
        ldy #>t_hdr
        jsr print
        lda #0
        sta drv
t1loop: jsr setdrv
        lda lvl1
        jsr drvlevel
        jsr scanmux
        lda drv
        jsr prpin
        lda #' '|$80
        jsr COUT
        ldx #0
t1pr:   stx tmpx
        lda res,x
        jsr prdig
        ldx tmpx
        inx
        cpx #19
        bne t1pr
        jsr CROUT
        inc drv
        lda drv
        cmp #19
        bne t1loop
        jsr allin
        ldx #<t_key
        ldy #>t_key
        jsr print
        jsr RDKEY
        dec lvl1
        bpl t1page

; ---------------------------------------------------------- TESTE 2
        jsr HOME
        ldx #<t_t2
        ldy #>t_t2
        jsr print
        lda #0
        sta mode
t2loop: jsr allin
        lda mode
        asl
        asl
        asl
        asl
        asl
        asl                ; mode -> bits 7,6
        sta pc76
        jsr wrpc
        lda #'7'|$80       ; "76=xy "
        jsr COUT
        lda #'6'|$80
        jsr COUT
        lda #'='|$80
        jsr COUT
        lda mode
        lsr
        and #1
        jsr prdig
        lda mode
        and #1
        jsr prdig
        lda #' '|$80
        jsr COUT
        jsr scanmux
        ldx #0
@pr:    stx tmpx
        lda res,x
        jsr prdig
        ldx tmpx
        inx
        cpx #19
        bne @pr
        lda #' '|$80
        jsr COUT
        ldy #0             ; PA
        jsr rddat
        jsr PRBYTE
        ldy #1             ; PB
        jsr rddat
        jsr PRBYTE
        jsr CROUT
        inc mode
        lda mode
        cmp #4
        bne t2loop
        lda #$80           ; volta ao padrao do software (PC7=1)
        sta pc76
        jsr wrpc
        ldx #<t_key
        ldy #>t_key
        jsr print
        jsr RDKEY

; ---------------------------------------------------------- TESTE 3
        jsr HOME
        ldx #<t_t3
        ldy #>t_t3
        jsr print
        jsr RDKEY
        and #$7F
        cmp #'S'
        beq @go3
        cmp #'s'
        bne fim
@go3:   jsr CROUT
        ldx #<t_t3h
        ldy #>t_t3h
        jsr print
        lda #0
        sta drv
t3loop: jsr allin
        ldx drv
        lda pdtab,x
        sta curpd
        jsr PRBYTE
        lda #':'|$80
        jsr COUT
        lda curpd
        ldy #3             ; PD
        jsr wrdat
        lda #$C0
        jsr WAIT
        jsr scanmux
        ldx #0
@p3:    stx tmpx
        lda res,x
        jsr prdig
        ldx tmpx
        inx
        cpx #19
        bne @p3
        lda #$C3
        ldy #3
        jsr wrdat
        lda #$C0
        jsr WAIT
        jsr CROUT
        inc drv
        lda drv
        cmp #PDN
        bne t3loop

fim:    jsr hwsafe
        ldx #<t_end
        ldy #>t_end
        jsr print
        jsr RDKEY
        jsr MLI
        .byte $65
        .word p_quit
        brk


; ---------------------------------------------------------- EXPLORAR PD
; aplica um codigo PD digitado (hex), mostra o comparador e SEGURA ate uma tecla
explore:
        jsr HOME
        ldx #<t_ex
        ldy #>t_ex
        jsr print
exloop: jsr CROUT
        ldx #<t_pdq
        ldy #>t_pdq
        jsr print
        jsr gethex
        bcc @ok
        jmp fim            ; ESC
@ok:    sta curpd
        jsr allin
        lda curpd
        ldy #3
        jsr wrdat
        lda #$C0
        jsr WAIT
        jsr CROUT
        lda #' '|$80
        jsr COUT
        jsr COUT
        jsr COUT
        jsr scanmux
        ldx #0
@p:     stx tmpx
        lda res,x
        jsr prdig
        ldx tmpx
        inx
        cpx #19
        bne @p
        jsr CROUT
        ldx #<t_hold
        ldy #>t_hold
        jsr print
        jsr RDKEY
        lda #$C3
        ldy #3
        jsr wrdat
        ldx #<t_off
        ldy #>t_off
        jsr print
        jmp exloop

; le 2 digitos hex -> A ; C=1 se ESC
gethex: jsr hexdig
        bcs @esc
        asl
        asl
        asl
        asl
        sta tmpx
        jsr hexdig
        bcs @esc
        ora tmpx
        clc
        rts
@esc:   sec
        rts
hexdig: jsr RDKEY
        and #$7F
        cmp #$1B
        beq @e
        cmp #'0'
        bcc hexdig
        cmp #'9'+1
        bcc @n
        and #$DF
        cmp #'A'
        bcc hexdig
        cmp #'F'+1
        bcs hexdig
        pha
        ora #$80
        jsr COUT
        pla
        sec
        sbc #'A'-10
        clc
        rts
@n:     pha
        ora #$80
        jsr COUT
        pla
        and #$0F
        clc
        rts
@e:     sec
        rts

; ---------------------------------------------------------- hardware
; calcula X = slot16 + 2*Y (porta Y = 0..5 -> A..F)
portx:  tya
        asl
        ora slot16
        tax
        rts
; escreve DDR: A=valor, Y=porta
wrdir:  pha
        jsr portx
        lda #0
        sta $C085,x
        pla
        sta $C084,x
        lda #4
        sta $C085,x
        rts
; escreve dado: A=valor, Y=porta
wrdat:  pha
        jsr portx
        pla
        sta $C084,x
        rts
; le dado: Y=porta -> A
rddat:  jsr portx
        lda $C084,x
        rts

hwinit: lda #$FF           ; PD saida, alimentacao em repouso ($C3)
        ldy #3
        jsr wrdir
        lda #$C3
        ldy #3
        jsr wrdat
        lda #$FF           ; PE, PF saidas = 0 (mux desligado)
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
        lda #$80           ; PC7=1 PC6=0 (padrao dos testes originais)
        sta pc76
        jsr allin
        rts

hwsafe: jsr allin
        lda #$C3
        ldy #3
        jsr wrdat
        lda #0
        ldy #4
        jsr wrdat
        lda #0
        ldy #5
        jsr wrdat
        rts

; todos os pinos do soquete como entrada
allin:  lda #0
        sta ddra
        sta ddrb
        sta pcpin
        sta pcdrv
        jsr apply
        lda #0
        ldy #0
        jsr wrdat
        lda #0
        ldy #1
        jsr wrdat
        rts

; aplica DDRs de PA, PB, PC (PC3-7 sempre saida)
apply:  lda ddra
        ldy #0
        jsr wrdir
        lda ddrb
        ldy #1
        jsr wrdir
        lda pcpin
        ora #$F8
        ldy #2
        jsr wrdir
        jmp wrpc

; escreve PC = pc76 | mux(bits3-5) | pcdrv(bits0-2)
wrpc:   lda pc76
        ora pcmux
        ora pcdrv
        ldy #2
        jmp wrdat

; drv (0..18) vira saida, o resto entrada
setdrv: lda #0
        sta ddra
        sta ddrb
        sta pcpin
        sta pcdrv
        lda drv
        cmp #8
        bcs @b
        tax
        lda bits,x
        sta ddra
        jmp apply
@b:     cmp #16
        bcs @c
        sec
        sbc #8
        tax
        lda bits,x
        sta ddrb
        jmp apply
@c:     sec
        sbc #16
        tax
        lda bits,x
        sta pcpin
        jmp apply

; poe o nivel A (0/1) no pino drv
drvlevel:
        sta lvl
        lda #0
        sta pcdrv
        lda lvl
        beq @z
        lda ddra
        ldy #0
        jsr wrdat
        lda ddrb
        ldy #1
        jsr wrdat
        lda pcpin
        sta pcdrv
        jmp wrpc
@z:     lda #0
        ldy #0
        jsr wrdat
        lda #0
        ldy #1
        jsr wrdat
        jmp wrpc

; le o comparador nas 19 linhas do mux -> res[0..18]
scanmux:
        lda #0
        sta mux
smloop: jsr selmux
        jsr delay
rdcmp:  lda $C100          ; operando alto = $Cn (auto-modificado)
        and #$03
        ldx mux
        sta res,x
        jsr desel
        inc mux
        lda mux
        cmp #19
        bne smloop
        rts

selmux: lda mux
        cmp #8
        bcs @f
        tax
        lda bits,x
        ldy #4
        jmp wrdat
@f:     cmp #16
        bcs @c
        sec
        sbc #8
        tax
        lda bits,x
        ldy #5
        jmp wrdat
@c:     sec
        sbc #16
        tax
        lda pcmuxtab,x
        sta pcmux
        jmp wrpc

desel:  lda #0
        ldy #4
        jsr wrdat
        lda #0
        ldy #5
        jsr wrdat
        lda #0
        sta pcmux
        jmp wrpc

delay:  ldy #40
@d:     dey
        bne @d
        rts

; ---------------------------------------------------------- impressao
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

COUT1h: ora #$80
        jsr COUT
        and #$7F
        rts

prdig:  ora #'0'|$80
        jmp COUT

; nome do bit de porta A=0..18: PA0..PA7 PB0..PB7 PC0..PC2
prpin:  pha
        lda #'P'|$80
        jsr COUT
        pla
        ldx #'A'|$80
        cmp #8
        bcc @p
        ldx #'B'|$80
        sbc #8
        cmp #8
        bcc @p
        ldx #'C'|$80
        sbc #8
@p:     pha
        txa
        jsr COUT
        pla
        jmp prdig

; nome da linha do mux A=0..18: E0..E7 F0..F7 C3..C5
prmux:  ldx #'E'|$80
        cmp #8
        bcc @p
        ldx #'F'|$80
        sbc #8
        cmp #8
        bcc @p
        ldx #'C'|$80
        sbc #5             ; 16..18 -> 3..5
@p:     pha
        txa
        jsr COUT
        pla
        jmp prdig

; ---------------------------------------------------------- dados
bits:     .byte $01,$02,$04,$08,$10,$20,$40,$80
pcmuxtab: .byte $08,$10,$20
pdtab:    .byte $C3,$87,$47,$C7,$C9,$D2,$E2
PDN = 7
p_quit:   .byte 4,0,0,0,0,0,0

t_title:  .byte "ICTDIAG V3 - DIAGNOSTICO IC TEST CARD",$0D
          .byte "DEIXE O SOQUETE ZIF VAZIO!",$0D,$0D
          .byte "SLOT DA PLACA (1-7)? ",0
t_t1:     .byte "T1: PINO LIGADO EM ",0
t_hdr:    .byte "    EEEEEEEEFFFFFFFFCCC",$0D
          .byte "    0123456701234567345",$0D,0
t_none:   .byte " ---",0
t_t2:     .byte "T2: PC7/PC6, PINOS SOLTOS",$0D
          .byte "      EEEEEEEEFFFFFFFFCCC",$0D
          .byte "      0123456701234567345 PAPB",$0D,0
t_t3:     .byte "T3: CODIGOS DE ALIMENTACAO (PD)",$0D,$0D
          .byte "SO OS CODIGOS USADOS PELO SOFTWARE",$0D
          .byte "ORIGINAL. O SOQUETE TEM QUE ESTAR",$0D
          .byte "VAZIO! CONTINUAR (S/N)? ",0
t_t3h:    .byte "PD EEEEEEEEFFFFFFFFCCC",$0D
          .byte "   0123456701234567345",$0D,0
t_key:    .byte "FOTOGRAFE A TELA E TECLE ALGO",0
t_menu:   .byte $0D,"1 = DIAGNOSTICO (T1-T3)",$0D
          .byte "2 = EXPLORAR CODIGO PD (SOQUETE VAZIO)",$0D,"? ",0
t_ex:     .byte "EXPLORAR PD - SOQUETE VAZIO! ESC=SAIR",$0D
          .byte "   EEEEEEEEFFFFFFFFCCC",$0D
          .byte "   0123456701234567345",0
t_pdq:    .byte "PD (HEX)? ",0
t_hold:   .byte "LIGADO. MECA E TECLE ALGO P/ DESLIGAR",0
t_off:    .byte $0D,"DESLIGADO ($C3)",0
t_end:    .byte $0D,"FIM. FOTOGRAFE E TECLE ALGO P/ SAIR",0

; ---------------------------------------------------------- variaveis
slot:   .byte 0
slotch: .byte 0
slot16: .byte 0
drv:    .byte 0
lvl:    .byte 0
mux:    .byte 0
mode:   .byte 0
cnt:    .byte 0
lvl1:   .byte 0
tmpx:   .byte 0
curpd:  .byte 0
ddra:   .byte 0
ddrb:   .byte 0
pcpin:  .byte 0
pcdrv:  .byte 0
pcmux:  .byte 0
pc76:   .byte 0
res:    .res 19
res1:   .res 19
