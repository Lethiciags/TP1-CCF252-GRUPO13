import sys
import os

def int_para_binario(valor, bits): #Converte um inteiro (positivo ou negativo, decimal ou hexadecimal) para binário em complemento de 2.
    return format(int(str(valor), 0) & ((1 << bits) - 1), f'0{bits}b')

def parse_registo(reg_str): #Pega só o valor numérico do registrador e converte para binário de 5 bits 
    num = int(reg_str.replace('x', ''))
    return int_para_binario(num, 5)

def processa_instrucao(linha_asm, pc, tabela_simbolos): #Recebe uma linha de código, descobre o que ela faz e monta os 32 bits.
    #Remove vírgulas, parênteses e separa os argumentos
    linha_limpa = linha_asm.replace(',', ' ').replace('(', ' ').replace(')', ' ')
    partes = linha_limpa.split()
    if not partes:
        return None
    nome_instrucao = partes[0].lower()
    
    #PSEUDO-INSTRUÇÕES
    if nome_instrucao == 'nop':
        nome_instrucao = 'addi'
        partes = ['addi', 'x0', 'x0', '0']
    elif nome_instrucao == 'mv':
        nome_instrucao = 'addi'
        partes = ['addi', partes[1], partes[2], '0']
    elif nome_instrucao == 'neg':
        nome_instrucao = 'sub'
        partes = ['sub', partes[1], 'x0', partes[2]]
    elif nome_instrucao == 'beqz':
        nome_instrucao = 'beq'
        partes = ['beq', partes[1], 'x0', partes[2]]
    elif nome_instrucao == 'bnez':
        nome_instrucao = 'bne'
        partes = ['bne', partes[1], 'x0', partes[2]]
    elif nome_instrucao == 'li':
        nome_instrucao = 'addi'
        partes = ['addi', partes[1], 'x0', partes[2]]
        
    #Dicionários com o código binário de cada instrução 
    opcodes = {
        'add': '0110011', 'sub': '0110011', 'and': '0110011', 'or': '0110011', 
        'xor': '0110011', 'sll': '0110011', 'srl': '0110011', 
        'ori': '0010011', 'andi': '0010011', 'addi': '0010011', 
        'lb':  '0000011', 'lh':   '0000011', 'lw':   '0000011', 
        'sb':  '0100011', 'sh':   '0100011', 'sw':   '0100011', 
        'bne': '1100011', 'beq':  '1100011'                     
    }
    
    funct3 = {
        'add': '000', 'sub': '000', 'and': '111', 'or': '110', 
        'xor': '100', 'sll': '001', 'srl': '101',
        'ori': '110', 'andi':'111', 'addi':'000',
        'lb':  '000', 'lh':  '001', 'lw':  '010',
        'sb':  '000', 'sh':  '001', 'sw':  '010',
        'bne': '001', 'beq': '000'
    }

    funct7_map = {
        'add': '0000000', 'sub': '0100000', 'and': '0000000', 'or': '0000000', 
        'xor': '0000000', 'sll': '0000000', 'srl': '0000000'
    }

    if nome_instrucao not in opcodes: #Caso a instrução não estiver no manual, mostra um erro 
        print(f"Erro: Instrução não suportada: {nome_instrucao}")
        return None
        
    #Coleta os códigos básicos da instrução atraves dos dicíonarios 
    opcode = opcodes[nome_instrucao]
    f3 = funct3[nome_instrucao]

    #INSTRUÇÕES TIPO R
    if nome_instrucao in ['add', 'sub', 'and', 'or', 'xor', 'sll', 'srl']:
        rd = parse_registo(partes[1])
        rs1 = parse_registo(partes[2])
        rs2 = parse_registo(partes[3])
        funct7 = funct7_map[nome_instrucao]
        return f"{funct7}{rs2}{rs1}{f3}{rd}{opcode}"

    #INSTRUÇÕES TIPO I 
    elif nome_instrucao in ['ori', 'andi', 'addi', 'lb', 'lh', 'lw']:
        if nome_instrucao in ['ori', 'andi', 'addi']:
            rd = parse_registo(partes[1])
            rs1 = parse_registo(partes[2])
            imm = int_para_binario(partes[3], 12)
        else: 
            rd = parse_registo(partes[1])
            imm = int_para_binario(partes[2], 12)
            rs1 = parse_registo(partes[3])
        return f"{imm}{rs1}{f3}{rd}{opcode}"

    #INSTRUÇÕES TIPO S 
    elif nome_instrucao in ['sb', 'sh', 'sw']:
        rs2 = parse_registo(partes[1])
        imm_bin = int_para_binario(partes[2], 12)
        rs1 = parse_registo(partes[3])
        imm_11_5 = imm_bin[0:7]
        imm_4_0 = imm_bin[7:12]
        return f"{imm_11_5}{rs2}{rs1}{f3}{imm_4_0}{opcode}"

    #INSTRUÇÕES TIPO B 
    elif nome_instrucao in ['bne', 'beq']:
        rs1 = parse_registo(partes[1])
        rs2 = parse_registo(partes[2])
        
        alvo = partes[3] 
        # Verifica se o alvo está na nossa Tabela de Símbolos (Labels)
        if alvo in tabela_simbolos:
            distancia_pulo = tabela_simbolos[alvo] - pc
            imm_bin = int_para_binario(distancia_pulo, 13)
        else:
            try:
                imm_bin = int_para_binario(alvo, 13)
            except ValueError:
                print(f"Erro Crítico: A Label '{alvo}' não foi encontrada no código!")
                return None
                
        imm_12 = imm_bin[0]
        imm_11 = imm_bin[1]
        imm_10_5 = imm_bin[2:8]
        imm_4_1 = imm_bin[8:12]
        return f"{imm_12}{imm_10_5}{rs2}{rs1}{f3}{imm_4_1}{imm_11}{opcode}"

