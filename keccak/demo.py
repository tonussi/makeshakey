#! /usr/bin/pythonw
# The Keccak sponge function, designed by Guido Bertoni, Joan Daemen,
# Michaël Peeters and Gilles Van Assche. For more information, feedback or
# questions, please refer to our website: http://keccak.noekeon.org/
# 
# Implementation by Renaud Bauvin,
# hereby denoted as "the implementer".
# 
# To the extent possible under law, the implementer has waived all copyright
# and related or neighboring rights to the source code in this file.
# http://creativecommons.org/publicdomain/zero/1.0/

from keccak import Keccak


def main():
    myKeccak = Keccak(b=1600)


    # The four SHA-3 hash functions are defined from the KECCAK [c] function specified in Sec. 5.2 by
    # appending two bits to the message and by specifying the length of the output, as follows:

    # SHA3-224(M) = KECCAK [448] (M || 01, 224); (56  byte)
    #myKeccak.Keccak((16, 'bbbb' + '01'), r=1152, c=448, n=224, verbose=True)
    # SHA3-256(M) = KECCAK [512] (M || 01, 256); (64  byte)
    #myKeccak.Keccak((16, 'bbbb' + '01'), r=1088, c=512, n=256, verbose=True)
    # SHA3-384(M) = KECCAK [768] (M || 01, 384); (96  byte)
    #myKeccak.Keccak((16, 'bbbb' + '01'), r=832, c=768, n=384, verbose=True)
    # SHA3-512(M) = KECCAK [1024] (M || 01, 512). (128 byte)
    #myKeccak.Keccak((16, 'bbbb' + '01'), r=576, c=1024, n=512, verbose=True)

    # The two SHA-3 XOFs can also be defined directly from K ECCAK , as follows:

    # SHAKE128(M, d) = KECCAK [256] (M || 1111, d),
    myKeccak.Keccak((16, 'bbbb' + '11'), r=1344, c=256, n=0, verbose=True)
    # SHAKE256(M, d) = KECCAK [512] (M || 1111, d).
    #myKeccak.Keccak((16, 'bbbb' + '11'), r=1088, c=512, n=0, verbose=True)


if __name__ == "__main__":
    main()
