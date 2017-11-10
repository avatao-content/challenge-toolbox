#!/usr/bin/env python3
import json
import requests
import sys

flag = sys.argv[1] if len(sys.argv) > 1 else 'flag'
data = json.dumps({'solution': flag})
headers = {'Content-Type': 'application/json'}
resp = requests.post('http://127.0.0.1:5555/secret', headers=headers, data=data)
print(resp.text)
