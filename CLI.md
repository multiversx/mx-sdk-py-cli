# Command Line Interface

## Overview

**mxpy** exposes a number of CLI **commands**, organized within **groups**.


```
$ mxpy --help
usage: mxpy [-h] [-v] [--verbose] COMMAND-GROUP [-h] COMMAND ...

-----------
DESCRIPTION
-----------
mxpy is part of the multiversx-sdk and consists of Command Line Tools and Python SDK
for interacting with the Blockchain (in general) and with Smart Contracts (in particular).

mxpy targets a broad audience of users and developers.

See:
 - https://docs.multiversx.com/sdk-and-tools/sdk-py
 - https://docs.multiversx.com/sdk-and-tools/sdk-py/mxpy-cli
        

COMMAND GROUPS:
  {contract,tx,validator,account,ledger,wallet,deps,config,localnet,data,staking-provider,dns,faucet}

TOP-LEVEL OPTIONS:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  --verbose

----------------------
COMMAND GROUPS summary
----------------------
contract                       Build, deploy, upgrade and interact with Smart Contracts
tx                             Create and broadcast Transactions
validator                      Stake, UnStake, UnBond, Unjail and other actions useful for Validators
account                        Get Account data (nonce, balance) from the Network
ledger                         Get Ledger App addresses and version
wallet                         Create wallet, derive secret key from mnemonic, bech32 address helpers etc.
deps                           Manage dependencies or multiversx-sdk modules
config                         Configure multiversx-sdk (default values etc.)
localnet                       Set up, start and control localnets
data                           Data manipulation omnitool
staking-provider               Staking provider omnitool
dns                            Operations related to the Domain Name Service
faucet                         Get xEGLD on Devnet or Testnet

```
## Group **Contract**


```
$ mxpy contract --help
usage: mxpy contract COMMAND [-h] ...

Build, deploy, upgrade and interact with Smart Contracts

COMMANDS:
  {new,templates,build,clean,test,report,deploy,call,upgrade,query,verify,reproducible-build}

OPTIONS:
  -h, --help            show this help message and exit

----------------
COMMANDS summary
----------------
new                            Create a new Smart Contract project based on a template.
templates                      List the available Smart Contract templates.
build                          Build a Smart Contract project.
clean                          Clean a Smart Contract project.
test                           Run tests.
report                         Print a detailed report of the smart contracts.
deploy                         Deploy a Smart Contract.
call                           Interact with a Smart Contract (execute function).
upgrade                        Upgrade a previously-deployed Smart Contract.
query                          Query a Smart Contract (call a pure function)
verify                         Verify the authenticity of the code of a deployed Smart Contract
reproducible-build             Build a Smart Contract and get the same output as a previously built Smart Contract

```
### Contract.New


```
$ mxpy contract new --help
usage: mxpy contract new [-h] ...

Create a new Smart Contract project based on a template.

options:
  -h, --help           show this help message and exit
  --name NAME          The name of the contract. If missing, the name of the template will be used.
  --template TEMPLATE  the template to use
  --tag TAG            the framework version on which the contract should be created
  --path PATH          the parent directory of the project (default: current directory)

```
### Contract.Templates


```
$ mxpy contract templates --help
usage: mxpy contract templates [-h] ...

List the available Smart Contract templates.

options:
  -h, --help  show this help message and exit
  --tag TAG   the sc-meta framework version referred to

```
### Contract.Build


```
$ mxpy contract build --help
usage: mxpy contract build [-h] ...

Build a Smart Contract project.

options:
  -h, --help                 show this help message and exit
  --path PATH                the project directory (default: current directory)
  --no-wasm-opt              do not optimize wasm files after the build (default: False)
  --wasm-symbols             for rust projects, does not strip the symbols from the wasm output. Useful for analysing
                             the bytecode. Creates larger wasm files. Avoid in production (default: False)
  --wasm-name WASM_NAME      for rust projects, optionally specify the name of the wasm bytecode output file
  --wasm-suffix WASM_SUFFIX  for rust projects, optionally specify the suffix of the wasm bytecode output file
  --target-dir TARGET_DIR    for rust projects, forward the parameter to Cargo
  --wat                      also generate a WAT file when building
  --mir                      also emit MIR files when building
  --llvm-ir                  also emit LL (LLVM) files when building
  --ignore IGNORE            ignore all directories with these names. [default: target]
  --no-imports               skips extracting the EI imports after building the contracts
  --no-abi-git-version       skips loading the Git version into the ABI
  --twiggy-top               generate a twiggy top report after building
  --twiggy-paths             generate a twiggy paths report after building
  --twiggy-monos             generate a twiggy monos report after building
  --twiggy-dominators        generate a twiggy dominators report after building

```
### Contract.Clean


```
$ mxpy contract clean --help
usage: mxpy contract clean [-h] ...

Clean a Smart Contract project.

options:
  -h, --help   show this help message and exit
  --path PATH  the project directory (default: current directory)

```
### Contract.Deploy


```
$ mxpy contract deploy --help
usage: mxpy contract deploy [-h] ...

Deploy a Smart Contract.

Output example:
===============
{
    "emittedTransaction": {
        "nonce": 42,
        "sender": "alice",
        "receiver": "bob",
        "...": "..."
    },
    "emittedTransactionData": "the transaction data, not encoded",
    "emittedTransactionHash": "the transaction hash",
    "contractAddress": "the address of the contract",
    "transactionOnNetwork": {
        "nonce": 42,
        "sender": "alice",
        "receiver": "bob",
        "...": "..."
    },
    "simulation": {
        "execution": {
            "...": "..."
        },
        "cost": {
            "...": "..."
        }
    }
}

options:
  -h, --help                                      show this help message and exit
  --bytecode BYTECODE                             the file containing the WASM bytecode
  --abi ABI                                       the ABI of the Smart Contract
  --metadata-not-upgradeable                      ‼ mark the contract as NOT upgradeable (default: upgradeable)
  --metadata-not-readable                         ‼ mark the contract as NOT readable (default: readable)
  --metadata-payable                              ‼ mark the contract as payable (default: not payable)
  --metadata-payable-by-sc                        ‼ mark the contract as payable by SC (default: not payable by SC)
  --outfile OUTFILE                               where to save the output (default: stdout)
  --pem PEM                                       🔑 the PEM file, if keyfile not provided
  --pem-index PEM_INDEX                           🔑 the index in the PEM file (default: 0)
  --keyfile KEYFILE                               🔑 a JSON keyfile, if PEM not provided
  --passfile PASSFILE                             🔑 a file containing keyfile's password, if keyfile provided
  --ledger                                        🔐 bool flag for signing transaction using ledger
  --ledger-account-index LEDGER_ACCOUNT_INDEX     🔐 the index of the account when using Ledger
  --ledger-address-index LEDGER_ADDRESS_INDEX     🔐 the index of the address when using Ledger
  --sender-username SENDER_USERNAME               🖄 the username of the sender
  --proxy PROXY                                   🔗 the URL of the proxy
  --nonce NONCE                                   # the nonce for the transaction
  --recall-nonce                                  ⭮ whether to recall the nonce when creating the transaction (default:
                                                  False)
  --gas-price GAS_PRICE                           ⛽ the gas price (default: 1000000000)
  --gas-limit GAS_LIMIT                           ⛽ the gas limit
  --value VALUE                                   the value to transfer (default: 0)
  --chain CHAIN                                   the chain identifier
  --version VERSION                               the transaction version (default: 2)
  --guardian GUARDIAN                             the address of the guradian
  --guardian-service-url GUARDIAN_SERVICE_URL     the url of the guardian service
  --guardian-2fa-code GUARDIAN_2FA_CODE           the 2fa code for the guardian
  --relayer RELAYER                               the address of the relayer
  --inner-transactions INNER_TRANSACTIONS         a json file containing the inner transactions; should only be provided
                                                  when creating the relayer's transaction
  --inner-transactions-outfile INNER_TRANSACTIONS_OUTFILE
                                                  where to save the transaction as an inner transaction (default:
                                                  stdout)
  --options OPTIONS                               the transaction options (default: 0)
  --arguments ARGUMENTS [ARGUMENTS ...]           arguments for the contract transaction, as [number, bech32-address,
                                                  ascii string, boolean] or hex-encoded. E.g. --arguments 42 0x64 1000
                                                  0xabba str:TOK-a1c2ef true erd1[..]
  --arguments-file ARGUMENTS_FILE                 a json file containing the arguments. ONLY if abi file is provided.
                                                  E.g. [{ 'to': 'erd1...', 'amount': 10000000000 }]
  --wait-result                                   signal to wait for the transaction result - only valid if --send is
                                                  set
  --timeout TIMEOUT                               max num of seconds to wait for result - only valid if --wait-result is
                                                  set
  --send                                          ✓ whether to broadcast the transaction (default: False)
  --simulate                                      whether to simulate the transaction (default: False)
  --guardian-pem GUARDIAN_PEM                     🔑 the PEM file, if keyfile not provided
  --guardian-pem-index GUARDIAN_PEM_INDEX         🔑 the index in the PEM file (default: 0)
  --guardian-keyfile GUARDIAN_KEYFILE             🔑 a JSON keyfile, if PEM not provided
  --guardian-passfile GUARDIAN_PASSFILE           🔑 a file containing keyfile's password, if keyfile provided
  --guardian-ledger                               🔐 bool flag for signing transaction using ledger
  --guardian-ledger-account-index GUARDIAN_LEDGER_ACCOUNT_INDEX
                                                  🔐 the index of the account when using Ledger
  --guardian-ledger-address-index GUARDIAN_LEDGER_ADDRESS_INDEX
                                                  🔐 the index of the address when using Ledger

```
### Contract.Call


```
$ mxpy contract call --help
usage: mxpy contract call [-h] ...

Interact with a Smart Contract (execute function).

Output example:
===============
{
    "emittedTransaction": {
        "nonce": 42,
        "sender": "alice",
        "receiver": "bob",
        "...": "..."
    },
    "emittedTransactionData": "the transaction data, not encoded",
    "emittedTransactionHash": "the transaction hash",
    "contractAddress": "the address of the contract",
    "transactionOnNetwork": {
        "nonce": 42,
        "sender": "alice",
        "receiver": "bob",
        "...": "..."
    },
    "simulation": {
        "execution": {
            "...": "..."
        },
        "cost": {
            "...": "..."
        }
    }
}

positional arguments:
  contract                                        🖄 the address of the Smart Contract

options:
  -h, --help                                      show this help message and exit
  --abi ABI                                       the ABI of the Smart Contract
  --outfile OUTFILE                               where to save the output (default: stdout)
  --pem PEM                                       🔑 the PEM file, if keyfile not provided
  --pem-index PEM_INDEX                           🔑 the index in the PEM file (default: 0)
  --keyfile KEYFILE                               🔑 a JSON keyfile, if PEM not provided
  --passfile PASSFILE                             🔑 a file containing keyfile's password, if keyfile provided
  --ledger                                        🔐 bool flag for signing transaction using ledger
  --ledger-account-index LEDGER_ACCOUNT_INDEX     🔐 the index of the account when using Ledger
  --ledger-address-index LEDGER_ADDRESS_INDEX     🔐 the index of the address when using Ledger
  --sender-username SENDER_USERNAME               🖄 the username of the sender
  --proxy PROXY                                   🔗 the URL of the proxy
  --nonce NONCE                                   # the nonce for the transaction
  --recall-nonce                                  ⭮ whether to recall the nonce when creating the transaction (default:
                                                  False)
  --gas-price GAS_PRICE                           ⛽ the gas price (default: 1000000000)
  --gas-limit GAS_LIMIT                           ⛽ the gas limit
  --value VALUE                                   the value to transfer (default: 0)
  --chain CHAIN                                   the chain identifier
  --version VERSION                               the transaction version (default: 2)
  --guardian GUARDIAN                             the address of the guradian
  --guardian-service-url GUARDIAN_SERVICE_URL     the url of the guardian service
  --guardian-2fa-code GUARDIAN_2FA_CODE           the 2fa code for the guardian
  --relayer RELAYER                               the address of the relayer
  --inner-transactions INNER_TRANSACTIONS         a json file containing the inner transactions; should only be provided
                                                  when creating the relayer's transaction
  --inner-transactions-outfile INNER_TRANSACTIONS_OUTFILE
                                                  where to save the transaction as an inner transaction (default:
                                                  stdout)
  --options OPTIONS                               the transaction options (default: 0)
  --function FUNCTION                             the function to call
  --arguments ARGUMENTS [ARGUMENTS ...]           arguments for the contract transaction, as [number, bech32-address,
                                                  ascii string, boolean] or hex-encoded. E.g. --arguments 42 0x64 1000
                                                  0xabba str:TOK-a1c2ef true erd1[..]
  --arguments-file ARGUMENTS_FILE                 a json file containing the arguments. ONLY if abi file is provided.
                                                  E.g. [{ 'to': 'erd1...', 'amount': 10000000000 }]
  --token-transfers TOKEN_TRANSFERS [TOKEN_TRANSFERS ...]
                                                  token transfers for transfer & execute, as [token, amount] E.g.
                                                  --token-transfers NFT-123456-0a 1 ESDT-987654 100000000
  --wait-result                                   signal to wait for the transaction result - only valid if --send is
                                                  set
  --timeout TIMEOUT                               max num of seconds to wait for result - only valid if --wait-result is
                                                  set
  --send                                          ✓ whether to broadcast the transaction (default: False)
  --simulate                                      whether to simulate the transaction (default: False)
  --relay                                         whether to relay the transaction (default: False)
  --guardian-pem GUARDIAN_PEM                     🔑 the PEM file, if keyfile not provided
  --guardian-pem-index GUARDIAN_PEM_INDEX         🔑 the index in the PEM file (default: 0)
  --guardian-keyfile GUARDIAN_KEYFILE             🔑 a JSON keyfile, if PEM not provided
  --guardian-passfile GUARDIAN_PASSFILE           🔑 a file containing keyfile's password, if keyfile provided
  --guardian-ledger                               🔐 bool flag for signing transaction using ledger
  --guardian-ledger-account-index GUARDIAN_LEDGER_ACCOUNT_INDEX
                                                  🔐 the index of the account when using Ledger
  --guardian-ledger-address-index GUARDIAN_LEDGER_ADDRESS_INDEX
                                                  🔐 the index of the address when using Ledger

```
### Contract.Upgrade


