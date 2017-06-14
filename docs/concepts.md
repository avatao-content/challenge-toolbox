# Concepts

## Challenge

A challenge refers to an exercise to be solved by users. There are different types of challenges supported by the platform. A challenge can be solved by dissecting files, completing programming exercises or there can be even more exotic ones such as network traffic analysis. The type of a challenge depends on the related resources. Such resources may include files or access to a virtual environment based on docker containers.  

## Containers

There can be two types of challenge containers defined:

- **solvable**: the challenge to be solved by the user (_solvable_ from here on)  
- **controller**: the controller checks the submitted user solution and tests if the challenge can be solved and works fine (_controller_ from here on). The controller inherits the volumes of the solvable and shares a network namespace with the solvable. Thus, they can communicate with eachother via localhost. Beware that the root user in the solvable may monitor or alter the network traffic of the controller in that case. 

We use two distinct containers to guarantee PID and IPC namespace isolation between the solvable challenge and the controller.

## Challenge types

Refers to the type of challenge which can be one of the following: _ssh, tcp, web, static_.  

- **ssh** challenges allow users to connect to the solvable container via SSH.
- **tcp** challenges allow users to connect to the solvable container exposed to a random TCP port using known clients such as `telnet` or `nc`.  
- **web** challenges can be accessed by users via their web browser on TCP port 80\. This type includes, for example, programming or web hacking challenges. Programming challenges can be solved in a built-in web IDE.  
- **static** challenges do not use docker containers, consist of files (e.g., binaries to reverse). The user can download all the related files to solve the challenge.  

