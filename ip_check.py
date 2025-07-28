import ipaddress
from ipwhois import IPWhois
import csv
import time

def get_whois_data(ip):
    """
    Get WHOIS information for an IP address.
    """
    try:
        obj = IPWhois(ip)
        result = obj.lookup_rdap()
        return {
            'IP': ip,
            'Network Name': result.get('network', {}).get('name', 'N/A'),
            'Country': result.get('network', {}).get('country', 'N/A'),
            'ASN': result.get('asn', 'N/A'),
            'ASN Description': result.get('asn_description', 'N/A')
        }
    except Exception as e:
        return {'IP': ip, 'Error': f"WHOIS lookup failed: {e}"}

def expand_prefixes(prefixes):
    """
    Expand a list of IP prefixes into individual IP addresses for WHOIS lookup.
    """
    ip_list = []
    for prefix in prefixes:
        try:
            network = ipaddress.ip_network(prefix, strict=False)
            ip_list.append(str(network[0]))  # Use the first IP for lookup
        except ValueError as e:
            print(f"Invalid prefix '{prefix}': {e}")
    return ip_list

def write_results_to_csv(results, output_file):
    """
    Write WHOIS results to a CSV file.
    """
    keys = results[0].keys() if results else []
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=keys)
        writer.writeheader()
        writer.writerows(results)

if __name__ == "__main__":
    # List of prefixes to check (example)
    prefixes = [
        "xxx.xxx.xxx.xxx/24",
        "xxx.xxx.xxx.xxx/21"
    ]
    
    # Expand prefixes into a list of IPs for WHOIS
    ip_list = expand_prefixes(prefixes)
    
    # Fetch WHOIS data for each IP
    whois_results = []
    for ip in ip_list:
        print(f"Checking WHOIS for {ip}...")
        result = get_whois_data(ip)
        whois_results.append(result)
        time.sleep(2)  # Avoid rate-limiting
    
    # Save results to a CSV file
    output_file = "whois_results.csv"
    write_results_to_csv(whois_results, output_file)
    print(f"WHOIS results saved to {output_file}")
