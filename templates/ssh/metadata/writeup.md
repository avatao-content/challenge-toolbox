Analyzing Logs - Part 1
=======================

## Where do I begin?

Cost: 10%

First you need to locate the logs - it shouldn't be too hard. Everything with **.log** extension is a log file.
Usually they're stored in the ```/var/log``` directory.

## How to find SQL Injection clues?

Cost: 40%

Look at the files and directories in ```/var/log``` directory. There it is - nginx!  
It contains two files: ```access.log``` and ```error.log```. Open ```access.log``` and you should find a lot of lines containing SQL keywords.

## But where is the username?

Cost: 40%

Analyze the attack, especially the last three requests! The attacker tried to guess the column name with ```doctor``` username.
You can open the database (```/db/database.sqlite3```) to see if the attack was successful (spoiler: **it was!**). 
And since every line begins with an **IP**...

## Complete solution

First you need to locate the logs - it shouldn't be too hard. Everything with **.log** extension is a log file.
Usually they're stored in the ```/var/log``` directory.  
Look at the files and directories here. There it is - nginx!  
It contains two files: ```access.log``` and ```error.log```. Open ```access.log``` and you should find a lot of lines containing SQL keywords.  
Analyze the attack, especially the last three requests! The attacker tried to guess the column name with "doctor" username.
You can open the database (```/db/database.sqlite3```) to see if the attack was successful (spoiler: **it was!**). 
And since every line begins with an **IP**, our first solution is: 

```
doctor@177.143.65.198
```
