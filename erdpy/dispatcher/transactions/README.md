# Transaction dispatcher

## Features

### Register (enqueue) a transaction to be sent

```
erdpy dispatcher enqueue --value="100" --receiver="erd1cux02zersde0l7hhklzhywcxk4u9n4py5tdxyx7vrvhnza2r4gmq4vw35r" --data="foo" --gas-price=200000000000 --gas-limit=50000000
```

### Dispatch registered (enqueued) transactions

This operation manages the nonce sequence, signs the transactions and sends them to the blockchain.

```
erdpy dispatcher dispatch --proxy="https://testnet-api.elrond.com" --pem="alice.pem"
```

### Continuously dispatch transactions

Same as above, but in a continuous, neverending process. The dispatch takes place at the specified time interval (in seconds).

```
erdpy dispatcher dispatch-continuously --proxy="https://testnet-api.elrond.com" -pem="./examples/keys/alice.pem" --interval=30
```

### Unregister (clear) all enqueued transactions

```
erdpy dispatcher clean 
```

## Roadmap

- Use a database as the queue backend
- Implement a mechanism to check which transactions were executed successfully (we need to use API route `transaction/:hash` and `transaction/:hash/status` )
