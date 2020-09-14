# Change Log

All notable changes will be documented in this file.

Check [Keep a Changelog](http://keepachangelog.com/) for recommendations on how to structure this file.

## [0.8.4] - 14.09.2020
 - Fix templates patching to work with elrond-wasm `0.6.0`.
 - Update build with respect to elrond-wasm `0.6.0`.
 - Update reference to newest Mandos `v0.3.35`, update tests runner.
 - Remove dependency on `list_api.txt` for C projects.
 - Trim whitespace for "wallet derive --mnemonic".

## [0.8.3] - 12.08.2020
 - Fix proxy requests, implement `hyperblock` route.

## [0.8.2] - 06.08.2020
 - Strip password for keyfile (remove left & right spaces, newlines)
 - Allow one to specify path to WASM (bytecode) for `contract deploy` and `contract upgrade`
 - Update reference to Arwen Tools
 - Allow sending SC transactions in offline mode (`--send` defaults to `false`).
 - Allow multi-pem files (selection via `--pem-index` parameter).


## [0.8.1] - 29.07.2020

 - Add SDK helpers to generate relayed transactions.

## [0.8.0] - 26.07.2020

 - Updated signing procedure with respect to the `data` field (which is now base64-encoded)
 - Redesigned the CLI for `validator stake`
 - Refactoring and design improvements


**Note that below, the change log is in chronological order. Will be soon updated to be in inverse chronological order (how it should have been in the first place).**

## [0.0.4]

- Initial release

## [0.0.5]

### Fixed

- Include **psutil** in the list of dependencies in `setup.py`.
- Handle missing / `none` arguments at deploy.
- Default to current directory in `build` command.
- Allow paths starting with `~` when specifying PEM.
- Forward gas limit, gas price parameters correctly.

### Changed

- Improve example for testnet to allow query after deploy.

## [0.0.6]

### Fixed

- Default to current directory in `build` command.

## [0.0.7]

### Added

- Enabled test runner: `erdpy test --wildcard='*'`

## [0.0.8]

### Fixed

- Set `LD_LIBRARY_PATH` before executing `nodedebug` and `testrunner`.

## [0.0.9]

### Fixed

- Fixed passing environment variables to test runner.

## [0.1.0]

### Fixed

- Fixed node-debug stdout & stderr decode.

### Other

- Updated reference to node-debug.
- SOLL migration in progress (Solidity build does not work yet).

## [0.1.1]

### Fixed

- Fixed Solidity / SOLL buildchain.

## [0.1.2]

### Fixed

- Default to current directory for `erdpy deploy`.

## [0.1.3]

### Fixed

- Fix passing arguments for command `erdpy call`.

## [0.1.4]

### Fixed

- Fix passing arguments for command `erdpy query`.

## [0.1.5]

### Fixed

- For MacOS `chmod +x` upon downloading SOLL, nodedebug.

## [0.1.6]

### Fixed

- Downloads performed using `requests` module (certificate errors on MacOS otherwise).

## [0.1.7]

### Fixed

- Node-debug build for MacOS.

### Other

- Updated reference to node-debug.

## [0.1.9]

### Fixed

- Transaction signing - updated to **Ed25519**
- Removed **node-debug** from the testnet flows (deployment and execution of smart contracts)
- Fixed contract project generation from Rust templates
- Minor fixes on the build flow.

### Other

- Temporarily disabled node-debug interaction (node-debug's place will be soon taken by a debug version of Arwen VM)
- Added extra command to prepare and send transactions against the testnet
- Added extra examples.

## [0.2.0]

### Fixed

- Fixed getting metrics from testnet.

### Other

- Temporarily disabled transaction costs estimators.

## [0.2.1]

### Fixed

- Fixed reference to pycryptodomex.

## [0.2.2]

### Fixed

- Fixed (improved) handling of proxy request errors.

## [0.2.3]

### Fixed

- Fixed CPP compilation support.

## [0.2.4]

### Fixed

- Dependency to psutils.

### Added

- Extra CLI command to prepare and send transaction.

## [0.2.5]

### Fixed

- Format of "transaction.data" field.


## [0.2.6]

### Fixed

- Upgradeable smart contracts.

## [0.2.7]

### Other

- Implement bech32 addresses.

## [0.2.8]

### Fixed

- Fixed calls to estimators.

## [0.2.9]

### Fixed

- Adjust reference to the new JSON testing tool.
- Other minor fixes.

## [0.3.0]

### Fixed

- Fix path to WASM binary (for rust projects).
- Fix build of rust projects (trim size of artifact).

## [0.3.1], [0.3.2]

### Fixed

- Fix path to contract binary within JSON tests.
- Fix templates download by deleting the "templates" folder at first.

## [0.3.3]

### Fixed

- Display address of smart contract upon deploy
- Improve tests CLI
- Copy build artifacts to "output" folder

## [0.3.4]

### Fixed

- Extra exported function for C builds

## [0.3.5]

### Features

- Stake, UnStake, UnBound, UnJail, ChangeRewardAddress

## [0.3.6]

### Fixed

- Extra exported function for C builds

## [0.3.7]

### Fixed

- Serialization algorithm used for signing ("data as string")
- Prettier CLI

## [0.3.8]

### Fixed

- Long description for setup (temporary workaround).

## [0.3.9]

### Fixed

- Add `claim` function for validators

## [0.4.0]

### Fixed

- Fixed action of CLI / network.

## [0.4.1]

## [0.4.2]

### Fixed

- Fixed passing arguments for stake.

## [0.4.3]

### Features

- First implementation of the transactions dispatcher.

## [0.4.4]

### Features

- Fix packaging.


## [0.4.5]

### Features

- Fix gas estimators for staking.
- Add mnemonic to PEM converter.


## [0.4.6]

### Fixed

- Fixed `new` command (default directory).
- Improved `deploy` command (add parameter `outfile`).

## [0.4.7]

### Fixed

- Mark `gas-limit` field as required.

## [0.4.8]

### Fixed

- Update reference to `mandos`, fix templating for tests.


## [0.4.9] - 24.06.2020

### Fixed

- Improved CLI for contracts (added CLI group of actions)
- Fixed response handling for `send-multiple`

## [0.5.0] - 25.06.2020

### Fixed

- Fixed list of `elrondei` functions.

## [0.5.1] - 25.06.2020

### Fixed

- Fix passing `--nonce` argument to validator commands.
- Add flag `--recall-nonce`, as an alternative to specifying the `--nonce=42`.

### Other

- Deprecated commands `stake-prepare` and `stake-send`. Will be replaced soon by `stake --prepare` and `tx send`.

## [0.7.0] - 13.07.2022

 - Redesigned CLI for creating and broadcasting transactions (`erdpy tx`).
 - Included `chainID` and `version` in transactions (erdpy, erdjs), updated signature accordingly.
 - Allow provisioning of wallet JSON **key-file** as well, in addition to PEM files (which will be deprecated). Many thanks to [flyingbasalt](https://github.com/flyingbasalt/erdkeys).
 - Redesign `erdpy-up` to use light Python virtual environments (`venv`).
 - Allow options `--no-modiy-path` and `--exact-version` in `erdpy-up`
 - Renamed some CLI commands (for `wallet`, for `tx`).
 - Cleanup templating logic for Smart Contracts - moved some features to Elrond IDE.
 - erdtestjs fixes and design improvements / refactoring.
 - Completely redesigned dependency management (`erdpy deps`), improved associated CLI.
 - Refactor and group (under `erdpy group`) validator-related commands.
 - Improved CLI help, added descriptions.
 - Do not receive mnemonic as parameter in `erdpy wallet derive`, but ask for user input instead.
 - Add Clean command for Smart Contract projects.
 - Create symlinks for `arwentools` binaries.
 - Updated references to `arwentools` components (Mandos, Arwen Debug).
 - Added CLI group `erdpy config`, which manages `~/elrondsdk/elrond.json`.
 - Deprecated `~/ElrondSCTools`, which will be removed by `erdpy-up`. The new installation folder is `~/elrondsdk`.
 - Require Python 3.8 on MacOS.
 - Smart Contracts `query` - return as base64, hex, number.
 - Require nonce for SC `deploy` & `call`.
 - Removed .py SC interaction samples, moved to `sc-examples` `sc-examples-rs` repositories, so that they become available in Elrond IDE.
 - Removed some deprecated code.
 - `mypy`-related refactoring.
 - Fix accounts CLI. Trucate data for "account get-transactions"

## [0.7.1] - 13.07.2020

### Fixed

 - Installation of `rust` (was broken upon refactoring).
 - Re-added command `erdpy contract test`.
 - Throw error when bad input for `erdpy validator ...`.

## [0.7.2] - 13.07.2020

### Fixed

 - Fixed call to `BunchOfTransactions`.
