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

"""Google service account JWT signing utility."""

__author__ = 'stevenle08@gmail.com (Steven Le)'

import base64
import json
import os
import sys
import time
from Crypto.Hash import SHA256 as sha256
from Crypto.PublicKey import RSA as rsa
from Crypto.Signature import PKCS1_v1_5 as pkcs1_v1_5
import requests

JWT_HEADER = '{"alg":"RS256","typ":"JWT"}'


class Error(Exception):
  pass


def encode(s):
  return base64.urlsafe_b64encode(s)


def sign(jwt_claim, private_key_pem):
  """Signs a JWT claim and returns the encoded assertion."""
  if not private_key_pem.startswith('-----BEGIN PRIVATE KEY-----'):
    raise Error(
        'Private key should be in PEM format. '
        'Run: openssl pkcs12 -in <key>.p12 -out <key>.pem -nocerts -nodes')

  signature_base = '{}.{}'.format(
      encode(JWT_HEADER), encode(json.dumps(jwt_claim, sort_keys=True)))
  rsa_key = rsa.importKey(private_key_pem)
  signature = pkcs1_v1_5.new(rsa_key).sign(sha256.new(signature_base))

  assertion = '{}.{}'.format(signature_base, encode(signature))
  return assertion


def access_token(client_id, private_key_pem, duration=300):
  """Returns an access token for a service account."""
  iat = int(time.time())
  exp = iat + duration
  jwt_claim = {
      'iss': '{}@developer.gserviceaccount.com'.format(client_id),
      'scope': 'https://www.googleapis.com/auth/userinfo.email',
      'aud': 'https://accounts.google.com/o/oauth2/token',
      'exp': exp,
      'iat': iat,
  }

  jwt_assertion = sign(jwt_claim, private_key_pem)
  response = requests.post('https://accounts.google.com/o/oauth2/token', data={
    'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
    'assertion': jwt_assertion,
  })
  return response.json()['access_token']
