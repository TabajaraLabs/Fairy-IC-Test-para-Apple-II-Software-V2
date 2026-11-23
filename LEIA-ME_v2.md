# IC TESTER (Yu Fung / Yih-Lung Enterprises, 1984) — versão ProDOS

Software da placa "UNIVERSAL I.C. TESTER" para Apple II, convertido de DOS 3.3 para ProDOS
para rodar do HD (BOOTI, CFFA etc.) sem disquete.

## Estrutura
- original/  `Fairy IC Test Card Disk.dsk`: imagem do disquete original (NUNCA alterar)
- analise/   desmontagens (`TEST2.lst`, `CMOS2.lst`, `HMOS2.lst`), os BASIC destokenizados (`basic/`),
             o fonte do carregador (`fonte/ictester_v1.s`) e as ferramentas Python (`ferramentas/`)
- patch/     `IC_Tester_ProDOS_v1.po` (imagem ProDOS 140K) e `arquivos_v1/` (os arquivos soltos)

## Diagnóstico (2026-11-19)
O disco **não é ProDOS: é DOS 3.3** (VTOC na T$11, volume 254). E não tem proteção de disco de
verdade: o RWTS é o padrão (prólogos D5 AA 96 / D5 AA AD), sem trilha especial e sem leitura de
assinatura. A "proteção" é de outro tipo:

1. **Nomes de arquivo com caracteres de controle invisíveis.** O boot roda uma cadeia de BASIC:
   `HELLO` → `HELLO3` (logo HGR) → `HELLO2` (tela HGR) → `HELLO6` (menu A/B/C) →
   `HELLO4`/`HELLO5`/`HELLO7` → `BRUN TEST.2` / `CMOS.2` / `HMOS.2`.
   Quase todos os nomes têm ^C ^D ^E ^O ^Q ^R ^W ^F escondidos (ex.: `HELLO2^Q^R^E^O^D^W^C`).
   Copiadores e conversores para ProDOS/CFFA não preservam esses nomes, porque o ProDOS nem
   aceita caracteres de controle em nome de arquivo. Aí a cadeia quebra.
2. **Anti-reset.** `POKE 1010,28 : POKE 1011,1 : POKE 1012,255`: o vetor de reset fica com o
   byte de power-up inválido, e o RESET reinicia a máquina.
3. **Os binários destroem a página zero do Applesoft** ($B0–$C6, onde fica a CHRGET). Qualquer
   volta ao BASIC termina em travamento ou no monitor.

Os três binários são autônomos: carregam em $0800 e só usam a ROM do monitor (COUT1 $FDF0,
RDKEY $FD35, HOME, VTAB, PRBYTE, SETINV/SETNORM) e o I/O da placa (`STA/LDA $C084-$C08F,X`,
com X = slot×16 em $DA). Não chamam DOS nem Applesoft.

| Arquivo | Família | Carga | Tamanho |
|---|---|---|---|
| TEST.2 | TTL 54/74 ("PART-II") | $0800 | $4500 |
| CMOS.2 | CMOS 40/45 ("SAMPLE") | $0800 | $4000 |
| HMOS.2 | HCMOS 74HC ("CMOS-74C") | $0800 | $4000 |

(Atenção: o menu do HELLO6 manda "B: CMOS" para `HELLO5` = BRUN CMOS.2 e "C: HCMOS" para
`HELLO7` = BRUN HMOS.2.)

De $4300 em diante há restos do fonte em assembly que ficaram no buffer do editor (rótulos
TEST287, PECTRL, PEDIR, PCIO...). Isso indica que a placa usa portas tipo PIA (6821/6522).

## A solução: ICTESTER.SYSTEM
Carregador ProDOS (`analise/fonte/ictester_v1.s`, montado com ca65/ld65):
- carregado em $2000, se reloca para $9000 (fora da área $0800–$4CFF dos binários)
- desliga 80 colunas e ALTCHAR, faz SETVID/SETKBD e mostra o menu A/B/C (+ Q para sair)
- abre o binário escolhido pelo MLI (buffer de E/S em $9400), lê em $0800 e salta para $0800
- o RESET passa a voltar ao menu (vetor $3F2 válido apontando para $9000)
- se o prefixo estiver vazio, usa o diretório do caminho em $0280 ou o volume do último dispositivo

### Patch nos binários (2 bytes, igual nos três)
O menu "CARD IN WHICH SLOT ?" testava a tecla 5 duas vezes e nunca a 6 (slot do drive).
A rotina do slot 6 existia em $08BD, só que inalcançável.
- $086D: `B5` → `B6`   (CMP #'6')
- $086F: `3F` → `4D`   (BEQ $08BD)
Agora a placa pode ficar no slot 6, o que é útil num IIe sem drive.

## Como usar
- **Opção 1:** monte `IC_Tester_ProDOS_v1.po` na BOOTI como um segundo volume e rode
  `ICTESTER.SYSTEM` pelo launcher (Bitsy Bye etc.). A imagem **não é inicializável**, porque não
  contém o arquivo PRODOS.
- **Opção 2:** copie os 4 arquivos de `patch/arquivos_v1/` para uma pasta do HD (CiderPress II:
  ICTESTER.SYSTEM tipo SYS $FF aux $2000; TEST.2/CMOS.2/HMOS.2 tipo BIN $06 aux $0800).
  Os 4 arquivos precisam ficar na mesma pasta.
- **Opção 3 (boot direto):** copie um PRODOS para dentro do volume. Se ICTESTER.SYSTEM for o
  primeiro *.SYSTEM do diretório, ele roda sozinho no boot.

## Testes
- Simulador 6502 (py65, `ferramentas/sim.py`) com MLI e ROM interceptados: menu → OPEN/READ →
  JMP $0800 → pergunta do slot (1–7, incluindo o 6) → tela principal do testador. Funcionou nos
  três modos (A, B e C).
- Falta testar no Apple real com a placa. O campo do número do CI é lido da memória de tela, o
  que o simulador não reproduz.

## Estado
- 2026-11-19: v1 gerada, aguardando teste no IIe.
