chmod +x bin/activate && . bin/activate

python3 main.py submitEncryptedResponse_ClientEndpoint 'http://localhost:3030/v0.0.1/publicrequests' 6c4c581f-0b20-4fde-b9a9-154f9465a9a6 6c4c581f-0b20-4fde-b9a9-154f9465a9a6/ENC_response_path.bin 

deactivate