```
$ mxpy contract upgrade --help
usage: mxpy contract upgrade [-h] ...

Upgrade a previously-deployed Smart Contract.

Output example:
===============
{
    "emittedTransaction": {
        "nonce": 42,
        "sender": "alice",
        "receiver": "bob",
        "...": "..."
    },
    "emittedTransactionData": "the transaction data, not encoded",
    "emittedTransactionHash": "the transaction hash",
    "contractAddress": "the address of the contract",
    "transactionOnNetwork": {
        "nonce": 42,
        "sender": "alice",
        "receiver": "bob",
        "...": "..."
    },
    "simulation": {
        "execution": {
            "...": "..."
        },
        "cost": {
            "...": "..."
        }
    }
}

positional arguments:
  contract                                        🖄 the address of the Smart Contract

options:
  -h, --help                                      show this help message and exit
  --abi ABI                                       the ABI of the Smart Contract
  --outfile OUTFILE                               where to save the output (default: stdout)
  --bytecode BYTECODE                             the file containing the WASM bytecode
  --metadata-not-upgradeable                      ‼ mark the contract as NOT upgradeable (default: upgradeable)
  --metadata-not-readable                         ‼ mark the contract as NOT readable (default: readable)
  --metadata-payable                              ‼ mark the contract as payable (default: not payable)
  --metadata-payable-by-sc                        ‼ mark the contract as payable by SC (default: not payable by SC)
  --pem PEM                                       🔑 the PEM file, if keyfile not provided
  --pem-index PEM_INDEX                           🔑 the index in the PEM file (default: 0)
  --keyfile KEYFILE                               🔑 a JSON keyfile, if PEM not provided
  --passfile PASSFILE                             🔑 a file containing keyfile's password, if keyfile provided
  --ledger                                        🔐 bool flag for signing transaction using ledger
  --ledger-account-index LEDGER_ACCOUNT_INDEX     🔐 the index of the account when using Ledger
  --ledger-address-index LEDGER_ADDRESS_INDEX     🔐 the index of the address when using Ledger
  --sender-username SENDER_USERNAME               🖄 the username of the sender
  --proxy PROXY                                   🔗 the URL of the proxy
  --nonce NONCE                                   # the nonce for the transaction
  --recall-nonce                                  ⭮ whether to recall the nonce when creating the transaction (default:
                                                  False)
  --gas-price GAS_PRICE                           ⛽ the gas price (default: 1000000000)
  --gas-limit GAS_LIMIT                           ⛽ the gas limit
  --value VALUE                                   the value to transfer (default: 0)
  --chain CHAIN                                   the chain identifier
  --version VERSION                               the transaction version (default: 2)
  --guardian GUARDIAN                             the address of the guradian
  --guardian-service-url GUARDIAN_SERVICE_URL     the url of the guardian service
  --guardian-2fa-code GUARDIAN_2FA_CODE           the 2fa code for the guardian
  --relayer RELAYER                               the address of the relayer
  --inner-transactions INNER_TRANSACTIONS         a json file containing the inner transactions; should only be provided
                                                  when creating the relayer's transaction
  --inner-transactions-outfile INNER_TRANSACTIONS_OUTFILE
                                                  where to save the transaction as an inner transaction (default:
                                                  stdout)
  --options OPTIONS                               the transaction options (default: 0)
  --arguments ARGUMENTS [ARGUMENTS ...]           arguments for the contract transaction, as [number, bech32-address,
                                                  ascii string, boolean] or hex-encoded. E.g. --arguments 42 0x64 1000
                                                  0xabba str:TOK-a1c2ef true erd1[..]
  --arguments-file ARGUMENTS_FILE                 a json file containing the arguments. ONLY if abi file is provided.
                                                  E.g. [{ 'to': 'erd1...', 'amount': 10000000000 }]
  --wait-result                                   signal to wait for the transaction result - only valid if --send is
                                                  set
  --timeout TIMEOUT                               max num of seconds to wait for result - only valid if --wait-result is
                                                  set
  --send                                          ✓ whether to broadcast the transaction (default: False)
  --simulate                                      whether to simulate the transaction (default: False)
  --guardian-pem GUARDIAN_PEM                     🔑 the PEM file, if keyfile not provided
  --guardian-pem-index GUARDIAN_PEM_INDEX         🔑 the index in the PEM file (default: 0)
  --guardian-keyfile GUARDIAN_KEYFILE             🔑 a JSON keyfile, if PEM not provided
  --guardian-passfile GUARDIAN_PASSFILE           🔑 a file containing keyfile's password, if keyfile provided
  --guardian-ledger                               🔐 bool flag for signing transaction using ledger
  --guardian-ledger-account-index GUARDIAN_LEDGER_ACCOUNT_INDEX
                                                  🔐 the index of the account when using Ledger
  --guardian-ledger-address-index GUARDIAN_LEDGER_ADDRESS_INDEX
                                                  🔐 the index of the address when using Ledger

```
### Contract.Query


```
$ mxpy contract query --help
usage: mxpy contract query [-h] ...

Query a Smart Contract (call a pure function)

positional arguments:
  contract                               🖄 the address of the Smart Contract

options:
  -h, --help                             show this help message and exit
  --abi ABI                              the ABI of the Smart Contract
  --proxy PROXY                          🔗 the URL of the proxy
  --function FUNCTION                    the function to call
  --arguments ARGUMENTS [ARGUMENTS ...]  arguments for the contract transaction, as [number, bech32-address, ascii
                                         string, boolean] or hex-encoded. E.g. --arguments 42 0x64 1000 0xabba
                                         str:TOK-a1c2ef true erd1[..]
  --arguments-file ARGUMENTS_FILE        a json file containing the arguments. ONLY if abi file is provided. E.g. [{
                                         'to': 'erd1...', 'amount': 10000000000 }]

```
### Contract.Report


```
$ mxpy contract report --help
usage: mxpy contract report [-h] ...

Print a detailed report of the smart contracts.

options:
  -h, --help                                      show this help message and exit
  --skip-build                                    skips the step of building of the wasm contracts
  --skip-twiggy                                   skips the steps of building the debug wasm files and running twiggy
  --output-format {github-markdown,text-markdown,json}
                                                  report output format (default: text-markdown)
  --output-file OUTPUT_FILE                       if specified, the output is written to a file, otherwise it's written
                                                  to the standard output
  --compare report-1.json [report-2.json ...]     create a comparison from two or more reports
  --path PATH                                     the project directory (default: current directory)
  --no-wasm-opt                                   do not optimize wasm files after the build (default: False)
  --wasm-symbols                                  for rust projects, does not strip the symbols from the wasm output.
                                                  Useful for analysing the bytecode. Creates larger wasm files. Avoid in
                                                  production (default: False)
  --wasm-name WASM_NAME                           for rust projects, optionally specify the name of the wasm bytecode
                                                  output file
  --wasm-suffix WASM_SUFFIX                       for rust projects, optionally specify the suffix of the wasm bytecode
                                                  output file
  --target-dir TARGET_DIR                         for rust projects, forward the parameter to Cargo
  --wat                                           also generate a WAT file when building
  --mir                                           also emit MIR files when building
  --llvm-ir                                       also emit LL (LLVM) files when building
  --ignore IGNORE                                 ignore all directories with these names. [default: target]
  --no-imports                                    skips extracting the EI imports after building the contracts
  --no-abi-git-version                            skips loading the Git version into the ABI
  --twiggy-top                                    generate a twiggy top report after building
  --twiggy-paths                                  generate a twiggy paths report after building
  --twiggy-monos                                  generate a twiggy monos report after building
  --twiggy-dominators                             generate a twiggy dominators report after building

```
## Group **Transactions**


```
$ mxpy tx --help
usage: mxpy tx COMMAND [-h] ...

Create and broadcast Transactions

COMMANDS:
  {new,send,get,sign}

OPTIONS:
  -h, --help           show this help message and exit

----------------
COMMANDS summary
----------------
new                            Create a new transaction.
send                           Send a previously saved transaction.
get                            Get a transaction.
sign                           Sign a previously saved transaction.

```
### Transactions.New


```
$ mxpy tx new --help
usage: mxpy tx new [-h] ...

Create a new transaction.

Output example:
===============
{
    "emittedTransaction": {
        "nonce": 42,
        "sender": "alice",
        "receiver": "bob",
        "...": "..."
    },
    "emittedTransactionData": "the transaction data, not encoded",
    "emittedTransactionHash": "the transaction hash"
}

options:
  -h, --help                                      show this help message and exit
  --pem PEM                                       🔑 the PEM file, if keyfile not provided
  --pem-index PEM_INDEX                           🔑 the index in the PEM file (default: 0)
  --keyfile KEYFILE                               🔑 a JSON keyfile, if PEM not provided
  --passfile PASSFILE                             🔑 a file containing keyfile's password, if keyfile provided
  --ledger                                        🔐 bool flag for signing transaction using ledger
  --ledger-account-index LEDGER_ACCOUNT_INDEX     🔐 the index of the account when using Ledger
  --ledger-address-index LEDGER_ADDRESS_INDEX     🔐 the index of the address when using Ledger
  --sender-username SENDER_USERNAME               🖄 the username of the sender
  --nonce NONCE                                   # the nonce for the transaction
  --recall-nonce                                  ⭮ whether to recall the nonce when creating the transaction (default:
                                                  False)
  --receiver RECEIVER                             🖄 the address of the receiver
  --receiver-username RECEIVER_USERNAME           🖄 the username of the receiver
  --gas-price GAS_PRICE                           ⛽ the gas price (default: 1000000000)
  --gas-limit GAS_LIMIT                           ⛽ the gas limit
  --value VALUE                                   the value to transfer (default: 0)
  --data DATA                                     the payload, or 'memo' of the transaction (default: )
  --chain CHAIN                                   the chain identifier
  --version VERSION                               the transaction version (default: 2)
  --guardian GUARDIAN                             the address of the guradian
  --guardian-service-url GUARDIAN_SERVICE_URL     the url of the guardian service
  --guardian-2fa-code GUARDIAN_2FA_CODE           the 2fa code for the guardian
  --relayer RELAYER                               the address of the relayer
  --inner-transactions INNER_TRANSACTIONS         a json file containing the inner transactions; should only be provided
                                                  when creating the relayer's transaction
  --inner-transactions-outfile INNER_TRANSACTIONS_OUTFILE
                                                  where to save the transaction as an inner transaction (default:
                                                  stdout)
  --options OPTIONS                               the transaction options (default: 0)
  --data-file DATA_FILE                           a file containing transaction data
  --token-transfers TOKEN_TRANSFERS [TOKEN_TRANSFERS ...]
                                                  token transfers for transfer & execute, as [token, amount] E.g.
                                                  --token-transfers NFT-123456-0a 1 ESDT-987654 100000000
  --outfile OUTFILE                               where to save the output (signed transaction, hash) (default: stdout)
  --send                                          ✓ whether to broadcast the transaction (default: False)
  --simulate                                      whether to simulate the transaction (default: False)
  --relay                                         whether to relay the transaction (default: False)
  --proxy PROXY                                   🔗 the URL of the proxy
  --guardian-pem GUARDIAN_PEM                     🔑 the PEM file, if keyfile not provided
  --guardian-pem-index GUARDIAN_PEM_INDEX         🔑 the index in the PEM file (default: 0)
  --guardian-keyfile GUARDIAN_KEYFILE             🔑 a JSON keyfile, if PEM not provided
  --guardian-passfile GUARDIAN_PASSFILE           🔑 a file containing keyfile's password, if keyfile provided
  --guardian-ledger                               🔐 bool flag for signing transaction using ledger
  --guardian-ledger-account-index GUARDIAN_LEDGER_ACCOUNT_INDEX
                                                  🔐 the index of the account when using Ledger
  --guardian-ledger-address-index GUARDIAN_LEDGER_ADDRESS_INDEX
                                                  🔐 the index of the address when using Ledger
  --wait-result                                   signal to wait for the transaction result - only valid if --send is
                                                  set
  --timeout TIMEOUT                               max num of seconds to wait for result - only valid if --wait-result is
                                                  set

```
### Transactions.Send


