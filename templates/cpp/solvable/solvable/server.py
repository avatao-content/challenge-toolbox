from contextlib import suppress
from enum import Enum
from functools import partial
import os
import pickle
import socketserver
import subprocess
import sys

SOLUTION = 'app/geomean.cpp'
OBJECT = 'solution.o'
EXECUTABLE = 'solution'
TEST_EXECUTABLE = 'tests/apptest'

LINKED_DYNAMICALLY = False

COMPILE_TEST_EXECUTABLE = ['sudo', 'make', '-C', 'tests']
COMPILE_OBJECT = ['sudo', 'g++', '-std=c++14', '-c', SOLUTION, '-o', OBJECT]
COMPILE_EXECUTABLE = ['sudo', 'g++', '-std=c++14', 'main.cpp', '-o', EXECUTABLE]
VALGRIND = ['sudo', '-u', 'user', 'valgrind', '--leak-check=full', '--show-leak-kinds=all', TEST_EXECUTABLE]
OBJDUMP = ['sudo', '-u', 'user', 'objdump', '--syms', EXECUTABLE]
OBJDUMP_DYNAMIC = ['sudo', '-u', 'user', 'objdump', '--dynamic-syms', EXECUTABLE]
DISABLED_FUNCTIONS = ['fork', 'popen', 'pipe', 'exec', 'system', 'readdir', 'opendir', 'clock', 'time', 'rand']


SolutionCheckTypes = Enum('SolutionCheckTypes',
                          [
                              'MEMORY_LEAK',
                              'INVALID_READ_WRITE',
                              'DISABLED_FUNCTION',
                              'FAILED_UNIT_TEST'
                          ])


class SolutionCheckError(Exception):
    error_messages = {
        SolutionCheckTypes.MEMORY_LEAK: 'Memory leak detected!\n',
        SolutionCheckTypes.INVALID_READ_WRITE: 'Invalid read/write!',
        SolutionCheckTypes.DISABLED_FUNCTION: 'You should not use the following function: {}',
        SolutionCheckTypes.FAILED_UNIT_TEST: 'Not all unit tests passed:\n{}'
    }

    def __init__(self, cause: SolutionCheckTypes, *args):
        super().__init__()
        self.cause = cause
        self.message = self.error_messages[cause].format(*args)


run_command = partial(subprocess.check_output, stderr=subprocess.STDOUT, universal_newlines=True)


def check_valgrind():
    """
    Check the output of the valgrind tool for memory leaks and other problems
    present in the submitted solution

    :return: True if the solution did not raise any error during testing
    """
    valgrind_output = run_command(VALGRIND)
    if valgrind_output.find(' 0 errors') != -1:
        return True
    if valgrind_output.find("All heap blocks were freed") == -1:
        raise SolutionCheckError(SolutionCheckTypes.MEMORY_LEAK)
    else:
        raise SolutionCheckError(SolutionCheckTypes.INVALID_READ_WRITE)


def check_imports():
    """
    Check the output of the objdump tool for dangerous functions present in the
    submitted solution

    :return: True if the solution did not contain any of the disabled functions
    """
    objdump_output = run_command(OBJDUMP)
    objdump_dynamic_output = run_command(OBJDUMP_DYNAMIC) if LINKED_DYNAMICALLY else ''
    for func in DISABLED_FUNCTIONS:
        if objdump_output.find(func) != -1 or objdump_dynamic_output.find(func) != -1:
            raise SolutionCheckError(SolutionCheckTypes.DISABLED_FUNCTION, func)
    return True


def check_gtest():
    """
    Check the output of the unit tests linked to the submitted solution

    :return: True, if all unit tests passed
    """
    output = run_command(['sudo', '-u', 'user', TEST_EXECUTABLE])
    if output.find("FAILED") != -1 and output.find("PASSED") == -1:
        raise SolutionCheckError(SolutionCheckTypes.FAILED_UNIT_TEST, output)
    return True, output


class SolutionCheckHandler(socketserver.BaseRequestHandler):
    def handle(self):
        """
        Serve an incoming request with the result of compiling and testing the
        submitted solution
        """
        try:
            run_command(COMPILE_OBJECT)
            run_command(COMPILE_EXECUTABLE)
            run_command(COMPILE_TEST_EXECUTABLE)

            imports = check_imports()
            valgrind = check_valgrind()
            gtest, output = check_gtest()

            success_exit_code = 0 if all((imports, valgrind, gtest)) else 1
            self._send_data(success_exit_code, output)
        except SolutionCheckError as sce:
            self._send_data(sce.cause, sce.message)
        except subprocess.CalledProcessError as cpe:
            self._send_data(cpe.returncode, str(cpe.output))

    def setup(self):
        """
        Set up the environment to properly serve an incoming request
        """
        with suppress(FileNotFoundError):
            os.remove(OBJECT)
            os.remove(EXECUTABLE)
            os.remove(TEST_EXECUTABLE)
        run_command(['chmod', '-R', 'o+x', '/solvable/tests'])

    def finish(self):
        """
        Reset the environment after serving an incoming request
        """
        run_command(['chmod', '-R', 'o-x', '/solvable/tests'])

    def _send_data(self, exit_code, data):
        message = {
            'success': exit_code == 0,
            'output': str(data) if data else ''
        }

        pickled_message = pickle.dumps(message)
        self.request.sendall(pickled_message)

if __name__ == '__main__':
    os.chdir('/solvable')

    # Bind to the exposed HTTP port to allow the controller container to connect to
    SERVER_ADDRESS = ('0.0.0.0', 7777)

    server = socketserver.TCPServer(SERVER_ADDRESS, SolutionCheckHandler)

    try:
        server.serve_forever()
    except Exception as e:
        server.server_close()
        print(e)
        sys.exit(1)
