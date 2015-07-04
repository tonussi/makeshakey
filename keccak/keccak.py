#! /usr/bin/pythonw

import math
import time


def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        print('%r - %2.5f sec' % (method.__name__, te - ts))
        return result

    return timed

# Utility lambda for printing strings
hexformatter = lambda m: ' '.join(m[i:i + 16] for i in range(0, len(m), 16))


class Keccak:  # Classe que implementa a função esponja

    def __init__(self, b=1600):
        """Constructor:

        b: parameter b, must be 25, 50, 100, 200, 400, 800 or 1600 (default value)"""

        # set keccak innner encoding
        self.encoding = 16

        self.setB(b)

    def setB(self, b):
        assert b in [25, 50, 100, 200, 400, 800, 1600], 'Valores válidos para b: 25, 50, 100, 200, 400, 800 or 1600'

        # Update all the parameters based on the used value of b
        # Parâmetros
        self.b = b  # b : largura da permutação (tamanho do estado)
        self.w = b // 25  # w : raia
        self.nr = 12 + 2 * int(math.log(self.w, 2))  # nr: quantidade de rodadas

    # Constants

    # Constantes de rodada ver Sec 3.2.5 Específicação
    # do algoritmo iota, pg 23 - Step Mappings (Draft Fips 202)
    RC = [0x0000000000000001, 0x0000000000008082, 0x800000000000808A, 0x8000000080008000,
          0x000000000000808B, 0x0000000080000001, 0x8000000080008081, 0x8000000000008009,
          0x000000000000008A, 0x0000000000000088, 0x0000000080008009, 0x000000008000000A,
          0x000000008000808B, 0x800000000000008B, 0x8000000000008089, 0x8000000000008003,
          0x8000000000008002, 0x8000000000000080, 0x000000000000800A, 0x800000008000000A,
          0x8000000080008081, 0x8000000000008080, 0x0000000080000001, 0x8000000080008008]

    # Constantes de rotacao
    # Ver sec. 3.2.2 Specification of ρ DRAFT FIPS 202
    # Tabela 2: Offsets do algoritmo 2 (Step Mappings)
    # G. Bertoni, J. Daemen, M. Peeters, and G. Van Assche,
    # “The K ECCAK reference, Version 3.0,” January 2011,
    # http://keccak.noekeon.org/Keccak-reference-3.0.pdf.

    r = [[0, 36, 3, 41, 18],
         [1, 44, 10, 45, 2],
         [62, 6, 43, 15, 61],
         [28, 55, 25, 21, 56],
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

    # indices_rotacao = [[153, 231, 3, 10, 171],
    #                    [55, 276, 36, 300, 6],
    #                    [28, 91, 0, 1, 190],
    #                    [120, 78, 210, 66, 253],
    #                    [21, 136, 105, 45, 15]]


    def rot(self, x, n, verbose=False):
        """Rotacao bit-a-bit (para a esquerda) n bits"""

        n = n % self.w  # n tem que estar entre 0 e w (w = b // 25)
        res = ((x >> (self.w - n)) + (x << n)) % (1 << self.w)
        if verbose:
            print('Rotacionar Esquerda(' + str(x) + ',' + str(n) + '[bits]) = ' + str(res))
        return res
        # Rotacao bit-a-bit (para a esquerda) n bits mas considerando \
        # len(string de bits) == w bits long

    def fromHexStringToLane(self, hexstring, verbose=True):  # Troca a ordem dos bytes para Little Endian
        assert len(hexstring) % 2 == 0, "A mensagem não termina com um byte completo"
        # Converte uma hexstring para um valor inteiro

        if verbose:
            print("String antes da conversão da linha: %s (base 16)" % hexformatter(hexstring))

        byte_array = [hexstring[i:i + 2] for i in range(0, len(hexstring), 2)]

        if verbose:
            print("String depois divisão em bytes: %s (base 16)" % ' '.join(byte_array))

        byte_array.reverse()
        little_endian_string = ''.join(byte_array)

        if verbose:
            print("String depois a troca para little_endian: %s (base 16)" % little_endian_string)

        return int(little_endian_string, self.encoding)

    def fromLaneToHexString(self, lane, verbose=False):
        """Convert a lane value to a string of bytes written in hexadecimal"""

        if verbose:
            print("Linha antes da conversão para hexadecimal: %d (base 10)" % lane)

        laneHexBE = (("%%0%dX" % (self.w // 4)) % lane)

        byte_array = [laneHexBE[i:i + 2] for i in range(0, len(laneHexBE), 2)]

        if verbose:
            print("Linha depois da conversão para hexstring (little endian): %s (base 16)" % ' '.join(byte_array))

        byte_array.reverse()

        if verbose:
            print("Linha depois da conversão para hexstring (big endian): %s (base 16)" % ' '.join(byte_array))

        big_endian_string = ''.join(byte_array)

        return big_endian_string

    def printState(self, state, info):
        """Print on screen the state of the sponge function preceded by string info"""
        print("Valor atual do State Array %s" % (info))
        for y in range(5):
            line = []
            for x in range(5):
                line.append('%016X' % (state[x][y]))
            print('\t%s' % line)

    def convertStringToStateArray(self, string):  # Constrói o State Array (5x5) a partir de uma string
        assert self.w % 8 == 0, "w não é múltiplo de 8"  # cada ítem (lane) tem w bits
        assert len(string) == 2 * (self.b) // 8, "string deve ter exatament %s bits (tem %s)" % (self.b, len(string))

        output = [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]
        for x in range(5):
            for y in range(5):
                start = 2 * ((5 * y + x) * self.w) // 8
                end = start + (2 * self.w // 8)
                output[x][y] = self.fromHexStringToLane(string[start:end], verbose=False)
        return output

    def convertStateArrayToString(self, table):  # Converte o state array para uma string hexadecimal
        assert self.w % 8 == 0, "w não é múltiplo de 8"
        assert (len(table) == 5) and (all(len(row) == 5 for row in table)), "tabela deve ser 5x5"

        output = [''] * 25
        for x in range(5):
            for y in range(5):
                output[5 * y + x] = self.fromLaneToHexString(table[x][y], verbose=False)
        output = ''.join(output).upper()
        return output

    def round(self, A, RCfixed, verbose=False):
        """Perform one round of computation as defined in the Keccak-f permutation"""

        # Initialisation of temporary variables
        B = [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]
        C = [0, 0, 0, 0, 0]
        D = [0, 0, 0, 0, 0]

        # modulo theta

        if verbose:
            print('Antes de theta', [hex(x) for x in C])
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
            print('Depois da rotacao de theta', 'A[', x, ']', [hex(x) for x in A[x]])

        for x in range(5):
            for y in range(5):
                #  A[x,y] = a[x,y] ⊕ D[x]
                A[x][y] = A[x][y] ^ D[x]
        if verbose:
            print('Depois de theta', [hex(x) for x in A[x]])

        if verbose:
            print('Antes de rho e pi', [hex(x) for x in B[y]])
        # modulos rho e pi respectivamente
        for x in range(5):
            for y in range(5):
                B[y][(2 * x + 3 * y) % 5] = self.rot(A[x][y], self.r[x][y], verbose)
        if verbose:
            print('Depois de rho e pi e da rotacao em A[', x, '][', y, ']', [hex(x) for x in B[y]])

        if verbose:
            print('Antes do modulo chi', [hex(x) for x in A[x]])
        # modulo chi
        for x in range(5):
            for y in range(5):
                A[x][y] = B[x][y] ^ ((~B[(x + 1) % 5][y]) & B[(x + 2) % 5][y])
        if verbose:
            print('Depois do modulo chi', [hex(x) for x in A[x]])

        if verbose:
            print('Antes do modulo iota', [hex(x) for x in A[0]])
        # modulo iota
        A[0][0] = A[0][0] ^ RCfixed  # entrada de cada uma das 24 constantes dos 24 rounds
        if verbose:
            print('Depois do modulo iota', [hex(x) for x in A[0]])

        return A

    def KeccakF(self, A, verbose=False):
        """Perform Keccak-f function on the state A"""

        if verbose:
            self.printState(A, " antes da primeira rodada")

        for i in range(self.nr):
            round_constant = self.RC[i] % (1 << self.w)  # RC é truncada de acordo com o tamanho das lanes (w)
            A = self.round(A, round_constant, verbose)

            if verbose: self.printState(A, " após a rodada %d/%d" % (i + 1, self.nr))

        return A

    ### Padding rule

    def pad10star1(self, M, n):
        """Preencha M com a regra de preenchimento pad10*1 para alcancar
        um tamanho multiplo de r (bitrate)

        M: message pair (comprimento em bits, string de caracteres hexadecimais('0123456789ABCD...')
        n: comprimento em bits (precisa ser multiplo de 8)
        Example: pad10star1([60, 'BA594E0FB9EBBD30'],8) returns 'BA594E0FB9EBBD93'
        """

        [tam, text] = M

        assert n % 8 == 0, 'n deve ser múltiplo de 8'

        text += '0' * (len(text) % 2)  # Acrescenta '0' se a string não tiver tamanho par

        assert tam <= (len(text) // 2 * 8), "the string is too short to contain the number of bits announced"

        bytes_filled = tam // 8
        bits_filled = tam % 8
        l = tam % n
        if ((n - 8) <= l <= (n - 2)):
            if (bits_filled == 0):
                pad_byte = 0
            else:
                pad_byte = int(text[bytes_filled * 2:bytes_filled * 2 + 2], self.encoding)
            pad_byte = (pad_byte >> (8 - bits_filled))
            pad_byte = pad_byte + 2 ** (bits_filled) + 2 ** 7
            pad_byte = "%02X" % pad_byte
            text = text[0:bytes_filled * 2] + pad_byte
        else:
            if (bits_filled == 0):
                pad_byte = 0
            else:
                pad_byte = int(text[bytes_filled * 2:bytes_filled * 2 + 2], self.encoding)
            pad_byte = (pad_byte >> (8 - bits_filled))
            pad_byte = pad_byte + 2 ** (bits_filled)
            pad_byte = "%02X" % pad_byte
            text = text[0:bytes_filled * 2] + pad_byte
            while ((8 * len(text) // 2) % n < (n - 8)):
                text = text + '00'
            text = text + '80'

        return text

    def Keccak(self, M, r=1024, c=576, n=1024, verbose=False):
        """Compute the Keccak[r,c,d] sponge function on message M"""

        assert r and (r % 8 == 0), 'r deve ser múltiplo de 8'
        assert n % 8 == 0, 'o tamanho de saída deve ser múltiplo de 8'

        self.setB(r + c)

        if verbose:
            print("Gerando a função Keccak com (r=%d, c=%d (i.e. w=%d))" % (r, c, (r + c) // 25))

        # Inicialização do State Array
        S = [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]

        # Adiciona padding
        P = self.pad10star1(M, r)

        if verbose:
            print("String pronta para ser absorvida: %s (será completada com %d x '00')" % (
                hexformatter(P).lower(), c // 8))

        # Absorbing phase
        block_size = 2 * r // 8
        block_count = (len(P) * 8 // 2) // r
        for i in range(block_count):
            block = P[block_size * i:block_size * (i + 1)]
            pad = '00' * (c // 8)
            string = block + pad
            Pi = self.convertStringToStateArray(string)

            for y in range(5):  # Incorpora o novo bloco ao state array, aplicando XOR nas lanes correspondentes
                for x in range(5):
                    S[x][y] = S[x][y] ^ Pi[x][y]

            S = self.KeccakF(S, verbose)  # Aplica a função Keccak-F

        if verbose:
            print("Valor após ter absorvido: %s" % (hexformatter(self.convertStateArrayToString(S)).lower()))

        # Squeezing phase
        Z = ''
        bits_left = n
        while bits_left > 0:
            string = self.convertStateArrayToString(S)
            Z += string[:block_size]
            bits_left -= r
            if bits_left > 0:
                S = self.KeccakF(S, verbose)

        if verbose:
            print("Valor após ter espremido: %s" % (hexformatter(self.convertStateArrayToString(S)).lower()))

        return Z[:2 * n // 8]

    """
    Para variantes propostas pelo campeonato do SHA-3, o valor do parâmetros c
    é igual ao comprimento do resumo multiplicado por 2. Por exemplo, o candidato
    SHA-3 com 512-bit de comprimento é o Keccak com c = 1024 e r = 576 (r + c = 1600).
    Variantes são então, Keccak-224, Keccak-256, e Keccak-512 (O número no final é o
    comprimento do resumo criptográfico gerado por essas funções.

    O número r de mensagem em bits processadas por bloco de permutação depende da vazão
    do comprimento do resumo criptográfico. A rate r pode ser 1152, 1088, 832, ou 576
    que bate respectivamente com os tamanhos de resumo cript. 224, 256, 384, e 512-bit.

    Todos com palavras de 64-bit.

    Para assegurar que a mensagem pode ser dividida corretamente em blocos de tamanho
    igual a r-bits, e será enxertado (padded) com valor 1 binário, zero ou mais bits
    0 (zero) binário e ao final novamente com o valor 1 binário (por isso que o nome
    da função se chama pad10star1.

    Finalmente o estado (state) pode ser visualizado como um arranjo de 5x5 linhas (lanes)
    onde cada linha é uma palavra de 64-bit (64-bit word). O estado inicial de 1600-bit
    é totalmente preenchido com zeros (DRAFT FIPS 202).
    """

    @timeit
    def SHA3_224(self, m, verbose=False):
        tamanho_em_bits = (len(m) * 8 // 2) + 2
        # incrementamos o valor da mensagem em 2 bits
        m += '8'  # 8 é 0100
        return self.Keccak((tamanho_em_bits, m), 1152, 448, 224, verbose).lower()

    @timeit
    def BLOCOS_SHA3_224(self, blocos, verbose=False):
        for m in blocos:
            tamanho_em_bits = (len(m) * 8 // 2) + 2
            m += '8'
            if verbose:
                print('\nSHA3-224(M) = KECCAK [448] (M || 01, 224);')
                print('\nMensagem de entrada', m)  # for sha3 domain service settings
                print('\nTamanho da mensagem em bits', tamanho_em_bits)
                self.Keccak((tamanho_em_bits, m), 1152, 448, 224, verbose)
        return str(len(blocos)) + ' blocos processados com sha3 224'

    @timeit
    def SHA3_256(self, m, verbose=False):
        tamanho_em_bits = (len(m) * 8 // 2) + 2  # incrementamos o valor da mensagem em 2 bits
        m += '8'  # 8 é 0100
        return self.Keccak((tamanho_em_bits, m), 1088, 512, 256, verbose).lower()

    @timeit
    def BLOCOS_SHA3_256(self, blocos, verbose=False):
        for m in blocos:
            tamanho_em_bits = (len(m) * 8 // 2) + 2
            m += '8'
            if verbose:
                print('\nSHA3-256(M) = KECCAK [512] (M || 01, 256);')
                print('\nMensagem de entrada', m)  # for sha3 domain service settings
                print('\nTamanho da mensagem em bits', tamanho_em_bits)
            self.Keccak((tamanho_em_bits, m), 1088, 512, 256, verbose)
        return str(len(blocos)) + ' blocos processados com sha3 256'

    @timeit
    def SHA3_384(self, m, verbose=False):
        tamanho_em_bits = (len(m) * 8 // 2) + 2  # incrementamos o valor da mensagem em 2 bits
        m += '8'  # 8 é 0100
        return self.Keccak((tamanho_em_bits, m), 832, 768, 384, verbose).lower()

    @timeit
    def BLOCOS_SHA3_384(self, blocos, verbose=False):
        for m in blocos:
            m += '8'
            tamanho_em_bits = (len(m) * 8 // 2) + 2  # length ajusted
            if verbose:
                print('\nSHA3-384(M) = KECCAK [768] (M || 01, 384);')
                print('\nMensagem de entrada', m)  # for sha3 domain service settings
                print('\nTamanho da mensagem em bits', tamanho_em_bits)
            self.Keccak((tamanho_em_bits, m), 832, 768, 384, verbose)
        return str(len(blocos)) + ' blocos processados com sha3 384'

    @timeit
    def SHA3_512(self, m, verbose=False):
        tamanho_em_bits = (len(m) * 8 // 2) + 2  # incrementamos o valor da mensagem em 2 bits
        m += '8'  # 8 é 0100
        return self.Keccak((tamanho_em_bits, m), 576, 1024, 512, verbose).lower()

    @timeit
    def BLOCOS_SHA3_512(self, blocos, verbose=False):
        for m in blocos:
            m += '8'
            tamanho_em_bits = (len(m) * 8 // 2) + 2
            if verbose:
                print('\nSHA3-512(M) = KECCAK [1024] (M || 01, 512);')
                print('\nMensagem de entrada', m)  # for sha3 domain service settings
                print('\nTamanho da mensagem em bits', tamanho_em_bits)
            self.Keccak((tamanho_em_bits, m), 576, 1024, 512, verbose)
        return str(len(blocos)) + ' blocos processados com sha3 512'

    @timeit
    def SHAKE128(self, m, d=512, verbose=False):
        tamanho_em_bits = (len(m) * 8 // 2) + 4  # incrementamos o valor da mensagem em 2 bits
        m += 'F'  # 8 é 0100
        return self.Keccak((tamanho_em_bits, m), 1344, 256, d, verbose).lower()

    @timeit
    def BLOCOS_SHAKE128(self, blocos, d=512, verbose=False):
        for m in blocos:
            tamanho_em_bits = len(m) * 8 // 2
            m += 'F'  # cada bloco recebe + 'F'
            if verbose:
                print('\nSHAKE128(M, d) = KECCAK [256] (M || 1111, d);')
                print('\nMensagem de entrada', m)  # for sha3 domain service settings
                print('\nTamanho da mensagem em bits', tamanho_em_bits)
            self.Keccak((tamanho_em_bits, m), 1344, 256, d, verbose)
        return str(len(blocos)) + ' blocos processados com shake128'

    @timeit
    def SHAKE256(self, m, d=512, verbose=False):
        tamanho_em_bits = (len(m) * 8 // 2) + 4  # incrementamos o valor da mensagem em 2 bits
        m += 'F'  # F é 1111
        return self.Keccak((tamanho_em_bits, m), 1088, 512, d, verbose).lower()

    @timeit
    def BLOCOS_SHAKE256(self, blocos, d=512, verbose=False):
        for m in blocos:
            tamanho_em_bits = (len(m) * 8 // 2) + 4
            m += 'F'
            if verbose:
                print('\nSHAKE256(M, d) = KECCAK [512] (M || 1111, d);')
                print('\nMensagem de entrada', m)  # for sha3 domain service settings
                print('\nTamanho da mensagem em bits', tamanho_em_bits)
            self.Keccak((tamanho_em_bits, m), 1088, 512, d, verbose)
        return str(len(blocos)) + ' blocos processados com shake256'
