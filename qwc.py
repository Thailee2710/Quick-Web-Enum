import subprocess
import socket
import time
import re
from subprocess import STDOUT, check_output
from numpy import tile
from configparser import ConfigParser

config = ConfigParser()

config.read('config.ini')

# Function check IPv4:port
def check_IPV4(ip):
    x = re.search("^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]):[0-9]+$", ip)
    if x:
        return 1
    else:
        return -1

# Function check IP
def check_IP(ip):
    x = re.search("^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])", ip)
    if x:
        # IP
        return 1 
    else:
        #Domain
        return -1 

# Function check telnet
def checkTelnet(domain):
    subprocess.run("sudo echo ", shell=True)
    check = check_IPV4(domain)
    if check==1:
        print("---check_IPV4: Ok---")
        domain = domain.replace(":", " ")
        print(domain)
        try:
            print("\033[92mProgress is being processed, please wait.\033[0;35;40m")
            temp = subprocess.run(f"telnet {domain}", shell=True, capture_output=True, timeout=15)

            #Check result of telnet 
            if str(temp).find("Connection refused") != -1:
                print("*************************\n")
                print("---Connection refused---\n")
                print("*************************")
                return False
            elif str(temp).find("closed") != -1:
                print("*************************\n")
                print("---Connection Ok---\n")
                print("*************************")
                return True
            else:
                print("*************************\n")
                print("---Connection Error---\n")
                print("*************************")
                return False
        except:
            print("*************************\n")
            print("---Connection Ok---\n")
            print("*************************")
            return True
    else:
        print("*************************\n")
        print(f"---Not as IP addr or IP no port---\n\t{domain}")
        print("*************************")
        return True

def checkHttp_Https(domain):
    check = check_IPV4(domain)
    if check==1:
        print("---check_IPV4: Ok---")
        txt = domain.split(":")
        return str(txt[1])      
    else:
        pass

file_input2 = config['option2']['file_input2']
wordlist2 = config['option2']['wordlist']
file_output2 = config['option2']['place']
rate2 = config['option2']['rate2']
# Function main scan IP
def scan_path():
    file_input = file_input2
    wordlist = wordlist2
    place = file_output2
    rate = int(rate2)
    sp = " "
    print(f"\033[92mFile input is: {file_input}.\033[0;35;40m")
    print(f"\033[92mPath output is: {place}.\033[0;35;40m")
    print(f"\033[92mFile wordlist is: {wordlist}.\033[0;35;40m")
    print(f"\033[92mRate: {rate}.\033[0;35;40m")
    file = open(file_input,"r")
    for line in file:
        url = line.strip()
        # tempTelnet = checkTelnet(url) Chay list xac dinh nen bo de tang toc do
        subprocess.run(f"sudo echo {url} > url_temp.txt", shell=True)
        tempTelnet = True # Cho fuction moi check onl dat o day set True neu onl
        sPort = checkHttp_Https(url)
        if (sPort == "80" or sPort =="443"): # Dieu kien la da co port 80 or 443
            print(f"----Port {sPort}----")
            if(sPort == "80"):
                urlNoPort = url.split(":")
                domain = f"sudo dirsearch -u http://{urlNoPort[0]}/ -i 200,302,403 --force-recursive -t {rate} -w {wordlist} -o {place}http_{urlNoPort[0]}.txt"
                try:
                    print("*********HTTP*********")
                    subprocess.run(domain, shell=True, stderr=STDOUT, timeout=1200)
                    subprocess.run(f"sudo echo {sp} >> {place}http_{urlNoPort[0]}.txt", shell=True)
                    subprocess.run(f"sudo echo Default: >> {place}http_{urlNoPort[0]}.txt", shell=True)
                    subprocess.run(f"sudo echo http://{urlNoPort[0]}/ >> {place}http_{urlNoPort[0]}.txt", shell=True)
                except:
                    pass
            else:
                urlNoPort = url.split(":")
                domain = f"sudo dirsearch -u https://{urlNoPort[0]}/ -i 200,302,403 --force-recursive -t {rate} -w {wordlist} -o {place}https_{urlNoPort[0]}.txt"
                try:
                    print("*********HTTP*********")
                    subprocess.run(domain, shell=True, stderr=STDOUT, timeout=1200)
                    subprocess.run(f"sudo echo {sp} >> {place}https_{urlNoPort[0]}.txt", shell=True)
                    subprocess.run(f"sudo echo Default: >> {place}https_{urlNoPort[0]}.txt", shell=True)
                    subprocess.run(f"sudo echo https://{urlNoPort[0]}/ >> {place}https_{urlNoPort[0]}.txt", shell=True)
                except:
                    pass
        else:
            if tempTelnet == True: # Dieu kien la chua port nen check onl roi chay
                start = time.time()
                domain = f"sudo dirsearch -u http://{url}/ -i 200,302,403 --force-recursive -t {rate} -w {wordlist} -o {place}http_{url}.txt"
                try:
                    print("*********HTTP*********")
                    subprocess.run(domain, shell=True, stderr=STDOUT, timeout=1200)
                    subprocess.run(f"sudo echo {sp} >> {place}http_{url}.txt", shell=True)
                    subprocess.run(f"sudo echo Default: >> {place}http_{url}.txt", shell=True)
                    subprocess.run(f"sudo echo http://{url}/ >> {place}http_{url}.txt", shell=True)
                    end = time.time()
                    time_err = end - start
                    print(time_err)
                    if time_err < 600:
                        print("*********HTTPS*********")
                        domain = f"sudo dirsearch -u https://{url}/ -i 200,302,403 --force-recursive -t {rate} -w {wordlist} -o {place}https_{url}.txt"
                        subprocess.run(domain, shell=True, stderr=STDOUT, timeout=1200)
                        subprocess.run(f"sudo echo {sp} >> {place}https_{url}.txt", shell=True)
                        subprocess.run(f"sudo echo Default: >> {place}https_{url}.txt", shell=True)
                        subprocess.run(f"sudo echo https://{url}/ >> {place}https_{url}.txt", shell=True)
                except:
                    pass
            else:
                pass

