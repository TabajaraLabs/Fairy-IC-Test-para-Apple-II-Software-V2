# IC TESTER (Fairy / Yih-Lung Enterprises, 1984) — projeto de preservação e ampliação

Placa "UNIVERSAL I.C. TESTER" / "IC TEST CARD" para Apple II + Testool (ZIF de 20 pinos).

## Estrutura
- original/   `Fairy IC Test Card Disk.dsk` (DOS 3.3, original — NUNCA alterar)
- patch/      `IC_Tester_ProDOS_v11.po` + `arquivos_v11/` (ATUAL: v10 + opção D: MEMORY (RAM) = RAMTEST.ENG v1)
              `IC_Tester_ProDOS_v10.po` + `arquivos_v10/` (v9 + ICTDIAG v3 com modo "explorar PD")
              `IC_Tester_ProDOS_v9.po` + `arquivos_v9/` (v8 + menu de entrada igual ao original)
              `IC_Tester_ProDOS_v8.po` + `arquivos_v8/` (Version 2.0 Expanded + busca rápida + COPYRIGHT 1984/2026)
              `IC_Tester_ProDOS_v7.po` + `arquivos_v7/` (v7: busca lenta, ~27 s)
              `IC_Tester_ProDOS_v6.po` + `arquivos_v6/` (v5 + todas as travas neutralizadas)
              `IC_Tester_ProDOS_v5.po` + `arquivos_v5/` (testes originais + ICTDIAG v2 + biblioteca Elnec D/E/F)
              `IC_Tester_ProDOS_v4.po` + `arquivos_v4/` (testador v2 + ICTDIAG v2)
              `IC_Tester_ProDOS_v3.po` + `arquivos_v3/` (ICTDIAG v1: tela T1 estourava as 40 colunas — não usar)
              `IC_Tester_ProDOS_v2.po` + `arquivos_v2/` (v2: testada e funcionando)
              `IC_Tester_ProDOS_v1.po` + `arquivos_v1/` (v1: NÃO usar — opção A/TTL dá sempre OVER)
- manual/     `RAM_Tester_e_Adaptador_v1.pdf` (guia da opção D + adaptador 6116/6264), `build_ram_v1.py`;
              `Fairy_IC_Test_Card_Manual_v2.pdf` (manual redigitado; v2 = fotos da placa original e da alternativa no apêndice), `build_manual_v2.py`, `img/`, `capturas/` (telas do scan)
- analise/    desmontagens, BASIC, fonte do carregador, ferramentas, comparação com o Elnec

## 1. Diagnóstico do disco (v2)
DOS 3.3 sem proteção de disco. A "proteção" são nomes de arquivo com caracteres de controle,
reset desarmado e destruição da página zero do Applesoft. Os três binários ($0800) são autônomos.
A versão ProDOS (ICTESTER.SYSTEM) já existe; ver LEIA-ME_v2.md.
Patch: slot 6 liberado no menu "CARD IN WHICH SLOT" ($086D B5→B6, $086F 3F→4D).

## 1b. Proteção encontrada (2026-11-20) — checksum da tela de texto
Sintoma na v1: tudo roda, mas na opção A (TTL) qualquer CI dá "OVER" no Ctrl-S.
Causa: no início ($082D) o binário soma os 40 bytes de cada uma das 24 linhas da tela de texto
($0400–$07FF, rotina $0EDE) e guarda em uma variável. No disco original quem roda antes é o HELLO4,
cuja tela (arte FAIRY + "WAITING.....") soma $25. Em $1020 o TEST.2 testa:
`LDA $0F67 / CMP #$25 / BEQ ok` — se a soma não for $25, troca o slot ($DA) por $68 e todos os
acessos à placa vão para $C0EC+ (controladora de disco do slot 6): nenhum teste passa, sem mensagem.
- CMOS.2 ($0FB7) e HMOS.2 ($0F54) calculam a soma mas não a usam.
- Segunda trava (TEST.2 $0A3F, CMOS.2 $0A42): compara 256 bytes do texto de copyright com uma cópia
  escondida; se alguém editar o copyright, também desvia para $68. Não alteramos esses textos.
- **Patch v2 (TEST.2):** $1020 `AD 67 0F` → `4C 2F 10` (JMP $102F, pula a verificação).
  Diferenças do TEST.2 v2 para o original: $086D B5→B6, $086F 3F→4D (slot 6), $1020-$1022 (proteção).
