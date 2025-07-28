"""
This module provides functions to check IP addresses and their prefixes.
"""

import re

def validate_ip(ip_addr):
    """
    Validates an IPv4 address.
    Returns True if valid, False otherwise.
    """
    pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if not re.match(pattern, ip_addr):
        return False
    octets = ip_addr.split('.')
    for octet in octets:
        try:
            if not 0 <= int(octet) <= 255:
                return False
        except ValueError:
            return False
    return True

def process_prefixes(prefix_list):
    """
    Processes a list of IP prefixes (e.g. 192.168.1.0/24).
    Returns a list of valid prefixes.
    """
    valid_prefixes = []
    for prefix_item in prefix_list:
        try:
            ip_part, mask = prefix_item.split('/')
            if validate_ip(ip_part) and 0 <= int(mask) <= 32:
                valid_prefixes.append(prefix_item)
        except ValueError:
            continue
    return valid_prefixes

def check_ips(ip_address_list, prefixes):
    """
    Checks which IPs in ip_address_list belong to the given prefixes.
    Returns a list of results.
    """
    results = []
    valid_prefixes = process_prefixes(prefixes)
    for ip_addr_item in ip_address_list:
        if not validate_ip(ip_addr_item):
            results.append((ip_addr_item, False))
            continue
        match_found = False
        for prefix in valid_prefixes:
            ip_part, mask = prefix.split('/')
            mask = int(mask)
            ip_bin = ip_to_bin(ip_addr_item)
            prefix_bin = ip_to_bin(ip_part)
            if ip_bin[:mask] == prefix_bin[:mask]:
                match_found = True
                break
        results.append((ip_addr_item, match_found))
    return results

def ip_to_bin(ip_addr):
    """
    Converts an IPv4 address to its binary representation as a string.
    """
    return ''.join(f'{int(octet):08b}' for octet in ip_addr.split('.'))

if __name__ == "__main__":
    # Example usage:
    test_ips = ['192.168.1.10', '10.0.0.1 ', '256.1.1.1', '192.168.1.255']
    test_prefixes = ['192.168.1.0/24', '10.0.0.0/8', 'not_a_prefix', '192.168.2.0/24']
    results = check_ips(test_ips, test_prefixes)
    for ip_addr_item, is_in_prefix in results:
        print(f"{ip_addr_item.strip()} is in prefix: {is_in_prefix}")
    # Save results to a CSV file
    output_file = "whois_results.csv"
    write_results_to_csv(whois_results, output_file)
    print(f"WHOIS results saved to {output_file}")
