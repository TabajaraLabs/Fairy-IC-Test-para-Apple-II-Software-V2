# IC TESTER (Yu Fung) — software ProDOS com proteção de disco

Objetivo: fazer o software da placa IC TESTER (Yu Fung, Apple II) rodar a partir de
armazenamento de massa (BOOTI / imagem .po), sem depender do disquete original.

## Estrutura
- original/  imagens do disquete original (.woz / .nib / .po / .dsk) — NUNCA alterar
- analise/   desmontagens, notas, dumps de memória
- patch/     imagens .po corrigidas (versionadas: _v1, _v2...)

## Plano
1. Obter imagem do disco original (ideal: .woz via Applesauce/Greaseweazle; mínimo: .po/.dsk)
2. Extrair os arquivos ProDOS (SYSTEM, BIN) e desmontar
3. Achar a verificação da proteção (acessos diretos a $C08x,X do Disk II, leitura de
   nibbles/trilha especial, checksum de assinatura)
4. Neutralizar a verificação e (se houver) devolver o valor esperado
5. Testar no emulador e depois no IIe via BOOTI

## Estado
- 2026-11-19: pasta criada; aguardando imagem do disco original.
