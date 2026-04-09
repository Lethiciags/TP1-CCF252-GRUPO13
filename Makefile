#Makefile para o Montador RISC-V em Python

all: #Avisa o usuário dos comandos disponíveis 
	@echo "O montador foi feito em Python e nao precisa ser compilado."
	@echo "Comandos disponiveis:"
	@echo "  make run-terminal : Roda o programa e imprime no terminal"
	@echo "  make run-arquivo  : Roda o programa e salva em saida.txt"
	@echo "  make clean        : Apaga os arquivos de saida gerados"

#Imprime no terminal
run-terminal:
	python3 montador.py entrada.asm
#Salva no arquivo
run-arquivo:
	python3 montador.py entrada.asm -o saida.txt
#Remove o arquivo saida.txt e pastas de cache do Python (se houver)
clean:
	rm -f saida.txt
	rm -rf __pycache__
