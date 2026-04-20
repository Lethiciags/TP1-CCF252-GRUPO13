# TP1-CCF252-GRUPO13

Este repositório contém a implementação de um montador simplificado para a arquitetura RISC-V, desenvolvido como requisito para a disciplina de Organização de Computadores I (CCF 252) da Universidade Federal de Viçosa (UFV) - Campus Florestal.

O montador foi desenvolvido inteiramente em Python 3 e é responsável por ler um código-fonte em linguagem assembly (extensão `.asm`) e convertê-lo para código de máquina em binário (32 bits).

O Arquivo de Teste (`entrada.asm`)
O arquivo de entrada presente neste repositório não contém apenas os dois casos básicos da especificação. Ele foi construído para testar todas as capacidades avançadas do montador, incluindo:
1. Tradução de pseudo-instruções e suporte a hexadecimal.
2. Laços de repetição complexos (pulos para a frente e para trás na memória).
3. Testes em todos os formatos suportados (Tipo R, I, S e B).
