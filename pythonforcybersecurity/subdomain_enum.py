import requests
import sys

sub_list = open(sys.argv[2]).read()
subdoms = sub_list.splitlines()

for sub in subdoms:
    sub_domains = f"http://{sub}.{sys.argv[1]}"
    
    try:
        requests.get(sub_domains)
        
    except requests.ConnectionError:
        pass
        
    else:
        print("valid domain: ", sub_domains)
