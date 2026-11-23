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
