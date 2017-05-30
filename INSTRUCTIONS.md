Função de Hash Criptográfica SHA-3
==================================

Compreensão da Lista de Tarefas

Produzir um documento com o seguinte conteúdo:

1.  Definição de função de hash criptográfica

2.  Propriedades

    a.  Pré-imagem

    b.  Segunda pré-imagem

    c.  Colisão

3.  Explicar o SHA-3

4.  Responder às seguintes questões relacionadas a referência oficial sobre o SHA-3 (NIST) que
    apresenta o SHA-3 padronizado pelo NIST

    a.  O que é e para que serve o State Array ( figura 1 )?

    b.  Como é feita a conversão de strings para State Arrays? Mostrar
        também um exemplo de vocês, diferente do NIST;

    c.  Como é feita a conversão de State Array para Strings? Incluir um
        exemplo de vocês;

    d.  Explicar os cinco passos de mapeamento ( Step Mappings ).
        Explicar os algoritmos envolvidos e cada uma das figuras
        apresentadas ( figuras 3 à 6 )

    e.  Explicar a permutação Keccak-p\[b,nr\]

        i.  Compare esta função com a Keccak-f

    f.  Descrever o framework Sponge Construction

        i.  Explique a figura 7 e o Algoritmo 8

    g.  Explique a família de funções esponja Keccak, conforme seção 5

    h.  Explique as especificação da função SHA-3, conforme Seção 6

        i.  Funções de Hash SHA-3

        ii. Funções de Saída Estendida

    i.  Apresente a análise de segurança conforme Apêndice A.1

    j.  Gere os seus próprios exemplos ( diferente do NIST ) conforme
        Apêndice A.2

5.  Apresentar uma implementação do SHA-3 ( pode ser em qualquer
    linguagem )

    a.  Descreva a implementação

    b.  Mostre na implementação onde se da cada passo importante do
        cálculo do Hash

    c.  Execute a implementação passo a passo, mostrando o maior número
        possível de saídas.

6.  Compare o SHA-2, em termos de performance, com os hashes da
    família SHA-2. Use um mesmo computador e implementações padrão
    para esta comparação. O resultado da comparação deve ser em termos
    de tamanhos de arquivos dos quais hashes são calculados e quanto
    tempo para hash ( uma média ) demora para ser calculado.

7.  Apresentar uma crítica ao SHA-3

    a.  O que ele é melhor ou diferente em relação a outros hashes?

    b.  Quanto tempo você acha ( e por que ) o SHA-3 será considerado
        seguro?
