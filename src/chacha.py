from copy import deepcopy
from typing import List, Tuple

# Used <https://en.wikipedia.org/wiki/Salsa20#ChaCha_variant> for reference

U32_BYTES = 4
U32_MAX = 2**32 - 1

KEY_LEN = 8
NONCE_LEN = 3
KEY_BYTES = KEY_LEN * U32_BYTES
NONCE_BYTES = NONCE_LEN * U32_BYTES

CONSTANT = [
    0x61707865, # b"expa"
    0x3320646e, # b"nd 3"
    0x79622d32, # b"2-by"
    0x6b206574, # b"te k"
]

def trunc(value: int) -> int:
    return value & U32_MAX

# Used <https://en.wikipedia.org/wiki/Circular_shift#Implementing_circular_shifts> for reference
def rotl32(value: int, count: int) -> int:
    return trunc((value << count) | (value >> (32 - count)))

def qr(a: int, b: int, c: int, d: int) -> Tuple[int, int, int, int]:
    a = trunc(a + b); d = trunc(d ^ a); d = rotl32(d, 16)
    c = trunc(c + d); b = trunc(b ^ c); b = rotl32(b, 12)
    a = trunc(a + b); d = trunc(d ^ a); d = rotl32(d,  8)
    c = trunc(c + d); b = trunc(b ^ c); b = rotl32(b,  7)

    return (a, b, c, d)

def qr_mut(state: List[int], a: int, b: int, c: int, d: int) -> None:
    (state[a], state[b], state[c], state[d]) = qr(state[a], state[b], state[c], state[d])

def block(state: List[int], rounds: int) -> List[int]:
    assert len(state) == 16

    # save copy of original for matrix multiplication
    state = deepcopy(state)
    original = deepcopy(state)

    # compute quarter rounds
    for i in range(rounds):
        if i & 1 == 0:
            qr_mut(state, 0, 4,  8, 12) # column 1
            qr_mut(state, 1, 5,  9, 13) # column 2
            qr_mut(state, 2, 6, 10, 14) # column 3
            qr_mut(state, 3, 7, 11, 15) # column 4
        else:
            qr_mut(state, 0, 5, 10, 15) # diagonal 1
            qr_mut(state, 1, 6, 11, 12) # diagonal 2
            qr_mut(state, 2, 7,  8, 13) # diagonal 3
            qr_mut(state, 3, 4,  9, 14) # diagonal 4

    # add original state to new state
    for x in range(len(state)):
        state[x] = trunc(state[x] + original[x])

    return state

def test() -> None:
    # rfc 7539 2.1.1
    assert qr(
        0x11111111,
        0x01020304,
        0x9b8d6f43,
        0x01234567,
    ) == (
        0xea2a92f4,
        0xcb1cf8ce,
        0x4581472e,
        0x5881c4bb,
    )
    # rfc 7539 2.3.2
    assert block([
        0x61707865, 0x3320646e, 0x79622d32, 0x6b206574,
        0x03020100, 0x07060504, 0x0b0a0908, 0x0f0e0d0c,
        0x13121110, 0x17161514, 0x1b1a1918, 0x1f1e1d1c,
        0x00000001, 0x09000000, 0x4a000000, 0x00000000,
    ], 20) == [
        0xe4e7f110, 0x15593bd1, 0x1fdd0f50, 0xc47120a3,
        0xc7f4d1c7, 0x0368c033, 0x9aaa2204, 0x4e6cd4c3,
        0x466482d2, 0x09aa9f07, 0x05d7c214, 0xa2028bd9,
        0xd19c12b5, 0xb94e16de, 0xe883d0cb, 0x4e3c50a2,
    ]

if __name__ == "__main__":
    test()
