## DETERMINATION OF USERS THAT RUN PERIODIC SCRIPTS WITH CLUSTERING METHOD: DBCSAN<br>

### Problem Definition<br>
In a network, the transactions of users(employees) are kept in Transaction Logs of the nodes. All commands that are executed by the users are recorded in these logs. Normally it is forbidden for a user to run a script(periodic command entries) with his/her public user. All scripts must be run with service users. The goal in this case is to find the users that run scripts(periodic command entries) by analysing the transaction logs.<br>

### Clustering Solution With DBSCAN<br>
* Time difference between the consecutive command entries of each users is to be extracted.
* If a user is running a script then the time delta between the execution of the commands must be equal or very similar(because the commands run periodically). So the time deltas of consecutive command entries are clustered.
* For clustering purpose, Unsupervised Clustering method DBSCAN is used. Because it does not require the information of number of clusters while fitting.
* If more than %85 of the command entries of a user belongs to a specific cluster, then this user is assumed to be a user that is executing a script.

A sample graph of a user's time delta between its consecutive command executions (detected as a script user by the algorithm):
![image](https://user-images.githubusercontent.com/44832162/147388140-bff09db5-e81e-45a0-ad38-63f7c299fa44.png)

The attached codes can be used with attached toy transaction log data.
