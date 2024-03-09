cd EVM/Atomicity/ && ./comp_newframe.sh #compile Solidity framework binary

mkdir basic_framework/contracts #make default contracts folder 

# solidity flattener install
git clone https://github.com/poanetwork/solidity-flattener 

cd solidity-flattener

npm install
##

cd ../../../Ergo/SigmaParticle/ && ./comp_new_frame.sh #compile Ergo framework binary

git clone https://github.com/ScorexFoundation/sigmastate-interpreter --branch v5.0.7 ~/Downloads/sigmastate-interpreter/ #get sigmastate interpreter 5.0.7

#sbt install https://www.scala-sbt.org/download.html
echo "deb https://repo.scala-sbt.org/scalasbt/debian all main" | sudo tee /etc/apt/sources.list.d/sbt.list
echo "deb https://repo.scala-sbt.org/scalasbt/debian /" | sudo tee /etc/apt/sources.list.d/sbt_old.list
curl -sL "https://keyserver.ubuntu.com/pks/lookup?op=get&search=0x2EE0EA64E40A89B84B2DF73499E82A75642AC823" | sudo apt-key add
sudo apt-get update
sudo apt-get install sbt
##

setuppwd=$(pwd) #save current dir path to variable

#build sigmastate interpreter jar
cd ~/Downloads/sigmastate-interpreter/

sbt assembly -Djava.security.manager=allow
#run both of these scripts because some systems need the flag and the other will fail, TODO: make this optional also because takes minutes
sbt assembly 
##

cd $setuppwd #go back to atomicAPI setup directory

#build rsElGamal and move it's bin to base folder
cd ../../rust/ && git clone https://github.com/dzyphr/rsElGamal ElGamal

cd ElGamal && rustup default nightly && cargo build --release

cp target/release/ElGamal ../../ElGamal && cd ../../
##

# install venv build it and activate it
sudo apt install python3.10-venv 

python3 -m venv . 

chmod +x bin/activate && . bin/activate 
##

python3 -m pip install python-dotenv ergpy numpy libnum web3==5.31.3 py-solc-x cryptography #install python packages to the venv python

#build general .env file here if there isnt one to solve potential chicken or egg 
if [ -e ".env" ]; then
    echo "Path already exists"
else
    echo "[default]

MINIMUM_REFUND_LOCKTIME_ERGO=10
MIN_CLAIM_LOCKTIME_ERGOTESTNET=2

MIN_REFUND_LOCKTIME_SEPOLIA=150
MINIMUM_CLAIM_LOCKTIME_SEPOLIA=16

SEPOLIA_EVM_GAS_CONTROL=7000000
SEPOLIA_EVM_GASMOD_CONTROL=1" >> .env
fi

python3 main.py firstRunCheck #run firstRunCheck to initialize accounts


./ElGamal genPubKey #gen ElGamal keypair TODO: specify q & g

deactivate #deactivate venv (standard for all py scripts)
