from glob import glob
import socket
import struct
import subprocess
import os

os.chdir('/solvable')

POPEN_ARGS = ['sudo', 'gcc', 'app/app.c'] + glob('tests/test*.c') + ['-o', 'apptest', '-lcmocka']
VALGRIND = ['sudo', '-u', 'user', 'valgrind', '--leak-check=full', './apptest']
OBJDUMP = ['sudo', '-u', 'user', 'objdump', '--dynamic-syms', './apptest']
DISABLED_F = ['rand', 'fork', 'popen', 'pipe', 'exec', 'system', 'readdir', 'opendir', 'time', 'clock']

# Bind to the exposed HTTP port to allow the controller container to connect to
BIND_TO = ('0.0.0.0', 7777)


def check_valgrind():
    try:
        output = subprocess.check_output(VALGRIND, stderr=subprocess.STDOUT, universal_newlines=True)
    except subprocess.CalledProcessError as e:
        output = e.output
    finally:
        if str(output).find(" 0 errors") != -1:
            return True, str(output)
    return False, str(output)


def check_imports():
    try:
        output = subprocess.check_output(OBJDUMP, stderr=subprocess.STDOUT, universal_newlines=True)
    except subprocess.CalledProcessError as e:
        output = e.output
    finally:
        for f in DISABLED_F:
            if str(output).find(f) != -1:
                return False
    return True


def run():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(BIND_TO)
    sock.listen(2)

    while True:
        try:
            conn, addr = sock.accept()
            try:
                success = 0
                valgrind = False
                imports = False
                subprocess.check_output(['chmod', '-R', '+x'] + glob('tests/'), stderr=subprocess.STDOUT)
                try:
                    try:
                        os.remove("./apptest")
                    except:
                        pass
                    output = subprocess.check_output(POPEN_ARGS, stderr=subprocess.STDOUT, universal_newlines=True) + subprocess.check_output(['sudo', '-u', 'user', './apptest'], stderr=subprocess.STDOUT, universal_newlines=True)
                except subprocess.CalledProcessError as e:
                    output = e.output
                output = str(output)

                if os.path.isfile("./apptest"):
                    additional_errors = ""
                    valgrind, val_out = check_valgrind()
                    if not valgrind:
                        if val_out.find("All heap blocks were freed") == -1:
                            additional_errors = "Memory leak detected!\n" + additional_errors
                        else:
                            additional_errors = "Invalid read/write!\n" + additional_errors

                    if check_imports():
                        imports = True
                    else:
                        additional_errors = "You should not use that function!\n" + additional_errors

                    if output.find("FAILED") == -1 and output.find("[  PASSED  ] 9 test(s)") != -1:
                        if valgrind and imports:
                            success = 1
                        else:
                            output = additional_errors + output

                output = output.encode()
                conn.send(struct.pack('h', success))
                conn.send(struct.pack('I', len(output)))
                conn.send(output)
            except subprocess.CalledProcessError as e:
                output = str(e.output).encode()
                conn.send(struct.pack('h', 0))
                conn.send(struct.pack('I', len(output)))
                conn.send(output)
            finally:
                try:
                    subprocess.check_output(['chmod', '-R', '-x'] + glob('tests/'), stderr=subprocess.STDOUT)
                except:
                    pass
        except Exception as e:
            print(e)
        finally:
            conn.close()
    sock.close()

if __name__ == '__main__':
    run()
