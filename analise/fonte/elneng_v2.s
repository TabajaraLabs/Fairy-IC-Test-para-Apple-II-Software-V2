; =====================================================================
; ELNEC.ENG v2 - motor de testes por vetores para a placa IC TEST CARD
; (Fairy / Yih-Lung 1984), usando bibliotecas convertidas do Elnec.
;
; Carregado pelo ICTESTER.SYSTEM em $0800; biblioteca (ICTL) em $2000.
; Volta ao menu com JMP $9000 (carregador residente).
;
; Hardware (confirmado com o ICTDIAG na placa real):
;   PIAs em $C084+slot*16: PA $84/$85, PB $86/$87, PC $88/$89,
;   PD $8A/$8B, PE $8C/$8D, PF $8E/$8F (CR=0 -> DDR, CR=4 -> dados)
;   posicoes do soquete: indice 0-7 = PA0-7, 8-15 = PB0-7, 16-18 = PC0-2
;   mux de nivel: PE0-7 / PF0-7 / PC3,PC4,PC5 (um por vez)
;   comparador em $Cn00 bits 0-1: 1 = H, 2 = L, 0 = intermediario
;   PC7=1 PC6=0 = modo padrao dos testes
;
; Vetor: 10 bytes = 19 nibbles (indice 0..18):
;   0=X 1='0' 2='1' 3=L 4=H 5=Z 6=C 7=K 8=G secundario 9=V secundario
; =====================================================================

LIB     = $2000
MENU    = $B800          ; v2: carregador v4+ vive em $B800
HOME    = $FC58
COUT    = $FDED
CROUT   = $FD8E
RDKEY   = $FD0C
GETLN   = $FD6A
PRBYTE  = $FDDA
WAIT    = $FCA8
BELL    = $FF3A
INBUF   = $0200

ptr     = $06              ; ponteiro geral (impressao)
rec     = $08              ; registro do CI atual
vp      = $EB              ; ponteiro do vetor atual
lp      = $ED              ; ponteiro de varredura da biblioteca

        .org $0800

start:  cld
        ldx #$FF
        txs
        jsr HOME
        ; confere a biblioteca
        lda LIB
        cmp #'I'
        bne badlib
        lda LIB+1
        cmp #'C'
        bne badlib
        jmp askslot
badlib: ldx #<t_badlib
        ldy #>t_badlib
        jsr print
        jsr RDKEY
        jmp MENU

askslot:
        ldx #<t_slot
        ldy #>t_slot
        jsr print
@k:     jsr RDKEY
        and #$7F
        cmp #'1'
        bcc @k
        cmp #'8'
        bcs @k
        pha
        ora #$80
        jsr COUT
        pla
        and #$07
        sta slot
        asl
        asl
        asl
        asl
        sta slot16
        lda slot
        ora #$C0
        sta rdcmp+2
        jsr hwinit

; ---------------------------------------------------------- tela principal
banner: jsr HOME
        ldx #<t_ban1
        ldy #>t_ban1
        jsr print
        ; familia (tamanho em LIB+7, texto em LIB+8)
        ldx #0
@f:     cpx LIB+7
        beq @fe
        lda LIB+8,x
        ora #$80
        jsr COUT
        inx
        bne @f
@fe:    lda #')'|$80
        jsr COUT
        jsr CROUT
        lda LIB+5          ; nº de CIs (< 256)
        jsr prdec3
        ldx #<t_ban2
        ldy #>t_ban2
        jsr print

prompt: jsr CROUT
        lda #'C'|$80
        jsr COUT
        lda #'I'|$80
        sta $33            ; prompt do GETLN
        jsr GETLN          ; X = tamanho, texto em $0200
        stx inlen
        cpx #0
        bne havein
        ; RETURN vazio: repete o ultimo teste
        lda lastok
        beq prompt
        jmp dotest
havein: lda INBUF
        and #$7F
        cmp #'?'
        bne @n1
        jmp listall
@n1:    cmp #'M'
        bne @n2
        ldx inlen
        cpx #1
        bne @n2
        jsr hwsafe
        jmp MENU
@n2:    cmp #'S'
        bne @n3
        ldx inlen
        cpx #1
        bne @n3
        jmp search
@n3:    jsr normalize      ; -> key[], keylen
        lda keylen
        beq prompt
        jsr findic         ; -> rec / C=1 se nao achou
        bcc @found
        ldx #<t_nf
        ldy #>t_nf
        jsr print
        jmp prompt
@found: lda rec
        sta lastrec
        lda rec+1
        sta lastrec+1
        lda #1
        sta lastok
dotest: lda lastrec
        sta rec
        lda lastrec+1
        sta rec+1
        ldx #<t_testing
        ldy #>t_testing
        jsr print
        jsr prname
        lda #' '|$80
        jsr COUT
        lda #'.'|$80
        jsr COUT
        jsr COUT
        jsr COUT
        jsr runtest
        jsr report
        jmp prompt

; ---------------------------------------------------------- relatorio
report: lda result
        bne @bad
        ldx #<t_ok
        ldy #>t_ok
        jsr print
        jsr longbeep
        rts
@bad:   cmp #2
        bne @err
        ldx #<t_power
        ldy #>t_power
        jsr print
        jsr beep5
        rts
