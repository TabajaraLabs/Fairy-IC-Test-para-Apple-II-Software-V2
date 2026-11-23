
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

## 8. ICTDIAG.SYSTEM (diagnóstico, v1) — na imagem IC_Tester_ProDOS_v3.po
Rodar com o **soquete vazio**. Mede sozinho (sem pontas de prova):
- T1: para cada bit de porta, qual linha do mux responde e o valor do comparador com 1 e com 0
  (→ significado dos bits do comparador).
- T2: comparador e portas com os pinos soltos nas 4 combinações de PC7/PC6 (→ pull-up/down).
- T3: posição de VCC/GND para os 7 códigos PD usados pelo software original (só esses).
Resultado esperado no simulador (modelo ideal): PA0→E0 … PB7→F7, PC0→C3, PC1→C4, PC2→C5.
