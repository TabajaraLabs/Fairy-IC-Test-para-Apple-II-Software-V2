; =====================================================================
; ELHOOK.ENG v1 - integra a biblioteca Elnec DENTRO dos programas originais
; A (TEST.2), B (CMOS.2) e C (HMOS.2) da placa IC TEST CARD.
; Carregado em $4300 (sobre o resto de fonte do assembler, area nao usada);
; biblioteca ICTL da familia em $4F00.
;
; Patches em cada binario (so 2):
;   $0946: JSR <imprime copyright>  ->  JSR VERx  (imprime e acrescenta 2 linhas)
;   <NA>  : inicio do "THIS NO. IS UNAVAILABLE"  ->  JMP NAx
; NAx: se o CI estiver na biblioteca, testa e salta para os caminhos da
; propria Fairy de "passou"/"falhou" (TEST OK, TEST ERROR, bipes, Ctrl-L e
; Ctrl-S continuam iguais); se nao estiver, segue o fluxo original.
; =====================================================================

LIB     = $4F00
COUT1   = $FDF0
COUT    = $FDF0
WAIT    = $FCA8
VTAB    = $FC22

ptr     = $06
rec     = $08
vp      = $EB
lp      = $ED
cfg     = $EF              ; ponteiro p/ a configuracao do binario ($EF/$F0)
tmpw    = $FA              ; ponteiro temporario ($FA/$FB)

        .org $4300

        jmp verT           ; $4300
        jmp naT            ; $4303
        jmp verC           ; $4306
        jmp naC            ; $4309
        jmp verH           ; $430C
        jmp naH            ; $430F
        jmp naTr           ; $4312  prefixo recusado (TEST.2)
        jmp naCr           ; $4315  prefixo recusado (CMOS.2)
        jmp naHr           ; $4318  prefixo recusado (HMOS.2)

