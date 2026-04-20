# 1. PSEUDO-INSTRUÇÕES E SUPORTE A HEXADECIMAL
nop                     
li x1, 0x1A             
li x2, 0x05             
mv x3, x1               
neg x4, x2              

# 2. TESTE DE LABELS
beqz x4, pula_frente    

# 3. INSTRUÇÕES TIPO R 
add x5, x1, x2          
sub x6, x1, x2          
and x7, x1, x2         
or x8, x1, x2           
xor x9, x1, x2         
sll x10, x1, x2         
srl x11, x1, x2         

pula_frente:            
# 4. INSTRUÇÕES TIPO I 
addi x12, x0, 100       
andi x13, x12, 0xFF   
ori x14, x13, 0x0F    

# 5. INSTRUÇÕES TIPO S 
sb x5, 0(x1)            
sh x6, 4(x1)           
sw x7, 8(x1)            

# 6. INSTRUÇÕES TIPO I 
lb x15, 0(x1)           
lh x16, 4(x1)          
lw x17, 8(x1)           

# 7. TESTE DE LAÇOS
laco_repeticao:         
addi x12, x12, -1       
bnez x12, laco_repeticao 
bne x12, x0, laco_repeticao 
beq x12, x0, fim        

fim:
nop                     