@err:   ldx #<t_err
        ldy #>t_err
        jsr print
        jsr CROUT
        ldx #<t_vec
        ldy #>t_vec
        jsr print
        lda failvec+1
        jsr PRBYTE
        lda failvec
        jsr PRBYTE
        ldx #<t_pin
        ldy #>t_pin
        jsr print
        lda failpin
        jsr prdec
        ldx #<t_exp
        ldy #>t_exp
        jsr print
        ldx failexp
        lda expch,x
        jsr COUT
        ldx #<t_got
        ldy #>t_got
        jsr print
        ldx failcmp
        lda cmpch,x
        jsr COUT
        jsr beep5
        rts

; ---------------------------------------------------------- busca (S)
search: ldx #<t_search
        ldy #>t_search
        jsr print
        lda #0
        sta nfound
        lda #<LIB
        clc
        adc #8
        adc LIB+7
        sta lp
        lda #>LIB
        adc #0
        sta lp+1
@lp:    ldy #0
        lda (lp),y
        beq @end
        lda lp
        sta rec
        lda lp+1
        sta rec+1
        jsr runtest
        lda result
        bne @nx
        lda #' '|$80
        jsr COUT
        jsr prname
        inc nfound
@nx:    jsr nextrec
        lda $C000          ; tecla interrompe
        bpl @lp
        bit $C010
@end:   lda nfound
        bne @o
        ldx #<t_none
        ldy #>t_none
        jsr print
@o:     ldx #<t_over
        ldy #>t_over
        jsr print
        jmp prompt

; ---------------------------------------------------------- lista (?)
listall:
        lda #<LIB
        clc
        adc #8
        adc LIB+7
        sta lp
        lda #>LIB
        adc #0
        sta lp+1
        lda #0
        sta col
        sta lines
        jsr CROUT
@lp:    ldy #0
        lda (lp),y
        beq @end
        lda lp
        sta rec
        lda lp+1
        sta rec+1
        jsr prname
        ; preenche ate 7 colunas
        ldy #0
        lda (rec),y
        tax
@pad:   cpx #7
        bcs @pd
        lda #' '|$80
        jsr COUT
        inx
        bne @pad
@pd:    inc col
        lda col
        cmp #5
        bne @nx
        lda #0
        sta col
        jsr CROUT
        inc lines
        lda lines
        cmp #20
        bne @nx
        lda #0
        sta lines
        ldx #<t_more
        ldy #>t_more
        jsr print
        jsr RDKEY
        jsr CROUT
@nx:    jsr nextrec
        jmp @lp
@end:   jsr CROUT
        jmp prompt

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

; ---------------------------------------------------------- nome / busca
; normaliza a entrada: tira letras iniciais (CD, SN, HEF...); depois de "74"
; tira as letras da familia (LS, HC, HCT, S, F, ALS...). Fica: digitos + sufixo.
normalize:
        ldx #0
        ldy #0
@skip:  cpx inlen          ; pula letras/espacos/traços iniciais
        beq @done
        lda INBUF,x
        and #$7F
        cmp #'0'
        bcc @sk1
        cmp #'9'+1
        bcc @dig
@sk1:   inx
        bne @skip
@dig:   ; copia digitos; se os 2 primeiros forem "74", pula letras logo apos
        lda INBUF,x
        and #$7F
        cmp #'0'
        bcc @oth
        cmp #'9'+1
        bcs @oth
        sta key,y
        iny
        inx
        cpy #2
        bne @chk
        lda key
        cmp #'7'
        bne @chk
        lda key+1
        cmp #'4'
        bne @chk
@lt:    cpx inlen          ; pula letras de familia
        beq @done
        lda INBUF,x
        and #$7F
        cmp #'A'
        bcc @chk
        inx
        bne @lt
@chk:   cpx inlen
        beq @done
        cpy #8
        bcs @done
        jmp @dig
@oth:   cmp #'-'
        beq @ign
        cmp #' '
        beq @ign
        cmp #'a'
        bcc @up
        and #$DF
@up:    sta key,y          ; sufixo (ex.: 4063B)
        iny
@ign:   inx
        jmp @chk
@done:  sty keylen
        rts

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
rdcmp:  lda $C100          ; operando alto = $Cn
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

; ---------------------------------------------------------- som / texto
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

; imprime A (0..255) em decimal
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
        jsr COUT
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
        jsr COUT
        pla
        ora #'0'|$80
        jmp COUT
@n:     pla
; imprime A (0..99) em decimal
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

t_badlib: .byte "BIBLIOTECA NAO CARREGADA.",$0D,"TECLE ALGO.",0
t_slot:   .byte "IC TESTER - BIBLIOTECA ELNEC",$0D,$0D
          .byte "SLOT DA PLACA (1-7)? ",0
t_ban1:   .byte "IC TESTER - ELNEC (",0
t_ban2:   .byte " CIS. SOQUETE: GND EMBAIXO.",$0D
          .byte "NUMERO DO CI (EX: 74LS123, 4094)",$0D
          .byte "RETURN=REPETE  S=BUSCA  ?=LISTA  M=MENU",0
t_nf:     .byte $0D,"NAO ESTA NA BIBLIOTECA.",0
t_testing:.byte "TESTANDO ",0
t_ok:     .byte $0D,"RESULTADO: TEST OK !",0
t_err:    .byte $0D,"RESULTADO: TEST ERROR",0
t_power:  .byte $0D,"LEVEL ERROR, POWER LOW (CI INVERTIDO?)",0
t_vec:    .byte "VETOR $",0
t_pin:    .byte " PINO ",0
t_exp:    .byte " ESPERADO ",0
t_got:    .byte " LIDO ",0
t_search: .byte $0D,"BUSCANDO (TECLA PARA):",0
t_none:   .byte " NENHUM",0
t_over:   .byte $0D,"OVER",0
t_more:   .byte "-- MAIS --",0

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
