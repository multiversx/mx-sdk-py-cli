# Command Line Interface

## Overview

**erdpy** exposes a number of CLI **commands**, organized within **groups**.


```
$ erdpy --help
usage: erdpy [-h] [-v] [--verbose] COMMAND-GROUP [-h] COMMAND ...

-----------
DESCRIPTION
-----------
erdpy is part of the elrond-sdk and consists of Command Line Tools and Python SDK
for interacting with the Blockchain (in general) and with Smart Contracts (in particular).

erdpy targets a broad audience of users and developers.
https://docs.elrond.com/tools/erdpy.
        

COMMAND GROUPS:
  {contract,tx,validator,account,ledger,wallet,network,cost,dispatcher,blockatlas,deps,config,hyperblock,testnet,data,staking-provider,dns}

TOP-LEVEL OPTIONS:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  --verbose

----------------------
COMMAND GROUPS summary
----------------------
contract                       Build, deploy and interact with Smart Contracts
tx                             Create and broadcast Transactions
validator                      Stake, UnStake, UnBond, Unjail and other actions useful for Validators
account                        Get Account data (nonce, balance) from the Network
ledger                         Get Ledger App addresses and version
wallet                         Create wallet, derive secret key from mnemonic, bech32 address helpers etc.
network                        Get Network parameters, such as number of shards, chain identifier etc.
cost                           Estimate cost of Transactions
dispatcher                     Enqueue transactions, then bulk dispatch them
blockatlas                     Interact with an Block Atlas instance
deps                           Manage dependencies or elrond-sdk modules
config                         Configure elrond-sdk (default values etc.)
hyperblock                     Get Hyperblock from the Network
testnet                        Set up, start and control local testnets
data                           Data manipulation omnitool
staking-provider               Staking provider omnitool
dns                            Operations related to the Domain Name Service

```
## Group **Contract**


```
$ erdpy contract --help
usage: erdpy contract COMMAND [-h] ...

Build, deploy and interact with Smart Contracts

COMMANDS:
  {new,templates,build,clean,test,deploy,call,upgrade,query}

OPTIONS:
  -h, --help            show this help message and exit

----------------
COMMANDS summary
----------------
new                            Create a new Smart Contract project based on a template.
templates                      List the available Smart Contract templates.
build                          Build a Smart Contract project using the appropriate buildchain.
clean                          Clean a Smart Contract project.
test                           Run Mandos tests.
deploy                         Deploy a Smart Contract.
call                           Interact with a Smart Contract (execute function).
upgrade                        Upgrade a previously-deployed Smart Contract
query                          Query a Smart Contract (call a pure function)

```
### Contract.New


```
$ erdpy contract new --help
usage: erdpy contract new [-h] ...

Create a new Smart Contract project based on a template.

positional arguments:
  name

optional arguments:
  -h, --help             show this help message and exit
  --template TEMPLATE    the template to use
  --directory DIRECTORY  🗀 the parent directory of the project (default: current directory)

```
### Contract.Templates


```
$ erdpy contract templates --help
usage: erdpy contract templates [-h] ...

List the available Smart Contract templates.

optional arguments:
  -h, --help  show this help message and exit

```
### Contract.Build


```
$ erdpy contract build --help
usage: erdpy contract build [-h] ...

Build a Smart Contract project using the appropriate buildchain.

positional arguments:
  project                              🗀 the project directory (default: current directory)

optional arguments:
  -h, --help                           show this help message and exit
  --debug                              set debug flag (default: False)
  --no-optimization                    bypass optimizations (for clang) (default: False)
  --cargo-target-dir CARGO_TARGET_DIR  for rust projects, forward the parameter to Cargo
  --wasm-symbols                       for rust projects, does not strip the symbols from the wasm output. Useful for
                                       analysing the bytecode. Creates larger wasm files. Avoid in production (default:
                                       False)
  --wasm-name WASM_NAME                for rust projects, optionally specify the name of the wasm bytecode output file

```
### Contract.Clean


```
$ erdpy contract clean --help
usage: erdpy contract clean [-h] ...

Clean a Smart Contract project.

positional arguments:
  project     🗀 the project directory (default: current directory)

optional arguments:
  -h, --help  show this help message and exit

```
### Contract.Deploy


```
$ erdpy contract deploy --help
usage: erdpy contract deploy [-h] ...

Deploy a Smart Contract.

optional arguments:
  -h, --help                                   show this help message and exit
  --project PROJECT                            🗀 the project directory (default: current directory)
  --bytecode BYTECODE                          the file containing the WASM bytecode
  --metadata-not-upgradeable                   ‼ mark the contract as NOT upgradeable (default: upgradeable)
  --metadata-payable                           ‼ mark the contract as payable (default: not payable)
  --outfile OUTFILE                            where to save the output (default: stdout)
  --pem PEM                                    🔑 the PEM file, if keyfile not provided
  --pem-index PEM_INDEX                        🔑 the index in the PEM file (default: 0)
  --keyfile KEYFILE                            🔑 a JSON keyfile, if PEM not provided
  --passfile PASSFILE                          🔑 a file containing keyfile's password, if keyfile provided
  --ledger                                     🔐 bool flag for signing transaction using ledger
  --ledger-account-index LEDGER_ACCOUNT_INDEX  🔐 the index of the account when using Ledger
  --ledger-address-index LEDGER_ADDRESS_INDEX  🔐 the index of the address when using Ledger
  --sender-username SENDER_USERNAME            🖄 the username of the sender
  --proxy PROXY                                🔗 the URL of the proxy (default: https://testnet-api.elrond.com)
  --nonce NONCE                                # the nonce for the transaction
  --recall-nonce                               ⭮ whether to recall the nonce when creating the transaction (default:
                                               False)
  --gas-price GAS_PRICE                        ⛽ the gas price (default: 1000000000)
  --gas-limit GAS_LIMIT                        ⛽ the gas limit
  --value VALUE                                the value to transfer (default: 0)
  --chain CHAIN                                the chain identifier (default: T)
  --version VERSION                            the transaction version (default: 1)
  --options OPTIONS                            the transaction options (default: 0)
  --arguments ARGUMENTS [ARGUMENTS ...]        arguments for the contract transaction, as numbers or hex-encoded. E.g.
                                               --arguments 42 0x64 1000 0xabba
  --wait-result                                signal to wait for the transaction result - only valid if --send is set
  --timeout TIMEOUT                            max num of seconds to wait for result - only valid if --wait-result is
                                               set
  --send                                       ✓ whether to broadcast the transaction (default: False)
  --simulate                                   whether to simulate the transaction (default: False)

```
### Contract.Call


