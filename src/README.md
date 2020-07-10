# password-manager

This script can be used as an utility to store passwords along with associated fields.
It encrypts and stores password in a JSON file.

1. This script requires to be run in python3. 
2. You need to store the key carefully(with 400 permission) which is used for encryption/decryption.
3. You can update password for any credential.
4. Initial data.json file already present in the repo should not be deleted.

#### usage: pswd_mgr.py [-h] [-w] [-r] [-l] [-d]

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

## Fields in JSON file

```

{
    "alias": "new",                                   # alias for a credential
    "last_updated": "06-Jul-2020 (13:28:13.566265)",  # last updated date
    "password":                              "gAAAAABfAtmQCE35-J-Q07YX8a3UzLR-AQVuVEk6sUn8WEg3PPDEFgIW9_RdMO3X3ct9GUOsZT8eXBEDjjaVQgsOjCtCH-tJ0g==",
    "username": "new",                                # username
    "website": "https://new.com"                      # field for website reference
}
```

## How to use?

### adding new credential

```
Mon Jul 06 01:28 PM IST: 192.168.64.3:8443: src$ python3 pswd_mgr.py -w
Enter alias for this credential: new
Enter username: new
Enter password: 
Enter website: https://new.com

{
    "alias": "new",
    "last_updated": "06-Jul-2020 (13:28:13.566265)",
    "password": "gAAAAABfAtmQCE35-J-Q07YX8a3UzLR-AQVuVEk6sUn8WEg3PPDEFgIW9_RdMO3X3ct9GUOsZT8eXBEDjjaVQgsOjCtCH-tJ0g==",
    "username": "new",
    "website": "https://new.com"
}

[OK] Successfully added new credential.
```

### reading a credential

```
Mon Jul 06 01:28 PM IST: 192.168.64.3:8443: src$ python3 pswd_mgr.py -r new

[OK] Details found for credential: new

{
    "alias": "new",
    "last_updated": "06-Jul-2020 (13:28:13.566265)",
    "password": "gAAAAABfAtmQCE35-J-Q07YX8a3UzLR-AQVuVEk6sUn8WEg3PPDEFgIW9_RdMO3X3ct9GUOsZT8eXBEDjjaVQgsOjCtCH-tJ0g==",
    "username": "new",
    "website": "https://new.com"
}

[OK] Password has been copied on clipboard for username: "new"

```

### updating an existing credential

```
Mon Jul 06 01:40 PM IST: 192.168.64.3:8443: src$ python3 pswd_mgr.py -w
Enter alias for this credential: new
Credential new already exists!
You want to update? Y/N: Y
Enter password: 

[OK] Successfully updated credential.
{
    "alias": "new",
    "last_updated": "06-Jul-2020 (13:28:13.566265)",
    "password": "gAAAAABfAtyBx2yW6TaVnf6X00yZMygLy9uyN8D06-n0516ZdxpsZdQguERM3p7SCh2BvIz-xF56nnUH4xmbKdE1dRNFL-yCmg==",
    "username": "new",
    "website": "https://new.com"
}

```

### deleting a credential


```
Mon Jul 06 01:40 PM IST: 192.168.64.3:8443: src$ python3 pswd_mgr.py -d new

[WARNING] Credential "new" will be removed!

Password inventory contains credentials for below usernames: 

USERNAME                       ALIAS     

test                           test 
dxxxxxxxxnxxx                  dockerhub 
dxxxxxxxxnaxx                  github  
ok                             ok        

[OK] Credential removed.

```

### listing credentials

```
Mon Jul 06 01:41 PM IST: 192.168.64.3:8443: src$ python3 pswd_mgr.py -l

Password inventory contains credentials for below usernames: 

USERNAME                       ALIAS     
test                           test   
dxxxxxxxxnxxx                  dockerhub 
dxxxxxxxxnaxx                  github  
ok                             ok 

```


