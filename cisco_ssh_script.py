#!/usr/bin/env python3
"""
SSH Script to connect to Cisco devices through a bastion server
Reads device credentials from CSV and logs results
"""

import csv
import paramiko
import logging
from datetime import datetime
import time
import os
from pathlib import Path

# Configuration
BASTION_HOST = "bastion.example.com"
BASTION_PORT = 22
BASTION_USERNAME = "your_username"
BASTION_KEY_FILE = "/path/to/your/private_key.pem"  # Path to private key for bastion

CSV_FILE = "devices.csv"  # CSV with columns: host,username,password

# Cisco commands to execute
CISCO_COMMANDS = [
    "show version",
    "show ip interface brief",
    "show running-config | include hostname"
]

# Logging setup
LOG_FOLDER = "logs"  # Folder to store log files
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Create logs folder if it doesn't exist
Path(LOG_FOLDER).mkdir(parents=True, exist_ok=True)

success_log = os.path.join(LOG_FOLDER, f"success_{timestamp}.log")
error_log = os.path.join(LOG_FOLDER, f"error_{timestamp}.log")

# Configure loggers
logging.basicConfig(level=logging.INFO)
success_logger = logging.getLogger('success')
error_logger = logging.getLogger('error')

# Success logger
success_handler = logging.FileHandler(success_log)
success_handler.setLevel(logging.INFO)
success_formatter = logging.Formatter('%(asctime)s - %(message)s')
success_handler.setFormatter(success_formatter)
success_logger.addHandler(success_handler)
success_logger.propagate = False

# Error logger
error_handler = logging.FileHandler(error_log)
error_handler.setLevel(logging.ERROR)
error_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
error_handler.setFormatter(error_formatter)
error_logger.addHandler(error_handler)
error_logger.propagate = False


def create_bastion_tunnel(bastion_host, bastion_port, bastion_username, bastion_key_file):
    """
    Create SSH connection to bastion server
    """
    try:
        bastion_client = paramiko.SSHClient()
        bastion_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Load private key
        private_key = paramiko.RSAKey.from_private_key_file(bastion_key_file)
        
        print(f"Connecting to bastion server: {bastion_host}")
        bastion_client.connect(
            hostname=bastion_host,
            port=bastion_port,
            username=bastion_username,
            pkey=private_key,
            timeout=10
        )
        print("Successfully connected to bastion server")
        return bastion_client
    
    except Exception as e:
        error_logger.error(f"Failed to connect to bastion server: {str(e)}")
        print(f"ERROR: Failed to connect to bastion server: {str(e)}")
        return None


def connect_through_bastion(bastion_client, device_host, device_port, device_username, device_password):
    """
    Connect to device through bastion server using SSH tunnel
    """
    try:
        # Create transport through bastion
        bastion_transport = bastion_client.get_transport()
        dest_addr = (device_host, device_port)
        local_addr = ('127.0.0.1', 22)
        
        # Open channel through bastion
        bastion_channel = bastion_transport.open_channel(
            "direct-tcpip",
            dest_addr,
            local_addr
        )
        
        # Create client for device
        device_client = paramiko.SSHClient()
        device_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Connect to device through tunnel
        device_client.connect(
            hostname=device_host,
            port=device_port,
            username=device_username,
            password=device_password,
            sock=bastion_channel,
            timeout=10,
            look_for_keys=False,
            allow_agent=False
        )
        
        return device_client
    
    except Exception as e:
        raise Exception(f"Failed to connect to device: {str(e)}")


def execute_cisco_commands(device_client, device_host, commands):
    """
    Execute commands on Cisco device and return output
    """
    output = []
    
    try:
        # Invoke shell for interactive session
        shell = device_client.invoke_shell()
        time.sleep(1)
        
        # Clear initial output
        shell.recv(9999)
        
        # Disable paging
        shell.send("terminal length 0\n")
        time.sleep(1)
        shell.recv(9999)
        
        # Execute each command
        for command in commands:
            shell.send(f"{command}\n")
            time.sleep(2)
            
            command_output = ""
            while shell.recv_ready():
                command_output += shell.recv(9999).decode('utf-8')
                time.sleep(0.5)
            
            output.append(f"\n{'='*60}\nCommand: {command}\n{'='*60}\n{command_output}")
        
        return "\n".join(output)
    
    except Exception as e:
        raise Exception(f"Failed to execute commands: {str(e)}")


def read_devices_from_csv(csv_file):
    """
    Read device information from CSV file
    Expected columns: host,username,password
    """
    devices = []
    
    try:
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                devices.append({
                    'host': row['host'].strip(),
                    'username': row['username'].strip(),
                    'password': row['password'].strip()
                })
        
        print(f"Loaded {len(devices)} devices from {csv_file}")
        return devices
    
    except FileNotFoundError:
        print(f"ERROR: CSV file '{csv_file}' not found")
        error_logger.error(f"CSV file '{csv_file}' not found")
        return []
    
    except Exception as e:
        print(f"ERROR: Failed to read CSV file: {str(e)}")
        error_logger.error(f"Failed to read CSV file: {str(e)}")
        return []


def process_device(bastion_client, device, commands):
    """
    Process single device: connect and execute commands
    """
    device_host = device['host']
    device_username = device['username']
    device_password = device['password']
    
    print(f"\nProcessing device: {device_host}")
    
    try:
        # Connect to device through bastion
        device_client = connect_through_bastion(
            bastion_client,
            device_host,
            22,
            device_username,
            device_password
        )
        
        print(f"  ✓ Connected to {device_host}")
        
        # Execute commands
        output = execute_cisco_commands(device_client, device_host, commands)
        
        # Log success
        success_logger.info(f"\n{'#'*80}\nDevice: {device_host}\n{'#'*80}\n{output}")
        print(f"  ✓ Commands executed successfully on {device_host}")
        
        # Close device connection
        device_client.close()
        
        return True
    
    except Exception as e:
        error_msg = f"Device: {device_host} - Error: {str(e)}"
        error_logger.error(error_msg)
        print(f"  ✗ Failed: {device_host} - {str(e)}")
        return False


def main():
    """
    Main function to orchestrate the script
    """
    print("="*80)
    print("Cisco Device SSH Script via Bastion Server")
    print("="*80)
    
    # Read devices from CSV
    devices = read_devices_from_csv(CSV_FILE)
    
    if not devices:
        print("No devices to process. Exiting.")
        return
    
    # Connect to bastion server
    bastion_client = create_bastion_tunnel(
        BASTION_HOST,
        BASTION_PORT,
        BASTION_USERNAME,
        BASTION_KEY_FILE
    )
    
    if not bastion_client:
        print("Failed to connect to bastion server. Exiting.")
        return
    
    # Process each device
    success_count = 0
    failure_count = 0
    
    for device in devices:
        if process_device(bastion_client, device, CISCO_COMMANDS):
            success_count += 1
        else:
            failure_count += 1
        
        # Small delay between devices
        time.sleep(1)
    
    # Close bastion connection
    bastion_client.close()
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Total devices processed: {len(devices)}")
    print(f"Successful: {success_count}")
    print(f"Failed: {failure_count}")
    print(f"\nSuccess log: {success_log}")
    print(f"Error log: {error_log}")
    print("="*80)


if __name__ == "__main__":
    main()