- Verificado no simulador: depois de um Ctrl-S, v1 deixa $DA=$68 e a v2 mantém $DA=$10 (slot 1).

## 2. Hardware (deduzido do código, confirmado pelas fotos e pelo manual)
- 3 × MC6821 (PIA) em $C084–$C08F + slot×16:

| Endereço | PIA | Registro |
|---|---|---|
| $C084 / $C085 | PIA1 | PA (dados/DDR) / CRA |
| $C086 / $C087 | PIA1 | PB / CRB |
| $C088 / $C089 | PIA2 | PC / CRC |
| $C08A / $C08B | PIA2 | PD / CRD |
| $C08C / $C08D | PIA3 | PE / CRE |
| $C08E / $C08F | PIA3 | PF / CRF |

  (Escrita de CR=0 seleciona o DDR, CR=4 seleciona o registro de dados — padrão do 6821.)
- **PA/PB/PC0-2** = pinos do soquete. **PD** = código de alimentação (onde VCC e GND são aplicados,
  via CD4066 e transistores). **PE/PF** = saídas de controle (zeradas no início; ligadas ao teste
  de nível/LEVEL; função exata a confirmar).
- Comparadores com trimpots: VR1 = nível H (2,4–4,5 V, padrão 2,6 V), VR2 = nível L (0,3–1,2 V, padrão 0,8 V).
- **Soquete:** ZIF de 20 pinos, CI **alinhado pelo GND** (marcas 14/16/18/20 PIN). Mapa dos pinos:
  - CI de 14 pinos: pinos 1–7 = PA1–PA7; pinos 8–14 = PB0–PB6
  - CI de 16 pinos: pinos 1–8 = PA0–PA7; pinos 9–16 = PB0–PB7
  - CI de 20 pinos: pinos 3–10 = PA0–PA7; pinos 11–18 = PB0–PB7; pinos 1, 2 e 19 → PC0–PC2 (a confirmar na bancada); pino 20 = VCC
- **Códigos de alimentação PD** (rotina $122D, Y=código):

| PD | Uso |
|---|---|
| $87 | 14 pinos, GND 7 / VCC 14 (rotina $122B) |
| $47 | 16 pinos, GND 8 / VCC 16 (rotina $1226) |
| $C7 | 20 pinos, GND 10 / VCC 20 (rotina $1221) |
| $C9 | 7490/92/93: GND 10 / VCC 5 |
| $D2 | 7473/77/78: GND 11 / VCC 4 — 7475/7483: GND 12 / VCC 5 |
| $E2 | 7476: GND 13 / VCC 5 |

## 3. Motor de testes
- Número do CI em BCD: centenas + dezena/unidade (TEST.2: $0F4E/$0F4D; CMOS.2: $0F9E/$0F9D;
  HMOS.2: $0F3B/$0F3A); cadeias CMP/JMP despacham para o handler de cada CI.
- Handler típico: alimentação (JSR $122x) → direções (LDX/LDY tabela, JSR $1243 = IDIR16) →
  ponteiros das tabelas em $D0/$D2(/$D4) → JMP $1060 (2 portas) ou $1155 (3 portas) = GATCHK.
- **GATCHK é orientado a tabela:** cada vetor tem 1 byte por porta, com as entradas E as saídas
  esperadas no mesmo byte; escreve na porta, relê e compara. Exatamente o modelo do Elnec.
- CIs com clock (flip-flops, contadores) têm código próprio.

## 4. Cobertura
- TEST.2: 158 CIs TTL; CMOS.2: 68 CIs 40xx; HMOS.2: 49 CIs 74HC (listas em analise/elnec/).
- O disco é uma versão **anterior/menor** que a anunciada no manual: faltam as 45xx e as memórias CMOS
  (4164, 2114, 2125, 2511, 82S16, 8216, 8T26, 8T28 nunca foram implementadas).
  As memórias TTL existem no TEST.2 (7489, 74189, 74201, 74287, 74288, 74289, 74471, 74472).

## 5. Bibliotecas Elnec (74_ttl.lib, 74_cmos.lib, 4000.lib)
Formato texto: `.NOME PINOS` + vetores com 1 caractere por pino
(0/1 entrada, L/H saída esperada, Z flutuante, C/K pulso de clock, G/V alimentação, X não importa).
Comparação (analise/comparacao_elnec_v1.txt): **179 CIs novos com até 20 pinos**
(37 TTL, 114 74HC/HCT/AC, 28 4000/4500); os de 24 pinos não cabem no soquete.
Quase todos usam a alimentação padrão; os não-padrão (7491, 74141, ...) têm código PD já conhecido.

