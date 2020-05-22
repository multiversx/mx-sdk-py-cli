#Transaction dispatcher

##Commands

```
# erdpy dispatcher enqueue-transaction will put a transaction in a queue without send sender address and sign it
erdpy dispatcher enqueue-transaction --value="100" --receiver="bech32Addr" --data="blablabla" --gas-price=int(optional) --gas-limit=int(optional)
```
```
# erdpy dispatcher dispatch-transactions will prepare (sign, sync nonce and set sender address) and send all transactions that are in queue
erdpy dispatcher dispatch-transactions --proxy="https://api.elrond.com" -pem="./examples/keys/alice.pem"
```
```
# erdpy dispatcher dispatch-transactions-continuously will prepare (sign, sync nonce and set sender address) and send all transactions that are in queue at a specified time interval
erdpy dispatcher dispatch-transactions-continuously --proxy="https://api.elrond.com" -pem="./examples/keys/alice.pem" --interval=int(dispatch interval in seconds)
```
```
erdpy dispatcher clean  will remove all transactions that are stored in queue
erdpy dispatcher clean 
```

TODO
- implement a micro-DB (right now transactions are saved in a json file and the writing operation in this are not atomic)
- implement a mechanism to check which transactions was executed successfully (we need to use api route `transaction/:hash` and `transaction/:hash/status` )
- implement a mechanism to close _dispatch-transactions-continuously_ command
