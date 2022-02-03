from chacha import KEY_BYTES, NONCE_BYTES
from png import *
import sys

from lib import *

from typing import Optional

def decode(encoded: bytearray) -> bytearray:
    # input must have enough bytes to parse 8 byte key and 3 byte nonce
    assert len(encoded) >= KEY_BYTES + NONCE_BYTES, "input is too short"

    # parse key and nonce
    key = bytes_to_u32s(encoded[: KEY_BYTES])
    nonce = bytes_to_u32s(encoded[KEY_BYTES : KEY_BYTES + NONCE_BYTES])
    message = encoded[KEY_BYTES + NONCE_BYTES :]

    # compute plaintext
    plaintext = compute_xored_message_stream(key, nonce, message)

    return plaintext

# TODO: detect if there's more than one chCh chunk
def parse_injected_payload(png: bytearray) -> Optional[bytearray]:
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

        # keep skipping until the payload chunk
        if chunk_type == MAGIC_TYPE:
            # read chunk data and return
            chunk_data = png[i : i + chunk_len]
            return chunk_data

        else:
            i += chunk_len
            i += PNG_CRC_LEN

    return None

def main(path: str) -> None:
    # open png containing payload
    with open(path, "rb") as f:
        # read png file
        png = bytearray(f.read())

        # get encoded message from png
        encoded = parse_injected_payload(png)

        if encoded is not None:
            # decode message
            decoded = decode(bytearray(encoded))

            # print decoded message
            sys.stdout.buffer.write(decoded)
        else:
            print("fatal: no payload found", file=sys.stderr)
            exit(1)

if __name__ == "__main__":
    args = sys.argv

    if len(args) != 2:
        print("usage: decode.py <PNG FILE PATH>", file=sys.stderr)
        print(f"fatal: expected 1 argument but found {len(args) - 1}", file=sys.stderr)
        exit(1)

    path = args[1]

    main(path)
