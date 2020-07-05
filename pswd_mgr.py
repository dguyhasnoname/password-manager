import simplejson as json
import getopt, sys, os, re, argparse
from datetime import datetime
from cryptography.fernet import Fernet
import subprocess
from getpass import getpass

global f
PASSWORD_MANAGER_KEY = os.getenv('PASSWORD_MANAGER_KEY', '/Users/mukund/.ssh/fernet_key')
with open(PASSWORD_MANAGER_KEY, "rb") as file:
    key = file.read()
    f = Fernet(key)

os.system("")
class style():
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    RESET = '\033[0m'

def usage():
    parser=argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""This script can be used as an utility to store passwords along with associated fields.
It encrypts and stores password in a JSON file.\n
Dependencies: 
    1. python version                       python3
    2. Encryption/Decryption                cryptography.fernet
    3. JSON formating to handle byte data   simplejson
    4. Hiding password input                getpass
    5. Others                               subprocess/daterime/re etc \n

Before running script export key file as env:

    env=<location to key file to be user for encryption/decryption>
    export PASSWORD_MANAGER_KEY=/Users/dguyhasnoname/.ssh/fernet_key\n""",
        epilog="""All's well that ends well.""")
    
    parser.add_argument('-w', '--write=', metavar='', type=str, help="interactive write mode. Use this flag to write new credentials.")
    parser.add_argument('-r', '--read=', metavar='', type=str, help="read mode. Use this flag to read specific username's detail. \
                                                                    Password is not shown on the screen, instead it gets copied to clip board.")
    parser.add_argument('-l', '--list', metavar='', type=str, help="list mode. Lists all usernames present in inventory.")
    parser.add_argument('-d', '--delete=', metavar='', type=str, help="deletes given username credentials from inventory.")
    args=parser.parse_args() 

def list_username(user_list_flag):
    with open('data.json') as json_file: 
        data = json.load(json_file) 
        global user_list
        user_list = []
        for i in data['accounts']:
            user = json.dumps(i['username'], indent=4, sort_keys=True)
            user_list.append(user)
        if user_list_flag:
            print (style.GREEN + "\nPassword inventory contains credentials for below usernames: \n" + style.RESET)
            print(*user_list,sep='\n')
        return user_list

def write_data():
    # function to add to JSON 
    def write_json(data, filename='data.json'):
        with open(filename,'w') as f: 
            json.dump(data, f, indent=4)

    with open('data.json') as json_file: 
        data = json.load(json_file) 
        temp = data['accounts']
    
        # taking user input to add new data
        username_add = input("Enter username: ")
        for value in temp:
           list_username(False) 
           if any(username_add in s for s in user_list):
               print ("Username {} already exists!".format(username_add))
               user_input = input("You want to update? Y/N: ")
               if user_input == "Y":
                    for v in temp:
                        if username_add == v['username']:
                            password_input = input("Enter password: ")
                            password_add = f.encrypt(password_input.encode("utf-8"))
                            dateTimeObj = datetime.now()
                            last_updated_add = dateTimeObj.strftime("%d-%b-%Y (%H:%M:%S.%f)")
                            v['password'] = password_add
                            print (style.GREEN + "\n[OK] Successfully updated credential." + style.RESET)
                            print(json.dumps(v, indent=4, sort_keys=True))
                            write_json(data)
                            sys.exit()
               else:
                   print ("Exiting!")
                   sys.exit()
           else:
               #password_add = input("Enter password: ") 
               password_input = getpass("Enter password: ") 
               password_add = f.encrypt(password_input.encode("utf-8"))
               website_add = input("Enter website: ") 
               dateTimeObj = datetime.now()
               last_updated_add = dateTimeObj.strftime("%d-%b-%Y (%H:%M:%S.%f)")

               # python object to be appended 
               y = {"username": username_add, 
                   "website": website_add, 
                   "password": password_add,
                   "last_updated": last_updated_add
                   } 
            
                # appending data to emp_details  
               temp.append(y) 
               write_json(data)
               for v in temp:
                    if username_add == v['username']:
                        print("\n" + json.dumps(v, indent=4, sort_keys=True))
                        print (style.GREEN + "\n[OK] Successfully added new credential." + style.RESET)              
               sys.exit()

def get_data(username):
    with open('data.json') as json_file: 
        data = json.load(json_file)
        list_username(False)       
        for value in data['accounts']:
            if username == value['username']:
                print (style.GREEN + "\n[OK] Details found for username:", username + "\n" + style.RESET)
                print(json.dumps(value, indent=4, sort_keys=True))
                return_password_byte = f.decrypt(value['password'].encode("utf-8"))
                # converting return_password_byte to utf format to avoid json serialization error
                return_password = return_password_byte.decode("utf-8") 
                subprocess.run("pbcopy", universal_newlines=True, input=return_password)
                print (style.GREEN + "\n[OK] Password has been copied on clipboard for username:", username + "\n" + style.RESET)
                sys.exit()
            else:
                user_exist = False
        if not user_exist:   
            print (style.RED + "\n[WARNING] " + style.RESET + "Username \"{}\" not found! ".format(username))
            list_username(True)

def delete_data(username):
    with open('data.json', 'rb') as json_file: 
        data = json.load(json_file)  
    list_username(False) 
    if any(username in s for s in user_list):
        print (style.RED + "\n[WARNING] Credential for username \"{}\" will be removed!".format(username) + style.RESET)  
        data['accounts'] = [i for i in data['accounts'] if i['username'] != username]
        with open('data.json','w') as f: 
            json.dump(data, f, indent=4)
        list_username(True)
        print (style.GREEN + "\n[OK] Credential removed." + style.RESET)
    else:
        print (style.RED + "\n[WARNING] " + style.RESET + "Username \"{}\" not found! ".format(username))
        list_username(True)

             

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hwr:ld:", ["help", "write", "read=", "list", "delete="])
        if not opts:
            print (style.RED + "\n[ERROR] " + style.RESET + "No arguments supplied! Run script with -h to see usage.")
            
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err)
        usage()
        sys.exit(2)
    username = ""
    global user_list_flag 
    user_list_flag = ""
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-w", "--write"):
            write_data()
        elif o in ("-r", "--read"):
            username = a
            get_data(username)
        elif o in ("-l", "--list"):
            user_list_flag = True
            list_username(user_list_flag)
        elif o in ("-d", "--delete"):
            username = a
            delete_data(username)  
        else:
            assert False, "unhandled option"

if __name__ == "__main__":
    main()