```
$ mxpy tx send --help
usage: mxpy tx send [-h] ...

Send a previously saved transaction.

Output example:
===============
{
    "emittedTransaction": {
        "nonce": 42,
        "sender": "alice",
        "receiver": "bob",
        "...": "..."
    },
    "emittedTransactionData": "the transaction data, not encoded",
    "emittedTransactionHash": "the transaction hash"
}

options:
  -h, --help         show this help message and exit
  --infile INFILE    input file (a previously saved transaction)
  --outfile OUTFILE  where to save the output (the hash) (default: stdout)
  --proxy PROXY      🔗 the URL of the proxy

```
### Transactions.Get


```
$ mxpy tx get --help
usage: mxpy tx get [-h] ...

Get a transaction.

Output example:
===============
{
    "transactionOnNetwork": {
        "nonce": 42,
        "sender": "alice",
        "receiver": "bob",
        "...": "..."
    }
}

options:
  -h, --help                 show this help message and exit
  --hash HASH                the hash
  --sender SENDER            the sender address
  --with-results             will also return the results of transaction
  --proxy PROXY              🔗 the URL of the proxy
  --omit-fields OMIT_FIELDS  omit fields in the output payload (default: [])

```
## Group **Validator**


```
$ mxpy validator --help
usage: mxpy validator COMMAND [-h] ...

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
$ mxpy validator stake --help
usage: mxpy validator stake [-h] ...

Stake value into the Network

options:
  -h, --help                                      show this help message and exit
  --proxy PROXY                                   🔗 the URL of the proxy
  --pem PEM                                       🔑 the PEM file, if keyfile not provided
  --pem-index PEM_INDEX                           🔑 the index in the PEM file (default: 0)
  --keyfile KEYFILE                               🔑 a JSON keyfile, if PEM not provided
  --passfile PASSFILE                             🔑 a file containing keyfile's password, if keyfile provided
  --ledger                                        🔐 bool flag for signing transaction using ledger
  --ledger-account-index LEDGER_ACCOUNT_INDEX     🔐 the index of the account when using Ledger
  --ledger-address-index LEDGER_ADDRESS_INDEX     🔐 the index of the address when using Ledger
  --sender-username SENDER_USERNAME               🖄 the username of the sender
  --nonce NONCE                                   # the nonce for the transaction
  --recall-nonce                                  ⭮ whether to recall the nonce when creating the transaction (default:
                                                  False)
  --gas-price GAS_PRICE                           ⛽ the gas price (default: 1000000000)
  --gas-limit GAS_LIMIT                           ⛽ the gas limit
  --estimate-gas                                  ⛽ whether to estimate the gas limit (default: 0)
  --value VALUE                                   the value to transfer (default: 0)
  --chain CHAIN                                   the chain identifier
  --version VERSION                               the transaction version (default: 2)
  --guardian GUARDIAN                             the address of the guradian
  --guardian-service-url GUARDIAN_SERVICE_URL     the url of the guardian service
  --guardian-2fa-code GUARDIAN_2FA_CODE           the 2fa code for the guardian
  --relayer RELAYER                               the address of the relayer
  --inner-transactions INNER_TRANSACTIONS         a json file containing the inner transactions; should only be provided
                                                  when creating the relayer's transaction
  --inner-transactions-outfile INNER_TRANSACTIONS_OUTFILE
                                                  where to save the transaction as an inner transaction (default:
                                                  stdout)
  --options OPTIONS                               the transaction options (default: 0)
  --send                                          ✓ whether to broadcast the transaction (default: False)
  --simulate                                      whether to simulate the transaction (default: False)
  --outfile OUTFILE                               where to save the output (signed transaction, hash) (default: stdout)
  --guardian-pem GUARDIAN_PEM                     🔑 the PEM file, if keyfile not provided
  --guardian-pem-index GUARDIAN_PEM_INDEX         🔑 the index in the PEM file (default: 0)
  --guardian-keyfile GUARDIAN_KEYFILE             🔑 a JSON keyfile, if PEM not provided
  --guardian-passfile GUARDIAN_PASSFILE           🔑 a file containing keyfile's password, if keyfile provided
  --guardian-ledger                               🔐 bool flag for signing transaction using ledger
  --guardian-ledger-account-index GUARDIAN_LEDGER_ACCOUNT_INDEX
                                                  🔐 the index of the account when using Ledger
  --guardian-ledger-address-index GUARDIAN_LEDGER_ADDRESS_INDEX
                                                  🔐 the index of the address when using Ledger
  --reward-address REWARD_ADDRESS                 the reward address
  --validators-file VALIDATORS_FILE               a JSON file describing the Nodes
  --top-up                                        Stake value for top up

```
### Validator.Unstake


```
$ mxpy validator unstake --help
usage: mxpy validator unstake [-h] ...

Unstake value

options:
  -h, --help                                      show this help message and exit
  --proxy PROXY                                   🔗 the URL of the proxy
  --pem PEM                                       🔑 the PEM file, if keyfile not provided
  --pem-index PEM_INDEX                           🔑 the index in the PEM file (default: 0)
  --keyfile KEYFILE                               🔑 a JSON keyfile, if PEM not provided
  --passfile PASSFILE                             🔑 a file containing keyfile's password, if keyfile provided
  --ledger                                        🔐 bool flag for signing transaction using ledger
  --ledger-account-index LEDGER_ACCOUNT_INDEX     🔐 the index of the account when using Ledger
  --ledger-address-index LEDGER_ADDRESS_INDEX     🔐 the index of the address when using Ledger
  --sender-username SENDER_USERNAME               🖄 the username of the sender
  --nonce NONCE                                   # the nonce for the transaction
  --recall-nonce                                  ⭮ whether to recall the nonce when creating the transaction (default:
                                                  False)
  --gas-price GAS_PRICE                           ⛽ the gas price (default: 1000000000)
  --gas-limit GAS_LIMIT                           ⛽ the gas limit
  --estimate-gas                                  ⛽ whether to estimate the gas limit (default: 0)
  --value VALUE                                   the value to transfer (default: 0)
  --chain CHAIN                                   the chain identifier
  --version VERSION                               the transaction version (default: 2)
  --guardian GUARDIAN                             the address of the guradian
  --guardian-service-url GUARDIAN_SERVICE_URL     the url of the guardian service
  --guardian-2fa-code GUARDIAN_2FA_CODE           the 2fa code for the guardian
  --relayer RELAYER                               the address of the relayer
  --inner-transactions INNER_TRANSACTIONS         a json file containing the inner transactions; should only be provided
                                                  when creating the relayer's transaction
  --inner-transactions-outfile INNER_TRANSACTIONS_OUTFILE
                                                  where to save the transaction as an inner transaction (default:
                                                  stdout)
  --options OPTIONS                               the transaction options (default: 0)
  --send                                          ✓ whether to broadcast the transaction (default: False)
  --simulate                                      whether to simulate the transaction (default: False)
  --outfile OUTFILE                               where to save the output (signed transaction, hash) (default: stdout)
  --guardian-pem GUARDIAN_PEM                     🔑 the PEM file, if keyfile not provided
  --guardian-pem-index GUARDIAN_PEM_INDEX         🔑 the index in the PEM file (default: 0)
  --guardian-keyfile GUARDIAN_KEYFILE             🔑 a JSON keyfile, if PEM not provided
  --guardian-passfile GUARDIAN_PASSFILE           🔑 a file containing keyfile's password, if keyfile provided
  --guardian-ledger                               🔐 bool flag for signing transaction using ledger
  --guardian-ledger-account-index GUARDIAN_LEDGER_ACCOUNT_INDEX
                                                  🔐 the index of the account when using Ledger
  --guardian-ledger-address-index GUARDIAN_LEDGER_ADDRESS_INDEX
                                                  🔐 the index of the address when using Ledger
  --nodes-public-keys NODES_PUBLIC_KEYS           the public keys of the nodes as CSV (addrA,addrB)

```
### Validator.Unjail


```
$ mxpy validator unjail --help
usage: mxpy validator unjail [-h] ...

Unjail a Validator Node

options:
  -h, --help                                      show this help message and exit
  --proxy PROXY                                   🔗 the URL of the proxy
  --pem PEM                                       🔑 the PEM file, if keyfile not provided
  --pem-index PEM_INDEX                           🔑 the index in the PEM file (default: 0)
  --keyfile KEYFILE                               🔑 a JSON keyfile, if PEM not provided
  --passfile PASSFILE                             🔑 a file containing keyfile's password, if keyfile provided
  --ledger                                        🔐 bool flag for signing transaction using ledger
  --ledger-account-index LEDGER_ACCOUNT_INDEX     🔐 the index of the account when using Ledger
  --ledger-address-index LEDGER_ADDRESS_INDEX     🔐 the index of the address when using Ledger
  --sender-username SENDER_USERNAME               🖄 the username of the sender
  --nonce NONCE                                   # the nonce for the transaction
  --recall-nonce                                  ⭮ whether to recall the nonce when creating the transaction (default:
                                                  False)
  --gas-price GAS_PRICE                           ⛽ the gas price (default: 1000000000)
  --gas-limit GAS_LIMIT                           ⛽ the gas limit
  --estimate-gas                                  ⛽ whether to estimate the gas limit (default: 0)
  --value VALUE                                   the value to transfer (default: 0)
  --chain CHAIN                                   the chain identifier
  --version VERSION                               the transaction version (default: 2)
  --guardian GUARDIAN                             the address of the guradian
  --guardian-service-url GUARDIAN_SERVICE_URL     the url of the guardian service
  --guardian-2fa-code GUARDIAN_2FA_CODE           the 2fa code for the guardian
  --relayer RELAYER                               the address of the relayer
  --inner-transactions INNER_TRANSACTIONS         a json file containing the inner transactions; should only be provided
                                                  when creating the relayer's transaction
  --inner-transactions-outfile INNER_TRANSACTIONS_OUTFILE
                                                  where to save the transaction as an inner transaction (default:
                                                  stdout)
  --options OPTIONS                               the transaction options (default: 0)
  --send                                          ✓ whether to broadcast the transaction (default: False)
  --simulate                                      whether to simulate the transaction (default: False)
  --outfile OUTFILE                               where to save the output (signed transaction, hash) (default: stdout)
  --guardian-pem GUARDIAN_PEM                     🔑 the PEM file, if keyfile not provided
  --guardian-pem-index GUARDIAN_PEM_INDEX         🔑 the index in the PEM file (default: 0)
  --guardian-keyfile GUARDIAN_KEYFILE             🔑 a JSON keyfile, if PEM not provided
  --guardian-passfile GUARDIAN_PASSFILE           🔑 a file containing keyfile's password, if keyfile provided
  --guardian-ledger                               🔐 bool flag for signing transaction using ledger
  --guardian-ledger-account-index GUARDIAN_LEDGER_ACCOUNT_INDEX
                                                  🔐 the index of the account when using Ledger
  --guardian-ledger-address-index GUARDIAN_LEDGER_ADDRESS_INDEX
                                                  🔐 the index of the address when using Ledger
  --nodes-public-keys NODES_PUBLIC_KEYS           the public keys of the nodes as CSV (addrA,addrB)

```
### Validator.Unbond


