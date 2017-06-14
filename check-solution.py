#!/usr/bin/env python3

import requests
import sys

flag = "null"
if len(sys.argv) > 1:
	flag = sys.argv[1]

headers = {
    'Content-Type': 'application/json',
}

data = '{"solution":"' + flag + '"}'

r = requests.post('http://127.0.0.1:5555/secret', headers=headers, data=data)
print(r.text)
