import os
import json

FILTERS_DIR = os.path.join('data', 'filters')

PREDEFINED = {
    'invert': {'type': 'invert'},
    'brighten': {'type': 'brightness', 'amount': 30},
    'darken': {'type': 'brightness', 'amount': -30},
}


def load_user_filters():
    filters = {}
    if os.path.isdir(FILTERS_DIR):
        for fname in os.listdir(FILTERS_DIR):
            if fname.endswith('.json'):
                path = os.path.join(FILTERS_DIR, fname)
                with open(path, 'r') as f:
                    filters[os.path.splitext(fname)[0]] = json.load(f)
    return filters


def all_filters():
    filters = PREDEFINED.copy()
    filters.update(load_user_filters())
    return filters


def save_filter(name: str, data: dict):
    """Save a filter definition under a sanitized name."""
    safe_name = os.path.basename(name)
    if not safe_name or safe_name in ('.', '..'):
        raise ValueError('Invalid filter name')
    os.makedirs(FILTERS_DIR, exist_ok=True)
    path = os.path.join(FILTERS_DIR, safe_name + '.json')
    with open(path, 'w') as f:
        json.dump(data, f)


def create_difference_filter(orig_pixels: bytes, filtered_pixels: bytes):
    if len(orig_pixels) != len(filtered_pixels):
        raise ValueError('Images must be same size')
    dr = dg = db = 0
    count = len(orig_pixels) // 3
    for i in range(0, len(orig_pixels), 3):
        dr += filtered_pixels[i] - orig_pixels[i]
        dg += filtered_pixels[i+1] - orig_pixels[i+1]
        db += filtered_pixels[i+2] - orig_pixels[i+2]
    return {
        'type': 'difference',
        'dr': dr / count,
        'dg': dg / count,
        'db': db / count,
    }


def apply_filter(pixels: bytearray, filter_def: dict, maxval: int):
    if filter_def['type'] == 'invert':
        for i in range(len(pixels)):
            pixels[i] = maxval - pixels[i]
    elif filter_def['type'] == 'brightness':
        amt = filter_def.get('amount', 0)
        for i in range(len(pixels)):
            val = pixels[i] + amt
            if val < 0:
                val = 0
            if val > maxval:
                val = maxval
            pixels[i] = val
    elif filter_def['type'] == 'difference':
        dr = filter_def.get('dr', 0)
        dg = filter_def.get('dg', 0)
        db = filter_def.get('db', 0)
        for i in range(0, len(pixels), 3):
            r = pixels[i] + dr
            g = pixels[i+1] + dg
            b = pixels[i+2] + db
            pixels[i] = int(min(max(r, 0), maxval))
            pixels[i+1] = int(min(max(g, 0), maxval))
            pixels[i+2] = int(min(max(b, 0), maxval))
    else:
        raise ValueError('Unknown filter type')
