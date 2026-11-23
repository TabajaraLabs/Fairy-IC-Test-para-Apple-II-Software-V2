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