## 6. Próximos passos (proposta)
1. Confirmar na bancada o mapa de pinos de 20 pinos, os bits de PC e a função de PE/PF.
2. Escrever um motor genérico de vetores (6502, ProDOS) que leia uma biblioteca convertida do Elnec:
   aplica alimentação (PD), direções, entradas, pulsos C/K, lê e compara (inclusive Z com pull-up/down).
3. Conversor PC: .lib do Elnec → tabela binária compacta no volume ProDOS.
4. Integrar no ICTESTER.SYSTEM como opção "D: biblioteca externa", mantendo os testes originais.
5. Memórias (2114 etc.) como módulo à parte.

## 7. Modelo do hardware refinado (2026-11-20, a partir do código)
- **Soquete:** ZIF de 20 posições; a posição 10 (embaixo à esquerda) é GND fixo; as outras 19
  têm, cada uma, um bit de porta e uma linha do multiplexador de nível:
  - posições 3–10 = PA0–PA7 (PA7 = posição do GND, lida como 0)
  - posições 11–18 = PB0–PB7
  - posições 1, 2, 19 = PC0, PC1, PC2 (CI de 20 pinos: pinos 1, 2, 19 — confirmado pelo 74373)
  - posição 20 = VCC dos CIs de 20 pinos
  - CI de p pinos (n = p/2): pino k ≤ n → posição k + (10 − n); pino k > n → posição 10 + (k − n)
- **Multiplexador de nível:** PE0–7, PF0–7 e PC3/PC4/PC5 (um bit por vez) ligam uma posição ao
  comparador de janela (VR1/VR2), lido em **$Cn00** (/IOSEL do slot), bits 0–1; 00 = nível
  intermediário (nem H nem L) = pino flutuante ("Z") ou nível ruim ("LEVEL ERROR").
- **Detecção de Z no original:** conta quantas posições estão na zona intermediária (exige ≥ 3).
- **PC6/PC7:** controle; antes de cada teste o original põe PC7=1 PC6=0 ($12D0); para coletor
  aberto, PC7=0 ($12AD) → provavelmente liga os pull-ups.
- **Códigos PD (VCC na posição / GND extra):** $87 = 17; $47 = 18; $C7 = 20; $C9 = 8/13;
  $D2 = 7/14; $E2 = 7/15; $C3 = repouso. Pinos de alimentação secundários (ex.: VEE do 4051)
  são ligados pela porta lógica (0/1).
- **Cobertura:** os 179 CIs novos do Elnec (≤ 20 pinos) podem ser alimentados com esses códigos
  (177 direto, 4054 e 40123 com pino secundário pela porta).

## 8. ICTDIAG.SYSTEM (diagnóstico, v2) — na imagem IC_Tester_ProDOS_v4.po
Rodar com o **soquete vazio**. Mede sozinho (sem pontas de prova):
- T1 (duas telas: pino em 1, pino em 0): uma linha por bit de porta com os 19 valores do comparador
  (colunas E0–E7, F0–F7, C3–C5), formato fixo de 23 colunas (v1 estourava as 40 colunas).
- T2: comparador e portas com os pinos soltos nas 4 combinações de PC7/PC6 (→ pull-up/down).
- T3: posição de VCC/GND para os 7 códigos PD usados pelo software original (só esses).
Resultado esperado no simulador (modelo ideal): PA0→E0 … PB7→F7, PC0→C3, PC1→C4, PC2→C5.

## 9. Resultado do ICTDIAG v2 na placa real (2026-11-20) — fotos em analise/diag_fotos/
**Comparador ($Cn00 bits 0–1): 1 = H, 2 = L, 0 = nível intermediário (solto/Z).**

**Mapa pino → linha do mux CONFIRMADO** (pino em 0 → "2" exatamente na diagonal):
PA0–7 → E0–7, PB0–7 → F0–7, PC0 → C3, PC1 → C4, PC2 → C5. Nenhum acoplamento, nenhuma linha morta.

