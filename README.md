👋 Scan path, ports, and service 
                                                    
**Main-Purpose**: 
- This script use for scan all path of url (domain and IP) (ex: https://abc.com/xyz/123). 
- This script use for scan all ports from IP.
- This script use for check service from input.
- This script user for audit API from input.
- This script is used to check if IP or DNS is working.

---
**Setup and Configuration**
Support scan http-https. Main tool used in this scrpit is `Dirsearch`.
 * Update pip, apt, apt-get to latest version
 - To run need to install:
    + `dirsearch`: 
      - For Kali: sudo apt install dirsearch (For Kali Linux)
      - For Ubuntu: git clone https://github.com/maurosoria/dirsearch.git ; cd dirsearch ; pip install -r requirements.txt
    + `masscan`: sudo apt install masscan.
    + `ffuf`: git clone https://github.com/ffuf/ffuf ; cd ffuf ; go build
    + `Other`: pip install -r requirements.txt

 - To edit option you can see [Dirsearch](https://www.kali.org/tools/dirsearch/),[Masscan](https://www.kali.org/tools/masscan/),[Nmap](https://www.kali.org/tools/nmap/).
 - Input and output files can be edited at `config.ini` *(Recommended to review before using this script)*.

### **Run script**: `python qwc.py`
---
**Input Data Rule**
- Input should be `domain` or `IP`
- Do not input the IP range because the script cannot run.
- Input and output paths should be correct (edit through `config.ini`)
- With input as domain thid `cannot` be:
   + http:// or https://
   + / at the end

**Feature**
 - This script has 3 features:
   1. Scan all ports of input IP.
   2. Scan for subpaths in the domain.
      1. Dirsearch
      2. FFUF
   3. Scan service through Nmap.
   4. Check IP Onl/Off and DNS reverse lookup

 **Note**:
 - If running `option 2` (scan path) fails, you just need to reinstall `dirsearch`
 - This script just working only on Linux (Recommend: Kali Linux)
 - After running `pip install -r requirements.txt` the script is now operational. You can install additional tools to use specific functionalities.

 💞 Thanks you, hope you happy when use this tool 💞