# Copyright (c) 2017  Niklas Rosenstein
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the follo  wing conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import argparse
import config
import docbrowser

parser = argparse.ArgumentParser()
parser.add_argument('addr', nargs='?', help='[host:]port', default=config.address)
parser.add_argument('--debug', action='store_true', default=config.debug)

def main():
  args = parser.parse_args()
  addr = (args.addr or ':8000').split(':', 1)
  if len(addr) == 1:
    addr.insert(0, '0.0.0.0')
  try:
    addr[1] = int(addr[1])
  except ValueError:
    parser.error('port must be an integer, got {!r}'.format(addr[1]))

  docbrowser.app.run(host=addr[0], port=addr[1], debug=args.debug)

if __name__ == '__main__':
  main()
