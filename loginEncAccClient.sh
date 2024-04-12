
 if [ "$#" -lt 4 ]; then
	 echo "Usage: $0 <Chain> <AccountName> <Password> <Bearer-RESTAPI-Auth-Key>"
 fi

python3 main.py logInToPasswordEncryptedAccount_Client $1 $2 $3 $4