```
$ erdpy contract call --help
usage: erdpy contract call [-h] ...

Interact with a Smart Contract (execute function).

positional arguments:
  contract                                     🖄 the address of the Smart Contract

optional arguments:
  -h, --help                                   show this help message and exit
  --outfile OUTFILE                            where to save the output (default: stdout)
  --pem PEM                                    🔑 the PEM file, if keyfile not provided
  --pem-index PEM_INDEX                        🔑 the index in the PEM file (default: 0)
  --keyfile KEYFILE                            🔑 a JSON keyfile, if PEM not provided
  --passfile PASSFILE                          🔑 a file containing keyfile's password, if keyfile provided
  --ledger                                     🔐 bool flag for signing transaction using ledger
  --ledger-account-index LEDGER_ACCOUNT_INDEX  🔐 the index of the account when using Ledger
  --ledger-address-index LEDGER_ADDRESS_INDEX  🔐 the index of the address when using Ledger
  --sender-username SENDER_USERNAME            🖄 the username of the sender
  --proxy PROXY                                🔗 the URL of the proxy (default: https://testnet-api.elrond.com)
  --nonce NONCE                                # the nonce for the transaction
  --recall-nonce                               ⭮ whether to recall the nonce when creating the transaction (default:
                                               False)
  --gas-price GAS_PRICE                        ⛽ the gas price (default: 1000000000)
  --gas-limit GAS_LIMIT                        ⛽ the gas limit
  --value VALUE                                the value to transfer (default: 0)
  --chain CHAIN                                the chain identifier (default: T)
  --version VERSION                            the transaction version (default: 1)
  --options OPTIONS                            the transaction options (default: 0)
  --function FUNCTION                          the function to call
  --arguments ARGUMENTS [ARGUMENTS ...]        arguments for the contract transaction, as numbers or hex-encoded. E.g.
                                               --arguments 42 0x64 1000 0xabba
  --wait-result                                signal to wait for the transaction result - only valid if --send is set
  --timeout TIMEOUT                            max num of seconds to wait for result - only valid if --wait-result is
                                               set
  --send                                       ✓ whether to broadcast the transaction (default: False)
  --simulate                                   whether to simulate the transaction (default: False)
  --relay                                      whether to relay the transaction (default: False)

```
### Contract.Upgrade


```
$ erdpy contract upgrade --help
usage: erdpy contract upgrade [-h] ...

Upgrade a previously-deployed Smart Contract

positional arguments:
  contract                                     🖄 the address of the Smart Contract

optional arguments:
  -h, --help                                   show this help message and exit
  --outfile OUTFILE                            where to save the output (default: stdout)
  --project PROJECT                            🗀 the project directory (default: current directory)
  --bytecode BYTECODE                          the file containing the WASM bytecode
  --metadata-not-upgradeable                   ‼ mark the contract as NOT upgradeable (default: upgradeable)
  --metadata-payable                           ‼ mark the contract as payable (default: not payable)
  --pem PEM                                    🔑 the PEM file, if keyfile not provided
  --pem-index PEM_INDEX                        🔑 the index in the PEM file (default: 0)
  --keyfile KEYFILE                            🔑 a JSON keyfile, if PEM not provided
  --passfile PASSFILE                          🔑 a file containing keyfile's password, if keyfile provided
  --ledger                                     🔐 bool flag for signing transaction using ledger
  --ledger-account-index LEDGER_ACCOUNT_INDEX  🔐 the index of the account when using Ledger
  --ledger-address-index LEDGER_ADDRESS_INDEX  🔐 the index of the address when using Ledger
  --sender-username SENDER_USERNAME            🖄 the username of the sender
  --proxy PROXY                                🔗 the URL of the proxy (default: https://testnet-api.elrond.com)
  --nonce NONCE                                # the nonce for the transaction
  --recall-nonce                               ⭮ whether to recall the nonce when creating the transaction (default:
                                               False)
  --gas-price GAS_PRICE                        ⛽ the gas price (default: 1000000000)
  --gas-limit GAS_LIMIT                        ⛽ the gas limit
  --value VALUE                                the value to transfer (default: 0)
  --chain CHAIN                                the chain identifier (default: T)
  --version VERSION                            the transaction version (default: 1)
  --options OPTIONS                            the transaction options (default: 0)
  --arguments ARGUMENTS [ARGUMENTS ...]        arguments for the contract transaction, as numbers or hex-encoded. E.g.
                                               --arguments 42 0x64 1000 0xabba
  --wait-result                                signal to wait for the transaction result - only valid if --send is set
  --timeout TIMEOUT                            max num of seconds to wait for result - only valid if --wait-result is
                                               set
  --send                                       ✓ whether to broadcast the transaction (default: False)
  --simulate                                   whether to simulate the transaction (default: False)

```
### Contract.Query


```
$ erdpy contract query --help
usage: erdpy contract query [-h] ...

Query a Smart Contract (call a pure function)

positional arguments:
  contract                               🖄 the address of the Smart Contract

optional arguments:
  -h, --help                             show this help message and exit
  --proxy PROXY                          🔗 the URL of the proxy (default: https://testnet-api.elrond.com)
  --function FUNCTION                    the function to call
  --arguments ARGUMENTS [ARGUMENTS ...]  arguments for the contract transaction, as numbers or hex-encoded. E.g.
                                         --arguments 42 0x64 1000 0xabba

```
## Group **Transactions**


