# Fairy IC-Test para Apple II — Software V2

**VERSION 2.0 EXPANDED BY TABAJARA LABS** — software novo para a placa **Fairy / Yih-Lung "Universal I.C. Tester" (IC TEST CARD, 1984)** para Apple II, II Plus e IIe.

O programa original (disquete DOS 3.3, protegido contra cópia) foi preservado intacto em `original/`. A versão 2.0 roda pelo **ProDOS** (disco rígido, CompactFlash/CFFA, BOOTI…) num Apple II de 64K, mantém o programa original e o copyright do fabricante em todas as telas e acrescenta:

- **Todas as travas neutralizadas**: o checksum da tela de texto e a comparação do copyright, que faziam o programa falhar fora do disquete original.
- **CIs novos dentro das opções originais**, com padrões de teste convertidos das bibliotecas do programador Elnec:
  | Opção | Original | Acrescentados | Total |
  |---|---|---|---|
  | A — TTL 54/74 | 158 | 37 | **195** |
  | B — CMOS 40/45 | 68 | 26 | **94** |
  | C — HCMOS 74HC | 49 | 110 | **159** |
- **Busca Ctrl-S rápida**: ~4 s por CI (antes ~27 s), também nos CIs novos. Famílias que o original recusa (74F, 74ALS…) passam a ser testadas pelo número.
- **Opção D — MEMORY (RAM)**: a opção "Memory" anunciada no manual de 1984, que nunca foi entregue. Testa 2114, 2147, 4164, 41256, 4416, 4464, e 6116/6264 com um adaptador (74HC574). Mostra na tela onde colocar a memória no soquete.
- **ICTDIAG**: diagnóstico da placa (soquete, comparadores, chaves de alimentação) — fora do disco de boot, em `nova_versao/arquivo/arquivos_v12/`.
- **Disco bootável**: ProDOS 2.4.3 + Bitsy Bye num disquete de 140 KB.
- **Manual restaurado** em A5, no visual da impressão original, com a nova seção (V) da versão 2.0.

## Como usar

1. Grave a imagem `nova_versao/IC_Tester_ProDOS_v13.po` (atual) num disquete de 5,25" ou use-a num emulador de drive (Floppy Emu, CFFA, BOOTI…).
   **A imagem é bootável** (ProDOS 2.4.3): ao dar boot, o testador entra direto no menu. Q sai para o Bitsy Bye.
2. Também dá para copiar os arquivos para outro volume ProDOS e executar `ICTESTER.SYSTEM`.
3. Escolha A, B, C ou D e informe o slot da placa.

O resto da operação é igual ao manual original. Veja `manual/Fairy_IC_Test_Card_Manual_v3.pdf`.

## Organização

| Pasta | Conteúdo |
|---|---|
| `original/` | disquete original (DOS 3.3), nunca alterado |
| `nova_versao/` | versão atual: imagem ProDOS bootável `IC_Tester_ProDOS_v13.po` e os arquivos soltos dela (`arquivos_v13/`) |
| `nova_versao/arquivo/` | versões anteriores (v1 a v12), guardadas como histórico; o diagnóstico `ICTDIAG.SYSTEM` e o motor avulso `ELNEC.ENG` estão em `arquivo/arquivos_v12/` |
| `analise/fonte/` | fontes 6502 (ca65): carregador, gancho Elnec, motor, teste de RAM, diagnóstico |
| `analise/ferramentas/` | ferramentas Python: leitores DOS 3.3/ProDOS, gerador de imagem .po, conversor Elnec, simuladores da placa (py65) |
| `analise/` | desmontagens anotadas, notas de hardware, travas, comparação com o Elnec, resultados de bancada |
| `manual/` | manuais em PDF e os geradores |
| `LEIA-ME_v22.md` e `.pdf` | diário técnico do projeto (versão atual) |

Em cada diretório fica **só a versão mais nova** de cada arquivo. As versões anteriores ficam
em um subdiretório `arquivo/` dentro do próprio diretório (por exemplo `analise/fonte/arquivo/`,
`manual/arquivo/` e `arquivo/` na raiz, com os LEIA-ME v1 a v21). Os LEIA-ME antigos citam a pasta
de imagens pelo nome antigo, `patch/`, hoje `nova_versao/`.

O manual é gerado por `manual/build_manual_v4.py`, que usa o texto e os desenhos de
`manual/arquivo/build_manual_v2.py`.

## Estado

As versões até a v10 foram testadas num Apple IIe real. As v11 a v13 (teste de RAM, contagens corrigidas e disco bootável) foram validadas no simulador e falta testá-las no hardware.

## Créditos

- Placa e software originais: **Yih-Lung Enterprises Co., Ltd.** (Fairy), 1984. O copyright do fabricante aparece em todas as telas.
- Padrões de teste acrescentados: convertidos das bibliotecas de dispositivos do software do programador **Elnec**.
- Fotos da placa no manual: **AppleBox / J.E.H. Walsh** (applefritter.com).
- Versão 2.0: **Tabajara Labs** — [tabalabs.com.br](https://tabalabs.com.br), 2026.
