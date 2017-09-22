# Monero-churn

If you are not familiar with Monero start here: [https://getmonero.org/](https://getmonero.org/)

In Monero, 'churning' is the process of sending a wallet's entire balance back to itself. Since Monero transactions
are private, this process has the benefit of increasing user privacy.
Read more about [what is churning?](https://monero.stackexchange.com/questions/4565/what-is-churning)

The `churn.py` script automatically churns your funds multiple times in a selected time interval.  

## Start a wallet RPC server
To use the script you must have a wallet rpc server running. If you're running monero daemon on 
your local machine, you can start a wallet rpc server by running:
```
monero-wallet-rpc --disable-rpc-login --wallet-file <your_wallet_name> --rpc-bind-port 18082 
```
If you connect to a remote node you should add `--daemon-address <host>:<port>`

You can also run the server with authentication enabled by omitting the `--disable-rpc-login` flag, and providing
username+password as arguments to the script.

## Start churning

After you have rpc server running (assuming on localhost:18082) you can start churning with the default 
parameters by running:
```
python3 churn.py
```

You can choose the churn parameters according to your paranoia level. You should read
the help of the `churn.py` script to see the different parameters:
```
python3 churn.py --help
```

Logs are written to a file `churn.log` in the current directory.

## Tip Jar
Donations are greatly appreciated.  
Monero address: `4D4HpbmA9VJPjJHutYjZtsb7zBhJQc4CodAd5ujsxxVPjHtQ8ELKTgwJig64wEzFry9NWnm47t4jcWMH4cM2FjLZNjmtcvVAUxj67Ud5Z8`
