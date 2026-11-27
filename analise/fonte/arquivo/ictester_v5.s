; =====================================================================
; ICTESTER.SYSTEM  -  carregador ProDOS para o software da placa
; "UNIVERSAL I.C. TESTER" (Yih-Lung Enterprises / Yu Fung, 1984)
;
; O software original e' DOS 3.3: um encadeamento de programas Applesoft
; com nomes de arquivo contendo caracteres de controle invisiveis, que
; termina em BRUN de um de tres binarios ($0800):
;     TEST.2  -> TTL 54/74      CMOS.2 -> CMOS 40/45     HMOS.2 -> 74HC
; Esses binarios so' usam a ROM do monitor e o I/O da placa; nao usam
; DOS nem Applesoft. Este carregador faz o papel do HELLO6 (menu A/B/C):
; carrega o binario escolhido em $0800 via MLI e salta para ele.
;
; Mapa de memoria:
;   $2000       ponto de entrada (ProDOS carrega o .SYSTEM aqui)
;   $B800-$BBFF este codigo, depois de relocado (v4: sobe para dar lugar a biblioteca)
;   $B400-$B7FF buffer de E/S do ProDOS para o OPEN
;   $0800-$4CFF binario do testador
; RESET volta para o menu (vetor $3F2 aponta para MENU).
; =====================================================================

MLI      = $BF00
DEVNUM   = $BF30
PATH280  = $0280          ; caminho do .SYSTEM deixado pelo launcher
HOME     = $FC58
COUT     = $FDED
CROUT    = $FD8E
RDKEY    = $FD0C
PRBYTE   = $FDDA
SETNORM  = $FE84
INIT     = $FB2F
SETVID   = $FE93
SETKBD   = $FE89
BELL     = $FF3A
SOFTEV   = $03F2
PWREDUP  = $03F4

LOADADR  = $0800
MAXLEN   = $6000          ; ate $7FFF (biblioteca em $2000: max 24 KB)
LIBADR   = $2000
HOOKADR  = $4300
HLIBADR  = $4F00
IOBUF    = $B400
RUNADR   = $B800

ptr      = $06            ; ponteiro p/ imprimir strings (ZP livre)

        .segment "CODE"
        .org $2000
; ------------------------------------------------- reloca $2000 -> $9000
entry:  cld
        ldy #0
@cp:    lda image,y
        sta RUNADR,y
        lda image+$100,y
        sta RUNADR+$100,y
        lda image+$200,y
        sta RUNADR+$200,y
        lda image+$300,y
        sta RUNADR+$300,y
        lda image+$400,y
        sta RUNADR+$400,y
        iny
        bne @cp
        jmp start

image:
        .org RUNADR
; ------------------------------------------------- inicializacao (uma vez)
start:  jsr fixprefix
; ------------------------------------------------- menu (RESET cai aqui)
menu:   cld
        ldx #$FF
        txs
        sta $C051          ; TEXT
        sta $C054          ; PAGE1
        sta $C00C          ; 80COL off (IIe; inofensivo no II Plus)
        sta $C000          ; 80STORE off
        sta $C00E          ; ALTCHAR off
        jsr SETNORM
        jsr INIT
        jsr SETVID
        jsr SETKBD
        lda #<menu         ; RESET -> menu
        sta SOFTEV
        lda #>menu
        sta SOFTEV+1
        eor #$A5
        sta PWREDUP
        jsr HOME
        lda #<txtmenu
        ldy #>txtmenu
        jsr print
@key:   jsr RDKEY
        and #$DF           ; maiuscula
        cmp #'A'|$80
        beq @a
        cmp #'B'|$80
        beq @b
        cmp #'C'|$80
        beq @c
        cmp #'D'|$80
        beq @d
        cmp #'E'|$80
        beq @e
        cmp #'F'|$80
        beq @f
        cmp #'Q'|$80
        bne @nq
        jmp quit
@nq:    jsr BELL
        jmp @key
@a:     ldx #<nameA
        ldy #>nameA
        lda #<libD
        sta libptr
        lda #>libD
        sta libptr+1
        jmp load
@b:     ldx #<nameB
        ldy #>nameB
        lda #<libF
        sta libptr
        lda #>libF
        sta libptr+1
        jmp load
@c:     ldx #<nameC
        ldy #>nameC
        lda #<libE
        sta libptr
        lda #>libE
        sta libptr+1
        jmp load
@d:     lda #<libD
        ldy #>libD
        jmp loadel
@e:     lda #<libE
        ldy #>libE
        jmp loadel
@f:     lda #<libF
        ldy #>libF
        jmp loadel
; ------------------------------------------------- carrega e executa
load:   jsr loadfile   ; programa original em $0800
        bcc *+5
        jmp err
        lda #<HOOKADR
        sta p_read+2
        lda #>HOOKADR
        sta p_read+3
        ldx #<nameHook
        ldy #>nameHook
        jsr loadfile       ; ELHOOK.ENG em $4300
        bcc *+5
        jmp err
        lda #<HLIBADR
        sta p_read+2
        lda #>HLIBADR
        sta p_read+3
        ldx libptr
        ldy libptr+1
        jsr loadfile       ; biblioteca da familia em $4F00
        bcc *+5
        jmp err
        lda #<LOADADR
        sta p_read+2
        lda #>LOADADR
        sta p_read+3
        jsr HOME
        jmp LOADADR        ; nao volta

