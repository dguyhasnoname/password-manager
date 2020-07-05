# password-manager

This script can be used as an utility to store passwords along with associated fields.
It encrypts and stores password in a JSON file.

1. This script requires to be run in python3. 
2. You need to store the key carefully(with 400 permission) which is used for encryption/decryption.
3. You can update password for any credential.

### usage: pswd_mgr.py [-h] [-w] [-r] [-l] [-d]

Before running script export key file as env:

    env = <location to key file to be user for encryption/decryption>

   ` export PASSWORD_MANAGER_KEY=/Users/dguyhasnoname/.ssh/fernet_key`

## Dependencies: 
    1. python version                       python3
    2. Encryption/Decryption                cryptography.fernet
    3. JSON formating to handle byte data   simplejson
    4. Hiding password input                getpass
    5. Others                               subprocess/daterime/re etc 

### optional arguments:
```
  -h, --help       show this help message and exit
  -w , --write=    interactive write mode. Use this flag to write new
                   credentials.
  -r , --read=     read mode. Use this flag to read specific username's
                   detail. Password is not shown on the screen, instead it
                   gets copied to clip board.
  -l , --list      list mode. Lists all usernames present in inventory.
  -d , --delete=   deletes given username credentials from inventory.
```