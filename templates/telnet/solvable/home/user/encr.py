import sys
	
def send(msg):
	sys.stdout.write(msg+'\n')
	sys.stdout.flush()

while (1):
	send('Enter the text you want to encrypt:')
	text = sys.stdin.readline().strip()
	if not text:
		break
	send('Here\'s your encrypted text:')
	bts = [ord(c) for c in text]
	if len(bts)%2 == 1:
		bts.append(0)
	for i in range(len(bts)/2):
		tmp = bts[2*i+1]
		bts[2*i+1] = bts[2*i]
		bts[2*i] = tmp
	send(''.join([hex(c^42)[2:] for c in bts]))
		