**Pinos soltos:**
- Lado PA (posições 3–10) e PC (1, 2, 19) leem sempre H: são portas "A" do 6821, que têm pull-up interno.
- Lado PB (posições 11–18) é porta "B" do 6821 (alta impedância): solto = intermediário (0) com PC7=1.
- PC7=0 → todos os pinos em H (liga pull-ups externos no lado PB) → modo usado pelo original para coletor aberto.
- PC7=1, PC6=0 (padrão dos testes) → lado PB solto fica intermediário; leitura digital PB = FF.
- PC7=1, PC6=1 → lado PB continua intermediário no comparador, mas a leitura digital vira 00 (puxa para baixo fraco).
- Consequência: "Z" só é detectável com certeza no lado PB; no lado PA/PC um Z aparece como H.
  Isso explica o "≥ 3" do teste do 7405: as 3 saídas do lado PB ficam intermediárias.

**Alimentação (PD) — GND também é chaveado (não é fixo!):**

| PD | GND em | VCC em | observado |
|---|---|---|---|
| $C3 | — | — | repouso: nada ligado (posição 10 solta, lida H) |
| $87 | 10 (E7=L) | 17 (F6=H) | 14 pinos |
| $47 | 10 (E7=L) | 18 (F7=H) | 16 pinos |
| $C7 | 10 (E7=L) | 20 (sem linha de mux) | 20 pinos |
| $C9 | 13 (F2=L) | 8 (lado PA, não distinguível) | 7490/92/93 |
| $D2 | 14 (F3=L) | 7 (lado PA) | 7473/75/77/78/83 |
| $E2 | 15 (F4=L) | 7 (lado PA) | 7476 |
Tudo bate com o previsto pelo código.

## 10. Biblioteca Elnec integrada (v5, 2026-11-20)
Imagem `patch/IC_Tester_ProDOS_v5.po` (9 arquivos, 232/280 blocos). Menu novo:
A/B/C = testes originais; **D = Elnec TTL (161 CIs), E = Elnec 74HC/HCT/AC (162), F = Elnec 4000 (84)**.
- `ELNEC.ENG` (motor, $0800, 2,5 KB) + `ELxxx.LIB` (biblioteca, $2000, ~17,5 KB cada).
- Conversor: `analise/ferramentas/elnec2ict_v1.py arquivo.lib SAIDA.LIB "FAMILIA"`.
  Formato ICTL v1: "ICTL", versão, nº de CIs, família; por CI: nome, pinos, código PD, nº de
  vetores (2 bytes) e 10 bytes por vetor (19 nibbles: X 0 1 L H Z C K G V).
- Ficam de fora só os de 24 pinos (7 TTL, 7 HC, 4 da série 4000). 4049/4050: VDD pela porta (como o original).
- Motor: aplica PD, confere GND/VCC (LEVEL ERROR, POWER LOW se falhar), para cada vetor põe dados e
  direções, dá os pulsos C/K pino a pino, e confere cada saída pela leitura digital E pelo comparador
  (L=2, H=1); Z: lado PB precisa ficar intermediário, lado PA/PC não pode ser L.
- Comandos: número do CI (aceita 74LS123, 74HC00, CD4011...), RETURN = repete, S = busca,
  ? = lista, M = menu. Erro mostra vetor, pino do CI, esperado e lido.
- Simulado com modelos funcionais independentes: 7400 OK, 7400 com porta travada = ERRO no pino 8,
  7405 (coletor aberto) OK, 7474 (clock) OK, 4011 OK, soquete vazio = ERRO, 7400 testado como 7404 = ERRO.

### Memória (pergunta: cabe nos programas A/B/C?)
TEST.2 ocupa $0800–$4CFF (17,7 KB); CMOS.2/HMOS.2 $0800–$47FF (16 KB). Sob ProDOS sobra
$4D00–$8FFF (~17 KB). Uma biblioteca inteira (~17,5 KB) + motor (2,5 KB) não cabe junto, mas só os CIs
NOVOS de cada família cabem (poucos KB). Integração possível: desviar o "THIS NO. IS UNAVAILABLE"
($0C72 no TEST.2) para o motor — fica como próximo passo opcional. Outra opção: a memória auxiliar
de 64 KB do IIe.

## 11. Todas as travas neutralizadas (binários v3, imagem v6, 2026-11-20)
Pedido do autor: neutralizar toda trava para preservar o funcionamento (o disco original continua
preservado em original/ e o copyright do fabricante não é removido em lugar nenhum).