```
$ erdpy tx --help
usage: erdpy tx COMMAND [-h] ...

Create and broadcast Transactions

COMMANDS:
  {new,send,get}

OPTIONS:
  -h, --help      show this help message and exit

----------------
COMMANDS summary
----------------
new                            Create a new transaction
send                           Send a previously saved transaction
get                            Get a transaction

```
### Transactions.New


```
$ erdpy tx new --help
usage: erdpy tx new [-h] ...

Create a new transaction

optional arguments:
  -h, --help                                   show this help message and exit
  --pem PEM                                    🔑 the PEM file, if keyfile not provided
  --pem-index PEM_INDEX                        🔑 the index in the PEM file (default: 0)
  --keyfile KEYFILE                            🔑 a JSON keyfile, if PEM not provided
  --passfile PASSFILE                          🔑 a file containing keyfile's password, if keyfile provided
  --ledger                                     🔐 bool flag for signing transaction using ledger
  --ledger-account-index LEDGER_ACCOUNT_INDEX  🔐 the index of the account when using Ledger
  --ledger-address-index LEDGER_ADDRESS_INDEX  🔐 the index of the address when using Ledger
  --sender-username SENDER_USERNAME            🖄 the username of the sender
  --nonce NONCE                                # the nonce for the transaction
  --recall-nonce                               ⭮ whether to recall the nonce when creating the transaction (default:
                                               False)
  --receiver RECEIVER                          🖄 the address of the receiver
  --receiver-username RECEIVER_USERNAME        🖄 the username of the receiver
  --gas-price GAS_PRICE                        ⛽ the gas price (default: 1000000000)
  --gas-limit GAS_LIMIT                        ⛽ the gas limit
  --value VALUE                                the value to transfer (default: 0)
  --data DATA                                  the payload, or 'memo' of the transaction (default: )
  --chain CHAIN                                the chain identifier (default: T)
  --version VERSION                            the transaction version (default: 1)
  --options OPTIONS                            the transaction options (default: 0)
  --data-file DATA_FILE                        a file containing transaction data
  --outfile OUTFILE                            where to save the output (signed transaction, hash) (default: stdout)
  --send                                       ✓ whether to broadcast the transaction (default: False)
  --simulate                                   whether to simulate the transaction (default: False)
  --relay                                      whether to relay the transaction (default: False)
  --proxy PROXY                                🔗 the URL of the proxy (default: https://testnet-api.elrond.com)
  --wait-result                                signal to wait for the transaction result - only valid if --send is set
  --timeout TIMEOUT                            max num of seconds to wait for result - only valid if --wait-result is
                                               set

```
### Transactions.Send


```
$ erdpy tx send --help
usage: erdpy tx send [-h] ...

Send a previously saved transaction

optional arguments:
  -h, --help         show this help message and exit
  --infile INFILE    input file (a previously saved transaction)
  --outfile OUTFILE  where to save the output (the hash) (default: stdout)
  --proxy PROXY      🔗 the URL of the proxy (default: https://testnet-api.elrond.com)

```
### Transactions.Get


```
$ erdpy tx get --help
usage: erdpy tx get [-h] ...

Get a transaction

optional arguments:
  -h, --help                 show this help message and exit
  --hash HASH                the hash
  --sender SENDER            the sender address
  --with-results             will also return the results of transaction
  --proxy PROXY              🔗 the URL of the proxy (default: https://testnet-api.elrond.com)
  --omit-fields OMIT_FIELDS  omit fields in the output payload (default: [])

```
## Group **Hyperblocks**


```
$ erdpy hyperblock --help
usage: erdpy hyperblock COMMAND [-h] ...

Get Hyperblock from the Network

COMMANDS:
  {get}

OPTIONS:
  -h, --help  show this help message and exit

```
### Hyperblock.Get


```
$ erdpy hyperblock get --help
usage: erdpy hyperblock get [-h] ...

Get hyperblock

optional arguments:
  -h, --help     show this help message and exit
  --proxy PROXY  🔗 the URL of the proxy (default: https://testnet-api.elrond.com)
  --key KEY      the hash or the nonce of the hyperblock

```
## Group **Validator**


```
$ erdpy validator --help
usage: erdpy validator COMMAND [-h] ...

Stake, UnStake, UnBond, Unjail and other actions useful for Validators

COMMANDS:
  {stake,unstake,unjail,unbond,change-reward-address,claim,unstake-nodes,unstake-tokens,unbond-nodes,unbond-tokens,clean-registered-data,restake-unstaked-nodes}

OPTIONS:
  -h, --help            show this help message and exit

----------------
COMMANDS summary
----------------
stake                          Stake value into the Network
unstake                        Unstake value
unjail                         Unjail a Validator Node
unbond                         Unbond tokens for a bls key
change-reward-address          Change the reward address
claim                          Claim rewards
unstake-nodes                  Unstake-nodes will unstake nodes for provided bls keys
unstake-tokens                 This command will un-stake the given amount (if value is greater than the existing topUp value, it will unStake one or several nodes)
unbond-nodes                   It will unBond nodes
unbond-tokens                  It will unBond tokens, if provided value is bigger that topUp value will unBond nodes
clean-registered-data          Deletes duplicated keys from registered data
restake-unstaked-nodes         It will reStake UnStaked nodes

```
### Validator.Stake


