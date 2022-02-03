from chacha import block, CONSTANT, U32_BYTES

from typing import List

# the type of the chunk the encoder & decoder use as storage for the encoded message
MAGIC_TYPE = b"chCh"

CHACHA_ROUNDS: int = 20

def u32s_to_bytes(u32s: List[int]) -> bytearray:
    bytes = bytearray()
    for n in u32s:
        bytes += n.to_bytes(U32_BYTES, "little")
    return bytes

def bytes_to_u32s(bytes: bytearray) -> List[int]:
    u32s = list()
    for i in range(0, len(bytes), U32_BYTES):
        u32s.append(int.from_bytes(bytes[i : i + U32_BYTES], "little"))
    return u32s

def compute_xored_message_stream(key: List[int], nonce: List[int], message: bytes) -> bytearray:
    # compute stream
    stream = bytearray()
    state_init = [
        CONSTANT[0], CONSTANT[1], CONSTANT[2], CONSTANT[3],
        key[0], key[1], key[2], key[3],
        key[4], key[5], key[6], key[7],
        0, nonce[0], nonce[1], nonce[2],
    ]

    while len(stream) < len(message) * U32_BYTES:
        stream += u32s_to_bytes(block(state_init, CHACHA_ROUNDS))
        state_init[12] += 1 # increment counter

    # xor stream with message
    xored_message = bytearray()
    for i in range(len(message)):
        xored_message.append(message[i] ^ stream[i])

    return xored_message