| Binário | Trava | Neutralização |
|---|---|---|
| TEST.2 | checksum da tela ($0F67 ≠ $25) → slot vira $68 | $1020 `JMP $102F` (v2) + $1027–$102E → 8×NOP |
| TEST.2 | comparação do texto de copyright (256 bytes, $0CFA × cópia escondida) → slot $68 | $0A47–$0A4E → 8×NOP |
| CMOS.2 | mesma comparação (código morto) | $0A4A–$0A51 → 8×NOP |
| CMOS.2 / HMOS.2 | checksum da tela | calculado mas nunca usado — nada a fazer |
| HMOS.2 | — | não tem trava |

Os 8 bytes neutralizados são sempre `LDA #$68 / STA $DA / LDA #$E3 / STA $D9`, que desviavam a placa para
a controladora de disco do slot 6. Diferenças para o original:
- TEST.2: $086D, $086F (slot 6), $0A47–$0A4E, $1020–$1022, $1027–$102E
- CMOS.2: $086D, $086F, $0A4A–$0A51
- HMOS.2: $086D, $086F

Prova no simulador (texto "UNIVERSAL I.C. TESTER" alterado de propósito + Ctrl-S): v2 → slot $68
(trava ativa); v3 → slot $10 (correto). Base para pôr "V2.0" e o total de CIs na tela.
Também ficam valendo: nomes com caracteres de controle e reset desarmado (só no disco DOS 3.3 original;
a versão ProDOS não usa os programas BASIC).

## 12. Versão 2.0 Expanded — Elnec integrado DENTRO de A/B/C (imagem v7, 2026-11-20)
Imagem `patch/IC_Tester_ProDOS_v7.po` (10 arquivos, 239/280 blocos). Requer 64K (ProDOS).
- A (TTL): 158 Fairy + 37 Elnec = **195 CIs**; B (CMOS 40/45): 68 + 28 = **96**; C (74HC): 49 + 114 = **163**.
- Tela principal: linha 3 "nnn ICS AVAILABLE FOR TEST"; linha 6 "VERSION 2.0 EXPANDED BY TABAJARA LABS"
  (abaixo de "BY YIH-LUNG ENTERPRISES CO.,LTD.", copyright do fabricante mantido).
- Uso igual ao original: Ctrl-C, número (ex.: 74-LS-36), SPACE; Ctrl-S busca também nos CIs do Elnec
  (achou "036," com um 7436 no simulador); Ctrl-L continua igual.
- Famílias que a Fairy recusa (74F, 74ALS...) agora caem no Elnec pelo número (74F00 → 7400).

### Memória (64K, ProDOS)
| Faixa | Conteúdo |
|---|---|
| $0800–$42FF | programa original da Fairy (TEST.2/CMOS.2/HMOS.2) |
| $4300–$4B53 | ELHOOK.ENG (gancho + núcleo do motor, 2,1 KB), sobre o resto de fonte não usado |
| $4F00–~$9470 | biblioteca Elnec da família (ELTTL/EL4000/ELHC.LIB, ~17,5 KB) |
| $B400–$B7FF | buffer de E/S do ProDOS |
| $B800–$BC1F | carregador ICTESTER.SYSTEM v4 (subiu de $9000 para dar lugar à biblioteca) |

### Patches de integração (além das travas e do slot 6)
| Onde | TEST.2 | CMOS.2 | HMOS.2 | Efeito |
|---|---|---|---|---|
| JSR que imprime o copyright ($0946) | → $4300 | → $4306 | → $430C | imprime o copyright + as 2 linhas novas |
| início do "THIS NO. IS UNAVAILABLE" | $0C72 → JMP $4303 | $0C3E → JMP $4309 | $0C5D → JMP $430F | número já convertido (BCD) |
| "prefixo de família recusado" | $0FAE → $4312 | $1548 → $4315 | $0F9B → $4318 | número cru, como digitado |
O gancho procura o CI na biblioteca; se achar, testa e salta para o caminho "passou" ou "falhou" da
própria Fairy (TEST OK / FUNCTION ERROR / bipes / busca / loop); se não achar, executa as instruções
substituídas e segue o fluxo original. Detalhe importante: a rotina de conversão da Fairy altera os
dígitos digitados no lugar, por isso o gancho usa o BCD (despachante) ou o texto cru (prefixo recusado).

Diferenças finais para o original:
- TEST.2: $086D, $086F, $0947–$0948, $0A47–$0A4E, $0C72–$0C74, $0FAF–$0FB0, $1020–$1022, $1027–$102E
- CMOS.2: $086D, $086F, $0947–$0948, $0A4A–$0A51, $0C3E–$0C40, $1549–$154A
- HMOS.2: $086D, $086F, $0947–$0948, $0C5D–$0C5F, $0F9C–$0F9D