```
$ erdpy validator stake --help
usage: erdpy validator stake [-h] ...

Stake value into the Network

optional arguments:
  -h, --help                                   show this help message and exit
  --proxy PROXY                                🔗 the URL of the proxy (default: https://testnet-api.elrond.com)
  --pem PEM                                    🔑 the PEM file, if keyfile not provided
  --pem-index PEM_INDEX                        🔑 the index in the PEM file (default: 0)
  --keyfile KEYFILE                            🔑 a JSON keyfile, if PEM not provided
  --passfile PASSFILE                          🔑 a file containing keyfile's password, if keyfile provided
  --ledger                                     🔐 bool flag for signing transaction using ledger
  --ledger-account-index LEDGER_ACCOUNT_INDEX  🔐 the index of the account when using Ledger
  --ledger-address-index LEDGER_ADDRESS_INDEX  🔐 the index of the address when using Ledger
  --sender-username SENDER_USERNAME            🖄 the username of the sender
  --nonce NONCE                                # the nonce for the transaction
  --recall-nonce                               ⭮ whether to recall the nonce when creating the transaction (default:
                                               False)
  --gas-price GAS_PRICE                        ⛽ the gas price (default: 1000000000)
  --gas-limit GAS_LIMIT                        ⛽ the gas limit
  --estimate-gas                               ⛽ whether to estimate the gas limit (default: 0)
  --value VALUE                                the value to transfer (default: 0)
  --chain CHAIN                                the chain identifier (default: T)
  --version VERSION                            the transaction version (default: 1)
  --options OPTIONS                            the transaction options (default: 0)
  --send                                       ✓ whether to broadcast the transaction (default: False)
  --simulate                                   whether to simulate the transaction (default: False)
  --outfile OUTFILE                            where to save the output (signed transaction, hash) (default: stdout)
  --reward-address REWARD_ADDRESS              the reward address
  --validators-file VALIDATORS_FILE            a JSON file describing the Nodes
  --top-up                                     Stake value for top up

```
### Validator.Unstake


```
$ erdpy validator unstake --help
usage: erdpy validator unstake [-h] ...

Unstake value

optional arguments:
  -h, --help                                   show this help message and exit
  --proxy PROXY                                🔗 the URL of the proxy (default: https://testnet-api.elrond.com)
  --pem PEM                                    🔑 the PEM file, if keyfile not provided
  --pem-index PEM_INDEX                        🔑 the index in the PEM file (default: 0)
  --keyfile KEYFILE                            🔑 a JSON keyfile, if PEM not provided
  --passfile PASSFILE                          🔑 a file containing keyfile's password, if keyfile provided
  --ledger                                     🔐 bool flag for signing transaction using ledger
  --ledger-account-index LEDGER_ACCOUNT_INDEX  🔐 the index of the account when using Ledger
  --ledger-address-index LEDGER_ADDRESS_INDEX  🔐 the index of the address when using Ledger
  --sender-username SENDER_USERNAME            🖄 the username of the sender
  --nonce NONCE                                # the nonce for the transaction
  --recall-nonce                               ⭮ whether to recall the nonce when creating the transaction (default:
                                               False)
  --gas-price GAS_PRICE                        ⛽ the gas price (default: 1000000000)
  --gas-limit GAS_LIMIT                        ⛽ the gas limit
  --estimate-gas                               ⛽ whether to estimate the gas limit (default: 0)
  --value VALUE                                the value to transfer (default: 0)
  --chain CHAIN                                the chain identifier (default: T)
  --version VERSION                            the transaction version (default: 1)
  --options OPTIONS                            the transaction options (default: 0)
  --send                                       ✓ whether to broadcast the transaction (default: False)
  --simulate                                   whether to simulate the transaction (default: False)
  --outfile OUTFILE                            where to save the output (signed transaction, hash) (default: stdout)
  --nodes-public-keys NODES_PUBLIC_KEYS        the public keys of the nodes as CSV (addrA,addrB)

```
### Validator.Unjail


```
$ erdpy validator unjail --help
usage: erdpy validator unjail [-h] ...

Unjail a Validator Node

optional arguments:
  -h, --help                                   show this help message and exit
  --proxy PROXY                                🔗 the URL of the proxy (default: https://testnet-api.elrond.com)
  --pem PEM                                    🔑 the PEM file, if keyfile not provided
  --pem-index PEM_INDEX                        🔑 the index in the PEM file (default: 0)
  --keyfile KEYFILE                            🔑 a JSON keyfile, if PEM not provided
  --passfile PASSFILE                          🔑 a file containing keyfile's password, if keyfile provided
  --ledger                                     🔐 bool flag for signing transaction using ledger
  --ledger-account-index LEDGER_ACCOUNT_INDEX  🔐 the index of the account when using Ledger
  --ledger-address-index LEDGER_ADDRESS_INDEX  🔐 the index of the address when using Ledger
  --sender-username SENDER_USERNAME            🖄 the username of the sender
  --nonce NONCE                                # the nonce for the transaction
  --recall-nonce                               ⭮ whether to recall the nonce when creating the transaction (default:
                                               False)
  --gas-price GAS_PRICE                        ⛽ the gas price (default: 1000000000)
  --gas-limit GAS_LIMIT                        ⛽ the gas limit
  --estimate-gas                               ⛽ whether to estimate the gas limit (default: 0)
  --value VALUE                                the value to transfer (default: 0)
  --chain CHAIN                                the chain identifier (default: T)
  --version VERSION                            the transaction version (default: 1)
  --options OPTIONS                            the transaction options (default: 0)
  --send                                       ✓ whether to broadcast the transaction (default: False)
  --simulate                                   whether to simulate the transaction (default: False)
  --outfile OUTFILE                            where to save the output (signed transaction, hash) (default: stdout)
  --nodes-public-keys NODES_PUBLIC_KEYS        the public keys of the nodes as CSV (addrA,addrB)

```
### Validator.Unbond