```
$ mxpy validator unbond --help
usage: mxpy validator unbond [-h] ...

Unbond tokens for a bls key

options:
  -h, --help                                      show this help message and exit
  --proxy PROXY                                   🔗 the URL of the proxy
  --pem PEM                                       🔑 the PEM file, if keyfile not provided
  --pem-index PEM_INDEX                           🔑 the index in the PEM file (default: 0)
  --keyfile KEYFILE                               🔑 a JSON keyfile, if PEM not provided
  --passfile PASSFILE                             🔑 a file containing keyfile's password, if keyfile provided
  --ledger                                        🔐 bool flag for signing transaction using ledger
  --ledger-account-index LEDGER_ACCOUNT_INDEX     🔐 the index of the account when using Ledger
  --ledger-address-index LEDGER_ADDRESS_INDEX     🔐 the index of the address when using Ledger
  --sender-username SENDER_USERNAME               🖄 the username of the sender
  --nonce NONCE                                   # the nonce for the transaction
  --recall-nonce                                  ⭮ whether to recall the nonce when creating the transaction (default:
                                                  False)
  --gas-price GAS_PRICE                           ⛽ the gas price (default: 1000000000)
  --gas-limit GAS_LIMIT                           ⛽ the gas limit
  --estimate-gas                                  ⛽ whether to estimate the gas limit (default: 0)
  --value VALUE                                   the value to transfer (default: 0)
  --chain CHAIN                                   the chain identifier
  --version VERSION                               the transaction version (default: 2)
  --guardian GUARDIAN                             the address of the guradian
  --guardian-service-url GUARDIAN_SERVICE_URL     the url of the guardian service
  --guardian-2fa-code GUARDIAN_2FA_CODE           the 2fa code for the guardian
  --relayer RELAYER                               the address of the relayer
  --inner-transactions INNER_TRANSACTIONS         a json file containing the inner transactions; should only be provided
                                                  when creating the relayer's transaction
  --inner-transactions-outfile INNER_TRANSACTIONS_OUTFILE
                                                  where to save the transaction as an inner transaction (default:
                                                  stdout)
  --options OPTIONS                               the transaction options (default: 0)
  --send                                          ✓ whether to broadcast the transaction (default: False)
  --simulate                                      whether to simulate the transaction (default: False)
  --outfile OUTFILE                               where to save the output (signed transaction, hash) (default: stdout)
  --guardian-pem GUARDIAN_PEM                     🔑 the PEM file, if keyfile not provided
  --guardian-pem-index GUARDIAN_PEM_INDEX         🔑 the index in the PEM file (default: 0)
  --guardian-keyfile GUARDIAN_KEYFILE             🔑 a JSON keyfile, if PEM not provided
  --guardian-passfile GUARDIAN_PASSFILE           🔑 a file containing keyfile's password, if keyfile provided
  --guardian-ledger                               🔐 bool flag for signing transaction using ledger
  --guardian-ledger-account-index GUARDIAN_LEDGER_ACCOUNT_INDEX
                                                  🔐 the index of the account when using Ledger
  --guardian-ledger-address-index GUARDIAN_LEDGER_ADDRESS_INDEX
                                                  🔐 the index of the address when using Ledger
  --nodes-public-keys NODES_PUBLIC_KEYS           the public keys of the nodes as CSV (addrA,addrB)

```
### Validator.ChangeRewardAddress


```
$ mxpy validator change-reward-address --help
usage: mxpy validator change-reward-address [-h] ...

Change the reward address

options:
  -h, --help                                      show this help message and exit
  --proxy PROXY                                   🔗 the URL of the proxy
  --pem PEM                                       🔑 the PEM file, if keyfile not provided
  --pem-index PEM_INDEX                           🔑 the index in the PEM file (default: 0)
  --keyfile KEYFILE                               🔑 a JSON keyfile, if PEM not provided
  --passfile PASSFILE                             🔑 a file containing keyfile's password, if keyfile provided
  --ledger                                        🔐 bool flag for signing transaction using ledger
  --ledger-account-index LEDGER_ACCOUNT_INDEX     🔐 the index of the account when using Ledger
  --ledger-address-index LEDGER_ADDRESS_INDEX     🔐 the index of the address when using Ledger
  --sender-username SENDER_USERNAME               🖄 the username of the sender
  --nonce NONCE                                   # the nonce for the transaction
  --recall-nonce                                  ⭮ whether to recall the nonce when creating the transaction (default:
                                                  False)
  --gas-price GAS_PRICE                           ⛽ the gas price (default: 1000000000)
  --gas-limit GAS_LIMIT                           ⛽ the gas limit
  --estimate-gas                                  ⛽ whether to estimate the gas limit (default: 0)
  --value VALUE                                   the value to transfer (default: 0)
  --chain CHAIN                                   the chain identifier
  --version VERSION                               the transaction version (default: 2)
  --guardian GUARDIAN                             the address of the guradian
  --guardian-service-url GUARDIAN_SERVICE_URL     the url of the guardian service
  --guardian-2fa-code GUARDIAN_2FA_CODE           the 2fa code for the guardian
  --relayer RELAYER                               the address of the relayer
  --inner-transactions INNER_TRANSACTIONS         a json file containing the inner transactions; should only be provided
                                                  when creating the relayer's transaction
  --inner-transactions-outfile INNER_TRANSACTIONS_OUTFILE
                                                  where to save the transaction as an inner transaction (default:
                                                  stdout)
  --options OPTIONS                               the transaction options (default: 0)
  --send                                          ✓ whether to broadcast the transaction (default: False)
  --simulate                                      whether to simulate the transaction (default: False)
  --outfile OUTFILE                               where to save the output (signed transaction, hash) (default: stdout)
  --guardian-pem GUARDIAN_PEM                     🔑 the PEM file, if keyfile not provided
  --guardian-pem-index GUARDIAN_PEM_INDEX         🔑 the index in the PEM file (default: 0)
  --guardian-keyfile GUARDIAN_KEYFILE             🔑 a JSON keyfile, if PEM not provided
  --guardian-passfile GUARDIAN_PASSFILE           🔑 a file containing keyfile's password, if keyfile provided
  --guardian-ledger                               🔐 bool flag for signing transaction using ledger
  --guardian-ledger-account-index GUARDIAN_LEDGER_ACCOUNT_INDEX
                                                  🔐 the index of the account when using Ledger
  --guardian-ledger-address-index GUARDIAN_LEDGER_ADDRESS_INDEX
                                                  🔐 the index of the address when using Ledger
  --reward-address REWARD_ADDRESS                 the new reward address

```
### Validator.Claim


```
$ mxpy validator claim --help
usage: mxpy validator claim [-h] ...

Claim rewards

options:
  -h, --help                                      show this help message and exit
  --proxy PROXY                                   🔗 the URL of the proxy
  --pem PEM                                       🔑 the PEM file, if keyfile not provided
  --pem-index PEM_INDEX                           🔑 the index in the PEM file (default: 0)
  --keyfile KEYFILE                               🔑 a JSON keyfile, if PEM not provided
  --passfile PASSFILE                             🔑 a file containing keyfile's password, if keyfile provided
  --ledger                                        🔐 bool flag for signing transaction using ledger
  --ledger-account-index LEDGER_ACCOUNT_INDEX     🔐 the index of the account when using Ledger
  --ledger-address-index LEDGER_ADDRESS_INDEX     🔐 the index of the address when using Ledger
  --sender-username SENDER_USERNAME               🖄 the username of the sender
  --nonce NONCE                                   # the nonce for the transaction
  --recall-nonce                                  ⭮ whether to recall the nonce when creating the transaction (default:
                                                  False)
  --gas-price GAS_PRICE                           ⛽ the gas price (default: 1000000000)
  --gas-limit GAS_LIMIT                           ⛽ the gas limit
  --estimate-gas                                  ⛽ whether to estimate the gas limit (default: 0)
  --value VALUE                                   the value to transfer (default: 0)
  --chain CHAIN                                   the chain identifier
  --version VERSION                               the transaction version (default: 2)
  --guardian GUARDIAN                             the address of the guradian
  --guardian-service-url GUARDIAN_SERVICE_URL     the url of the guardian service
  --guardian-2fa-code GUARDIAN_2FA_CODE           the 2fa code for the guardian
  --relayer RELAYER                               the address of the relayer
  --inner-transactions INNER_TRANSACTIONS         a json file containing the inner transactions; should only be provided
                                                  when creating the relayer's transaction
  --inner-transactions-outfile INNER_TRANSACTIONS_OUTFILE
                                                  where to save the transaction as an inner transaction (default:
                                                  stdout)
  --options OPTIONS                               the transaction options (default: 0)
  --send                                          ✓ whether to broadcast the transaction (default: False)
  --simulate                                      whether to simulate the transaction (default: False)
  --outfile OUTFILE                               where to save the output (signed transaction, hash) (default: stdout)
  --guardian-pem GUARDIAN_PEM                     🔑 the PEM file, if keyfile not provided
  --guardian-pem-index GUARDIAN_PEM_INDEX         🔑 the index in the PEM file (default: 0)
  --guardian-keyfile GUARDIAN_KEYFILE             🔑 a JSON keyfile, if PEM not provided
  --guardian-passfile GUARDIAN_PASSFILE           🔑 a file containing keyfile's password, if keyfile provided
  --guardian-ledger                               🔐 bool flag for signing transaction using ledger
  --guardian-ledger-account-index GUARDIAN_LEDGER_ACCOUNT_INDEX
                                                  🔐 the index of the account when using Ledger
  --guardian-ledger-address-index GUARDIAN_LEDGER_ADDRESS_INDEX
                                                  🔐 the index of the address when using Ledger

```
## Group **StakingProvider**


```
$ mxpy staking-provider --help
usage: mxpy staking-provider COMMAND [-h] ...

Staking provider omnitool

COMMANDS:
  {create-new-delegation-contract,get-contract-address,add-nodes,remove-nodes,stake-nodes,unbond-nodes,unstake-nodes,unjail-nodes,delegate,claim-rewards,redelegate-rewards,undelegate,withdraw,change-service-fee,modify-delegation-cap,automatic-activation,redelegate-cap,set-metadata,make-delegation-contract-from-validator}

OPTIONS:
  -h, --help            show this help message and exit

----------------
COMMANDS summary
----------------
create-new-delegation-contract Create a new delegation system smart contract, transferred value must be greater than baseIssuingCost + min deposit value
get-contract-address           Get create contract address by transaction hash
add-nodes                      Add new nodes must be called by the contract owner
remove-nodes                   Remove nodes must be called by the contract owner
stake-nodes                    Stake nodes must be called by the contract owner
unbond-nodes                   Unbond nodes must be called by the contract owner
unstake-nodes                  Unstake nodes must be called by the contract owner
unjail-nodes                   Unjail nodes must be called by the contract owner
delegate                       Delegate funds to a delegation contract
claim-rewards                  Claim the rewards earned for delegating
redelegate-rewards             Redelegate the rewards earned for delegating
undelegate                     Undelegate funds from a delegation contract
withdraw                       Withdraw funds from a delegation contract
change-service-fee             Change service fee must be called by the contract owner
modify-delegation-cap          Modify delegation cap must be called by the contract owner
automatic-activation           Automatic activation must be called by the contract owner
redelegate-cap                 Redelegate cap must be called by the contract owner
set-metadata                   Set metadata must be called by the contract owner
make-delegation-contract-from-validator Create a delegation contract from validator data. Must be called by the node operator

```
### StakingProvider.CreateNewDelegationContract


```
$ mxpy staking-provider create-new-delegation-contract --help
usage: mxpy staking-provider create-new-delegation-contract [-h] ...

Create a new delegation system smart contract, transferred value must be greater than baseIssuingCost + min deposit value

options:
  -h, --help                                      show this help message and exit
  --proxy PROXY                                   🔗 the URL of the proxy
  --pem PEM                                       🔑 the PEM file, if keyfile not provided
  --pem-index PEM_INDEX                           🔑 the index in the PEM file (default: 0)
  --keyfile KEYFILE                               🔑 a JSON keyfile, if PEM not provided
  --passfile PASSFILE                             🔑 a file containing keyfile's password, if keyfile provided
  --ledger                                        🔐 bool flag for signing transaction using ledger
  --ledger-account-index LEDGER_ACCOUNT_INDEX     🔐 the index of the account when using Ledger
  --ledger-address-index LEDGER_ADDRESS_INDEX     🔐 the index of the address when using Ledger
  --sender-username SENDER_USERNAME               🖄 the username of the sender
  --nonce NONCE                                   # the nonce for the transaction
  --recall-nonce                                  ⭮ whether to recall the nonce when creating the transaction (default:
                                                  False)
  --gas-price GAS_PRICE                           ⛽ the gas price (default: 1000000000)
  --gas-limit GAS_LIMIT                           ⛽ the gas limit
  --estimate-gas                                  ⛽ whether to estimate the gas limit (default: 0)
  --value VALUE                                   the value to transfer (default: 0)
  --chain CHAIN                                   the chain identifier
  --version VERSION                               the transaction version (default: 2)
  --guardian GUARDIAN                             the address of the guradian
  --guardian-service-url GUARDIAN_SERVICE_URL     the url of the guardian service
  --guardian-2fa-code GUARDIAN_2FA_CODE           the 2fa code for the guardian
  --relayer RELAYER                               the address of the relayer
  --inner-transactions INNER_TRANSACTIONS         a json file containing the inner transactions; should only be provided
                                                  when creating the relayer's transaction
  --inner-transactions-outfile INNER_TRANSACTIONS_OUTFILE
                                                  where to save the transaction as an inner transaction (default:
                                                  stdout)
  --options OPTIONS                               the transaction options (default: 0)
  --send                                          ✓ whether to broadcast the transaction (default: False)
  --simulate                                      whether to simulate the transaction (default: False)
  --outfile OUTFILE                               where to save the output (signed transaction, hash) (default: stdout)
  --guardian-pem GUARDIAN_PEM                     🔑 the PEM file, if keyfile not provided
  --guardian-pem-index GUARDIAN_PEM_INDEX         🔑 the index in the PEM file (default: 0)
  --guardian-keyfile GUARDIAN_KEYFILE             🔑 a JSON keyfile, if PEM not provided
  --guardian-passfile GUARDIAN_PASSFILE           🔑 a file containing keyfile's password, if keyfile provided
  --guardian-ledger                               🔐 bool flag for signing transaction using ledger
  --guardian-ledger-account-index GUARDIAN_LEDGER_ACCOUNT_INDEX
                                                  🔐 the index of the account when using Ledger
  --guardian-ledger-address-index GUARDIAN_LEDGER_ADDRESS_INDEX
                                                  🔐 the index of the address when using Ledger
  --total-delegation-cap TOTAL_DELEGATION_CAP     the total delegation contract capacity
  --service-fee SERVICE_FEE                       the delegation contract service fee

```
### StakingProvider.GetContractAddress


