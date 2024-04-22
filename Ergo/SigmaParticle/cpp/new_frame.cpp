#include <bits/stdc++.h>
#include <iostream>
#include <filesystem>
#include <vector>
using std::cout, std::string, std::vector;
void makeNewContractFrame(string ContractName);
void echoContractName(string ContractName);
int main(int argc, char* argv[])
{
	if (argc < 2)
	{
		cout << "enter the Contract Name";
	}
	else if (argc >= 2)
	{
		makeNewContractFrame(argv[1]);
		echoContractName(argv[1]);
	}
}

void makeNewContractFrame(string ContractName)
{
	std::string dirpath = ContractName;
	if (std::filesystem::exists(dirpath) && std::filesystem::is_directory(dirpath))
	{
		string command = "cp -r basic_framework/* " + ContractName;
		system(command.c_str());	
	}
	else
	{
		//if it doesnt exist yet copy and create, this will copy folder into existing folder if it existed
		string command = "cp -r basic_framework " + ContractName;
                system(command.c_str());
	}
}

void echoContractName(string ContractName)
{
	string command = "echo \'ContractName=\"" +  ContractName + "\"' >> " + ContractName + "/.env";
	system(command.c_str());
}