```
$ erdpy validator unbond --help
usage: erdpy validator unbond [-h] ...

Unbond tokens for a bls key

optional arguments:
  -h, --help                                   show this help message and exit
  --proxy PROXY                                🔗 the URL of the proxy (default: https://testnet-api.elrond.com)
  --pem PEM                                    🔑 the PEM file, if keyfile not provided
  --pem-index PEM_INDEX                        🔑 the index in the PEM file (default: 0)
  --keyfile KEYFILE                            🔑 a JSON keyfile, if PEM not provided
  --passfile PASSFILE                          🔑 a file containing keyfile's password, if keyfile provided
  --ledger                                     🔐 bool flag for signing transaction using ledger
  --ledger-account-index LEDGER_ACCOUNT_INDEX  🔐 the index of the account when using Ledger
  --ledger-address-index LEDGER_ADDRESS_INDEX  🔐 the index of the address when using Ledger
  --sender-username SENDER_USERNAME            🖄 the username of the sender
  --nonce NONCE                                # the nonce for the transaction
  --recall-nonce                               ⭮ whether to recall the nonce when creating the transaction (default:
                                               False)
  --gas-price GAS_PRICE                        ⛽ the gas price (default: 1000000000)
  --gas-limit GAS_LIMIT                        ⛽ the gas limit
  --estimate-gas                               ⛽ whether to estimate the gas limit (default: 0)
  --value VALUE                                the value to transfer (default: 0)
  --chain CHAIN                                the chain identifier (default: T)
  --version VERSION                            the transaction version (default: 1)
  --options OPTIONS                            the transaction options (default: 0)
  --send                                       ✓ whether to broadcast the transaction (default: False)
  --simulate                                   whether to simulate the transaction (default: False)
  --outfile OUTFILE                            where to save the output (signed transaction, hash) (default: stdout)
  --nodes-public-keys NODES_PUBLIC_KEYS        the public keys of the nodes as CSV (addrA,addrB)

```
### Validator.ChangeRewardAddress


```
$ erdpy validator change-reward-address --help
usage: erdpy validator change-reward-address [-h] ...

Change the reward address

optional arguments:
  -h, --help                                   show this help message and exit
  --proxy PROXY                                🔗 the URL of the proxy (default: https://testnet-api.elrond.com)
  --pem PEM                                    🔑 the PEM file, if keyfile not provided
  --pem-index PEM_INDEX                        🔑 the index in the PEM file (default: 0)
  --keyfile KEYFILE                            🔑 a JSON keyfile, if PEM not provided
  --passfile PASSFILE                          🔑 a file containing keyfile's password, if keyfile provided
  --ledger                                     🔐 bool flag for signing transaction using ledger
  --ledger-account-index LEDGER_ACCOUNT_INDEX  🔐 the index of the account when using Ledger
  --ledger-address-index LEDGER_ADDRESS_INDEX  🔐 the index of the address when using Ledger
  --sender-username SENDER_USERNAME            🖄 the username of the sender
  --nonce NONCE                                # the nonce for the transaction
  --recall-nonce                               ⭮ whether to recall the nonce when creating the transaction (default:
                                               False)
  --gas-price GAS_PRICE                        ⛽ the gas price (default: 1000000000)
  --gas-limit GAS_LIMIT                        ⛽ the gas limit
  --estimate-gas                               ⛽ whether to estimate the gas limit (default: 0)
  --value VALUE                                the value to transfer (default: 0)
  --chain CHAIN                                the chain identifier (default: T)
  --version VERSION                            the transaction version (default: 1)
  --options OPTIONS                            the transaction options (default: 0)
  --send                                       ✓ whether to broadcast the transaction (default: False)
  --simulate                                   whether to simulate the transaction (default: False)
  --outfile OUTFILE                            where to save the output (signed transaction, hash) (default: stdout)
  --reward-address REWARD_ADDRESS              the new reward address

```
### Validator.Claim


```
$ erdpy validator claim --help
usage: erdpy validator claim [-h] ...

Claim rewards

optional arguments:
  -h, --help                                   show this help message and exit
  --proxy PROXY                                🔗 the URL of the proxy (default: https://testnet-api.elrond.com)
  --pem PEM                                    🔑 the PEM file, if keyfile not provided
  --pem-index PEM_INDEX                        🔑 the index in the PEM file (default: 0)
  --keyfile KEYFILE                            🔑 a JSON keyfile, if PEM not provided
  --passfile PASSFILE                          🔑 a file containing keyfile's password, if keyfile provided
  --ledger                                     🔐 bool flag for signing transaction using ledger
  --ledger-account-index LEDGER_ACCOUNT_INDEX  🔐 the index of the account when using Ledger
  --ledger-address-index LEDGER_ADDRESS_INDEX  🔐 the index of the address when using Ledger
  --sender-username SENDER_USERNAME            🖄 the username of the sender
  --nonce NONCE                                # the nonce for the transaction
  --recall-nonce                               ⭮ whether to recall the nonce when creating the transaction (default:
                                               False)
  --gas-price GAS_PRICE                        ⛽ the gas price (default: 1000000000)
  --gas-limit GAS_LIMIT                        ⛽ the gas limit
  --estimate-gas                               ⛽ whether to estimate the gas limit (default: 0)
  --value VALUE                                the value to transfer (default: 0)
  --chain CHAIN                                the chain identifier (default: T)
  --version VERSION                            the transaction version (default: 1)
  --options OPTIONS                            the transaction options (default: 0)
  --send                                       ✓ whether to broadcast the transaction (default: False)
  --simulate                                   whether to simulate the transaction (default: False)
  --outfile OUTFILE                            where to save the output (signed transaction, hash) (default: stdout)

```
## Group **Account**


```
$ erdpy account --help
usage: erdpy account COMMAND [-h] ...

Get Account data (nonce, balance) from the Network

COMMANDS:
  {get,get-transactions}

OPTIONS:
  -h, --help            show this help message and exit

----------------
COMMANDS summary
----------------
get                            Query account details (nonce, balance etc.)
get-transactions               Query account transactions

```
### Account.Get


```
$ erdpy account get --help
usage: erdpy account get [-h] ...

Query account details (nonce, balance etc.)

optional arguments:
  -h, --help                 show this help message and exit
  --proxy PROXY              🔗 the URL of the proxy (default: https://testnet-api.elrond.com)
  --address ADDRESS          🖄 the address to query
  --balance                  whether to only fetch the balance
  --nonce                    whether to only fetch the nonce
  --username                 whether to only fetch the username
  --omit-fields OMIT_FIELDS  omit fields in the output payload (default: [])

```
### Account.GetTransactions