```
$ mxpy staking-provider get-contract-address --help
usage: mxpy staking-provider get-contract-address [-h] ...

Get create contract address by transaction hash

options:
  -h, --help                       show this help message and exit
  --create-tx-hash CREATE_TX_HASH  the hash
  --sender SENDER                  the sender address
  --proxy PROXY                    🔗 the URL of the proxy

```
### StakingProvider.AddNodes


```
$ mxpy staking-provider add-nodes --help
usage: mxpy staking-provider add-nodes [-h] ...

Add new nodes must be called by the contract owner

options:
  -h, --help                                      show this help message and exit
  --validators-file VALIDATORS_FILE               a JSON file describing the Nodes
  --delegation-contract DELEGATION_CONTRACT       address of the delegation contract
  --proxy PROXY                                   🔗 the URL of the proxy
  --pem PEM                                       🔑 the PEM file, if keyfile not provided
  --pem-index PEM_INDEX                           🔑 the index in the PEM file (default: 0)
  --keyfile KEYFILE                               🔑 a JSON keyfile, if PEM not provided
  --passfile PASSFILE                             🔑 a file containing keyfile's password, if keyfile provided
  --ledger                                        🔐 bool flag for signing transaction using ledger
  --ledger-account-index LEDGER_ACCOUNT_INDEX     🔐 the index of the account when using Ledger
  --ledger-address-index LEDGER_ADDRESS_INDEX     🔐 the index of the address when using Ledger
  --sender-username SENDER_USERNAME               🖄 the username of the sender
  --nonce NONCE                                   # the nonce for the transaction
  --recall-nonce                                  ⭮ whether to recall the nonce when creating the transaction (default:
                                                  False)
  --gas-price GAS_PRICE                           ⛽ the gas price (default: 1000000000)
  --gas-limit GAS_LIMIT                           ⛽ the gas limit
  --estimate-gas                                  ⛽ whether to estimate the gas limit (default: 0)
  --value VALUE                                   the value to transfer (default: 0)
  --chain CHAIN                                   the chain identifier
  --version VERSION                               the transaction version (default: 2)
  --guardian GUARDIAN                             the address of the guradian
  --guardian-service-url GUARDIAN_SERVICE_URL     the url of the guardian service
  --guardian-2fa-code GUARDIAN_2FA_CODE           the 2fa code for the guardian
  --relayer RELAYER                               the address of the relayer
  --inner-transactions INNER_TRANSACTIONS         a json file containing the inner transactions; should only be provided
                                                  when creating the relayer's transaction
  --inner-transactions-outfile INNER_TRANSACTIONS_OUTFILE
                                                  where to save the transaction as an inner transaction (default:
                                                  stdout)
  --options OPTIONS                               the transaction options (default: 0)
  --send                                          ✓ whether to broadcast the transaction (default: False)
  --simulate                                      whether to simulate the transaction (default: False)
  --outfile OUTFILE                               where to save the output (signed transaction, hash) (default: stdout)
  --guardian-pem GUARDIAN_PEM                     🔑 the PEM file, if keyfile not provided
  --guardian-pem-index GUARDIAN_PEM_INDEX         🔑 the index in the PEM file (default: 0)
  --guardian-keyfile GUARDIAN_KEYFILE             🔑 a JSON keyfile, if PEM not provided
  --guardian-passfile GUARDIAN_PASSFILE           🔑 a file containing keyfile's password, if keyfile provided
  --guardian-ledger                               🔐 bool flag for signing transaction using ledger
  --guardian-ledger-account-index GUARDIAN_LEDGER_ACCOUNT_INDEX
                                                  🔐 the index of the account when using Ledger
  --guardian-ledger-address-index GUARDIAN_LEDGER_ADDRESS_INDEX
                                                  🔐 the index of the address when using Ledger

```
### StakingProvider.RemoveNodes


```
$ mxpy staking-provider remove-nodes --help
usage: mxpy staking-provider remove-nodes [-h] ...

Remove nodes must be called by the contract owner

options:
  -h, --help                                      show this help message and exit
  --bls-keys BLS_KEYS                             a list with the bls keys of the nodes
  --validators-file VALIDATORS_FILE               a JSON file describing the Nodes
  --delegation-contract DELEGATION_CONTRACT       address of the delegation contract
  --proxy PROXY                                   🔗 the URL of the proxy
  --pem PEM                                       🔑 the PEM file, if keyfile not provided
  --pem-index PEM_INDEX                           🔑 the index in the PEM file (default: 0)
  --keyfile KEYFILE                               🔑 a JSON keyfile, if PEM not provided
  --passfile PASSFILE                             🔑 a file containing keyfile's password, if keyfile provided
  --ledger                                        🔐 bool flag for signing transaction using ledger
  --ledger-account-index LEDGER_ACCOUNT_INDEX     🔐 the index of the account when using Ledger
  --ledger-address-index LEDGER_ADDRESS_INDEX     🔐 the index of the address when using Ledger
  --sender-username SENDER_USERNAME               🖄 the username of the sender
  --nonce NONCE                                   # the nonce for the transaction
  --recall-nonce                                  ⭮ whether to recall the nonce when creating the transaction (default:
                                                  False)
  --gas-price GAS_PRICE                           ⛽ the gas price (default: 1000000000)
  --gas-limit GAS_LIMIT                           ⛽ the gas limit
  --estimate-gas                                  ⛽ whether to estimate the gas limit (default: 0)
  --value VALUE                                   the value to transfer (default: 0)
  --chain CHAIN                                   the chain identifier
  --version VERSION                               the transaction version (default: 2)
  --guardian GUARDIAN                             the address of the guradian
  --guardian-service-url GUARDIAN_SERVICE_URL     the url of the guardian service
  --guardian-2fa-code GUARDIAN_2FA_CODE           the 2fa code for the guardian
  --relayer RELAYER                               the address of the relayer
  --inner-transactions INNER_TRANSACTIONS         a json file containing the inner transactions; should only be provided
                                                  when creating the relayer's transaction
  --inner-transactions-outfile INNER_TRANSACTIONS_OUTFILE
                                                  where to save the transaction as an inner transaction (default:
                                                  stdout)
  --options OPTIONS                               the transaction options (default: 0)
  --send                                          ✓ whether to broadcast the transaction (default: False)
  --simulate                                      whether to simulate the transaction (default: False)
  --outfile OUTFILE                               where to save the output (signed transaction, hash) (default: stdout)
  --guardian-pem GUARDIAN_PEM                     🔑 the PEM file, if keyfile not provided
  --guardian-pem-index GUARDIAN_PEM_INDEX         🔑 the index in the PEM file (default: 0)
  --guardian-keyfile GUARDIAN_KEYFILE             🔑 a JSON keyfile, if PEM not provided
  --guardian-passfile GUARDIAN_PASSFILE           🔑 a file containing keyfile's password, if keyfile provided
  --guardian-ledger                               🔐 bool flag for signing transaction using ledger
  --guardian-ledger-account-index GUARDIAN_LEDGER_ACCOUNT_INDEX
                                                  🔐 the index of the account when using Ledger
  --guardian-ledger-address-index GUARDIAN_LEDGER_ADDRESS_INDEX
                                                  🔐 the index of the address when using Ledger

```
### StakingProvider.StakeNodes


```
$ mxpy staking-provider stake-nodes --help
usage: mxpy staking-provider stake-nodes [-h] ...

Stake nodes must be called by the contract owner

options:
  -h, --help                                      show this help message and exit
  --bls-keys BLS_KEYS                             a list with the bls keys of the nodes
  --validators-file VALIDATORS_FILE               a JSON file describing the Nodes
  --delegation-contract DELEGATION_CONTRACT       address of the delegation contract
  --proxy PROXY                                   🔗 the URL of the proxy
  --pem PEM                                       🔑 the PEM file, if keyfile not provided
  --pem-index PEM_INDEX                           🔑 the index in the PEM file (default: 0)
  --keyfile KEYFILE                               🔑 a JSON keyfile, if PEM not provided
  --passfile PASSFILE                             🔑 a file containing keyfile's password, if keyfile provided
  --ledger                                        🔐 bool flag for signing transaction using ledger
  --ledger-account-index LEDGER_ACCOUNT_INDEX     🔐 the index of the account when using Ledger
  --ledger-address-index LEDGER_ADDRESS_INDEX     🔐 the index of the address when using Ledger
  --sender-username SENDER_USERNAME               🖄 the username of the sender
  --nonce NONCE                                   # the nonce for the transaction
  --recall-nonce                                  ⭮ whether to recall the nonce when creating the transaction (default:
                                                  False)
  --gas-price GAS_PRICE                           ⛽ the gas price (default: 1000000000)
  --gas-limit GAS_LIMIT                           ⛽ the gas limit
  --estimate-gas                                  ⛽ whether to estimate the gas limit (default: 0)
  --value VALUE                                   the value to transfer (default: 0)
  --chain CHAIN                                   the chain identifier
  --version VERSION                               the transaction version (default: 2)
  --guardian GUARDIAN                             the address of the guradian
  --guardian-service-url GUARDIAN_SERVICE_URL     the url of the guardian service
  --guardian-2fa-code GUARDIAN_2FA_CODE           the 2fa code for the guardian
  --relayer RELAYER                               the address of the relayer
  --inner-transactions INNER_TRANSACTIONS         a json file containing the inner transactions; should only be provided
                                                  when creating the relayer's transaction
  --inner-transactions-outfile INNER_TRANSACTIONS_OUTFILE
                                                  where to save the transaction as an inner transaction (default:
                                                  stdout)
  --options OPTIONS                               the transaction options (default: 0)
  --send                                          ✓ whether to broadcast the transaction (default: False)
  --simulate                                      whether to simulate the transaction (default: False)
  --outfile OUTFILE                               where to save the output (signed transaction, hash) (default: stdout)
  --guardian-pem GUARDIAN_PEM                     🔑 the PEM file, if keyfile not provided
  --guardian-pem-index GUARDIAN_PEM_INDEX         🔑 the index in the PEM file (default: 0)
  --guardian-keyfile GUARDIAN_KEYFILE             🔑 a JSON keyfile, if PEM not provided
  --guardian-passfile GUARDIAN_PASSFILE           🔑 a file containing keyfile's password, if keyfile provided
  --guardian-ledger                               🔐 bool flag for signing transaction using ledger
  --guardian-ledger-account-index GUARDIAN_LEDGER_ACCOUNT_INDEX
                                                  🔐 the index of the account when using Ledger
  --guardian-ledger-address-index GUARDIAN_LEDGER_ADDRESS_INDEX
                                                  🔐 the index of the address when using Ledger

```
### StakingProvider.UnbondNodes