def main():
    if len(sys.argv) < 2:
        print("Uso correto:")
        print("Para terminal: python3 montador.py entrada.asm")
        print("Para ficheiro: python3 montador.py entrada.asm -o saida")
        sys.exit(1)
        
    ficheiro_entrada = sys.argv[1]  
    ficheiro_saida = None
    
    if len(sys.argv) >= 4 and sys.argv[2] == '-o':
        ficheiro_saida = sys.argv[3]
        
    if not os.path.exists(ficheiro_entrada):
        print(f"Erro: O ficheiro '{ficheiro_entrada}' não existe.")
        sys.exit(1)
    tabela_simbolos = {} 
    linhas_instrucoes = [] 
    pc_atual = 0 
    with open(ficheiro_entrada, 'r') as f: 
        for linha in f: 
            linha_codigo = linha.split('#')[0].strip()
            if not linha_codigo:
                continue
            # Verifica se tem ':', o que indica uma Label (ex: "loop: add x1, x2, x3")
            if ':' in linha_codigo:
                partes_label = linha_codigo.split(':')
                nome_label = partes_label[0].strip()
                
                # Salva o nome da label e em qual endereço de memória ela aponta
                tabela_simbolos[nome_label] = pc_atual
                
                # Pega o que sobrou da linha (a instrução em si, se houver)
                linha_codigo = partes_label[1].strip()
                
                if not linha_codigo:
                    continue # Se a linha só tinha a label, pula para a próxima instrução
            
            # Guarda a instrução limpa e o endereço em que ela vai morar
            linhas_instrucoes.append((pc_atual, linha_codigo))
            pc_atual += 4 

    binarios_gerados = []
    for pc, instrucao in linhas_instrucoes:
        codigo_maquina = processa_instrucao(instrucao, pc, tabela_simbolos)
        if codigo_maquina: 
            binarios_gerados.append(codigo_maquina)
    if ficheiro_saida:
        with open(ficheiro_saida, 'w') as f:
            for b in binarios_gerados:
                f.write(b + '\n') 
    else:
        for b in binarios_gerados:
            print(b)

if __name__ == "__main__":
    main()
