from pwn import *

IP = 'solvable'
PORT = 8888

r = remote(IP, PORT)

r.close()