### Simulação completa (carregador + Fairy + gancho + biblioteca + placa + CI funcional)
74LS02 (Fairy) OK; 74LS36 com NOR certo (só Elnec) OK; 74LS36 com NAND = FUNCTION ERROR;
74HC37 (só Elnec, opção C) OK; 74LS999 = UNAVAILABLE; 74F00 = OK (Elnec 7400); CD4011 OK; Ctrl-S acha "036,".

## 13. v8 — busca rápida e linha de copyright (2026-11-20)
Teste da v7 no Apple: tudo funcionando, mas o Ctrl-S levava ~27 s (simulador: original 1,9 s, v7 24 s).
- **Causa:** a busca da Fairy varre 000–699 e chama o gancho ~500 vezes (números que ela não conhece);
  a cada chamada o gancho percorria a biblioteca inteira (161 registros).
- **Correção (ELHOOK v3):** mapa de bits de 1000 posições por prefixo ($4E00 = "74"/"40", $4E80 = "45"),
  montado na 1ª chamada; número ausente é descartado com uma leitura de bit. Simulador: **24 s → 3,9 s**
  (o 1,9 s original + os testes reais dos CIs que só existem no Elnec).
- **Copyright:** a linha "COPYRIGHT 1984" ocupava as colunas 26–39 e a 39 é cortada pelo monitor (o "4"
  sumia). Agora: **"COPYRIGHT 1984/2026"** nas colunas 19–37, alinhada com as linhas de cima.
- Memória do gancho: $4300–$4CF0; mapas de bits $4E00–$4EFF; biblioteca a partir de $4F00.
- Bateria repetida no simulador: 74LS02, 74LS36 (Elnec), 74LS36 com chip errado, 74HC37, 74LS999,
  74F00, CD4011 e Ctrl-S — todos corretos.

## 14. v9 — menu de entrada limpo (2026-11-20)
O menu do ICTESTER.SYSTEM (v5) agora é idêntico ao HELLO6 do disquete original: "A: TTL 54/74 SERIES"
(linha 10, coluna 10), "B: CMOS 40/45 SERIES" (12), "C: HCMOS 74HC SERIES" (14) e
"WHICH ONE ? A , B OR C" (linha 17, coluna 13). Teclas escondidas: D/E/F = biblioteca Elnec direta
(com diagnóstico de vetor/pino) e Q = sair para o ProDOS.

## 15. Próxima etapa: memórias RAM (planejado em 2026-11-20 02:00; retomar às 03:21)
Pedido: incluir TODAS as RAMs possíveis, SRAM e DRAM. Fase 1 na bancada (agora): descobrir códigos PD.

| RAM | Pinos | VCC/GND (pino) | Posição no soquete | Código PD |
|---|---|---|---|---|
| 2114, 2147, 4416, 4464 | 18 | 18 / 9 | VCC 19 / GND 10 | desconhecido — hipótese **$07** |
| 4164, 41256 (DRAM) | 16 | 8 / 16 (invertido) | VCC 10 / GND 18 | desconhecido (pode não existir) |
| 2102, 2125 | 16 | 10 / 9 | VCC 12 / GND 11 | desconhecido |
| 7489, 74S189, 74S201 | 16 | 16 / 8 | padrão | já testados pelo TEST.2 |
| 4116 | — | precisa +12/−5 V | — | impossível |
| 6116, 6264 | 24/28 | — | — | não cabem |

Hipótese de decodificação do PD: bits 1–0 = modo (11 = padrão, 01 = VCC8/GND13, 10 = VCC7 + GND por bits 5–4);
no modo padrão bit 2 = GND na posição 10 e bits 7–6 = posição do VCC (10→17, 01→18, 11→20, 00→19?).
Método: soquete vazio, aplicar só códigos candidatos, medir com a ponte do osciloscópio (Documents/Claude/pontes),
uma ponta por vez. Posição 19 é lado PC (pull-up interno) → o comparador não distingue VCC de solto; precisa da ponta.
ICTDIAG v3 (imagem v10): opção 2 = EXPLORAR PD — digita o código em hexa, liga, mostra o comparador nas 19 linhas
e segura ligado até uma tecla (volta para $C3). Medição com a ponta do osciloscópio; terra da ponta no borne GND do Testool.
Fase 2: motor de teste de RAM (marcha; SRAM direto; DRAM com RAS/CAS e refresh por software) integrado em A/B/C.

