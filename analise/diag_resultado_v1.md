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