```
$ erdpy account get-transactions --help
usage: erdpy account get-transactions [-h] ...

Query account transactions

optional arguments:
  -h, --help         show this help message and exit
  --proxy PROXY      🔗 the URL of the proxy (default: https://testnet-api.elrond.com)
  --outfile OUTFILE  where to save the output (default: stdout)
  --address ADDRESS  🖄 the address to query

```
## Group **Wallet**


```
$ erdpy wallet --help
usage: erdpy wallet COMMAND [-h] ...

Create wallet, derive secret key from mnemonic, bech32 address helpers etc.

COMMANDS:
  {new,derive,bech32,pem-address,pem-address-hex}

OPTIONS:
  -h, --help            show this help message and exit

----------------
COMMANDS summary
----------------
new                            Create a new wallet and print its mnemonic; optionally save as password-protected JSON (recommended) or PEM (not recommended)
derive                         Derive a PEM file from a mnemonic or generate a new PEM file (for tests only!)
bech32                         Helper for encoding and decoding bech32 addresses
pem-address                    Get the public address out of a PEM file as bech32
pem-address-hex                Get the public address out of a PEM file as hex

```
### Wallet.New


```
$ erdpy wallet new --help
usage: erdpy wallet new [-h] ...

Create a new wallet and print its mnemonic; optionally save as password-protected JSON (recommended) or PEM (not
recommended)

optional arguments:
  -h, --help                 show this help message and exit
  --json                     whether to create a json key file
  --pem                      whether to create a pem key file
  --output-path OUTPUT_PATH  the output path and base file name for the generated wallet files (default: ./wallet)

```
### Wallet.Derive


```
$ erdpy wallet derive --help
usage: erdpy wallet derive [-h] ...

Derive a PEM file from a mnemonic or generate a new PEM file (for tests only!)

positional arguments:
  pem            path of the output PEM file

optional arguments:
  -h, --help     show this help message and exit
  --mnemonic     whether to derive from an existing mnemonic
  --index INDEX  the account index

```
### Wallet.Bech32


```
$ erdpy wallet bech32 --help
usage: erdpy wallet bech32 [-h] ...

Helper for encoding and decoding bech32 addresses

positional arguments:
  value       the value to encode or decode

optional arguments:
  -h, --help  show this help message and exit
  --encode    whether to encode
  --decode    whether to decode

```
## Group **Testnet**


```
$ erdpy testnet --help
usage: erdpy testnet COMMAND [-h] ...

Set up, start and control local testnets

COMMANDS:
  {prerequisites,start,config,clean}

OPTIONS:
  -h, --help            show this help message and exit

```
### Testnet.Prerequisites


```
$ erdpy testnet prerequisites --help
usage: erdpy testnet prerequisites [-h] ...

Download and verify the prerequisites for running a testnet

optional arguments:
  -h, --help               show this help message and exit
  --configfile CONFIGFILE  An optional configuration file describing the testnet

```
### Testnet.Config


```
$ erdpy testnet config --help
usage: erdpy testnet config [-h] ...

Configure a testnet (required before starting it the first time or after clean)

optional arguments:
  -h, --help               show this help message and exit
  --configfile CONFIGFILE  An optional configuration file describing the testnet

```
### Testnet.Start


```
$ erdpy testnet start --help
usage: erdpy testnet start [-h] ...

Start a testnet

optional arguments:
  -h, --help               show this help message and exit
  --configfile CONFIGFILE  An optional configuration file describing the testnet

```
### Testnet.Clean


```
$ erdpy testnet clean --help
usage: erdpy testnet clean [-h] ...

Erase the currently configured testnet (must be already stopped)

optional arguments:
  -h, --help               show this help message and exit
  --configfile CONFIGFILE  An optional configuration file describing the testnet

```
## Group **Network**


```
$ erdpy network --help
usage: erdpy network COMMAND [-h] ...

Get Network parameters, such as number of shards, chain identifier etc.

COMMANDS:
  {num-shards,block-nonce,chain}

OPTIONS:
  -h, --help            show this help message and exit

----------------
COMMANDS summary
----------------
num-shards                     Get the number of shards.
block-nonce                    Get the latest block nonce, by shard.
chain                          Get the chain identifier.

```
### Network.NumShards


```
$ erdpy network num-shards --help
usage: erdpy network num-shards [-h] ...

Get the number of shards.

optional arguments:
  -h, --help     show this help message and exit
  --proxy PROXY  🔗 the URL of the proxy (default: https://testnet-api.elrond.com)

```
### Network.BlockNonce


```
$ erdpy network block-nonce --help
usage: erdpy network block-nonce [-h] ...

Get the latest block nonce, by shard.

optional arguments:
  -h, --help     show this help message and exit
  --proxy PROXY  🔗 the URL of the proxy (default: https://testnet-api.elrond.com)
  --shard SHARD  the shard ID (use 4294967295 for metachain)

```
### Network.Chain


```
$ erdpy network chain --help
usage: erdpy network chain [-h] ...

Get the chain identifier.

optional arguments:
  -h, --help     show this help message and exit
  --proxy PROXY  🔗 the URL of the proxy (default: https://testnet-api.elrond.com)

```
## Group **Cost**


```
$ erdpy cost --help
usage: erdpy cost COMMAND [-h] ...

Estimate cost of Transactions

COMMANDS:
  {gas-price,tx-transfer,sc-deploy,sc-call}

OPTIONS:
  -h, --help            show this help message and exit

----------------
COMMANDS summary
----------------
gas-price                      Query minimum gas price
tx-transfer                    Query cost of regular transaction (transfer)
sc-deploy                      Query cost of Smart Contract deploy transaction
sc-call                        Query cost of Smart Contract call transaction

```
### Cost.GasPrice


