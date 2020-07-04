# password-manager

Utility tool to store your passwords in encrypted way in JSON format.

1. This script requires to be run in python3. 
2. You need to store the key carefully(with 400 permission) which is used for encryption/decryption.
3. You can update password for any credential.

Syntax: `python3 pswd_mgr.py <options>`

Options: 

```
-h              --help      help about the script.
-w              --write     write mode. Use this flag to write new credentials.
-r <username>   --read      read mode. Use this flag to read specific username's detail.
                            Password is not shown on the screen, instead it gets copied
                            to clip board.
-l              --list      list mode. Lists all usernames present in inventory. 
```