```
$ mxpy staking-provider unbond-nodes --help
usage: mxpy staking-provider unbond-nodes [-h] ...

Unbond nodes must be called by the contract owner

options:
  -h, --help                                      show this help message and exit
  --bls-keys BLS_KEYS                             a list with the bls keys of the nodes
  --validators-file VALIDATORS_FILE               a JSON file describing the Nodes
  --delegation-contract DELEGATION_CONTRACT       address of the delegation contract
  --proxy PROXY                                   🔗 the URL of the proxy
  --pem PEM                                       🔑 the PEM file, if keyfile not provided
  --pem-index PEM_INDEX                           🔑 the index in the PEM file (default: 0)
  --keyfile KEYFILE                               🔑 a JSON keyfile, if PEM not provided
  --passfile PASSFILE                             🔑 a file containing keyfile's password, if keyfile provided
  --ledger                                        🔐 bool flag for signing transaction using ledger
  --ledger-account-index LEDGER_ACCOUNT_INDEX     🔐 the index of the account when using Ledger
  --ledger-address-index LEDGER_ADDRESS_INDEX     🔐 the index of the address when using Ledger
  --sender-username SENDER_USERNAME               🖄 the username of the sender
  --nonce NONCE                                   # the nonce for the transaction
  --recall-nonce                                  ⭮ whether to recall the nonce when creating the transaction (default:
                                                  False)
  --gas-price GAS_PRICE                           ⛽ the gas price (default: 1000000000)
  --gas-limit GAS_LIMIT                           ⛽ the gas limit
  --estimate-gas                                  ⛽ whether to estimate the gas limit (default: 0)
  --value VALUE                                   the value to transfer (default: 0)
  --chain CHAIN                                   the chain identifier
  --version VERSION                               the transaction version (default: 2)
  --guardian GUARDIAN                             the address of the guradian
  --guardian-service-url GUARDIAN_SERVICE_URL     the url of the guardian service
  --guardian-2fa-code GUARDIAN_2FA_CODE           the 2fa code for the guardian
  --relayer RELAYER                               the address of the relayer
  --inner-transactions INNER_TRANSACTIONS         a json file containing the inner transactions; should only be provided
                                                  when creating the relayer's transaction
  --inner-transactions-outfile INNER_TRANSACTIONS_OUTFILE
                                                  where to save the transaction as an inner transaction (default:
                                                  stdout)
  --options OPTIONS                               the transaction options (default: 0)
  --send                                          ✓ whether to broadcast the transaction (default: False)
  --simulate                                      whether to simulate the transaction (default: False)
  --outfile OUTFILE                               where to save the output (signed transaction, hash) (default: stdout)
  --guardian-pem GUARDIAN_PEM                     🔑 the PEM file, if keyfile not provided
  --guardian-pem-index GUARDIAN_PEM_INDEX         🔑 the index in the PEM file (default: 0)
  --guardian-keyfile GUARDIAN_KEYFILE             🔑 a JSON keyfile, if PEM not provided
  --guardian-passfile GUARDIAN_PASSFILE           🔑 a file containing keyfile's password, if keyfile provided
  --guardian-ledger                               🔐 bool flag for signing transaction using ledger
  --guardian-ledger-account-index GUARDIAN_LEDGER_ACCOUNT_INDEX
                                                  🔐 the index of the account when using Ledger
  --guardian-ledger-address-index GUARDIAN_LEDGER_ADDRESS_INDEX
                                                  🔐 the index of the address when using Ledger

```
### StakingProvider.UnstakeNodes


```
$ mxpy staking-provider unstake-nodes --help
usage: mxpy staking-provider unstake-nodes [-h] ...

Unstake nodes must be called by the contract owner

options:
  -h, --help                                      show this help message and exit
  --bls-keys BLS_KEYS                             a list with the bls keys of the nodes
  --validators-file VALIDATORS_FILE               a JSON file describing the Nodes
  --delegation-contract DELEGATION_CONTRACT       address of the delegation contract
  --proxy PROXY                                   🔗 the URL of the proxy
  --pem PEM                                       🔑 the PEM file, if keyfile not provided
  --pem-index PEM_INDEX                           🔑 the index in the PEM file (default: 0)
  --keyfile KEYFILE                               🔑 a JSON keyfile, if PEM not provided
  --passfile PASSFILE                             🔑 a file containing keyfile's password, if keyfile provided
  --ledger                                        🔐 bool flag for signing transaction using ledger
  --ledger-account-index LEDGER_ACCOUNT_INDEX     🔐 the index of the account when using Ledger
  --ledger-address-index LEDGER_ADDRESS_INDEX     🔐 the index of the address when using Ledger
  --sender-username SENDER_USERNAME               🖄 the username of the sender
  --nonce NONCE                                   # the nonce for the transaction
  --recall-nonce                                  ⭮ whether to recall the nonce when creating the transaction (default:
                                                  False)
  --gas-price GAS_PRICE                           ⛽ the gas price (default: 1000000000)
  --gas-limit GAS_LIMIT                           ⛽ the gas limit
  --estimate-gas                                  ⛽ whether to estimate the gas limit (default: 0)
  --value VALUE                                   the value to transfer (default: 0)
  --chain CHAIN                                   the chain identifier
  --version VERSION                               the transaction version (default: 2)
  --guardian GUARDIAN                             the address of the guradian
  --guardian-service-url GUARDIAN_SERVICE_URL     the url of the guardian service
  --guardian-2fa-code GUARDIAN_2FA_CODE           the 2fa code for the guardian
  --relayer RELAYER                               the address of the relayer
  --inner-transactions INNER_TRANSACTIONS         a json file containing the inner transactions; should only be provided
                                                  when creating the relayer's transaction
  --inner-transactions-outfile INNER_TRANSACTIONS_OUTFILE
                                                  where to save the transaction as an inner transaction (default:
                                                  stdout)
  --options OPTIONS                               the transaction options (default: 0)
  --send                                          ✓ whether to broadcast the transaction (default: False)
  --simulate                                      whether to simulate the transaction (default: False)
  --outfile OUTFILE                               where to save the output (signed transaction, hash) (default: stdout)
  --guardian-pem GUARDIAN_PEM                     🔑 the PEM file, if keyfile not provided
  --guardian-pem-index GUARDIAN_PEM_INDEX         🔑 the index in the PEM file (default: 0)
  --guardian-keyfile GUARDIAN_KEYFILE             🔑 a JSON keyfile, if PEM not provided
  --guardian-passfile GUARDIAN_PASSFILE           🔑 a file containing keyfile's password, if keyfile provided
  --guardian-ledger                               🔐 bool flag for signing transaction using ledger
  --guardian-ledger-account-index GUARDIAN_LEDGER_ACCOUNT_INDEX
                                                  🔐 the index of the account when using Ledger
  --guardian-ledger-address-index GUARDIAN_LEDGER_ADDRESS_INDEX
                                                  🔐 the index of the address when using Ledger

```
### StakingProvider.UnjailNodes


```
$ mxpy staking-provider unjail-nodes --help
usage: mxpy staking-provider unjail-nodes [-h] ...

Unjail nodes must be called by the contract owner

options:
  -h, --help                                      show this help message and exit
  --bls-keys BLS_KEYS                             a list with the bls keys of the nodes
  --validators-file VALIDATORS_FILE               a JSON file describing the Nodes
  --delegation-contract DELEGATION_CONTRACT       address of the delegation contract
  --proxy PROXY                                   🔗 the URL of the proxy
  --pem PEM                                       🔑 the PEM file, if keyfile not provided
  --pem-index PEM_INDEX                           🔑 the index in the PEM file (default: 0)
  --keyfile KEYFILE                               🔑 a JSON keyfile, if PEM not provided
  --passfile PASSFILE                             🔑 a file containing keyfile's password, if keyfile provided
  --ledger                                        🔐 bool flag for signing transaction using ledger
  --ledger-account-index LEDGER_ACCOUNT_INDEX     🔐 the index of the account when using Ledger
  --ledger-address-index LEDGER_ADDRESS_INDEX     🔐 the index of the address when using Ledger
  --sender-username SENDER_USERNAME               🖄 the username of the sender
  --nonce NONCE                                   # the nonce for the transaction
  --recall-nonce                                  ⭮ whether to recall the nonce when creating the transaction (default:
                                                  False)
  --gas-price GAS_PRICE                           ⛽ the gas price (default: 1000000000)
  --gas-limit GAS_LIMIT                           ⛽ the gas limit
  --estimate-gas                                  ⛽ whether to estimate the gas limit (default: 0)
  --value VALUE                                   the value to transfer (default: 0)
  --chain CHAIN                                   the chain identifier
  --version VERSION                               the transaction version (default: 2)
  --guardian GUARDIAN                             the address of the guradian
  --guardian-service-url GUARDIAN_SERVICE_URL     the url of the guardian service
  --guardian-2fa-code GUARDIAN_2FA_CODE           the 2fa code for the guardian
  --relayer RELAYER                               the address of the relayer
  --inner-transactions INNER_TRANSACTIONS         a json file containing the inner transactions; should only be provided
                                                  when creating the relayer's transaction
  --inner-transactions-outfile INNER_TRANSACTIONS_OUTFILE
                                                  where to save the transaction as an inner transaction (default:
                                                  stdout)
  --options OPTIONS                               the transaction options (default: 0)
  --send                                          ✓ whether to broadcast the transaction (default: False)
  --simulate                                      whether to simulate the transaction (default: False)
  --outfile OUTFILE                               where to save the output (signed transaction, hash) (default: stdout)
  --guardian-pem GUARDIAN_PEM                     🔑 the PEM file, if keyfile not provided
  --guardian-pem-index GUARDIAN_PEM_INDEX         🔑 the index in the PEM file (default: 0)
  --guardian-keyfile GUARDIAN_KEYFILE             🔑 a JSON keyfile, if PEM not provided
  --guardian-passfile GUARDIAN_PASSFILE           🔑 a file containing keyfile's password, if keyfile provided
  --guardian-ledger                               🔐 bool flag for signing transaction using ledger
  --guardian-ledger-account-index GUARDIAN_LEDGER_ACCOUNT_INDEX
                                                  🔐 the index of the account when using Ledger
  --guardian-ledger-address-index GUARDIAN_LEDGER_ADDRESS_INDEX
                                                  🔐 the index of the address when using Ledger

```
### StakingProvider.ChangeServiceFee


```
$ mxpy staking-provider change-service-fee --help
usage: mxpy staking-provider change-service-fee [-h] ...

Change service fee must be called by the contract owner

options:
  -h, --help                                      show this help message and exit
  --service-fee SERVICE_FEE                       new service fee value
  --delegation-contract DELEGATION_CONTRACT       address of the delegation contract
  --proxy PROXY                                   🔗 the URL of the proxy
  --pem PEM                                       🔑 the PEM file, if keyfile not provided
  --pem-index PEM_INDEX                           🔑 the index in the PEM file (default: 0)
  --keyfile KEYFILE                               🔑 a JSON keyfile, if PEM not provided
  --passfile PASSFILE                             🔑 a file containing keyfile's password, if keyfile provided
  --ledger                                        🔐 bool flag for signing transaction using ledger
  --ledger-account-index LEDGER_ACCOUNT_INDEX     🔐 the index of the account when using Ledger
  --ledger-address-index LEDGER_ADDRESS_INDEX     🔐 the index of the address when using Ledger
  --sender-username SENDER_USERNAME               🖄 the username of the sender
  --nonce NONCE                                   # the nonce for the transaction
  --recall-nonce                                  ⭮ whether to recall the nonce when creating the transaction (default:
                                                  False)
  --gas-price GAS_PRICE                           ⛽ the gas price (default: 1000000000)
  --gas-limit GAS_LIMIT                           ⛽ the gas limit
  --estimate-gas                                  ⛽ whether to estimate the gas limit (default: 0)
  --value VALUE                                   the value to transfer (default: 0)
  --chain CHAIN                                   the chain identifier
  --version VERSION                               the transaction version (default: 2)
  --guardian GUARDIAN                             the address of the guradian
  --guardian-service-url GUARDIAN_SERVICE_URL     the url of the guardian service
  --guardian-2fa-code GUARDIAN_2FA_CODE           the 2fa code for the guardian
  --relayer RELAYER                               the address of the relayer
  --inner-transactions INNER_TRANSACTIONS         a json file containing the inner transactions; should only be provided
                                                  when creating the relayer's transaction
  --inner-transactions-outfile INNER_TRANSACTIONS_OUTFILE
                                                  where to save the transaction as an inner transaction (default:
                                                  stdout)
  --options OPTIONS                               the transaction options (default: 0)
  --send                                          ✓ whether to broadcast the transaction (default: False)
  --simulate                                      whether to simulate the transaction (default: False)
  --outfile OUTFILE                               where to save the output (signed transaction, hash) (default: stdout)
  --guardian-pem GUARDIAN_PEM                     🔑 the PEM file, if keyfile not provided
  --guardian-pem-index GUARDIAN_PEM_INDEX         🔑 the index in the PEM file (default: 0)
  --guardian-keyfile GUARDIAN_KEYFILE             🔑 a JSON keyfile, if PEM not provided
  --guardian-passfile GUARDIAN_PASSFILE           🔑 a file containing keyfile's password, if keyfile provided
  --guardian-ledger                               🔐 bool flag for signing transaction using ledger
  --guardian-ledger-account-index GUARDIAN_LEDGER_ACCOUNT_INDEX
                                                  🔐 the index of the account when using Ledger
  --guardian-ledger-address-index GUARDIAN_LEDGER_ADDRESS_INDEX
                                                  🔐 the index of the address when using Ledger

```
### StakingProvider.ModifyDelegationCap


