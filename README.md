 # Atomic API


#### Python Based Low Level API for Encryped Cross-Chain Atomic Swaps



## NOTE: Project is in Alpha / Testnet Phase | Actively Seeking Contributions and Feedback

## Key Features

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

## How To Build

#### Ubuntu:

To clone and build this application, you'll need [Git](https://git-scm.com).

```bash
# Clone this repository
$ git clone 

# Go into the repository
$ cd atomicAPI

# REMINDER/WARNING: This is ALPHA software, the build script is currently very make-shift and may do things you don't want.
# You should always read scripts before blindly running them, regardless please read the build script before proceeding.
# If you have suggestions on better ways to build the project please leave feedback in Issues or through Discord.

# Run the Ubuntu build script:
$ chmod +x build-ubuntu.sh && ./build-ubuntu

# If it is your first time building, you will need to run through the initial account setup.
# This simply builds a local file that stores the account data you use to perform atomic swaps.
# You can build these files manually if you wish to, this initial account script is meant for convinience.

# (If it is your first time building)Follow the account setup as prompted.

# If it is not your first time building you can simply reply 'n' to the prompts to deny attempting to overwrite the account files.
```

## License

GPL3

Discord [AtomicAnalogs](https://discord.gg/VDJGszpW58)