## 16. Bancada 2026-11-20 03:40 — o PD é um conjunto de 8 chaves independentes
Medições (ICTDIAG v3 "explorar PD", soquete vazio, ponte do osciloscópio, terra no borne GND do Testool):
- $07: comparador 1111111 2 000000 11 111 → GND na posição 10 e VCC nas posições 17 E 18 ao mesmo tempo.
- Posição 19 com $07 e com $C3: igual (4,14 V médio, ruído ~1,8 Vpp) = pull-up interno do 6821; **não há VCC na 19**.
- Posição 20 com $C3 (repouso): 5,4 V médio → **VCC fixo, sempre ligado** (sem chave).

| Bit | Chave | Ativa com |
|---|---|---|
| b0 | VCC posição 7 | 0 |
| b1 | VCC posição 8 | 0 |
| b6 | VCC posição 17 | 0 |
| b7 | VCC posição 18 | 0 |
| b2 | GND posição 10 | 1 |
| b3 | GND posição 13 | 1 |
| b4 | GND posição 14 | 1 |
| b5 | GND posição 15 | 1 |
| — | VCC posição 20 | sempre |
Confere com todos os códigos: $C3 (nada além do VCC 20), $87, $47, $C7, $C9, $D2, $E2, $07.

Consequências para as RAMs:
- **4164 / 41256: inserir GIRADA 180° (chanfro para baixo)**, encostada embaixo: VCC (pino 8) → posição 18,
  GND (pino 16) → posição 10 = código $47 (já validado). Pino k (1–8) → posição 10+k; pino k (9–16) → posição k−6.
- **2114 / 2147 (18 pinos, normal):** VCC (pino 18) cai na posição 19, sem chave → **jumper entre os pinos 19 e 20 do ZIF**
  (ou soquete adaptador); GND na 10 → código $C7. Posição 19 (PC2) fica sempre como entrada.
- **4416 / 4464 (18 pinos): girada 180°** + o mesmo jumper 19–20: VCC (pino 9) → 19, GND (pino 18) → 10.
- 2102/2125: sem combinação possível. 4116: impossível (±5/12 V). 6116/6264: não cabem.

## 17. v11 — opção D: MEMORY (RAM) (2026-11-20 04:15)
Menu principal (ICTESTER.SYSTEM v6): nova linha visível "D: MEMORY (RAM)" e "WHICH ONE ? A , B , C OR D".
Teclas escondidas do Elnec avulso passaram para **E** (TTL), **F** (HC) e **G** (4000); Q = sair.
ELNEC.ENG v2: corrigido o retorno ao menu (era $9000, agora $B800).

RAMTEST.ENG v1 (fonte `analise/fonte/ramtest_v1.s`, carregado em $0800, tabelas em $3000-$377F):
pede o slot, lista as 8 memórias e, ao escolher, **desenha o ZIF** (posição, pino do chip em cada furo, chanfro "()",
jumper 19-20). ESPAÇO liga a alimentação e testa; ESC volta.

| Chip | Orientação | Jumper 19-20 | PD | Tempo (sim.) |
|---|---|---|---|---|
| 2114 | normal | sim | $C7 | ~4 s |
| 2147 | normal | sim | $C7 | ~12 s |
| 4164 | girada 180° | não | $47 | ~1 min 40 s |
| 41256 | girada 180° | não | $47 | ~7 min |
| 4416 | girada 180° | sim | $C7 | ~40 s |
| 4464 | girada 180° | sim | $C7 | ~2 min 25 s |
| 6116 / 6264 | adaptador | — | $C7 | ~6 s / ~22 s |

Testes: SRAM = xadrez + invertido em todos os endereços + teste das linhas de endereço (bit andando).
DRAM = por linha (o acesso às colunas mantém a linha; refresh por software é impossível: varrer 256 linhas leva ~25 ms);
xadrez + invertido; depois linhas de endereço ROW e COL. /RAS baixo ~75 µs por ciclo (datasheet: máx. 10 µs) —
é o ponto frágil; se uma DRAM boa falhar sempre, é isto.
Escrita SRAM controlada pelo /CS (WE desce antes) para não haver briga no barramento; dados da porta são escritos antes
de virar saída (sem glitch de RAS/WE ao ligar).
Mensagens: TEST OK ! / LEVEL ERROR, POWER LOW / TEST ERROR END, STEP n + endereço (ou ROW/COL) EXP/GOT / BAD ADDR BIT n.

