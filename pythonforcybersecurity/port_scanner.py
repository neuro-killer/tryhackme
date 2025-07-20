import sys
import socket
import pyfiglet
import argparse

parser = argparse.ArgumentParser(description="TryHackMe Python Port Scanner")
parser.add_argument("ip", type=str, help="Target IP address")
parser.add_argument("start", type=int, help="Start port")
parser.add_argument("end", type=int, help="End port")
parser.add_argument("--verbose", action="store_true", help="Show verbose output")

args = parser.parse_args()


ip = args.ip
open_ports = [] 

ports = range(args.start, args.end)


#ascii_banner = pyfiglet.figlet_format("TryHackMe \n Python 4 Pentesters \nPort Scanner")
print("TryHackMe Python 4 Pentesters Port Scanner\n")
print(f"IP   : {args.ip}")
print(f"Range: {args.start}-{args.end}\n")

def probe_port(ip, port, result = 1): 
  try: 
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    sock.settimeout(0.5) 
    r = sock.connect_ex((ip, port))   
    
    if r == 0: 
      result = r 
    sock.close() 
    
  except Exception as e: 
    pass 
    
  return result


for port in ports: 
    sys.stdout.flush() 
    response = probe_port(ip, port) 
    
    if response == 0: 
        open_ports.append(port)
        if args.verbose:
            print(f"{port} is open!")
    #else:
    #    print(f"{port} is closed!")
    

if open_ports:
    print("\nOpen Ports are:")
    print(sorted(open_ports))
else:
    print("Looks like no ports are open :(")
