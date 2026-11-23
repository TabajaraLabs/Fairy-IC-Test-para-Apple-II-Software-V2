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