file_input1 = config['option1']['file_input1']
file_output1 = config['option1']['file_out1']
rate1 = config['option1']['rate1']
# Function scan port of IP
def scan_port():
    file_input = file_input1
    file_output = file_output1 
    file = open(file_input,"r")
    temp = """awk '{print $6":"$4}'"""
    #awkDomain = """awk 'FNR == 12 {print $5}'"""
    rate = int(rate1)
    print(f"\033[92mFile input is: {file_input}.\033[0;35;40m")
    print(f"\033[92mFile output is: {file_output}.\033[0;35;40m")
    print(f"\033[92mRate: {rate}.\033[0;35;40m")
    try:
        for line in file:
            url = line.strip()
            print("------------------------")
            print(url)
            a = 0
            a = check_IP(url)
            try:
                if a == -1:
                    try:
                        if url != "":
                            print(f"\033[92m---Domain {url} was changed to IP and added to the {file_input}.--\033[0;35;40m\n")
                            # sudo dig cs-socket.mto.zing.vn | awk 'FNR == 12 {print $5}' >> ./testpass.txt 
                            subprocess.run(f"sudo dig {url} +short >> {file_input}", shell=True)
                            subprocess.run(f"sudo echo {url} >> {file_output}", shell=True)
                            a = 0
                        else:
                            a = 0
                    except:
                        a = 0
                        pass
                else:
                    # subprocess.run(f"sudo masscan -p1-65535 --rate=200 {url} >> ./{file_output}", shell=True)
                    print("\033[92mProgress is being processed, please wait.\033[0;35;40m")
                    subprocess.run(f"sudo masscan --rate={rate} -p1-65535 {url} | {temp}  >> {file_output}", shell=True) # setting speed
            except:
                pass
    except:
        print("---Error---")

    #Delete /tcp in file
    file = open(file_output, "r")
    replacement = ""
    # using the for loop
    for line in file:
        line = line.strip()
        changes = line.replace("/tcp", "")
        replacement = replacement + changes + "\n"
    file.close()

    # opening the file in write mode
    file = open(file_output, "w")
    file.write(replacement)
    file.close()

file_input3 = config['option3']['file_input3']
file_output3 = config['option3']['file_out3']
# Function scan service Nmap
def scan_service():
    file_input = file_input3
    file_output = file_output3
    file = open(file_input,"r")
    replacement = ""
    sp = " "
    temp = """awk 'NR==5{print $0}; NR==6{print $0}'"""
    # print(temp)
    print(f"\033[92mFile input is: {file_input}.\033[0;35;40m")
    print(f"\033[92mFile output is: {file_output}.\033[0;35;40m")
    try:
        for line in file:
            try:
                url = line.strip()
                urlErorr = url
                url = url.split(":")
                a = url[0]
                b = url[1]
                url = replacement + a + sp + b
                print("------------------------")
                print(url)
                subprocess.run(f"echo {url} >> {file_output}", shell=True)
                subprocess.run(f"sudo nmap -sV -p {b} -Pn {a} | {temp}  >> {file_output} ", shell=True) # setting speed
                subprocess.run(f"echo {sp} >> {file_output}", shell=True)
            except:
                print("------------------------")
                print(f"---Error: {urlErorr} Wrong format ---")
                subprocess.run(f"echo {urlErorr} >> {file_output}", shell=True)
                subprocess.run(f"echo {sp} >> {file_output}", shell=True)
    except:
        print("---Error---")

# Open web brower with incognito mode
def open_incognito():
    script="google-chrome --incognito"
    subprocess.run(script, shell=True)


