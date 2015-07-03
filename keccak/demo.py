#! /usr/bin/pythonw
# -*- coding: utf-8 -*-

import hashlib
import time
import string
import random
from base64 import b16encode

from keccak import Keccak


def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        print('%2.5f segundos' % (te - ts))
        return result

    return timed


@timeit
def BLOCOS_SHA_224(blocks):
    for b in blocks:
        hashlib.sha224(b).hexdigest()
    return str(len(blocks)) + 'blocos processados com sha224'


@timeit
def BLOCOS_SHA_256(blocks):
    for b in blocks:
        hashlib.sha256(b).hexdigest()
    return str(len(blocks)) + 'blocos processados com sha256'


@timeit
def BLOCOS_SHA_384(blocks):
    for b in blocks:
        hashlib.sha384(b).hexdigest()
    return str(len(blocks)) + 'blocos processados com sha384'


@timeit
def BLOCOS_SHA_512(blocks):
    for b in blocks:
        hashlib.sha512(b).hexdigest()
    return str(len(blocks)) + ' blocos processados com sha512'


def testBlocos():
    keccak = Keccak(b=1600)

    nroBlocos = 1024  # unidades
    tamanhoBloco = 64  # bytes

    blocks = []
    for x in range(nroBlocos):
        s = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(tamanhoBloco))
        s = b16encode(s.encode('utf-8')).decode('utf-8')
        blocks.append(s)

    # cada palavra no block tem 512 bytes
    # cada byte tem 8 bits totalizando 512 * 8 = 4096 bits
    # o bloco tem 24 palavras distintas de 4096 bits

    print(tamanhoBloco, 'bytes/bloco *', nroBlocos, 'blocos -- totalizando', nroBlocos * tamanhoBloco // 1000,
          'KB de dados\n')

    print('Tempo da familia SHA-3, processando os blocos\n')

    print('\item')
    print(keccak.BLOCOS_SHA3_224(blocks, verbose=False))
    print()

    print('\item')
    print(keccak.BLOCOS_SHA3_256(blocks, verbose=False))
    print()

    print('\item')
    print(keccak.BLOCOS_SHA3_384(blocks, verbose=False))
    print()

    print('\item')
    print(keccak.BLOCOS_SHA3_512(blocks, verbose=False))
    print()

    print('\item')
    print(keccak.BLOCOS_SHAKE128(blocks, 1024, verbose=False))
    print()

    print('\item')
    print(keccak.BLOCOS_SHAKE256(blocks, 1024, verbose=False))
    print()

    print('Tempo da familia SHA-2, processando os blocos\n')

    blocks = [elem.encode('utf-8') for elem in blocks]

    print('\item')
    print(BLOCOS_SHA_224(blocks))
    print()

    print('\item')
    print(BLOCOS_SHA_256(blocks))
    print()

    print('\item')
    print(BLOCOS_SHA_384(blocks))
    print()

    print('\item')
    print(BLOCOS_SHA_512(blocks))
    print()


hexformatter = lambda m: ' '.join(m[i:i + 16] for i in range(0, len(m), 16))  # função de utilidade


def main():
    option = input('Verificar tempos de processamento de blocos? (s/n): ')

    if option == 's':
        testBlocos()
    else:
        text = input('\nMensagem (para testar todos os digests sha3: ')
        print('\nComparar com www.di-mgt.com.au/sha_testvectors.html')

        keccak = Keccak(b=1600)
        hexstring = b16encode(text.encode('utf-8')).decode('utf-8')
        output = keccak.SHA3_224(hexstring, verbose=True)
        print('\nResumo: %s \n' % hexformatter(output))
        # output = keccak.SHA3_256(hexstring, verbose=False)
        # print('\nResumo: %s \n' % hexformatter(output))
        # output = keccak.SHA3_384(hexstring, verbose=False)
        # print('\nResumo: %s \n' % hexformatter(output))
        # output = keccak.SHA3_512(hexstring, verbose=False)
        # print('\nResumo: %s \n' % hexformatter(output))
        # output = keccak.SHAKE128(hexstring, verbose=False)
        # print('\nResumo: %s \n' % hexformatter(output))
        # output = keccak.SHAKE256(hexstring, verbose=False)
        # print('\nResumo: %s \n' % hexformatter(output))

if __name__ == "__main__":
    main()
