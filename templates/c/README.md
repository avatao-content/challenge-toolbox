Avatao C WebIDE challenge template
==================================

This project is prepared to provide an environment for challenges where the user has to write or complete C code, which is then checked by the CMocka framework. The provided code is also checked for memory leaks and other programming errors with _valgrind_, and for dangerous functions such as `system()` or `fork()` with _objdump_.

## Usage

You have to prepare a skeleton for the user to work on, and the unit tests which will test the submitted solution, and place them in `solvable/src` and `solvable/test`, respectively. You probably also want to place a copy of a complete solution in `controller/usr/share` for testing. Update the filenames in `controller/opt/server.py`, `solvable/server.py` and `solvable/CMakeLists.txt` according to your changes. You can also update any of the `CMakeLists.txt`s and the `Dockerfile`s to satisfy challenge-specific needs, should they arise. Fire up the containers and debug away!

## Tips and tricks

If you want to access the socket of the solvable container directly on the host, you can simply telnet to it:
```bash
telnet <container-ip> 7777
```
The IP of the container can be learned with the following command:
```bash
docker inspect $(docker ps | grep solvable | cut -c1-12) -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}'
```