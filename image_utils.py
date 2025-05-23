import io


def _read_token(f):
    token = b''
    ch = f.read(1)
    while ch and ch.isspace():
        ch = f.read(1)
    while ch and not ch.isspace():
        token += ch
        ch = f.read(1)
    return token


def load_ppm(data: bytes):
    """Load binary PPM (P6) image from bytes."""
    f = io.BytesIO(data)
    magic = _read_token(f)
    if magic != b'P6':
        raise ValueError('Only binary PPM (P6) supported')
    width = int(_read_token(f))
    height = int(_read_token(f))
    maxval = int(_read_token(f))
    pixels = bytearray(f.read())
    return width, height, maxval, pixels


def save_ppm_bytes(width: int, height: int, maxval: int, pixels: bytes) -> bytes:
    header = f'P6\n{width} {height}\n{maxval}\n'.encode('ascii')
    return header + pixels
