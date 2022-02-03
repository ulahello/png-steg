PNG_SIG_LEN = 8
PNG_LEN_LEN = 4
PNG_TYPE_LEN = 4
PNG_CRC_LEN = 4

def check_png_sig(png: bytearray) -> bool:
    # each png file begins with a specific sequence of 8 bytes
    return png[: PNG_SIG_LEN] == bytearray([137, 80, 78, 71, 13, 10, 26, 10])