```
$ erdpy cost gas-price --help
usage: erdpy cost gas-price [-h] ...

Query minimum gas price

optional arguments:
  -h, --help     show this help message and exit
  --proxy PROXY  🔗 the URL of the proxy (default: https://testnet-api.elrond.com)

```
### Cost.TxTransfer


```
$ erdpy cost tx-transfer --help
usage: erdpy cost tx-transfer [-h] ...

Query cost of regular transaction (transfer)

optional arguments:
  -h, --help     show this help message and exit
  --proxy PROXY  🔗 the URL of the proxy (default: https://testnet-api.elrond.com)
  --data DATA    a transaction payload, required to estimate the cost

```
### Cost.ScDeploy


```
$ erdpy cost sc-deploy --help
usage: erdpy cost sc-deploy [-h] ...

Query cost of Smart Contract deploy transaction

optional arguments:
  -h, --help                             show this help message and exit
  --proxy PROXY                          🔗 the URL of the proxy (default: https://testnet-api.elrond.com)
  --project PROJECT                      🗀 the project directory (default: current directory)
  --bytecode BYTECODE                    the file containing the WASM bytecode
  --arguments ARGUMENTS [ARGUMENTS ...]  arguments for the contract transaction, as numbers or hex-encoded. E.g.
                                         --arguments 42 0x64 1000 0xabba

```
### Cost.ScCall


```
$ erdpy cost sc-call --help
usage: erdpy cost sc-call [-h] ...

Query cost of Smart Contract call transaction

positional arguments:
  contract                               🖄 the address of the Smart Contract

optional arguments:
  -h, --help                             show this help message and exit
  --proxy PROXY                          🔗 the URL of the proxy (default: https://testnet-api.elrond.com)
  --function FUNCTION                    the function to call
  --arguments ARGUMENTS [ARGUMENTS ...]  arguments for the contract transaction, as numbers or hex-encoded. E.g.
                                         --arguments 42 0x64 1000 0xabba

```
## Group **Dispatcher**


```
$ erdpy dispatcher --help
usage: erdpy dispatcher COMMAND [-h] ...

Enqueue transactions, then bulk dispatch them

COMMANDS:
  {enqueue,dispatch,dispatch-continuously,clean}

OPTIONS:
  -h, --help            show this help message and exit

----------------
COMMANDS summary
----------------
enqueue                        Enqueue a transaction
dispatch                       Dispatch queued transactions
dispatch-continuously          Continuously dispatch queued transactions
clean                          Clear queue of transactions

```
### Dispatcher.Enqueue


```
$ erdpy dispatcher enqueue --help
usage: erdpy dispatcher enqueue [-h] ...

Enqueue a transaction

optional arguments:
  -h, --help                             show this help message and exit
  --receiver RECEIVER                    🖄 the address of the receiver
  --receiver-username RECEIVER_USERNAME  🖄 the username of the receiver
  --gas-price GAS_PRICE                  ⛽ the gas price (default: 1000000000)
  --gas-limit GAS_LIMIT                  ⛽ the gas limit
  --value VALUE                          the value to transfer (default: 0)
  --data DATA                            the payload, or 'memo' of the transaction (default: )
  --chain CHAIN                          the chain identifier (default: T)
  --version VERSION                      the transaction version (default: 1)
  --options OPTIONS                      the transaction options (default: 0)

```
### Dispatcher.Dispatch


```
$ erdpy dispatcher dispatch --help
usage: erdpy dispatcher dispatch [-h] ...

Dispatch queued transactions

optional arguments:
  -h, --help                                   show this help message and exit
  --proxy PROXY                                🔗 the URL of the proxy (default: https://testnet-api.elrond.com)
  --pem PEM                                    🔑 the PEM file, if keyfile not provided
  --pem-index PEM_INDEX                        🔑 the index in the PEM file (default: 0)
  --keyfile KEYFILE                            🔑 a JSON keyfile, if PEM not provided
  --passfile PASSFILE                          🔑 a file containing keyfile's password, if keyfile provided
  --ledger                                     🔐 bool flag for signing transaction using ledger
  --ledger-account-index LEDGER_ACCOUNT_INDEX  🔐 the index of the account when using Ledger
  --ledger-address-index LEDGER_ADDRESS_INDEX  🔐 the index of the address when using Ledger
  --sender-username SENDER_USERNAME            🖄 the username of the sender

```
### Dispatcher.DispatchContinuously


```
$ erdpy dispatcher dispatch-continuously --help
usage: erdpy dispatcher dispatch-continuously [-h] ...

Continuously dispatch queued transactions

optional arguments:
  -h, --help                                   show this help message and exit
  --proxy PROXY                                🔗 the URL of the proxy (default: https://testnet-api.elrond.com)
  --pem PEM                                    🔑 the PEM file, if keyfile not provided
  --pem-index PEM_INDEX                        🔑 the index in the PEM file (default: 0)
  --keyfile KEYFILE                            🔑 a JSON keyfile, if PEM not provided
  --passfile PASSFILE                          🔑 a file containing keyfile's password, if keyfile provided
  --ledger                                     🔐 bool flag for signing transaction using ledger
  --ledger-account-index LEDGER_ACCOUNT_INDEX  🔐 the index of the account when using Ledger
  --ledger-address-index LEDGER_ADDRESS_INDEX  🔐 the index of the address when using Ledger
  --sender-username SENDER_USERNAME            🖄 the username of the sender
  --interval INTERVAL                          the interval to retrieve transactions from the queue, in seconds

```
### Dispatcher.Clean


```
$ erdpy dispatcher clean --help
usage: erdpy dispatcher clean [-h] ...

Clear queue of transactions

optional arguments:
  -h, --help  show this help message and exit

```
## Group **BlockAtlas**


