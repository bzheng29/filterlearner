import os
import cgi
from wsgiref.simple_server import make_server
from wsgiref.util import setup_testing_defaults
from io import BytesIO
from image_utils import load_ppm, save_ppm_bytes
import filters as flt

STATIC_DIR = os.path.join(os.path.dirname(__file__), 'static')


def render_index():
    filter_names = sorted(flt.all_filters().keys())
    options = "\n".join(
        f'<option value="{name}">{name}</option>' for name in filter_names
    )
    index_path = os.path.join(STATIC_DIR, 'index.html')
    with open(index_path, 'r', encoding='utf-8') as f:
        html = f.read()
    html = html.replace('{{options}}', options)
    return html.encode('utf-8')


def handle_learn(environ):
    form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)
    name = form.getfirst('name', '').strip()
    if not name:
        return b'Filter name required', '400 Bad Request', 'text/plain'
    orig_file = form['original']
    filt_file = form['filtered']
    if not getattr(orig_file, 'file', None) or not getattr(filt_file, 'file', None):
        return b'Both images required', '400 Bad Request', 'text/plain'
    orig_data = orig_file.file.read()
    filt_data = filt_file.file.read()
    ow, oh, maxval, orig_pixels = load_ppm(orig_data)
    fw, fh, _, filt_pixels = load_ppm(filt_data)
    if ow != fw or oh != fh:
        return b'Images must be same size', '400 Bad Request', 'text/plain'
    filter_def = flt.create_difference_filter(orig_pixels, filt_pixels)
    flt.save_filter(name, filter_def)
    return b'Filter saved', '200 OK', 'text/plain'


def handle_apply(environ):
    form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)
    filter_name = form.getfirst('filter', '')
    filt = flt.all_filters().get(filter_name)
    if not filt:
        return b'Unknown filter', '400 Bad Request', 'text/plain'
    img_file = form['image']
    if not getattr(img_file, 'file', None):
        return b'Image required', '400 Bad Request', 'text/plain'
    img_data = img_file.file.read()
    w, h, maxval, pixels = load_ppm(img_data)
    flt.apply_filter(pixels, filt, maxval)
    out_data = save_ppm_bytes(w, h, maxval, pixels)
    return out_data, '200 OK', 'image/x-portable-pixmap'


def app(environ, start_response):
    setup_testing_defaults(environ)
    path = environ.get('PATH_INFO', '/')
    if environ['REQUEST_METHOD'] == 'GET' and path == '/':
        data = render_index()
        start_response('200 OK', [('Content-Type', 'text/html')])
        return [data]
    elif environ['REQUEST_METHOD'] == 'GET' and path.startswith('/static/'):
        file_path = os.path.join(STATIC_DIR, path[len('/static/'):])
        if os.path.isfile(file_path):
            with open(file_path, 'rb') as f:
                data = f.read()
            ctype = 'text/css' if file_path.endswith('.css') else 'text/html'
            start_response('200 OK', [('Content-Type', ctype)])
            return [data]
        else:
            start_response('404 Not Found', [('Content-Type', 'text/plain')])
            return [b'Not Found']
    elif environ['REQUEST_METHOD'] == 'POST' and path == '/learn':
        data, status, ctype = handle_learn(environ)
    elif environ['REQUEST_METHOD'] == 'POST' and path == '/apply':
        data, status, ctype = handle_apply(environ)
    else:
        status = '404 Not Found'
        data = b'Not Found'
        ctype = 'text/plain'
    start_response(status, [('Content-Type', ctype)])
    return [data]


if __name__ == '__main__':
    port = int(os.environ.get('PORT', '8000'))
    with make_server('', port, app) as httpd:
        print(f'Serving on port {port}...')
        httpd.serve_forever()
