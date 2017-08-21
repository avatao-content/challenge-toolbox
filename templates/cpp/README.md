Avatao C++ WebIDE challenge template
====================================

This project is prepared to provide an environment for challenges where the user has to write or complete C++ code, which is then checked by the Google Test framework. The provided code is also checked for memory leaks and other programming errors with _valgrind_, and for dangerous functions such as `system()` or `fork()` with _objdump_.

## Usage

You have to prepare a skeleton for the user to work on, and the unit tests which will test the submitted solution, and place them in `solvable/app` and `solvable/tests`, respectively. Then update `main.cpp` in `solvable` to call the same function(s) as the test code does. This is needed by the _objdump_ tests, as they have to use a compiled executable which is properly linked with e.g. glibc, but doesn't link with the test code. You probably also want to place a copy of a complete solution in `controller/usr/share` for testing. Update the filenames in `controller/opt/server.py`, `solvable/server.py` and `solvable/tests/CMakeLists.txt` according to your changes. You can also update the `CMakeLists.txt` and the `Dockerfile`s to satisfy challenge-specific needs, should they arise. Fire up the containers and debug away!

## Tips and tricks

If you want to access the socket of the solvable container directly on the host, you can simply telnet to it:
```bash
telnet <container-ip> 7777
```
The IP of the container can be learned with the following command:
```bash
docker inspect $(docker ps | grep solvable | cut -c1-12) -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}'
```

## Open Source licences

Test cases built with CMake files based on [DownloadProject](https://github.com/Crascit/DownloadProject), which is available under the MIT license.