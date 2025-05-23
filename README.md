# filterlearner

This project provides a minimal image filter learning web service that relies
only on Python's standard library. Images must be uploaded in binary PPM (P6)
format.

## Running the server

```
python3 filter_server.py
```

The server listens on port `8000` by default. Navigate to
`http://localhost:8000/` to access the web interface.

## Features

* **Learn Filter** – Upload an original image and the same image with a filter
  applied. A simple colour difference filter is computed and stored under the
  provided name.
* **Apply Filter** – Upload an image and choose from predefined filters
  (`invert`, `brighten`, `darken`) or previously learned filters. The server
  returns the filtered image as a PPM file.

Because no third-party dependencies are used, only PPM images are supported.

## Converting images

If you have ImageMagick installed you can convert common formats to PPM with:

```
convert input.jpg output.ppm
```

This produces a binary PPM (P6) file suitable for upload.
