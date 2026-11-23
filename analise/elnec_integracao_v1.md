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
