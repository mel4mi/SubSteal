from scapy.all import sniff, DNS, DNSQR
import logging

LOG_FILE = "dns_logs.txt"
DECODED_DATA = "data.txt"

logging.basicConfig(filename='error.log', level=logging.ERROR)

processed_queries = set()

def process_packet(packet):
    try:
        if packet.haslayer(DNS) and packet[DNS].opcode == 0:  
            dns_query = packet[DNSQR].qname.decode().strip(".")
            
            if dns_query in processed_queries:
                return            
            processed_queries.add(dns_query)

            if dns_query.startswith('ns1.') or dns_query.startswith('ns2.'):
                pass

            with open(LOG_FILE, "a") as log_file:
                try:
                    log_file.write(f"{dns_query}\n")
                except Exception as e:
                    logging.error(f"Error writing to log file: {e}")
            
            decrypted_data = decrypt(dns_query)
            with open(DECODED_DATA, "a") as data_file:
                try:
                    data_file.write(f"{decrypted_data}\n")
                except Exception as e:
                    logging.error(f"Error writing to decoded data file: {e}")
            
            # Print for debugging (optional)
            # print(f"Logged: {dns_query}")
    except Exception as e:
        logging.error(f"Error processing packet: {e}")

def decrypt(data):
    if data in ["ns1", "ns2"]:
        pass
    try:
        decoded_data = data.split(".")[0]
        decoded_data = decoded_data.replace("mail", "").replace("dashboard", "").replace("www", "")
        decoded_data = decoded_data.split(".")[0]
        decoded_data = bytes.fromhex(decoded_data).decode()
        print(f"Decoded: {decoded_data}")
        return decoded_data
    except Exception as e:
        logging.error(f"Error decoding data: {e}")
        return ""

def main():
    print("DNS Queries are logging...")
    sniff(filter="port 53", prn=process_packet, store=False)

if __name__ == "__main__":
    main()
