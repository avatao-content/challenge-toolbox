import sys

while (1):
	print('Enter the text you want to encrypt:')
	text = sys.stdin.readline().strip()
	if not text:
		break
	print('Here\'s your encrypted text:')
	bts = [ord(c) for c in text]
	if len(bts)%2 == 1:
		bts.append(0)
	for i in range(len(bts)/2):
		tmp = bts[2*i+1]
		bts[2*i+1] = bts[2*i]
		bts[2*i] = tmp
	print ''.join([hex(c^42)[2:] for c in bts])
		

