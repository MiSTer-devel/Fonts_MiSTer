#!/usr/bin/env python3

# png2pf
# Convert PNG image to MiSTer UI font (1bpp bitmap),
# and optionally a nicely formatted preview image.
#
# Program by David Lindecrantz <optiroc@gmail.com>
# Distributed under the terms of the MIT license

import argparse
import functools
import os
import sys
import png

def is_file(parser, arg):
  if not os.path.isfile(arg): parser.error("file %s does not exist" % arg)
  else: return arg

def chunks(seq, size):
  return (seq[pos:pos + size] for pos in range(0, len(seq), size))

# read png as 2D bitmap array (bool[][])
def read_png_1bpp(path):
  (_, _, data, _) = png.Reader(file=open(path, "rb")).asRGBA8()
  bitmap = []
  for line in data:
    l = []
    for rgba in chunks(line, 4):
      l.append((rgba[3] > 127) and (0.2989 * rgba[0] + 0.5870 * rgba[1] + 0.1140 * rgba[2]) < 128)
    bitmap.append(l)
  return bitmap

# slice 2D array into dim*dim sized tiles
def make_tiles(pixels, dim=8):
  if len(pixels) % dim != 0:
    raise Exception("image height not a multiple of {}".format(dim))
  if len(pixels[0]) % dim != 0:
    raise Exception("image width not a multiple of {}".format(dim))
  tiles = []
  for y in range(0, len(pixels), dim):
    for x in range(0, len(pixels[0]), dim):
      tiles.append([pixels[y+yl][x:x+dim] for yl in range(dim)])
  return tiles

# write preview png
def write_preview(bitmap, path, dim=8):
  scale = 4
  width = scale * (1 + len(bitmap[0]) + len(bitmap[0]) // dim)
  height = scale * (1 + len(bitmap) + len(bitmap) // dim)
  tiles = make_tiles(bitmap, dim)
  pixels = [bytearray(width) for i in range(height)]

  for ypos in range(scale, height, scale * (dim + 1)):
    for xpos in range(scale, width, scale * (dim + 1)):
      blit_bitmap(tiles.pop(0), pixels, xpos, ypos, scale)

  with open(path, "wb") as file:
    writer = png.Writer(size=(width,height), greyscale=True, compression=9)
    writer.write(file, pixels)

# blit bitmap (int/bool[][]) to pixel array (bytearray[][])
def blit_bitmap(src_bitmap, dest_pixels, xpos, ypos, scale=1):
  for srcy, row in enumerate(src_bitmap):
    for srcx, pixel in enumerate(row):
      val = int(pixel) if not isinstance(pixel, bool) else (255 if pixel else 0)
      dx = xpos + srcx * scale
      dy = ypos + srcy * scale
      for dx,dy in [(x,y) for x in range(dx, dx + scale) for y in range(dy, dy + scale)]:
        dest_pixels[dy][dx] = val

def main():
  try:
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--in-png", dest="in_png", metavar="FILE", required=True, type=lambda x: is_file(parser, x), help="input png")
    parser.add_argument("-o", "--out-pf", dest="out_pf", metavar="FILE", help="output bitmap")
    parser.add_argument("-p", "--out-preview", dest="out_preview", metavar="FILE", help="output preview image")
    args = parser.parse_args()

    bitmap = read_png_1bpp(args.in_png)

    if args.out_pf:
      pf = bytearray()
      for tile in make_tiles(bitmap):
        for line in tile:
          pf.append(functools.reduce(lambda a,b: (a << 1) + b, line))
      with open(args.out_pf, "wb") as file:
        file.write(pf)

    if args.out_preview:
      write_preview(bitmap, args.out_preview)

    return 0

  except Exception as err:
    print("error - {}".format(err))
    sys.exit(1)

if __name__ == "__main__":
  sys.exit(main())
