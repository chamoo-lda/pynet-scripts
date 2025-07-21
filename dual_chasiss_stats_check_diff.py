import csv
import re

def parse_device_file(filepath):
    """Parses a device text file and returns a list of dictionaries with interface stats."""
    data = []
    interface_pattern = re.compile(r'interface (\S+)')
    timestamp_pattern = re.compile(r'^(.*) UTC$')
    input_pattern = re.compile(r'(\d+) packets input, (\d+) bytes')
    output_pattern = re.compile(r'(\d+) packets output, (\d+) bytes')

    with open(filepath, 'r') as infile:
        lines = []
        for line in infile:
            clean = line.strip()
            if clean:
                lines.append(clean)

            if len(lines) == 4:
                interface = interface_pattern.search(lines[0]).group(1) if interface_pattern.search(lines[0]) else ''
                timestamp = timestamp_pattern.search(lines[1]).group(1) if timestamp_pattern.search(lines[1]) else ''
                input_match = input_pattern.search(lines[2])
                output_match = output_pattern.search(lines[3])

                input_packets = int(input_match.group(1)) if input_match else 0
                input_bytes = int(input_match.group(2)) if input_match else 0
                output_packets = int(output_match.group(1)) if output_match else 0
                output_bytes = int(output_match.group(2)) if output_match else 0

                data.append({
                    'Interface': interface,
                    'Timestamp': timestamp,
                    'Input Packets': input_packets,
                    'Input Bytes': input_bytes,
                    'Output Packets': output_packets,
                    'Output Bytes': output_bytes
                })
                lines = []
    return data

# Load both device files
device1 = parse_device_file('device1.txt')
device2 = parse_device_file('device2.txt')

# Merge rows and calculate differences
merged_rows = []
for d1, d2 in zip(device1, device2):
    row = {
        'Interface': d1['Interface'],
        'Timestamp': d1['Timestamp'],
        'Input Packets 1': d1['Input Packets'],
        'Input Packets 2': d2['Input Packets'],
        'Input Packets Diff': d2['Input Packets'] - d1['Input Packets'],
        'Input Bytes 1': d1['Input Bytes'],
        'Input Bytes 2': d2['Input Bytes'],
        'Input Bytes Diff': d2['Input Bytes'] - d1['Input Bytes'],
        'Output Packets 1': d1['Output Packets'],
        'Output Packets 2': d2['Output Packets'],
        'Output Packets Diff': d2['Output Packets'] - d1['Output Packets'],
        'Output Bytes 1': d1['Output Bytes'],
        'Output Bytes 2': d2['Output Bytes'],
        'Output Bytes Diff': d2['Output Bytes'] - d1['Output Bytes']
    }
    merged_rows.append(row)

# Define column order
columns = [
    'Interface', 'Timestamp',
    'Input Packets 1', 'Input Packets 2', 'Input Packets Diff',
    'Input Bytes 1', 'Input Bytes 2', 'Input Bytes Diff',
    'Output Packets 1', 'Output Packets 2', 'Output Packets Diff',
    'Output Bytes 1', 'Output Bytes 2', 'Output Bytes Diff'
]

# Write to CSV
with open('device_comparison.csv', 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=columns)
    writer.writeheader()
    writer.writerows(merged_rows)
