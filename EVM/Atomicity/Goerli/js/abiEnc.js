const dotenv = require('dotenv').config()  
var contractName = ""
var constructorParams = 0
var constructorParamsVals = []
var lastindex = 0
process.argv.forEach(function (arg, index, array) {
	switch (index)
	{
		case 2:
			contractName = arg
			break
		case 3:
			constructorParams = arg
			break
		default:
			if (index > 3) //prevents javascript binary command and filename from being interpreted
			{
				if (constructorParams > 0)
				{
					if (index < array.length)
					{
						if (arg.includes("["))
                                                {
                                                        constructorParamsVals.push(JSON.parse(arg)) //if array parse as json obj
                                                }
                                                else
                                                {
                                                        constructorParamsVals.push(arg)
                                                }

					}
				}
				else
				{
					console.log('parameterVal arguments provided after 0 constructor parameters specified!')
					throw 'set the parameterCount arg == to the amount of parameters in your contract constructor!'
				}
			}
			break
	}
	lastindex = index
})
if (constructorParamsVals.length != constructorParams)
{
	throw 'provided less constructor parameter values than number of constructor parameters!'
}
if (lastindex < 3)
{
	console.log("please provide arguments:\n")
	throw"node abiEnc.js contractName numberOfConstructorParameters parameter1val parameter2val!"
}
const currentChain = process.env.CurrentChain
const fs = require('fs')
const abiFile = contractName + "-abi.json" //expects a file labeled as your contractName-abi.json JSON.parse(contractabi.json)
const jsonABI = JSON.parse(fs.readFileSync(abiFile, 'utf8'))
const Web3 = require('web3')
var web3
switch(currentChain)
{
	case "Goerli":
		web3 = new Web3(Web3.givenProvider || process.env.Goerli)
		break
	case "Ganache":
		web3 = new Web3(Web3.givenProvider || process.env.LocalGanache)
		break
	default:
		throw'Please specify the current chainrpc to get encoding from!\n Use .env variable CurrentChain !'
}
var encodedConstructor = ""
if (constructorParams > 0)
{
	//when a contract has constructor parameters( inputs )they need to be given as arguments in order to deploy the contract
	//when a contract is deployed, any arguments given will be turned into their encoded counterpart within the contract
	//etherscan cannot guess which values you used when uploading the transaction
	//(unless you upload in the exact same way meaning same or extremely similar constructor values)
	//hence it needs to be uploaded to verify on etherscan, 
	//grab each parameter from the constructor, get its type, get the value that was
	//entered into it when the contract was published, encode the parameter with its value. 
	var jsonConstructor = jsonABI[0]
	var typeArray = []
	if (jsonConstructor["inputs"].length != 0)
	{
		for (let i = 0;  i < jsonConstructor["inputs"].length; i++)
		{
			typeArray.push(jsonConstructor["inputs"][i]["internalType"])
		}
	}
	else
	{
		throw'no inputs found in given constructor!'
	}
	console.assert(
		jsonConstructor["inputs"].length == constructorParams, 
		"json constructor inputs length != specified constructorParamsCount!"
	)
	console.assert(
		typeArray.length == constructorParams, 
		"typeArray length != specified constructorParamsCount!" //this would indicate error in constructor parsing algo
							//means some fundamental object structure is different than expected
	)
	for (let i = 0;  i < constructorParams; i++)
	{
		encodedConstructor = web3.eth.abi.encodeParameters(typeArray, constructorParamsVals)
		chop0x = encodedConstructor.slice(2)
	}
	console.log(chop0x)
}
else
{
	console.log("abiEnc.js currently only encodes solidity constructors, currently no use for contracts w no constructor params\n")
}
