# IC TESTER (Fairy / Yih-Lung Enterprises, 1984) — projeto de preservação e ampliação

Placa "UNIVERSAL I.C. TESTER" / "IC TEST CARD" para Apple II + Testool (ZIF de 20 pinos).

## Estrutura
- original/   `Fairy IC Test Card Disk.dsk` (DOS 3.3, original — NUNCA alterar)
- patch/      `IC_Tester_ProDOS_v1.po` + `arquivos_v1/` (versão ProDOS: ICTESTER.SYSTEM + TEST.2/CMOS.2/HMOS.2)
- manual/     `Fairy_IC_Test_Card_Manual_v2.pdf` (manual redigitado; v2 = fotos da placa original e da alternativa no apêndice), `build_manual_v2.py`, `img/`, `capturas/` (telas do scan)
- analise/    desmontagens, BASIC, fonte do carregador, ferramentas, comparação com o Elnec

## 1. Diagnóstico do disco (v2)
DOS 3.3 sem proteção de disco. A "proteção" são nomes de arquivo com caracteres de controle,
reset desarmado e destruição da página zero do Applesoft. Os três binários ($0800) são autônomos.
A versão ProDOS (ICTESTER.SYSTEM) já existe; ver LEIA-ME_v2.md.
Patch: slot 6 liberado no menu "CARD IN WHICH SLOT" ($086D B5→B6, $086F 3F→4D).

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

## Estado
- 2026-11-19: v1 ProDOS gerada (falta testar no IIe); manual v1 em PDF; hardware e motor mapeados;
  comparação com o Elnec feita; manual v2 com as fotos das duas versões da placa.
