# Respostas das Questões
## Q1

Para verificar é preciso abrir o CRT através do uso openssl x509 -text -noout -in MSG_SERVER.crt e depois fazer o mesmo para a key através do comando $ openssl rsa -text -noout -in MSG_SERVER.key e verificar se nos varios modulus da key aparece o modulus do crt.
Se o valor do módulo na chave privada corresponder ao valor do módulo no certificado, isso indica que as chaves constituem um par de chaves RSA válido.

## Q2

Pelo que podemos verificar as partes que são importantes a se ter em conta nos certificados são:

 -> Issue;
 
 -> Validity;
 
 -> Subject, mas precisamente o CN e o pseudonym;
 
 -> Modulus para fazer a ligação do CRT à KEY correspondente;
 
 -> Extensions, que nos certificados dados para esta tabela são "ignorados";
 
 -> Signature Value, para verificar a autenticidade.
 

# Relatório do Guião da Semana 7
