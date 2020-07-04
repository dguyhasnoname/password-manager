import json 
import getopt, sys, os, base64
from datetime import datetime
from Crypto.Cipher import AES

os.system("")
class style():
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'

def usage():
    print (style.YELLOW + "\nUsage: \n" + style.RESET)
    print ("This script requires to be run in python3.\n")
    print ("Syntax: python3 pswd_mgr.py <options>\n")
    print ("Options: \n")
    print ("-h              --help      help about the script.")
    print ("-w              --write     write mode. Use this flag to write new credentials.")
    print ("-r <username>   --read      read mode. Use this flag to read specific username's detail.")  
    print ("-l              --list      list mode. Lists all usernames present in inventory.")  

def list_username(user_list_flag):
    with open('data.json') as json_file: 
        data = json.load(json_file) 
        global user_list
        user_list = []
        for i in data['accounts']:
            user = json.dumps(i['username'], indent=4, sort_keys=True)
            user_list.append(user)
        if user_list_flag:
            print (style.GREEN + "\nPassword inventory contains below usernames: \n" + style.RESET)
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
           list_username(user_list_flag) 
           if any(username_add in s for s in user_list):
               print ("Username {} already exists!".format(username_add))
               user_input = input("You want to update? Y/N: ")
               if user_input == "Y":
                    password_add = input("Enter password: ") 
                    dateTimeObj = datetime.now()
                    last_updated_add = dateTimeObj.strftime("%d-%b-%Y (%H:%M:%S.%f)")
                    value['password'] = password_add
                    write_json(data)
                    sys.exit()
               else:
                   print ("Exiting!")
                   sys.exit()
           else:
               password_add = input("Enter password: ") 
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
               sys.exit()

def get_data(username):
    with open('data.json') as json_file: 
        data = json.load(json_file) 
        for value in data['accounts']:
            if username == value['username']:
                print (style.GREEN + "\nDetails found for username:", username + "\n" + style.RESET)
                print(json.dumps(value, indent=4, sort_keys=True))
            else:
                print (style.RED + "[WARNING] " + style.RESET + "Username \"{}\" not found! ".format(username))

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hwr:l", ["help", "write", "read", "list"])
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
        else:
            assert False, "unhandled option"
    # ...

if __name__ == "__main__":
    main()