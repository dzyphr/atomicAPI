usage() {
    echo "Usage: $0 <[Options: --stateReloadTest=<SpecificSwapState or all>, --watch]> ..."
    echo "Description of your script usage."
    exit 1
}

# Check number of arguments
if [ "$#" -lt 1 ]; then
    usage
fi
python3 main.py automated_test_local_client_side $1
