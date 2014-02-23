#!/usr/bin/env python
#
# Copyright 2014 Steven Le (stevenle08@gmail.com)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Command-line utility to compile Go code via github and a cloud compiler."""

__author__ = 'stevenle08@gmail.com (Steven Le)'

import argparse
import json
import os
import stat
import gserviceaccount
import requests


class Error(Exception):
  pass


def build(args):
  private_key = open(args.private_key).read()
  access_token = gserviceaccount.access_token(args.client_id, private_key)

  headers = {
      'Authorization': 'Bearer {}'.format(access_token),
      'Content-Type': 'application/json',
  }

  request = {
      'src': 'https://github.com/stevenle/pi.git',
      'pkg': 'github.com/stevenle/pi',
      'target': 'github.com/stevenle/pi/{}'.format(target),
  }
  payload = json.dumps(request)

  response = requests.post(args.gocloud, headers=headers, data=payload)
  if response.status_code != 200:
    raise Error('Error {}'.format(response.status_code))

  with open(args.output, 'w') as fp:
    fp.write(response.content)

  # Equivalent to chmod +x.
  os.chmod(args.output, os.stat(args.output).st_mod | stat.S_IEXEC)


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--client_id', '-c', dest='client_id')
  parser.add_argument('--private_key', '-k', dest='private_key')
  parser.add_argument('--gocloud')
  parser.add_argument('--output', '-o', dest='output')
  parser.add_argument('cmd')
  parser.add_argument('target')
  args = parser.parse_args()

  if not args.client_id:
    raise Error('Missing --client_id.')
  if not args.private_key or not os.path.exists(args.private_key):
    raise Error('Missing --private_key.')
  if not args.gocloud:
    raise Error('Missing --gocloud.')
  if args.cmd != 'build':
    raise Error('Unsupported command: {}'.format(args.cmd))

  build(args)


if __name__ == '__main__':
  main()