file_input4 = config['option4']['file_input4']
wordlist4 = config['option4']['wordlist']
file_output4 = config['option4']['place']
rate4 = config['option4']['rate4']
outType = config["option4"]["outType"]
# Scaning API by fuzzing (ffuf)
def scan_pathFuzz():
    file_input = file_input4
    wordlist = wordlist4
    place = file_output4
    rate = int(rate4)
    outPutType = outType
    sp = " "
    print(f"\033[92mFile input is: {file_input}.\033[0;35;40m")
    print(f"\033[92mPath output is: {place}.\033[0;35;40m")
    print(f"\033[92mFile wordlist is: {wordlist}.\033[0;35;40m")
    print(f"\033[92mRate: {rate}.\033[0;35;40m")
    print(f"\033[92mRate: {outPutType}.\033[0;35;40m")
    file = open(file_input,"r")
    for line in file:
        url = line.strip()
        start = time.time()
        domain = f"ffuf -c -u http://{url}/FUZZ -w {wordlist} -fc 500,501,502,503,504,505 -t {rate} -se -o {place}http_{url}.{outPutType} -of {outPutType} -recursion"
        try:
            print("*********HTTP*********")
            subprocess.run(domain, shell=True, stderr=STDOUT)
            end = time.time()
            time_err = end - start
            print(time_err)
            if time_err < 120:
                print("*********HTTPS*********")
                domain = f"ffuf -c -u https://{url}/FUZZ -w {wordlist} -fc 500,501,502,503,504,505 -t {rate} -se -o {place}https_{url}.{outPutType} -of {outPutType} -recursion"
                subprocess.run(domain, shell=True, stderr=STDOUT)
        except:
            pass   

file_input6 = config['option6']['file_input6']
file_output6 = config['option6']['file_out6']
#Check IP Online and dns reverse lookup
def recon_Pub_DNS():
    input = file_input6
    place = file_output6
    print(f"\033[92mFile input is: {input}.\033[0;35;40m")
    print(f"\033[92mPath output is: {place}.\033[0;35;40m")
    file = open(input,"r")
    for line in file:
        url = line.strip()
        host = ""
        host_final = ""
        check = check_IPV4(url)
        checkHost = check_IP(url)
        if check==1:
            print("IP have port: Pass")
            subprocess.run(f"echo {url} >> {place}", shell=True)
        elif checkHost == -1:
            subprocess.run(f"echo {url} >> {place}", shell=True)
        else:
            try:
                # Check IP onl or off
                checkPub = subprocess.run(f"python -m rpchecker -u {url}", shell=True, capture_output=True)
                checkPub = checkPub.stdout 
                checkPub = checkPub.rstrip() # Xoa /n cua ket qua
                temp = str(checkPub)
                temp2 = """b'1'"""
                #"""b'1'""" la onl
                if temp == temp2:
                    try:
                        print(f"{url} Onl")
                        subprocess.run(f"echo {url} >> {place}", shell=True)
                        # dns reverse lookup
                        host = socket.gethostbyaddr(url)
                    except:
                        print(f"--{url} No Host--")
                        host = ""
                    print(host[0]) #Host of IP
                    host_final = host[0]
                    if host=="":
                        print("Not save")
                    else:
                        print("Save")
                        subprocess.run(f"echo {host_final} >> {place}", shell=True)
                else:
                    print(f"{url} OFF")
            except:
                pass
    check_dup(place)

# Check duplicate
def check_dup(file):
    with open(file, 'r+') as f:
        lines = f.readlines()
        f.seek(0)
        f.truncate()
        lines_set = set(lines)
        for line in lines_set:
            f.write(line)

# Function option in main
def switch(action):
    try:
        if action == '1':
            scan_port()
        elif action == '2':
            print("---Choice tools---")
            print("  1) Dirsearch")
            print("  2) FFUF (with tool will output file .csv (Can change other type in config)")
            print("  3) Exit")
            option2Choice = str(input("Options: "))
            if option2Choice == '1':
                scan_path()
            elif option2Choice == '2':
                scan_pathFuzz()
            elif option2Choice == '3':
                print(" --Exit--")
            elif option2Choice !=1 and option2Choice != 2 and option2Choice != 3:
                print("Input not correct")
        elif action == '3':
            scan_service()
        elif action == '4':
            recon_Pub_DNS()
        else:
            print("Nope")
    except:
        pass

# Main
if __name__ == "__main__":
    action = ""
    title = """\033[0;35;40m 
    
   ____        _      __      _       __     __       ________              __  
  / __ \__  __(_)____/ /__   | |     / /__  / /_     / ____/ /_  ___  _____/ /__
 / / / / / / / / ___/ //_/   | | /| / / _ \/ __ \   / /   / __ \/ _ \/ ___/ //_/
/ /_/ / /_/ / / /__/ ,<      | |/ |/ /  __/ /_/ /  / /___/ / / /  __/ /__/ ,<   
\___\_\__,_/_/\___/_/|_|     |__/|__/\___/_.___/   \____/_/ /_/\___/\___/_/|_|  
                                                                                
                                                            
    """
    print(title)

    while True:
        print("\033[0;35;40m##########--------##########")
        print("Your choice is: ")
        print("  1) Scan port of list IP (Can reverse Host to IP).")
        print("  2) Scan path")
        print("  3) Scan service by Nmap")
        print("  4) Check IP Onl/Off and DNS reverse lookup \033[92m(Recommand run before option 2)\033[0;35;40m")
        print("  5) Exit")
        action=str(input("Options: "))
        print("")
        if action in ['1', '2', '3', '4']:
            switch(action)
        elif action == '5':
            print(" --- Thank you, bye bye ---")
            break
        else:
            print("Invalid")