Adaptador 6116/6264: plugue de 20 pinos no ZIF + soquete 28 + 74HC574. PA0-6 = A0-A6; PB0-7 = D0-D7 e entrada do latch;
PC0 = CLK do latch (Q0-Q5 = A7-A12); PC1 = /OE; PC2 = /WE; /CE1 = GND; CE2 = VCC; VCC da posição 20, GND da 10.
J1 no pino 23 do soquete: 6264 = Q4 (A11), 6116 = PC2 (/WE). A 6116 entra encostada embaixo (pino 1 no pino 3 do soquete).
Lista completa de ligações no PDF.

Simulação (`analise/ferramentas/simram_v1.py`): placa com PD por chaves + modelos de SRAM, DRAM (RAS/CAS, retenção 2 s)
e adaptador escritos a partir dos datasheets. Aprovados: todos os 8 chips (DRAM completas). Reprovados corretamente:
bit preso, linha de endereço aberta (inclusive A8 da 41256 e A11/A12 do adaptador), chip morto, chip invertido.
Nenhum conflito de barramento no modelo. Falta: testar no Apple com as memórias reais e montar o adaptador.

## Estado
- 2026-11-19: v1 ProDOS gerada;
- 2026-11-20: v1 testada no IIe: roda, mas TTL sempre dá OVER → achada a proteção da tela; v2 gerada;
- 2026-11-20: **v2 testada no Apple IIe com a placa: FUNCIONA** (74LS02 reconhecido no Ctrl-S e TEST OK). Versão ProDOS concluída.
  manual v1 em PDF; hardware e motor mapeados;
  comparação com o Elnec feita; manual v2 com as fotos das duas versões da placa.
- 2026-11-20: hardware mapeado pelo código (soquete, mux de nível, PD); ICTDIAG v1 gerado (falta rodar no Apple).
- 2026-11-20: ICTDIAG v2 (telas de largura fixa, cabeçalho de 2 linhas) — falta rodar no Apple.
- 2026-11-20: ICTDIAG v2 rodado na placa real: mapa do soquete, comparador (1=H 2=L 0=meio), pull-ups e códigos PD CONFIRMADOS. Próximo: motor de vetores + conversor Elnec.
- 2026-11-20: v5 com biblioteca Elnec (D/E/F, 407 CIs) — simulada OK, falta testar no Apple.
- 2026-11-20: v6 — todas as travas neutralizadas (TEST.2: tela + copyright; CMOS.2: copyright). Plano aprovado: integrar o Elnec dentro de A/B/C com "V2.0" e total de CIs na tela (A=195, B=96, C=163).
- 2026-11-20: opção D da v5/v6 testada no Apple: funciona. v7 = Version 2.0 Expanded (Elnec dentro de A/B/C, 454 CIs) — simulada OK, falta testar no Apple.
- 2026-11-20: **v7 rodando no Apple IIe**: tela "195 ICS AVAILABLE FOR TEST" / "VERSION 2.0 EXPANDED BY TABAJARA LABS" OK; Ctrl-S achou 005, 006, 016 (equivalentes coletor aberto). Obs.: o "4" de COPYRIGHT 1984 fica na coluna 40, cortada pelo monitor LCD (igual no programa original).
- 2026-11-20: v8 — busca Ctrl-S de ~27 s para ~4 s (mapa de bits) e linha "COPYRIGHT 1984/2026" visível. Falta testar no Apple.
- 2026-11-20: v9 — menu igual ao original (D/E/F e Q escondidas).
- 2026-11-20 02:00: plano das RAMs registrado; trabalho pausado a pedido até 03:21 (próximo passo: bancada para descobrir códigos PD).
- 2026-11-20 03:30: retomado; ICTDIAG v3 (explorar PD) pronto na imagem v10 para a bancada.
- 2026-11-20 03:50: bancada — PD decifrado (8 chaves), posição 20 = VCC fixo; plano das RAMs (4164 girada; 2114 com jumper 19–20).
- 2026-11-20 04:15: v11 — opção D: MEMORY (RAM) (8 memórias, desenho do ZIF, adaptador 6116/6264); simulada OK, falta testar no Apple.
- Pendente (pedido para o fim do projeto, de manhã): PDF detalhado explicando como a placa descobre qual CI está no soquete (Ctrl-S).
