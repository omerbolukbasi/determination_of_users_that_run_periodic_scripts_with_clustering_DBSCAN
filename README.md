## DETERMINATION OF USERS THAT RUN PERIODIC SCRIPTS WITH CLUSTERING METHOD DBCSAN<br>

### Problem Definition<br>
In a network the transactions of users(employees) are kept in Transaction Logs of the nodes. All commands that are executed by the users are recorded in these logs. Normally it is forbidden for a user to run a script(periodic command entries) with his/her public user. All scripts must be run with service users.The goal in this case is to find the users that run scripts(periodic command entries) by analysing the transaction logs.<br>

### Clustering Solution With DBSCAN<br>
> Time difference between the consecutive command entries of each users is to be extracted.
> This program can be used to determine the users that run periodic scripts from the transaction log of nodes.
