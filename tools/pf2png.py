#!/usr/bin/env python3

# pf2png
# Convert MiSTer UI font (1bpp bitmap) to 16*n character sheet PNG image.
#
# Program by David Lindecrantz <optiroc@gmail.com>
# Distributed under the terms of the MIT license

import argparse
import os
import sys
import png

def is_file(parser, arg):
  if not os.path.isfile(arg): parser.error("file %s does not exist" % arg)
  else: return arg

def chunks(seq, size):
  return (seq[pos:pos + size] for pos in range(0, len(seq), size))

def main():
  try:
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--in-pf", dest="in_pf", metavar="FILE", required=True, type=lambda x: is_file(parser, x), help="input bitmap")
    parser.add_argument("-o", "--out-png", dest="out_png", metavar="FILE", help="output png")
    args = parser.parse_args()

    pf = list(open(args.in_pf, "rb").read())

    if args.out_png:
      chars_per_line = 16
      png_rows = []
      for (char_index, char) in enumerate(chunks(pf, 8)):
        for (char_line, char_byte) in enumerate(char):
          png_line = (char_index // chars_per_line) * 8 + char_line
          if len(png_rows) <= png_line:
            png_rows.append([])
          png_row = png_rows[png_line]
          for bit in range(7, -1, -1):
            png_row.append(255 if ((char_byte >> bit) & 1) else 0)

      with open(args.out_png, "wb") as file:
        writer = png.Writer(size=(len(png_rows[0]),len(png_rows)), greyscale=True, compression=9)
        writer.write(file, png_rows)

    return 0

  except Exception as err:
    print("error - {}".format(err))
    sys.exit(1)

if __name__ == "__main__":
  sys.exit(main())