```
$ erdpy blockatlas --help
usage: erdpy blockatlas COMMAND [-h] ...

Interact with an Block Atlas instance

COMMANDS:
  {current-block-number,block-by-number,transactions}

OPTIONS:
  -h, --help            show this help message and exit
  --url URL             🖧 URL of Block Atlas instance
  --coin COIN           coin identifier (e.g. erd, bnb)

----------------
COMMANDS summary
----------------
current-block-number           Get latest notarized metablock (number / nonce)
block-by-number                Get block by number (nonce)
transactions                   Get transactions by address

```
### BlockAtlas.CurrentBlockNumber


```
$ erdpy blockatlas current-block-number --help
usage: erdpy blockatlas current-block-number [-h] ...

Get latest notarized metablock (number / nonce)

optional arguments:
  -h, --help  show this help message and exit

```
### BlockAtlas.BlockByNumber


```
$ erdpy blockatlas block-by-number --help
usage: erdpy blockatlas block-by-number [-h] ...

Get block by number (nonce)

optional arguments:
  -h, --help       show this help message and exit
  --number NUMBER  the number (nonce)

```
### BlockAtlas.Transactions


```
$ erdpy blockatlas transactions --help
usage: erdpy blockatlas transactions [-h] ...

Get transactions by address

optional arguments:
  -h, --help         show this help message and exit
  --address ADDRESS  🖄 the address to query
  --outfile OUTFILE  where to save the output (default: stdout)

```
## Group **Dependencies**


```
$ erdpy deps --help
usage: erdpy deps COMMAND [-h] ...

Manage dependencies or elrond-sdk modules

COMMANDS:
  {install,check}

OPTIONS:
  -h, --help       show this help message and exit

----------------
COMMANDS summary
----------------
install                        Install dependencies or elrond-sdk modules.
check                          Check whether a dependency is installed.

```
### Dependencies.Install


```
$ erdpy deps install --help
usage: erdpy deps install [-h] ...

Install dependencies or elrond-sdk modules.

positional arguments:
  {all,llvm,clang,cpp,vmtools,rust,nodejs,elrond_go,elrond_proxy_go,golang,mcl_signer}
                                                  the dependency to install

optional arguments:
  -h, --help                                      show this help message and exit
  --overwrite                                     whether to overwrite an existing installation
  --tag TAG                                       the tag or version to install

```
### Dependencies.Check


```
$ erdpy deps check --help
usage: erdpy deps check [-h] ...

Check whether a dependency is installed.

positional arguments:
  {all,llvm,clang,cpp,vmtools,rust,nodejs,elrond_go,elrond_proxy_go,golang,mcl_signer}
                                                  the dependency to check

optional arguments:
  -h, --help                                      show this help message and exit
  --tag TAG                                       the tag or version to check

```
## Group **Configuration**


```
$ erdpy config --help
usage: erdpy config COMMAND [-h] ...

Configure elrond-sdk (default values etc.)

COMMANDS:
  {dump,get,set,delete,new,switch,list}

OPTIONS:
  -h, --help            show this help message and exit

----------------
COMMANDS summary
----------------
dump                           Dumps configuration.
get                            Gets a configuration value.
set                            Sets a configuration value.
delete                         Deletes a configuration value.
new                            Creates a new configuration.
switch                         Switch to a different config
list                           List available configs

```
### Configuration.Dump


```
$ erdpy config dump --help
usage: erdpy config dump [-h] ...

Dumps configuration.

optional arguments:
  -h, --help  show this help message and exit
  --defaults  dump defaults instead of local config

```
### Configuration.Get


```
$ erdpy config get --help
usage: erdpy config get [-h] ...

Gets a configuration value.

positional arguments:
  name        the name of the configuration entry

optional arguments:
  -h, --help  show this help message and exit

```
### Configuration.Set


```
$ erdpy config set --help
usage: erdpy config set [-h] ...

Sets a configuration value.

positional arguments:
  name        the name of the configuration entry
  value       the new value

optional arguments:
  -h, --help  show this help message and exit

```
### Configuration.New


```
$ erdpy config new --help
usage: erdpy config new [-h] ...

Creates a new configuration.

positional arguments:
  name                 the name of the configuration entry

optional arguments:
  -h, --help           show this help message and exit
  --template TEMPLATE  template from which to create the new config

```
### Configuration.Switch


```
$ erdpy config switch --help
usage: erdpy config switch [-h] ...

Switch to a different config

positional arguments:
  name        the name of the configuration entry

optional arguments:
  -h, --help  show this help message and exit

```
### Configuration.List


```
$ erdpy config list --help
usage: erdpy config list [-h] ...

List available configs

optional arguments:
  -h, --help  show this help message and exit

```
## Group **Data**


```
$ erdpy data --help
usage: erdpy data COMMAND [-h] ...

Data manipulation omnitool

COMMANDS:
  {parse,store,load}

OPTIONS:
  -h, --help          show this help message and exit

----------------
COMMANDS summary
----------------
parse                          Parses values from a given file
store                          Stores a key-value pair within a partition
load                           Loads a key-value pair from a storage partition

```
### Data.Dump


```
$ erdpy data parse --help
usage: erdpy data parse [-h] ...

Parses values from a given file

optional arguments:
  -h, --help               show this help message and exit
  --file FILE              path of the file to parse
  --expression EXPRESSION  the Python-Dictionary expression to evaluate in order to extract the data

```
### Data.Store


```
$ erdpy data store --help
usage: erdpy data store [-h] ...

Stores a key-value pair within a partition

optional arguments:
  -h, --help             show this help message and exit
  --key KEY              the key
  --value VALUE          the value to save
  --partition PARTITION  the storage partition (default: *)
  --use-global           use the global storage (default: False)

```
### Data.Load


```
$ erdpy data load --help
usage: erdpy data load [-h] ...

Loads a key-value pair from a storage partition

optional arguments:
  -h, --help             show this help message and exit
  --key KEY              the key
  --partition PARTITION  the storage partition (default: *)
  --use-global           use the global storage (default: False)

```
