# Challenge directory structure

There are descriptor files for a challenge, you can see the right structure format below:  


(D) = for Docker challenges only  
[ ] = optional / if it is really needed  

    repository_name ------------------------ (DIR)
        controller (D) --------------------- (DIR)
        solvable (D) ----------------------- (DIR)
        src -------------------------------- (DIR)
        [downloads] ------------------------ (DIR)      
        config.yml ------------------------- (FILE)
            version ------------------------ (ITEM)
            name --------------------------- (ITEM)
            difficulty --------------------- (ITEM)
            [flag] ------------------------- (ITEM)
            enable_flag_input -------------- (ITEM)
            ports (D) ---------------------- (ITEM)                 
            [capabilities] (D) ------------- (ITEM)
            skills ------------------------- (ITEM)
            recommendations ---------------- (ITEM)
            owner -------------------------- (ITEM)                 
        [CHANGELOG] ------------------------ (FILE)
        [README.md] ------------------------ (FILE)
        metadata --------------------------- (DIR)
            description.md ----------------- (FILE)
            summary.md --------------------- (FILE)
            writeup.md --------------------- (FILE)

## Structure details
In this section we detail the directory structure of challenges. Under the [skeleton](https://github.com/avatao/challenge-engine/tree/master/skeleton) directory in this repository you can find example content for all the items below. Also, we have prepared various challenge templates for different challenge types (e.g., [c](https://github.com/avatao/challenge-engine/tree/master/templates/c), [c#](https://github.com/avatao/challenge-engine/tree/master/templates/csharp), [static](https://github.com/avatao/challenge-engine/tree/master/templates/file), [java](https://github.com/avatao/challenge-engine/tree/master/templates/java), [ssh](https://github.com/avatao/challenge-engine/tree/master/templates/ssh), [telnet](https://github.com/avatao/challenge-engine/tree/master/templates/telnet), [xss](https://github.com/avatao/challenge-engine/tree/master/templates/xss)) that you can fork and customize according to your needs. So the structure is the following:

- **controller** [docker]: The directory for controller should always exist for docker-based challenges. Place here the scripts to check submitted user solution if the flag is not static (e.g., dynamically generated upon container start). The files in this directory _won't_ be accessible for users.
- **solvable** [docker]: The directory for solvable exists for most of the docker-based challenges. Place here all your challenges files (e.g., flag.txt, your server, database files).
- **downloads** [optional]: Optionally, if you want to share challenge files (e.g., crackme, some components, source code) with users please place them here. These can be also relative symlinks which point to another file (e.g., a file in the _solvable_ directory) in the challenge repository. *IMPORTANT* This directory is mandatory for static challenges. 
- **src**: Place all the other source codes and source files of a challenge into this directory. No matter if you have already placed some of these files under the `solvable` or `downloads` directory, please also put them here to have everything in one place.
- **config.yml**: A well-formatted YAML file which contains all the _long_run_ configuration parameters of the challenge. These parameters are the following:
    - **version**: Version number of the config file.  Currently it is `v1`.
    - **capabilities** \[docker]: Place here the list of required linux/docker capabilities. Have only the minimal capability (CAP drop all by default), and add only those you really need. [Read more.](https://docs.docker.com/engine/reference/run/#runtime-privilege-and-linux-capabilities)
    - **difficulty**: Guessed difficulty of a challenge should range from 10 to 500.  
    - **flag** [optional]: If a docker challenge has static flag or the challenge itself is static then insert your flag here. In that case we won't need to start up a distinct container for solution checking. **IMPORTANT**: _However, you have to still create controller for docker-based challenges with the `test` function implemented. This way, we make sure that your challenge is working properly and can be solved._ 
    - **name**: Name of the challenge limited to **200** characters.  
    - **enable_flag_input**: Solution submission can happen in two ways. The first option is that the user submits a text (flag) in an input field on the platform. In this case please set it *true* to tell the platform to create an input field for the solution submission. The second option is when the solution checking works by checking the state changes (e.g., files created, configuration modified) inside the container the user is working on. For example, when the user solves a programming challenge and the controller executes multiple unit tests to accept their code. In that case please set it *false* as their source code is the solution.
    - **ports** [docker]: Please insert internal ports and corresponding protocols here that your solvable container exposes. The corresponding external ports will be generated automatically by our platform. For example:      
        ```
        ports:
            8080: {http: embedded}
            8081: {http: raw}
            8888: {tcp: embedded}
            8889: {tcp: raw}
            2222: {ssh: raw}  
        ```
        As the example shows, we store this information in key-value pairs as follows: `<port>: {ssh|tcp|http: embedded|raw}`. Port and protocols are straightforward. The `embedded` keyword tells the platform to use the embedded web client (e.g., terminal, IDE) and connect to challenge directly. Otherwise, the frontend only exposes the connection information (e.g., web link, SSH port and password) and users have to connect manually. Note that currently only the latter is supported.
 
    - **skills**: Skill tags related to this challenge. Available skill tags are listed on our [API](https://platform.avatao.com/api-explorer/#/api/core/skills/). If you cannot find a proper skill, please [contact us](content@avatao.com).  
    - **recommendations**: Contains external links to resources related to a challenge. Each line of this parameter consists of two parts. The first part is the corresponding URL to the resource, while the second part is the name of the recommended resource.
    - **owner**: Who owns the Intellectual Property. Somebody originally created a challenge and you fork it. In that case, we should mention the original creator, too beside the license information. In case of MITRE cyberacademy challenges, for example, the IP belongs to MITRE, however, we do not have a MITRE community to link the challenge to. Note that it is also possible that the owner equals to the content creator
  
- **README.md** [optional]: Any additional information that you would like to tell about the challenge. If the original challenge is licensed this should be the extended README.md of that challenge.
- **CHANGELOG** [optional]: If you modified an existing licensed challenge, please summarize what your changes were.
 - **metadata**: A directory for challenge description, summary and writeup in markdown format. You can use the online markdown editor [dillinger.io](http://dillinger.io) to format your text properly.
    - **description.md**: Challenge description in markdown format limited to **30000** characters. It is important to use maximally H4 section names (####) so as to fit into the current frontend style. In the `skel` directory you can find an [example](https://github.com/avatao/challenge-engine/blob/master/skeleton/metadata/description.md). 
    - **summary.md**: Short, Twitter-style description of the challenge limited to **200** characters. This is used for teasers and previews.  
    - **writeup.md**: It describes how to solve the challenge. Detailed information can be read under the **Writeup guide** section of this guide. A nice writeup example can be found [here](https://github.com/avatao/challenge-engine/blob/master/skeleton/metadata/writeup.md).   

