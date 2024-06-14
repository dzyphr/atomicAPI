 # Atomic API _ Test


#### Python Based Low Level API for Encryped Cross-Chain Atomic Swaps



## NOTE: Project is in Alpha / Testnet Phase 
## Actively Seeking Contributions and Feedback

## Atomic Swap Implementation Details

* Pedersen + Schnorr Atomic Swaps 
  - Formula Described here: [Grin Docs](https://github.com/mimblewimble/grin/blob/master/doc/contracts.md#atomic-swap)
  - Ergo Atomic Schnorr Contract: [Atomic Schnorr ErgoScript](https://github.com/dzyphr/atomicAPI/blob/main/Ergo/SigmaParticle/AtomicMultiSig/py/main.py#L74)
  - Solidity Atomic Scalar Contract: [Atomic Scalar Solidity](https://github.com/dzyphr/atomicAPI/blob/main/EVM/Atomicity/AtomicMultiSigSecp256k1/contracts/AtomicMultiSigSecp256k1.sol)



## Key Features

* Generalized Atomic Swap Function Endpoints
  - Commit initiations
  - Finalize swaps 
  - Claim atomic swaps from derived secrets
  - Response commitments
  - Claim from finalization commitments
* Functional Testing Scripts
  - Test Atomic Swaps across different chains with specific setups and modular swap metadata
* REST-API Testing Endpoints
  - Test REST-API interactions from the command line
* Supporting Multiple Cryptocurrency Networks
  - Currently enabled: TestnetErgo, Sepolia
* Initiators enabled on:
  - Ergo
* Responders enabled on:
  - Sepolia
* Compatible with other DLCs

## Future Plans

* Port to faster (and more type safe)languages
  - Rust, CPP, etc...
* Integrate more Cryptocurrency Networks
  - Bitcoin / Lightning, Grin, Monero
* Integrate more optimized atomic swap protocols
  - Adaptor Swaps: 
    - [Adaptor Schnorr Swap | Blockstream](https://github.com/BlockstreamResearch/scriptless-scripts/blob/master/md/atomic-swap.md)
    - [Adaptor Pedersen Swap | Blockstream](https://github.com/BlockstreamResearch/scriptless-scripts/blob/master/md/pedersen-swap.md)
* Standardization and Detailed Documentation

## How To Build

#### Ubuntu:

To clone and build this application, you'll need [Git](https://git-scm.com).

```bash
# Clone this repository
$ git clone https://github.com/dzyphr/atomicAPI 

# Go into the repository
$ cd atomicAPI

# REMINDER/WARNING: This is ALPHA software, the build script is currently very make-shift and may do things you don't want.
# You should always read scripts before blindly running them, regardless please read the build script before proceeding.
# If you have suggestions on better ways to build the project please leave feedback in Issues or through Discord.

# Run the Ubuntu build script:
$ chmod +x build-ubuntu.sh && ./build-ubuntu.sh

# If it is your first time building, you will need to run through the initial account setup.
# This simply builds a local file that stores the account data you use to perform atomic swaps.
# You can build these files manually if you wish to, this initial account script is meant for convinience.

# (If it is your first time building)Follow the account setup as prompted.

# If it is not your first time building you can simply reply 'n' to the prompts to deny attempting to overwrite the account files.
```

## License

GPL3

## Contact

Discord:
[AtomicAnalogs](https://discord.gg/VDJGszpW58)  | [Ergo](https://discord.gg/ergo-platform-668903786361651200)




