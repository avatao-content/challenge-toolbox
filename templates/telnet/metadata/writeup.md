Black box crypto
================

## Understanding the problem

Cost: 10%

Let's see what we have: An encrypted text and access to the service that encrypted it. The flag is likely the text that was encrypted, so we'll have to figure out how to decrypt it, which means we also have to figure out the encryption algorithm used by the server.
Since we don't have access to the server's code, we'll have to resort to manual fuzzing: Let's try sending in a few plaintexts and see what kind of outputs we get!
Here are some samples:

    AA -> 6b6b
    AAAA ->6b6b6b6b
    BB -> 6868
    BBBB -> 68686868

At first glance, it looks like each byte of the plaintext gets transformed into a different byte whose hex representation is then printed. Upon further inspection, however, we can see that this is not quite the case:

    AB -> 686b
    BAAB ->6b68686b
    ABAB -> 686b686b

Now we're getting `68` at `A`'s position in the plaintext and `6b` at `B`'s, the exact opposite of what happened before! What's going on?

## Figuring out the relationship between the plaintext and the ciphertext bytes

Cost: 40%

Let's do some more fuzzing to determine how the plaintext bytes affect the bytes in the encrypted text!

    AAAA -> 6b6b6b6b
    BAAA -> 6b686b6b
    AAAB -> 6b6b686b
    CAAA -> 6b696b6b
    AAAC -> 6b6b696b

It seems that a byte-change in the plaintext only affects one byte in the ciphertext. If we divide the plaintext into groups of 2 characters, we can see that modifying one of the two chars in a group changes the other byte in the same group in the ciphertext. In other words, the server's encryption algorithm is something like this:

    for i from 0 to length(plaintext)/2:
        ciphertext[i*2] = encrypt_char(plaintext[i*2+1]) 
        ciphertext[i*2+1] = encrypt_char(plaintext[i*2])

Now all that remains is to reverse-engineer the `encrypt_char` function!

## Figuring out the how the characters are encrypted

Cost: 40%

Now that we know which plaintext byte corresponds to which ciphertext byte, let's see if we can figure out the algorithm used to "encrypt" the bytes. Here are some plaintext-ciphertext samples:

    plaintext: A 0x41 1000001
    ciphertext:  0x6b 1101011

    plaintext: B 0x42 1000010
    ciphertext:  0x68 1101000

    plaintext: X 0x58 1011000
    ciphertext:  0x72 1110010

    plaintext: a 0x61 1100001
    ciphertext:  0x4b 1001011

Let's look for a pattern. In the character `A`, the second, fourth and sixth bits change from `0` to `1`. In `B`, the second bit changes from `1` to `0`, and the fourth and sixth change from `0` to `1`. It seems that the encryption algorithm simply flips the second, fourth and sixth bits of the plaintext byte (i.e. XORs it with `0b101010`, or `42`). So the encryption looks like this:

    encrypt_char(char):
        return char ^ 42

To reverse this, all we have to do is XOR the bytes with `42` again and we'll get the original plaintext characters back. Now all we have to do is put them into the correct order!

## Complete solution

The following python script decrypts the text given in the challenge description:

    cipher = '4b795162425d5e1e1e757544726f6669797f7c63756f4249461e4f464d44754f425e534f5975585f75197d797e1b62696e6f5e751b424d4475595a5f4b7548755e434b754b424b424d755e4f1b75155e2a57'

    # Turn ciphertext into bytes
    cipher_bytes = ''
    for i in range(len(cipher)/2):
        cipher_bytes += chr(int(cipher[i*2:i*2+2], 16));

    # Decrypt the ciphertext
    plaintext = ''
    for i in range(len(cipher_bytes)/2):
        plaintext += chr(ord(cipher_bytes[i*2+1])^42)
        plaintext += chr(ord(cipher_bytes[i*2])^42)

    print(plaintext)