```
$ mxpy staking-provider modify-delegation-cap --help
usage: mxpy staking-provider modify-delegation-cap [-h] ...

Modify delegation cap must be called by the contract owner

options:
  -h, --help                                      show this help message and exit
  --delegation-cap DELEGATION_CAP                 new delegation contract capacity
  --delegation-contract DELEGATION_CONTRACT       address of the delegation contract
  --proxy PROXY                                   🔗 the URL of the proxy
  --pem PEM                                       🔑 the PEM file, if keyfile not provided
  --pem-index PEM_INDEX                           🔑 the index in the PEM file (default: 0)
  --keyfile KEYFILE                               🔑 a JSON keyfile, if PEM not provided
  --passfile PASSFILE                             🔑 a file containing keyfile's password, if keyfile provided
  --ledger                                        🔐 bool flag for signing transaction using ledger
  --ledger-account-index LEDGER_ACCOUNT_INDEX     🔐 the index of the account when using Ledger
  --ledger-address-index LEDGER_ADDRESS_INDEX     🔐 the index of the address when using Ledger
  --sender-username SENDER_USERNAME               🖄 the username of the sender
  --nonce NONCE                                   # the nonce for the transaction
  --recall-nonce                                  ⭮ whether to recall the nonce when creating the transaction (default:
                                                  False)
  --gas-price GAS_PRICE                           ⛽ the gas price (default: 1000000000)
  --gas-limit GAS_LIMIT                           ⛽ the gas limit
  --estimate-gas                                  ⛽ whether to estimate the gas limit (default: 0)
  --value VALUE                                   the value to transfer (default: 0)
  --chain CHAIN                                   the chain identifier
  --version VERSION                               the transaction version (default: 2)
  --guardian GUARDIAN                             the address of the guradian
  --guardian-service-url GUARDIAN_SERVICE_URL     the url of the guardian service
  --guardian-2fa-code GUARDIAN_2FA_CODE           the 2fa code for the guardian
  --relayer RELAYER                               the address of the relayer
  --inner-transactions INNER_TRANSACTIONS         a json file containing the inner transactions; should only be provided
                                                  when creating the relayer's transaction
  --inner-transactions-outfile INNER_TRANSACTIONS_OUTFILE
                                                  where to save the transaction as an inner transaction (default:
                                                  stdout)
  --options OPTIONS                               the transaction options (default: 0)
  --send                                          ✓ whether to broadcast the transaction (default: False)
  --simulate                                      whether to simulate the transaction (default: False)
  --outfile OUTFILE                               where to save the output (signed transaction, hash) (default: stdout)
  --guardian-pem GUARDIAN_PEM                     🔑 the PEM file, if keyfile not provided
  --guardian-pem-index GUARDIAN_PEM_INDEX         🔑 the index in the PEM file (default: 0)
  --guardian-keyfile GUARDIAN_KEYFILE             🔑 a JSON keyfile, if PEM not provided
  --guardian-passfile GUARDIAN_PASSFILE           🔑 a file containing keyfile's password, if keyfile provided
  --guardian-ledger                               🔐 bool flag for signing transaction using ledger
  --guardian-ledger-account-index GUARDIAN_LEDGER_ACCOUNT_INDEX
                                                  🔐 the index of the account when using Ledger
  --guardian-ledger-address-index GUARDIAN_LEDGER_ADDRESS_INDEX
                                                  🔐 the index of the address when using Ledger

```
### StakingProvider.AutomaticActivation


```
$ mxpy staking-provider automatic-activation --help
usage: mxpy staking-provider automatic-activation [-h] ...

Automatic activation must be called by the contract owner

options:
  -h, --help                                      show this help message and exit
  --set                                           set automatic activation True
  --unset                                         set automatic activation False
  --delegation-contract DELEGATION_CONTRACT       address of the delegation contract
  --proxy PROXY                                   🔗 the URL of the proxy
  --pem PEM                                       🔑 the PEM file, if keyfile not provided
  --pem-index PEM_INDEX                           🔑 the index in the PEM file (default: 0)
  --keyfile KEYFILE                               🔑 a JSON keyfile, if PEM not provided
  --passfile PASSFILE                             🔑 a file containing keyfile's password, if keyfile provided
  --ledger                                        🔐 bool flag for signing transaction using ledger
  --ledger-account-index LEDGER_ACCOUNT_INDEX     🔐 the index of the account when using Ledger
  --ledger-address-index LEDGER_ADDRESS_INDEX     🔐 the index of the address when using Ledger
  --sender-username SENDER_USERNAME               🖄 the username of the sender
  --nonce NONCE                                   # the nonce for the transaction
  --recall-nonce                                  ⭮ whether to recall the nonce when creating the transaction (default:
                                                  False)
  --gas-price GAS_PRICE                           ⛽ the gas price (default: 1000000000)
  --gas-limit GAS_LIMIT                           ⛽ the gas limit
  --estimate-gas                                  ⛽ whether to estimate the gas limit (default: 0)
  --value VALUE                                   the value to transfer (default: 0)
  --chain CHAIN                                   the chain identifier
  --version VERSION                               the transaction version (default: 2)
  --guardian GUARDIAN                             the address of the guradian
  --guardian-service-url GUARDIAN_SERVICE_URL     the url of the guardian service
  --guardian-2fa-code GUARDIAN_2FA_CODE           the 2fa code for the guardian
  --relayer RELAYER                               the address of the relayer
  --inner-transactions INNER_TRANSACTIONS         a json file containing the inner transactions; should only be provided
                                                  when creating the relayer's transaction
  --inner-transactions-outfile INNER_TRANSACTIONS_OUTFILE
                                                  where to save the transaction as an inner transaction (default:
                                                  stdout)
  --options OPTIONS                               the transaction options (default: 0)
  --send                                          ✓ whether to broadcast the transaction (default: False)
  --simulate                                      whether to simulate the transaction (default: False)
  --outfile OUTFILE                               where to save the output (signed transaction, hash) (default: stdout)
  --guardian-pem GUARDIAN_PEM                     🔑 the PEM file, if keyfile not provided
  --guardian-pem-index GUARDIAN_PEM_INDEX         🔑 the index in the PEM file (default: 0)
  --guardian-keyfile GUARDIAN_KEYFILE             🔑 a JSON keyfile, if PEM not provided
  --guardian-passfile GUARDIAN_PASSFILE           🔑 a file containing keyfile's password, if keyfile provided
  --guardian-ledger                               🔐 bool flag for signing transaction using ledger
  --guardian-ledger-account-index GUARDIAN_LEDGER_ACCOUNT_INDEX
                                                  🔐 the index of the account when using Ledger
  --guardian-ledger-address-index GUARDIAN_LEDGER_ADDRESS_INDEX
                                                  🔐 the index of the address when using Ledger

```
### StakingProvider.RedelegateCap


```
$ mxpy staking-provider redelegate-cap --help
usage: mxpy staking-provider redelegate-cap [-h] ...

Redelegate cap must be called by the contract owner

options:
  -h, --help                                      show this help message and exit
  --set                                           set redelegate cap True
  --unset                                         set redelegate cap False
  --delegation-contract DELEGATION_CONTRACT       address of the delegation contract
  --proxy PROXY                                   🔗 the URL of the proxy
  --pem PEM                                       🔑 the PEM file, if keyfile not provided
  --pem-index PEM_INDEX                           🔑 the index in the PEM file (default: 0)
  --keyfile KEYFILE                               🔑 a JSON keyfile, if PEM not provided
  --passfile PASSFILE                             🔑 a file containing keyfile's password, if keyfile provided
  --ledger                                        🔐 bool flag for signing transaction using ledger
  --ledger-account-index LEDGER_ACCOUNT_INDEX     🔐 the index of the account when using Ledger
  --ledger-address-index LEDGER_ADDRESS_INDEX     🔐 the index of the address when using Ledger
  --sender-username SENDER_USERNAME               🖄 the username of the sender
  --nonce NONCE                                   # the nonce for the transaction
  --recall-nonce                                  ⭮ whether to recall the nonce when creating the transaction (default:
                                                  False)
  --gas-price GAS_PRICE                           ⛽ the gas price (default: 1000000000)
  --gas-limit GAS_LIMIT                           ⛽ the gas limit
  --estimate-gas                                  ⛽ whether to estimate the gas limit (default: 0)
  --value VALUE                                   the value to transfer (default: 0)
  --chain CHAIN                                   the chain identifier
  --version VERSION                               the transaction version (default: 2)
  --guardian GUARDIAN                             the address of the guradian
  --guardian-service-url GUARDIAN_SERVICE_URL     the url of the guardian service
  --guardian-2fa-code GUARDIAN_2FA_CODE           the 2fa code for the guardian
  --relayer RELAYER                               the address of the relayer
  --inner-transactions INNER_TRANSACTIONS         a json file containing the inner transactions; should only be provided
                                                  when creating the relayer's transaction
  --inner-transactions-outfile INNER_TRANSACTIONS_OUTFILE
                                                  where to save the transaction as an inner transaction (default:
                                                  stdout)
  --options OPTIONS                               the transaction options (default: 0)
  --send                                          ✓ whether to broadcast the transaction (default: False)
  --simulate                                      whether to simulate the transaction (default: False)
  --outfile OUTFILE                               where to save the output (signed transaction, hash) (default: stdout)
  --guardian-pem GUARDIAN_PEM                     🔑 the PEM file, if keyfile not provided
  --guardian-pem-index GUARDIAN_PEM_INDEX         🔑 the index in the PEM file (default: 0)
  --guardian-keyfile GUARDIAN_KEYFILE             🔑 a JSON keyfile, if PEM not provided
  --guardian-passfile GUARDIAN_PASSFILE           🔑 a file containing keyfile's password, if keyfile provided
  --guardian-ledger                               🔐 bool flag for signing transaction using ledger
  --guardian-ledger-account-index GUARDIAN_LEDGER_ACCOUNT_INDEX
                                                  🔐 the index of the account when using Ledger
  --guardian-ledger-address-index GUARDIAN_LEDGER_ADDRESS_INDEX
                                                  🔐 the index of the address when using Ledger

```
### StakingProvider.SetMetadata


```
$ mxpy staking-provider set-metadata --help
usage: mxpy staking-provider set-metadata [-h] ...

Set metadata must be called by the contract owner

options:
  -h, --help                                      show this help message and exit
  --name NAME                                     name field in staking provider metadata
  --website WEBSITE                               website field in staking provider metadata
  --identifier IDENTIFIER                         identifier field in staking provider metadata
  --delegation-contract DELEGATION_CONTRACT       address of the delegation contract
  --proxy PROXY                                   🔗 the URL of the proxy
  --pem PEM                                       🔑 the PEM file, if keyfile not provided
  --pem-index PEM_INDEX                           🔑 the index in the PEM file (default: 0)
  --keyfile KEYFILE                               🔑 a JSON keyfile, if PEM not provided
  --passfile PASSFILE                             🔑 a file containing keyfile's password, if keyfile provided
  --ledger                                        🔐 bool flag for signing transaction using ledger
  --ledger-account-index LEDGER_ACCOUNT_INDEX     🔐 the index of the account when using Ledger
  --ledger-address-index LEDGER_ADDRESS_INDEX     🔐 the index of the address when using Ledger
  --sender-username SENDER_USERNAME               🖄 the username of the sender
  --nonce NONCE                                   # the nonce for the transaction
  --recall-nonce                                  ⭮ whether to recall the nonce when creating the transaction (default:
                                                  False)
  --gas-price GAS_PRICE                           ⛽ the gas price (default: 1000000000)
  --gas-limit GAS_LIMIT                           ⛽ the gas limit
  --estimate-gas                                  ⛽ whether to estimate the gas limit (default: 0)
  --value VALUE                                   the value to transfer (default: 0)
  --chain CHAIN                                   the chain identifier
  --version VERSION                               the transaction version (default: 2)
  --guardian GUARDIAN                             the address of the guradian
  --guardian-service-url GUARDIAN_SERVICE_URL     the url of the guardian service
  --guardian-2fa-code GUARDIAN_2FA_CODE           the 2fa code for the guardian
  --relayer RELAYER                               the address of the relayer
  --inner-transactions INNER_TRANSACTIONS         a json file containing the inner transactions; should only be provided
                                                  when creating the relayer's transaction
  --inner-transactions-outfile INNER_TRANSACTIONS_OUTFILE
                                                  where to save the transaction as an inner transaction (default:
                                                  stdout)
  --options OPTIONS                               the transaction options (default: 0)
  --send                                          ✓ whether to broadcast the transaction (default: False)
  --simulate                                      whether to simulate the transaction (default: False)
  --outfile OUTFILE                               where to save the output (signed transaction, hash) (default: stdout)
  --guardian-pem GUARDIAN_PEM                     🔑 the PEM file, if keyfile not provided
  --guardian-pem-index GUARDIAN_PEM_INDEX         🔑 the index in the PEM file (default: 0)
  --guardian-keyfile GUARDIAN_KEYFILE             🔑 a JSON keyfile, if PEM not provided
  --guardian-passfile GUARDIAN_PASSFILE           🔑 a file containing keyfile's password, if keyfile provided
  --guardian-ledger                               🔐 bool flag for signing transaction using ledger
  --guardian-ledger-account-index GUARDIAN_LEDGER_ACCOUNT_INDEX
                                                  🔐 the index of the account when using Ledger
  --guardian-ledger-address-index GUARDIAN_LEDGER_ADDRESS_INDEX
                                                  🔐 the index of the address when using Ledger

```
## Group **Account**


