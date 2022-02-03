from chacha import U32_MAX, KEY_LEN, NONCE_LEN
from png import *
import random
import sys

from lib import *

def encode(message: bytes) -> bytearray:
    # generate random key and nonce
    key = random.sample(range(U32_MAX), k=KEY_LEN)
    nonce = random.sample(range(U32_MAX), k=NONCE_LEN)

    # compute ciphertext
    ciphertext = compute_xored_message_stream(key, nonce, message)

    # prepare payload for the png image
    payload = u32s_to_bytes(key)
    payload += u32s_to_bytes(nonce)
    payload += ciphertext

    return payload

# TODO: don't inject if there's already one
def inject(png: bytearray, payload: bytearray) -> None:
    # check png magic number (if it doesn't have this it's invalid png)
    assert check_png_sig(png), "not a png file"

    # iterate through png bytes
    i = PNG_SIG_LEN
    while i < len(png):
        # get chunk length
        chunk_len = int.from_bytes(png[i : i + PNG_LEN_LEN], "big")
        i += PNG_LEN_LEN

        # get chunk type
        chunk_type = png[i : i + PNG_TYPE_LEN]
        i += PNG_TYPE_LEN

        # keep skipping until the last chunk
        if chunk_type == b"IEND":
            # get "out" of this chunk (we're up to the data section)
            i -= PNG_TYPE_LEN
            i -= PNG_LEN_LEN

            # insert payload
            ## chunk length
            png[i:i] = len(payload).to_bytes(4, "big")
            i += PNG_LEN_LEN

            ## chunk type
            png[i:i] = MAGIC_TYPE
            i += PNG_TYPE_LEN

            ## chunk data
            png[i:i] = payload
            i += len(payload)

            ## chunk crc
            ## image viewers don't care, so crc is 0
            ## i also don't know how to compute crc
            png[i:i] = (0).to_bytes(4, "big")
            i += PNG_CRC_LEN

            return

        else:
            i += chunk_len
            i += PNG_CRC_LEN

def main(path: str) -> None:
    # inject png with payload
    with open(path, "rb+") as f:
        # get message from stdin
        message = sys.stdin.buffer.read()

        # "encode" the message with chacha
        payload = encode(message)

        # read the png file
        png = bytearray(f.read())

        # inject the payload
        inject(png, payload)

        # overwrite the file
        f.seek(0)
        f.write(png)

if __name__ == "__main__":
    args = sys.argv

    if len(args) != 2:
        print("usage: encode.py <PNG FILE PATH>", file=sys.stderr)
        print(f"fatal: expected 1 argument but found {len(args) - 1}", file=sys.stderr)
        exit(1)

    path = args[1]

    main(path)
