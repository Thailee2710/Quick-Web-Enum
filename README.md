👋 Scan path, ports, and service 
                                                    
**Main-Purpose**: 
- This script use for scan all path of url (domain and IP) (ex: https://abc.com/xyz/123). 
- This script use for scan all ports from IP.
- This script use for check service from input.
- This script user for audit API from input.
- This script is used to check if IP or DNS is working.

**Setup and Configuration**
Support scan http-https. Main tool used in this scrpit is `Dirsearch`.
 * Update pip, apt, apt-get to latest version
 - To run need to install `dirsearch`, `masscan`, `click`, `numpy`.
    + `dirsearch`: sudo apt-get install dirsearch.
    + `masscan`: udo apt-get install masscan.
    + `click`: pip install -U click.
    + `numpy`: pip install numpy.
    + `ffuf`: git clone https://github.com/ffuf/ffuf ; cd ffuf ; go build
    + `Other`: pip install -r requirements.txt

 - To edit option you can see [Dirsearch](https://www.kali.org/tools/dirsearch/),[Masscan](https://www.kali.org/tools/masscan/),[Nmap](https://www.kali.org/tools/nmap/).
 - Input and output files can be edited at `config.ini` (Recommended to review before using this script).

**Run script**: `python qwc.py`

**Input Data Rule**
- Input should be `domain` or `IP`
- Do not input the IP range because the script cannot run.
- Input and output paths should be correct (edit through `config.ini`)
- With input as domain thid `cannot` be:
   + http:// or https://
   + / at the end

**Feature**
 - This script has 3 features:
    + 1. Scan all ports of input IP.
    + 2. Scan for subpaths in the domain.
      * 1. Dirsearch
      * 2. FFUF
    + 3. Scan service through Nmap.
    + 4. Scan API via Kiterunner (Recommend)

 **Note**:
 - If you want to leave it over night, you need to:
     + Make sure the running process is not interrupted.
     + Set never sleep and turn off screen saver (On both host machine and virtual machine).
     + Make sure the network connection is still active. 
 - File input should be .txt file, and need to leave "one" blank row at the end of the file (to avoid errors).
      __For example__:
      """
      abc.com
      127.0.0.1

      """
 - If running `option 2` (scan path) fails, you just need to reinstall `dirsearch`
 - This script just working only on Linux (Recommend: Kali Linux)
 - If you want to `read` result of `option 4` (scan API) without error, you run the following command:
   + `cat endpointAPI.txt`

 💞 Thanks you, hope you happy when use this tool 💞