#! /usr/bin/pythonw
# A função esponja Keccak, desenvolvida por Guida Bertoni, Joan Daemen,
# Michaël Peeters e Gilles Van Assche. Para mais informações. retornos ou
# questões. Por favor visite o website: http://keccak.noekeon.org/
# Implementação de Renaud Bauvin,
# http://creativecommons.org/publicdomain/zero/1.0/

import math


class KeccakError(Exception):
    """Classe de excecao padrao usada pela implementacao Keccak implementation

    Modo de Usar: raise KeccakError.KeccakError("Texto a ser mostrado")"""

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Keccak:
    """
    Classe implementando a função esponja Keccak
    """

    def __init__(self, b=1600):
        """Construtor:

        Parametro b, precisa ser! dentre {25, 50, 100, 200, 400, 800,  1600 (default value)}"""
        self.setB(b)

    def setB(self, b):
        """Coloca valor do parametro b (e entao em w (word block), l (length) e nr (numero de rodadas) tambem)

        Parameter b, precisa ser! dentre {25, 50, 100, 200, 400, 800, 1600}
        """

        if b not in [25, 50, 100, 200, 400, 800, 1600]:
            raise KeccakError.KeccakError('Valor errado para b - usar 25, 50, 100, 200, 400, 800 or 1600')

        # Atualiza todos os parametros em funcao do valor configurado para b
        self.b = b  # b bits para caber no arranjo de estados
        self.w = b // 25  # altura das colunas do arranjo de estados
        self.l = int(math.log(self.w, 2))
        self.nr = 12 + 2 * self.l  # numero de rodadas

    # Constants

    # Constantes de rodada ver Sec 3.2.5 Específicação
    # do algoritmo iota, pg 23 - Step Mappings (Draft Fips 202)
    RC = [0x0000000000000001,
          0x0000000000008082,
          0x800000000000808A,
          0x8000000080008000,
          0x000000000000808B,
          0x0000000080000001,
          0x8000000080008081,
          0x8000000000008009,
          0x000000000000008A,
          0x0000000000000088,
          0x0000000080008009,
          0x000000008000000A,
          0x000000008000808B,
          0x800000000000008B,
          0x8000000000008089,
          0x8000000000008003,
          0x8000000000008002,
          0x8000000000000080,
          0x000000000000800A,
          0x800000008000000A,
          0x8000000080008081,
          0x8000000000008080,
          0x0000000080000001,
          0x8000000080008008]

    # Constantes de rotacao
    # Ver sec. 3.2.2 Specification of ρ DRAFT FIPS 202
    # Tabela 2: Offsets do algoritmo 2 (Step Mappings)
    # G. Bertoni, J. Daemen, M. Peeters, and G. Van Assche,
    # “The K ECCAK reference, Version 3.0,” January 2011,
    # http://keccak.noekeon.org/Keccak-reference-3.0.pdf.

    r = [[0, 36, 3, 41, 18], [1, 44, 10, 45, 2], [62, 6, 43, 15, 61], [28, 55, 25, 21, 56],
         [27, 20, 39, 8, 14]]

    # Essa é a tabela da secao 3.2.2 - DRAFT FIPS 202
    # Porem o arranjo é diferente na implementacao em Python do Renaud Bauvin
    #         +---------------------------------------+
    #         | x = 3 | x = 4 | x = 0 | x = 1 | x = 2 |
    # +-------+---------------------------------------+
    # | y = 2 | 153   | 231   | 3     | 10    | 171   |
    # | y = 1 | 55    | 276   | 36    | 300   | 6     |
    # \ y = 0 | 28    | 91    | 0     | 1     | 190   |
    # | y = 4 | 120   | 78    | 210   | 66    | 253   \
    # | y = 3 | 21    | 136   | 105   | 45    | 15    |
    # +-------+---------------------------------------+

    # r = [[153, 231, 3, 10, 171], [55, 276, 36, 300, 6], [28, 91, 0, 1, 190], [120, 78, 210, 66, 253],
    #     [21, 136, 105, 45, 15]]


    def rot(self, x, n):
        """Rotacao bit-a-bit (para a esquerda) n bits"""

        n = n % self.w  # n tem que estar entre 0 e w (w = b // 25)
        res = ((x >> (self.w - n)) + (x << n)) % (1 << self.w)
        print('Rotacao prevista', res)
        return res  # Rotacao bit-a-bit (para a esquerda) n bits mas considerando \
        # len(string de bits) == w bits long

    def fromHexStringToLane(self, string):
        """Converte a STRING de bytes escrita em HEXADECIMAL, para uma linha (row) valor"""

        if len(string) % 2 != 0:  # Analisa se o string tem um numero par de caracteres
            raise KeccakError.KeccakError(
                "String tem que terminar com byte completo")  # Erro caso string nao termine com byte completo

        # Realiza a modificacao
        temp = ''
        nrBytes = len(string) // 2  # calcula nro de bytes usando nroCaracteres // 2 p.e: 0xABCD = 0b1010101111001101
        # cada byte tem 8 bits, entao 2 bytes para 0xABCD

        for i in range(nrBytes):  # itera por todos os bytes da string dados por nroCaracteres // 2
            offset = (nrBytes - i - 1) * 2  # esse offset pega de 2 em 2 bytes
            # print("nrBytes:", nrBytes, "Indice:", i, "Offset:", offset)
            # nrBytes: 8 Indice: 0 Offset: 14
            # nrBytes: 8 Indice: 1 Offset: 12
            # nrBytes: 8 Indice: 2 Offset: 10
            # nrBytes: 8 Indice: 3 Offset: 8
            # nrBytes: 8 Indice: 4 Offset: 6
            # nrBytes: 8 Indice: 5 Offset: 4
            # nrBytes: 8 Indice: 6 Offset: 2
            # nrBytes: 8 Indice: 7 Offset: 0
            # E se repete ciclicamente
            temp += string[offset:offset + 2]
        print('Bytes da string na linha:', temp)

        return int(temp, 16)

    def fromLaneToHexString(self, lane):
        """Converte a linha para uma string de bytes escrita em hexadecimal (base 16)"""

        laneHexBE = (("%%0%dX" % (self.w // 4)) % lane)
        # Realiza a modificação
        temp = ''
        nrBytes = len(laneHexBE) // 2
        for i in range(nrBytes):
            offset = (nrBytes - i - 1) * 2
            temp += laneHexBE[offset:offset + 2]
        return temp.upper()

    def printState(self, state, info):
        """Mostra na tela o estado da função esponja precedida da informação da strin

        state: estado da funcao esponja
        info: uma string de caracteres usadas como identificador"""

        print("Current value of state: %s" % (info))
        for y in range(5):
            line = []
            for x in range(5):
                line.append(hex(state[x][y]))
            print('\t%s' % line)

    ### Funções de Conversão da String <-> Tabela (e vice-versa)

    def convertStrToTable(self, string):
        """Converte a string de bytes para a matrix 5x5

        string: string of bytes of hex-coded bytes (e.g. '9A2C...')"""

        # Checagem dos parametros
        if self.w % 8 != 0:  # w precisa ser multiplo de 8
            raise KeccakError("w nao eh multiplo de 8")
        if len(string) != 2 * (self.b) // 8:  # tem que ser possivel dividir a string em 25 blocos
            # senao nao da para montar o cubo 5x5xw como proposto pelo keccak
            raise KeccakError.KeccakError("string nao pode ser dividida em 25 blocos de w bits cada\
            p.e. string precisa ter exatamente b bits")

        # Converte
        output = [[0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0]]

        for x in range(5):
            for y in range(5):
                offset = 2 * ((5 * y + x) * self.w) // 8
                output[x][y] = self.fromHexStringToLane(string[offset:offset + (2 * self.w // 8)])
        return output

    def convertTableToStr(self, table):
        """Converte a matrix 5x5 de representacao"""

        # Checagem do formato da entrada
        if self.w % 8 != 0:
            raise KeccakError.KeccakError("w nao eh multiplo de 8")
        if (len(table) != 5) or (False in [len(row) == 5 for row in table]):
            raise KeccakError.KeccakError("tabela precisa ser 5x5")

        # Convert
        output = [''] * 25  # sabesse de ante mao que o arranjo tera 25 strings (tabela de 5x5)
        for x in range(5):
            for y in range(5):
                output[5 * y + x] = self.fromLaneToHexString(table[x][y])
                print('Output cada 5 * ', y, ' + ', x, ': output[', 5 * y + x, '] <-',
                      self.fromLaneToHexString(table[x][y]))
        output = ''.join(output).upper()
        return output

    def Round(self, A, RCfixed, verbose=False):
        """Realiza uma rodada de computação como definido pelo Keccak-f

        A: arranjo de estado atual (matriz 5x5)
        RCfixed: valor da rodada para ser usada no passo iota
        """

        # Inicialização das variaveis temporarias
        B = [[0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0]]
        C = [0, 0, 0, 0, 0]
        D = [0, 0, 0, 0, 0]

        # modulo theta

        if verbose:
            print('Antes de theta', [bin(x) for x in C])
        for x in range(5):
            # para x = 0 ate 4 faca:
            #   C[x] = a[x, 0]
            #   para y = 1 ate 4 faca
            #     C[x] = C[x] ⊕ a[x, y]
            #   fim para
            # fim para
            C[x] = A[x][0] ^ A[x][1] ^ A[x][2] ^ A[x][3] ^ A[x][4]

        for x in range(5):
            # D[x] = C[x-1] ⊕ ROTACIONA(C[x+1], 1)
            D[x] = C[(x - 1) % 5] ^ self.rot(C[(x + 1) % 5], 1)
        if verbose:
            print('Depois da rotacao de theta', 'A[', x, ']', [bin(x) for x in A[x]])

        for x in range(5):
            for y in range(5):
                #  A[x,y] = a[x,y] ⊕ D[x]
                A[x][y] = A[x][y] ^ D[x]
        if verbose:
            print('Depois de theta', [bin(x) for x in A[x]])

        if verbose:
            print('Antes de rho e pi', [bin(x) for x in B[y]])
        # modulos rho e pi respectivamente
        for x in range(5):
            for y in range(5):
                #
                B[y][(2 * x + 3 * y) % 5] = self.rot(A[x][y], self.r[x][y])
        if verbose:
            print('Depois de rho e pi e da rotacao em A[', x, '][', y, ']', [bin(x) for x in B[y]])

        if verbose:
            print('Antes do modulo chi', [bin(x) for x in A[x]])
        # modulo chi
        for x in range(5):
            for y in range(5):
                A[x][y] = B[x][y] ^ ((~B[(x + 1) % 5][y]) & B[(x + 2) % 5][y])
        if verbose:
            print('Depois do modulo chi', [bin(x) for x in A[x]])

        if verbose:
            print('Antes do modulo iota', [bin(x) for x in A[0]])
        # modulo iota
        A[0][0] = A[0][0] ^ RCfixed  # entrada de cada uma das 24 constantes dos 24 rounds
        if verbose:
            print('Depois do modulo iota', [bin(x) for x in A[0]])

        return A

    def KeccakF(self, A, verbose=False):
        """Realiza a funcao esponja Keccak-f em A

        A: Matriz 5x5 contendo os bit estados
        verbose: mostra os estados intermediarios para analise
        """

        if verbose:
            self.printState(A, "Antes da primeira rodada")

        for i in range(self.nr):
            # NB: result is truncated to lane size
            A = self.Round(A, self.RC[i] % (1 << self.w), verbose)

            if verbose:
                self.printState(A, "Situação depois da rodada #%d/%d" % (i + 1, self.nr))

        return A

    ### Padding rule

    def pad10star1(self, M, n):
        """Preencha M com a regra de preenchimento pad10*1 para alcancar
        um tamanho multiplo de r (bitrate)

        M: message pair (comprimento em bits, string de caracteres hexadecimais('0123456789ABCD...')
        n: comprimento em bits (precisa ser multiplo de 8)
        Example: pad10star1([60, 'BA594E0FB9EBBD30'],8) returns 'BA594E0FB9EBBD93'
        """

        [my_string_length,
         my_string] = M  # p.e '00112233445566778899AABBCCDDEEFF' (8 [bits cada byte] * 16 [bytes] = 128 bits)
        # entao a entrada sera [128 [em bits], '00112233445566778899AABBCCDDEEFF']
        # outro exemplo pode ser [16, 'bbbb'] (8 * 2 [bytes] = 16 bits)

        # Checagem do parametro n
        if n % 8 != 0:  # N tem que ser multiplo de 8
            raise KeccakError.KeccakError("n precisa ser multiplo de 8")

        # Checa o tamanho a string de entrada
        if len(my_string) % 2 != 0:
            # Preenche com um '0' para alcancar o tamanho certo
            # Tamanho da string nao pode ser impar
            my_string = my_string + '0'  # aqui o tamanho da string eh par
        if my_string_length > (len(my_string) // 2 * 8):
            raise KeccakError.KeccakError("O tamanho da string nao bate com valor agregado",
                                          my_string_length, '>', (len(my_string) // 2 * 8))

        nr_bytes_filled = my_string_length // 8  # salva quantos bytes (8 bits) tem a string
        nbr_bits_filled = my_string_length % 8
        l = my_string_length % n  # quantidade de blocos totais

        if ((n - 8) <= l <= (n - 2)):
            if (nbr_bits_filled == 0):
                my_byte = 0
            else:
                my_byte = int(my_string[nr_bytes_filled * 2:nr_bytes_filled * 2 + 2], 16)
            my_byte = (my_byte >> (8 - nbr_bits_filled))
            my_byte = my_byte + 2 ** (nbr_bits_filled) + 2 ** 7
            my_byte = "%02X" % my_byte
            my_string = my_string[0:nr_bytes_filled * 2] + my_byte
        else:
            if (nbr_bits_filled == 0):
                my_byte = 0
            else:
                my_byte = int(my_string[nr_bytes_filled * 2:nr_bytes_filled * 2 + 2], 16)
            my_byte = (my_byte >> (8 - nbr_bits_filled))
            my_byte = my_byte + 2 ** (nbr_bits_filled)
            my_byte = "%02X" % my_byte
            my_string = my_string[0:nr_bytes_filled * 2] + my_byte
            while ((8 * len(my_string) // 2) % n < (n - 8)):
                my_string = my_string + '00'
            my_string = my_string + '80'

        return my_string

    def Keccak(self, M, r=1024, c=576, n=1024, verbose=False):
        """Compute the Keccak[r,c,d] sponge function on message M

        M: mensagem (message pair) (comprimento em bits,
           string de caracteres hexadecimais ('0123456789ABCD...')
        r: taxa (bitrate) em bits (defautl: 1024)
        c: capacidade (capacity) em bits (default: 576)
        n: comprimento da saida (output length) em bits (default: 1024),
        verbose: print detalhes da computacao (default:False)
        """

        # Checagem das entradas
        if (r < 0) or (r % 8 != 0):
            raise KeccakError.KeccakError('r precisa ser multiplo de 8 nessa implementacao')
        if (n % 8 != 0):
            raise KeccakError.KeccakError('output length (vazao) precisa ser multiplo de 8')
        self.setB(r + c)
        print('R + C:', r + c, 'bits')
        print('Output Length (Vazao):', n)  # para o shake128 e shake256 temos que n = 0

        if verbose:
            print("Criar funcao esponja Keccak com parametros r = %d c = %d w = %d" % (r, c, (r + c) // 25))

        # Computa o tamanho da linha (em bits)
        w = (r + c) // 25

        # Inicialização do 'state array'
        S = [[0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0]]

        # Preenchendo mensagens
        P = self.pad10star1(M, r)  # retorna mensagem com padding por blocos de r

        if verbose:
            print('Mensagem com pad10*1:',
                  "String pronta para ser absorvida: %s (vai ser completada por %d x '00')" % (P, c // 8))

        # Fase de inchando a esponja
        # Fase do hashing em sí, essa fase é importante
        for i in range((len(P) * 8 // 2) // r):  # precorre de bloco em bloco a string P (com pdf10*1)
            Pi = self.convertStrToTable(P[i * (2 * r // 8):(i + 1) * (2 * r // 8)] + '00' * (
                c // 8))  # coloca pares de zeros suficientes para encaixar cada
            print(Pi)

            for y in range(5):
                for x in range(5):
                    S[x][y] = S[x][y] ^ Pi[x][y]  # xors dos bits nos cortes em planos (Panes(x,y)
                    print('Inchando Esponja:', bin(S[x][y]), bin(S[x][y]), 'xor', bin(Pi[x][y]))
            S = self.KeccakF(S, verbose)
            print('State:', i, S)

        if verbose:
            print("Valor depois de absorver: %s" % (self.convertTableToStr(S)))

        # Fase de espremendo da esponja
        Z = ''
        outputLength = n
        while outputLength > 0:  # faz o controle para ver se os n bits do bloco foram processado
            string = self.convertTableToStr(S)
            Z = Z + string[:r * 2 // 8]
            outputLength -= r
            if outputLength > 0:
                S = self.KeccakF(S, verbose)

                # NB: termina a cada bloco de tamanho r
                # podera ser cortado se o comprimento
                # de saida nao eh multiplo de
                # [:2 * n // 8] corta os blocos

        if verbose:
            print("Valor depois de espremer a esponja: %s" % (self.convertTableToStr(S)))

        return Z[:2 * n // 8]