; motor ELNEC.ENG em $0800 + biblioteca (A/Y = nome) em $2000
loadel: sta libptr
        sty libptr+1
        lda #<LOADADR
        sta p_read+2
        lda #>LOADADR
        sta p_read+3
        ldx #<nameEng
        ldy #>nameEng
        jsr loadfile
        bcs err
        lda #<LIBADR
        sta p_read+2
        lda #>LIBADR
        sta p_read+3
        ldx libptr
        ldy libptr+1
        jsr loadfile
        bcs err
        lda #<LOADADR      ; restaura destino padrao
        sta p_read+2
        lda #>LOADADR
        sta p_read+3
        jsr HOME
        jmp LOADADR

; OPEN/READ/CLOSE do arquivo X/Y no destino de p_read. C=1 erro (A)
loadfile:
        stx p_open+1
        sty p_open+2
        jsr MLI
        .byte $C8          ; OPEN
        .word p_open
        bcs @lfe
        lda p_open+5
        sta p_read+1
        sta p_close+1
        jsr MLI
        .byte $CA          ; READ
        .word p_read
        php
        pha
        jsr MLI
        .byte $CC          ; CLOSE
        .word p_close
        pla
        plp
@lfe:   rts

quit:   jsr MLI
        .byte $65          ; QUIT
        .word p_quit
        brk

err:    pha
        lda #<LOADADR      ; restaura destino padrao
        sta p_read+2
        lda #>LOADADR
        sta p_read+3
        pla
        pha
        jsr CROUT
        lda #<txterr
        ldy #>txterr
        jsr print
        pla
        jsr PRBYTE
        lda #<txtkey
        ldy #>txtkey
        jsr print
        jsr RDKEY
        jmp menu

; ------------------------------------------------- prefixo
; Se o prefixo estiver vazio, usa o diretorio de $0280 (caminho do
; .SYSTEM deixado pelo launcher; no boot do ProDOS e' o nome do volume).
fixprefix:
        jsr MLI
        .byte $C7          ; GET_PREFIX
        .word p_gpfx
        bcs @done
        lda pfxbuf
        bne @done          ; ja tem prefixo
        lda PATH280
        beq @online
        cmp #65
        bcs @online
        tax                ; X = comprimento
@scan:  lda PATH280,x      ; procura a ultima '/'
        and #$7F
        cmp #'/'
        beq @slash
        dex
        bne @scan
        beq @online
@slash: cpx #1
        bne @setlen        ; "/VOL/.../ARQ" -> "/VOL/..."
        ldx PATH280        ; so' "/VOL": usa tudo
@setlen:stx PATH280
        jsr MLI
        .byte $C6          ; SET_PREFIX
        .word p_spfx
@done:  rts
@online:                   ; ultimo dispositivo usado -> nome do volume
        lda DEVNUM
        sta p_onl+1
        jsr MLI
        .byte $C5          ; ON_LINE
        .word p_onl
        bcs @done
        lda pfxbuf+1
        and #$0F
        beq @done
        tax
        inx
        stx pfxbuf         ; comprimento = nome + '/'
        lda #'/'
        sta pfxbuf+1
        jsr MLI
        .byte $C6
        .word p_spfx2
        rts

; ------------------------------------------------- imprime string (0=fim)
print:  sta ptr
        sty ptr+1
        ldy #0
@lp:    lda (ptr),y
        beq @end
        ora #$80
        jsr COUT
        iny
        bne @lp
        inc ptr+1
        bne @lp
@end:   rts

; ------------------------------------------------- parametros MLI
p_open: .byte 3
        .word 0            ; caminho
        .word IOBUF
        .byte 0            ; ref
p_read: .byte 4
        .byte 0
        .word LOADADR
        .word MAXLEN
        .word 0
p_close:.byte 1
        .byte 0
p_quit: .byte 4,0,0,0,0,0,0
p_gpfx: .byte 1
        .word pfxbuf
p_spfx: .byte 1
        .word PATH280
p_spfx2:.byte 1
        .word pfxbuf
p_onl:  .byte 2
        .byte 0
        .word pfxbuf+1     ; ON_LINE grava (drv/len)+nome a partir daqui

nameA:  .byte 6,"TEST.2"
nameB:  .byte 6,"CMOS.2"
nameC:  .byte 6,"HMOS.2"
nameEng:.byte 9,"ELNEC.ENG"
nameHook:.byte 10,"ELHOOK.ENG"
libD:   .byte 9,"ELTTL.LIB"
libE:   .byte 8,"ELHC.LIB"
libF:   .byte 10,"EL4000.LIB"
libptr: .word 0

txtmenu:                   ; igual a tela original (HELLO6 do disquete da Fairy)
        .byte $0D,$0D,$0D,$0D,$0D,$0D,$0D,$0D,$0D
        .byte "         A: TTL 54/74 SERIES",$0D,$0D
        .byte "         B: CMOS 40/45 SERIES",$0D,$0D
        .byte "         C: HCMOS 74HC SERIES",$0D,$0D,$0D
        .byte "            WHICH ONE ? A , B OR C ",0
        ; teclas escondidas: D/E/F = biblioteca Elnec direta (diagnostico
        ; detalhado de vetor e pino), Q = sair para o ProDOS
txterr: .byte "ERRO PRODOS $",0
txtkey: .byte $0D,"TECLE ALGO...",0

pfxbuf: .res 66