```
$ mxpy account --help
usage: mxpy account COMMAND [-h] ...

Get Account data (nonce, balance) from the Network

COMMANDS:
  {get}

OPTIONS:
  -h, --help  show this help message and exit

----------------
COMMANDS summary
----------------
get                            Query account details (nonce, balance etc.)

```
### Account.Get


```
$ mxpy account get --help
usage: mxpy account get [-h] ...

Query account details (nonce, balance etc.)

options:
  -h, --help                 show this help message and exit
  --proxy PROXY              🔗 the URL of the proxy
  --address ADDRESS          🖄 the address to query
  --balance                  whether to only fetch the balance
  --nonce                    whether to only fetch the nonce
  --username                 whether to only fetch the username
  --omit-fields OMIT_FIELDS  omit fields in the output payload (default: [])

```
## Group **Wallet**


```
$ mxpy wallet --help
usage: mxpy wallet COMMAND [-h] ...

Create wallet, derive secret key from mnemonic, bech32 address helpers etc.

COMMANDS:
  {new,convert,bech32,sign-message,verify-message}

OPTIONS:
  -h, --help            show this help message and exit

----------------
COMMANDS summary
----------------
new                            Create a new wallet and print its mnemonic; optionally save as password-protected JSON (recommended) or PEM (not recommended)
convert                        Convert a wallet from one format to another
bech32                         Helper for encoding and decoding bech32 addresses
sign-message                   Sign a message
verify-message                 Verify a previously signed message

```
### Wallet.New


```
$ mxpy wallet new --help
usage: mxpy wallet new [-h] ...

Create a new wallet and print its mnemonic; optionally save as password-protected JSON (recommended) or PEM (not recommended)

options:
  -h, --help                                      show this help message and exit
  --format {raw-mnemonic,keystore-mnemonic,keystore-secret-key,pem}
                                                  the format of the generated wallet file (default: None)
  --outfile OUTFILE                               the output path and base file name for the generated wallet files
                                                  (default: None)
  --address-hrp ADDRESS_HRP                       the human-readable part of the address, when format is keystore-
                                                  secret-key or pem (default: erd)
  --shard SHARD                                   the shard in which the address will be generated; (default: random)

```
### Wallet.Convert


```
$ mxpy wallet convert --help
usage: mxpy wallet convert [-h] ...

Convert a wallet from one format to another

options:
  -h, --help                                      show this help message and exit
  --infile INFILE                                 path to the input file
  --outfile OUTFILE                               path to the output file
  --in-format {raw-mnemonic,keystore-mnemonic,keystore-secret-key,pem}
                                                  the format of the input file
  --out-format {raw-mnemonic,keystore-mnemonic,keystore-secret-key,pem,address-bech32,address-hex}
                                                  the format of the output file
  --address-index ADDRESS_INDEX                   the address index, if input format is raw-mnemonic, keystore-mnemonic
                                                  or pem (with multiple entries) and the output format is keystore-
                                                  secret-key or pem
  --address-hrp ADDRESS_HRP                       the human-readable part of the address, when the output format is
                                                  keystore-secret-key or pem (default: erd)

```
### Wallet.Bech32


```
$ mxpy wallet bech32 --help
usage: mxpy wallet bech32 [-h] ...

Helper for encoding and decoding bech32 addresses

positional arguments:
  value       the value to encode or decode

options:
  -h, --help  show this help message and exit
  --encode    whether to encode
  --decode    whether to decode

```
### Wallet.SignMessage


```
$ mxpy wallet sign-message --help
usage: mxpy wallet sign-message [-h] ...

Sign a message

options:
  -h, --help                                   show this help message and exit
  --message MESSAGE                            the message you want to sign
  --pem PEM                                    🔑 the PEM file, if keyfile not provided
  --pem-index PEM_INDEX                        🔑 the index in the PEM file (default: 0)
  --keyfile KEYFILE                            🔑 a JSON keyfile, if PEM not provided
  --passfile PASSFILE                          🔑 a file containing keyfile's password, if keyfile provided
  --ledger                                     🔐 bool flag for signing transaction using ledger
  --ledger-account-index LEDGER_ACCOUNT_INDEX  🔐 the index of the account when using Ledger
  --ledger-address-index LEDGER_ADDRESS_INDEX  🔐 the index of the address when using Ledger
  --sender-username SENDER_USERNAME            🖄 the username of the sender

```
### Wallet.VerifyMessage


```
$ mxpy wallet verify-message --help
usage: mxpy wallet verify-message [-h] ...

Verify a previously signed message

options:
  -h, --help             show this help message and exit
  --address ADDRESS      the bech32 address of the signer
  --message MESSAGE      the previously signed message(readable text, as it was signed)
  --signature SIGNATURE  the signature in hex format

```
## Group **Localnet**


```
$ mxpy localnet --help
usage: mxpy localnet COMMAND [-h] ...

Set up, start and control localnets

COMMANDS:
  {setup,new,prerequisites,build,start,config,clean}

OPTIONS:
  -h, --help            show this help message and exit

```
### Localnet.Setup


```
$ mxpy localnet setup --help
usage: mxpy localnet setup [-h] ...

Set up a localnet (runs 'prerequisites', 'build' and 'config' in one go)

options:
  -h, --help               show this help message and exit
  --configfile CONFIGFILE  An optional configuration file describing the localnet

```
### Localnet.New


```
$ mxpy localnet new --help
usage: mxpy localnet new [-h] ...

Create a new localnet configuration

options:
  -h, --help               show this help message and exit
  --configfile CONFIGFILE  An optional configuration file describing the localnet

```
### Localnet.Prerequisites


```
$ mxpy localnet prerequisites --help
usage: mxpy localnet prerequisites [-h] ...

Download and verify the prerequisites for running a localnet

options:
  -h, --help               show this help message and exit
  --configfile CONFIGFILE  An optional configuration file describing the localnet

```
### Localnet.Build


```
$ mxpy localnet build --help
usage: mxpy localnet build [-h] ...

Build necessary software for running a localnet

options:
  -h, --help                                      show this help message and exit
  --configfile CONFIGFILE                         An optional configuration file describing the localnet
  --software {node,seednode,proxy} [{node,seednode,proxy} ...]
                                                  The software to build (default: ['node', 'seednode', 'proxy'])

```
### Localnet.Config


```
$ mxpy localnet config --help
usage: mxpy localnet config [-h] ...

Configure a localnet (required before starting it the first time or after clean)

options:
  -h, --help               show this help message and exit
  --configfile CONFIGFILE  An optional configuration file describing the localnet

```
### Localnet.Start


```
$ mxpy localnet start --help
usage: mxpy localnet start [-h] ...

Start a localnet

options:
  -h, --help                               show this help message and exit
  --configfile CONFIGFILE                  An optional configuration file describing the localnet
  --stop-after-seconds STOP_AFTER_SECONDS  Stop the localnet after a given number of seconds (default: 31536000)

```
### Localnet.Clean


```
$ mxpy localnet clean --help
usage: mxpy localnet clean [-h] ...

Erase the currently configured localnet (must be already stopped)

options:
  -h, --help               show this help message and exit
  --configfile CONFIGFILE  An optional configuration file describing the localnet

```
## Group **Dependencies**


```
$ mxpy deps --help
usage: mxpy deps COMMAND [-h] ...

Manage dependencies or multiversx-sdk modules

COMMANDS:
  {install,check}

OPTIONS:
  -h, --help       show this help message and exit

----------------
COMMANDS summary
----------------
install                        Install dependencies or multiversx-sdk modules.
check                          Check whether a dependency is installed.

```
### Dependencies.Install


```
$ mxpy deps install --help
usage: mxpy deps install [-h] ...

Install dependencies or multiversx-sdk modules.

positional arguments:
  {all,rust,golang,testwallets}  the dependency to install

options:
  -h, --help                     show this help message and exit
  --overwrite                    whether to overwrite an existing installation

```
### Dependencies.Check


```
$ mxpy deps check --help
usage: mxpy deps check [-h] ...

Check whether a dependency is installed.

positional arguments:
  {all,rust,golang,testwallets}  the dependency to check

options:
  -h, --help                     show this help message and exit

```
## Group **Configuration**


```
$ mxpy config --help
usage: mxpy config COMMAND [-h] ...

Configure multiversx-sdk (default values etc.)

COMMANDS:
  {dump,get,set,delete,new,switch,list,reset}

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
reset                          Deletes the config file. Default config will be used.

```
### Configuration.Dump


```
$ mxpy config dump --help
usage: mxpy config dump [-h] ...

Dumps configuration.

options:
  -h, --help  show this help message and exit
  --defaults  dump defaults instead of local config

```
### Configuration.Get


```
$ mxpy config get --help
usage: mxpy config get [-h] ...

Gets a configuration value.

positional arguments:
  name        the name of the configuration entry

options:
  -h, --help  show this help message and exit

```
### Configuration.Set


```
$ mxpy config set --help
usage: mxpy config set [-h] ...

Sets a configuration value.

positional arguments:
  name        the name of the configuration entry
  value       the new value

options:
  -h, --help  show this help message and exit

```
### Configuration.New


```
$ mxpy config new --help
usage: mxpy config new [-h] ...

Creates a new configuration.

positional arguments:
  name                 the name of the configuration entry

options:
  -h, --help           show this help message and exit
  --template TEMPLATE  template from which to create the new config

```
### Configuration.Switch


```
$ mxpy config switch --help
usage: mxpy config switch [-h] ...

Switch to a different config

positional arguments:
  name        the name of the configuration entry

options:
  -h, --help  show this help message and exit

```
### Configuration.List


```
$ mxpy config list --help
usage: mxpy config list [-h] ...

List available configs

options:
  -h, --help  show this help message and exit

```
### Configuration.Reset


```
$ mxpy config reset --help
usage: mxpy config reset [-h] ...

Deletes the config file. Default config will be used.

options:
  -h, --help  show this help message and exit

```
## Group **Data**


```
$ mxpy data --help
usage: mxpy data COMMAND [-h] ...

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
$ mxpy data parse --help
usage: mxpy data parse [-h] ...

Parses values from a given file

options:
  -h, --help               show this help message and exit
  --file FILE              path of the file to parse
  --expression EXPRESSION  the Python-Dictionary expression to evaluate in order to extract the data

```
### Data.Store


```
$ mxpy data store --help
usage: mxpy data store [-h] ...

Stores a key-value pair within a partition

options:
  -h, --help             show this help message and exit
  --key KEY              the key
  --value VALUE          the value to save
  --partition PARTITION  the storage partition (default: *)
  --use-global           use the global storage (default: False)

```
### Data.Load


```
$ mxpy data load --help
usage: mxpy data load [-h] ...

Loads a key-value pair from a storage partition

options:
  -h, --help             show this help message and exit
  --key KEY              the key
  --partition PARTITION  the storage partition (default: *)
  --use-global           use the global storage (default: False)

```
## Group **Faucet**


```
$ mxpy faucet --help
usage: mxpy faucet COMMAND [-h] ...

Get xEGLD on Devnet or Testnet

COMMANDS:
  {request}

OPTIONS:
  -h, --help  show this help message and exit

----------------
COMMANDS summary
----------------
request                        Request xEGLD.

```
### Faucet.Request


```
$ mxpy faucet request --help
usage: mxpy faucet request [-h] ...

Request xEGLD.

options:
  -h, --help                                   show this help message and exit
  --pem PEM                                    🔑 the PEM file, if keyfile not provided
  --pem-index PEM_INDEX                        🔑 the index in the PEM file (default: 0)
  --keyfile KEYFILE                            🔑 a JSON keyfile, if PEM not provided
  --passfile PASSFILE                          🔑 a file containing keyfile's password, if keyfile provided
  --ledger                                     🔐 bool flag for signing transaction using ledger
  --ledger-account-index LEDGER_ACCOUNT_INDEX  🔐 the index of the account when using Ledger
  --ledger-address-index LEDGER_ADDRESS_INDEX  🔐 the index of the address when using Ledger
  --sender-username SENDER_USERNAME            🖄 the username of the sender
  --chain CHAIN                                the chain identifier

```
