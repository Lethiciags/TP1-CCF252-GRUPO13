import sys
import os

def int_para_binario(valor, bits): #Converte um inteiro (positivo ou negativo, decimal ou hexadecimal) para binário em complemento de 2.
    return format(int(str(valor), 0) & ((1 << bits) - 1), f'0{bits}b')

def parse_registo(reg_str): #Pega só o valor numérico do registrador e converte para binário de 5 bits 
    num = int(reg_str.replace('x', ''))
    return int_para_binario(num, 5)

def processa_instrucao(linha_asm): #Recebe uma linha de código, descobre o que ela faz e monta os 32 bits.
    #Remove vírgulas, parênteses e separa os argumentos
    linha_limpa = linha_asm.replace(',', ' ').replace('(', ' ').replace(')', ' ')
    partes = linha_limpa.split()
    if not partes:
        return None
    nome_instrucao = partes[0].lower()
    nome_instrucao = partes[0].lower()
    #PSEUDO-INSTRUÇÕES
    if nome_instrucao == 'nop':
        # nop -> addi x0, x0, 0
        nome_instrucao = 'addi'
        partes = ['addi', 'x0', 'x0', '0']
    elif nome_instrucao == 'mv':
        # mv rd, rs -> addi rd, rs, 0
        nome_instrucao = 'addi'
        partes = ['addi', partes[1], partes[2], '0']
    elif nome_instrucao == 'neg':
        # neg rd, rs -> sub rd, x0, rs
        nome_instrucao = 'sub'
        partes = ['sub', partes[1], 'x0', partes[2]]
    elif nome_instrucao == 'beqz':
        # beqz rs, imm -> beq rs, x0, imm
        nome_instrucao = 'beq'
        partes = ['beq', partes[1], 'x0', partes[2]]
    elif nome_instrucao == 'bnez':
        # bnez rs, imm -> bne rs, x0, imm
        nome_instrucao = 'bne'
        partes = ['bne', partes[1], 'x0', partes[2]]
    elif nome_instrucao == 'li':
        # li rd, imm -> addi rd, x0, imm
        nome_instrucao = 'addi'
        partes = ['addi', partes[1], 'x0', partes[2]]
    #Dicionários com o código binário de cada instrução 
    opcodes = {
        # Tipo R
        'add': '0110011', 'sub': '0110011', 'and': '0110011', 'or': '0110011', 
        'xor': '0110011', 'sll': '0110011', 'srl': '0110011', 
        # Tipo I (Aritméticas)
        'ori': '0010011', 'andi': '0010011', 'addi': '0010011', 
        # Tipo I (Loads)
        'lb':  '0000011', 'lh':   '0000011', 'lw':   '0000011', 
        # Tipo S
        'sb':  '0100011', 'sh':   '0100011', 'sw':   '0100011', 
        # Tipo B
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

    if nome_instrucao not in opcodes: #Caso a instrução não estiver no manual, mostramos um erro 
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
        imm_bin = int_para_binario(partes[3], 13)
        imm_12 = imm_bin[0]
        imm_11 = imm_bin[1]
        imm_10_5 = imm_bin[2:8]
        imm_4_1 = imm_bin[8:12]
        return f"{imm_12}{imm_10_5}{rs2}{rs1}{f3}{imm_4_1}{imm_11}{opcode}"

def main():
    if len(sys.argv) < 2: #Verifica se o usuário digitou os comandos de forma correta no terminal.
        print("Uso correto:")
        print("Para terminal: python3 montador.py entrada.asm")
        print("Para ficheiro: python3 montador.py entrada.asm -o saida")
        sys.exit(1)
    #Guarda o nome do arquivo que o usuário quer ler    
    ficheiro_entrada = sys.argv[1]  
    ficheiro_saida = None
    if len(sys.argv) >= 4 and sys.argv[2] == '-o': #Se o usuário digitou mais coisas e incluiu o '-o', guardamos o nome do arquivo de saída.
        ficheiro_saida = sys.argv[3]
    if not os.path.exists(ficheiro_entrada): # Verifica se o arquivo de entrada realmente existe no computador.
        print(f"Erro: O ficheiro '{ficheiro_entrada}' não existe.")
        sys.exit(1)
    binarios_gerados = [] #Cria uma lista vazia para guardar os binários que vamos gerar.
    with open(ficheiro_entrada, 'r') as f: #Abre o arquivo de entrada em modo leitura
        for linha in f: 
            linha_codigo = linha.split('#')[0].strip() #Ignora quebras de linha e comentários iniciados com #
            if not linha_codigo:
                continue
            codigo_maquina = processa_instrucao(linha_codigo) #Manda a linha para ser processada 
            if codigo_maquina: #Caso o binaŕio tenha sido retornado com sucesso, guarda na lista 
                binarios_gerados.append(codigo_maquina)
    if ficheiro_saida:  #Se o usuário pediu um arquivo de saída, abre esse novo arquivo em modo de escrita
        with open(ficheiro_saida, 'w') as f:
            for b in binarios_gerados:
                f.write(b + '\n') #Escreve o binário e adiciona um \n para quebrar a linha.
    else: # Senão, apenas "printa" cada binário na tela do terminal.
        for b in binarios_gerados:
            print(b)

if __name__ == "__main__":
    main()
