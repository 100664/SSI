# Respostas das Questões
## Q1

Usamos os seguinte comandos:
- `chmod`: para alterar permissões;
- `chown`: para alterar o proprietário;
- `chgrp`: para alterar o grupo do proprietário
- `umask`: para definir as permissões padrão para novos ficheiros e diretórios criados.

## Q2

Os membros desse grupo têm todos Mac como tal vamos ter que apresentar a lista de passos que se tem que seguir no MacOs:

Criamos os 3 utilizadores referentes aos membros do grupo:
- sudo dscl . -create /Users/MartimR
- sudo dscl . -create /Users/JessicaC
- sudo dscl . -create /Users/TiagoM

Criamos o grupo para todos os elementos:
- sudo dscl . -create /Groups/grupo50

Acrescentamos ao grupo:
- sudo dscl . -append /Groups/grupo50 GroupMembership MartimR
- sudo dscl . -append /Groups/grupo50 GroupMembership JessicaC
- sudo dscl . -append /Groups/grupo50 GroupMembership TiagoM

Criamos o grupo para só 2 elementos da equipa:
- sudo dscl . -create /Groups/selectGroup

Acrescentamos ao grupo:
- sudo dscl . -append /Groups/selectGroup GroupMembership JessicaC
- sudo dscl . -append /Groups/selectGroup GroupMembership TiagoM

 
Verificar os membros se estão todos corretos:
- sudo dscl . -read /Groups/grupo50
- sudo dscl . -read /Groups/selectGroup

## Q3
Para esta questão criamos o programa `impress_cont.py`, que imprime o conteúdo de um ficheiro de texto cujo nome é passado como único argumento da sua linha de comando.

## Q4
 

# Relatório do Guião da Semana 8