; configuracao por binario (offsets C_*)
C_PRINT = 0                ; rotina original que imprime o copyright
C_NA    = 2                ; inicio do handler "nao disponivel"
C_V5E   = 4                ; variavel do 1o STA do handler (LDA #0 / STA v5e)
C_SRCH  = 6                ; flag do modo busca (Ctrl-S)
C_HI    = 8                ; centena (BCD)
C_LO    = 10               ; dezena/unidade (BCD)
C_PFX   = 12               ; prefixo digitado (2 chars)
C_DIG   = 14               ; digitos digitados (3 chars, $A0 = branco)
C_PASS  = 16               ; caminho "passou" da Fairy
C_FAIL  = 18               ; caminho "falhou"
C_CNT   = 20               ; total de CIs (2 bytes)
C_FAM   = 22               ; 0 = TTL/HC ("74"), 1 = CMOS ("40"/"45")

cfgT:   .word $0CEA,$0C72,$0F5E,$0F5D,$0F4E,$0F4D,$0F58,$0F5A,$0C0A,$0BDE,195
        .byte 0
cfgC:   .word $0CB6,$0C3E,$0FAE,$0FAD,$0F9E,$0F9D,$0FA8,$0FAA,$0EC2,$0BE1,96
        .byte 1
cfgH:   .word $0CD5,$0C5D,$0F4B,$0F4A,$0F3B,$0F3A,$0F45,$0F47,$0BF5,$0BC9,163
        .byte 0

setT:   lda #<cfgT
        ldx #>cfgT
        bne setc
setC:   lda #<cfgC
        ldx #>cfgC
        bne setc
setH:   lda #<cfgH
        ldx #>cfgH
setc:   sta cfg
        stx cfg+1
        rts

verT:   jsr setT
        jmp ver
verC:   jsr setC
        jmp ver
verH:   jsr setH
        jmp ver
naT:    jsr setT
        jmp na
naC:    jsr setC
        jmp na
naH:    jsr setH
        jmp na
naTr:   jsr setT
        jmp naraw
naCr:   jsr setC
        jmp naraw
naHr:   jsr setH
        jmp naraw

; le palavra cfg+Y -> tmpw
getw:   lda (cfg),y
        sta tmpw
        iny
        lda (cfg),y
        sta tmpw+1
        rts


; ---------------------------------------------------------- versao na tela
ver:    ldy #C_PRINT       ; chama a rotina original (imprime o copyright)
        jsr getw
        jsr callw
        lda $24
        pha
        lda $25
        pha
        ; linha 3: "nnn ICS AVAILABLE FOR TEST"
        lda #3
        sta $25
        jsr VTAB
        lda #7
        sta $24
        ldy #C_CNT
        lda (cfg),y
        jsr prdec3
        ldx #<t_avail
        ldy #>t_avail
        jsr print
        ; linha 6: versao
        lda #6
        sta $25
        jsr VTAB
        lda #1
        sta $24
        ldx #<t_ver
        ldy #>t_ver
        jsr print
        ; linha 7: refaz o copyright (1984 original + 2026 da expansao),
        ; terminando na coluna 37 como as linhas de cima (a 39 e' cortada em muitos monitores)
        lda #7
        sta $25
        jsr VTAB
        lda #0
        sta $24
        ldx #40
@sp:    lda #' '|$80
        jsr COUT1
        dex
        bne @sp
        lda #7
        sta $25
        jsr VTAB
        lda #19
        sta $24
        ldx #<t_copy
        ldy #>t_copy
        jsr print
        pla
        sta $25
        jsr VTAB
        pla
        sta $24
        rts
callw:  jmp (tmpw)

; ---------------------------------------------------------- nao disponivel
na:     lda LIB            ; biblioteca carregada?
        cmp #'I'
        bne orig
        lda LIB+1
        cmp #'C'
        bne orig
        lda #0
        sta altpfx
        lda #1
        sta usebm          ; numero BCD: usa o filtro do mapa de bits
        jsr bcdname        ; nome a partir do numero BCD (ja convertido pela Fairy)
        ldy #C_SRCH        ; fora da busca: CMOS usa o "40"/"45" digitado
        jsr getw
        ldy #0
        lda (tmpw),y
        bne look
        jsr cmospfx
        jmp look
; prefixo recusado pela Fairy: o numero nao foi convertido, os digitos estao intactos
naraw:  lda LIB
        cmp #'I'
        bne orig
        lda LIB+1
        cmp #'C'
        bne orig
        lda #1
        sta altpfx         ; sem segunda tentativa
        lda #0
        sta usebm          ; texto cru: sem filtro (pode ter letras, ex. 4063B)
        jsr rawname
look:   lda keylen
        beq orig
        jsr findq
        bcc found
        ; CMOS em busca: tenta tambem "45"
        ldy #C_FAM
        lda (cfg),y
        beq orig
        ldy #C_SRCH
        jsr getw
        ldy #0
        lda (tmpw),y
        beq orig
        lda altpfx
        bne orig
        inc altpfx
        lda #'5'
        sta key+1
        jsr findq
        bcc found
orig:   ; executa as instrucoes substituidas (LDA #0 / STA v5e) e volta
        ldy #C_V5E
        jsr getw
        lda #0
        ldy #0
        sta (tmpw),y
        ldy #C_NA
        jsr getw
        lda tmpw
        clc
        adc #5
        sta tmpw
        bcc @j
        inc tmpw+1
@j:     jmp (tmpw)

found:  ; slot e comparador vem da propria Fairy ($DA = slot*16, $D9 = $Cn)
        lda $DA
        sta slot16
        lda $D9
        sta rdcmp+2
        jsr hwprep
        jsr runtest
        ldy #C_V5E         ; mesmo efeito do inicio do handler original
        jsr getw
        lda #0
        ldy #0
        sta (tmpw),y
        lda result
        bne @f
        ldy #C_PASS
        jsr getw
        jmp (tmpw)
@f:     ldy #C_FAIL
        jsr getw
        jmp (tmpw)

; prefixo do nome: "74" (TTL/HC) ou "4x" (CMOS: do campo digitado)
pfxname:
        ldy #C_FAM
        lda (cfg),y
        bne @c
        lda #'7'
        sta key
        lda #'4'
        sta key+1
        rts
@c:     lda #'4'
        sta key
        lda #'0'
        sta key+1
        rts

; CMOS: troca o "40" pelo "4x" digitado no campo do prefixo, se numerico
cmospfx:
        ldy #C_FAM
        lda (cfg),y
        beq @x
        ldy #C_PFX
        jsr getw
        ldy #1
        lda (tmpw),y
        and #$7F
        cmp #'0'
        bcc @x
        cmp #'9'+1
        bcs @x
        sta key+1
@x:     rts

rawname:
        jsr pfxname
        jsr cmospfx
        ldy #C_DIG
        jsr getw
        ldx #2
        ldy #0
@l:     sty tmpy
        lda (tmpw),y
        and #$7F
        cmp #'0'
        bcc @n
        cmp #'9'+1
        bcs @n
        sta key,x
        inx
@n:     ldy tmpy
        iny
        cpy #3
        bne @l
        cpx #3             ; so 1 digito: completa com 0 na frente
        bne @k
        lda key+2
        sta key+3
        lda #'0'
        sta key+2
        ldx #4
@k:     cpx #2
        bne @ok
        ldx #0
@ok:    stx keylen
        rts

bcdname:
        jsr pfxname
        ldx #2
        ldy #C_HI
        jsr getw
        ldy #0
        lda (tmpw),y
        beq @nh
        ora #'0'
        sta key,x
        inx
@nh:    stx tmpy
        ldy #C_LO
        jsr getw
        ldy #0
        lda (tmpw),y
        pha
        lsr
        lsr
        lsr
        lsr
        ora #'0'
        ldx tmpy
        sta key,x
        inx
        pla
        and #$0F
        ora #'0'
        sta key,x
        inx
        stx keylen
        rts

; ---------------------------------------------------------- filtro rapido
; Mapa de bits de 1000 posicoes por prefixo: BM0 = "74" (TTL/HC) ou "40" (CMOS),
; BM1 = "45" (CMOS). Construido na 1a chamada. Um numero ausente e' descartado
; com uma leitura de bit (a busca Ctrl-S da Fairy chama o gancho ~500 vezes).
BM0     = $4E00
BM1     = $4E80

; key/keylen -> C=0 achou (rec) / C=1 nao achou
findq:  lda usebm
        beq @full
        lda bmok
        bne @t
        jsr bmbuild
@t:     ldx #0
@c:     lda key,x          ; copia key -> kbuf
        sta kbuf,x
        inx
        cpx keylen
        bne @c
        stx kblen
        jsr kbval
        bcs @full          ; formato inesperado: busca completa
        lda BM0,x
        and tmask
        bne @full
        sec                ; bit apagado: nao existe
        rts
@full:  jmp findic

; monta os mapas de bits a partir da biblioteca
bmbuild:
        lda #0
        tax
@z:     sta BM0,x
        inx
        bne @z
        lda #<LIB
        clc
        adc #8
        adc LIB+7
        sta lp
        lda #>LIB
        adc #0
        sta lp+1
@rec:   ldy #0
        lda (lp),y
        beq @done
        cmp #4
        bcc @nx
        cmp #6
        bcs @nx
        sta kblen
        tax
@cp:    lda (lp),y         ; y=0 e' o tamanho; nome em y=1..
        iny
        lda (lp),y
        sta kbuf-1,y
        dex
        bne @cp
        jsr kbval
        bcs @nx
        lda BM0,x
        ora tmask
        sta BM0,x
@nx:    jsr nextrec
        jmp @rec
@done:  lda #1
        sta bmok
        rts

; kbuf/kblen -> X = indice no mapa (BM0 + sel), tmask = bit ; C=1 se invalido
kbval:  ldx #0             ; todos digitos?
        beq @d
@bad:   sec
        rts
@d:     lda kbuf,x
        cmp #'0'
        bcc @bad
        cmp #'9'+1
        bcs @bad
        inx
        cpx kblen
        bne @d
        ; seletor pelo prefixo
        ldy #C_FAM
        lda (cfg),y
        bne @cm
        lda kbuf
        cmp #'7'
        bne @bad
        lda kbuf+1
        cmp #'4'
        bne @bad
        lda #0
        beq @sel
@cm:    lda kbuf
        cmp #'4'
        bne @bad
        lda kbuf+1
        cmp #'0'
        beq @s0
        cmp #'5'
        bne @bad
        lda #$80
        bne @sel
@s0:    lda #0
@sel:   sta bmsel
        ; valor decimal dos digitos 2..kblen-1 (16 bits)
        lda #0
        sta val
        sta val+1
        ldx #2
@v:     ; val = val*10 + digito
        lda val
        sta tw
        lda val+1
        sta tw+1
        asl val
        rol val+1
        asl val
        rol val+1          ; *4
        lda val
        clc
        adc tw
        sta val
        lda val+1
        adc tw+1
        sta val+1          ; *5
        asl val
        rol val+1          ; *10
        lda kbuf,x
        and #$0F
        clc
        adc val
        sta val
        bcc @n
        inc val+1
@n:     inx
        cpx kblen
        bne @v
        ; indice = val >> 3 (0..124), bit = val & 7
        lda val
        and #7
        tay
        lda bits,y
        sta tmask
        lda val+1
        lsr
        sta tw+1
        lda val
        ror
        lsr tw+1
        ror
        lsr tw+1
        ror
        cmp #125
        bcc @ok
        sec
        rts
@ok:    ora bmsel
        tax
        clc
        rts

usebm:  .byte 0
bmok:   .byte 0
bmsel:  .byte 0
tmask:  .byte 0
val:    .word 0
tw:     .word 0
kblen:  .byte 0
kbuf:   .res 8


; registradores de E/S que a Fairy talvez ainda nao tenha preparado
hwprep: lda #$FF
        ldy #3
        jsr wrdir
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
        lda #$80
        sta pc76
        lda #0
        sta pcmux
        rts

print:  stx ptr
        sty ptr+1
        ldy #0
@l:     lda (ptr),y
        beq @e
        ora #$80
        jsr COUT1
        iny
        bne @l
@e:     rts

prdec3: ldx #0
@h:     cmp #100
        bcc @t
        sbc #100
        inx
        bne @h
@t:     pha
        txa
        beq @n
        ora #'0'|$80
        jsr COUT1
        pla
        ldx #0
@t2:    cmp #10
        bcc @u2
        sbc #10
        inx
        bne @t2
@u2:    pha
        txa
        ora #'0'|$80
        jsr COUT1
        pla
        ora #'0'|$80
        jmp COUT1
@n:     pla
        ldx #0
@t3:    cmp #10
        bcc @u3
        sbc #10
        inx
        bne @t3
@u3:    pha
        txa
        beq @s
        ora #'0'|$80
        jsr COUT1
@s:     pla
        ora #'0'|$80
        jmp COUT1

t_avail: .byte " ICS AVAILABLE FOR TEST",0
t_ver:   .byte "VERSION 2.0 EXPANDED BY TABAJARA LABS",0
t_copy:  .byte "COPYRIGHT 1984/2026",0
tmpy:    .byte 0
altpfx:  .byte 0

; procura key[] na biblioteca -> rec ; C=0 achou
findic: lda #<LIB
        clc
        adc #8
        adc LIB+7
        sta lp
        lda #>LIB
        adc #0
        sta lp+1
@lp:    ldy #0
        lda (lp),y
        beq @nf
        cmp keylen
        bne @nx
        tax
@c:     lda (lp),y         ; y=0..: compara nome[y] com key[y-1]
        iny
        lda (lp),y
        cmp key-1,y
        bne @nx
        dex
        bne @c
        lda lp
        sta rec
        lda lp+1
        sta rec+1
        clc
        rts
@nx:    jsr nextrec
        jmp @lp
@nf:    sec
        rts

prname: ldy #0
        lda (rec),y
        tax
@l:     iny
        lda (rec),y
        ora #$80
        jsr COUT
        dex
        bne @l
        rts

; avanca lp para o proximo registro
nextrec:
        ldy #0
        lda (lp),y         ; nlen
        clc
        adc #5             ; nlen + 1 + pinos + pd + nvec(2)
        sta tmp
        ldy #0
        lda (lp),y
        tay
        iny
        iny
        iny                ; y -> nvec lo
        lda (lp),y
        sta cnt
        iny
        lda (lp),y
        sta cnt+1
        ; bytes = tmp + cnt*10
        lda cnt
        sta mul
        lda cnt+1
        sta mul+1
        asl mul
        rol mul+1          ; *2
        lda mul
        sta tmp2
        lda mul+1
        sta tmp2+1
        asl mul
        rol mul+1
        asl mul
        rol mul+1          ; *8
        lda mul
        clc
        adc tmp2
        sta mul
        lda mul+1
        adc tmp2+1
        sta mul+1          ; *10
        lda lp
        clc
        adc tmp
        sta lp
        bcc @a
        inc lp+1
@a:     lda lp
        clc
        adc mul
        sta lp
        lda lp+1
        adc mul+1
        sta lp+1
        rts

; ---------------------------------------------------------- teste
; result: 0 = OK, 1 = erro de vetor, 2 = alimentacao
runtest:
        ldy #0
        lda (rec),y
        tay
        iny
        lda (rec),y
        sta pins
        iny
        lda (rec),y
        sta pdcode
        iny
        lda (rec),y
        sta nvec
        iny
        lda (rec),y
        sta nvec+1
        iny
        tya
        clc
        adc rec
        sta vp
        lda rec+1
        adc #0
        sta vp+1
        lda #0
        sta result
        sta vecno
        sta vecno+1
        ; tudo entrada, liga alimentacao
        jsr allin
        lda pdcode
        ldy #3
        jsr wrdat
        lda #$40
        jsr WAIT
        jsr powchk
        bcc @vl
        lda #2
        sta result
        jmp @off
@vl:    lda vecno
        cmp nvec
        bne @go
        lda vecno+1
        cmp nvec+1
        beq @off
@go:    jsr dovec
        lda result
        bne @off
        lda vp
        clc
        adc #10
        sta vp
        bcc @i
        inc vp+1
@i:     inc vecno
        bne @vl
        inc vecno+1
        jmp @vl
@off:   jsr allin
        lda #$C3
        ldy #3
        jsr wrdat
        rts

; confere GND (e VCC quando visivel no mux) logo apos ligar
powchk: ldx #0
@f:     lda pdtab,x
        beq @ok            ; codigo nao tabelado: sem conferencia
        cmp pdcode
        beq @t
        inx
        inx
        inx
        bne @f
@t:     lda pdtab+1,x      ; linha do GND
        stx tmp
        sta mux
        jsr readmux
        cmp #2
        bne @bad
        ldx tmp
        lda pdtab+2,x      ; linha do VCC ($FF = nao visivel)
        cmp #$FF
        beq @ok
        sta mux
        jsr readmux
        cmp #1
        bne @bad
@ok:    clc
        rts
@bad:   sec
        rts

; executa um vetor (vp)
dovec:  ; decodifica nibbles -> mascaras
        lda #0
        ldx #8
@z:     sta mdir-1,x       ; mdir(3) mdat(3) + 2 extras
        dex
        bne @z
        lda #0
        sta k
@d:     jsr getnib
        tax
        lda isout,x
        beq @n
        jsr kbit           ; A = bit, X = porta (0..2)
        pha
        ora mdir,x
        sta mdir,x
        pla
        ldy kcode
        ldx kport
        pha
        lda isone,y
        beq @n0
        pla
        ora mdat,x
        sta mdat,x
        jmp @n
@n0:    pla
@n:     inc k
        lda k
        cmp #19
        bne @d
        ; dados antes do DDR
        lda mdat
        ldy #0
        jsr wrdat
        lda mdat+1
        ldy #1
        jsr wrdat
        lda mdat+2
        sta pcdrv
        jsr wrpc
        lda mdir
        ldy #0
        jsr wrdir
        lda mdir+1
        ldy #1
        jsr wrdir
        lda mdir+2
        ora #$F8
        ldy #2
        jsr wrdir
        ; pulsos de clock, um pino por vez (esquerda -> direita)
        lda #0
        sta k
@c:     jsr getnib
        cmp #6
        beq @cl
        cmp #7
        bne @cn
@cl:    jsr kbit
        sta tmp
        jsr pulse
@cn:    inc k
        lda k
        cmp #19
        bne @c
        jsr delay
        ; leitura
        lda #0
        ldy #0
        jsr rddat
        sta rd
        ldy #1
        jsr rddat
        sta rd+1
        ldy #2
        jsr rddat
        sta rd+2
        lda #0
        sta k
@r:     jsr getnib
        cmp #3
        bcc @rn
        cmp #6
        bcs @rn
        sta kcode
        lda k
        sta mux
        jsr readmux
        sta cmpv
        jsr kbit
        and rd,x
        sta dbit           ; 0 ou bit
        lda kcode
        cmp #3
        bne @h
        ; L: digital 0 e comparador 2
        lda dbit
        bne @fail
        lda cmpv
        cmp #2
        bne @fail
        beq @rn
@h:     cmp #4
        bne @zz
        lda dbit
        beq @fail
        lda cmpv
        cmp #1
        bne @fail
        beq @rn
@zz:    ; Z: lado PB -> intermediario; lado PA/PC -> nao pode ser L
        lda k
        cmp #8
        bcc @za
        cmp #16
        bcs @za
        lda cmpv
        bne @fail
        beq @rn
@za:    lda cmpv
        cmp #2
        beq @fail
@rn:    inc k
        lda k
        cmp #19
        bne @r
        rts
@fail:  lda #1
        sta result
        lda vecno
        sta failvec
        lda vecno+1
        sta failvec+1
        lda kcode
        sta failexp
        lda cmpv
        and #3
        sta failcmp
        ldx k
        lda k2pin,x        ; posicao do soquete
        jsr sock2pin       ; -> numero do pino do CI
        sta failpin
        rts

; nibble k do vetor atual -> A (e kcode)
getnib: lda k
        lsr
        tay
        lda (vp),y
        bcc @lo
        lsr
        lsr
        lsr
        lsr
@lo:    and #$0F
        sta kcode
        rts

; A = mascara do bit do indice k, X = porta 0/1/2 (kport)
kbit:   lda k
        cmp #8
        bcc @a
        cmp #16
        bcc @b
        sec
        sbc #16
        tax
        lda bits,x
        ldx #2
        stx kport
        rts
@b:     sec
        sbc #8
        tax
        lda bits,x
        ldx #1
        stx kport
        rts
@a:     tax
        lda bits,x
        ldx #0
        stx kport
        rts

; pulso no pino k (C: L-H-L ; K: H-L-H). tmp = bit, kport = porta
pulse:  ldx kport
        lda mdat,x
        eor tmp
        sta mdat,x
        jsr wrport
        jsr delay
        ldx kport
        lda mdat,x
        eor tmp
        sta mdat,x
        jsr wrport
        rts
wrport: ldx kport
        cpx #2
        beq @c
        lda mdat,x
        txa
        tay
        lda mdat,y
        jmp wrdat
@c:     lda mdat+2
        sta pcdrv
        jmp wrpc

; posicao do soquete -> pino do CI (pins = 14/16/20)
sock2pin:
        sta tmp
        lda pins
        lsr
        sta tmp2           ; n
        lda tmp
        cmp #11
        bcs @r
        ; esquerda: pino = s - (10 - n)
        lda #10
        sec
        sbc tmp2
        sta tmp2+1
        lda tmp
        sec
        sbc tmp2+1
        rts
@r:     ; direita: pino = n + (s - 10)
        lda tmp
        sec
        sbc #10
        clc
        adc tmp2
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
rddat:  jsr portx
        lda $C084,x
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
        lda #$80
        sta pc76
        lda #0
        sta pcmux
        jsr allin
        rts

hwsafe: jsr allin
        lda #$C3
        ldy #3
        jsr wrdat
        rts

allin:  lda #0
        sta pcdrv
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
        jmp wrpc

wrpc:   lda pc76
        ora pcmux
        ora pcdrv
        ldy #2
        jmp wrdat

; le o comparador na linha mux (0..18) -> A (0..3)
readmux:
        lda mux
        cmp #8
        bcs @f
        tax
        lda bits,x
        ldy #4
        jsr wrdat
        jmp @rd
@f:     cmp #16
        bcs @c
        sec
        sbc #8
        tax
        lda bits,x
        ldy #5
        jsr wrdat
        jmp @rd
@c:     sec
        sbc #16
        tax
        lda pcmuxtab,x
        sta pcmux
        jsr wrpc
@rd:    jsr delay
rdcmp:  lda $C100          ; operando alto = $Cn (vem de $D9)
        and #$03
        pha
        lda #0
        ldy #4
        jsr wrdat
        lda #0
        ldy #5
        jsr wrdat
        lda #0
        sta pcmux
        jsr wrpc
        pla
        rts

delay:  ldy #40
@d:     dey
        bne @d
        rts

; ---------------------------------------------------------- tabelas
bits:     .byte $01,$02,$04,$08,$10,$20,$40,$80
pcmuxtab: .byte $08,$10,$20
; nibble -> pino e' saida do Apple? / nivel inicial 1?
isout:    .byte 0,1,1,0,0,0,1,1,1,1,0,0,0,0,0,0
isone:    .byte 0,0,1,0,0,0,0,1,0,1,0,0,0,0,0,0
; indice k -> posicao do soquete
k2pin:    .byte 3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,1,2,19
; PD, linha do GND, linha do VCC ($FF = nao visivel)
pdtab:    .byte $87,7,14, $47,7,15, $C7,7,$FF, $C9,10,$FF, $D2,11,$FF, $E2,12,$FF, 0
expch:    .byte "?01LHZCK"
cmpch:    .byte "ZHL?"           ; 0=meio 1=H 2=L

; ---------------------------------------------------------- variaveis
slot:    .byte 0
slot16:  .byte 0
inlen:   .byte 0
key:     .res 9
keylen:  .byte 0
lastrec: .word 0
lastok:  .byte 0
pins:    .byte 0
pdcode:  .byte 0
nvec:    .word 0
vecno:   .word 0
result:  .byte 0
failvec: .word 0
failpin: .byte 0
failexp: .byte 0
failcmp: .byte 0
k:       .byte 0
kcode:   .byte 0
kport:   .byte 0
mux:     .byte 0
cmpv:    .byte 0
dbit:    .byte 0
mdir:    .res 3
mdat:    .res 3
extra:   .res 2
rd:      .res 3
pcdrv:   .byte 0
pcmux:   .byte 0
pc76:    .byte 0
tmp:     .byte 0
tmp2:    .word 0
cnt:     .word 0
mul:     .word 0
col:     .byte 0
lines:   .byte 0
nfound:  .byte 0
